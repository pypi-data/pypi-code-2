import re
import types
from inspect import getargspec, isclass
from rumcomponent.util import NoDefault
from rumcomponent.util import import_string

__all__ = ["import_string", "adapt_call", "safe_issubclass", "NoDefault",
           "generate_label", "merge_dicts", 'use_join']


def adapt_call(func, **kw):
    """
    Calls ``func`` with as many arguments from ``kw`` as possible.

    Example::

        >>> def some_func(a, b):
        ...     return a + b
        >>> adapt_call(some_func, a=4, b=3, c=6)
        7
        
        >>> def some_func(a, b=2):
        ...     return a + b
        >>> adapt_call(some_func, a=4)
        6

        >>> def some_func(a, b=2, **kw):
        ...     return a + b + kw['c']
        >>> adapt_call(some_func, a=4, c=2)
        8

        >>> class SomeCallable(object):
        ...     def __call__(self, a, b):
        ...         return a + b
        >>> adapt_call(SomeCallable(), a=5, b=4)
        9

        >>> class SomeClass(object):
        ...     def __init__(self, name):
        ...         self.name = name
        >>> obj = adapt_call(SomeClass, name="foo", age="bar")
        >>> obj.name
        'foo'
    """
    if not isinstance(func, (types.FunctionType, types.MethodType)):
        if isclass(func):
            # Handle constructors
            inspect = getattr(func, '__init__')
        else:
            # Handle callable objects
            func = inspect = getattr(func, '__call__')
    else:
        inspect = func
    args, varargs, varkw, defaults = getargspec(inspect)
    if varkw is None:
        for k in kw.keys():
            if k not in args:
                del kw[k]
    return func(**kw)

def safe_issubclass(cls, typs):
    return isclass(cls) and issubclass(cls, typs)



_labelRE = re.compile(r'([A-Z][a-z0-9]+|[a-z0-9]+|[A-Z0-9]+)')

def generate_label(name):
    """
    Convert a name to a Human Readable name.

    Yanked from TGFastData
    """
    # Create label from the name:
    #   1) Convert _ to spaces
    #   2) Convert CamelCase to Camel Case
    #   3) Upcase first character of Each Word
    # Note: I *think* it would be thread-safe to
    #       memoize this thing.
    from rum.i18n import ugettext
    return ugettext(' '.join(_labelRE.findall(name))).capitalize()

def keywords_to_str(keywords_orig):
    keywords=dict()
    for (k,v) in keywords_orig.iteritems():
        if isinstance(k,unicode):
            k=k.encode("utf-8")
        keywords[k]=v
    return keywords

    
def merge_dicts(to, from_):
    """
    Recursively merges ``from_`` into ``to`` (in-place) and returns ``to``.
    Keys from ``from_`` will ovewrite existing keys in ``to``

    Example::

        >>> d1 = {'a':1, 'sub':{'a':2}}
        >>> d2 = {'a':3, 'sub':{'b':4}}
        >>> result = merge_dicts(d1, d2)
        >>> result['a'] == 3
        True
        >>> result['sub']['a'] == 2
        True
        >>> result['sub']['b'] == 4
        True
    """
    for (k,v) in from_.iteritems():
        if k in to and isinstance(to[k], dict) and isinstance(v, dict):
            merge_dicts(to[k], v)
        else:
            to[k] = v
    return to


def use_join(j, selected_fields, resource, fields_for_resource, has_permission_for_field, related_to=None):
    '''
        >>> from rum import fields
        >>> class Model(object): pass
        >>> def fields_for_resource(f): return [fields.ToOneRelation('egg', other=Model, remote_name='hams', label='egg')]
        >>> def has_permission_for_field(f): return True
        >>> selected_fields=[fields.String('foo')]
        >>> use_join('egg.egg.egg', selected_fields, Model,\
            fields_for_resource=fields_for_resource, has_permission_for_field=has_permission_for_field,\
        )
        >>> selected_fields
        [rum.fields.String(name='foo', required=False, label='Foo', default=NoDefault, read_only=False, length=None, sortable=True, searchable=True, description=''), rum.fields.RelatedField(related_to=rum.fields.RelatedField(related_to=rum.fields.RelatedField(related_to=rum.fields.ToOneRelation(name='egg', other=<class 'rum.util.Model'>, remote_name='hams', required=False, label='egg', default=NoDefault, read_only=False, searchable=False, sortable=False, description=''), real_field=rum.fields.ToOneRelation(name='egg', other=<class 'rum.util.Model'>, remote_name='hams', required=False, label='egg', default=NoDefault, read_only=False, searchable=False, sortable=False, description=''), label=u'egg.egg'), real_field=rum.fields.ToOneRelation(name='egg', other=<class 'rum.util.Model'>, remote_name='hams', required=False, label='egg', default=NoDefault, read_only=False, searchable=False, sortable=False, description=''), label=u'egg.egg.egg'), real_field=rum.fields.ToOneRelation(name='egg', other=<class 'rum.util.Model'>, remote_name='hams', required=False, label='egg', default=NoDefault, read_only=False, searchable=False, sortable=False, description=''), label=u'egg.egg.egg.egg')]
    '''
    from rum import fields
    #split j='person.address.town' in 'person' and 'address.town'
    pos=j.find('.')
    if pos>=0:
        base=j[:pos]
        remote=j[pos+1:]
    else:
        base=j
        remote=None
    
    # lookup related resource in fields
    for resource_field in fields_for_resource(resource):
        if resource_field.name==base:
            if isinstance(resource_field, fields.ToOneRelation) and resource_field.other is not None:
                if related_to is not None:
                    related_to = fields.RelatedField(real_field=resource_field, related_to=related_to)
                else:
                    related_to=resource_field
                if has_permission_for_field(related_to):#just optimization and additional, superfluous lock
                    #expensive call so I put it as last condition
                    
                    #construct related fields or go deeper in recursion for nested related resources
                    if remote is None:
                        for related_field in fields_for_resource(resource_field.other):
                            to_append=fields.RelatedField(real_field=related_field, related_to=related_to)
                            if has_permission_for_field(to_append):
                                selected_fields.append(to_append)
                    else:
                        use_join(remote, selected_fields, resource=resource_field.other, 
                            fields_for_resource=fields_for_resource,
                            has_permission_for_field=has_permission_for_field,
                            related_to=related_to)
                    break

