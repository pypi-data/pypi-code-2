from zope.interface import Interface, implements, Attribute
from zope import schema

from collective.properties import messageFactory as _


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
    
    def __init__(self, context, id, value=default, ptype=None):
        self.context = context
        self.id = id
        # we don't need to update context's property on property init
        self.__dict__['value'] = value
        self.ptype = ptype
    
    def _get_value(self):
        return self.__dict__['value']
    
    def _set_value(self, value):
        self.__dict__['value'] = value
        # on explicit attribute set (property.value = value) we update
        # context's property value
        # Note: we never set value to None, instead we always set it to
        # default property type value, otherwise old manage_propertiesForm
        # breaks, so we're just following the same old rules ;)
        if value is None:
            value = self.default
        self.context._updateProperty(self.id, value)
    
    value = property(_get_value, _set_value)
    
    def __repr__(self):                                                                                                              
        return "<Property with id=%r, value=%r>" % (self.id, self.value)

# IPropertyManager 'string' property

class IStringProperty(IProperty):
    value = schema.TextLine(
        title=_(u"Property Value"),
        description=_(u"Contains text line, including any non-ascii"
                      " characters."),
        required=False,
        default=u'')

class StringProperty(Property):
    implements(IStringProperty)
    default = u''

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
    value = schema.Tuple(
        title=_(u"Property Value"),
        description=_(u"Contains list of strings."),
        required=False,
        value_type=schema.TextLine(),
        default=())

# TODO: fix lines property: ComponentLookupError: ((<zope.schema._field.Tuple object at 0x10e5bd110>, <zope.schema._bootstrapfields.TextLine object at 0x10e5bd050>, <HTTPRequest, URL=http://localhost:8080/www/f1/@@manage-properties>), <InterfaceClass z3c.form.interfaces.IFieldWidget>, u'')

class LinesProperty(Property):
    implements(ILinesProperty)
    default = ()

# registerPropertyType('lines', LinesProperty)

# IPropertyManager 'text' property

class ITextProperty(IProperty):
    value = schema.Text(
        title=_(u"Property Value"),
        description=_(u"Contains text."),
        required=False,
        default=u'')

class TextProperty(Property):
    implements(ITextProperty)
    default = u''

registerPropertyType('text', TextProperty)

# TODO: add left property types:
#    selection, multiple selection, tokens, date, lines
