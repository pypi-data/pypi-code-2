from __future__ import with_statement
try:
    from collections import OrderedDict
except ImportError:
    try:
        from ordereddict import OrderedDict
    except ImportError:
        raise ImportError("inputgen requires an OrderedDict implementation."
                          " Either use Python >2.7 or install the ordereddict"
                          " library from PyPI.")
from copy import copy
import itertools
import unittest


class FieldDescriptor(object):
    """
    A descriptor class to use for swapping out attributes that are used for
    finitization.  Get accesses are recorded on the factory instance.

    Each descriptor instance maintains a reference back to the factory that
    created it.  If an accessed field is not being finitized by the factory,
    then the descriptor falls back to the object instance's __dict__.  This
    way, non-finitized object instances are not affected by their class'
    instrumentation.
    """

    def __init__(self, warehouse, field_name, record=True):
        self.warehouse = warehouse
        self.field_name = field_name
        self.record = record

    def __get__(self, instance, owner):
        try:
            return self.get_field_and_record(instance).value
        except KeyError:
            # Instance is not instrumented, try normal attribute lookup.
            try:
                return instance.__dict__[self.field_name]
            except KeyError:
                raise AttributeError("'%s'" % self.field_name)

    def __set__(self, instance, value):
        try:
            self.get_field_and_record(instance).value = value
        except KeyError:
            # Instance is not instrumented, try normal attribute assignment.
            instance.__dict__[self.field_name] = value

    def get_field_and_record(self, instance):
        factory = self.warehouse.instances[instance]
        field = factory.get_field(instance, self.field_name)
        if self.record:
            factory.record_field_access(field)
        return field


class Warehouse(object):
    """
    Maintains references from each Field's instance object to the Factory
    instance that maintains its state information.

    Primarily used for multiprocess operation, where one Factory instance is
    created for each process.  The FieldDescriptor instrumentation uses this
    to determine the correct Factory/state to lookup for an instrumented
    field.
    """

    def __init__(self):
        # {instance -> factory}
        self.instances = {}

# Default Warehouse instance.
warehouse = Warehouse()


class Factory(object):
    """
    The Factory object maintains information about:

    * All of the created ClassDomain instances.
    * All Field objects, referenced by the instance and the name of the field.
    * All accessed fields, in the order of access.
    """

    def __init__(self, enable_backtracking=True, enable_iso_breaking=True,
                 warehouse=warehouse):
        self.enable_backtracking = enable_backtracking
        self.enable_iso_breaking = enable_iso_breaking
        self.warehouse = warehouse
        # Flag to signify if factory has been initialized.
        self.initialized = False
        # We initialize class_domains to include a class domain for the factory
        # object itself so that field can be set on it.
        self.domain = ClassDomain(self, cls=self.__class__, instances=[self])
        self.class_domains = [self.domain]
        # Cache domain equality.  (Field) -> set(Fields)
        self.domain_equality = {}

        # instance -> {field_name -> Field}
        self.obj_fields = OrderedDict()
        self.fields = []

        # Used for recording field accesses, we only use the keys which are
        # Field instances.
        self.accessed_fields = OrderedDict()

    def __str__(self):
        return ('<Factory, indicies: %s, accessed: %s>'
                % (str(self.indicies), self.accessed_field_indicies))

    def has_field(self, instance, field_name):
        try:
            self.obj_fields[instance][field_name]
            return True
        except KeyError:
            return False

    def get_field(self, instance, field_name):
#        if not self.initialized:
#            raise RuntimeError("Factory must be initialized before accessing fields")
        return self.obj_fields[instance][field_name]

    @property
    def lengths(self):
        for field in self.fields:
            yield len(field.domain)

    @property
    def objects(self):
        for obj in self.obj_fields:
            yield obj

    @property
    def indicies(self):
        """The current index values for all Fields."""
        return tuple(field.index for field in self.fields)

    @property
    def values(self):
        """The current values for all Fields."""
        return tuple(field.value for field in self.fields)

    @property
    def field_names(self):
        """The current field names for all Fields."""
        return tuple(field.name for field in self.fields)

    @property
    def accessed_field_indicies(self):
        """The indices (order index) of the fields that have been accessed."""
        return tuple(field.order for field in self.accessed_fields)

    def __iter__(self):
        for indicies in self.iter_indicies():
            self.apply_indicies(indicies)
            yield self

    def apply_indicies(self, indicies):
        self.accessed_fields.clear()
        for field, index in itertools.izip(self.fields, indicies):
            if field.index != index:
                field.index = index

    def iter_indicies(self, start_indicies=None, stop_stack=None, queue=None,
                      activity=None):
        # Cache the fields, list of lengths, and number of indicies for later.
        fields = self.fields
        lengths = tuple(self.lengths)
        num_indicies = len(lengths)

        # Initialize list of indicies and the stack.
        if start_indicies is not None:
            indicies = start_indicies
        else:
            indicies = [0] * num_indicies
        stack = []

        while True:
            yield indicies

            if self.enable_backtracking:
                # When backtracking, increment only accessed fields.  Since we
                # push these one at a time onto the stack, the last field
                # accessed will be on top of the stack.
                selected_indicies = self.accessed_field_indicies
            else:
                selected_indicies = reversed(xrange(num_indicies))
            # Push indicies onto the stack.
            orig_stack_length = len(stack)
            for i in selected_indicies:
                if i not in stack:
                    stack.append(i)

            orig_indicies = copy(indicies)
            indicies = self.increment_indicies(fields, lengths, indicies,
                                               stack, stop_stack)


            # If the stack got bigger, add that work to the queue and continue
            # where we left off.
            if orig_stack_length and (len(stack) > orig_stack_length):
                # Return stack back to previous run.
                stack = stack[:orig_stack_length]
                # The original stack becomes the stop_stack for this work.
                with activity:
                    queue.put((copy(indicies), copy(stack)))
                    activity.notify()
                #print 'putting on queue:', indicies, stack
                # Return indicies back to the previous run and clear accessed fields.
                self.accessed_fields.clear()
                indicies = self.increment_indicies(
                    fields, lengths, orig_indicies, stack, stop_stack)
                # Stop if we've reached the stop_stack (increment_indicies
                # returned None).
                if indicies is None:
                    break
                # Continue work on the original, pre-expanded stack using
                # previous indicies and same stop_stack.
                with activity:
                    queue.put((copy(indicies), copy(stop_stack)))
                    activity.notify()
                #print 'putting on queue:', indicies, stack
                break

            # Stop if we've reached the stop_stack (increment_indicies
            # returned None).
            if indicies is None:
                break

            if not stack:
                # All indicies rolled over, we are done.
                break

    def increment_indicies(self, fields, lengths, indicies, stack, stop_stack):

        # Increment the first index, then go through and check for any
        # rolled-over counters.
        while stack:

            i = stack[-1]   # top index on stack

            if (self.enable_iso_breaking):
                field = fields[i]

                # Compute m_f, as described in first Korat paper.
                m = -1
                for m_field_index in stack[:-1]:
                    m_field = fields[m_field_index]
                    domains_equal = m_field in self.domain_equality[field]
                    if domains_equal:
                        m = max(m, m_field.index)

                # if an isomorphic candidate would be next...
                iso_candidate_is_next = field.index > m
                if iso_candidate_is_next:
                    # ...skip to the end of domain
                    indicies[i] = field.get_last_iso_index()

            indicies[i] += 1
            index_rolled_over = indicies[i] >= lengths[i]
            if index_rolled_over:
                # Reset to zero and continue to next index in the stack.
                indicies[i] = 0
                stack.pop()
                if stack == stop_stack:
                    return None
            else:
                break
        return indicies

    def iter_values(self):
        for indicies in self.iter_indicies():
            for field, index in itertools.izip(self.fields, indicies):
                field.index = index
            yield tuple(field.value for field in self.fields)

    def set(self, name, values, all=False):
        self.domain.set(name, values, all)

    def create(self, cls, num=1, none=False, init=False):
        """
        Create a ClassDomain with num items of the given class.

        If num is not given, it defaults to one.  If none is True, the None
        object will also be added to the domain.  If init is True, then the
        class' __init__ method will be used to create instances instead of the
        __new__ method.
        """
        class_domain = ClassDomain(self, cls, num, none=none, init=init)
        self.class_domains.append(class_domain)
        return class_domain

    def initialize(self):
        """
        Initialize all contained ClassDomains and their contained FieldDomains.
        """
        for class_domain in self.class_domains:
            class_domain.initialize()
        for class_domain in self.class_domains:
            class_domain.initialize_field_domains()
        self.cache_domain_equality()
        self.initialized = True

    def cache_domain_equality(self):
        """
        Cache domain equality for speeding up index iteration.

        Uses a mapping from each Field to the set of Fields with equal domains.
        """
        for field in self.fields:
            self.domain_equality[field] = set()
            for cache_field in self.fields:
                if field is not cache_field:
                    if field.domain == cache_field.domain:
                        self.domain_equality[field].add(cache_field)

    def add_field(self, field):
        """
        Add a Field object to the factory.  Used by ClassDomains during
        initialization.
        """
        if field.instance not in self.obj_fields:
            self.obj_fields[field.instance] = {}
        self.obj_fields[field.instance][field.name] = field
        order = len(self.fields)
        field.order = order
        self.fields.append(field)

    def record_field_access(self, field):
        if field not in self.accessed_fields:
            self.accessed_fields[field] = None

    def store_instance(self, instance):
        """
        Store the given instance in the warehouse with a relation back to
        this factory.
        """
        self.warehouse.instances[instance] = self


class Field(object):
    def __init__(self, instance, name, domain, order=None, index=0):
        self.instance = instance
        self.name = name
        self.domain = domain
        # Order within a Factory instance's list of Field objects.
        self.order = order
        self.index = index

    def get_index(self):
        return self._index

    def set_index(self, value):
        self._index = value
        try:
            del self._value
        except AttributeError:
            pass

    def get_last_iso_index(self):
        """
        Return the index representing the last value that is the same type as
        the current value.

        If this field's FieldDomain's all attribute is True, then just return
        the current index, as we are using all values.
        """
        if self.domain.all:
            return self.index
        current_type = type(self.value)
        length_of_domain = len(self.domain)

        i = self.index
        while (i < (length_of_domain - 1)
               and type(self.domain[i + 1]) == current_type):
            i += 1
        return i

    def get_value(self):
        if not hasattr(self, '_value'):
            self._value = self.domain[self.index]
        return self._value

    def set_value(self, value):
        self._value = value

    index = property(get_index, set_index)
    value = property(get_value, set_value)


class ClassDomain(list):
    """
    A custom list class that stores possible instances of a class that may be
    used for the finitization of a field.  Also allows finitization of fields
    of the stored instances, and keeps information about all Field and
    FieldDomain objects set up on this ClassDomain.
    """

    def __init__(self, factory, cls, num=1, none=False, instances=None,
                 init=False):
        """
        Normally, we are given a cls and num and create num instances of cls
        during initialization.  However, if instances is given, it should be
        one or more instances to use in place of having the initialization
        create them.
        """
        self.factory = factory
        self.cls = cls
        self.instances = instances
        self.num = num
        self.none = none
        self.init = init
        self.field_domains = OrderedDict()  # field name -> domain

        # This gets populated by the initialize method.
        self.fields = []
        # self is the list of instances.
        # self

    def __str__(self):
        return "<ClassDomain: %s>" % self

    @property
    def indicies(self):
        """The current index values for all Fields."""
        return tuple(field.index for field in self.fields)

    def initialize(self):
        self[:] = []
        self.fields = []
        if self.none:
            self.append(None)
        if self.instances:
            self.extend(self.instances)
        else:
            if self.init:
                self.extend([self.cls() for _ in xrange(self.num)])
            else:
                self.extend([self.cls.__new__(self.cls) for _ in xrange(self.num)])
        for obj in self:
            # None is special since it won't have any attributes/fields.
            if obj is None:
                continue
            self.factory.store_instance(obj)
            for field_name, domain in self.field_domains.iteritems():
                field = Field(obj, field_name, domain)
                self.fields.append(field)

        for field in self.fields:
            self.factory.add_field(field)

    def initialize_field_domains(self):
        for field_name, field_domain in self.field_domains.iteritems():
            field_domain.initialize()

    def set(self, name, values, all=False):
        """
        Set the field domain for the given attribute name.  If all is given,
        values of the same type will not be skipped when isomorphism breaking
        is enabled.
        """
        fd = FieldDomain(values, all=all)
        self.field_domains[name] = fd
        self.instrument_field(name)

    def instrument_field(self, name):
        """
        Replace the given attribute with a descriptor to record field access.
        """
        setattr(self.cls, name, FieldDescriptor(self.factory.warehouse, name))


class FieldDomain(list):
    """
    Represents the possible values for a single Field.

    Values are stored separated by type, for use when generating isomorphic
    structures.
    """

    def __init__(self, values, all=False):
        self.initialized = False
        # Flag that determine whether or not all values should be used when
        # isomorphism breaking is enabled.
        self.all = all
        # type -> list of values
        self.types = OrderedDict()
        self.lengths = OrderedDict()
        # Flattened values are stored as self.
        #self

        # Handling for when values is of type ClassDomain, which requires
        # initialization before we can use it.
        self.class_domains = []
        if isinstance(values, ClassDomain):
            self.class_domains.append(values)
        elif isinstance(values, FieldDomain):
            raise ValueError("values cannot be a FieldDomain instance")
        else:
            self.extend(values)

    def __str__(self):
        return '<FieldDomain: %s>' % super(FieldDomain, self).__str__()

    def __eq__(self, other):
        try:
            return self.types == other.types
        except AttributeError:
            return NotImplemented

    def __ne__(self, other):
        try:
            return self.types != other.types
        except AttributeError:
            return NotImplemented

    def initialize(self):
        """
        Must be called after ClassDomains have been initialized.
        """
        for class_domain in self.class_domains:
            # Don't sort or flatten here, since we do that when finished
            # processing all class domains.
            self.extend(class_domain, sort=False, flatten=False)
        self.sort_values()
        self.flatten_values()
        self.initialized = True

    def sort_values(self):
        """Sort the values in each type bucket."""
        for type, values in self.types.iteritems():
            self.types[type] = sorted(values)

    def flatten_values(self):
        self[:] = []
        list_extend = super(FieldDomain, self).extend
        for values in self.types.itervalues():
            list_extend(values)

    def extend(self, values, sort=True, flatten=True):
        """
        Add the list of values to this field domain.
        """
        for value in values:
            value_type = type(value)
            try:
                self.types[value_type].append(value)
            except KeyError:
                self.types[value_type] = [value]
            try:
                self.lengths[value_type] += 1
            except KeyError:
                self.lengths[value_type] = 1
        # Sort and flatten back out the values.
        if sort:
            self.sort_values()
        if flatten:
            self.flatten_values()


#
# Integration into unit testing.
#

from Queue import Empty
from multiprocessing import Process, Value, cpu_count, Lock, JoinableQueue, Condition


class TestCase(unittest.TestCase):
    """
    Overrides default TestCase class to implement iteration over all
    instantiated Variable object values.
    """

    num_processes = cpu_count()
    process_list = []
    good_total = Value('i')
    bad_total = Value('i')
    factories = []
    print_indicies = True
    print_lock = Lock()
    activity = Condition()
    shutdown = Value('b')

    def display(self, text):
        with self.print_lock:
            print text

    def search(self, i, queue):
        self.display('process %s starting' % i)

        factory = self.factories[i]
        good = 0
        bad = 0
        self.display('fields: %s' % list(f.name for f in factory.fields))

        while not self.shutdown.value:
            with self.activity:
                try:
                    start_indicies, stop_stack = queue.get(timeout=False)
                    self.display('process %s: pulled from queue: %s %s' % (i, start_indicies, stop_stack))
                except Empty:
                    self.display('process %s: waiting for activity' % i)
                    self.activity.wait(timeout=0.1)
                    continue

            for indicies in factory.iter_indicies(start_indicies, stop_stack,
                                                  queue=queue,
                                                  activity=self.activity):
                factory.apply_indicies(indicies)
                if self.repOK(factory):
                    good += 1
                    if self.print_indicies:
                        self.display('process %s: %s ***good***' % (i, factory))
                    self.run_method(factory)
                else:
                    bad += 1
                    if self.print_indicies:
                        self.display('process %s: %s - bad' % (i, factory))
            queue.task_done()
        self.good_total.value += good
        self.bad_total.value += bad
        self.display('process %s exiting' % i)

    def test(self):
        work_queue = JoinableQueue()

        # Construct a factory object for each process.
        for i in range(self.num_processes):
            factory = self.fin()
            factory.initialize()
            self.factories.append(factory)

        # Place starting indicies in queue (indicies, accessed fields)
        indicies = [0] * len(self.factories[0].fields)
        work_queue.put((indicies, []))

        for i in range(self.num_processes):
            proc = Process(target=self.search, args=(i, work_queue))
            self.process_list.append(proc)
            proc.start()
        work_queue.join()
        self.shutdown.value = True
        with self.activity:
            self.activity.notify_all()
        for proc in self.process_list:
            proc.join()

        good = self.good_total.value
        bad = self.bad_total.value
        dashes = '-' * 15
        print ('\n%s\n Good: %8d\n  Bad: %8d\nTotal: %8d\n%s'
               % (dashes, good, bad, good + bad, dashes))
        print 'done.'
