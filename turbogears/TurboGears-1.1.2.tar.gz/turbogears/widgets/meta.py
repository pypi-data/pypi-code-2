import copy
import threading
import warnings

from inspect import isclass
from itertools import count, ifilter
from new import instancemethod

from turbogears import validators
from turbogears.util import setlike
from formencode.schema import Schema

# FIXME-dbr: we need to make kid-support pluggable or such.
try:
    import kid
except ImportError:
    pass

__all__ = ["MetaWidget", "load_kid_template"]

param_prefix = '_param_'

class MetaWidget(type):
    """The meta class for widgets."""

    def __new__(cls, name, bases, dct):
        # Makes sure we get the union of params and member_widgets
        # from all our bases.
        params = setlike(dct.get('params', []))
        member_widgets = setlike(dct.get('member_widgets', []))
        compound = False
        for base in bases:
            params.add_all(getattr(base, 'params', []))
            if getattr(base, 'compound', False):
                member_widgets.add_all(getattr(base, 'member_widgets', []))
                compound = True
        for param in params:
            # Swap all params listed at 'params' with a ParamDescriptor
            try:
                dct[param_prefix + param] = dct[param]
                dct[param] = ParamDescriptor(param)
            except KeyError:
                for base in bases:
                    if hasattr(base, param):
                        break
                else:
                    # not declared in any superclass, let default be None
                    dct[param_prefix + param] = None
                    dct[param] = ParamDescriptor(param)
        params = list(params)
        dct['params'] = params
        if compound:
            dct['member_widgets'] = list(member_widgets)
        # Pick params_doc from all bases giving priority to the widget's own
        params_doc = {}
        for base in bases:
            params_doc.update(getattr(base, 'params_doc', {}))
        params_doc.update(dct.get('params_doc', {}))
        dct['params_doc'] = params_doc
        return super(MetaWidget, cls).__new__(cls, name, bases, dct)

    def __init__(cls, name, bases, dct):
        if "__init__" in dct:
            dct["__init__"] = _decorate_widget_init(dct["__init__"])
            cls.__init__ = dct["__init__"]
        super(MetaWidget, cls).__init__(name, bases, dct)
        if cls.template:
            (cls.template_c, cls.template) = load_kid_template(cls.template)
        cls._locked = False

#############################################################################
# Method decorators and other MetaWidget helpers                            #
#############################################################################

class ParamDescriptor(object):
    """Descriptor to support automatic callable support for widget params."""
    def __init__(self, param_name):
        self.param_name = param_prefix + param_name

    def __get__(self, obj, typ=None):
        if obj is None:
            # return the original class attribute. This makes the descriptor
            # almost invisible
            return getattr(typ, self.param_name)
        param = getattr(obj, self.param_name)
        if callable(param):
            return param()
        return param

    def __set__(self, obj, value):
        setattr(obj, self.param_name, value)

def lockwidget(self, *args, **kw):
    """Set this widget as locked the first time it's displayed."""
    gotlock = self._displaylock.acquire(False)
    if gotlock:
        del self.display
        self._locked = True
    output = self.__class__.display(self, *args, **kw)
    if gotlock:
        self._displaylock.release()
    return output

def _decorate_widget_init(func):
    """Decorator for a widgets __init__ method.

    Ensures that the display method for the instance is overridden by
    lockwidget, that an eventual validator dict is applied to the widget
    validator and that a validation schema is generated for compound widgets.

    """
    def widget_init(self, *args, **kw):
        self.display = instancemethod(lockwidget, self, self.__class__)
        # We may want to move the InputWidget related logic to another
        # decorator
        input_widget = hasattr(self, "validator")
        # Makes sure we only generate a schema once in the all __init__
        # cooperative calls from subclasses. Same for the displaylock
        if not hasattr(self, '__initstack'):
            self._displaylock = threading.Lock()
            self.__initstack = []
        else:
            self.__initstack.append(True)
        # Manage an eventual validator dictionary that provides additional
        # parameters to the default validator (if present).
        # We remove it from kw and apply it after the execution of the
        # decorated __init__ method since only at this point we can check
        # for the presence of a default validator
        if input_widget and ("validator" in kw) \
           and isinstance(kw["validator"], dict):
            validator_dict = kw.pop("validator")
        else:
            validator_dict = None
        # Execute the decorated __init__ method
        func(self, *args, **kw)
        try:
            self.__initstack.pop()
        except IndexError:
            # We're the first __init__ called
            del self.__initstack
            if input_widget:
                # Apply an eventual validator dictionary
                if validator_dict:
                    if self.validator is not None:
                        class_validator = self.__class__.validator
                        if self.validator is class_validator:
                            # avoid modifying a validator that has been
                            # defined at class level and therefor is
                            # shared by all instances of this widget
                            self.validator = copy.deepcopy(class_validator)
                        self.validator.__dict__.update(validator_dict)
                    else:
                        raise ValueError, ("You can't use a dictionary to "
                                           "provide additional parameters "
                                           "as the widget doesn't provide a "
                                           "default validator" )
                # Generate the validation Schema if we are a compound widget
                if getattr(self, 'compound', False):
                    widgets = self.iter_member_widgets()
                    # generate the schema associated to our widgets
                    validator = generate_schema(self.validator, widgets)
                    if getattr(self, 'repeating', False):
                        self.validator = validators.ForEach(validator)
                    else:
                        self.validator = validator
    return widget_init

#############################################################################
# Widget template support.                                                  #
#############################################################################

# Keeps a count of the widget instances which have overrided their template on
# the constructor so we can generate unique template-module names
widget_instance_serial = count()

# XXX: Maybe Widget should have a __del__ method to unload any template that
#      has been loaded during the instances initialization?
# FIXME-dbr: This is returning nonsens in case KID isn't imported because
# we want to get rid of KID as a dependency - and as long as the widgets
# are in TG itself, that leads no not-so-beautiful compromises.
def load_kid_template(t, modname=None):
    """Load the given template into the given module name.

    If modname is None, an unique one will be generated.
    Returns a tuple (compiled_tmpl, template_text (or modulepath).

    """
    # this is a dummy-value-return-thingy, see above comment
    try:
        kid
    except NameError:
        return None, None

    if isinstance(t, basestring) and "<" in t:
        if not modname:
            modname = 'instance_template_%d' % widget_instance_serial.next()
        return (kid.load_template(t, name=modname).Template, t)
    else:
        return (t, None)

#############################################################################
# Schema generation support                                                 #
#############################################################################
class NullValidator(validators.FancyValidator):
    """A do-nothing validator.

    Used as a placeholder for fields with no validator so they don't get
    stripped by the Schema.

    """
    if_missing = None

def copy_schema(schema):
    """Recursively copy a schema."""
    new_schema = copy.copy(schema)
    new_schema.pre_validators = schema.pre_validators[:]
    new_schema.chained_validators = schema.chained_validators[:]
    fields = {}
    for k, v in schema.fields.iteritems():
        if isinstance(v, Schema):
            v = copy_schema(v)
        fields[k] = v
    new_schema.fields = fields
    return new_schema

def merge_schemas(to_schema, from_schema, inplace=False):
    """Recursively merge from_schema into to_schema

    Takes care of leaving to_schema intact if inplace is False (default).
    Returns a new Schema instance if inplace is False or to_schema is a Schema
    class not an instance or the changed to_schema.

    """
    # Nested schemas may be Schema (sub-)classes instead of instances.
    # Copying Schema classes does not work, so we just create an instance.
    if isclass(to_schema) and issubclass(to_schema, validators.Schema):
        to_schema = to_schema()
    elif not inplace:
        to_schema = copy_schema(to_schema)

    # Recursively merge child schemas
    is_schema = lambda f: isinstance(f[1], validators.Schema)
    seen = set()
    for k, v in ifilter(is_schema, to_schema.fields.iteritems()):
        seen.add(k)
        from_field = from_schema.fields.get(k)
        if from_field:
            v = merge_schemas(v, from_field)
            to_schema.add_field(k, v)

    # Add remaining fields if we can
    can_add = lambda f: f[0] not in seen and can_add_field(to_schema, f[0])
    for field in ifilter(can_add, from_schema.fields.iteritems()):
        to_schema.add_field(*field)

    return to_schema

def add_field_to_schema(schema, widget):
    """Add widget's validator if any to the given schema."""
    name = widget.name
    if widget.validator is not None:
        if isinstance(widget.validator, validators.Schema):
            # Schema instance or class, might need to merge 'em...
            if widget.name in schema.fields:
                assert (isinstance(schema.fields[name], validators.Schema) or
                    issubclass(schema.fields[name], validators.Schema)
                    ), "Validator for '%s' should be a Schema subclass" % name
                v = merge_schemas(schema.fields[name], widget.validator)
            else:
                v = widget.validator
            schema.add_field(name, v)
        elif can_add_field(schema, name):
            # Non-schema validator, add it if we can...
            schema.add_field(name, widget.validator)
    elif can_add_field(schema, name):
        schema.add_field(name, NullValidator())

def generate_schema(schema, widgets):
    """Generate or extend a copy of schema with all validators of all widgets.

    schema may be a schema instance or class, widgets is a list of widgets
    instances.
    Returns the new schema instance.

    """
    if schema is None:
        schema = validators.Schema()
    elif isclass(schema) and issubclass(schema, validators.Schema):
        # allows to attach Schema (sub-)classes to widgets.
        schema = schema()
    else:
        schema = copy_schema(schema)
    for widget in widgets:
        if widget.is_named:
            add_field_to_schema(schema, widget)
    return schema

def can_add_field(schema, field_name):
    """Checks if we can safely add a field.

    Makes sure we're not overriding any field in the Schema. NullValidators
    are ok to override.

    """
    current_field = schema.fields.get(field_name)
    return bool(current_field is None or
                isinstance(current_field, NullValidator))
