import types
from datetime import datetime

from DateTime import DateTime

from zope.interface import Interface, implements, Attribute
from zope import schema

from collective.properties import messageFactory as _
from collective.properties.config import DEFAULT_DATE_VALUE
from collective.properties.field import BytesLineTuple


# keeps mapping of IPropertyManager property types to
# interfaces for z3c.form forms to display it in CRUD listing
PROPERTY_MAP = {}

def registerPropertyType(ptype, prop):
    assert ptype not in PROPERTY_MAP
    PROPERTY_MAP[ptype] = prop

def unregisterPropertyType(ptype):
    assert ptype in PROPERTY_MAP
    del PROPERTY_MAP[ptype]

# abstract property to inherit from for all IPropertyManager property types

class IProperty(Interface):
    
    default = Attribute(_(u"Default valid property value."))
    
    id = schema.ASCIILine(
        title=_(u"Property Id"),
        description=u'',
        required=True,
        readonly=True)
    
    ptype = schema.ASCIILine(
        title=_(u"Property Type"),
        description=u'',
        required=True,
        readonly=True)

class Property(object):
    
    implements(IProperty)
    
    default = None
    
    def __init__(self, context, id, value=default, ptype=None,
                 select_variable=None, mode='wd'):
        self.context = context
        self.id = id
        # we don't need to update context's property on property init
        self.__dict__['value'] = value
        self.ptype = ptype
        self.select_variable = select_variable
        self.mode = mode
    
    def _get_value(self):
        return self.__dict__['value']
    
    def _set_value(self, value):
        # on explicit attribute set (property.value = value) we update
        # context's property value
        # Note: we never set value to None, instead we always set it to
        # default property type value, otherwise old manage_propertiesForm
        # breaks, so we're just following the same old rules ;)
        if value is None:
            value = self.default
        
        # check if property is writable
        self._validate()
        
        self.context._updateProperty(self.id, value)
        self.__dict__['value'] = value
    
    value = property(_get_value, _set_value)
    
    def _validate(self):
        """Checks if property is writable"""
        propdict = self.context.propdict()
        if 'w' not in propdict[self.id].get('mode', 'wd'):
            raise schema.ValidationError(u"The property '%s' is not writable." %
                self.id)
    
    def __repr__(self):                                                                                                              
        return "<Property with id=%r, type=%r, value=%r>" % (self.id,
            self.ptype, self.value)

# IPropertyManager 'string' property

class IStringProperty(IProperty):
    value = schema.BytesLine(
        title=_(u"Property Value"),
        description=_(u"Contains text line, including any non-ascii"
                      " characters."),
        required=False,
        default='')

class StringProperty(Property):
    implements(IStringProperty)
    default = ''

registerPropertyType('string', StringProperty)

# IPropertyManager 'int' property

class IIntProperty(IProperty):
    value = schema.Int(
        title=_(u"Property Value"),
        description=_(u"Contains integer value, e.g. -1, 0, 1, 2."),
        required=False,
        default=0)

class IntProperty(Property):
    implements(IIntProperty)
    default = 0

registerPropertyType('int', IntProperty)
registerPropertyType('long', IntProperty)

# IPropertyManager 'float' property

class IFloatProperty(IProperty):
    value = schema.Float(
        title=_(u"Property Value"),
        description=_(u"Contains floating value, e.g. -1.1, 0.0, 1.25."),
        required=False,
        default=0.0)

class FloatProperty(Property):
    implements(IFloatProperty)
    default = 0.0

registerPropertyType('float', FloatProperty)

# IPropertyManager 'lines' property

class ILinesProperty(IProperty):    
    # we keep data in bytes lines to be compliant with OFS.PropertyManager
    value = BytesLineTuple(
        title=_(u"Property Value"),
        description=_(u"Contains list of strings."),
        required=False,
        value_type=schema.BytesLine(),
        default=())

class LinesProperty(Property):
    implements(ILinesProperty)
    default = ()

registerPropertyType('lines', LinesProperty)

# IPropertyManager 'text' property

class ITextProperty(IProperty):
    value = schema.Bytes(
        title=_(u"Property Value"),
        description=_(u"Contains text."),
        required=False,
        default='')

class TextProperty(Property):
    implements(ITextProperty)
    default = ''

registerPropertyType('text', TextProperty)

# IPropertyManager 'boolean' property

class IBooleanProperty(IProperty):
    value = schema.Bool(
        title=_(u"Property Value"),
        description=_(u"Checked for True, otherwise - False."),
        required=False,
        default=False)

class BooleanProperty(Property):
    implements(IBooleanProperty)
    default = False

registerPropertyType('boolean', BooleanProperty)

# IPropertyManager 'date' property

class IDateProperty(IProperty):
    value = schema.Datetime(
        title=_(u"Property Value"),
        description=_(u"Contains date and time value."),
        required=False,
        default=DEFAULT_DATE_VALUE)

class DateProperty(Property):
    implements(IDateProperty)
    default = DEFAULT_DATE_VALUE

    def _get_value(self):
        """Override this method here to convert value from Zope2 DateTime
        to python datetime object.
        """
        # convert DateTime to datetime
        value = self.__dict__['value']
        if isinstance(value, DateTime):
            parts = value.parts()
            value = datetime(*(parts[:5]+(int(parts[5]),)))
        return value
    
    def _set_value(self, value):
        """Override this method here to convert python datetime object
        we got from z3c.form based form to Zope2 DateTime to save into
        date property type.
        """
        # convert python datetime object to Zope2 DateTime
        if isinstance(value, datetime):
            value = DateTime(value.strftime('%Y/%m/%d %H:%M:%S'))
        
        # on explicit attribute set (property.value = value) we update
        # context's property value
        # Note: we never set value to None, instead we always set it to
        # default property type value, otherwise old manage_propertiesForm
        # breaks, so we're just following the same old rules ;)
        if value is None:
            value = self.default
        
        # check if property is writable
        self._validate()
        
        self.context._updateProperty(self.id, value)
        self.__dict__['value'] = value

    value = property(_get_value, _set_value)

registerPropertyType('date', DateProperty)

# IPropertyManager 'tokens' property

class ITokensProperty(IProperty):
    value = schema.BytesLine(
        title=_(u"Property Value"),
        description=_(u"Contains words separated by spaces."),
        required=False,
        default='')

class TokensProperty(Property):
    implements(ITokensProperty)
    default = ''

    def __init__(self, context, id, value=default, ptype=None,
                 select_variable=None, mode='wd'):
        """Override it here to convert value (which is list) to string.
        This is required because IPropertyManger expects string to be
        passed to it while saving tokens property value as list.
        So we decided to use string field and widget to manage tokens
        property type.
        """
        self.context = context
        self.id = id
        self.ptype = ptype
        self.mode = mode
        
        # here we get tuple of tokens, so convert it to string before
        # returning it to string widget
        if isinstance(value, (types.TupleType, types.ListType)):
            value = ' '.join(value)
        
        self.__dict__['value'] = value

registerPropertyType('tokens', TokensProperty)

# IPropertyManager 'selection' property

class ISelectionProperty(IProperty):
    value = schema.Choice(
        title=_(u"Property Value"),
        description=_(u"Contains utf-8 encoded string."),
        required=False,
        vocabulary='collective.properties.SelectionPropertyTypeVocabulary',
        default='',
        missing_value='')

class SelectionProperty(Property):
    implements(ISelectionProperty)
    default = ''

    def _get_value(self):
        """Override this method here to convert string to unicode value
        before returning it to outside world. We can't do this only
        inside data converter as this breaks while z3c.form form compares
        old and new value to check if applying changes is needed.
        """
        # convert utf-8 encoded string to unicode
        value = self.__dict__['value']
        if isinstance(value, str):
            value = value.decode('utf-8')
        return value
    
    def _set_value(self, value):
        """Override this method here to convert value to utf-8
        encoded string. That's how IPropertyManager sets selection
        property type value.
        """
        if value is None:
            value = self.default
        
        # encode unicode value to utf-8 encoded string
        if isinstance(value, unicode):
            value = value.encode('utf-8')
        
        # check if property is writable
        self._validate()
        
        self.context._updateProperty(self.id, value)
        self.__dict__['value'] = value

    value = property(_get_value, _set_value)

registerPropertyType('selection', SelectionProperty)

# IPropertyManager 'multiple selection' property

class IMultipleSelectionProperty(IProperty):
    value = BytesLineTuple(
        title=_(u"Property Value"),
        description=_(u"Contains list of utf-8 encoded strings."),
        required=False,
        value_type=schema.Choice(
            vocabulary='collective.properties.SelectionPropertyTypeVocabulary'),
        default=())

class MultipleSelectionProperty(Property):
    implements(IMultipleSelectionProperty)
    default = ()

    def _get_value(self):
        """Convert list of strings to list of unicodes."""
        # convert utf-8 encoded string to unicode
        value = self.__dict__['value']
        result = []
        for item in value:
            if isinstance(item, str):
                item = item.decode('utf-8')
            result.append(item)
        return tuple(result)
    
    def _set_value(self, value):
        """Convert list of unicodes to list of strings."""
        if value is None:
            value = self.default
        
        # encode unicode value to utf-8 encoded string
        result = []
        for item in value:
            if isinstance(item, unicode):
                item = item.encode('utf-8')
            result.append(item)
        value = tuple(result)

        # check if property is writable
        self._validate()

        self.context._updateProperty(self.id, value)
        self.__dict__['value'] = value

    value = property(_get_value, _set_value)

registerPropertyType('multiple selection', MultipleSelectionProperty)
