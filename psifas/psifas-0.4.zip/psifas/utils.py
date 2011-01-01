# Copyright 2010 Oren Zomer <oren.zomer@gmail.com>
#
# This file is part of pypsifas.

# pypsifas is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# pypsifas is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with pypsifas.  If not, see <http://www.gnu.org/licenses/>.

from copy import deepcopy
from itertools import izip, imap, tee
import operator
from collections import defaultdict
from collections import deque as _deque
import thread
from functools import wraps
from os import SEEK_CUR
from weakref import WeakValueDictionary
try:
    from io import BytesIO
except ImportError:
    from cStringIO import StringIO as BytesIO

try:
    import scapy.all as _scapy
except ImportError:
    _scapy = None
    

from psifas_exceptions import *

try:
    _deque(maxlen=1)
except TypeError:
    class LimitedDeque(_deque):
        def __init__(cls, iterable, maxlen):
            super(LimitedDeque, self).__init__(iterable)
            self.__maxlen = maxlen
            
        def appendleft(self, *args, **kw):
            try:
                return super(LimitedDeque, self).appendleft(*args, **kw)
            finally:
                if len(self) > self.__maxlen:
                    self.pop()

        def extendleft(self, var):
            try:
                return super(LimitedDeque, self).extendleft(var)
            finally:
                while len(self) > self.__maxlen:
                    self.pop()
            
        def append(self, *args, **kw):
            try:
                return super(LimitedDeque, self).append(*args, **kw)
            finally:
                if len(self) > self.__maxlen:
                    self.popleft()

        def extend(self, var):
            try:
                return super(LimitedDeque, self).extend(var)
            finally:
                while len(self) > self.__maxlen:
                    self.popleft()

    def deque(iterable = (), maxlen = None):
        if maxlen is None:
            return _deque(iterable)
        return LimitedDeque(iterable, maxlen)
else:
    deque = _deque

class RecursionLockException(AssertionError):
    """
    This error is an assertion error - not just an error of usage.
    """
    pass

_recursion_lock_sets = defaultdict(deque)

def recursion_lock(replace_func, exclude = ()):
    """
    replace_func - the function to use in case of recursion
    exclude - a list\tuple of the names & indexes of the args to ignore when checking for recursion.
    for example, see the pretty_str func, in whchi the 'nesting' variable (given in the kws or
    arg #1) is increased in every sub-call, and by ignoring it we can still find out if a recursive
    call happend.
    """
    def decorator(func):
        dummy = object()
        @wraps(func)
        def new_func(*args, **kws):
            recursion_lock_set = _recursion_lock_sets[thread.get_ident()]
            if len(exclude) == 0:
                key_args = args
                key_kws = kws
            else:
                key_args = tuple(arg for ind, arg in enumerate(args) if ind not in exclude)
                key_kws = kws.copy()
                for name in exclude:
                    key_kws.pop(name, None)
            for (rec_func, rec_args, rec_kws) in recursion_lock_set:
                if (func is rec_func) and \
                   (len(key_args) == len(rec_args)) and \
                   all(key_arg is rec_arg for (key_arg, rec_arg) in izip(key_args, rec_args)) and \
                   (len(key_kws) == len(rec_kws)) and \
                   all((value is rec_kws.get(name, dummy)) for (name, value) in key_kws.iteritems()):
                    return replace_func(*args, **kws)
            recursion_key = (func, key_args, key_kws)
            recursion_lock_set.append(recursion_key)
            try:
                rle = None
                return func(*args, **kws)
            except RecursionLockException, rle:
                raise
            finally:
                if rle is None:
                    try:
                        if recursion_lock_set.pop() is not recursion_key:
                            raise RecursionLockException("the recursion-lock set top key is not the expected value")
                    except IndexError:
                        RecursionLockException("the recursion-lock set top key does not exists")
                        
                    if len(recursion_lock_set) == 0:
                        if _recursion_lock_sets.pop(thread.get_ident(), None) is not recursion_lock_set:
                            raise RecursionLockException("the recursion-lock set was misused and is not in the set of all recursion-lock sets")
        return new_func
    return decorator

def on_recursion(*args, **kw):
    print 'recursion detected', args, kw

def pairwise(iterable):
    a, b = tee(iterable)
    next(b, None)
    return izip(a, b)

class _singleton_metaclass(type):
    def __new__(mcs, name, bases, namespace):
        """
        instead of returning the new type, it returns a new instance of the new type.
        """
        return type.__new__(mcs, name, bases, namespace)()

class Singleton(object):
    def __metaclass__(name, bases, namespace):
        """
        every subclass of Singleton will be created with _singleton_metaclass
        """
        return type.__new__(_singleton_metaclass, name, bases, namespace)

    def __repr__(self):
        return '<%s>' % (self.__class__.__name__,)

    def __deepcopy__(self, memo):
        return self

    def __reduce__(self):
        """
        makes it pickleable
        """
        return self.__class__.__name__

def imerge(a, b):
    """
    Tries to inclusive-merge 'a' with 'b'.
    Returns 2 values:
    - the merged value (if it was inclusive, it will be the object 'a')
    - a boolean whether the merge did any changes
    """
    if (a is b) or (a == b):
        return a, False
    if isinstance(b, DumbMerge) and not isinstance(a, DumbMerge):
        # A merge of any value with DumbMerge will return the samve value.
        # If both values are DumbMerge, their imerge will be called.
        return a, False
    return getattr(a.__class__, 'imerge', _builtins_imerge)(a, b)

def _builtins_imerge(a, b):
    """
    How merge works for types that does not have the imerge function
    """
    if operator.isSequenceType(a) and operator.isSequenceType(b):
        if tuple(a) == tuple(b):
            return a, False
    if operator.isNumberType(a) and operator.isNumberType(b) and (isinstance(a, float) or isinstance(b, float)):
        if abs(a - b) < 5e-15:
            return a, False
    if (_scapy is not None) and isinstance(a, _scapy.Packet) and isinstance(b, _scapy.Packet) and str(a) == str(b):
        a_layer = a
        b_layer = b
        while not isinstance(a_layer, _scapy.NoPayload) or not isinstance(b_layer, _scapy.NoPayload):
            if a_layer.__class__ is not b_layer.__class__:
                break
            a_layer = a_layer.payload
            b_layer = b_layer.payload
        else:
            return a, False
        
    raise MergeException('Objects could not be merged', a, b)

class DumbMerge(object):
    dumb_merge_hierarchy = 0

    def _dumb_merge_key(self):
        return (self.dumb_merge_hierarchy, self)
    
    def imerge(self, other):
        if not isinstance(other, DumbMerge):
            return other, True
        better_dumb = max(self, other, key = DumbMerge._dumb_merge_key)
        return better_dumb, better_dumb is other

class NoValue(Singleton, DumbMerge):
    __slots__ = []

    dumb_merge_hierarchy = 1

    def __nonzero__(self):
        return False
    # for python3:
    __bool__ = __nonzero__

class Default(Singleton, DumbMerge):
    """
    The difference between NoValue, AcceptAll, and Default is in the parsing-dependency.
    When the _parse function returns NoValue, it means that it failed to calculate what it needs,
    and if it keeps happening with incrementation of 'process', an exception will be raised on
    'missing dependencies'.
    When the _parse function returns AcceptAll, it means that the calculation has finished, but
    nothing will be put in the context. Therefore other Psifases that depend on this context may
    not be executed until someone else puts a real value in that context - the context stays
    with NoValue.
    When the _parse function returns Default, the context's value is filled with Default. This
    value can dumb-merge with any other value. The other Psifases will be fully executed, and
    will se the value Default in that context.
    """
    __slots__ = []
    
    dumb_merge_hierarchy = 2

Ignore = Default
    
class Finished(Singleton):
    def __iadd__(self, other):
        return self
    
class AcceptAll(Singleton): pass

class _PathFromElements(dict):
    max_size = 10**4
    
    def __missing__(self, elements):
        if len(self) >= size:
            self.clear()
        self[elements] = instance = Path._from_elements(elements)
        return instance

class _PathFromString(dict):
    """
    This mapping contains a link to a path_from_elements mapping,
    and automatically checks it and updates it when a key is missing.
    """
    max_size = 10**4
    
    def __init__(self, path_from_elements):
        super(_PathFromString, self).__init__()
        self.path_from_elements = path_from_elements

    def __missing__(self, path_string):
        if len(self) >= self.max_size:
            self.clear()
        self[path_string] = instance = self.path_from_elements[path_string.split('/')]
        return instance

class Path(object):
    __slots__ = ['__elements', '__weakref__']

    # This deque exists inorder to keep the last 10**4 paths "alive", even
    # if noone holds their instance. This makes their recreation faster.
    _last_paths = deque(maxlen = 10**4)

    _from_string = WeakValueDictionary()
    _from_elements = WeakValueDictionary()

    _special_elements = frozenset(('', '.', '..', '...'))

    @property
    def elements(self):
        return self.__elements

    @classmethod
    def _from_simplified_elements(cls, elements):
        """
        This constructor simply creates a new instance, without
        updating the maps (_from_string, _from_elements).

        Assumes elements is a tuple.
        """
        instance = super(Path, cls).__new__(cls)
        instance.__elements = elements
        cls._last_paths.append(instance)
        return instance

    @classmethod
    def _simplify(cls, elements):
        parent_level = 0
        simplified_elements = []
        for element in reversed(elements):
            if element in cls._special_elements:
                if element == '..':
                    parent_level += 1
                elif element == '...':
                    simplified_elements += ['..'] * parent_level
                    simplified_elements.append('...')
                    parent_level = 0
            elif parent_level > 0:
                parent_level -= 1
            else:
                simplified_elements.append(element)
        simplified_elements += ['..'] * parent_level
        simplified_elements.reverse()
        return simplified_elements

    @classmethod
    def from_elements(cls, elements):
        """
        This constructor tries to retrieve the path from the _from_elements
        mapping. On failure, updates the mapping with the new instance.
        """
        elements = tuple(elements)
        instance = cls._from_elements.get(elements, None)
        if instance is None:
            simplified_elements = tuple(cls._simplify(elements))
            instance = cls._from_elements.get(simplified_elements, None)
            if instance is None:
                cls._from_elements[simplified_elements] = instance = cls._from_simplified_elements(simplified_elements)
            cls._from_elements[elements] = instance
        return instance

    def __new__(cls, path_string=''):
        """
        This constructor tries to retrieve the path from the _from_string
        mapping. On failure, updates the mapping with the new instance.
        """
        instance = cls._from_string.get(path_string, None)
        if instance is None:
            cls._from_string[path_string] = instance = cls.from_elements(path_string.split('/'))
        return instance

    def join(self, other):
        """
        This constructor acts like from_elements.
        However, because we know that self.__elements and other.__elements are already simplified
        we can simplifiy their concatenation in a faster way.
        """
        elements = self.__elements + other.__elements
        instance = self._from_elements.get(elements, None)
        if instance is None:
            # a faster way to simplify the sum
            index = 0
            for index, (parent, other_element) in enumerate(izip(reversed(self.__elements), other.__elements)):
                if (other_element != '..') or (parent in ('..', '...')):
                    break
            if index > 0:
                simplified_elements = self.__elements[:-index] + other.__elements[index:]
                instance = self._from_elements.get(simplified_elements, None)
                if instance is None:
                    self._from_elements[simplified_elements] = instance = self._from_simplified_elements(simplified_elements)
            else:
                # already simplified
                instance = self._from_simplified_elements(elements)
        self._from_elements[elements] = instance
        return instance

    def to_string(self):
        return ('/'.join(self.__elements)) or '.'

    def __repr__(self):
        return '%s(%r)' % (self.__class__.__name__, self.to_string())

    def __eq__(self, other):
        if self is other:
            return True
        if not isinstance(other, Path):
            return super(Path, self) == other
        return self.__elements == other.__elements
    
    def __hash__(self):
        return hash(self.__elements)

    def __deepcopy__(self, o):
        return self

class Link(Path):
    _from_string = WeakValueDictionary()
    _from_elements = WeakValueDictionary()
    
    def is_broken(self, context):
        try:
            if context.sub_context(self).value is not NoValue:
                return False
        except DereferenceException:
            pass
        return True

class Context(object):
    __slots__ = ['value', 'value_locations', 'spiritual', 'files', 'parent_stack', 'is_link']

    max_visited_links = 100

    @classmethod
    def _increase_max_visited_links(cls):
        cls.max_visited_links *= 2

    def __init__(self, parent = None):
        super(Context, self).__init__()

        self.value = NoValue
        self.value_locations = []
        if parent is not None:
            self.parent_stack = (parent,) + parent.parent_stack
        else:
            self.parent_stack = ()
        self.spiritual = False
        self.files = {'.': self}
        self.is_link = False

    @classmethod
    def from_value(cls, value):
        context = cls()
        context.value = value
        return context

    def get_file(self, name):
        result = self.files.get(name, None)
        if result is None:
            self.files[name] = result = Context(self)
        return result

    def set_value(self, value, value_location):
        if (value is NoValue) or (value is AcceptAll):
            return

        if value_location not in self.value_locations:
            value_location.proceed()
            self.value_locations.append(value_location)

        if self.value == value:
            return
        try:
            self.value, merge_flag = imerge(self.value, value)
            if merge_flag:
                value_location.proceed()
                if isinstance(self.value, Link):
                    self.is_link = True
                    # for debugging, we don't allow links to contain files at all.
                    del self.files
        except MergeException:
            raise Contradiction("new value %r found from %s contradicts old value %r found from: %s" %
                                (value,
                                 value_location,
                                 self.value,
                                 ', '.join(str(vl) for vl in self.value_locations if vl is not value_location)))

    def _deref(self, visited_links):
        # assert self.is_link
        if len(visited_links) > self.max_visited_links:
            if self in visited_links:
                raise InfiniteRecursionException("Links point to each other and create infinite dereference loop", self)
            else:
                # the max_visited_links estimation was too low
                self._increase_max_visited_links()
        visited_links.append(self)
        return self.parent_stack[0]._sub_context(self.value, visited_links)

    # the following function do not receive "self" in purpose.

    def _normal_parent(parent_stack, target, element, visited_links):
        return parent_stack.popleft()

    def _spiritual_parent(parent_stack, target, element, visited_links):
        target = parent_stack.popleft()
        while not target.spiritual:
            target = parent_stack.popleft()
        return target

    @staticmethod
    def _normal_element(parent_stack, target, element, visited_links):
        parent_stack.appendleft(target)

        target = target.get_file(element)
        if target.is_link:
            return target._deref(visited_links)
        return target

    _sub_context_func = {'..': _normal_parent,
                         '...': _spiritual_parent}

    def sub_context(self, full_path):
        try:
            return self._sub_context(full_path, [])
        except IndexError, e:
            raise DereferenceException("cannot deref to: %s" % (full_path,), e)

    def _sub_context(self, full_path, visited_links):
        if self.is_link:
            target = self._deref(visited_links)
        else:
            target = self

        parent_stack = deque(self.parent_stack)

        for element in full_path.elements:
            target = self._sub_context_func.get(element, self._normal_element)(parent_stack,
                                                                               target,
                                                                               element,
                                                                               visited_links)
        return target

    @recursion_lock(lambda indent, indent_string, recursive: "(RECURSION IN TREE!)", exclude = (0, 'indent', 1, 'indent_string'))
    def ls_iter(self, indent = 0, indent_string = '   ', recursive = False):
        """
        Aid function to iterate over the textual format of the child-contexts.
        """
        if not hasattr(self, 'files'):
            yield '<link does not have files>'
            return
        for name, sub_context in sorted(self.files.iteritems()):
            if name == '.':
                continue
            spiritual = '*' if sub_context.spiritual else ''
            if isinstance(sub_context.value, Link):
                yield '%s%s%s -> %s%s' % ((indent_string * indent), name, spiritual,
                                          sub_context.value.to_string(), ' ???' if sub_context.value.is_broken(self) else '')
            else:
                yield '%s%s%s: %r' % ((indent_string * indent), name, spiritual, sub_context.value)
                if recursive:
                    for line in sub_context.ls_iter(indent + 1, indent_string, recursive):
                        yield line

    def ls(self, indent_string = '   ', recursive = False):
        """
        Aid function to return a tuple of the textual format of the child-contexts.
        If you want a recurisve ls without indentations, use indent_string = ''.
        """
        return tuple(self.ls_iter(indent_string = indent_string, recursive = recursive))

    def tree(self):
        """
        Joins a recursive ls to a string
        """
        return '\n'.join(self.ls_iter(recursive = True))

    def name(self):
        """
        Gets the name of the context from its parent context.
        This is a heavy operation.
        """
        if len(self.parent_stack) == 0:
            return ''
        for name, value in getattr(self.parent_stack[0], 'files', {}).iteritems():
            if value is self:
                return name
        return "<not found in parent's files>"

    @recursion_lock(lambda self: '%s(...)' % (self.__class__.__name__,))
    def __repr__(self):
        return '%s(%r%s)' % (self.__class__.__name__, self.value,
                             ''.join(map(', %s = %r'.__mod__,
                                         sorted((name, value) for (name, value) in
                                                getattr(self, 'files', {}).iteritems()
                                                if name != '.'))))

    @recursion_lock(lambda self: '%s(...)' % (self.__class__.__name__,))
    def __str__(self):
        try:
            return '%s(%s/%s)' % (self.__class__.__name__,
                                  '/'.join(parent.name() for parent in reversed(self.parent_stack)),
                                  self.name())
        except AttributeError:
            # If someone illegally played with the parent_stack, we still want to
            # be able to do str()
            return super(Context, self).__str__()

class _Location(list):
    """
    In this partial class _context is not set.
    When TopLocation is initialized, it creates a new Context.
    When Location is initialized, it creates a sub-context from its parent.
    """
    __slots__ = ['parent', 'index', 'full_name', '_context',
                 'process', 'stream', 'payload',
                 'decipher_finished', 'stream_finished', 'parent_stream_used', 'parent_stream_borrowed', 'subpayloads_verified',
                 'try_copy', 'try_exception']

    def __init__(self, index, full_name, parent):
        super(_Location, self).__init__()

        # assert '/' not in full_name
        # assert full_name not in ('', '..')

        self.parent = parent
        self.index = index
        self.full_name = full_name

        self.process = 0
        self.stream = None
        self.payload = None

        self.decipher_finished = False
        self.stream_finished = False
        self.parent_stream_used = False
        self.parent_stream_borrowed = False
        self.subpayloads_verified = False

        # a place for the Try class to save the tree-copy
        self.try_copy = None
        self.try_exception = None

    def parent_stream(self):
        raise NotImplementedError

    def iter_fields(self, fields):
        """
        Iterates over the sub-locations.
        If the sub-locations does not exist - automatically creates them.
        """
        current_len = len(self)
        if current_len < len(fields):
            # adds the new fields
            self.extend(Location(current_len + index, field.full_name, self) for index, field
                        in enumerate(fields[current_len:]))
            self.proceed()
        return iter(self)

    def get_field(self, index, full_name = '.'):
        """
        If the number of sub-locations is smaller then 'index',
        creates new ones with the given name (Usually only one).
        """
        current_len = len(self)
        if current_len > index:
            return self[index]
        self.extend(Location(new_index, full_name, self) for new_index in xrange(current_len, index + 1))
        self.proceed()
        return self[-1]

    def iter_names(self):
        """
        iterator on the sub_locations' names
        """
        return (sub_location.full_name for sub_location in self)

    def names(self):
        """
        returns a list of the sub-locations' names
        """
        return list(self.iter_names())

    @recursion_lock(lambda self: '%s(%r, ...)' % (self.__class__.__name__, self.full_name))
    def __repr__(self):
        return '%s(%r%s)' % (self.__class__.__name__, self.full_name,
                             (', process = %s' % (self.process,) if self.process is not Finished else ''))

    def __str__(self):
        return '%s(/%s)' % (self.__class__.__name__,
                            '/'.join('%s:%s' % (parent.index, parent.full_name)
                                     for parent in self.parent_stack()[1:]))

    def find_iter(self, full_name):
        """
        finds the sub-locations with the given name
        """
        for sub_location in self:
            if sub_location.full_name == full_name:
                yield sub_location

    def find(self, full_name):
        return list(self.find_iter(full_name))

    def reload_location(self, location):
        self._context = location._context
        self.process = location.process
        self.stream = location.stream
        if isinstance(self.stream, PsifasStream):
            if self.stream.reload_offset is not None:
                self.stream.seek(self.stream.reload_offset)
        self.payload = location.payload
        self.decipher_finished = location.decipher_finished
        self.stream_finished = location.stream_finished
        self.parent_stream_used = location.parent_stream_used
        self.parent_stream_borrowed = location.parent_stream_borrowed
        self.subpayloads_verified = location.subpayloads_verified

        self.try_copy = location.try_copy
        self.try_exception = location.try_exception

        del self[len(location):]

        for self_child, child in izip(self, location):
            self_child.reload_location(child)

    def set_payload(self, payload):
        if self.payload is None:
            if not isinstance(payload, str):
                raise Contradiction("new payload is not a string", payload)
            self.payload = payload
            self.proceed()
        elif self.payload != payload:
            raise Contradiction("new payload contradicts old payload", payload, self.payload)

    def proceed(self):
        self.process += 1

    def context(self, rel_path_str = None):
        if rel_path_str is None:
            return self._context
        return self._context.sub_context(Path(rel_path_str))

    def parent_stack(self):
        stack = [self]
        current = self.parent
        while current is not None:
            stack.append(current)
            current = current.parent
        stack.reverse()
        return stack
                                 
    def top_parent(self):
        current = self
        while current.parent is not None:
            current = current.parent
        return current

class Location(_Location):
    def __init__(self, index, full_name, parent):
        super(Location, self).__init__(index, full_name, parent)
        self._context = parent._context.get_file(full_name.split('$', 1)[0])

    def parent_stream(self):
        return self.parent.stream

class TopLocation(_Location):
    __slots__ = _Location.__slots__ + ['ghosts']

    def __init__(self, stream = None, full_name = '.'):
        super(TopLocation, self).__init__(0, full_name, None)
        self._context = Context()
        self.ghosts = []
        if stream is not None:
            if not isinstance(stream, PsifasStream):
                stream = PsifasStream(stream)
            self.stream = stream

    def create_ghost(self):
        current_ghosts = self.ghosts
        try:
            del self.ghosts
            current_ghosts.append(deepcopy(self))
            return len(current_ghosts) - 1
        finally:
            self.ghosts = current_ghosts

    def load_ghost(self, index):
        pre_process = self.process
        self.reload_location(self.ghosts[index])
        self.process = pre_process

    def parent_stream(self):
        return None

class Container(DumbMerge):
    dumb_merge_hierarchy = 3

    def __init__(self, *args, **kw):
        self.__dict__['_Container__fields_order'] = deque()
        super(Container, self).__init__()
        for name, value in args:
            setattr(self, name, value)
        for name, value in sorted(kw.iteritems()):
            setattr(self, name, value)

    def __setattr__(self, name, value):
        if not self.__dict__.has_key(name):
            self.__fields_order.append(name)
        super(Container, self).__setattr__(name, value)

    def __delattr__(self, name):
        if name in self.__fields_order:
            self.__fields_order.remove(name)
        super(Container, self).__delattr__(name)

    @recursion_lock(lambda self, other: (self, False))
    def imerge(self, other):
        if not isinstance(other, Container):
            return super(Container, self).imerge(other)
        if self is other:
            return self, False
        change_flag = False
        for field in other.__fields_order:
            sub_value, sub_flag = imerge(getattr(self, field, NoValue),
                                         getattr(other, field))
            if sub_flag:
                setattr(self, field, sub_value)
                change_flag = True
        return self, change_flag

    def iter_fields(self):
        order = self.__fields_order
        for field in order:
            yield field, getattr(self, field)

    @recursion_lock(lambda self, other: True)
    def __eq__(self, other):
        if self is other:
            return True
        if not isinstance(other, Container):
            return super(Container, self) == other
        sorted_fields = sorted(self.__fields_order)
        if sorted_fields != sorted(other.__fields_order):
            return False
        return all(getattr(self, field) == getattr(other, field) for field in sorted_fields)

    @recursion_lock(lambda self: '%s(...)' % (self.__class__.__name__,))
    def __str__(self):
        return '%s(%s)' % (self.__class__.__name__,
                           ', '.join({False: '%s = %r', True: '%s = %s'}[isinstance(value, Container)] % (name, value)
                           for name, value in self.iter_fields() if not name.startswith('_')))

    @recursion_lock(lambda self: '%s(...)' % (self.__class__.__name__,))
    def __repr__(self):
        return '%s(%s)' % (self.__class__.__name__,
                           ', '.join('%s = %r' % (name, value) for (name, value) in self.iter_fields() if not name.startswith('__')))

class DefaultContainer(Container):
    def __getattr__(self, name):
        return getattr(super(DefaultContainer, self), name, Default)

class PsifasStream(object):
    __slots__ = ['stream', 'reload_offset']
    def __init__(self, stream, reload_offset = None):
        super(PsifasStream, self).__init__()
        if isinstance(stream, str):
            stream = BytesIO(stream)
        self.stream = stream
        self.reload_offset = reload_offset

    def __getattr__(self, name):
        return getattr(self.stream, name)

    def read(self, size, best_effort = False):
        first_part = self.stream.read(size)
        size -= len(first_part)
        all_parts = []
        while size > 0:
            # usually doesn't happen
            new_part = self.stream.read(size)
            if new_part == '':
                if best_effort:
                    break
                self.stream.seek(-len(first_part) - sum(map(len, all_parts)), SEEK_CUR)
                raise EndOfStreamException()
            size -= len(new_part)
        return first_part + ''.join(all_parts)

    def read_all(self):
        all_parts = [self.stream.read()]
        new_part = self.stream.read()
        while new_part != '':
            all_parts.append(new_part)
            new_part = self.stream.read()
        return ''.join(all_parts)

    def is_eof(self):
        c = self.stream.read(1)
        if len(c) == 0:
            return True
        self.stream.seek(-1, SEEK_CUR)
        return False

    def __deepcopy__(self, memo):
        return PsifasStream(self.stream, self.stream.tell())

