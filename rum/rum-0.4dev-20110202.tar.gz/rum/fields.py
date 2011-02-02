"""
This modules provides a layer to decouple resource field types from
the view factory that will generate the views for the repository items.

These objects just serve as metadata, they do not do anything and do not
depend on any specific library. They are here just to serve as a common
vocabulary between plugins to know what kind of object a field is.

It is the responsability of the :class:`rum.interfaces.IRepositoryFactory`
implementation to provide this metadata about the resources it knows how to
handle.

Two distinct plugins that depend on each other just to share a definition
of a :class:`Field` should get in touch to get the :class:`Field`
declaration included here in order to decouple from each other.
"""
from inspect import isclass, getargspec
from operator import isSequenceType

from peak.util.decorators import decorate_class

from rum import app
from rum.util import NoDefault, generate_label, adapt_call
from rum.genericfunctions import generic, NoApplicableMethods, around
from rum.basefactory import BaseFactory, cache_call
from new import instancemethod
@generic
def rum_getattr(obj, attr):
    '''
        attribute of resource objects should always be fetched by this function
    '''
    pass

def rum_setattr(obj, attr, value):
    '''
        attribute of resource objects should always be set by this function
    '''
    return setattr(obj, attr, value)
class FieldFactory(BaseFactory):
    def __init__(self):
        self._cache = {}

    @generic
    def get(self, resource, attr=None, args=None):
        """
        Returns a :class:`rum.fields.Field` subclass.
        """

    def __call__(self, resource, attr=None):
        args = {}
        try:
            field_cls = self.get(resource=resource, attr=attr, args=args)
        except NoApplicableMethods:
            # We just ignore attributes we don't know how to handle
            field_cls = None
        return self.instantiate_field(field_cls, **args)

    # Cache generated fields in factory instance
    around(__call__)(cache_call)

    def instantiate_field(self, field_cls, **kw):
        if field_cls:
            return adapt_call(field_cls, **kw)


    @classmethod
    def fields(cls, *fields, **kw):
        """
        Associates a series of :class:`rum.fields.Field` instances to a model
        class.

        This :class:`rum.fields.Field` are queried by the
        :class:`rum.view.ViewFactory` and give it a hint on how it should
        generate the interface.

        It can be placed right in the model class it assigns metadata to like
        a "class decorator"::

            >>> class Peanut(object):
            ...     FieldFactory.fields(
            ...         Unicode("name", required=True),
            ...         Integer("weight")
            ...     )

        Or the binding can be done elsewhere (anywhere both the model
        and ``fields`` can be imported). This is useful to avoid
        contaminating your models with Rum imports::

            >>> class Orange(object):
            ...     pass

        Then in some other module::

            >>> FieldFactory.fields(Orange, [
            ...     Unicode("name", required=True),
            ...     Integer("weight")
            ... ])
            <class 'rum.fields.Orange'>

        .. note::
            This module needs to be imported somehow since if it's not the fields
            will not be registered and Rum will try to guess them.

        Both ways are equivalent, use the one you find more pleasing to the
        eye or allows you to structure your code better.

        Notice that (in both situations) the original class is returned as-is,
        it is not modified in any way (the registry lives inside PEAK-Rules
        if you're wondering)

        There's a third syntax to override just one field::

            >>> FieldFactory.fields(Orange, "weight", Unicode("weight"))
            <class 'rum.fields.Orange'>

        Fields registered this way will override fields registered in any of
        the other two ways.

        :meth:`fields` accepts one keyword argument:
            `prio`
                Priority of the generated rule, it will be passed to `when`,
                again this parameter is very unlikely that it'll ever be needed.

        .. note:: 

            Remember, the View can do whatever it feels like with this
            information. These are just *hints*.
        """
        if len(fields) == 2 and isSequenceType(fields[1]):
            # We're being called as a normal func.
            target_cls, fields = fields
            return cls._override_all(target_cls, fields, **kw)
        elif len(fields) == 3 and not isinstance(fields[0], Field):
            # We're being called to register just one field for an attr
            target_cls, attr_name, field = fields
            return cls._override_attribute(target_cls, attr_name, field, **kw)
        elif fields and isinstance(fields[0], (Field,basestring)):
            # We're being called as a class decorator
            def callback(target_cls):
                return cls._override_all(target_cls, fields, **kw)
            return decorate_class(callback)
        raise TypeError(
            cls.__name__ + ".fields cannot be called with those arguments"
            )


    @classmethod
    def _override_all(cls, target_cls, fields, **kw):
        prio = kw.pop('prio', 0)
        fields = cls._field_getter(target_cls, fields)
        cls.register(FieldList, target_cls, attr=None, _prio=prio,
                     defaults=dict(fields=fields))
        return target_cls
        
    @classmethod
    def _override_attribute(cls, target_cls, attr_name, field, **kw):
        if field.name != attr_name:
            raise ValueError(
                "Field has a different name than the attribute you're "\
                "registering it for. Probably a typo...."
                )
        prio = kw.pop('prio', 0)
        field_attrs = dict(field.attrs)
        cls.register(field.__class__, target_cls, attr=attr_name, _prio=prio,
                     defaults=field_attrs)
        return target_cls

    @staticmethod
    def _field_getter(target_cls, fields):
        def _guess_field_if_string(field):
            if isinstance(field, basestring):
                factory = app.repositoryfactory
                return factory.fields_for_resource(target_cls, field)
            return field
        return lambda: filter(None, map(_guess_field_if_string, fields))


    def defaults(self, resource):
        """
        Returns a dict with default values to populate an instance of
        ``resource``.
        """
        fields = self(resource) or []
        return dict((f.name, f.get_default()) for f in fields if f.has_default)

class FieldList(list):
    def __init__(self, fields):
        if callable(fields):
            fields = fields()
        list.__init__(self, fields)

class Field(object):
    """
    A field base class

    **Attributes**
        ``name``
            The name of the field. Should be the same as the name of the
            attribute of the ``resource`` it models.
        ``required``
            Is this field required?
        ``label``
            The label for this field. If ``None`` it will be derived from
            ``name``
        ``default``
            Default value for this field.
        ``read_only``
            Set to True if no GUI should be generated to allow this field to
            be modified
        
    Examples::

        >>> Field(name='name')
        rum.fields.Field(name='name', required=False, label='Name', default=NoDefault, read_only=False, searchable=False, sortable=False, description='')
    """
    def __init__(self, name, required=False, label=None, default=NoDefault,
                 read_only=False, searchable=False,
                 sortable=False, description=''):
        self.name = name
        self.required = required
        self.label = label or generate_label(name)
        self.default = default
        self.read_only = read_only
        self.searchable = searchable
        self.sortable = sortable
        self.description  = description

    def get_default(self):
        if self.default is not NoDefault and callable(self.default):
            return self.default()
        return self.default

    @property
    def has_default(self):
        return self.default is not NoDefault

    @property
    def field_type(self):
        return self.__class__.__module__+'.'+self.__class__.__name__

    def __repr__(self):
        return self.field_type + '(' + ', '.join('%s=%r'%i for i in self.attrs if not isinstance(i[1], instancemethod)) + ')'
        #avoid maximum recursion exceeded

    @property
    def attrs(self):
        attrs = getargspec(self.__init__)[0][1:]
        return tuple((attr, getattr(self, attr)) for attr in attrs if hasattr(self, attr))

    def __hash__(self):
        return hash(tuple((v for (k,v) in self.attrs if not isinstance(v, instancemethod))))

    def __eq__(self, other):
        return self.attrs == getattr(other, 'attrs', None)

#
# binary types
#
class Binary(Field):
    def __init__(self, name, required=False, label=None, default=NoDefault, 
                 read_only=False, content_type="", searchable=False, filename_for=None,
                 content_type_for=None, disposition_type_for=None,
                 description=''):
        super(Binary, self).__init__(name, required, label, default, read_only, searchable, description=description)
        self._content_type=content_type

        if content_type_for is not None:
            self.content_type_for=content_type_for
        if filename_for is not None:
            self.filename_for= filename_for
        if disposition_type_for is not None:
            self.disposition_type_for = disposition_type_for
    
    def disposition_type_for(self, obj, action):
        return 'attachment'

    def filename_for(self, obj):
        """This method determines the filename for the attribute <name> of obj.
           Default implementation is to return a fixed type for all objects.
           However it is also possible to access other attributes, 
           which might store the content type.
        """
        try:
            suffix="."+self.content_type_for(obj).split("/")[1]
        except IndexError:
            suffix=""
        
        from rum import app
        repositoryfactory=app.repositoryfactory
        repository=repositoryfactory(obj.__class__)
        obj_id=repository.get_id(obj)
        filename=self.name+"-"+unicode(obj_id)+suffix
        return filename
        
    def content_type_for(self, obj):
        """This method determines the content type for the attribute <name> of obj.
           Default implementation is to return a fixed type for all objects.
           However it is also possible to access other attributes, 
           which might store the content type.
        """
        return self._content_type
class Image(Binary):
    def __init__(self,name, content_type, required=False, label=None, default=NoDefault, 
                 read_only=False,preview_width=150,preview_height=100, searchable=False,description='', disposition_type_for=None):
        super(Image,self).__init__(name=name,required=required,label=label,default=default,read_only=read_only,\
            content_type=content_type, searchable=searchable, description= description, disposition_type_for=disposition_type_for)
        self.preview_width=preview_width
        self.preview_height=preview_height
    
    def disposition_type_for(self, obj, action):
        if action=='preview':
            return 'inline'
        else:
            return 'attachment'

class JPEGImage(Image):
    def __init__(self,name, required=False, label=None, default=NoDefault, 
                 read_only=False,preview_width=150,preview_height=100, searchable=False, description=''):
        super(JPEGImage,self).__init__(name=name,required=required,
            label=label,default=default,read_only=read_only,\
            content_type="image/jpeg",preview_width=preview_width,
            preview_height=preview_height, searchable=searchable, description=description)

#
# Strings
#

class String(Field):
    """
    This :class:`Field` represents an ascii string.
    
    **Attributes** 
        ``length``
            The maximum number of characters this field can hold.
            Leave as None if length should not be checked.

    Examples::

        >>> String(name='name', length=50)
        rum.fields.String(name='name', required=False, label='Name', default=NoDefault, read_only=False, length=50, sortable=True, searchable=True, description='')
    """
    def __init__(self, name, required=False, label=None, default=NoDefault, 
                 read_only=False, length=None, sortable=True, searchable=True, description=''):
        super(String, self).__init__(name, required, label, default,
            read_only, searchable=searchable, sortable=sortable, description= description)
        self.length = length

class Text(String):
    """
    This :class:`Field` is a :class:`String` but the GUI should render
    a textarea of some other sort of control to manipulate a chunk
    of text.
    
    Examples::

        >>> Text(name='name', length=50)
        rum.fields.Text(name='name', required=False, label='Name', default=NoDefault, read_only=False, length=50, sortable=True, searchable=True, description='')
    """


class PreformattedText(Text):
    """
    This :class:`Field` is a :class:`PreformattedText`, which should use html pre tags when displayed.
    
    Examples::

        >>> PreformattedText(name='name', length=50)
        rum.fields.PreformattedText(name='name', required=False, label='Name', default=NoDefault, read_only=False, length=50, sortable=True, searchable=True, description='')
    """

class Address(PreformattedText):
    pass

class Unicode(String):
    """
    This :class:`Field` is a :class:`String` but can hold unicode strings.
    
    Examples::

        >>> Unicode(name='name', length=50, description='foo')
        rum.fields.Unicode(name='name', required=False, label='Name', default=NoDefault, read_only=False, length=50, sortable=True, searchable=True, description='foo')
    """

class Password(String):
    """
    This :class:`Field` is a :class:`Unicode` which holds a password. It signals
    the GUI to handle it in a special way (eg: by not showing it, etc...)
    
    Examples::

        >>> Password(name='password', length=50)
        rum.fields.Password(name='password', required=False, label='Password', default=NoDefault, read_only=False, length=50, sortable=False, searchable=False, description='')
    """
    def __init__(self, name, required=False, label=None, default=NoDefault, 
                 read_only=False, length=None, sortable=False,
                 searchable=False, description=''):
        super(Password, self).__init__(name, required, label, default,
                                       read_only, length, sortable, searchable, description = description)

class UnicodeText(Unicode, Text):
    """
    This :class:`Field` is a :class:`Unicode` but the GUI should render
    a textarea of some other sort of control to manipulate a chunk
    of text.
    
    Examples::

        >>> Unicode(name='name', length=50)
        rum.fields.Unicode(name='name', required=False, label='Name', default=NoDefault, read_only=False, length=50, sortable=True, searchable=True, description='')
    """

class HTMLText(UnicodeText):
    """
    This :class:`Field` is a :class:`UnicodeText` but the GUI should render
    some sort of fancy control to edit HTML.
    
    Examples::

        >>> HTMLText(name='name', length=50)
        rum.fields.HTMLText(name='name', required=False, label='Name', default=NoDefault, read_only=False, length=50, sortable=True, searchable=True, description='')
    """

class Email(Unicode):
    """
    This :class:`Field` is a :class:`String` but signals the GUI and
    validation framework that is should contain a valid email
    address.
    
    Examples::

        >>> Email(name='name', length=50)
        rum.fields.Email(name='name', required=False, label='Name', default=NoDefault, read_only=False, length=50, sortable=True, searchable=True, description='')
    """

class Url(String):
    """
    This :class:`Field` is a :class:`String` but signals the GUI and
    validation framework that is should contain a valid URL.
    
    Examples::

        >>> Url(name='name', length=50)
        rum.fields.Url(name='name', required=False, label='Name', default=NoDefault, read_only=False, length=50, sortable=True, searchable=True, description='')
    """

#
# numbers and boolean
#

class Boolean(Field):
    """
    This :class:`Field` holds a boolean value

    Examples::

        >>> Boolean(name='name')
        rum.fields.Boolean(name='name', required=False, label='Name', default=NoDefault, read_only=False, searchable=False, sortable=True, description='')
    """
    def __init__(self, name, required=False, label=None, default=NoDefault,
                 read_only=False, searchable=False,
                 sortable=True, description=''):
        super(Boolean, self).__init__(name=name, required=required, label=label, default=default,
            read_only=read_only, searchable=searchable,
            sortable=sortable, description=description)

class Number(Field):
    """
    This :class:`Field` holds a number

    **Attributes** 
        ``range``
            A tuple that holds the bounds of the range of
            (min,max) values the field can hold.
            A value of None at either end means the range is
            not bounded on that direction.
        
    Examples::

        >>> Number(name='name', range=(10,50))
        rum.fields.Number(name='name', required=False, label='Name', default=NoDefault, read_only=False, range=(10, 50), sortable=True, searchable=True, description='')
    """
    def __init__(self, name, required=False, label=None, default=NoDefault,
                 read_only=False, range=(None,None), sortable=True, searchable=True, description=''):
        super(Number, self).__init__(name, required, label,
            default, read_only, searchable=searchable, sortable=sortable,
            description=description)
        self.range = range

class Integer(Number):
    """
    This :class:`Field` is a :class:`Number` that can only hold int or long
    numbers.

    Examples::

        >>> Integer(name='name', range=(10,50))
        rum.fields.Integer(name='name', required=False, label='Name', default=NoDefault, read_only=False, range=(10, 50), sortable=True, searchable=True, description='')
    """

class Decimal(Number):
    """
    This :class:`Field` holds a real number

    **Attributes** 
        ``precision``
            Number of digits in the decimal part.
    
    Examples::

        >>> Decimal(name='name', range=(10,50), precision=10)
        rum.fields.Decimal(name='name', required=False, label='Name', default=NoDefault, read_only=False, range=(10, 50), precision=10, sortable=True, searchable=True, description='')
    """
    def __init__(self, name, required=False, label=None, default=NoDefault,
                 read_only=False, range=(None,None), precision=4, sortable=True, searchable=True, description=''):
        super(Decimal, self).__init__(
            name, required, label, default, read_only, range, sortable, searchable=searchable,
            description=description
            )
        self.precision = precision


#
# date and times
#
class Date(Field):
    """
    This :class:`Field` represents a date

    Examples::

        >>> Date(name='pub_date')
        rum.fields.Date(name='pub_date', required=False, label='Pub date', default=NoDefault, read_only=False, sortable=True, searchable=False, description='')
    """
    def __init__(self, name, required=False, label=None, default=NoDefault,
                 read_only=False, sortable=True, searchable=False, description=''):
        super(Date, self).__init__(name, required, label, default, read_only, searchable=searchable, sortable=sortable,
        description=description)

class Time(Field):
    """
    This :class:`Field` represents a time

    **Attributes** 
        ``has_timezone``
            A flag that indicates if this field is timezone aware

    Examples::

        >>> Time(name='name', has_timezone=True)
        rum.fields.Time(name='name', required=False, label='Name', default=NoDefault, read_only=False, has_timezone=True, sortable=True, searchable=False, description='')
    """
    def __init__(self, name, required=False, label=None, default=NoDefault,
                 read_only=False, has_timezone=False, sortable=True, searchable=False, description=''):
        super(Time, self).__init__(name, required, label, default, read_only, searchable=searchable, sortable=sortable, description=description)
        self.has_timezone = has_timezone

class DateTime(Time, Date):
    """
    This :class:`Field` represents a time with an associated date.

    Examples::

        >>> DateTime(name='name', has_timezone=True)
        rum.fields.DateTime(name='name', required=False, label='Name', default=NoDefault, read_only=False, has_timezone=True, sortable=True, searchable=False, description='')
    """

#
# relations
#

class Relation(Field):
    """
    This :class:`Field` represents a relation to another object

    **Attributes** 
        ``other``
            The resource class this field relates to.
    
    Examples::

        >>> class Related: pass
        >>> Relation(name='name', other=Related, remote_name='related') # doctest: +ELLIPSIS
        rum.fields.Relation(name='name', other=<class rum.fields.Related at ...>, remote_name='related', required=False, label='Name', default=NoDefault, read_only=False, searchable=False, sortable=False, description='')
    """
    def __init__(self, name, other, remote_name, required=False, label=None,
                 default=NoDefault, read_only=False, searchable=False, sortable=False, description=''):
        super(Relation, self).__init__(name, required, label=label, default=default, read_only=read_only, searchable=searchable, sortable=sortable,description=description )
        self.other = other
        self.remote_name = remote_name

class ToOneRelation(Relation):
    """
    This :class:`Field` represents a relation to another object

    **Attributes** 
        ``other``
            The resource class this field relates to.
    
    Examples::

        >>> class Related: pass
        >>> ToOneRelation(name='name', other=Related, remote_name='related') # doctest: +ELLIPSIS
        rum.fields.ToOneRelation(name='name', other=<class rum.fields.Related at ...>, remote_name='related', required=False, label='Name', default=NoDefault, read_only=False, searchable=False, sortable=False, description='')
    """
    def __init__(self, name, other, remote_name, required=False, label=None,
                 default=NoDefault, read_only=False, searchable=False, sortable=False, description=''):
                 super(ToOneRelation, self).__init__(name=name, required=required, label=label,
                    default=default, read_only=read_only, searchable=searchable,
                    sortable=sortable,description=description, other=other, remote_name=remote_name )
class Collection(Relation):
    """
    This :class:`Relation` represents a relation to a collection of objects

    Examples::

        >>> class Related: pass
        >>> Collection(name='name', other=Related, remote_name='related') # doctest: +ELLIPSIS
        rum.fields.Collection(name='name', other=<class rum.fields.Related at ...>, remote_name='related', required=False, label='Name', default=NoDefault, read_only=False, searchable=False, sortable=False, description='')
    """

class List(Collection):
    """
    This :class:`Relation` represents a relation to an ordered list of objects

    Examples::

        >>> class Related: pass
        >>> List(name='name', other=Related, remote_name='related') # doctest: +ELLIPSIS
        rum.fields.List(name='name', other=<class rum.fields.Related at ...>, remote_name='related', required=False, label='Name', default=NoDefault, read_only=False, searchable=False, sortable=False, description='')
    """
    
class Mapping(Collection):
    """
    This :class:`Relation` represents a relation to mapping of objects by some
    key.
    (think of a dictionary)

    Examples::

        >>> class Related: pass
        >>> Mapping(name='name', other=Related, remote_name='related') # doctest: +ELLIPSIS
        rum.fields.Mapping(name='name', other=<class rum.fields.Related at ...>, remote_name='related', required=False, label='Name', default=NoDefault, read_only=False, searchable=False, sortable=False, description='')
    """
    
    
#
# internal fields. These are usually implementation details which should not
# be reflected in the GUI
#

class InternalField(Field):
    """
    This :class:`Field` represents a field which is an implementation detail.
    An should not be shown in the GUI.

    **Attributes** 
        ``type``
            The real :class:`Field` this attribute represents if it weren't an
            implementation detail. ``name`` and ``required`` are autogenerated
            from this :class:`Field`
    
    Examples::

        >>> InternalField(Integer('id'))
        rum.fields.InternalField(type=rum.fields.Integer(name='id', required=False, label='Id', default=NoDefault, read_only=False, range=(None, None), sortable=True, searchable=True, description=''), searchable=False, description='')
    """
    def __init__(self, type, searchable=False,description=''):
        super(InternalField, self).__init__(type.name, type.required,
                                            type.label, type.default,
                                            type.read_only, searchable=searchable, description=description)
        self.type = type
    
    def __getattr__(self, attr):
        return getattr(self.type, attr)


class RelatedField(Field):
    """
    This :class:`Field` represents a field of a related object.
    An should not be shown in the GUI.

    **Attributes** 
        ``real_field``
            The real :class:`Field` this attribute represents
        ``related_to``
            The resource ``real_field`` belongs to, given as a ``Relation``

    Examples::
        >>> class Foo(object): pass
        >>> RelatedField(real_field=Integer('id'), related_to=Relation('foo', other=Foo, remote_name=None), label='foo.id')
        rum.fields.RelatedField(related_to=rum.fields.Relation(name='foo', other=<class 'rum.fields.Foo'>, remote_name=None, required=False, label='Foo', default=NoDefault, read_only=False, searchable=False, sortable=False, description=''), real_field=rum.fields.Integer(name='id', required=False, label='Id', default=NoDefault, read_only=False, range=(None, None), sortable=True, searchable=True, description=''), label='foo.id')
            
    """
    def __init__(self, related_to, real_field, label=None):
        if label is None:
            label='.'.join([unicode(related_to.label), unicode(real_field.label)])
        super(RelatedField, self).__init__('.'.join([related_to.name, real_field.name]), real_field.required,
                                            label=label, default=real_field.default,
                                            read_only=True#real_field.read_only
                                            )
        self.real_field = real_field
        self.related_to=related_to
        self.sortable=real_field.sortable
        self.searchable=real_field.searchable
    
    def next_relation_in_chain(self):
        '''for person.address.town return Person class, the next resource in the chain of the relation.
        This in encapsulated deep in the field
        >>> class Person(object): pass
        >>> class Address(object): pass
        >>> class town(object): pass
        >>> f=RelatedField(related_to=RelatedField(\
                related_to=Relation(name='person', remote_name=None, other=Person),\
                real_field=Relation(name='address', remote_name=None, other=Address),\
            label='person.address'\
            ), real_field=String(name='town'), label='person.address.town')
        >>> f.next_relation_in_chain()
        rum.fields.Relation(name='person', other=<class 'rum.fields.Person'>, remote_name=None, required=False, label='Person', default=NoDefault, read_only=False, searchable=False, sortable=False, description='')
        '''
        f=self
        while isinstance(f, RelatedField):
            f=f.related_to
        return f

class PrimaryKey(InternalField):
    """
    This :class:`Field` represents a primary key. It normally signals the GUI
    to render a disabled field or not render it at all on edit forms.

    If it is autogenerated then it will probably not be rendered at all.

    **Attributes** 
        ``auto``
            A flag that signals that the underlying data store will
            autogenerate the key
            This will probably make the GUI hide the field when creating a new
            object and mark this field as not required so validation doesn't
            fail when it's missing.
            (The underlying ``type`` will still be marked as required though)
        ``order``
            If this is a composite primary key the this is the index of the pk
            tuple this key goes in. If the PK is not composite then leave it to
            ``None``
    
    Examples::

        >>> PrimaryKey(Integer('id'))
        rum.fields.PrimaryKey(type=rum.fields.Integer(name='id', required=True, label='Id', default=NoDefault, read_only=False, range=(None, None), sortable=True, searchable=True, description=''), auto=True, order=None)
        >>> PrimaryKey(Integer('id'), auto=False)
        rum.fields.PrimaryKey(type=rum.fields.Integer(name='id', required=True, label='Id', default=NoDefault, read_only=False, range=(None, None), sortable=True, searchable=True, description=''), auto=False, order=None)
    """
    def __init__(self, type, auto=True, order=None):
        # Primary keys are always required
        type.required = True
        super(PrimaryKey, self).__init__(type)
        # Override requiredness if the field is autogenerated
        self.required = not auto
        self.auto = auto
        self.order = order

class ForeignKey(InternalField):
    """
    This :class:`Field` represents a foreign key. It normally signals the GUI
    not to render it at all and use the associated :class:`Relation` instead.

    It's ``name`` and ``required`` flag are derived from ``type``

    **Attributes** 
        ``type``
            The :class:`Field` for this FK.
        ``order``
            If this is a composite foreign key the this is the index of the fk
            tuple this key goes in. If the FK is not composite then leave it to
            ``None``
    
    Examples::

        >>> ForeignKey(Integer('id'))
        rum.fields.ForeignKey(type=rum.fields.Integer(name='id', required=False, label='Id', default=NoDefault, read_only=False, range=(None, None), sortable=True, searchable=True, description=''), order=None, searchable=False)
        >>> ForeignKey(Integer('id', required=True, description=''), order=0)
        rum.fields.ForeignKey(type=rum.fields.Integer(name='id', required=True, label='Id', default=NoDefault, read_only=False, range=(None, None), sortable=True, searchable=True, description=''), order=0, searchable=False)
    """
    def __init__(self, type, order=None, searchable=False):
        super(ForeignKey, self).__init__(type)
        self.order = order

class PolymorphicDiscriminator(InternalField):
    """
    This :class:`Field` represents a polymorphic discriminator. This makes sense
    for SQLAlchemy really but other backend might find it useful perhaps.

        >>> PolymorphicDiscriminator(String('type'))
        rum.fields.PolymorphicDiscriminator(type=rum.fields.String(name='type', required=False, label='Type', default=NoDefault, read_only=False, length=None, sortable=True, searchable=True, description=''), searchable=False, description='')
    """

class VersionID(InternalField):
    """
    This :class:`Field` represents a version id field used implement optimistic
    locking of model instances to avoid concurrent modification.
    This makes sense for SQLAlchemy really but other backend might find it
    useful too.

        >>> VersionID(Integer('version'))
        rum.fields.VersionID(type=rum.fields.Integer(name='version', required=False, label='Version', default=NoDefault, read_only=False, range=(None, None), sortable=True, searchable=True, description=''), searchable=False, description='')
    """


@rum_getattr.when('isinstance(attr, basestring)')
def _rum_getattr_default(obj, attr):
    return getattr(obj, attr)

@rum_getattr.when('isinstance(attr, basestring) and attr.find(".")>=0')
def _rum_getattr_recursive_basestring(obj, attr):
    '''
    >>> class Ham(object):pass
    >>> ham=Ham()
    >>> class Egg(object):pass
    >>> egg=Egg()
    >>> ham.egg=egg
    >>> egg.id=7
    >>> egg2 = Egg()
    >>> egg2.id=13
    >>> egg.sister_egg=egg2
    
    '''
    pos = attr.find('.')
    base =attr[:pos]
    remote_part= attr[pos+1:]
    remote =rum_getattr(obj, base)
    if remote is not None:
        return rum_getattr(remote, remote_part)
    else:
        return None
    
    
@rum_getattr.when('isinstance(attr, Field)')
def _rum_getattr_field(obj, attr):
    return getattr(obj, attr.name)


@rum_getattr.when('isinstance(attr, RelatedField)')
def _rum_getattr_recursive_field(obj, attr):
    '''
    >>> class Ham(object):pass
    >>> ham=Ham()
    >>> class Egg(object):pass
    >>> egg=Egg()
    >>> ham.egg=egg
    >>> egg.id=7
    >>> egg_field = Relation('egg', other=Egg, remote_name=None)
    >>> f=RelatedField(real_field=Integer('id'), related_to=egg_field, label='egg.id')
    >>> rum_getattr(ham, f)
    7
    >>> eggs_sister_egg=RelatedField(real_field=Relation('sister_egg',  other=Egg, remote_name=None),\
        related_to=egg_field, label='egg.sister_egg')
    >>> egg2 = Egg()
    >>> egg2.id=13
    >>> egg.sister_egg=egg2
    >>> g = RelatedField(real_field=Integer('id'), related_to=eggs_sister_egg, label='egg.sister_egg.id')
    >>> rum_getattr(ham, g)
    13
    '''
    remote =rum_getattr(obj, attr.related_to)
    if remote is not None:
        return rum_getattr(remote, attr.real_field)
    else:
        return None

__all__ = [k for k,v in locals().items() if isclass(v) and issubclass(v, Field)]
__all__.sort()
__all__ = ["FieldFactory", "FieldList",'rum_setattr', 'rum_getattr'] + __all__


