# ./pyxb/bundles/opengis/raw/ogckml22.py
# PyXB bindings for NM:cb051a2fa805178d0865f0ce9b303a52f418cb84
# Generated 2011-09-09 14:18:59.939652 by PyXB version 1.1.3
# Namespace http://www.opengis.net/kml/2.2

import pyxb
import pyxb.binding
import pyxb.binding.saxer
import StringIO
import pyxb.utils.utility
import pyxb.utils.domutils
import sys

# Unique identifier for bindings created at the same time
_GenerationUID = pyxb.utils.utility.UniqueIdentifier('urn:uuid:91d4b888-db18-11e0-ad7d-001fbc013adc')

# Import bindings for namespaces imported into schema
import pyxb.binding.datatypes
import pyxb.bundles.opengis._atom
import pyxb.bundles.opengis.misc.xAL

Namespace = pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/kml/2.2', create_if_missing=True)
Namespace.configureCategories(['typeBinding', 'elementBinding'])
ModuleRecord = Namespace.lookupModuleRecordByUID(_GenerationUID, create_if_missing=True)
ModuleRecord._setModule(sys.modules[__name__])

def CreateFromDocument (xml_text, default_namespace=None, location_base=None):
    """Parse the given XML and use the document element to create a Python instance."""
    if pyxb.XMLStyle_saxer != pyxb._XMLStyle:
        dom = pyxb.utils.domutils.StringToDOM(xml_text)
        return CreateFromDOM(dom.documentElement)
    saxer = pyxb.binding.saxer.make_parser(fallback_namespace=Namespace.fallbackNamespace(), location_base=location_base)
    handler = saxer.getContentHandler()
    saxer.parse(StringIO.StringIO(xml_text))
    instance = handler.rootObject()
    return instance

def CreateFromDOM (node, default_namespace=None):
    """Create a Python instance from the given DOM node.
    The node tag must correspond to an element declaration in this module.

    @deprecated: Forcing use of DOM interface is unnecessary; use L{CreateFromDocument}."""
    if default_namespace is None:
        default_namespace = Namespace.fallbackNamespace()
    return pyxb.binding.basis.element.AnyCreateFromDOM(node, _fallback_namespace=default_namespace)


# List SimpleTypeDefinition
# superclasses pyxb.binding.datatypes.anySimpleType
class coordinatesType (pyxb.binding.basis.STD_list):

    """Simple type that is a list of pyxb.binding.datatypes.string."""

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'coordinatesType')
    _Documentation = None

    _ItemType = pyxb.binding.datatypes.string
coordinatesType._InitializeFacetMap()
Namespace.addCategoryObject('typeBinding', u'coordinatesType', coordinatesType)

# Atomic SimpleTypeDefinition
class angle180Type (pyxb.binding.datatypes.double):

    """An atomic simple type."""

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'angle180Type')
    _Documentation = None
angle180Type._CF_maxInclusive = pyxb.binding.facets.CF_maxInclusive(value_datatype=angle180Type, value=pyxb.binding.datatypes.double(180.0))
angle180Type._CF_minInclusive = pyxb.binding.facets.CF_minInclusive(value_datatype=angle180Type, value=pyxb.binding.datatypes.double(-180.0))
angle180Type._InitializeFacetMap(angle180Type._CF_maxInclusive,
   angle180Type._CF_minInclusive)
Namespace.addCategoryObject('typeBinding', u'angle180Type', angle180Type)

# Union SimpleTypeDefinition
# superclasses pyxb.binding.datatypes.anySimpleType
class dateTimeType (pyxb.binding.basis.STD_union):

    """Simple type that is a union of pyxb.binding.datatypes.dateTime, pyxb.binding.datatypes.date, pyxb.binding.datatypes.gYearMonth, pyxb.binding.datatypes.gYear."""

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'dateTimeType')
    _Documentation = None

    _MemberTypes = ( pyxb.binding.datatypes.dateTime, pyxb.binding.datatypes.date, pyxb.binding.datatypes.gYearMonth, pyxb.binding.datatypes.gYear, )
dateTimeType._CF_pattern = pyxb.binding.facets.CF_pattern()
dateTimeType._CF_enumeration = pyxb.binding.facets.CF_enumeration(value_datatype=dateTimeType)
dateTimeType._InitializeFacetMap(dateTimeType._CF_pattern,
   dateTimeType._CF_enumeration)
Namespace.addCategoryObject('typeBinding', u'dateTimeType', dateTimeType)

# Atomic SimpleTypeDefinition
class shapeEnumType (pyxb.binding.datatypes.string, pyxb.binding.basis.enumeration_mixin):

    """An atomic simple type."""

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'shapeEnumType')
    _Documentation = None
shapeEnumType._CF_enumeration = pyxb.binding.facets.CF_enumeration(value_datatype=shapeEnumType, enum_prefix=None)
shapeEnumType.rectangle = shapeEnumType._CF_enumeration.addEnumeration(unicode_value=u'rectangle', tag=u'rectangle')
shapeEnumType.cylinder = shapeEnumType._CF_enumeration.addEnumeration(unicode_value=u'cylinder', tag=u'cylinder')
shapeEnumType.sphere = shapeEnumType._CF_enumeration.addEnumeration(unicode_value=u'sphere', tag=u'sphere')
shapeEnumType._InitializeFacetMap(shapeEnumType._CF_enumeration)
Namespace.addCategoryObject('typeBinding', u'shapeEnumType', shapeEnumType)

# Atomic SimpleTypeDefinition
class unitsEnumType (pyxb.binding.datatypes.string, pyxb.binding.basis.enumeration_mixin):

    """An atomic simple type."""

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'unitsEnumType')
    _Documentation = None
unitsEnumType._CF_enumeration = pyxb.binding.facets.CF_enumeration(value_datatype=unitsEnumType, enum_prefix=None)
unitsEnumType.fraction = unitsEnumType._CF_enumeration.addEnumeration(unicode_value=u'fraction', tag=u'fraction')
unitsEnumType.pixels = unitsEnumType._CF_enumeration.addEnumeration(unicode_value=u'pixels', tag=u'pixels')
unitsEnumType.insetPixels = unitsEnumType._CF_enumeration.addEnumeration(unicode_value=u'insetPixels', tag=u'insetPixels')
unitsEnumType._InitializeFacetMap(unitsEnumType._CF_enumeration)
Namespace.addCategoryObject('typeBinding', u'unitsEnumType', unitsEnumType)

# Atomic SimpleTypeDefinition
class gridOriginEnumType (pyxb.binding.datatypes.string, pyxb.binding.basis.enumeration_mixin):

    """An atomic simple type."""

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'gridOriginEnumType')
    _Documentation = None
gridOriginEnumType._CF_enumeration = pyxb.binding.facets.CF_enumeration(value_datatype=gridOriginEnumType, enum_prefix=None)
gridOriginEnumType.lowerLeft = gridOriginEnumType._CF_enumeration.addEnumeration(unicode_value=u'lowerLeft', tag=u'lowerLeft')
gridOriginEnumType.upperLeft = gridOriginEnumType._CF_enumeration.addEnumeration(unicode_value=u'upperLeft', tag=u'upperLeft')
gridOriginEnumType._InitializeFacetMap(gridOriginEnumType._CF_enumeration)
Namespace.addCategoryObject('typeBinding', u'gridOriginEnumType', gridOriginEnumType)

# Atomic SimpleTypeDefinition
class angle360Type (pyxb.binding.datatypes.double):

    """An atomic simple type."""

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'angle360Type')
    _Documentation = None
angle360Type._CF_maxInclusive = pyxb.binding.facets.CF_maxInclusive(value_datatype=angle360Type, value=pyxb.binding.datatypes.double(360.0))
angle360Type._CF_minInclusive = pyxb.binding.facets.CF_minInclusive(value_datatype=angle360Type, value=pyxb.binding.datatypes.double(-360.0))
angle360Type._InitializeFacetMap(angle360Type._CF_maxInclusive,
   angle360Type._CF_minInclusive)
Namespace.addCategoryObject('typeBinding', u'angle360Type', angle360Type)

# Atomic SimpleTypeDefinition
class angle90Type (pyxb.binding.datatypes.double):

    """An atomic simple type."""

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'angle90Type')
    _Documentation = None
angle90Type._CF_maxInclusive = pyxb.binding.facets.CF_maxInclusive(value_datatype=angle90Type, value=pyxb.binding.datatypes.double(90.0))
angle90Type._CF_minInclusive = pyxb.binding.facets.CF_minInclusive(value_datatype=angle90Type, value=pyxb.binding.datatypes.double(-90.0))
angle90Type._InitializeFacetMap(angle90Type._CF_maxInclusive,
   angle90Type._CF_minInclusive)
Namespace.addCategoryObject('typeBinding', u'angle90Type', angle90Type)

# Atomic SimpleTypeDefinition
class colorType (pyxb.binding.datatypes.hexBinary):

    """
        
        aabbggrr
        
        ffffffff: opaque white
        ff000000: opaque black
        
        """

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'colorType')
    _Documentation = u'\n        \n        aabbggrr\n        \n        ffffffff: opaque white\n        ff000000: opaque black\n        \n        '
colorType._CF_length = pyxb.binding.facets.CF_length(value=pyxb.binding.datatypes.nonNegativeInteger(4L))
colorType._InitializeFacetMap(colorType._CF_length)
Namespace.addCategoryObject('typeBinding', u'colorType', colorType)

# Atomic SimpleTypeDefinition
class anglepos180Type (pyxb.binding.datatypes.double):

    """An atomic simple type."""

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'anglepos180Type')
    _Documentation = None
anglepos180Type._CF_maxInclusive = pyxb.binding.facets.CF_maxInclusive(value_datatype=anglepos180Type, value=pyxb.binding.datatypes.double(180.0))
anglepos180Type._CF_minInclusive = pyxb.binding.facets.CF_minInclusive(value_datatype=anglepos180Type, value=pyxb.binding.datatypes.double(0.0))
anglepos180Type._InitializeFacetMap(anglepos180Type._CF_maxInclusive,
   anglepos180Type._CF_minInclusive)
Namespace.addCategoryObject('typeBinding', u'anglepos180Type', anglepos180Type)

# Atomic SimpleTypeDefinition
class refreshModeEnumType (pyxb.binding.datatypes.string, pyxb.binding.basis.enumeration_mixin):

    """An atomic simple type."""

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'refreshModeEnumType')
    _Documentation = None
refreshModeEnumType._CF_enumeration = pyxb.binding.facets.CF_enumeration(value_datatype=refreshModeEnumType, enum_prefix=None)
refreshModeEnumType.onChange = refreshModeEnumType._CF_enumeration.addEnumeration(unicode_value=u'onChange', tag=u'onChange')
refreshModeEnumType.onInterval = refreshModeEnumType._CF_enumeration.addEnumeration(unicode_value=u'onInterval', tag=u'onInterval')
refreshModeEnumType.onExpire = refreshModeEnumType._CF_enumeration.addEnumeration(unicode_value=u'onExpire', tag=u'onExpire')
refreshModeEnumType._InitializeFacetMap(refreshModeEnumType._CF_enumeration)
Namespace.addCategoryObject('typeBinding', u'refreshModeEnumType', refreshModeEnumType)

# Atomic SimpleTypeDefinition
class viewRefreshModeEnumType (pyxb.binding.datatypes.string, pyxb.binding.basis.enumeration_mixin):

    """An atomic simple type."""

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'viewRefreshModeEnumType')
    _Documentation = None
viewRefreshModeEnumType._CF_enumeration = pyxb.binding.facets.CF_enumeration(value_datatype=viewRefreshModeEnumType, enum_prefix=None)
viewRefreshModeEnumType.never = viewRefreshModeEnumType._CF_enumeration.addEnumeration(unicode_value=u'never', tag=u'never')
viewRefreshModeEnumType.onRequest = viewRefreshModeEnumType._CF_enumeration.addEnumeration(unicode_value=u'onRequest', tag=u'onRequest')
viewRefreshModeEnumType.onStop = viewRefreshModeEnumType._CF_enumeration.addEnumeration(unicode_value=u'onStop', tag=u'onStop')
viewRefreshModeEnumType.onRegion = viewRefreshModeEnumType._CF_enumeration.addEnumeration(unicode_value=u'onRegion', tag=u'onRegion')
viewRefreshModeEnumType._InitializeFacetMap(viewRefreshModeEnumType._CF_enumeration)
Namespace.addCategoryObject('typeBinding', u'viewRefreshModeEnumType', viewRefreshModeEnumType)

# Atomic SimpleTypeDefinition
class listItemTypeEnumType (pyxb.binding.datatypes.string, pyxb.binding.basis.enumeration_mixin):

    """An atomic simple type."""

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'listItemTypeEnumType')
    _Documentation = None
listItemTypeEnumType._CF_enumeration = pyxb.binding.facets.CF_enumeration(value_datatype=listItemTypeEnumType, enum_prefix=None)
listItemTypeEnumType.radioFolder = listItemTypeEnumType._CF_enumeration.addEnumeration(unicode_value=u'radioFolder', tag=u'radioFolder')
listItemTypeEnumType.check = listItemTypeEnumType._CF_enumeration.addEnumeration(unicode_value=u'check', tag=u'check')
listItemTypeEnumType.checkHideChildren = listItemTypeEnumType._CF_enumeration.addEnumeration(unicode_value=u'checkHideChildren', tag=u'checkHideChildren')
listItemTypeEnumType.checkOffOnly = listItemTypeEnumType._CF_enumeration.addEnumeration(unicode_value=u'checkOffOnly', tag=u'checkOffOnly')
listItemTypeEnumType._InitializeFacetMap(listItemTypeEnumType._CF_enumeration)
Namespace.addCategoryObject('typeBinding', u'listItemTypeEnumType', listItemTypeEnumType)

# Atomic SimpleTypeDefinition
class altitudeModeEnumType (pyxb.binding.datatypes.string, pyxb.binding.basis.enumeration_mixin):

    """An atomic simple type."""

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'altitudeModeEnumType')
    _Documentation = None
altitudeModeEnumType._CF_enumeration = pyxb.binding.facets.CF_enumeration(value_datatype=altitudeModeEnumType, enum_prefix=None)
altitudeModeEnumType.clampToGround = altitudeModeEnumType._CF_enumeration.addEnumeration(unicode_value=u'clampToGround', tag=u'clampToGround')
altitudeModeEnumType.relativeToGround = altitudeModeEnumType._CF_enumeration.addEnumeration(unicode_value=u'relativeToGround', tag=u'relativeToGround')
altitudeModeEnumType.absolute = altitudeModeEnumType._CF_enumeration.addEnumeration(unicode_value=u'absolute', tag=u'absolute')
altitudeModeEnumType._InitializeFacetMap(altitudeModeEnumType._CF_enumeration)
Namespace.addCategoryObject('typeBinding', u'altitudeModeEnumType', altitudeModeEnumType)

# Atomic SimpleTypeDefinition
class itemIconStateEnumType (pyxb.binding.datatypes.string, pyxb.binding.basis.enumeration_mixin):

    """An atomic simple type."""

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'itemIconStateEnumType')
    _Documentation = None
itemIconStateEnumType._CF_enumeration = pyxb.binding.facets.CF_enumeration(value_datatype=itemIconStateEnumType, enum_prefix=None)
itemIconStateEnumType.open = itemIconStateEnumType._CF_enumeration.addEnumeration(unicode_value=u'open', tag=u'open')
itemIconStateEnumType.closed = itemIconStateEnumType._CF_enumeration.addEnumeration(unicode_value=u'closed', tag=u'closed')
itemIconStateEnumType.error = itemIconStateEnumType._CF_enumeration.addEnumeration(unicode_value=u'error', tag=u'error')
itemIconStateEnumType.fetching0 = itemIconStateEnumType._CF_enumeration.addEnumeration(unicode_value=u'fetching0', tag=u'fetching0')
itemIconStateEnumType.fetching1 = itemIconStateEnumType._CF_enumeration.addEnumeration(unicode_value=u'fetching1', tag=u'fetching1')
itemIconStateEnumType.fetching2 = itemIconStateEnumType._CF_enumeration.addEnumeration(unicode_value=u'fetching2', tag=u'fetching2')
itemIconStateEnumType._InitializeFacetMap(itemIconStateEnumType._CF_enumeration)
Namespace.addCategoryObject('typeBinding', u'itemIconStateEnumType', itemIconStateEnumType)

# List SimpleTypeDefinition
# superclasses pyxb.binding.datatypes.anySimpleType
class itemIconStateType (pyxb.binding.basis.STD_list):

    """Simple type that is a list of itemIconStateEnumType."""

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'itemIconStateType')
    _Documentation = None

    _ItemType = itemIconStateEnumType
itemIconStateType._InitializeFacetMap()
Namespace.addCategoryObject('typeBinding', u'itemIconStateType', itemIconStateType)

# Atomic SimpleTypeDefinition
class anglepos90Type (pyxb.binding.datatypes.double):

    """An atomic simple type."""

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'anglepos90Type')
    _Documentation = None
anglepos90Type._CF_maxInclusive = pyxb.binding.facets.CF_maxInclusive(value_datatype=anglepos90Type, value=pyxb.binding.datatypes.double(90.0))
anglepos90Type._CF_minInclusive = pyxb.binding.facets.CF_minInclusive(value_datatype=anglepos90Type, value=pyxb.binding.datatypes.double(0.0))
anglepos90Type._InitializeFacetMap(anglepos90Type._CF_maxInclusive,
   anglepos90Type._CF_minInclusive)
Namespace.addCategoryObject('typeBinding', u'anglepos90Type', anglepos90Type)

# Atomic SimpleTypeDefinition
class displayModeEnumType (pyxb.binding.datatypes.string, pyxb.binding.basis.enumeration_mixin):

    """An atomic simple type."""

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'displayModeEnumType')
    _Documentation = None
displayModeEnumType._CF_enumeration = pyxb.binding.facets.CF_enumeration(value_datatype=displayModeEnumType, enum_prefix=None)
displayModeEnumType.default = displayModeEnumType._CF_enumeration.addEnumeration(unicode_value=u'default', tag=u'default')
displayModeEnumType.hide = displayModeEnumType._CF_enumeration.addEnumeration(unicode_value=u'hide', tag=u'hide')
displayModeEnumType._InitializeFacetMap(displayModeEnumType._CF_enumeration)
Namespace.addCategoryObject('typeBinding', u'displayModeEnumType', displayModeEnumType)

# Atomic SimpleTypeDefinition
class colorModeEnumType (pyxb.binding.datatypes.string, pyxb.binding.basis.enumeration_mixin):

    """An atomic simple type."""

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'colorModeEnumType')
    _Documentation = None
colorModeEnumType._CF_enumeration = pyxb.binding.facets.CF_enumeration(value_datatype=colorModeEnumType, enum_prefix=None)
colorModeEnumType.normal = colorModeEnumType._CF_enumeration.addEnumeration(unicode_value=u'normal', tag=u'normal')
colorModeEnumType.random = colorModeEnumType._CF_enumeration.addEnumeration(unicode_value=u'random', tag=u'random')
colorModeEnumType._InitializeFacetMap(colorModeEnumType._CF_enumeration)
Namespace.addCategoryObject('typeBinding', u'colorModeEnumType', colorModeEnumType)

# Atomic SimpleTypeDefinition
class styleStateEnumType (pyxb.binding.datatypes.string, pyxb.binding.basis.enumeration_mixin):

    """An atomic simple type."""

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'styleStateEnumType')
    _Documentation = None
styleStateEnumType._CF_enumeration = pyxb.binding.facets.CF_enumeration(value_datatype=styleStateEnumType, enum_prefix=None)
styleStateEnumType.normal = styleStateEnumType._CF_enumeration.addEnumeration(unicode_value=u'normal', tag=u'normal')
styleStateEnumType.highlight = styleStateEnumType._CF_enumeration.addEnumeration(unicode_value=u'highlight', tag=u'highlight')
styleStateEnumType._InitializeFacetMap(styleStateEnumType._CF_enumeration)
Namespace.addCategoryObject('typeBinding', u'styleStateEnumType', styleStateEnumType)

# Complex type AbstractObjectType with content type ELEMENT_ONLY
class AbstractObjectType (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = True
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'AbstractObjectType')
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {http://www.opengis.net/kml/2.2}ObjectSimpleExtensionGroup uses Python identifier ObjectSimpleExtensionGroup
    __ObjectSimpleExtensionGroup = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'ObjectSimpleExtensionGroup'), 'ObjectSimpleExtensionGroup', '__httpwww_opengis_netkml2_2_AbstractObjectType_httpwww_opengis_netkml2_2ObjectSimpleExtensionGroup', True)

    
    ObjectSimpleExtensionGroup = property(__ObjectSimpleExtensionGroup.value, __ObjectSimpleExtensionGroup.set, None, None)

    
    # Attribute targetId uses Python identifier targetId
    __targetId = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'targetId'), 'targetId', '__httpwww_opengis_netkml2_2_AbstractObjectType_targetId', pyxb.binding.datatypes.NCName)
    
    targetId = property(__targetId.value, __targetId.set, None, None)

    
    # Attribute id uses Python identifier id
    __id = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'id'), 'id', '__httpwww_opengis_netkml2_2_AbstractObjectType_id', pyxb.binding.datatypes.ID)
    
    id = property(__id.value, __id.set, None, None)


    _ElementMap = {
        __ObjectSimpleExtensionGroup.name() : __ObjectSimpleExtensionGroup
    }
    _AttributeMap = {
        __targetId.name() : __targetId,
        __id.name() : __id
    }
Namespace.addCategoryObject('typeBinding', u'AbstractObjectType', AbstractObjectType)


# Complex type AbstractGeometryType with content type ELEMENT_ONLY
class AbstractGeometryType (AbstractObjectType):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = True
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'AbstractGeometryType')
    # Base type is AbstractObjectType
    
    # Element {http://www.opengis.net/kml/2.2}AbstractGeometrySimpleExtensionGroup uses Python identifier AbstractGeometrySimpleExtensionGroup
    __AbstractGeometrySimpleExtensionGroup = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'AbstractGeometrySimpleExtensionGroup'), 'AbstractGeometrySimpleExtensionGroup', '__httpwww_opengis_netkml2_2_AbstractGeometryType_httpwww_opengis_netkml2_2AbstractGeometrySimpleExtensionGroup', True)

    
    AbstractGeometrySimpleExtensionGroup = property(__AbstractGeometrySimpleExtensionGroup.value, __AbstractGeometrySimpleExtensionGroup.set, None, None)

    
    # Element {http://www.opengis.net/kml/2.2}AbstractGeometryObjectExtensionGroup uses Python identifier AbstractGeometryObjectExtensionGroup
    __AbstractGeometryObjectExtensionGroup = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'AbstractGeometryObjectExtensionGroup'), 'AbstractGeometryObjectExtensionGroup', '__httpwww_opengis_netkml2_2_AbstractGeometryType_httpwww_opengis_netkml2_2AbstractGeometryObjectExtensionGroup', True)

    
    AbstractGeometryObjectExtensionGroup = property(__AbstractGeometryObjectExtensionGroup.value, __AbstractGeometryObjectExtensionGroup.set, None, None)

    
    # Element ObjectSimpleExtensionGroup ({http://www.opengis.net/kml/2.2}ObjectSimpleExtensionGroup) inherited from {http://www.opengis.net/kml/2.2}AbstractObjectType
    
    # Attribute targetId inherited from {http://www.opengis.net/kml/2.2}AbstractObjectType
    
    # Attribute id inherited from {http://www.opengis.net/kml/2.2}AbstractObjectType

    _ElementMap = AbstractObjectType._ElementMap.copy()
    _ElementMap.update({
        __AbstractGeometrySimpleExtensionGroup.name() : __AbstractGeometrySimpleExtensionGroup,
        __AbstractGeometryObjectExtensionGroup.name() : __AbstractGeometryObjectExtensionGroup
    })
    _AttributeMap = AbstractObjectType._AttributeMap.copy()
    _AttributeMap.update({
        
    })
Namespace.addCategoryObject('typeBinding', u'AbstractGeometryType', AbstractGeometryType)


# Complex type LocationType with content type ELEMENT_ONLY
class LocationType (AbstractObjectType):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'LocationType')
    # Base type is AbstractObjectType
    
    # Element {http://www.opengis.net/kml/2.2}latitude uses Python identifier latitude
    __latitude = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'latitude'), 'latitude', '__httpwww_opengis_netkml2_2_LocationType_httpwww_opengis_netkml2_2latitude', False)

    
    latitude = property(__latitude.value, __latitude.set, None, None)

    
    # Element ObjectSimpleExtensionGroup ({http://www.opengis.net/kml/2.2}ObjectSimpleExtensionGroup) inherited from {http://www.opengis.net/kml/2.2}AbstractObjectType
    
    # Element {http://www.opengis.net/kml/2.2}altitude uses Python identifier altitude
    __altitude = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'altitude'), 'altitude', '__httpwww_opengis_netkml2_2_LocationType_httpwww_opengis_netkml2_2altitude', False)

    
    altitude = property(__altitude.value, __altitude.set, None, None)

    
    # Element {http://www.opengis.net/kml/2.2}longitude uses Python identifier longitude
    __longitude = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'longitude'), 'longitude', '__httpwww_opengis_netkml2_2_LocationType_httpwww_opengis_netkml2_2longitude', False)

    
    longitude = property(__longitude.value, __longitude.set, None, None)

    
    # Element {http://www.opengis.net/kml/2.2}LocationObjectExtensionGroup uses Python identifier LocationObjectExtensionGroup
    __LocationObjectExtensionGroup = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'LocationObjectExtensionGroup'), 'LocationObjectExtensionGroup', '__httpwww_opengis_netkml2_2_LocationType_httpwww_opengis_netkml2_2LocationObjectExtensionGroup', True)

    
    LocationObjectExtensionGroup = property(__LocationObjectExtensionGroup.value, __LocationObjectExtensionGroup.set, None, None)

    
    # Element {http://www.opengis.net/kml/2.2}LocationSimpleExtensionGroup uses Python identifier LocationSimpleExtensionGroup
    __LocationSimpleExtensionGroup = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'LocationSimpleExtensionGroup'), 'LocationSimpleExtensionGroup', '__httpwww_opengis_netkml2_2_LocationType_httpwww_opengis_netkml2_2LocationSimpleExtensionGroup', True)

    
    LocationSimpleExtensionGroup = property(__LocationSimpleExtensionGroup.value, __LocationSimpleExtensionGroup.set, None, None)

    
    # Attribute targetId inherited from {http://www.opengis.net/kml/2.2}AbstractObjectType
    
    # Attribute id inherited from {http://www.opengis.net/kml/2.2}AbstractObjectType

    _ElementMap = AbstractObjectType._ElementMap.copy()
    _ElementMap.update({
        __latitude.name() : __latitude,
        __altitude.name() : __altitude,
        __longitude.name() : __longitude,
        __LocationObjectExtensionGroup.name() : __LocationObjectExtensionGroup,
        __LocationSimpleExtensionGroup.name() : __LocationSimpleExtensionGroup
    })
    _AttributeMap = AbstractObjectType._AttributeMap.copy()
    _AttributeMap.update({
        
    })
Namespace.addCategoryObject('typeBinding', u'LocationType', LocationType)


# Complex type AbstractSubStyleType with content type ELEMENT_ONLY
class AbstractSubStyleType (AbstractObjectType):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = True
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'AbstractSubStyleType')
    # Base type is AbstractObjectType
    
    # Element {http://www.opengis.net/kml/2.2}AbstractSubStyleObjectExtensionGroup uses Python identifier AbstractSubStyleObjectExtensionGroup
    __AbstractSubStyleObjectExtensionGroup = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'AbstractSubStyleObjectExtensionGroup'), 'AbstractSubStyleObjectExtensionGroup', '__httpwww_opengis_netkml2_2_AbstractSubStyleType_httpwww_opengis_netkml2_2AbstractSubStyleObjectExtensionGroup', True)

    
    AbstractSubStyleObjectExtensionGroup = property(__AbstractSubStyleObjectExtensionGroup.value, __AbstractSubStyleObjectExtensionGroup.set, None, None)

    
    # Element {http://www.opengis.net/kml/2.2}AbstractSubStyleSimpleExtensionGroup uses Python identifier AbstractSubStyleSimpleExtensionGroup
    __AbstractSubStyleSimpleExtensionGroup = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'AbstractSubStyleSimpleExtensionGroup'), 'AbstractSubStyleSimpleExtensionGroup', '__httpwww_opengis_netkml2_2_AbstractSubStyleType_httpwww_opengis_netkml2_2AbstractSubStyleSimpleExtensionGroup', True)

    
    AbstractSubStyleSimpleExtensionGroup = property(__AbstractSubStyleSimpleExtensionGroup.value, __AbstractSubStyleSimpleExtensionGroup.set, None, None)

    
    # Element ObjectSimpleExtensionGroup ({http://www.opengis.net/kml/2.2}ObjectSimpleExtensionGroup) inherited from {http://www.opengis.net/kml/2.2}AbstractObjectType
    
    # Attribute targetId inherited from {http://www.opengis.net/kml/2.2}AbstractObjectType
    
    # Attribute id inherited from {http://www.opengis.net/kml/2.2}AbstractObjectType

    _ElementMap = AbstractObjectType._ElementMap.copy()
    _ElementMap.update({
        __AbstractSubStyleObjectExtensionGroup.name() : __AbstractSubStyleObjectExtensionGroup,
        __AbstractSubStyleSimpleExtensionGroup.name() : __AbstractSubStyleSimpleExtensionGroup
    })
    _AttributeMap = AbstractObjectType._AttributeMap.copy()
    _AttributeMap.update({
        
    })
Namespace.addCategoryObject('typeBinding', u'AbstractSubStyleType', AbstractSubStyleType)


# Complex type AbstractColorStyleType with content type ELEMENT_ONLY
class AbstractColorStyleType (AbstractSubStyleType):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = True
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'AbstractColorStyleType')
    # Base type is AbstractSubStyleType
    
    # Element {http://www.opengis.net/kml/2.2}AbstractColorStyleSimpleExtensionGroup uses Python identifier AbstractColorStyleSimpleExtensionGroup
    __AbstractColorStyleSimpleExtensionGroup = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'AbstractColorStyleSimpleExtensionGroup'), 'AbstractColorStyleSimpleExtensionGroup', '__httpwww_opengis_netkml2_2_AbstractColorStyleType_httpwww_opengis_netkml2_2AbstractColorStyleSimpleExtensionGroup', True)

    
    AbstractColorStyleSimpleExtensionGroup = property(__AbstractColorStyleSimpleExtensionGroup.value, __AbstractColorStyleSimpleExtensionGroup.set, None, None)

    
    # Element ObjectSimpleExtensionGroup ({http://www.opengis.net/kml/2.2}ObjectSimpleExtensionGroup) inherited from {http://www.opengis.net/kml/2.2}AbstractObjectType
    
    # Element {http://www.opengis.net/kml/2.2}color uses Python identifier color
    __color = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'color'), 'color', '__httpwww_opengis_netkml2_2_AbstractColorStyleType_httpwww_opengis_netkml2_2color', False)

    
    color = property(__color.value, __color.set, None, None)

    
    # Element AbstractSubStyleSimpleExtensionGroup ({http://www.opengis.net/kml/2.2}AbstractSubStyleSimpleExtensionGroup) inherited from {http://www.opengis.net/kml/2.2}AbstractSubStyleType
    
    # Element {http://www.opengis.net/kml/2.2}AbstractColorStyleObjectExtensionGroup uses Python identifier AbstractColorStyleObjectExtensionGroup
    __AbstractColorStyleObjectExtensionGroup = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'AbstractColorStyleObjectExtensionGroup'), 'AbstractColorStyleObjectExtensionGroup', '__httpwww_opengis_netkml2_2_AbstractColorStyleType_httpwww_opengis_netkml2_2AbstractColorStyleObjectExtensionGroup', True)

    
    AbstractColorStyleObjectExtensionGroup = property(__AbstractColorStyleObjectExtensionGroup.value, __AbstractColorStyleObjectExtensionGroup.set, None, None)

    
    # Element AbstractSubStyleObjectExtensionGroup ({http://www.opengis.net/kml/2.2}AbstractSubStyleObjectExtensionGroup) inherited from {http://www.opengis.net/kml/2.2}AbstractSubStyleType
    
    # Element {http://www.opengis.net/kml/2.2}colorMode uses Python identifier colorMode
    __colorMode = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'colorMode'), 'colorMode', '__httpwww_opengis_netkml2_2_AbstractColorStyleType_httpwww_opengis_netkml2_2colorMode', False)

    
    colorMode = property(__colorMode.value, __colorMode.set, None, None)

    
    # Attribute targetId inherited from {http://www.opengis.net/kml/2.2}AbstractObjectType
    
    # Attribute id inherited from {http://www.opengis.net/kml/2.2}AbstractObjectType

    _ElementMap = AbstractSubStyleType._ElementMap.copy()
    _ElementMap.update({
        __AbstractColorStyleSimpleExtensionGroup.name() : __AbstractColorStyleSimpleExtensionGroup,
        __color.name() : __color,
        __AbstractColorStyleObjectExtensionGroup.name() : __AbstractColorStyleObjectExtensionGroup,
        __colorMode.name() : __colorMode
    })
    _AttributeMap = AbstractSubStyleType._AttributeMap.copy()
    _AttributeMap.update({
        
    })
Namespace.addCategoryObject('typeBinding', u'AbstractColorStyleType', AbstractColorStyleType)


# Complex type IconStyleType with content type ELEMENT_ONLY
class IconStyleType (AbstractColorStyleType):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'IconStyleType')
    # Base type is AbstractColorStyleType
    
    # Element {http://www.opengis.net/kml/2.2}Icon uses Python identifier Icon
    __Icon = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'Icon'), 'Icon', '__httpwww_opengis_netkml2_2_IconStyleType_httpwww_opengis_netkml2_2Icon', False)

    
    Icon = property(__Icon.value, __Icon.set, None, None)

    
    # Element {http://www.opengis.net/kml/2.2}hotSpot uses Python identifier hotSpot
    __hotSpot = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'hotSpot'), 'hotSpot', '__httpwww_opengis_netkml2_2_IconStyleType_httpwww_opengis_netkml2_2hotSpot', False)

    
    hotSpot = property(__hotSpot.value, __hotSpot.set, None, None)

    
    # Element {http://www.opengis.net/kml/2.2}IconStyleSimpleExtensionGroup uses Python identifier IconStyleSimpleExtensionGroup
    __IconStyleSimpleExtensionGroup = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'IconStyleSimpleExtensionGroup'), 'IconStyleSimpleExtensionGroup', '__httpwww_opengis_netkml2_2_IconStyleType_httpwww_opengis_netkml2_2IconStyleSimpleExtensionGroup', True)

    
    IconStyleSimpleExtensionGroup = property(__IconStyleSimpleExtensionGroup.value, __IconStyleSimpleExtensionGroup.set, None, None)

    
    # Element AbstractColorStyleObjectExtensionGroup ({http://www.opengis.net/kml/2.2}AbstractColorStyleObjectExtensionGroup) inherited from {http://www.opengis.net/kml/2.2}AbstractColorStyleType
    
    # Element ObjectSimpleExtensionGroup ({http://www.opengis.net/kml/2.2}ObjectSimpleExtensionGroup) inherited from {http://www.opengis.net/kml/2.2}AbstractObjectType
    
    # Element AbstractSubStyleSimpleExtensionGroup ({http://www.opengis.net/kml/2.2}AbstractSubStyleSimpleExtensionGroup) inherited from {http://www.opengis.net/kml/2.2}AbstractSubStyleType
    
    # Element color ({http://www.opengis.net/kml/2.2}color) inherited from {http://www.opengis.net/kml/2.2}AbstractColorStyleType
    
    # Element {http://www.opengis.net/kml/2.2}IconStyleObjectExtensionGroup uses Python identifier IconStyleObjectExtensionGroup
    __IconStyleObjectExtensionGroup = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'IconStyleObjectExtensionGroup'), 'IconStyleObjectExtensionGroup', '__httpwww_opengis_netkml2_2_IconStyleType_httpwww_opengis_netkml2_2IconStyleObjectExtensionGroup', True)

    
    IconStyleObjectExtensionGroup = property(__IconStyleObjectExtensionGroup.value, __IconStyleObjectExtensionGroup.set, None, None)

    
    # Element {http://www.opengis.net/kml/2.2}scale uses Python identifier scale
    __scale = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'scale'), 'scale', '__httpwww_opengis_netkml2_2_IconStyleType_httpwww_opengis_netkml2_2scale', False)

    
    scale = property(__scale.value, __scale.set, None, None)

    
    # Element AbstractColorStyleSimpleExtensionGroup ({http://www.opengis.net/kml/2.2}AbstractColorStyleSimpleExtensionGroup) inherited from {http://www.opengis.net/kml/2.2}AbstractColorStyleType
    
    # Element AbstractSubStyleObjectExtensionGroup ({http://www.opengis.net/kml/2.2}AbstractSubStyleObjectExtensionGroup) inherited from {http://www.opengis.net/kml/2.2}AbstractSubStyleType
    
    # Element colorMode ({http://www.opengis.net/kml/2.2}colorMode) inherited from {http://www.opengis.net/kml/2.2}AbstractColorStyleType
    
    # Element {http://www.opengis.net/kml/2.2}heading uses Python identifier heading
    __heading = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'heading'), 'heading', '__httpwww_opengis_netkml2_2_IconStyleType_httpwww_opengis_netkml2_2heading', False)

    
    heading = property(__heading.value, __heading.set, None, None)

    
    # Attribute targetId inherited from {http://www.opengis.net/kml/2.2}AbstractObjectType
    
    # Attribute id inherited from {http://www.opengis.net/kml/2.2}AbstractObjectType

    _ElementMap = AbstractColorStyleType._ElementMap.copy()
    _ElementMap.update({
        __Icon.name() : __Icon,
        __hotSpot.name() : __hotSpot,
        __IconStyleSimpleExtensionGroup.name() : __IconStyleSimpleExtensionGroup,
        __IconStyleObjectExtensionGroup.name() : __IconStyleObjectExtensionGroup,
        __scale.name() : __scale,
        __heading.name() : __heading
    })
    _AttributeMap = AbstractColorStyleType._AttributeMap.copy()
    _AttributeMap.update({
        
    })
Namespace.addCategoryObject('typeBinding', u'IconStyleType', IconStyleType)


# Complex type DataType with content type ELEMENT_ONLY
class DataType (AbstractObjectType):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'DataType')
    # Base type is AbstractObjectType
    
    # Element {http://www.opengis.net/kml/2.2}DataExtension uses Python identifier DataExtension
    __DataExtension = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'DataExtension'), 'DataExtension', '__httpwww_opengis_netkml2_2_DataType_httpwww_opengis_netkml2_2DataExtension', True)

    
    DataExtension = property(__DataExtension.value, __DataExtension.set, None, None)

    
    # Element {http://www.opengis.net/kml/2.2}value uses Python identifier value_
    __value = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'value'), 'value_', '__httpwww_opengis_netkml2_2_DataType_httpwww_opengis_netkml2_2value', False)

    
    value_ = property(__value.value, __value.set, None, None)

    
    # Element ObjectSimpleExtensionGroup ({http://www.opengis.net/kml/2.2}ObjectSimpleExtensionGroup) inherited from {http://www.opengis.net/kml/2.2}AbstractObjectType
    
    # Element {http://www.opengis.net/kml/2.2}displayName uses Python identifier displayName
    __displayName = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'displayName'), 'displayName', '__httpwww_opengis_netkml2_2_DataType_httpwww_opengis_netkml2_2displayName', False)

    
    displayName = property(__displayName.value, __displayName.set, None, None)

    
    # Attribute targetId inherited from {http://www.opengis.net/kml/2.2}AbstractObjectType
    
    # Attribute name uses Python identifier name
    __name = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'name'), 'name', '__httpwww_opengis_netkml2_2_DataType_name', pyxb.binding.datatypes.string)
    
    name = property(__name.value, __name.set, None, None)

    
    # Attribute id inherited from {http://www.opengis.net/kml/2.2}AbstractObjectType

    _ElementMap = AbstractObjectType._ElementMap.copy()
    _ElementMap.update({
        __DataExtension.name() : __DataExtension,
        __value.name() : __value,
        __displayName.name() : __displayName
    })
    _AttributeMap = AbstractObjectType._AttributeMap.copy()
    _AttributeMap.update({
        __name.name() : __name
    })
Namespace.addCategoryObject('typeBinding', u'DataType', DataType)


# Complex type AliasType with content type ELEMENT_ONLY
class AliasType (AbstractObjectType):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'AliasType')
    # Base type is AbstractObjectType
    
    # Element {http://www.opengis.net/kml/2.2}sourceHref uses Python identifier sourceHref
    __sourceHref = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'sourceHref'), 'sourceHref', '__httpwww_opengis_netkml2_2_AliasType_httpwww_opengis_netkml2_2sourceHref', False)

    
    sourceHref = property(__sourceHref.value, __sourceHref.set, None, None)

    
    # Element {http://www.opengis.net/kml/2.2}AliasObjectExtensionGroup uses Python identifier AliasObjectExtensionGroup
    __AliasObjectExtensionGroup = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'AliasObjectExtensionGroup'), 'AliasObjectExtensionGroup', '__httpwww_opengis_netkml2_2_AliasType_httpwww_opengis_netkml2_2AliasObjectExtensionGroup', True)

    
    AliasObjectExtensionGroup = property(__AliasObjectExtensionGroup.value, __AliasObjectExtensionGroup.set, None, None)

    
    # Element {http://www.opengis.net/kml/2.2}targetHref uses Python identifier targetHref
    __targetHref = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'targetHref'), 'targetHref', '__httpwww_opengis_netkml2_2_AliasType_httpwww_opengis_netkml2_2targetHref', False)

    
    targetHref = property(__targetHref.value, __targetHref.set, None, None)

    
    # Element ObjectSimpleExtensionGroup ({http://www.opengis.net/kml/2.2}ObjectSimpleExtensionGroup) inherited from {http://www.opengis.net/kml/2.2}AbstractObjectType
    
    # Element {http://www.opengis.net/kml/2.2}AliasSimpleExtensionGroup uses Python identifier AliasSimpleExtensionGroup
    __AliasSimpleExtensionGroup = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'AliasSimpleExtensionGroup'), 'AliasSimpleExtensionGroup', '__httpwww_opengis_netkml2_2_AliasType_httpwww_opengis_netkml2_2AliasSimpleExtensionGroup', True)

    
    AliasSimpleExtensionGroup = property(__AliasSimpleExtensionGroup.value, __AliasSimpleExtensionGroup.set, None, None)

    
    # Attribute targetId inherited from {http://www.opengis.net/kml/2.2}AbstractObjectType
    
    # Attribute id inherited from {http://www.opengis.net/kml/2.2}AbstractObjectType

    _ElementMap = AbstractObjectType._ElementMap.copy()
    _ElementMap.update({
        __sourceHref.name() : __sourceHref,
        __AliasObjectExtensionGroup.name() : __AliasObjectExtensionGroup,
        __targetHref.name() : __targetHref,
        __AliasSimpleExtensionGroup.name() : __AliasSimpleExtensionGroup
    })
    _AttributeMap = AbstractObjectType._AttributeMap.copy()
    _AttributeMap.update({
        
    })
Namespace.addCategoryObject('typeBinding', u'AliasType', AliasType)


# Complex type BasicLinkType with content type ELEMENT_ONLY
class BasicLinkType (AbstractObjectType):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'BasicLinkType')
    # Base type is AbstractObjectType
    
    # Element {http://www.opengis.net/kml/2.2}BasicLinkSimpleExtensionGroup uses Python identifier BasicLinkSimpleExtensionGroup
    __BasicLinkSimpleExtensionGroup = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'BasicLinkSimpleExtensionGroup'), 'BasicLinkSimpleExtensionGroup', '__httpwww_opengis_netkml2_2_BasicLinkType_httpwww_opengis_netkml2_2BasicLinkSimpleExtensionGroup', True)

    
    BasicLinkSimpleExtensionGroup = property(__BasicLinkSimpleExtensionGroup.value, __BasicLinkSimpleExtensionGroup.set, None, None)

    
    # Element {http://www.opengis.net/kml/2.2}href uses Python identifier href
    __href = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'href'), 'href', '__httpwww_opengis_netkml2_2_BasicLinkType_httpwww_opengis_netkml2_2href', False)

    
    href = property(__href.value, __href.set, None, u'not anyURI due to $[x] substitution in\n      PhotoOverlay')

    
    # Element ObjectSimpleExtensionGroup ({http://www.opengis.net/kml/2.2}ObjectSimpleExtensionGroup) inherited from {http://www.opengis.net/kml/2.2}AbstractObjectType
    
    # Element {http://www.opengis.net/kml/2.2}BasicLinkObjectExtensionGroup uses Python identifier BasicLinkObjectExtensionGroup
    __BasicLinkObjectExtensionGroup = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'BasicLinkObjectExtensionGroup'), 'BasicLinkObjectExtensionGroup', '__httpwww_opengis_netkml2_2_BasicLinkType_httpwww_opengis_netkml2_2BasicLinkObjectExtensionGroup', True)

    
    BasicLinkObjectExtensionGroup = property(__BasicLinkObjectExtensionGroup.value, __BasicLinkObjectExtensionGroup.set, None, None)

    
    # Attribute targetId inherited from {http://www.opengis.net/kml/2.2}AbstractObjectType
    
    # Attribute id inherited from {http://www.opengis.net/kml/2.2}AbstractObjectType

    _ElementMap = AbstractObjectType._ElementMap.copy()
    _ElementMap.update({
        __BasicLinkSimpleExtensionGroup.name() : __BasicLinkSimpleExtensionGroup,
        __href.name() : __href,
        __BasicLinkObjectExtensionGroup.name() : __BasicLinkObjectExtensionGroup
    })
    _AttributeMap = AbstractObjectType._AttributeMap.copy()
    _AttributeMap.update({
        
    })
Namespace.addCategoryObject('typeBinding', u'BasicLinkType', BasicLinkType)


# Complex type AbstractStyleSelectorType with content type ELEMENT_ONLY
class AbstractStyleSelectorType (AbstractObjectType):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = True
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'AbstractStyleSelectorType')
    # Base type is AbstractObjectType
    
    # Element {http://www.opengis.net/kml/2.2}AbstractStyleSelectorObjectExtensionGroup uses Python identifier AbstractStyleSelectorObjectExtensionGroup
    __AbstractStyleSelectorObjectExtensionGroup = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'AbstractStyleSelectorObjectExtensionGroup'), 'AbstractStyleSelectorObjectExtensionGroup', '__httpwww_opengis_netkml2_2_AbstractStyleSelectorType_httpwww_opengis_netkml2_2AbstractStyleSelectorObjectExtensionGroup', True)

    
    AbstractStyleSelectorObjectExtensionGroup = property(__AbstractStyleSelectorObjectExtensionGroup.value, __AbstractStyleSelectorObjectExtensionGroup.set, None, None)

    
    # Element ObjectSimpleExtensionGroup ({http://www.opengis.net/kml/2.2}ObjectSimpleExtensionGroup) inherited from {http://www.opengis.net/kml/2.2}AbstractObjectType
    
    # Element {http://www.opengis.net/kml/2.2}AbstractStyleSelectorSimpleExtensionGroup uses Python identifier AbstractStyleSelectorSimpleExtensionGroup
    __AbstractStyleSelectorSimpleExtensionGroup = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'AbstractStyleSelectorSimpleExtensionGroup'), 'AbstractStyleSelectorSimpleExtensionGroup', '__httpwww_opengis_netkml2_2_AbstractStyleSelectorType_httpwww_opengis_netkml2_2AbstractStyleSelectorSimpleExtensionGroup', True)

    
    AbstractStyleSelectorSimpleExtensionGroup = property(__AbstractStyleSelectorSimpleExtensionGroup.value, __AbstractStyleSelectorSimpleExtensionGroup.set, None, None)

    
    # Attribute targetId inherited from {http://www.opengis.net/kml/2.2}AbstractObjectType
    
    # Attribute id inherited from {http://www.opengis.net/kml/2.2}AbstractObjectType

    _ElementMap = AbstractObjectType._ElementMap.copy()
    _ElementMap.update({
        __AbstractStyleSelectorObjectExtensionGroup.name() : __AbstractStyleSelectorObjectExtensionGroup,
        __AbstractStyleSelectorSimpleExtensionGroup.name() : __AbstractStyleSelectorSimpleExtensionGroup
    })
    _AttributeMap = AbstractObjectType._AttributeMap.copy()
    _AttributeMap.update({
        
    })
Namespace.addCategoryObject('typeBinding', u'AbstractStyleSelectorType', AbstractStyleSelectorType)


# Complex type NetworkLinkControlType with content type ELEMENT_ONLY
class NetworkLinkControlType (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'NetworkLinkControlType')
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {http://www.opengis.net/kml/2.2}linkName uses Python identifier linkName
    __linkName = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'linkName'), 'linkName', '__httpwww_opengis_netkml2_2_NetworkLinkControlType_httpwww_opengis_netkml2_2linkName', False)

    
    linkName = property(__linkName.value, __linkName.set, None, None)

    
    # Element {http://www.opengis.net/kml/2.2}expires uses Python identifier expires
    __expires = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'expires'), 'expires', '__httpwww_opengis_netkml2_2_NetworkLinkControlType_httpwww_opengis_netkml2_2expires', False)

    
    expires = property(__expires.value, __expires.set, None, None)

    
    # Element {http://www.opengis.net/kml/2.2}Update uses Python identifier Update
    __Update = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'Update'), 'Update', '__httpwww_opengis_netkml2_2_NetworkLinkControlType_httpwww_opengis_netkml2_2Update', False)

    
    Update = property(__Update.value, __Update.set, None, None)

    
    # Element {http://www.opengis.net/kml/2.2}cookie uses Python identifier cookie
    __cookie = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'cookie'), 'cookie', '__httpwww_opengis_netkml2_2_NetworkLinkControlType_httpwww_opengis_netkml2_2cookie', False)

    
    cookie = property(__cookie.value, __cookie.set, None, None)

    
    # Element {http://www.opengis.net/kml/2.2}NetworkLinkControlSimpleExtensionGroup uses Python identifier NetworkLinkControlSimpleExtensionGroup
    __NetworkLinkControlSimpleExtensionGroup = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'NetworkLinkControlSimpleExtensionGroup'), 'NetworkLinkControlSimpleExtensionGroup', '__httpwww_opengis_netkml2_2_NetworkLinkControlType_httpwww_opengis_netkml2_2NetworkLinkControlSimpleExtensionGroup', True)

    
    NetworkLinkControlSimpleExtensionGroup = property(__NetworkLinkControlSimpleExtensionGroup.value, __NetworkLinkControlSimpleExtensionGroup.set, None, None)

    
    # Element {http://www.opengis.net/kml/2.2}linkDescription uses Python identifier linkDescription
    __linkDescription = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'linkDescription'), 'linkDescription', '__httpwww_opengis_netkml2_2_NetworkLinkControlType_httpwww_opengis_netkml2_2linkDescription', False)

    
    linkDescription = property(__linkDescription.value, __linkDescription.set, None, None)

    
    # Element {http://www.opengis.net/kml/2.2}maxSessionLength uses Python identifier maxSessionLength
    __maxSessionLength = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'maxSessionLength'), 'maxSessionLength', '__httpwww_opengis_netkml2_2_NetworkLinkControlType_httpwww_opengis_netkml2_2maxSessionLength', False)

    
    maxSessionLength = property(__maxSessionLength.value, __maxSessionLength.set, None, None)

    
    # Element {http://www.opengis.net/kml/2.2}minRefreshPeriod uses Python identifier minRefreshPeriod
    __minRefreshPeriod = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'minRefreshPeriod'), 'minRefreshPeriod', '__httpwww_opengis_netkml2_2_NetworkLinkControlType_httpwww_opengis_netkml2_2minRefreshPeriod', False)

    
    minRefreshPeriod = property(__minRefreshPeriod.value, __minRefreshPeriod.set, None, None)

    
    # Element {http://www.opengis.net/kml/2.2}message uses Python identifier message
    __message = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'message'), 'message', '__httpwww_opengis_netkml2_2_NetworkLinkControlType_httpwww_opengis_netkml2_2message', False)

    
    message = property(__message.value, __message.set, None, None)

    
    # Element {http://www.opengis.net/kml/2.2}NetworkLinkControlObjectExtensionGroup uses Python identifier NetworkLinkControlObjectExtensionGroup
    __NetworkLinkControlObjectExtensionGroup = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'NetworkLinkControlObjectExtensionGroup'), 'NetworkLinkControlObjectExtensionGroup', '__httpwww_opengis_netkml2_2_NetworkLinkControlType_httpwww_opengis_netkml2_2NetworkLinkControlObjectExtensionGroup', True)

    
    NetworkLinkControlObjectExtensionGroup = property(__NetworkLinkControlObjectExtensionGroup.value, __NetworkLinkControlObjectExtensionGroup.set, None, None)

    
    # Element {http://www.opengis.net/kml/2.2}linkSnippet uses Python identifier linkSnippet
    __linkSnippet = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'linkSnippet'), 'linkSnippet', '__httpwww_opengis_netkml2_2_NetworkLinkControlType_httpwww_opengis_netkml2_2linkSnippet', False)

    
    linkSnippet = property(__linkSnippet.value, __linkSnippet.set, None, None)

    
    # Element {http://www.opengis.net/kml/2.2}AbstractViewGroup uses Python identifier AbstractViewGroup
    __AbstractViewGroup = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'AbstractViewGroup'), 'AbstractViewGroup', '__httpwww_opengis_netkml2_2_NetworkLinkControlType_httpwww_opengis_netkml2_2AbstractViewGroup', False)

    
    AbstractViewGroup = property(__AbstractViewGroup.value, __AbstractViewGroup.set, None, None)


    _ElementMap = {
        __linkName.name() : __linkName,
        __expires.name() : __expires,
        __Update.name() : __Update,
        __cookie.name() : __cookie,
        __NetworkLinkControlSimpleExtensionGroup.name() : __NetworkLinkControlSimpleExtensionGroup,
        __linkDescription.name() : __linkDescription,
        __maxSessionLength.name() : __maxSessionLength,
        __minRefreshPeriod.name() : __minRefreshPeriod,
        __message.name() : __message,
        __NetworkLinkControlObjectExtensionGroup.name() : __NetworkLinkControlObjectExtensionGroup,
        __linkSnippet.name() : __linkSnippet,
        __AbstractViewGroup.name() : __AbstractViewGroup
    }
    _AttributeMap = {
        
    }
Namespace.addCategoryObject('typeBinding', u'NetworkLinkControlType', NetworkLinkControlType)


# Complex type AbstractFeatureType with content type ELEMENT_ONLY
class AbstractFeatureType (AbstractObjectType):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = True
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'AbstractFeatureType')
    # Base type is AbstractObjectType
    
    # Element {http://www.w3.org/2005/Atom}link uses Python identifier link
    __link = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/2005/Atom'), u'link'), 'link', '__httpwww_opengis_netkml2_2_AbstractFeatureType_httpwww_w3_org2005Atomlink', False)

    
    link = property(__link.value, __link.set, None, None)

    
    # Element {http://www.opengis.net/kml/2.2}snippet uses Python identifier snippet
    __snippet = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'snippet'), 'snippet', '__httpwww_opengis_netkml2_2_AbstractFeatureType_httpwww_opengis_netkml2_2snippet', False)

    
    snippet = property(__snippet.value, __snippet.set, None, None)

    
    # Element {http://www.opengis.net/kml/2.2}AbstractStyleSelectorGroup uses Python identifier AbstractStyleSelectorGroup
    __AbstractStyleSelectorGroup = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'AbstractStyleSelectorGroup'), 'AbstractStyleSelectorGroup', '__httpwww_opengis_netkml2_2_AbstractFeatureType_httpwww_opengis_netkml2_2AbstractStyleSelectorGroup', True)

    
    AbstractStyleSelectorGroup = property(__AbstractStyleSelectorGroup.value, __AbstractStyleSelectorGroup.set, None, None)

    
    # Element {http://www.opengis.net/kml/2.2}AbstractFeatureObjectExtensionGroup uses Python identifier AbstractFeatureObjectExtensionGroup
    __AbstractFeatureObjectExtensionGroup = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'AbstractFeatureObjectExtensionGroup'), 'AbstractFeatureObjectExtensionGroup', '__httpwww_opengis_netkml2_2_AbstractFeatureType_httpwww_opengis_netkml2_2AbstractFeatureObjectExtensionGroup', True)

    
    AbstractFeatureObjectExtensionGroup = property(__AbstractFeatureObjectExtensionGroup.value, __AbstractFeatureObjectExtensionGroup.set, None, None)

    
    # Element {http://www.opengis.net/kml/2.2}description uses Python identifier description
    __description = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'description'), 'description', '__httpwww_opengis_netkml2_2_AbstractFeatureType_httpwww_opengis_netkml2_2description', False)

    
    description = property(__description.value, __description.set, None, None)

    
    # Element {http://www.opengis.net/kml/2.2}AbstractTimePrimitiveGroup uses Python identifier AbstractTimePrimitiveGroup
    __AbstractTimePrimitiveGroup = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'AbstractTimePrimitiveGroup'), 'AbstractTimePrimitiveGroup', '__httpwww_opengis_netkml2_2_AbstractFeatureType_httpwww_opengis_netkml2_2AbstractTimePrimitiveGroup', False)

    
    AbstractTimePrimitiveGroup = property(__AbstractTimePrimitiveGroup.value, __AbstractTimePrimitiveGroup.set, None, None)

    
    # Element {http://www.opengis.net/kml/2.2}Region uses Python identifier Region
    __Region = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'Region'), 'Region', '__httpwww_opengis_netkml2_2_AbstractFeatureType_httpwww_opengis_netkml2_2Region', False)

    
    Region = property(__Region.value, __Region.set, None, None)

    
    # Element {http://www.opengis.net/kml/2.2}address uses Python identifier address
    __address = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'address'), 'address', '__httpwww_opengis_netkml2_2_AbstractFeatureType_httpwww_opengis_netkml2_2address', False)

    
    address = property(__address.value, __address.set, None, None)

    
    # Element {http://www.opengis.net/kml/2.2}AbstractFeatureSimpleExtensionGroup uses Python identifier AbstractFeatureSimpleExtensionGroup
    __AbstractFeatureSimpleExtensionGroup = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'AbstractFeatureSimpleExtensionGroup'), 'AbstractFeatureSimpleExtensionGroup', '__httpwww_opengis_netkml2_2_AbstractFeatureType_httpwww_opengis_netkml2_2AbstractFeatureSimpleExtensionGroup', True)

    
    AbstractFeatureSimpleExtensionGroup = property(__AbstractFeatureSimpleExtensionGroup.value, __AbstractFeatureSimpleExtensionGroup.set, None, None)

    
    # Element {http://www.opengis.net/kml/2.2}name uses Python identifier name
    __name = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'name'), 'name', '__httpwww_opengis_netkml2_2_AbstractFeatureType_httpwww_opengis_netkml2_2name', False)

    
    name = property(__name.value, __name.set, None, None)

    
    # Element {http://www.opengis.net/kml/2.2}phoneNumber uses Python identifier phoneNumber
    __phoneNumber = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'phoneNumber'), 'phoneNumber', '__httpwww_opengis_netkml2_2_AbstractFeatureType_httpwww_opengis_netkml2_2phoneNumber', False)

    
    phoneNumber = property(__phoneNumber.value, __phoneNumber.set, None, None)

    
    # Element {http://www.opengis.net/kml/2.2}Metadata uses Python identifier Metadata
    __Metadata = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'Metadata'), 'Metadata', '__httpwww_opengis_netkml2_2_AbstractFeatureType_httpwww_opengis_netkml2_2Metadata', False)

    
    Metadata = property(__Metadata.value, __Metadata.set, None, u'Metadata deprecated in 2.2')

    
    # Element {http://www.w3.org/2005/Atom}author uses Python identifier author
    __author = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/2005/Atom'), u'author'), 'author', '__httpwww_opengis_netkml2_2_AbstractFeatureType_httpwww_w3_org2005Atomauthor', False)

    
    author = property(__author.value, __author.set, None, None)

    
    # Element {http://www.opengis.net/kml/2.2}visibility uses Python identifier visibility
    __visibility = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'visibility'), 'visibility', '__httpwww_opengis_netkml2_2_AbstractFeatureType_httpwww_opengis_netkml2_2visibility', False)

    
    visibility = property(__visibility.value, __visibility.set, None, None)

    
    # Element {http://www.opengis.net/kml/2.2}open uses Python identifier open
    __open = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'open'), 'open', '__httpwww_opengis_netkml2_2_AbstractFeatureType_httpwww_opengis_netkml2_2open', False)

    
    open = property(__open.value, __open.set, None, None)

    
    # Element {urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}AddressDetails uses Python identifier AddressDetails
    __AddressDetails = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'urn:oasis:names:tc:ciq:xsdschema:xAL:2.0'), u'AddressDetails'), 'AddressDetails', '__httpwww_opengis_netkml2_2_AbstractFeatureType_urnoasisnamestcciqxsdschemaxAL2_0AddressDetails', False)

    
    AddressDetails = property(__AddressDetails.value, __AddressDetails.set, None, u'This container defines the details of the address. Can define multiple addresses including tracking address history')

    
    # Element {http://www.opengis.net/kml/2.2}AbstractViewGroup uses Python identifier AbstractViewGroup
    __AbstractViewGroup = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'AbstractViewGroup'), 'AbstractViewGroup', '__httpwww_opengis_netkml2_2_AbstractFeatureType_httpwww_opengis_netkml2_2AbstractViewGroup', False)

    
    AbstractViewGroup = property(__AbstractViewGroup.value, __AbstractViewGroup.set, None, None)

    
    # Element {http://www.opengis.net/kml/2.2}ExtendedData uses Python identifier ExtendedData
    __ExtendedData = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'ExtendedData'), 'ExtendedData', '__httpwww_opengis_netkml2_2_AbstractFeatureType_httpwww_opengis_netkml2_2ExtendedData', False)

    
    ExtendedData = property(__ExtendedData.value, __ExtendedData.set, None, None)

    
    # Element {http://www.opengis.net/kml/2.2}Snippet uses Python identifier Snippet
    __Snippet = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'Snippet'), 'Snippet', '__httpwww_opengis_netkml2_2_AbstractFeatureType_httpwww_opengis_netkml2_2Snippet', False)

    
    Snippet = property(__Snippet.value, __Snippet.set, None, None)

    
    # Element ObjectSimpleExtensionGroup ({http://www.opengis.net/kml/2.2}ObjectSimpleExtensionGroup) inherited from {http://www.opengis.net/kml/2.2}AbstractObjectType
    
    # Element {http://www.opengis.net/kml/2.2}styleUrl uses Python identifier styleUrl
    __styleUrl = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'styleUrl'), 'styleUrl', '__httpwww_opengis_netkml2_2_AbstractFeatureType_httpwww_opengis_netkml2_2styleUrl', False)

    
    styleUrl = property(__styleUrl.value, __styleUrl.set, None, None)

    
    # Attribute targetId inherited from {http://www.opengis.net/kml/2.2}AbstractObjectType
    
    # Attribute id inherited from {http://www.opengis.net/kml/2.2}AbstractObjectType

    _ElementMap = AbstractObjectType._ElementMap.copy()
    _ElementMap.update({
        __link.name() : __link,
        __snippet.name() : __snippet,
        __AbstractStyleSelectorGroup.name() : __AbstractStyleSelectorGroup,
        __AbstractFeatureObjectExtensionGroup.name() : __AbstractFeatureObjectExtensionGroup,
        __description.name() : __description,
        __AbstractTimePrimitiveGroup.name() : __AbstractTimePrimitiveGroup,
        __Region.name() : __Region,
        __address.name() : __address,
        __AbstractFeatureSimpleExtensionGroup.name() : __AbstractFeatureSimpleExtensionGroup,
        __name.name() : __name,
        __phoneNumber.name() : __phoneNumber,
        __Metadata.name() : __Metadata,
        __author.name() : __author,
        __visibility.name() : __visibility,
        __open.name() : __open,
        __AddressDetails.name() : __AddressDetails,
        __AbstractViewGroup.name() : __AbstractViewGroup,
        __ExtendedData.name() : __ExtendedData,
        __Snippet.name() : __Snippet,
        __styleUrl.name() : __styleUrl
    })
    _AttributeMap = AbstractObjectType._AttributeMap.copy()
    _AttributeMap.update({
        
    })
Namespace.addCategoryObject('typeBinding', u'AbstractFeatureType', AbstractFeatureType)


# Complex type AbstractTimePrimitiveType with content type ELEMENT_ONLY
class AbstractTimePrimitiveType (AbstractObjectType):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = True
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'AbstractTimePrimitiveType')
    # Base type is AbstractObjectType
    
    # Element {http://www.opengis.net/kml/2.2}AbstractTimePrimitiveObjectExtensionGroup uses Python identifier AbstractTimePrimitiveObjectExtensionGroup
    __AbstractTimePrimitiveObjectExtensionGroup = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'AbstractTimePrimitiveObjectExtensionGroup'), 'AbstractTimePrimitiveObjectExtensionGroup', '__httpwww_opengis_netkml2_2_AbstractTimePrimitiveType_httpwww_opengis_netkml2_2AbstractTimePrimitiveObjectExtensionGroup', True)

    
    AbstractTimePrimitiveObjectExtensionGroup = property(__AbstractTimePrimitiveObjectExtensionGroup.value, __AbstractTimePrimitiveObjectExtensionGroup.set, None, None)

    
    # Element {http://www.opengis.net/kml/2.2}AbstractTimePrimitiveSimpleExtensionGroup uses Python identifier AbstractTimePrimitiveSimpleExtensionGroup
    __AbstractTimePrimitiveSimpleExtensionGroup = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'AbstractTimePrimitiveSimpleExtensionGroup'), 'AbstractTimePrimitiveSimpleExtensionGroup', '__httpwww_opengis_netkml2_2_AbstractTimePrimitiveType_httpwww_opengis_netkml2_2AbstractTimePrimitiveSimpleExtensionGroup', True)

    
    AbstractTimePrimitiveSimpleExtensionGroup = property(__AbstractTimePrimitiveSimpleExtensionGroup.value, __AbstractTimePrimitiveSimpleExtensionGroup.set, None, None)

    
    # Element ObjectSimpleExtensionGroup ({http://www.opengis.net/kml/2.2}ObjectSimpleExtensionGroup) inherited from {http://www.opengis.net/kml/2.2}AbstractObjectType
    
    # Attribute targetId inherited from {http://www.opengis.net/kml/2.2}AbstractObjectType
    
    # Attribute id inherited from {http://www.opengis.net/kml/2.2}AbstractObjectType

    _ElementMap = AbstractObjectType._ElementMap.copy()
    _ElementMap.update({
        __AbstractTimePrimitiveObjectExtensionGroup.name() : __AbstractTimePrimitiveObjectExtensionGroup,
        __AbstractTimePrimitiveSimpleExtensionGroup.name() : __AbstractTimePrimitiveSimpleExtensionGroup
    })
    _AttributeMap = AbstractObjectType._AttributeMap.copy()
    _AttributeMap.update({
        
    })
Namespace.addCategoryObject('typeBinding', u'AbstractTimePrimitiveType', AbstractTimePrimitiveType)


# Complex type LabelStyleType with content type ELEMENT_ONLY
class LabelStyleType (AbstractColorStyleType):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'LabelStyleType')
    # Base type is AbstractColorStyleType
    
    # Element AbstractColorStyleSimpleExtensionGroup ({http://www.opengis.net/kml/2.2}AbstractColorStyleSimpleExtensionGroup) inherited from {http://www.opengis.net/kml/2.2}AbstractColorStyleType
    
    # Element AbstractColorStyleObjectExtensionGroup ({http://www.opengis.net/kml/2.2}AbstractColorStyleObjectExtensionGroup) inherited from {http://www.opengis.net/kml/2.2}AbstractColorStyleType
    
    # Element ObjectSimpleExtensionGroup ({http://www.opengis.net/kml/2.2}ObjectSimpleExtensionGroup) inherited from {http://www.opengis.net/kml/2.2}AbstractObjectType
    
    # Element color ({http://www.opengis.net/kml/2.2}color) inherited from {http://www.opengis.net/kml/2.2}AbstractColorStyleType
    
    # Element AbstractSubStyleSimpleExtensionGroup ({http://www.opengis.net/kml/2.2}AbstractSubStyleSimpleExtensionGroup) inherited from {http://www.opengis.net/kml/2.2}AbstractSubStyleType
    
    # Element {http://www.opengis.net/kml/2.2}LabelStyleSimpleExtensionGroup uses Python identifier LabelStyleSimpleExtensionGroup
    __LabelStyleSimpleExtensionGroup = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'LabelStyleSimpleExtensionGroup'), 'LabelStyleSimpleExtensionGroup', '__httpwww_opengis_netkml2_2_LabelStyleType_httpwww_opengis_netkml2_2LabelStyleSimpleExtensionGroup', True)

    
    LabelStyleSimpleExtensionGroup = property(__LabelStyleSimpleExtensionGroup.value, __LabelStyleSimpleExtensionGroup.set, None, None)

    
    # Element AbstractSubStyleObjectExtensionGroup ({http://www.opengis.net/kml/2.2}AbstractSubStyleObjectExtensionGroup) inherited from {http://www.opengis.net/kml/2.2}AbstractSubStyleType
    
    # Element colorMode ({http://www.opengis.net/kml/2.2}colorMode) inherited from {http://www.opengis.net/kml/2.2}AbstractColorStyleType
    
    # Element {http://www.opengis.net/kml/2.2}LabelStyleObjectExtensionGroup uses Python identifier LabelStyleObjectExtensionGroup
    __LabelStyleObjectExtensionGroup = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'LabelStyleObjectExtensionGroup'), 'LabelStyleObjectExtensionGroup', '__httpwww_opengis_netkml2_2_LabelStyleType_httpwww_opengis_netkml2_2LabelStyleObjectExtensionGroup', True)

    
    LabelStyleObjectExtensionGroup = property(__LabelStyleObjectExtensionGroup.value, __LabelStyleObjectExtensionGroup.set, None, None)

    
    # Element {http://www.opengis.net/kml/2.2}scale uses Python identifier scale
    __scale = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'scale'), 'scale', '__httpwww_opengis_netkml2_2_LabelStyleType_httpwww_opengis_netkml2_2scale', False)

    
    scale = property(__scale.value, __scale.set, None, None)

    
    # Attribute targetId inherited from {http://www.opengis.net/kml/2.2}AbstractObjectType
    
    # Attribute id inherited from {http://www.opengis.net/kml/2.2}AbstractObjectType

    _ElementMap = AbstractColorStyleType._ElementMap.copy()
    _ElementMap.update({
        __LabelStyleSimpleExtensionGroup.name() : __LabelStyleSimpleExtensionGroup,
        __LabelStyleObjectExtensionGroup.name() : __LabelStyleObjectExtensionGroup,
        __scale.name() : __scale
    })
    _AttributeMap = AbstractColorStyleType._AttributeMap.copy()
    _AttributeMap.update({
        
    })
Namespace.addCategoryObject('typeBinding', u'LabelStyleType', LabelStyleType)


# Complex type LineStyleType with content type ELEMENT_ONLY
class LineStyleType (AbstractColorStyleType):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'LineStyleType')
    # Base type is AbstractColorStyleType
    
    # Element {http://www.opengis.net/kml/2.2}width uses Python identifier width
    __width = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'width'), 'width', '__httpwww_opengis_netkml2_2_LineStyleType_httpwww_opengis_netkml2_2width', False)

    
    width = property(__width.value, __width.set, None, None)

    
    # Element AbstractColorStyleSimpleExtensionGroup ({http://www.opengis.net/kml/2.2}AbstractColorStyleSimpleExtensionGroup) inherited from {http://www.opengis.net/kml/2.2}AbstractColorStyleType
    
    # Element ObjectSimpleExtensionGroup ({http://www.opengis.net/kml/2.2}ObjectSimpleExtensionGroup) inherited from {http://www.opengis.net/kml/2.2}AbstractObjectType
    
    # Element color ({http://www.opengis.net/kml/2.2}color) inherited from {http://www.opengis.net/kml/2.2}AbstractColorStyleType
    
    # Element AbstractSubStyleSimpleExtensionGroup ({http://www.opengis.net/kml/2.2}AbstractSubStyleSimpleExtensionGroup) inherited from {http://www.opengis.net/kml/2.2}AbstractSubStyleType
    
    # Element AbstractColorStyleObjectExtensionGroup ({http://www.opengis.net/kml/2.2}AbstractColorStyleObjectExtensionGroup) inherited from {http://www.opengis.net/kml/2.2}AbstractColorStyleType
    
    # Element {http://www.opengis.net/kml/2.2}LineStyleSimpleExtensionGroup uses Python identifier LineStyleSimpleExtensionGroup
    __LineStyleSimpleExtensionGroup = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'LineStyleSimpleExtensionGroup'), 'LineStyleSimpleExtensionGroup', '__httpwww_opengis_netkml2_2_LineStyleType_httpwww_opengis_netkml2_2LineStyleSimpleExtensionGroup', True)

    
    LineStyleSimpleExtensionGroup = property(__LineStyleSimpleExtensionGroup.value, __LineStyleSimpleExtensionGroup.set, None, None)

    
    # Element AbstractSubStyleObjectExtensionGroup ({http://www.opengis.net/kml/2.2}AbstractSubStyleObjectExtensionGroup) inherited from {http://www.opengis.net/kml/2.2}AbstractSubStyleType
    
    # Element colorMode ({http://www.opengis.net/kml/2.2}colorMode) inherited from {http://www.opengis.net/kml/2.2}AbstractColorStyleType
    
    # Element {http://www.opengis.net/kml/2.2}LineStyleObjectExtensionGroup uses Python identifier LineStyleObjectExtensionGroup
    __LineStyleObjectExtensionGroup = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'LineStyleObjectExtensionGroup'), 'LineStyleObjectExtensionGroup', '__httpwww_opengis_netkml2_2_LineStyleType_httpwww_opengis_netkml2_2LineStyleObjectExtensionGroup', True)

    
    LineStyleObjectExtensionGroup = property(__LineStyleObjectExtensionGroup.value, __LineStyleObjectExtensionGroup.set, None, None)

    
    # Attribute targetId inherited from {http://www.opengis.net/kml/2.2}AbstractObjectType
    
    # Attribute id inherited from {http://www.opengis.net/kml/2.2}AbstractObjectType

    _ElementMap = AbstractColorStyleType._ElementMap.copy()
    _ElementMap.update({
        __width.name() : __width,
        __LineStyleSimpleExtensionGroup.name() : __LineStyleSimpleExtensionGroup,
        __LineStyleObjectExtensionGroup.name() : __LineStyleObjectExtensionGroup
    })
    _AttributeMap = AbstractColorStyleType._AttributeMap.copy()
    _AttributeMap.update({
        
    })
Namespace.addCategoryObject('typeBinding', u'LineStyleType', LineStyleType)


# Complex type BoundaryType with content type ELEMENT_ONLY
class BoundaryType (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'BoundaryType')
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {http://www.opengis.net/kml/2.2}BoundarySimpleExtensionGroup uses Python identifier BoundarySimpleExtensionGroup
    __BoundarySimpleExtensionGroup = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'BoundarySimpleExtensionGroup'), 'BoundarySimpleExtensionGroup', '__httpwww_opengis_netkml2_2_BoundaryType_httpwww_opengis_netkml2_2BoundarySimpleExtensionGroup', True)

    
    BoundarySimpleExtensionGroup = property(__BoundarySimpleExtensionGroup.value, __BoundarySimpleExtensionGroup.set, None, None)

    
    # Element {http://www.opengis.net/kml/2.2}BoundaryObjectExtensionGroup uses Python identifier BoundaryObjectExtensionGroup
    __BoundaryObjectExtensionGroup = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'BoundaryObjectExtensionGroup'), 'BoundaryObjectExtensionGroup', '__httpwww_opengis_netkml2_2_BoundaryType_httpwww_opengis_netkml2_2BoundaryObjectExtensionGroup', True)

    
    BoundaryObjectExtensionGroup = property(__BoundaryObjectExtensionGroup.value, __BoundaryObjectExtensionGroup.set, None, None)

    
    # Element {http://www.opengis.net/kml/2.2}LinearRing uses Python identifier LinearRing
    __LinearRing = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'LinearRing'), 'LinearRing', '__httpwww_opengis_netkml2_2_BoundaryType_httpwww_opengis_netkml2_2LinearRing', False)

    
    LinearRing = property(__LinearRing.value, __LinearRing.set, None, None)


    _ElementMap = {
        __BoundarySimpleExtensionGroup.name() : __BoundarySimpleExtensionGroup,
        __BoundaryObjectExtensionGroup.name() : __BoundaryObjectExtensionGroup,
        __LinearRing.name() : __LinearRing
    }
    _AttributeMap = {
        
    }
Namespace.addCategoryObject('typeBinding', u'BoundaryType', BoundaryType)


# Complex type PolyStyleType with content type ELEMENT_ONLY
class PolyStyleType (AbstractColorStyleType):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'PolyStyleType')
    # Base type is AbstractColorStyleType
    
    # Element {http://www.opengis.net/kml/2.2}fill uses Python identifier fill
    __fill = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'fill'), 'fill', '__httpwww_opengis_netkml2_2_PolyStyleType_httpwww_opengis_netkml2_2fill', False)

    
    fill = property(__fill.value, __fill.set, None, None)

    
    # Element {http://www.opengis.net/kml/2.2}PolyStyleObjectExtensionGroup uses Python identifier PolyStyleObjectExtensionGroup
    __PolyStyleObjectExtensionGroup = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'PolyStyleObjectExtensionGroup'), 'PolyStyleObjectExtensionGroup', '__httpwww_opengis_netkml2_2_PolyStyleType_httpwww_opengis_netkml2_2PolyStyleObjectExtensionGroup', True)

    
    PolyStyleObjectExtensionGroup = property(__PolyStyleObjectExtensionGroup.value, __PolyStyleObjectExtensionGroup.set, None, None)

    
    # Element color ({http://www.opengis.net/kml/2.2}color) inherited from {http://www.opengis.net/kml/2.2}AbstractColorStyleType
    
    # Element ObjectSimpleExtensionGroup ({http://www.opengis.net/kml/2.2}ObjectSimpleExtensionGroup) inherited from {http://www.opengis.net/kml/2.2}AbstractObjectType
    
    # Element AbstractSubStyleObjectExtensionGroup ({http://www.opengis.net/kml/2.2}AbstractSubStyleObjectExtensionGroup) inherited from {http://www.opengis.net/kml/2.2}AbstractSubStyleType
    
    # Element {http://www.opengis.net/kml/2.2}outline uses Python identifier outline
    __outline = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'outline'), 'outline', '__httpwww_opengis_netkml2_2_PolyStyleType_httpwww_opengis_netkml2_2outline', False)

    
    outline = property(__outline.value, __outline.set, None, None)

    
    # Element AbstractSubStyleSimpleExtensionGroup ({http://www.opengis.net/kml/2.2}AbstractSubStyleSimpleExtensionGroup) inherited from {http://www.opengis.net/kml/2.2}AbstractSubStyleType
    
    # Element AbstractColorStyleObjectExtensionGroup ({http://www.opengis.net/kml/2.2}AbstractColorStyleObjectExtensionGroup) inherited from {http://www.opengis.net/kml/2.2}AbstractColorStyleType
    
    # Element colorMode ({http://www.opengis.net/kml/2.2}colorMode) inherited from {http://www.opengis.net/kml/2.2}AbstractColorStyleType
    
    # Element {http://www.opengis.net/kml/2.2}PolyStyleSimpleExtensionGroup uses Python identifier PolyStyleSimpleExtensionGroup
    __PolyStyleSimpleExtensionGroup = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'PolyStyleSimpleExtensionGroup'), 'PolyStyleSimpleExtensionGroup', '__httpwww_opengis_netkml2_2_PolyStyleType_httpwww_opengis_netkml2_2PolyStyleSimpleExtensionGroup', True)

    
    PolyStyleSimpleExtensionGroup = property(__PolyStyleSimpleExtensionGroup.value, __PolyStyleSimpleExtensionGroup.set, None, None)

    
    # Element AbstractColorStyleSimpleExtensionGroup ({http://www.opengis.net/kml/2.2}AbstractColorStyleSimpleExtensionGroup) inherited from {http://www.opengis.net/kml/2.2}AbstractColorStyleType
    
    # Attribute targetId inherited from {http://www.opengis.net/kml/2.2}AbstractObjectType
    
    # Attribute id inherited from {http://www.opengis.net/kml/2.2}AbstractObjectType

    _ElementMap = AbstractColorStyleType._ElementMap.copy()
    _ElementMap.update({
        __fill.name() : __fill,
        __PolyStyleObjectExtensionGroup.name() : __PolyStyleObjectExtensionGroup,
        __outline.name() : __outline,
        __PolyStyleSimpleExtensionGroup.name() : __PolyStyleSimpleExtensionGroup
    })
    _AttributeMap = AbstractColorStyleType._AttributeMap.copy()
    _AttributeMap.update({
        
    })
Namespace.addCategoryObject('typeBinding', u'PolyStyleType', PolyStyleType)


# Complex type LinearRingType with content type ELEMENT_ONLY
class LinearRingType (AbstractGeometryType):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'LinearRingType')
    # Base type is AbstractGeometryType
    
    # Element {http://www.opengis.net/kml/2.2}LinearRingSimpleExtensionGroup uses Python identifier LinearRingSimpleExtensionGroup
    __LinearRingSimpleExtensionGroup = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'LinearRingSimpleExtensionGroup'), 'LinearRingSimpleExtensionGroup', '__httpwww_opengis_netkml2_2_LinearRingType_httpwww_opengis_netkml2_2LinearRingSimpleExtensionGroup', True)

    
    LinearRingSimpleExtensionGroup = property(__LinearRingSimpleExtensionGroup.value, __LinearRingSimpleExtensionGroup.set, None, None)

    
    # Element AbstractGeometryObjectExtensionGroup ({http://www.opengis.net/kml/2.2}AbstractGeometryObjectExtensionGroup) inherited from {http://www.opengis.net/kml/2.2}AbstractGeometryType
    
    # Element {http://www.opengis.net/kml/2.2}altitudeModeGroup uses Python identifier altitudeModeGroup
    __altitudeModeGroup = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'altitudeModeGroup'), 'altitudeModeGroup', '__httpwww_opengis_netkml2_2_LinearRingType_httpwww_opengis_netkml2_2altitudeModeGroup', False)

    
    altitudeModeGroup = property(__altitudeModeGroup.value, __altitudeModeGroup.set, None, None)

    
    # Element {http://www.opengis.net/kml/2.2}LinearRingObjectExtensionGroup uses Python identifier LinearRingObjectExtensionGroup
    __LinearRingObjectExtensionGroup = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'LinearRingObjectExtensionGroup'), 'LinearRingObjectExtensionGroup', '__httpwww_opengis_netkml2_2_LinearRingType_httpwww_opengis_netkml2_2LinearRingObjectExtensionGroup', True)

    
    LinearRingObjectExtensionGroup = property(__LinearRingObjectExtensionGroup.value, __LinearRingObjectExtensionGroup.set, None, None)

    
    # Element {http://www.opengis.net/kml/2.2}extrude uses Python identifier extrude
    __extrude = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'extrude'), 'extrude', '__httpwww_opengis_netkml2_2_LinearRingType_httpwww_opengis_netkml2_2extrude', False)

    
    extrude = property(__extrude.value, __extrude.set, None, None)

    
    # Element {http://www.opengis.net/kml/2.2}coordinates uses Python identifier coordinates
    __coordinates = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'coordinates'), 'coordinates', '__httpwww_opengis_netkml2_2_LinearRingType_httpwww_opengis_netkml2_2coordinates', False)

    
    coordinates = property(__coordinates.value, __coordinates.set, None, None)

    
    # Element AbstractGeometrySimpleExtensionGroup ({http://www.opengis.net/kml/2.2}AbstractGeometrySimpleExtensionGroup) inherited from {http://www.opengis.net/kml/2.2}AbstractGeometryType
    
    # Element {http://www.opengis.net/kml/2.2}tessellate uses Python identifier tessellate
    __tessellate = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'tessellate'), 'tessellate', '__httpwww_opengis_netkml2_2_LinearRingType_httpwww_opengis_netkml2_2tessellate', False)

    
    tessellate = property(__tessellate.value, __tessellate.set, None, None)

    
    # Element ObjectSimpleExtensionGroup ({http://www.opengis.net/kml/2.2}ObjectSimpleExtensionGroup) inherited from {http://www.opengis.net/kml/2.2}AbstractObjectType
    
    # Attribute targetId inherited from {http://www.opengis.net/kml/2.2}AbstractObjectType
    
    # Attribute id inherited from {http://www.opengis.net/kml/2.2}AbstractObjectType

    _ElementMap = AbstractGeometryType._ElementMap.copy()
    _ElementMap.update({
        __LinearRingSimpleExtensionGroup.name() : __LinearRingSimpleExtensionGroup,
        __altitudeModeGroup.name() : __altitudeModeGroup,
        __LinearRingObjectExtensionGroup.name() : __LinearRingObjectExtensionGroup,
        __extrude.name() : __extrude,
        __coordinates.name() : __coordinates,
        __tessellate.name() : __tessellate
    })
    _AttributeMap = AbstractGeometryType._AttributeMap.copy()
    _AttributeMap.update({
        
    })
Namespace.addCategoryObject('typeBinding', u'LinearRingType', LinearRingType)


# Complex type SnippetType with content type SIMPLE
class SnippetType (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = pyxb.binding.datatypes.string
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_SIMPLE
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'SnippetType')
    # Base type is pyxb.binding.datatypes.string
    
    # Attribute maxLines uses Python identifier maxLines
    __maxLines = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'maxLines'), 'maxLines', '__httpwww_opengis_netkml2_2_SnippetType_maxLines', pyxb.binding.datatypes.int, unicode_default=u'2')
    
    maxLines = property(__maxLines.value, __maxLines.set, None, None)


    _ElementMap = {
        
    }
    _AttributeMap = {
        __maxLines.name() : __maxLines
    }
Namespace.addCategoryObject('typeBinding', u'SnippetType', SnippetType)


# Complex type AbstractOverlayType with content type ELEMENT_ONLY
class AbstractOverlayType (AbstractFeatureType):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = True
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'AbstractOverlayType')
    # Base type is AbstractFeatureType
    
    # Element link ({http://www.w3.org/2005/Atom}link) inherited from {http://www.opengis.net/kml/2.2}AbstractFeatureType
    
    # Element AbstractStyleSelectorGroup ({http://www.opengis.net/kml/2.2}AbstractStyleSelectorGroup) inherited from {http://www.opengis.net/kml/2.2}AbstractFeatureType
    
    # Element address ({http://www.opengis.net/kml/2.2}address) inherited from {http://www.opengis.net/kml/2.2}AbstractFeatureType
    
    # Element Region ({http://www.opengis.net/kml/2.2}Region) inherited from {http://www.opengis.net/kml/2.2}AbstractFeatureType
    
    # Element AddressDetails ({urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}AddressDetails) inherited from {http://www.opengis.net/kml/2.2}AbstractFeatureType
    
    # Element phoneNumber ({http://www.opengis.net/kml/2.2}phoneNumber) inherited from {http://www.opengis.net/kml/2.2}AbstractFeatureType
    
    # Element Metadata ({http://www.opengis.net/kml/2.2}Metadata) inherited from {http://www.opengis.net/kml/2.2}AbstractFeatureType
    
    # Element AbstractViewGroup ({http://www.opengis.net/kml/2.2}AbstractViewGroup) inherited from {http://www.opengis.net/kml/2.2}AbstractFeatureType
    
    # Element ExtendedData ({http://www.opengis.net/kml/2.2}ExtendedData) inherited from {http://www.opengis.net/kml/2.2}AbstractFeatureType
    
    # Element AbstractFeatureObjectExtensionGroup ({http://www.opengis.net/kml/2.2}AbstractFeatureObjectExtensionGroup) inherited from {http://www.opengis.net/kml/2.2}AbstractFeatureType
    
    # Element AbstractFeatureSimpleExtensionGroup ({http://www.opengis.net/kml/2.2}AbstractFeatureSimpleExtensionGroup) inherited from {http://www.opengis.net/kml/2.2}AbstractFeatureType
    
    # Element author ({http://www.w3.org/2005/Atom}author) inherited from {http://www.opengis.net/kml/2.2}AbstractFeatureType
    
    # Element {http://www.opengis.net/kml/2.2}color uses Python identifier color
    __color = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'color'), 'color', '__httpwww_opengis_netkml2_2_AbstractOverlayType_httpwww_opengis_netkml2_2color', False)

    
    color = property(__color.value, __color.set, None, None)

    
    # Element name ({http://www.opengis.net/kml/2.2}name) inherited from {http://www.opengis.net/kml/2.2}AbstractFeatureType
    
    # Element {http://www.opengis.net/kml/2.2}drawOrder uses Python identifier drawOrder
    __drawOrder = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'drawOrder'), 'drawOrder', '__httpwww_opengis_netkml2_2_AbstractOverlayType_httpwww_opengis_netkml2_2drawOrder', False)

    
    drawOrder = property(__drawOrder.value, __drawOrder.set, None, None)

    
    # Element visibility ({http://www.opengis.net/kml/2.2}visibility) inherited from {http://www.opengis.net/kml/2.2}AbstractFeatureType
    
    # Element ObjectSimpleExtensionGroup ({http://www.opengis.net/kml/2.2}ObjectSimpleExtensionGroup) inherited from {http://www.opengis.net/kml/2.2}AbstractObjectType
    
    # Element {http://www.opengis.net/kml/2.2}Icon uses Python identifier Icon
    __Icon = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'Icon'), 'Icon', '__httpwww_opengis_netkml2_2_AbstractOverlayType_httpwww_opengis_netkml2_2Icon', False)

    
    Icon = property(__Icon.value, __Icon.set, None, None)

    
    # Element snippet ({http://www.opengis.net/kml/2.2}snippet) inherited from {http://www.opengis.net/kml/2.2}AbstractFeatureType
    
    # Element description ({http://www.opengis.net/kml/2.2}description) inherited from {http://www.opengis.net/kml/2.2}AbstractFeatureType
    
    # Element AbstractTimePrimitiveGroup ({http://www.opengis.net/kml/2.2}AbstractTimePrimitiveGroup) inherited from {http://www.opengis.net/kml/2.2}AbstractFeatureType
    
    # Element {http://www.opengis.net/kml/2.2}AbstractOverlaySimpleExtensionGroup uses Python identifier AbstractOverlaySimpleExtensionGroup
    __AbstractOverlaySimpleExtensionGroup = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'AbstractOverlaySimpleExtensionGroup'), 'AbstractOverlaySimpleExtensionGroup', '__httpwww_opengis_netkml2_2_AbstractOverlayType_httpwww_opengis_netkml2_2AbstractOverlaySimpleExtensionGroup', True)

    
    AbstractOverlaySimpleExtensionGroup = property(__AbstractOverlaySimpleExtensionGroup.value, __AbstractOverlaySimpleExtensionGroup.set, None, None)

    
    # Element Snippet ({http://www.opengis.net/kml/2.2}Snippet) inherited from {http://www.opengis.net/kml/2.2}AbstractFeatureType
    
    # Element styleUrl ({http://www.opengis.net/kml/2.2}styleUrl) inherited from {http://www.opengis.net/kml/2.2}AbstractFeatureType
    
    # Element open ({http://www.opengis.net/kml/2.2}open) inherited from {http://www.opengis.net/kml/2.2}AbstractFeatureType
    
    # Element {http://www.opengis.net/kml/2.2}AbstractOverlayObjectExtensionGroup uses Python identifier AbstractOverlayObjectExtensionGroup
    __AbstractOverlayObjectExtensionGroup = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'AbstractOverlayObjectExtensionGroup'), 'AbstractOverlayObjectExtensionGroup', '__httpwww_opengis_netkml2_2_AbstractOverlayType_httpwww_opengis_netkml2_2AbstractOverlayObjectExtensionGroup', True)

    
    AbstractOverlayObjectExtensionGroup = property(__AbstractOverlayObjectExtensionGroup.value, __AbstractOverlayObjectExtensionGroup.set, None, None)

    
    # Attribute targetId inherited from {http://www.opengis.net/kml/2.2}AbstractObjectType
    
    # Attribute id inherited from {http://www.opengis.net/kml/2.2}AbstractObjectType

    _ElementMap = AbstractFeatureType._ElementMap.copy()
    _ElementMap.update({
        __color.name() : __color,
        __drawOrder.name() : __drawOrder,
        __Icon.name() : __Icon,
        __AbstractOverlaySimpleExtensionGroup.name() : __AbstractOverlaySimpleExtensionGroup,
        __AbstractOverlayObjectExtensionGroup.name() : __AbstractOverlayObjectExtensionGroup
    })
    _AttributeMap = AbstractFeatureType._AttributeMap.copy()
    _AttributeMap.update({
        
    })
Namespace.addCategoryObject('typeBinding', u'AbstractOverlayType', AbstractOverlayType)


# Complex type LinkType with content type ELEMENT_ONLY
class LinkType (BasicLinkType):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'LinkType')
    # Base type is BasicLinkType
    
    # Element {http://www.opengis.net/kml/2.2}viewRefreshTime uses Python identifier viewRefreshTime
    __viewRefreshTime = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'viewRefreshTime'), 'viewRefreshTime', '__httpwww_opengis_netkml2_2_LinkType_httpwww_opengis_netkml2_2viewRefreshTime', False)

    
    viewRefreshTime = property(__viewRefreshTime.value, __viewRefreshTime.set, None, None)

    
    # Element {http://www.opengis.net/kml/2.2}httpQuery uses Python identifier httpQuery
    __httpQuery = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'httpQuery'), 'httpQuery', '__httpwww_opengis_netkml2_2_LinkType_httpwww_opengis_netkml2_2httpQuery', False)

    
    httpQuery = property(__httpQuery.value, __httpQuery.set, None, None)

    
    # Element BasicLinkSimpleExtensionGroup ({http://www.opengis.net/kml/2.2}BasicLinkSimpleExtensionGroup) inherited from {http://www.opengis.net/kml/2.2}BasicLinkType
    
    # Element BasicLinkObjectExtensionGroup ({http://www.opengis.net/kml/2.2}BasicLinkObjectExtensionGroup) inherited from {http://www.opengis.net/kml/2.2}BasicLinkType
    
    # Element {http://www.opengis.net/kml/2.2}refreshInterval uses Python identifier refreshInterval
    __refreshInterval = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'refreshInterval'), 'refreshInterval', '__httpwww_opengis_netkml2_2_LinkType_httpwww_opengis_netkml2_2refreshInterval', False)

    
    refreshInterval = property(__refreshInterval.value, __refreshInterval.set, None, None)

    
    # Element {http://www.opengis.net/kml/2.2}viewBoundScale uses Python identifier viewBoundScale
    __viewBoundScale = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'viewBoundScale'), 'viewBoundScale', '__httpwww_opengis_netkml2_2_LinkType_httpwww_opengis_netkml2_2viewBoundScale', False)

    
    viewBoundScale = property(__viewBoundScale.value, __viewBoundScale.set, None, None)

    
    # Element {http://www.opengis.net/kml/2.2}refreshMode uses Python identifier refreshMode
    __refreshMode = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'refreshMode'), 'refreshMode', '__httpwww_opengis_netkml2_2_LinkType_httpwww_opengis_netkml2_2refreshMode', False)

    
    refreshMode = property(__refreshMode.value, __refreshMode.set, None, None)

    
    # Element {http://www.opengis.net/kml/2.2}LinkSimpleExtensionGroup uses Python identifier LinkSimpleExtensionGroup
    __LinkSimpleExtensionGroup = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'LinkSimpleExtensionGroup'), 'LinkSimpleExtensionGroup', '__httpwww_opengis_netkml2_2_LinkType_httpwww_opengis_netkml2_2LinkSimpleExtensionGroup', True)

    
    LinkSimpleExtensionGroup = property(__LinkSimpleExtensionGroup.value, __LinkSimpleExtensionGroup.set, None, None)

    
    # Element {http://www.opengis.net/kml/2.2}viewRefreshMode uses Python identifier viewRefreshMode
    __viewRefreshMode = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'viewRefreshMode'), 'viewRefreshMode', '__httpwww_opengis_netkml2_2_LinkType_httpwww_opengis_netkml2_2viewRefreshMode', False)

    
    viewRefreshMode = property(__viewRefreshMode.value, __viewRefreshMode.set, None, None)

    
    # Element ObjectSimpleExtensionGroup ({http://www.opengis.net/kml/2.2}ObjectSimpleExtensionGroup) inherited from {http://www.opengis.net/kml/2.2}AbstractObjectType
    
    # Element {http://www.opengis.net/kml/2.2}viewFormat uses Python identifier viewFormat
    __viewFormat = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'viewFormat'), 'viewFormat', '__httpwww_opengis_netkml2_2_LinkType_httpwww_opengis_netkml2_2viewFormat', False)

    
    viewFormat = property(__viewFormat.value, __viewFormat.set, None, None)

    
    # Element {http://www.opengis.net/kml/2.2}LinkObjectExtensionGroup uses Python identifier LinkObjectExtensionGroup
    __LinkObjectExtensionGroup = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'LinkObjectExtensionGroup'), 'LinkObjectExtensionGroup', '__httpwww_opengis_netkml2_2_LinkType_httpwww_opengis_netkml2_2LinkObjectExtensionGroup', True)

    
    LinkObjectExtensionGroup = property(__LinkObjectExtensionGroup.value, __LinkObjectExtensionGroup.set, None, None)

    
    # Element href ({http://www.opengis.net/kml/2.2}href) inherited from {http://www.opengis.net/kml/2.2}BasicLinkType
    
    # Attribute targetId inherited from {http://www.opengis.net/kml/2.2}AbstractObjectType
    
    # Attribute id inherited from {http://www.opengis.net/kml/2.2}AbstractObjectType

    _ElementMap = BasicLinkType._ElementMap.copy()
    _ElementMap.update({
        __viewRefreshTime.name() : __viewRefreshTime,
        __httpQuery.name() : __httpQuery,
        __refreshInterval.name() : __refreshInterval,
        __viewBoundScale.name() : __viewBoundScale,
        __refreshMode.name() : __refreshMode,
        __LinkSimpleExtensionGroup.name() : __LinkSimpleExtensionGroup,
        __viewRefreshMode.name() : __viewRefreshMode,
        __viewFormat.name() : __viewFormat,
        __LinkObjectExtensionGroup.name() : __LinkObjectExtensionGroup
    })
    _AttributeMap = BasicLinkType._AttributeMap.copy()
    _AttributeMap.update({
        
    })
Namespace.addCategoryObject('typeBinding', u'LinkType', LinkType)


# Complex type UpdateType with content type ELEMENT_ONLY
class UpdateType (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'UpdateType')
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {http://www.opengis.net/kml/2.2}Create uses Python identifier Create
    __Create = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'Create'), 'Create', '__httpwww_opengis_netkml2_2_UpdateType_httpwww_opengis_netkml2_2Create', True)

    
    Create = property(__Create.value, __Create.set, None, None)

    
    # Element {http://www.opengis.net/kml/2.2}Delete uses Python identifier Delete
    __Delete = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'Delete'), 'Delete', '__httpwww_opengis_netkml2_2_UpdateType_httpwww_opengis_netkml2_2Delete', True)

    
    Delete = property(__Delete.value, __Delete.set, None, None)

    
    # Element {http://www.opengis.net/kml/2.2}UpdateOpExtensionGroup uses Python identifier UpdateOpExtensionGroup
    __UpdateOpExtensionGroup = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'UpdateOpExtensionGroup'), 'UpdateOpExtensionGroup', '__httpwww_opengis_netkml2_2_UpdateType_httpwww_opengis_netkml2_2UpdateOpExtensionGroup', True)

    
    UpdateOpExtensionGroup = property(__UpdateOpExtensionGroup.value, __UpdateOpExtensionGroup.set, None, None)

    
    # Element {http://www.opengis.net/kml/2.2}targetHref uses Python identifier targetHref
    __targetHref = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'targetHref'), 'targetHref', '__httpwww_opengis_netkml2_2_UpdateType_httpwww_opengis_netkml2_2targetHref', False)

    
    targetHref = property(__targetHref.value, __targetHref.set, None, None)

    
    # Element {http://www.opengis.net/kml/2.2}UpdateExtensionGroup uses Python identifier UpdateExtensionGroup
    __UpdateExtensionGroup = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'UpdateExtensionGroup'), 'UpdateExtensionGroup', '__httpwww_opengis_netkml2_2_UpdateType_httpwww_opengis_netkml2_2UpdateExtensionGroup', True)

    
    UpdateExtensionGroup = property(__UpdateExtensionGroup.value, __UpdateExtensionGroup.set, None, None)

    
    # Element {http://www.opengis.net/kml/2.2}Change uses Python identifier Change
    __Change = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'Change'), 'Change', '__httpwww_opengis_netkml2_2_UpdateType_httpwww_opengis_netkml2_2Change', True)

    
    Change = property(__Change.value, __Change.set, None, None)


    _ElementMap = {
        __Create.name() : __Create,
        __Delete.name() : __Delete,
        __UpdateOpExtensionGroup.name() : __UpdateOpExtensionGroup,
        __targetHref.name() : __targetHref,
        __UpdateExtensionGroup.name() : __UpdateExtensionGroup,
        __Change.name() : __Change
    }
    _AttributeMap = {
        
    }
Namespace.addCategoryObject('typeBinding', u'UpdateType', UpdateType)


# Complex type AbstractViewType with content type ELEMENT_ONLY
class AbstractViewType (AbstractObjectType):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = True
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'AbstractViewType')
    # Base type is AbstractObjectType
    
    # Element {http://www.opengis.net/kml/2.2}AbstractViewSimpleExtensionGroup uses Python identifier AbstractViewSimpleExtensionGroup
    __AbstractViewSimpleExtensionGroup = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'AbstractViewSimpleExtensionGroup'), 'AbstractViewSimpleExtensionGroup', '__httpwww_opengis_netkml2_2_AbstractViewType_httpwww_opengis_netkml2_2AbstractViewSimpleExtensionGroup', True)

    
    AbstractViewSimpleExtensionGroup = property(__AbstractViewSimpleExtensionGroup.value, __AbstractViewSimpleExtensionGroup.set, None, None)

    
    # Element {http://www.opengis.net/kml/2.2}AbstractViewObjectExtensionGroup uses Python identifier AbstractViewObjectExtensionGroup
    __AbstractViewObjectExtensionGroup = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'AbstractViewObjectExtensionGroup'), 'AbstractViewObjectExtensionGroup', '__httpwww_opengis_netkml2_2_AbstractViewType_httpwww_opengis_netkml2_2AbstractViewObjectExtensionGroup', True)

    
    AbstractViewObjectExtensionGroup = property(__AbstractViewObjectExtensionGroup.value, __AbstractViewObjectExtensionGroup.set, None, None)

    
    # Element ObjectSimpleExtensionGroup ({http://www.opengis.net/kml/2.2}ObjectSimpleExtensionGroup) inherited from {http://www.opengis.net/kml/2.2}AbstractObjectType
    
    # Attribute targetId inherited from {http://www.opengis.net/kml/2.2}AbstractObjectType
    
    # Attribute id inherited from {http://www.opengis.net/kml/2.2}AbstractObjectType

    _ElementMap = AbstractObjectType._ElementMap.copy()
    _ElementMap.update({
        __AbstractViewSimpleExtensionGroup.name() : __AbstractViewSimpleExtensionGroup,
        __AbstractViewObjectExtensionGroup.name() : __AbstractViewObjectExtensionGroup
    })
    _AttributeMap = AbstractObjectType._AttributeMap.copy()
    _AttributeMap.update({
        
    })
Namespace.addCategoryObject('typeBinding', u'AbstractViewType', AbstractViewType)


# Complex type vec2Type with content type EMPTY
class vec2Type (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_EMPTY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'vec2Type')
    # Base type is pyxb.binding.datatypes.anyType
    
    # Attribute y uses Python identifier y
    __y = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'y'), 'y', '__httpwww_opengis_netkml2_2_vec2Type_y', pyxb.binding.datatypes.double, unicode_default=u'1.0')
    
    y = property(__y.value, __y.set, None, None)

    
    # Attribute yunits uses Python identifier yunits
    __yunits = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'yunits'), 'yunits', '__httpwww_opengis_netkml2_2_vec2Type_yunits', unitsEnumType, unicode_default=u'fraction')
    
    yunits = property(__yunits.value, __yunits.set, None, None)

    
    # Attribute xunits uses Python identifier xunits
    __xunits = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'xunits'), 'xunits', '__httpwww_opengis_netkml2_2_vec2Type_xunits', unitsEnumType, unicode_default=u'fraction')
    
    xunits = property(__xunits.value, __xunits.set, None, None)

    
    # Attribute x uses Python identifier x
    __x = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'x'), 'x', '__httpwww_opengis_netkml2_2_vec2Type_x', pyxb.binding.datatypes.double, unicode_default=u'1.0')
    
    x = property(__x.value, __x.set, None, None)


    _ElementMap = {
        
    }
    _AttributeMap = {
        __y.name() : __y,
        __yunits.name() : __yunits,
        __xunits.name() : __xunits,
        __x.name() : __x
    }
Namespace.addCategoryObject('typeBinding', u'vec2Type', vec2Type)


# Complex type AbstractContainerType with content type ELEMENT_ONLY
class AbstractContainerType (AbstractFeatureType):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = True
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'AbstractContainerType')
    # Base type is AbstractFeatureType
    
    # Element link ({http://www.w3.org/2005/Atom}link) inherited from {http://www.opengis.net/kml/2.2}AbstractFeatureType
    
    # Element AbstractStyleSelectorGroup ({http://www.opengis.net/kml/2.2}AbstractStyleSelectorGroup) inherited from {http://www.opengis.net/kml/2.2}AbstractFeatureType
    
    # Element address ({http://www.opengis.net/kml/2.2}address) inherited from {http://www.opengis.net/kml/2.2}AbstractFeatureType
    
    # Element Region ({http://www.opengis.net/kml/2.2}Region) inherited from {http://www.opengis.net/kml/2.2}AbstractFeatureType
    
    # Element AddressDetails ({urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}AddressDetails) inherited from {http://www.opengis.net/kml/2.2}AbstractFeatureType
    
    # Element phoneNumber ({http://www.opengis.net/kml/2.2}phoneNumber) inherited from {http://www.opengis.net/kml/2.2}AbstractFeatureType
    
    # Element Metadata ({http://www.opengis.net/kml/2.2}Metadata) inherited from {http://www.opengis.net/kml/2.2}AbstractFeatureType
    
    # Element AbstractViewGroup ({http://www.opengis.net/kml/2.2}AbstractViewGroup) inherited from {http://www.opengis.net/kml/2.2}AbstractFeatureType
    
    # Element ExtendedData ({http://www.opengis.net/kml/2.2}ExtendedData) inherited from {http://www.opengis.net/kml/2.2}AbstractFeatureType
    
    # Element snippet ({http://www.opengis.net/kml/2.2}snippet) inherited from {http://www.opengis.net/kml/2.2}AbstractFeatureType
    
    # Element AbstractFeatureSimpleExtensionGroup ({http://www.opengis.net/kml/2.2}AbstractFeatureSimpleExtensionGroup) inherited from {http://www.opengis.net/kml/2.2}AbstractFeatureType
    
    # Element styleUrl ({http://www.opengis.net/kml/2.2}styleUrl) inherited from {http://www.opengis.net/kml/2.2}AbstractFeatureType
    
    # Element {http://www.opengis.net/kml/2.2}AbstractContainerSimpleExtensionGroup uses Python identifier AbstractContainerSimpleExtensionGroup
    __AbstractContainerSimpleExtensionGroup = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'AbstractContainerSimpleExtensionGroup'), 'AbstractContainerSimpleExtensionGroup', '__httpwww_opengis_netkml2_2_AbstractContainerType_httpwww_opengis_netkml2_2AbstractContainerSimpleExtensionGroup', True)

    
    AbstractContainerSimpleExtensionGroup = property(__AbstractContainerSimpleExtensionGroup.value, __AbstractContainerSimpleExtensionGroup.set, None, None)

    
    # Element AbstractFeatureObjectExtensionGroup ({http://www.opengis.net/kml/2.2}AbstractFeatureObjectExtensionGroup) inherited from {http://www.opengis.net/kml/2.2}AbstractFeatureType
    
    # Element {http://www.opengis.net/kml/2.2}AbstractContainerObjectExtensionGroup uses Python identifier AbstractContainerObjectExtensionGroup
    __AbstractContainerObjectExtensionGroup = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'AbstractContainerObjectExtensionGroup'), 'AbstractContainerObjectExtensionGroup', '__httpwww_opengis_netkml2_2_AbstractContainerType_httpwww_opengis_netkml2_2AbstractContainerObjectExtensionGroup', True)

    
    AbstractContainerObjectExtensionGroup = property(__AbstractContainerObjectExtensionGroup.value, __AbstractContainerObjectExtensionGroup.set, None, None)

    
    # Element description ({http://www.opengis.net/kml/2.2}description) inherited from {http://www.opengis.net/kml/2.2}AbstractFeatureType
    
    # Element visibility ({http://www.opengis.net/kml/2.2}visibility) inherited from {http://www.opengis.net/kml/2.2}AbstractFeatureType
    
    # Element ObjectSimpleExtensionGroup ({http://www.opengis.net/kml/2.2}ObjectSimpleExtensionGroup) inherited from {http://www.opengis.net/kml/2.2}AbstractObjectType
    
    # Element name ({http://www.opengis.net/kml/2.2}name) inherited from {http://www.opengis.net/kml/2.2}AbstractFeatureType
    
    # Element open ({http://www.opengis.net/kml/2.2}open) inherited from {http://www.opengis.net/kml/2.2}AbstractFeatureType
    
    # Element Snippet ({http://www.opengis.net/kml/2.2}Snippet) inherited from {http://www.opengis.net/kml/2.2}AbstractFeatureType
    
    # Element author ({http://www.w3.org/2005/Atom}author) inherited from {http://www.opengis.net/kml/2.2}AbstractFeatureType
    
    # Element AbstractTimePrimitiveGroup ({http://www.opengis.net/kml/2.2}AbstractTimePrimitiveGroup) inherited from {http://www.opengis.net/kml/2.2}AbstractFeatureType
    
    # Attribute targetId inherited from {http://www.opengis.net/kml/2.2}AbstractObjectType
    
    # Attribute id inherited from {http://www.opengis.net/kml/2.2}AbstractObjectType

    _ElementMap = AbstractFeatureType._ElementMap.copy()
    _ElementMap.update({
        __AbstractContainerSimpleExtensionGroup.name() : __AbstractContainerSimpleExtensionGroup,
        __AbstractContainerObjectExtensionGroup.name() : __AbstractContainerObjectExtensionGroup
    })
    _AttributeMap = AbstractFeatureType._AttributeMap.copy()
    _AttributeMap.update({
        
    })
Namespace.addCategoryObject('typeBinding', u'AbstractContainerType', AbstractContainerType)


# Complex type ChangeType with content type ELEMENT_ONLY
class ChangeType (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'ChangeType')
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {http://www.opengis.net/kml/2.2}AbstractObjectGroup uses Python identifier AbstractObjectGroup
    __AbstractObjectGroup = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'AbstractObjectGroup'), 'AbstractObjectGroup', '__httpwww_opengis_netkml2_2_ChangeType_httpwww_opengis_netkml2_2AbstractObjectGroup', True)

    
    AbstractObjectGroup = property(__AbstractObjectGroup.value, __AbstractObjectGroup.set, None, None)


    _ElementMap = {
        __AbstractObjectGroup.name() : __AbstractObjectGroup
    }
    _AttributeMap = {
        
    }
Namespace.addCategoryObject('typeBinding', u'ChangeType', ChangeType)


# Complex type SchemaType with content type ELEMENT_ONLY
class SchemaType (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'SchemaType')
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {http://www.opengis.net/kml/2.2}SchemaExtension uses Python identifier SchemaExtension
    __SchemaExtension = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'SchemaExtension'), 'SchemaExtension', '__httpwww_opengis_netkml2_2_SchemaType_httpwww_opengis_netkml2_2SchemaExtension', True)

    
    SchemaExtension = property(__SchemaExtension.value, __SchemaExtension.set, None, None)

    
    # Element {http://www.opengis.net/kml/2.2}SimpleField uses Python identifier SimpleField
    __SimpleField = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'SimpleField'), 'SimpleField', '__httpwww_opengis_netkml2_2_SchemaType_httpwww_opengis_netkml2_2SimpleField', True)

    
    SimpleField = property(__SimpleField.value, __SimpleField.set, None, None)

    
    # Attribute name uses Python identifier name
    __name = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'name'), 'name', '__httpwww_opengis_netkml2_2_SchemaType_name', pyxb.binding.datatypes.string)
    
    name = property(__name.value, __name.set, None, None)

    
    # Attribute id uses Python identifier id
    __id = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'id'), 'id', '__httpwww_opengis_netkml2_2_SchemaType_id', pyxb.binding.datatypes.ID)
    
    id = property(__id.value, __id.set, None, None)


    _ElementMap = {
        __SchemaExtension.name() : __SchemaExtension,
        __SimpleField.name() : __SimpleField
    }
    _AttributeMap = {
        __name.name() : __name,
        __id.name() : __id
    }
Namespace.addCategoryObject('typeBinding', u'SchemaType', SchemaType)


# Complex type ViewVolumeType with content type ELEMENT_ONLY
class ViewVolumeType (AbstractObjectType):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'ViewVolumeType')
    # Base type is AbstractObjectType
    
    # Element {http://www.opengis.net/kml/2.2}topFov uses Python identifier topFov
    __topFov = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'topFov'), 'topFov', '__httpwww_opengis_netkml2_2_ViewVolumeType_httpwww_opengis_netkml2_2topFov', False)

    
    topFov = property(__topFov.value, __topFov.set, None, None)

    
    # Element {http://www.opengis.net/kml/2.2}ViewVolumeObjectExtensionGroup uses Python identifier ViewVolumeObjectExtensionGroup
    __ViewVolumeObjectExtensionGroup = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'ViewVolumeObjectExtensionGroup'), 'ViewVolumeObjectExtensionGroup', '__httpwww_opengis_netkml2_2_ViewVolumeType_httpwww_opengis_netkml2_2ViewVolumeObjectExtensionGroup', True)

    
    ViewVolumeObjectExtensionGroup = property(__ViewVolumeObjectExtensionGroup.value, __ViewVolumeObjectExtensionGroup.set, None, None)

    
    # Element ObjectSimpleExtensionGroup ({http://www.opengis.net/kml/2.2}ObjectSimpleExtensionGroup) inherited from {http://www.opengis.net/kml/2.2}AbstractObjectType
    
    # Element {http://www.opengis.net/kml/2.2}near uses Python identifier near
    __near = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'near'), 'near', '__httpwww_opengis_netkml2_2_ViewVolumeType_httpwww_opengis_netkml2_2near', False)

    
    near = property(__near.value, __near.set, None, None)

    
    # Element {http://www.opengis.net/kml/2.2}bottomFov uses Python identifier bottomFov
    __bottomFov = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'bottomFov'), 'bottomFov', '__httpwww_opengis_netkml2_2_ViewVolumeType_httpwww_opengis_netkml2_2bottomFov', False)

    
    bottomFov = property(__bottomFov.value, __bottomFov.set, None, None)

    
    # Element {http://www.opengis.net/kml/2.2}rightFov uses Python identifier rightFov
    __rightFov = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'rightFov'), 'rightFov', '__httpwww_opengis_netkml2_2_ViewVolumeType_httpwww_opengis_netkml2_2rightFov', False)

    
    rightFov = property(__rightFov.value, __rightFov.set, None, None)

    
    # Element {http://www.opengis.net/kml/2.2}ViewVolumeSimpleExtensionGroup uses Python identifier ViewVolumeSimpleExtensionGroup
    __ViewVolumeSimpleExtensionGroup = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'ViewVolumeSimpleExtensionGroup'), 'ViewVolumeSimpleExtensionGroup', '__httpwww_opengis_netkml2_2_ViewVolumeType_httpwww_opengis_netkml2_2ViewVolumeSimpleExtensionGroup', True)

    
    ViewVolumeSimpleExtensionGroup = property(__ViewVolumeSimpleExtensionGroup.value, __ViewVolumeSimpleExtensionGroup.set, None, None)

    
    # Element {http://www.opengis.net/kml/2.2}leftFov uses Python identifier leftFov
    __leftFov = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'leftFov'), 'leftFov', '__httpwww_opengis_netkml2_2_ViewVolumeType_httpwww_opengis_netkml2_2leftFov', False)

    
    leftFov = property(__leftFov.value, __leftFov.set, None, None)

    
    # Attribute targetId inherited from {http://www.opengis.net/kml/2.2}AbstractObjectType
    
    # Attribute id inherited from {http://www.opengis.net/kml/2.2}AbstractObjectType

    _ElementMap = AbstractObjectType._ElementMap.copy()
    _ElementMap.update({
        __topFov.name() : __topFov,
        __ViewVolumeObjectExtensionGroup.name() : __ViewVolumeObjectExtensionGroup,
        __near.name() : __near,
        __bottomFov.name() : __bottomFov,
        __rightFov.name() : __rightFov,
        __ViewVolumeSimpleExtensionGroup.name() : __ViewVolumeSimpleExtensionGroup,
        __leftFov.name() : __leftFov
    })
    _AttributeMap = AbstractObjectType._AttributeMap.copy()
    _AttributeMap.update({
        
    })
Namespace.addCategoryObject('typeBinding', u'ViewVolumeType', ViewVolumeType)


# Complex type CameraType with content type ELEMENT_ONLY
class CameraType (AbstractViewType):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'CameraType')
    # Base type is AbstractViewType
    
    # Element {http://www.opengis.net/kml/2.2}altitude uses Python identifier altitude
    __altitude = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'altitude'), 'altitude', '__httpwww_opengis_netkml2_2_CameraType_httpwww_opengis_netkml2_2altitude', False)

    
    altitude = property(__altitude.value, __altitude.set, None, None)

    
    # Element {http://www.opengis.net/kml/2.2}roll uses Python identifier roll
    __roll = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'roll'), 'roll', '__httpwww_opengis_netkml2_2_CameraType_httpwww_opengis_netkml2_2roll', False)

    
    roll = property(__roll.value, __roll.set, None, None)

    
    # Element AbstractViewSimpleExtensionGroup ({http://www.opengis.net/kml/2.2}AbstractViewSimpleExtensionGroup) inherited from {http://www.opengis.net/kml/2.2}AbstractViewType
    
    # Element {http://www.opengis.net/kml/2.2}longitude uses Python identifier longitude
    __longitude = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'longitude'), 'longitude', '__httpwww_opengis_netkml2_2_CameraType_httpwww_opengis_netkml2_2longitude', False)

    
    longitude = property(__longitude.value, __longitude.set, None, None)

    
    # Element {http://www.opengis.net/kml/2.2}heading uses Python identifier heading
    __heading = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'heading'), 'heading', '__httpwww_opengis_netkml2_2_CameraType_httpwww_opengis_netkml2_2heading', False)

    
    heading = property(__heading.value, __heading.set, None, None)

    
    # Element AbstractViewObjectExtensionGroup ({http://www.opengis.net/kml/2.2}AbstractViewObjectExtensionGroup) inherited from {http://www.opengis.net/kml/2.2}AbstractViewType
    
    # Element {http://www.opengis.net/kml/2.2}altitudeModeGroup uses Python identifier altitudeModeGroup
    __altitudeModeGroup = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'altitudeModeGroup'), 'altitudeModeGroup', '__httpwww_opengis_netkml2_2_CameraType_httpwww_opengis_netkml2_2altitudeModeGroup', False)

    
    altitudeModeGroup = property(__altitudeModeGroup.value, __altitudeModeGroup.set, None, None)

    
    # Element {http://www.opengis.net/kml/2.2}latitude uses Python identifier latitude
    __latitude = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'latitude'), 'latitude', '__httpwww_opengis_netkml2_2_CameraType_httpwww_opengis_netkml2_2latitude', False)

    
    latitude = property(__latitude.value, __latitude.set, None, None)

    
    # Element {http://www.opengis.net/kml/2.2}CameraObjectExtensionGroup uses Python identifier CameraObjectExtensionGroup
    __CameraObjectExtensionGroup = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'CameraObjectExtensionGroup'), 'CameraObjectExtensionGroup', '__httpwww_opengis_netkml2_2_CameraType_httpwww_opengis_netkml2_2CameraObjectExtensionGroup', True)

    
    CameraObjectExtensionGroup = property(__CameraObjectExtensionGroup.value, __CameraObjectExtensionGroup.set, None, None)

    
    # Element {http://www.opengis.net/kml/2.2}tilt uses Python identifier tilt
    __tilt = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'tilt'), 'tilt', '__httpwww_opengis_netkml2_2_CameraType_httpwww_opengis_netkml2_2tilt', False)

    
    tilt = property(__tilt.value, __tilt.set, None, None)

    
    # Element {http://www.opengis.net/kml/2.2}CameraSimpleExtensionGroup uses Python identifier CameraSimpleExtensionGroup
    __CameraSimpleExtensionGroup = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'CameraSimpleExtensionGroup'), 'CameraSimpleExtensionGroup', '__httpwww_opengis_netkml2_2_CameraType_httpwww_opengis_netkml2_2CameraSimpleExtensionGroup', True)

    
    CameraSimpleExtensionGroup = property(__CameraSimpleExtensionGroup.value, __CameraSimpleExtensionGroup.set, None, None)

    
    # Element ObjectSimpleExtensionGroup ({http://www.opengis.net/kml/2.2}ObjectSimpleExtensionGroup) inherited from {http://www.opengis.net/kml/2.2}AbstractObjectType
    
    # Attribute targetId inherited from {http://www.opengis.net/kml/2.2}AbstractObjectType
    
    # Attribute id inherited from {http://www.opengis.net/kml/2.2}AbstractObjectType

    _ElementMap = AbstractViewType._ElementMap.copy()
    _ElementMap.update({
        __altitude.name() : __altitude,
        __roll.name() : __roll,
        __longitude.name() : __longitude,
        __heading.name() : __heading,
        __altitudeModeGroup.name() : __altitudeModeGroup,
        __latitude.name() : __latitude,
        __CameraObjectExtensionGroup.name() : __CameraObjectExtensionGroup,
        __tilt.name() : __tilt,
        __CameraSimpleExtensionGroup.name() : __CameraSimpleExtensionGroup
    })
    _AttributeMap = AbstractViewType._AttributeMap.copy()
    _AttributeMap.update({
        
    })
Namespace.addCategoryObject('typeBinding', u'CameraType', CameraType)


# Complex type ImagePyramidType with content type ELEMENT_ONLY
class ImagePyramidType (AbstractObjectType):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'ImagePyramidType')
    # Base type is AbstractObjectType
    
    # Element {http://www.opengis.net/kml/2.2}gridOrigin uses Python identifier gridOrigin
    __gridOrigin = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'gridOrigin'), 'gridOrigin', '__httpwww_opengis_netkml2_2_ImagePyramidType_httpwww_opengis_netkml2_2gridOrigin', False)

    
    gridOrigin = property(__gridOrigin.value, __gridOrigin.set, None, None)

    
    # Element {http://www.opengis.net/kml/2.2}maxWidth uses Python identifier maxWidth
    __maxWidth = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'maxWidth'), 'maxWidth', '__httpwww_opengis_netkml2_2_ImagePyramidType_httpwww_opengis_netkml2_2maxWidth', False)

    
    maxWidth = property(__maxWidth.value, __maxWidth.set, None, None)

    
    # Element {http://www.opengis.net/kml/2.2}ImagePyramidSimpleExtensionGroup uses Python identifier ImagePyramidSimpleExtensionGroup
    __ImagePyramidSimpleExtensionGroup = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'ImagePyramidSimpleExtensionGroup'), 'ImagePyramidSimpleExtensionGroup', '__httpwww_opengis_netkml2_2_ImagePyramidType_httpwww_opengis_netkml2_2ImagePyramidSimpleExtensionGroup', True)

    
    ImagePyramidSimpleExtensionGroup = property(__ImagePyramidSimpleExtensionGroup.value, __ImagePyramidSimpleExtensionGroup.set, None, None)

    
    # Element {http://www.opengis.net/kml/2.2}maxHeight uses Python identifier maxHeight
    __maxHeight = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'maxHeight'), 'maxHeight', '__httpwww_opengis_netkml2_2_ImagePyramidType_httpwww_opengis_netkml2_2maxHeight', False)

    
    maxHeight = property(__maxHeight.value, __maxHeight.set, None, None)

    
    # Element ObjectSimpleExtensionGroup ({http://www.opengis.net/kml/2.2}ObjectSimpleExtensionGroup) inherited from {http://www.opengis.net/kml/2.2}AbstractObjectType
    
    # Element {http://www.opengis.net/kml/2.2}ImagePyramidObjectExtensionGroup uses Python identifier ImagePyramidObjectExtensionGroup
    __ImagePyramidObjectExtensionGroup = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'ImagePyramidObjectExtensionGroup'), 'ImagePyramidObjectExtensionGroup', '__httpwww_opengis_netkml2_2_ImagePyramidType_httpwww_opengis_netkml2_2ImagePyramidObjectExtensionGroup', True)

    
    ImagePyramidObjectExtensionGroup = property(__ImagePyramidObjectExtensionGroup.value, __ImagePyramidObjectExtensionGroup.set, None, None)

    
    # Element {http://www.opengis.net/kml/2.2}tileSize uses Python identifier tileSize
    __tileSize = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'tileSize'), 'tileSize', '__httpwww_opengis_netkml2_2_ImagePyramidType_httpwww_opengis_netkml2_2tileSize', False)

    
    tileSize = property(__tileSize.value, __tileSize.set, None, None)

    
    # Attribute targetId inherited from {http://www.opengis.net/kml/2.2}AbstractObjectType
    
    # Attribute id inherited from {http://www.opengis.net/kml/2.2}AbstractObjectType

    _ElementMap = AbstractObjectType._ElementMap.copy()
    _ElementMap.update({
        __gridOrigin.name() : __gridOrigin,
        __maxWidth.name() : __maxWidth,
        __ImagePyramidSimpleExtensionGroup.name() : __ImagePyramidSimpleExtensionGroup,
        __maxHeight.name() : __maxHeight,
        __ImagePyramidObjectExtensionGroup.name() : __ImagePyramidObjectExtensionGroup,
        __tileSize.name() : __tileSize
    })
    _AttributeMap = AbstractObjectType._AttributeMap.copy()
    _AttributeMap.update({
        
    })
Namespace.addCategoryObject('typeBinding', u'ImagePyramidType', ImagePyramidType)


# Complex type GroundOverlayType with content type ELEMENT_ONLY
class GroundOverlayType (AbstractOverlayType):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'GroundOverlayType')
    # Base type is AbstractOverlayType
    
    # Element link ({http://www.w3.org/2005/Atom}link) inherited from {http://www.opengis.net/kml/2.2}AbstractFeatureType
    
    # Element AbstractStyleSelectorGroup ({http://www.opengis.net/kml/2.2}AbstractStyleSelectorGroup) inherited from {http://www.opengis.net/kml/2.2}AbstractFeatureType
    
    # Element {http://www.opengis.net/kml/2.2}GroundOverlaySimpleExtensionGroup uses Python identifier GroundOverlaySimpleExtensionGroup
    __GroundOverlaySimpleExtensionGroup = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'GroundOverlaySimpleExtensionGroup'), 'GroundOverlaySimpleExtensionGroup', '__httpwww_opengis_netkml2_2_GroundOverlayType_httpwww_opengis_netkml2_2GroundOverlaySimpleExtensionGroup', True)

    
    GroundOverlaySimpleExtensionGroup = property(__GroundOverlaySimpleExtensionGroup.value, __GroundOverlaySimpleExtensionGroup.set, None, None)

    
    # Element address ({http://www.opengis.net/kml/2.2}address) inherited from {http://www.opengis.net/kml/2.2}AbstractFeatureType
    
    # Element Region ({http://www.opengis.net/kml/2.2}Region) inherited from {http://www.opengis.net/kml/2.2}AbstractFeatureType
    
    # Element {http://www.opengis.net/kml/2.2}GroundOverlayObjectExtensionGroup uses Python identifier GroundOverlayObjectExtensionGroup
    __GroundOverlayObjectExtensionGroup = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'GroundOverlayObjectExtensionGroup'), 'GroundOverlayObjectExtensionGroup', '__httpwww_opengis_netkml2_2_GroundOverlayType_httpwww_opengis_netkml2_2GroundOverlayObjectExtensionGroup', True)

    
    GroundOverlayObjectExtensionGroup = property(__GroundOverlayObjectExtensionGroup.value, __GroundOverlayObjectExtensionGroup.set, None, None)

    
    # Element AddressDetails ({urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}AddressDetails) inherited from {http://www.opengis.net/kml/2.2}AbstractFeatureType
    
    # Element phoneNumber ({http://www.opengis.net/kml/2.2}phoneNumber) inherited from {http://www.opengis.net/kml/2.2}AbstractFeatureType
    
    # Element Metadata ({http://www.opengis.net/kml/2.2}Metadata) inherited from {http://www.opengis.net/kml/2.2}AbstractFeatureType
    
    # Element visibility ({http://www.opengis.net/kml/2.2}visibility) inherited from {http://www.opengis.net/kml/2.2}AbstractFeatureType
    
    # Element ExtendedData ({http://www.opengis.net/kml/2.2}ExtendedData) inherited from {http://www.opengis.net/kml/2.2}AbstractFeatureType
    
    # Element AbstractFeatureObjectExtensionGroup ({http://www.opengis.net/kml/2.2}AbstractFeatureObjectExtensionGroup) inherited from {http://www.opengis.net/kml/2.2}AbstractFeatureType
    
    # Element Snippet ({http://www.opengis.net/kml/2.2}Snippet) inherited from {http://www.opengis.net/kml/2.2}AbstractFeatureType
    
    # Element styleUrl ({http://www.opengis.net/kml/2.2}styleUrl) inherited from {http://www.opengis.net/kml/2.2}AbstractFeatureType
    
    # Element color ({http://www.opengis.net/kml/2.2}color) inherited from {http://www.opengis.net/kml/2.2}AbstractOverlayType
    
    # Element description ({http://www.opengis.net/kml/2.2}description) inherited from {http://www.opengis.net/kml/2.2}AbstractFeatureType
    
    # Element drawOrder ({http://www.opengis.net/kml/2.2}drawOrder) inherited from {http://www.opengis.net/kml/2.2}AbstractOverlayType
    
    # Element AbstractViewGroup ({http://www.opengis.net/kml/2.2}AbstractViewGroup) inherited from {http://www.opengis.net/kml/2.2}AbstractFeatureType
    
    # Element ObjectSimpleExtensionGroup ({http://www.opengis.net/kml/2.2}ObjectSimpleExtensionGroup) inherited from {http://www.opengis.net/kml/2.2}AbstractObjectType
    
    # Element Icon ({http://www.opengis.net/kml/2.2}Icon) inherited from {http://www.opengis.net/kml/2.2}AbstractOverlayType
    
    # Element snippet ({http://www.opengis.net/kml/2.2}snippet) inherited from {http://www.opengis.net/kml/2.2}AbstractFeatureType
    
    # Element {http://www.opengis.net/kml/2.2}altitude uses Python identifier altitude
    __altitude = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'altitude'), 'altitude', '__httpwww_opengis_netkml2_2_GroundOverlayType_httpwww_opengis_netkml2_2altitude', False)

    
    altitude = property(__altitude.value, __altitude.set, None, None)

    
    # Element name ({http://www.opengis.net/kml/2.2}name) inherited from {http://www.opengis.net/kml/2.2}AbstractFeatureType
    
    # Element open ({http://www.opengis.net/kml/2.2}open) inherited from {http://www.opengis.net/kml/2.2}AbstractFeatureType
    
    # Element AbstractOverlaySimpleExtensionGroup ({http://www.opengis.net/kml/2.2}AbstractOverlaySimpleExtensionGroup) inherited from {http://www.opengis.net/kml/2.2}AbstractOverlayType
    
    # Element AbstractFeatureSimpleExtensionGroup ({http://www.opengis.net/kml/2.2}AbstractFeatureSimpleExtensionGroup) inherited from {http://www.opengis.net/kml/2.2}AbstractFeatureType
    
    # Element {http://www.opengis.net/kml/2.2}altitudeModeGroup uses Python identifier altitudeModeGroup
    __altitudeModeGroup = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'altitudeModeGroup'), 'altitudeModeGroup', '__httpwww_opengis_netkml2_2_GroundOverlayType_httpwww_opengis_netkml2_2altitudeModeGroup', False)

    
    altitudeModeGroup = property(__altitudeModeGroup.value, __altitudeModeGroup.set, None, None)

    
    # Element author ({http://www.w3.org/2005/Atom}author) inherited from {http://www.opengis.net/kml/2.2}AbstractFeatureType
    
    # Element AbstractTimePrimitiveGroup ({http://www.opengis.net/kml/2.2}AbstractTimePrimitiveGroup) inherited from {http://www.opengis.net/kml/2.2}AbstractFeatureType
    
    # Element AbstractOverlayObjectExtensionGroup ({http://www.opengis.net/kml/2.2}AbstractOverlayObjectExtensionGroup) inherited from {http://www.opengis.net/kml/2.2}AbstractOverlayType
    
    # Element {http://www.opengis.net/kml/2.2}LatLonBox uses Python identifier LatLonBox
    __LatLonBox = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'LatLonBox'), 'LatLonBox', '__httpwww_opengis_netkml2_2_GroundOverlayType_httpwww_opengis_netkml2_2LatLonBox', False)

    
    LatLonBox = property(__LatLonBox.value, __LatLonBox.set, None, None)

    
    # Attribute targetId inherited from {http://www.opengis.net/kml/2.2}AbstractObjectType
    
    # Attribute id inherited from {http://www.opengis.net/kml/2.2}AbstractObjectType

    _ElementMap = AbstractOverlayType._ElementMap.copy()
    _ElementMap.update({
        __GroundOverlaySimpleExtensionGroup.name() : __GroundOverlaySimpleExtensionGroup,
        __GroundOverlayObjectExtensionGroup.name() : __GroundOverlayObjectExtensionGroup,
        __altitude.name() : __altitude,
        __altitudeModeGroup.name() : __altitudeModeGroup,
        __LatLonBox.name() : __LatLonBox
    })
    _AttributeMap = AbstractOverlayType._AttributeMap.copy()
    _AttributeMap.update({
        
    })
Namespace.addCategoryObject('typeBinding', u'GroundOverlayType', GroundOverlayType)


# Complex type SimpleDataType with content type SIMPLE
class SimpleDataType (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = pyxb.binding.datatypes.string
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_SIMPLE
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'SimpleDataType')
    # Base type is pyxb.binding.datatypes.string
    
    # Attribute name uses Python identifier name
    __name = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'name'), 'name', '__httpwww_opengis_netkml2_2_SimpleDataType_name', pyxb.binding.datatypes.string, required=True)
    
    name = property(__name.value, __name.set, None, None)


    _ElementMap = {
        
    }
    _AttributeMap = {
        __name.name() : __name
    }
Namespace.addCategoryObject('typeBinding', u'SimpleDataType', SimpleDataType)


# Complex type MetadataType with content type ELEMENT_ONLY
class MetadataType (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'MetadataType')
    # Base type is pyxb.binding.datatypes.anyType
    _HasWildcardElement = True

    _ElementMap = {
        
    }
    _AttributeMap = {
        
    }
Namespace.addCategoryObject('typeBinding', u'MetadataType', MetadataType)


# Complex type PairType with content type ELEMENT_ONLY
class PairType (AbstractObjectType):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'PairType')
    # Base type is AbstractObjectType
    
    # Element {http://www.opengis.net/kml/2.2}key uses Python identifier key
    __key = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'key'), 'key', '__httpwww_opengis_netkml2_2_PairType_httpwww_opengis_netkml2_2key', False)

    
    key = property(__key.value, __key.set, None, None)

    
    # Element ObjectSimpleExtensionGroup ({http://www.opengis.net/kml/2.2}ObjectSimpleExtensionGroup) inherited from {http://www.opengis.net/kml/2.2}AbstractObjectType
    
    # Element {http://www.opengis.net/kml/2.2}styleUrl uses Python identifier styleUrl
    __styleUrl = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'styleUrl'), 'styleUrl', '__httpwww_opengis_netkml2_2_PairType_httpwww_opengis_netkml2_2styleUrl', False)

    
    styleUrl = property(__styleUrl.value, __styleUrl.set, None, None)

    
    # Element {http://www.opengis.net/kml/2.2}PairObjectExtensionGroup uses Python identifier PairObjectExtensionGroup
    __PairObjectExtensionGroup = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'PairObjectExtensionGroup'), 'PairObjectExtensionGroup', '__httpwww_opengis_netkml2_2_PairType_httpwww_opengis_netkml2_2PairObjectExtensionGroup', True)

    
    PairObjectExtensionGroup = property(__PairObjectExtensionGroup.value, __PairObjectExtensionGroup.set, None, None)

    
    # Element {http://www.opengis.net/kml/2.2}PairSimpleExtensionGroup uses Python identifier PairSimpleExtensionGroup
    __PairSimpleExtensionGroup = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'PairSimpleExtensionGroup'), 'PairSimpleExtensionGroup', '__httpwww_opengis_netkml2_2_PairType_httpwww_opengis_netkml2_2PairSimpleExtensionGroup', True)

    
    PairSimpleExtensionGroup = property(__PairSimpleExtensionGroup.value, __PairSimpleExtensionGroup.set, None, None)

    
    # Element {http://www.opengis.net/kml/2.2}AbstractStyleSelectorGroup uses Python identifier AbstractStyleSelectorGroup
    __AbstractStyleSelectorGroup = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'AbstractStyleSelectorGroup'), 'AbstractStyleSelectorGroup', '__httpwww_opengis_netkml2_2_PairType_httpwww_opengis_netkml2_2AbstractStyleSelectorGroup', False)

    
    AbstractStyleSelectorGroup = property(__AbstractStyleSelectorGroup.value, __AbstractStyleSelectorGroup.set, None, None)

    
    # Attribute targetId inherited from {http://www.opengis.net/kml/2.2}AbstractObjectType
    
    # Attribute id inherited from {http://www.opengis.net/kml/2.2}AbstractObjectType

    _ElementMap = AbstractObjectType._ElementMap.copy()
    _ElementMap.update({
        __key.name() : __key,
        __styleUrl.name() : __styleUrl,
        __PairObjectExtensionGroup.name() : __PairObjectExtensionGroup,
        __PairSimpleExtensionGroup.name() : __PairSimpleExtensionGroup,
        __AbstractStyleSelectorGroup.name() : __AbstractStyleSelectorGroup
    })
    _AttributeMap = AbstractObjectType._AttributeMap.copy()
    _AttributeMap.update({
        
    })
Namespace.addCategoryObject('typeBinding', u'PairType', PairType)


# Complex type ExtendedDataType with content type ELEMENT_ONLY
class ExtendedDataType (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'ExtendedDataType')
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {http://www.opengis.net/kml/2.2}SchemaData uses Python identifier SchemaData
    __SchemaData = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'SchemaData'), 'SchemaData', '__httpwww_opengis_netkml2_2_ExtendedDataType_httpwww_opengis_netkml2_2SchemaData', True)

    
    SchemaData = property(__SchemaData.value, __SchemaData.set, None, None)

    
    # Element {http://www.opengis.net/kml/2.2}Data uses Python identifier Data
    __Data = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'Data'), 'Data', '__httpwww_opengis_netkml2_2_ExtendedDataType_httpwww_opengis_netkml2_2Data', True)

    
    Data = property(__Data.value, __Data.set, None, None)

    _HasWildcardElement = True

    _ElementMap = {
        __SchemaData.name() : __SchemaData,
        __Data.name() : __Data
    }
    _AttributeMap = {
        
    }
Namespace.addCategoryObject('typeBinding', u'ExtendedDataType', ExtendedDataType)


# Complex type StyleMapType with content type ELEMENT_ONLY
class StyleMapType (AbstractStyleSelectorType):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'StyleMapType')
    # Base type is AbstractStyleSelectorType
    
    # Element {http://www.opengis.net/kml/2.2}StyleMapSimpleExtensionGroup uses Python identifier StyleMapSimpleExtensionGroup
    __StyleMapSimpleExtensionGroup = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'StyleMapSimpleExtensionGroup'), 'StyleMapSimpleExtensionGroup', '__httpwww_opengis_netkml2_2_StyleMapType_httpwww_opengis_netkml2_2StyleMapSimpleExtensionGroup', True)

    
    StyleMapSimpleExtensionGroup = property(__StyleMapSimpleExtensionGroup.value, __StyleMapSimpleExtensionGroup.set, None, None)

    
    # Element {http://www.opengis.net/kml/2.2}Pair uses Python identifier Pair
    __Pair = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'Pair'), 'Pair', '__httpwww_opengis_netkml2_2_StyleMapType_httpwww_opengis_netkml2_2Pair', True)

    
    Pair = property(__Pair.value, __Pair.set, None, None)

    
    # Element ObjectSimpleExtensionGroup ({http://www.opengis.net/kml/2.2}ObjectSimpleExtensionGroup) inherited from {http://www.opengis.net/kml/2.2}AbstractObjectType
    
    # Element {http://www.opengis.net/kml/2.2}StyleMapObjectExtensionGroup uses Python identifier StyleMapObjectExtensionGroup
    __StyleMapObjectExtensionGroup = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'StyleMapObjectExtensionGroup'), 'StyleMapObjectExtensionGroup', '__httpwww_opengis_netkml2_2_StyleMapType_httpwww_opengis_netkml2_2StyleMapObjectExtensionGroup', True)

    
    StyleMapObjectExtensionGroup = property(__StyleMapObjectExtensionGroup.value, __StyleMapObjectExtensionGroup.set, None, None)

    
    # Element AbstractStyleSelectorObjectExtensionGroup ({http://www.opengis.net/kml/2.2}AbstractStyleSelectorObjectExtensionGroup) inherited from {http://www.opengis.net/kml/2.2}AbstractStyleSelectorType
    
    # Element AbstractStyleSelectorSimpleExtensionGroup ({http://www.opengis.net/kml/2.2}AbstractStyleSelectorSimpleExtensionGroup) inherited from {http://www.opengis.net/kml/2.2}AbstractStyleSelectorType
    
    # Attribute targetId inherited from {http://www.opengis.net/kml/2.2}AbstractObjectType
    
    # Attribute id inherited from {http://www.opengis.net/kml/2.2}AbstractObjectType

    _ElementMap = AbstractStyleSelectorType._ElementMap.copy()
    _ElementMap.update({
        __StyleMapSimpleExtensionGroup.name() : __StyleMapSimpleExtensionGroup,
        __Pair.name() : __Pair,
        __StyleMapObjectExtensionGroup.name() : __StyleMapObjectExtensionGroup
    })
    _AttributeMap = AbstractStyleSelectorType._AttributeMap.copy()
    _AttributeMap.update({
        
    })
Namespace.addCategoryObject('typeBinding', u'StyleMapType', StyleMapType)


# Complex type OrientationType with content type ELEMENT_ONLY
class OrientationType (AbstractObjectType):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'OrientationType')
    # Base type is AbstractObjectType
    
    # Element {http://www.opengis.net/kml/2.2}OrientationSimpleExtensionGroup uses Python identifier OrientationSimpleExtensionGroup
    __OrientationSimpleExtensionGroup = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'OrientationSimpleExtensionGroup'), 'OrientationSimpleExtensionGroup', '__httpwww_opengis_netkml2_2_OrientationType_httpwww_opengis_netkml2_2OrientationSimpleExtensionGroup', True)

    
    OrientationSimpleExtensionGroup = property(__OrientationSimpleExtensionGroup.value, __OrientationSimpleExtensionGroup.set, None, None)

    
    # Element ObjectSimpleExtensionGroup ({http://www.opengis.net/kml/2.2}ObjectSimpleExtensionGroup) inherited from {http://www.opengis.net/kml/2.2}AbstractObjectType
    
    # Element {http://www.opengis.net/kml/2.2}OrientationObjectExtensionGroup uses Python identifier OrientationObjectExtensionGroup
    __OrientationObjectExtensionGroup = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'OrientationObjectExtensionGroup'), 'OrientationObjectExtensionGroup', '__httpwww_opengis_netkml2_2_OrientationType_httpwww_opengis_netkml2_2OrientationObjectExtensionGroup', True)

    
    OrientationObjectExtensionGroup = property(__OrientationObjectExtensionGroup.value, __OrientationObjectExtensionGroup.set, None, None)

    
    # Element {http://www.opengis.net/kml/2.2}roll uses Python identifier roll
    __roll = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'roll'), 'roll', '__httpwww_opengis_netkml2_2_OrientationType_httpwww_opengis_netkml2_2roll', False)

    
    roll = property(__roll.value, __roll.set, None, None)

    
    # Element {http://www.opengis.net/kml/2.2}tilt uses Python identifier tilt
    __tilt = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'tilt'), 'tilt', '__httpwww_opengis_netkml2_2_OrientationType_httpwww_opengis_netkml2_2tilt', False)

    
    tilt = property(__tilt.value, __tilt.set, None, None)

    
    # Element {http://www.opengis.net/kml/2.2}heading uses Python identifier heading
    __heading = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'heading'), 'heading', '__httpwww_opengis_netkml2_2_OrientationType_httpwww_opengis_netkml2_2heading', False)

    
    heading = property(__heading.value, __heading.set, None, None)

    
    # Attribute targetId inherited from {http://www.opengis.net/kml/2.2}AbstractObjectType
    
    # Attribute id inherited from {http://www.opengis.net/kml/2.2}AbstractObjectType

    _ElementMap = AbstractObjectType._ElementMap.copy()
    _ElementMap.update({
        __OrientationSimpleExtensionGroup.name() : __OrientationSimpleExtensionGroup,
        __OrientationObjectExtensionGroup.name() : __OrientationObjectExtensionGroup,
        __roll.name() : __roll,
        __tilt.name() : __tilt,
        __heading.name() : __heading
    })
    _AttributeMap = AbstractObjectType._AttributeMap.copy()
    _AttributeMap.update({
        
    })
Namespace.addCategoryObject('typeBinding', u'OrientationType', OrientationType)


# Complex type PointType with content type ELEMENT_ONLY
class PointType (AbstractGeometryType):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'PointType')
    # Base type is AbstractGeometryType
    
    # Element {http://www.opengis.net/kml/2.2}altitudeModeGroup uses Python identifier altitudeModeGroup
    __altitudeModeGroup = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'altitudeModeGroup'), 'altitudeModeGroup', '__httpwww_opengis_netkml2_2_PointType_httpwww_opengis_netkml2_2altitudeModeGroup', False)

    
    altitudeModeGroup = property(__altitudeModeGroup.value, __altitudeModeGroup.set, None, None)

    
    # Element AbstractGeometryObjectExtensionGroup ({http://www.opengis.net/kml/2.2}AbstractGeometryObjectExtensionGroup) inherited from {http://www.opengis.net/kml/2.2}AbstractGeometryType
    
    # Element {http://www.opengis.net/kml/2.2}PointObjectExtensionGroup uses Python identifier PointObjectExtensionGroup
    __PointObjectExtensionGroup = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'PointObjectExtensionGroup'), 'PointObjectExtensionGroup', '__httpwww_opengis_netkml2_2_PointType_httpwww_opengis_netkml2_2PointObjectExtensionGroup', True)

    
    PointObjectExtensionGroup = property(__PointObjectExtensionGroup.value, __PointObjectExtensionGroup.set, None, None)

    
    # Element {http://www.opengis.net/kml/2.2}coordinates uses Python identifier coordinates
    __coordinates = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'coordinates'), 'coordinates', '__httpwww_opengis_netkml2_2_PointType_httpwww_opengis_netkml2_2coordinates', False)

    
    coordinates = property(__coordinates.value, __coordinates.set, None, None)

    
    # Element {http://www.opengis.net/kml/2.2}extrude uses Python identifier extrude
    __extrude = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'extrude'), 'extrude', '__httpwww_opengis_netkml2_2_PointType_httpwww_opengis_netkml2_2extrude', False)

    
    extrude = property(__extrude.value, __extrude.set, None, None)

    
    # Element {http://www.opengis.net/kml/2.2}PointSimpleExtensionGroup uses Python identifier PointSimpleExtensionGroup
    __PointSimpleExtensionGroup = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'PointSimpleExtensionGroup'), 'PointSimpleExtensionGroup', '__httpwww_opengis_netkml2_2_PointType_httpwww_opengis_netkml2_2PointSimpleExtensionGroup', True)

    
    PointSimpleExtensionGroup = property(__PointSimpleExtensionGroup.value, __PointSimpleExtensionGroup.set, None, None)

    
    # Element AbstractGeometrySimpleExtensionGroup ({http://www.opengis.net/kml/2.2}AbstractGeometrySimpleExtensionGroup) inherited from {http://www.opengis.net/kml/2.2}AbstractGeometryType
    
    # Element ObjectSimpleExtensionGroup ({http://www.opengis.net/kml/2.2}ObjectSimpleExtensionGroup) inherited from {http://www.opengis.net/kml/2.2}AbstractObjectType
    
    # Attribute targetId inherited from {http://www.opengis.net/kml/2.2}AbstractObjectType
    
    # Attribute id inherited from {http://www.opengis.net/kml/2.2}AbstractObjectType

    _ElementMap = AbstractGeometryType._ElementMap.copy()
    _ElementMap.update({
        __altitudeModeGroup.name() : __altitudeModeGroup,
        __PointObjectExtensionGroup.name() : __PointObjectExtensionGroup,
        __coordinates.name() : __coordinates,
        __extrude.name() : __extrude,
        __PointSimpleExtensionGroup.name() : __PointSimpleExtensionGroup
    })
    _AttributeMap = AbstractGeometryType._AttributeMap.copy()
    _AttributeMap.update({
        
    })
Namespace.addCategoryObject('typeBinding', u'PointType', PointType)


# Complex type AbstractLatLonBoxType with content type ELEMENT_ONLY
class AbstractLatLonBoxType (AbstractObjectType):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = True
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'AbstractLatLonBoxType')
    # Base type is AbstractObjectType
    
    # Element {http://www.opengis.net/kml/2.2}AbstractLatLonBoxSimpleExtensionGroup uses Python identifier AbstractLatLonBoxSimpleExtensionGroup
    __AbstractLatLonBoxSimpleExtensionGroup = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'AbstractLatLonBoxSimpleExtensionGroup'), 'AbstractLatLonBoxSimpleExtensionGroup', '__httpwww_opengis_netkml2_2_AbstractLatLonBoxType_httpwww_opengis_netkml2_2AbstractLatLonBoxSimpleExtensionGroup', True)

    
    AbstractLatLonBoxSimpleExtensionGroup = property(__AbstractLatLonBoxSimpleExtensionGroup.value, __AbstractLatLonBoxSimpleExtensionGroup.set, None, None)

    
    # Element ObjectSimpleExtensionGroup ({http://www.opengis.net/kml/2.2}ObjectSimpleExtensionGroup) inherited from {http://www.opengis.net/kml/2.2}AbstractObjectType
    
    # Element {http://www.opengis.net/kml/2.2}north uses Python identifier north
    __north = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'north'), 'north', '__httpwww_opengis_netkml2_2_AbstractLatLonBoxType_httpwww_opengis_netkml2_2north', False)

    
    north = property(__north.value, __north.set, None, None)

    
    # Element {http://www.opengis.net/kml/2.2}AbstractLatLonBoxObjectExtensionGroup uses Python identifier AbstractLatLonBoxObjectExtensionGroup
    __AbstractLatLonBoxObjectExtensionGroup = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'AbstractLatLonBoxObjectExtensionGroup'), 'AbstractLatLonBoxObjectExtensionGroup', '__httpwww_opengis_netkml2_2_AbstractLatLonBoxType_httpwww_opengis_netkml2_2AbstractLatLonBoxObjectExtensionGroup', True)

    
    AbstractLatLonBoxObjectExtensionGroup = property(__AbstractLatLonBoxObjectExtensionGroup.value, __AbstractLatLonBoxObjectExtensionGroup.set, None, None)

    
    # Element {http://www.opengis.net/kml/2.2}east uses Python identifier east
    __east = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'east'), 'east', '__httpwww_opengis_netkml2_2_AbstractLatLonBoxType_httpwww_opengis_netkml2_2east', False)

    
    east = property(__east.value, __east.set, None, None)

    
    # Element {http://www.opengis.net/kml/2.2}west uses Python identifier west
    __west = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'west'), 'west', '__httpwww_opengis_netkml2_2_AbstractLatLonBoxType_httpwww_opengis_netkml2_2west', False)

    
    west = property(__west.value, __west.set, None, None)

    
    # Element {http://www.opengis.net/kml/2.2}south uses Python identifier south
    __south = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'south'), 'south', '__httpwww_opengis_netkml2_2_AbstractLatLonBoxType_httpwww_opengis_netkml2_2south', False)

    
    south = property(__south.value, __south.set, None, None)

    
    # Attribute targetId inherited from {http://www.opengis.net/kml/2.2}AbstractObjectType
    
    # Attribute id inherited from {http://www.opengis.net/kml/2.2}AbstractObjectType

    _ElementMap = AbstractObjectType._ElementMap.copy()
    _ElementMap.update({
        __AbstractLatLonBoxSimpleExtensionGroup.name() : __AbstractLatLonBoxSimpleExtensionGroup,
        __north.name() : __north,
        __AbstractLatLonBoxObjectExtensionGroup.name() : __AbstractLatLonBoxObjectExtensionGroup,
        __east.name() : __east,
        __west.name() : __west,
        __south.name() : __south
    })
    _AttributeMap = AbstractObjectType._AttributeMap.copy()
    _AttributeMap.update({
        
    })
Namespace.addCategoryObject('typeBinding', u'AbstractLatLonBoxType', AbstractLatLonBoxType)


# Complex type LatLonBoxType with content type ELEMENT_ONLY
class LatLonBoxType (AbstractLatLonBoxType):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'LatLonBoxType')
    # Base type is AbstractLatLonBoxType
    
    # Element AbstractLatLonBoxSimpleExtensionGroup ({http://www.opengis.net/kml/2.2}AbstractLatLonBoxSimpleExtensionGroup) inherited from {http://www.opengis.net/kml/2.2}AbstractLatLonBoxType
    
    # Element AbstractLatLonBoxObjectExtensionGroup ({http://www.opengis.net/kml/2.2}AbstractLatLonBoxObjectExtensionGroup) inherited from {http://www.opengis.net/kml/2.2}AbstractLatLonBoxType
    
    # Element {http://www.opengis.net/kml/2.2}LatLonBoxObjectExtensionGroup uses Python identifier LatLonBoxObjectExtensionGroup
    __LatLonBoxObjectExtensionGroup = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'LatLonBoxObjectExtensionGroup'), 'LatLonBoxObjectExtensionGroup', '__httpwww_opengis_netkml2_2_LatLonBoxType_httpwww_opengis_netkml2_2LatLonBoxObjectExtensionGroup', True)

    
    LatLonBoxObjectExtensionGroup = property(__LatLonBoxObjectExtensionGroup.value, __LatLonBoxObjectExtensionGroup.set, None, None)

    
    # Element north ({http://www.opengis.net/kml/2.2}north) inherited from {http://www.opengis.net/kml/2.2}AbstractLatLonBoxType
    
    # Element south ({http://www.opengis.net/kml/2.2}south) inherited from {http://www.opengis.net/kml/2.2}AbstractLatLonBoxType
    
    # Element {http://www.opengis.net/kml/2.2}rotation uses Python identifier rotation
    __rotation = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'rotation'), 'rotation', '__httpwww_opengis_netkml2_2_LatLonBoxType_httpwww_opengis_netkml2_2rotation', False)

    
    rotation = property(__rotation.value, __rotation.set, None, None)

    
    # Element east ({http://www.opengis.net/kml/2.2}east) inherited from {http://www.opengis.net/kml/2.2}AbstractLatLonBoxType
    
    # Element ObjectSimpleExtensionGroup ({http://www.opengis.net/kml/2.2}ObjectSimpleExtensionGroup) inherited from {http://www.opengis.net/kml/2.2}AbstractObjectType
    
    # Element west ({http://www.opengis.net/kml/2.2}west) inherited from {http://www.opengis.net/kml/2.2}AbstractLatLonBoxType
    
    # Element {http://www.opengis.net/kml/2.2}LatLonBoxSimpleExtensionGroup uses Python identifier LatLonBoxSimpleExtensionGroup
    __LatLonBoxSimpleExtensionGroup = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'LatLonBoxSimpleExtensionGroup'), 'LatLonBoxSimpleExtensionGroup', '__httpwww_opengis_netkml2_2_LatLonBoxType_httpwww_opengis_netkml2_2LatLonBoxSimpleExtensionGroup', True)

    
    LatLonBoxSimpleExtensionGroup = property(__LatLonBoxSimpleExtensionGroup.value, __LatLonBoxSimpleExtensionGroup.set, None, None)

    
    # Attribute targetId inherited from {http://www.opengis.net/kml/2.2}AbstractObjectType
    
    # Attribute id inherited from {http://www.opengis.net/kml/2.2}AbstractObjectType

    _ElementMap = AbstractLatLonBoxType._ElementMap.copy()
    _ElementMap.update({
        __LatLonBoxObjectExtensionGroup.name() : __LatLonBoxObjectExtensionGroup,
        __rotation.name() : __rotation,
        __LatLonBoxSimpleExtensionGroup.name() : __LatLonBoxSimpleExtensionGroup
    })
    _AttributeMap = AbstractLatLonBoxType._AttributeMap.copy()
    _AttributeMap.update({
        
    })
Namespace.addCategoryObject('typeBinding', u'LatLonBoxType', LatLonBoxType)


# Complex type LineStringType with content type ELEMENT_ONLY
class LineStringType (AbstractGeometryType):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'LineStringType')
    # Base type is AbstractGeometryType
    
    # Element {http://www.opengis.net/kml/2.2}coordinates uses Python identifier coordinates
    __coordinates = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'coordinates'), 'coordinates', '__httpwww_opengis_netkml2_2_LineStringType_httpwww_opengis_netkml2_2coordinates', False)

    
    coordinates = property(__coordinates.value, __coordinates.set, None, None)

    
    # Element AbstractGeometryObjectExtensionGroup ({http://www.opengis.net/kml/2.2}AbstractGeometryObjectExtensionGroup) inherited from {http://www.opengis.net/kml/2.2}AbstractGeometryType
    
    # Element {http://www.opengis.net/kml/2.2}tessellate uses Python identifier tessellate
    __tessellate = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'tessellate'), 'tessellate', '__httpwww_opengis_netkml2_2_LineStringType_httpwww_opengis_netkml2_2tessellate', False)

    
    tessellate = property(__tessellate.value, __tessellate.set, None, None)

    
    # Element {http://www.opengis.net/kml/2.2}LineStringSimpleExtensionGroup uses Python identifier LineStringSimpleExtensionGroup
    __LineStringSimpleExtensionGroup = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'LineStringSimpleExtensionGroup'), 'LineStringSimpleExtensionGroup', '__httpwww_opengis_netkml2_2_LineStringType_httpwww_opengis_netkml2_2LineStringSimpleExtensionGroup', True)

    
    LineStringSimpleExtensionGroup = property(__LineStringSimpleExtensionGroup.value, __LineStringSimpleExtensionGroup.set, None, None)

    
    # Element {http://www.opengis.net/kml/2.2}altitudeModeGroup uses Python identifier altitudeModeGroup
    __altitudeModeGroup = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'altitudeModeGroup'), 'altitudeModeGroup', '__httpwww_opengis_netkml2_2_LineStringType_httpwww_opengis_netkml2_2altitudeModeGroup', False)

    
    altitudeModeGroup = property(__altitudeModeGroup.value, __altitudeModeGroup.set, None, None)

    
    # Element {http://www.opengis.net/kml/2.2}LineStringObjectExtensionGroup uses Python identifier LineStringObjectExtensionGroup
    __LineStringObjectExtensionGroup = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'LineStringObjectExtensionGroup'), 'LineStringObjectExtensionGroup', '__httpwww_opengis_netkml2_2_LineStringType_httpwww_opengis_netkml2_2LineStringObjectExtensionGroup', True)

    
    LineStringObjectExtensionGroup = property(__LineStringObjectExtensionGroup.value, __LineStringObjectExtensionGroup.set, None, None)

    
    # Element AbstractGeometrySimpleExtensionGroup ({http://www.opengis.net/kml/2.2}AbstractGeometrySimpleExtensionGroup) inherited from {http://www.opengis.net/kml/2.2}AbstractGeometryType
    
    # Element {http://www.opengis.net/kml/2.2}extrude uses Python identifier extrude
    __extrude = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'extrude'), 'extrude', '__httpwww_opengis_netkml2_2_LineStringType_httpwww_opengis_netkml2_2extrude', False)

    
    extrude = property(__extrude.value, __extrude.set, None, None)

    
    # Element ObjectSimpleExtensionGroup ({http://www.opengis.net/kml/2.2}ObjectSimpleExtensionGroup) inherited from {http://www.opengis.net/kml/2.2}AbstractObjectType
    
    # Attribute targetId inherited from {http://www.opengis.net/kml/2.2}AbstractObjectType
    
    # Attribute id inherited from {http://www.opengis.net/kml/2.2}AbstractObjectType

    _ElementMap = AbstractGeometryType._ElementMap.copy()
    _ElementMap.update({
        __coordinates.name() : __coordinates,
        __tessellate.name() : __tessellate,
        __LineStringSimpleExtensionGroup.name() : __LineStringSimpleExtensionGroup,
        __altitudeModeGroup.name() : __altitudeModeGroup,
        __LineStringObjectExtensionGroup.name() : __LineStringObjectExtensionGroup,
        __extrude.name() : __extrude
    })
    _AttributeMap = AbstractGeometryType._AttributeMap.copy()
    _AttributeMap.update({
        
    })
Namespace.addCategoryObject('typeBinding', u'LineStringType', LineStringType)


# Complex type KmlType with content type ELEMENT_ONLY
class KmlType (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'KmlType')
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {http://www.opengis.net/kml/2.2}AbstractFeatureGroup uses Python identifier AbstractFeatureGroup
    __AbstractFeatureGroup = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'AbstractFeatureGroup'), 'AbstractFeatureGroup', '__httpwww_opengis_netkml2_2_KmlType_httpwww_opengis_netkml2_2AbstractFeatureGroup', False)

    
    AbstractFeatureGroup = property(__AbstractFeatureGroup.value, __AbstractFeatureGroup.set, None, None)

    
    # Element {http://www.opengis.net/kml/2.2}KmlSimpleExtensionGroup uses Python identifier KmlSimpleExtensionGroup
    __KmlSimpleExtensionGroup = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'KmlSimpleExtensionGroup'), 'KmlSimpleExtensionGroup', '__httpwww_opengis_netkml2_2_KmlType_httpwww_opengis_netkml2_2KmlSimpleExtensionGroup', True)

    
    KmlSimpleExtensionGroup = property(__KmlSimpleExtensionGroup.value, __KmlSimpleExtensionGroup.set, None, None)

    
    # Element {http://www.opengis.net/kml/2.2}NetworkLinkControl uses Python identifier NetworkLinkControl
    __NetworkLinkControl = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'NetworkLinkControl'), 'NetworkLinkControl', '__httpwww_opengis_netkml2_2_KmlType_httpwww_opengis_netkml2_2NetworkLinkControl', False)

    
    NetworkLinkControl = property(__NetworkLinkControl.value, __NetworkLinkControl.set, None, None)

    
    # Element {http://www.opengis.net/kml/2.2}KmlObjectExtensionGroup uses Python identifier KmlObjectExtensionGroup
    __KmlObjectExtensionGroup = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'KmlObjectExtensionGroup'), 'KmlObjectExtensionGroup', '__httpwww_opengis_netkml2_2_KmlType_httpwww_opengis_netkml2_2KmlObjectExtensionGroup', True)

    
    KmlObjectExtensionGroup = property(__KmlObjectExtensionGroup.value, __KmlObjectExtensionGroup.set, None, None)

    
    # Attribute hint uses Python identifier hint
    __hint = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'hint'), 'hint', '__httpwww_opengis_netkml2_2_KmlType_hint', pyxb.binding.datatypes.string)
    
    hint = property(__hint.value, __hint.set, None, None)


    _ElementMap = {
        __AbstractFeatureGroup.name() : __AbstractFeatureGroup,
        __KmlSimpleExtensionGroup.name() : __KmlSimpleExtensionGroup,
        __NetworkLinkControl.name() : __NetworkLinkControl,
        __KmlObjectExtensionGroup.name() : __KmlObjectExtensionGroup
    }
    _AttributeMap = {
        __hint.name() : __hint
    }
Namespace.addCategoryObject('typeBinding', u'KmlType', KmlType)


# Complex type PolygonType with content type ELEMENT_ONLY
class PolygonType (AbstractGeometryType):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'PolygonType')
    # Base type is AbstractGeometryType
    
    # Element {http://www.opengis.net/kml/2.2}extrude uses Python identifier extrude
    __extrude = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'extrude'), 'extrude', '__httpwww_opengis_netkml2_2_PolygonType_httpwww_opengis_netkml2_2extrude', False)

    
    extrude = property(__extrude.value, __extrude.set, None, None)

    
    # Element AbstractGeometryObjectExtensionGroup ({http://www.opengis.net/kml/2.2}AbstractGeometryObjectExtensionGroup) inherited from {http://www.opengis.net/kml/2.2}AbstractGeometryType
    
    # Element {http://www.opengis.net/kml/2.2}PolygonObjectExtensionGroup uses Python identifier PolygonObjectExtensionGroup
    __PolygonObjectExtensionGroup = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'PolygonObjectExtensionGroup'), 'PolygonObjectExtensionGroup', '__httpwww_opengis_netkml2_2_PolygonType_httpwww_opengis_netkml2_2PolygonObjectExtensionGroup', True)

    
    PolygonObjectExtensionGroup = property(__PolygonObjectExtensionGroup.value, __PolygonObjectExtensionGroup.set, None, None)

    
    # Element {http://www.opengis.net/kml/2.2}tessellate uses Python identifier tessellate
    __tessellate = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'tessellate'), 'tessellate', '__httpwww_opengis_netkml2_2_PolygonType_httpwww_opengis_netkml2_2tessellate', False)

    
    tessellate = property(__tessellate.value, __tessellate.set, None, None)

    
    # Element {http://www.opengis.net/kml/2.2}innerBoundaryIs uses Python identifier innerBoundaryIs
    __innerBoundaryIs = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'innerBoundaryIs'), 'innerBoundaryIs', '__httpwww_opengis_netkml2_2_PolygonType_httpwww_opengis_netkml2_2innerBoundaryIs', True)

    
    innerBoundaryIs = property(__innerBoundaryIs.value, __innerBoundaryIs.set, None, None)

    
    # Element {http://www.opengis.net/kml/2.2}altitudeModeGroup uses Python identifier altitudeModeGroup
    __altitudeModeGroup = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'altitudeModeGroup'), 'altitudeModeGroup', '__httpwww_opengis_netkml2_2_PolygonType_httpwww_opengis_netkml2_2altitudeModeGroup', False)

    
    altitudeModeGroup = property(__altitudeModeGroup.value, __altitudeModeGroup.set, None, None)

    
    # Element AbstractGeometrySimpleExtensionGroup ({http://www.opengis.net/kml/2.2}AbstractGeometrySimpleExtensionGroup) inherited from {http://www.opengis.net/kml/2.2}AbstractGeometryType
    
    # Element {http://www.opengis.net/kml/2.2}PolygonSimpleExtensionGroup uses Python identifier PolygonSimpleExtensionGroup
    __PolygonSimpleExtensionGroup = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'PolygonSimpleExtensionGroup'), 'PolygonSimpleExtensionGroup', '__httpwww_opengis_netkml2_2_PolygonType_httpwww_opengis_netkml2_2PolygonSimpleExtensionGroup', True)

    
    PolygonSimpleExtensionGroup = property(__PolygonSimpleExtensionGroup.value, __PolygonSimpleExtensionGroup.set, None, None)

    
    # Element ObjectSimpleExtensionGroup ({http://www.opengis.net/kml/2.2}ObjectSimpleExtensionGroup) inherited from {http://www.opengis.net/kml/2.2}AbstractObjectType
    
    # Element {http://www.opengis.net/kml/2.2}outerBoundaryIs uses Python identifier outerBoundaryIs
    __outerBoundaryIs = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'outerBoundaryIs'), 'outerBoundaryIs', '__httpwww_opengis_netkml2_2_PolygonType_httpwww_opengis_netkml2_2outerBoundaryIs', False)

    
    outerBoundaryIs = property(__outerBoundaryIs.value, __outerBoundaryIs.set, None, None)

    
    # Attribute targetId inherited from {http://www.opengis.net/kml/2.2}AbstractObjectType
    
    # Attribute id inherited from {http://www.opengis.net/kml/2.2}AbstractObjectType

    _ElementMap = AbstractGeometryType._ElementMap.copy()
    _ElementMap.update({
        __extrude.name() : __extrude,
        __PolygonObjectExtensionGroup.name() : __PolygonObjectExtensionGroup,
        __tessellate.name() : __tessellate,
        __innerBoundaryIs.name() : __innerBoundaryIs,
        __altitudeModeGroup.name() : __altitudeModeGroup,
        __PolygonSimpleExtensionGroup.name() : __PolygonSimpleExtensionGroup,
        __outerBoundaryIs.name() : __outerBoundaryIs
    })
    _AttributeMap = AbstractGeometryType._AttributeMap.copy()
    _AttributeMap.update({
        
    })
Namespace.addCategoryObject('typeBinding', u'PolygonType', PolygonType)


# Complex type PhotoOverlayType with content type ELEMENT_ONLY
class PhotoOverlayType (AbstractOverlayType):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'PhotoOverlayType')
    # Base type is AbstractOverlayType
    
    # Element link ({http://www.w3.org/2005/Atom}link) inherited from {http://www.opengis.net/kml/2.2}AbstractFeatureType
    
    # Element AbstractStyleSelectorGroup ({http://www.opengis.net/kml/2.2}AbstractStyleSelectorGroup) inherited from {http://www.opengis.net/kml/2.2}AbstractFeatureType
    
    # Element {http://www.opengis.net/kml/2.2}PhotoOverlayObjectExtensionGroup uses Python identifier PhotoOverlayObjectExtensionGroup
    __PhotoOverlayObjectExtensionGroup = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'PhotoOverlayObjectExtensionGroup'), 'PhotoOverlayObjectExtensionGroup', '__httpwww_opengis_netkml2_2_PhotoOverlayType_httpwww_opengis_netkml2_2PhotoOverlayObjectExtensionGroup', True)

    
    PhotoOverlayObjectExtensionGroup = property(__PhotoOverlayObjectExtensionGroup.value, __PhotoOverlayObjectExtensionGroup.set, None, None)

    
    # Element address ({http://www.opengis.net/kml/2.2}address) inherited from {http://www.opengis.net/kml/2.2}AbstractFeatureType
    
    # Element Region ({http://www.opengis.net/kml/2.2}Region) inherited from {http://www.opengis.net/kml/2.2}AbstractFeatureType
    
    # Element AddressDetails ({urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}AddressDetails) inherited from {http://www.opengis.net/kml/2.2}AbstractFeatureType
    
    # Element AbstractTimePrimitiveGroup ({http://www.opengis.net/kml/2.2}AbstractTimePrimitiveGroup) inherited from {http://www.opengis.net/kml/2.2}AbstractFeatureType
    
    # Element phoneNumber ({http://www.opengis.net/kml/2.2}phoneNumber) inherited from {http://www.opengis.net/kml/2.2}AbstractFeatureType
    
    # Element Metadata ({http://www.opengis.net/kml/2.2}Metadata) inherited from {http://www.opengis.net/kml/2.2}AbstractFeatureType
    
    # Element visibility ({http://www.opengis.net/kml/2.2}visibility) inherited from {http://www.opengis.net/kml/2.2}AbstractFeatureType
    
    # Element ExtendedData ({http://www.opengis.net/kml/2.2}ExtendedData) inherited from {http://www.opengis.net/kml/2.2}AbstractFeatureType
    
    # Element color ({http://www.opengis.net/kml/2.2}color) inherited from {http://www.opengis.net/kml/2.2}AbstractOverlayType
    
    # Element Snippet ({http://www.opengis.net/kml/2.2}Snippet) inherited from {http://www.opengis.net/kml/2.2}AbstractFeatureType
    
    # Element author ({http://www.w3.org/2005/Atom}author) inherited from {http://www.opengis.net/kml/2.2}AbstractFeatureType
    
    # Element {http://www.opengis.net/kml/2.2}rotation uses Python identifier rotation
    __rotation = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'rotation'), 'rotation', '__httpwww_opengis_netkml2_2_PhotoOverlayType_httpwww_opengis_netkml2_2rotation', False)

    
    rotation = property(__rotation.value, __rotation.set, None, None)

    
    # Element AbstractFeatureObjectExtensionGroup ({http://www.opengis.net/kml/2.2}AbstractFeatureObjectExtensionGroup) inherited from {http://www.opengis.net/kml/2.2}AbstractFeatureType
    
    # Element {http://www.opengis.net/kml/2.2}ViewVolume uses Python identifier ViewVolume
    __ViewVolume = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'ViewVolume'), 'ViewVolume', '__httpwww_opengis_netkml2_2_PhotoOverlayType_httpwww_opengis_netkml2_2ViewVolume', False)

    
    ViewVolume = property(__ViewVolume.value, __ViewVolume.set, None, None)

    
    # Element name ({http://www.opengis.net/kml/2.2}name) inherited from {http://www.opengis.net/kml/2.2}AbstractFeatureType
    
    # Element drawOrder ({http://www.opengis.net/kml/2.2}drawOrder) inherited from {http://www.opengis.net/kml/2.2}AbstractOverlayType
    
    # Element {http://www.opengis.net/kml/2.2}ImagePyramid uses Python identifier ImagePyramid
    __ImagePyramid = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'ImagePyramid'), 'ImagePyramid', '__httpwww_opengis_netkml2_2_PhotoOverlayType_httpwww_opengis_netkml2_2ImagePyramid', False)

    
    ImagePyramid = property(__ImagePyramid.value, __ImagePyramid.set, None, None)

    
    # Element AbstractViewGroup ({http://www.opengis.net/kml/2.2}AbstractViewGroup) inherited from {http://www.opengis.net/kml/2.2}AbstractFeatureType
    
    # Element Icon ({http://www.opengis.net/kml/2.2}Icon) inherited from {http://www.opengis.net/kml/2.2}AbstractOverlayType
    
    # Element snippet ({http://www.opengis.net/kml/2.2}snippet) inherited from {http://www.opengis.net/kml/2.2}AbstractFeatureType
    
    # Element {http://www.opengis.net/kml/2.2}Point uses Python identifier Point
    __Point = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'Point'), 'Point', '__httpwww_opengis_netkml2_2_PhotoOverlayType_httpwww_opengis_netkml2_2Point', False)

    
    Point = property(__Point.value, __Point.set, None, None)

    
    # Element description ({http://www.opengis.net/kml/2.2}description) inherited from {http://www.opengis.net/kml/2.2}AbstractFeatureType
    
    # Element open ({http://www.opengis.net/kml/2.2}open) inherited from {http://www.opengis.net/kml/2.2}AbstractFeatureType
    
    # Element AbstractOverlaySimpleExtensionGroup ({http://www.opengis.net/kml/2.2}AbstractOverlaySimpleExtensionGroup) inherited from {http://www.opengis.net/kml/2.2}AbstractOverlayType
    
    # Element AbstractFeatureSimpleExtensionGroup ({http://www.opengis.net/kml/2.2}AbstractFeatureSimpleExtensionGroup) inherited from {http://www.opengis.net/kml/2.2}AbstractFeatureType
    
    # Element {http://www.opengis.net/kml/2.2}shape uses Python identifier shape
    __shape = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'shape'), 'shape', '__httpwww_opengis_netkml2_2_PhotoOverlayType_httpwww_opengis_netkml2_2shape', False)

    
    shape = property(__shape.value, __shape.set, None, None)

    
    # Element styleUrl ({http://www.opengis.net/kml/2.2}styleUrl) inherited from {http://www.opengis.net/kml/2.2}AbstractFeatureType
    
    # Element ObjectSimpleExtensionGroup ({http://www.opengis.net/kml/2.2}ObjectSimpleExtensionGroup) inherited from {http://www.opengis.net/kml/2.2}AbstractObjectType
    
    # Element AbstractOverlayObjectExtensionGroup ({http://www.opengis.net/kml/2.2}AbstractOverlayObjectExtensionGroup) inherited from {http://www.opengis.net/kml/2.2}AbstractOverlayType
    
    # Element {http://www.opengis.net/kml/2.2}PhotoOverlaySimpleExtensionGroup uses Python identifier PhotoOverlaySimpleExtensionGroup
    __PhotoOverlaySimpleExtensionGroup = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'PhotoOverlaySimpleExtensionGroup'), 'PhotoOverlaySimpleExtensionGroup', '__httpwww_opengis_netkml2_2_PhotoOverlayType_httpwww_opengis_netkml2_2PhotoOverlaySimpleExtensionGroup', True)

    
    PhotoOverlaySimpleExtensionGroup = property(__PhotoOverlaySimpleExtensionGroup.value, __PhotoOverlaySimpleExtensionGroup.set, None, None)

    
    # Attribute targetId inherited from {http://www.opengis.net/kml/2.2}AbstractObjectType
    
    # Attribute id inherited from {http://www.opengis.net/kml/2.2}AbstractObjectType

    _ElementMap = AbstractOverlayType._ElementMap.copy()
    _ElementMap.update({
        __PhotoOverlayObjectExtensionGroup.name() : __PhotoOverlayObjectExtensionGroup,
        __rotation.name() : __rotation,
        __ViewVolume.name() : __ViewVolume,
        __ImagePyramid.name() : __ImagePyramid,
        __Point.name() : __Point,
        __shape.name() : __shape,
        __PhotoOverlaySimpleExtensionGroup.name() : __PhotoOverlaySimpleExtensionGroup
    })
    _AttributeMap = AbstractOverlayType._AttributeMap.copy()
    _AttributeMap.update({
        
    })
Namespace.addCategoryObject('typeBinding', u'PhotoOverlayType', PhotoOverlayType)


# Complex type TimeStampType with content type ELEMENT_ONLY
class TimeStampType (AbstractTimePrimitiveType):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'TimeStampType')
    # Base type is AbstractTimePrimitiveType
    
    # Element {http://www.opengis.net/kml/2.2}TimeStampObjectExtensionGroup uses Python identifier TimeStampObjectExtensionGroup
    __TimeStampObjectExtensionGroup = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'TimeStampObjectExtensionGroup'), 'TimeStampObjectExtensionGroup', '__httpwww_opengis_netkml2_2_TimeStampType_httpwww_opengis_netkml2_2TimeStampObjectExtensionGroup', True)

    
    TimeStampObjectExtensionGroup = property(__TimeStampObjectExtensionGroup.value, __TimeStampObjectExtensionGroup.set, None, None)

    
    # Element ObjectSimpleExtensionGroup ({http://www.opengis.net/kml/2.2}ObjectSimpleExtensionGroup) inherited from {http://www.opengis.net/kml/2.2}AbstractObjectType
    
    # Element {http://www.opengis.net/kml/2.2}when uses Python identifier when
    __when = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'when'), 'when', '__httpwww_opengis_netkml2_2_TimeStampType_httpwww_opengis_netkml2_2when', False)

    
    when = property(__when.value, __when.set, None, None)

    
    # Element AbstractTimePrimitiveObjectExtensionGroup ({http://www.opengis.net/kml/2.2}AbstractTimePrimitiveObjectExtensionGroup) inherited from {http://www.opengis.net/kml/2.2}AbstractTimePrimitiveType
    
    # Element {http://www.opengis.net/kml/2.2}TimeStampSimpleExtensionGroup uses Python identifier TimeStampSimpleExtensionGroup
    __TimeStampSimpleExtensionGroup = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'TimeStampSimpleExtensionGroup'), 'TimeStampSimpleExtensionGroup', '__httpwww_opengis_netkml2_2_TimeStampType_httpwww_opengis_netkml2_2TimeStampSimpleExtensionGroup', True)

    
    TimeStampSimpleExtensionGroup = property(__TimeStampSimpleExtensionGroup.value, __TimeStampSimpleExtensionGroup.set, None, None)

    
    # Element AbstractTimePrimitiveSimpleExtensionGroup ({http://www.opengis.net/kml/2.2}AbstractTimePrimitiveSimpleExtensionGroup) inherited from {http://www.opengis.net/kml/2.2}AbstractTimePrimitiveType
    
    # Attribute targetId inherited from {http://www.opengis.net/kml/2.2}AbstractObjectType
    
    # Attribute id inherited from {http://www.opengis.net/kml/2.2}AbstractObjectType

    _ElementMap = AbstractTimePrimitiveType._ElementMap.copy()
    _ElementMap.update({
        __TimeStampObjectExtensionGroup.name() : __TimeStampObjectExtensionGroup,
        __when.name() : __when,
        __TimeStampSimpleExtensionGroup.name() : __TimeStampSimpleExtensionGroup
    })
    _AttributeMap = AbstractTimePrimitiveType._AttributeMap.copy()
    _AttributeMap.update({
        
    })
Namespace.addCategoryObject('typeBinding', u'TimeStampType', TimeStampType)


# Complex type ModelType with content type ELEMENT_ONLY
class ModelType (AbstractGeometryType):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'ModelType')
    # Base type is AbstractGeometryType
    
    # Element {http://www.opengis.net/kml/2.2}ModelObjectExtensionGroup uses Python identifier ModelObjectExtensionGroup
    __ModelObjectExtensionGroup = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'ModelObjectExtensionGroup'), 'ModelObjectExtensionGroup', '__httpwww_opengis_netkml2_2_ModelType_httpwww_opengis_netkml2_2ModelObjectExtensionGroup', True)

    
    ModelObjectExtensionGroup = property(__ModelObjectExtensionGroup.value, __ModelObjectExtensionGroup.set, None, None)

    
    # Element {http://www.opengis.net/kml/2.2}Orientation uses Python identifier Orientation
    __Orientation = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'Orientation'), 'Orientation', '__httpwww_opengis_netkml2_2_ModelType_httpwww_opengis_netkml2_2Orientation', False)

    
    Orientation = property(__Orientation.value, __Orientation.set, None, None)

    
    # Element {http://www.opengis.net/kml/2.2}ResourceMap uses Python identifier ResourceMap
    __ResourceMap = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'ResourceMap'), 'ResourceMap', '__httpwww_opengis_netkml2_2_ModelType_httpwww_opengis_netkml2_2ResourceMap', False)

    
    ResourceMap = property(__ResourceMap.value, __ResourceMap.set, None, None)

    
    # Element {http://www.opengis.net/kml/2.2}altitudeModeGroup uses Python identifier altitudeModeGroup
    __altitudeModeGroup = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'altitudeModeGroup'), 'altitudeModeGroup', '__httpwww_opengis_netkml2_2_ModelType_httpwww_opengis_netkml2_2altitudeModeGroup', False)

    
    altitudeModeGroup = property(__altitudeModeGroup.value, __altitudeModeGroup.set, None, None)

    
    # Element {http://www.opengis.net/kml/2.2}Scale uses Python identifier Scale
    __Scale = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'Scale'), 'Scale', '__httpwww_opengis_netkml2_2_ModelType_httpwww_opengis_netkml2_2Scale', False)

    
    Scale = property(__Scale.value, __Scale.set, None, None)

    
    # Element {http://www.opengis.net/kml/2.2}ModelSimpleExtensionGroup uses Python identifier ModelSimpleExtensionGroup
    __ModelSimpleExtensionGroup = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'ModelSimpleExtensionGroup'), 'ModelSimpleExtensionGroup', '__httpwww_opengis_netkml2_2_ModelType_httpwww_opengis_netkml2_2ModelSimpleExtensionGroup', True)

    
    ModelSimpleExtensionGroup = property(__ModelSimpleExtensionGroup.value, __ModelSimpleExtensionGroup.set, None, None)

    
    # Element AbstractGeometrySimpleExtensionGroup ({http://www.opengis.net/kml/2.2}AbstractGeometrySimpleExtensionGroup) inherited from {http://www.opengis.net/kml/2.2}AbstractGeometryType
    
    # Element {http://www.opengis.net/kml/2.2}Location uses Python identifier Location
    __Location = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'Location'), 'Location', '__httpwww_opengis_netkml2_2_ModelType_httpwww_opengis_netkml2_2Location', False)

    
    Location = property(__Location.value, __Location.set, None, None)

    
    # Element {http://www.opengis.net/kml/2.2}Link uses Python identifier Link
    __Link = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'Link'), 'Link', '__httpwww_opengis_netkml2_2_ModelType_httpwww_opengis_netkml2_2Link', False)

    
    Link = property(__Link.value, __Link.set, None, None)

    
    # Element ObjectSimpleExtensionGroup ({http://www.opengis.net/kml/2.2}ObjectSimpleExtensionGroup) inherited from {http://www.opengis.net/kml/2.2}AbstractObjectType
    
    # Element AbstractGeometryObjectExtensionGroup ({http://www.opengis.net/kml/2.2}AbstractGeometryObjectExtensionGroup) inherited from {http://www.opengis.net/kml/2.2}AbstractGeometryType
    
    # Attribute targetId inherited from {http://www.opengis.net/kml/2.2}AbstractObjectType
    
    # Attribute id inherited from {http://www.opengis.net/kml/2.2}AbstractObjectType

    _ElementMap = AbstractGeometryType._ElementMap.copy()
    _ElementMap.update({
        __ModelObjectExtensionGroup.name() : __ModelObjectExtensionGroup,
        __Orientation.name() : __Orientation,
        __ResourceMap.name() : __ResourceMap,
        __altitudeModeGroup.name() : __altitudeModeGroup,
        __Scale.name() : __Scale,
        __ModelSimpleExtensionGroup.name() : __ModelSimpleExtensionGroup,
        __Location.name() : __Location,
        __Link.name() : __Link
    })
    _AttributeMap = AbstractGeometryType._AttributeMap.copy()
    _AttributeMap.update({
        
    })
Namespace.addCategoryObject('typeBinding', u'ModelType', ModelType)


# Complex type CreateType with content type ELEMENT_ONLY
class CreateType (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'CreateType')
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {http://www.opengis.net/kml/2.2}AbstractContainerGroup uses Python identifier AbstractContainerGroup
    __AbstractContainerGroup = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'AbstractContainerGroup'), 'AbstractContainerGroup', '__httpwww_opengis_netkml2_2_CreateType_httpwww_opengis_netkml2_2AbstractContainerGroup', True)

    
    AbstractContainerGroup = property(__AbstractContainerGroup.value, __AbstractContainerGroup.set, None, None)


    _ElementMap = {
        __AbstractContainerGroup.name() : __AbstractContainerGroup
    }
    _AttributeMap = {
        
    }
Namespace.addCategoryObject('typeBinding', u'CreateType', CreateType)


# Complex type DeleteType with content type ELEMENT_ONLY
class DeleteType (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'DeleteType')
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {http://www.opengis.net/kml/2.2}AbstractFeatureGroup uses Python identifier AbstractFeatureGroup
    __AbstractFeatureGroup = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'AbstractFeatureGroup'), 'AbstractFeatureGroup', '__httpwww_opengis_netkml2_2_DeleteType_httpwww_opengis_netkml2_2AbstractFeatureGroup', True)

    
    AbstractFeatureGroup = property(__AbstractFeatureGroup.value, __AbstractFeatureGroup.set, None, None)


    _ElementMap = {
        __AbstractFeatureGroup.name() : __AbstractFeatureGroup
    }
    _AttributeMap = {
        
    }
Namespace.addCategoryObject('typeBinding', u'DeleteType', DeleteType)


# Complex type LookAtType with content type ELEMENT_ONLY
class LookAtType (AbstractViewType):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'LookAtType')
    # Base type is AbstractViewType
    
    # Element {http://www.opengis.net/kml/2.2}tilt uses Python identifier tilt
    __tilt = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'tilt'), 'tilt', '__httpwww_opengis_netkml2_2_LookAtType_httpwww_opengis_netkml2_2tilt', False)

    
    tilt = property(__tilt.value, __tilt.set, None, None)

    
    # Element AbstractViewSimpleExtensionGroup ({http://www.opengis.net/kml/2.2}AbstractViewSimpleExtensionGroup) inherited from {http://www.opengis.net/kml/2.2}AbstractViewType
    
    # Element {http://www.opengis.net/kml/2.2}altitude uses Python identifier altitude
    __altitude = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'altitude'), 'altitude', '__httpwww_opengis_netkml2_2_LookAtType_httpwww_opengis_netkml2_2altitude', False)

    
    altitude = property(__altitude.value, __altitude.set, None, None)

    
    # Element {http://www.opengis.net/kml/2.2}range uses Python identifier range
    __range = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'range'), 'range', '__httpwww_opengis_netkml2_2_LookAtType_httpwww_opengis_netkml2_2range', False)

    
    range = property(__range.value, __range.set, None, None)

    
    # Element AbstractViewObjectExtensionGroup ({http://www.opengis.net/kml/2.2}AbstractViewObjectExtensionGroup) inherited from {http://www.opengis.net/kml/2.2}AbstractViewType
    
    # Element {http://www.opengis.net/kml/2.2}longitude uses Python identifier longitude
    __longitude = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'longitude'), 'longitude', '__httpwww_opengis_netkml2_2_LookAtType_httpwww_opengis_netkml2_2longitude', False)

    
    longitude = property(__longitude.value, __longitude.set, None, None)

    
    # Element {http://www.opengis.net/kml/2.2}LookAtObjectExtensionGroup uses Python identifier LookAtObjectExtensionGroup
    __LookAtObjectExtensionGroup = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'LookAtObjectExtensionGroup'), 'LookAtObjectExtensionGroup', '__httpwww_opengis_netkml2_2_LookAtType_httpwww_opengis_netkml2_2LookAtObjectExtensionGroup', True)

    
    LookAtObjectExtensionGroup = property(__LookAtObjectExtensionGroup.value, __LookAtObjectExtensionGroup.set, None, None)

    
    # Element {http://www.opengis.net/kml/2.2}LookAtSimpleExtensionGroup uses Python identifier LookAtSimpleExtensionGroup
    __LookAtSimpleExtensionGroup = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'LookAtSimpleExtensionGroup'), 'LookAtSimpleExtensionGroup', '__httpwww_opengis_netkml2_2_LookAtType_httpwww_opengis_netkml2_2LookAtSimpleExtensionGroup', True)

    
    LookAtSimpleExtensionGroup = property(__LookAtSimpleExtensionGroup.value, __LookAtSimpleExtensionGroup.set, None, None)

    
    # Element {http://www.opengis.net/kml/2.2}altitudeModeGroup uses Python identifier altitudeModeGroup
    __altitudeModeGroup = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'altitudeModeGroup'), 'altitudeModeGroup', '__httpwww_opengis_netkml2_2_LookAtType_httpwww_opengis_netkml2_2altitudeModeGroup', False)

    
    altitudeModeGroup = property(__altitudeModeGroup.value, __altitudeModeGroup.set, None, None)

    
    # Element {http://www.opengis.net/kml/2.2}latitude uses Python identifier latitude
    __latitude = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'latitude'), 'latitude', '__httpwww_opengis_netkml2_2_LookAtType_httpwww_opengis_netkml2_2latitude', False)

    
    latitude = property(__latitude.value, __latitude.set, None, None)

    
    # Element ObjectSimpleExtensionGroup ({http://www.opengis.net/kml/2.2}ObjectSimpleExtensionGroup) inherited from {http://www.opengis.net/kml/2.2}AbstractObjectType
    
    # Element {http://www.opengis.net/kml/2.2}heading uses Python identifier heading
    __heading = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'heading'), 'heading', '__httpwww_opengis_netkml2_2_LookAtType_httpwww_opengis_netkml2_2heading', False)

    
    heading = property(__heading.value, __heading.set, None, None)

    
    # Attribute targetId inherited from {http://www.opengis.net/kml/2.2}AbstractObjectType
    
    # Attribute id inherited from {http://www.opengis.net/kml/2.2}AbstractObjectType

    _ElementMap = AbstractViewType._ElementMap.copy()
    _ElementMap.update({
        __tilt.name() : __tilt,
        __altitude.name() : __altitude,
        __range.name() : __range,
        __longitude.name() : __longitude,
        __LookAtObjectExtensionGroup.name() : __LookAtObjectExtensionGroup,
        __LookAtSimpleExtensionGroup.name() : __LookAtSimpleExtensionGroup,
        __altitudeModeGroup.name() : __altitudeModeGroup,
        __latitude.name() : __latitude,
        __heading.name() : __heading
    })
    _AttributeMap = AbstractViewType._AttributeMap.copy()
    _AttributeMap.update({
        
    })
Namespace.addCategoryObject('typeBinding', u'LookAtType', LookAtType)


# Complex type BalloonStyleType with content type ELEMENT_ONLY
class BalloonStyleType (AbstractSubStyleType):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'BalloonStyleType')
    # Base type is AbstractSubStyleType
    
    # Element {http://www.opengis.net/kml/2.2}BalloonStyleSimpleExtensionGroup uses Python identifier BalloonStyleSimpleExtensionGroup
    __BalloonStyleSimpleExtensionGroup = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'BalloonStyleSimpleExtensionGroup'), 'BalloonStyleSimpleExtensionGroup', '__httpwww_opengis_netkml2_2_BalloonStyleType_httpwww_opengis_netkml2_2BalloonStyleSimpleExtensionGroup', True)

    
    BalloonStyleSimpleExtensionGroup = property(__BalloonStyleSimpleExtensionGroup.value, __BalloonStyleSimpleExtensionGroup.set, None, None)

    
    # Element {http://www.opengis.net/kml/2.2}color uses Python identifier color
    __color = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'color'), 'color', '__httpwww_opengis_netkml2_2_BalloonStyleType_httpwww_opengis_netkml2_2color', False)

    
    color = property(__color.value, __color.set, None, None)

    
    # Element {http://www.opengis.net/kml/2.2}text uses Python identifier text
    __text = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'text'), 'text', '__httpwww_opengis_netkml2_2_BalloonStyleType_httpwww_opengis_netkml2_2text', False)

    
    text = property(__text.value, __text.set, None, None)

    
    # Element AbstractSubStyleSimpleExtensionGroup ({http://www.opengis.net/kml/2.2}AbstractSubStyleSimpleExtensionGroup) inherited from {http://www.opengis.net/kml/2.2}AbstractSubStyleType
    
    # Element {http://www.opengis.net/kml/2.2}BalloonStyleObjectExtensionGroup uses Python identifier BalloonStyleObjectExtensionGroup
    __BalloonStyleObjectExtensionGroup = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'BalloonStyleObjectExtensionGroup'), 'BalloonStyleObjectExtensionGroup', '__httpwww_opengis_netkml2_2_BalloonStyleType_httpwww_opengis_netkml2_2BalloonStyleObjectExtensionGroup', True)

    
    BalloonStyleObjectExtensionGroup = property(__BalloonStyleObjectExtensionGroup.value, __BalloonStyleObjectExtensionGroup.set, None, None)

    
    # Element {http://www.opengis.net/kml/2.2}bgColor uses Python identifier bgColor
    __bgColor = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'bgColor'), 'bgColor', '__httpwww_opengis_netkml2_2_BalloonStyleType_httpwww_opengis_netkml2_2bgColor', False)

    
    bgColor = property(__bgColor.value, __bgColor.set, None, None)

    
    # Element {http://www.opengis.net/kml/2.2}displayMode uses Python identifier displayMode
    __displayMode = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'displayMode'), 'displayMode', '__httpwww_opengis_netkml2_2_BalloonStyleType_httpwww_opengis_netkml2_2displayMode', False)

    
    displayMode = property(__displayMode.value, __displayMode.set, None, None)

    
    # Element {http://www.opengis.net/kml/2.2}textColor uses Python identifier textColor
    __textColor = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'textColor'), 'textColor', '__httpwww_opengis_netkml2_2_BalloonStyleType_httpwww_opengis_netkml2_2textColor', False)

    
    textColor = property(__textColor.value, __textColor.set, None, None)

    
    # Element AbstractSubStyleObjectExtensionGroup ({http://www.opengis.net/kml/2.2}AbstractSubStyleObjectExtensionGroup) inherited from {http://www.opengis.net/kml/2.2}AbstractSubStyleType
    
    # Element ObjectSimpleExtensionGroup ({http://www.opengis.net/kml/2.2}ObjectSimpleExtensionGroup) inherited from {http://www.opengis.net/kml/2.2}AbstractObjectType
    
    # Attribute targetId inherited from {http://www.opengis.net/kml/2.2}AbstractObjectType
    
    # Attribute id inherited from {http://www.opengis.net/kml/2.2}AbstractObjectType

    _ElementMap = AbstractSubStyleType._ElementMap.copy()
    _ElementMap.update({
        __BalloonStyleSimpleExtensionGroup.name() : __BalloonStyleSimpleExtensionGroup,
        __color.name() : __color,
        __text.name() : __text,
        __BalloonStyleObjectExtensionGroup.name() : __BalloonStyleObjectExtensionGroup,
        __bgColor.name() : __bgColor,
        __displayMode.name() : __displayMode,
        __textColor.name() : __textColor
    })
    _AttributeMap = AbstractSubStyleType._AttributeMap.copy()
    _AttributeMap.update({
        
    })
Namespace.addCategoryObject('typeBinding', u'BalloonStyleType', BalloonStyleType)


# Complex type ListStyleType with content type ELEMENT_ONLY
class ListStyleType (AbstractSubStyleType):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'ListStyleType')
    # Base type is AbstractSubStyleType
    
    # Element {http://www.opengis.net/kml/2.2}listItemType uses Python identifier listItemType
    __listItemType = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'listItemType'), 'listItemType', '__httpwww_opengis_netkml2_2_ListStyleType_httpwww_opengis_netkml2_2listItemType', False)

    
    listItemType = property(__listItemType.value, __listItemType.set, None, None)

    
    # Element {http://www.opengis.net/kml/2.2}maxSnippetLines uses Python identifier maxSnippetLines
    __maxSnippetLines = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'maxSnippetLines'), 'maxSnippetLines', '__httpwww_opengis_netkml2_2_ListStyleType_httpwww_opengis_netkml2_2maxSnippetLines', False)

    
    maxSnippetLines = property(__maxSnippetLines.value, __maxSnippetLines.set, None, None)

    
    # Element ObjectSimpleExtensionGroup ({http://www.opengis.net/kml/2.2}ObjectSimpleExtensionGroup) inherited from {http://www.opengis.net/kml/2.2}AbstractObjectType
    
    # Element {http://www.opengis.net/kml/2.2}bgColor uses Python identifier bgColor
    __bgColor = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'bgColor'), 'bgColor', '__httpwww_opengis_netkml2_2_ListStyleType_httpwww_opengis_netkml2_2bgColor', False)

    
    bgColor = property(__bgColor.value, __bgColor.set, None, None)

    
    # Element AbstractSubStyleSimpleExtensionGroup ({http://www.opengis.net/kml/2.2}AbstractSubStyleSimpleExtensionGroup) inherited from {http://www.opengis.net/kml/2.2}AbstractSubStyleType
    
    # Element {http://www.opengis.net/kml/2.2}ListStyleSimpleExtensionGroup uses Python identifier ListStyleSimpleExtensionGroup
    __ListStyleSimpleExtensionGroup = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'ListStyleSimpleExtensionGroup'), 'ListStyleSimpleExtensionGroup', '__httpwww_opengis_netkml2_2_ListStyleType_httpwww_opengis_netkml2_2ListStyleSimpleExtensionGroup', True)

    
    ListStyleSimpleExtensionGroup = property(__ListStyleSimpleExtensionGroup.value, __ListStyleSimpleExtensionGroup.set, None, None)

    
    # Element {http://www.opengis.net/kml/2.2}ItemIcon uses Python identifier ItemIcon
    __ItemIcon = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'ItemIcon'), 'ItemIcon', '__httpwww_opengis_netkml2_2_ListStyleType_httpwww_opengis_netkml2_2ItemIcon', True)

    
    ItemIcon = property(__ItemIcon.value, __ItemIcon.set, None, None)

    
    # Element AbstractSubStyleObjectExtensionGroup ({http://www.opengis.net/kml/2.2}AbstractSubStyleObjectExtensionGroup) inherited from {http://www.opengis.net/kml/2.2}AbstractSubStyleType
    
    # Element {http://www.opengis.net/kml/2.2}ListStyleObjectExtensionGroup uses Python identifier ListStyleObjectExtensionGroup
    __ListStyleObjectExtensionGroup = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'ListStyleObjectExtensionGroup'), 'ListStyleObjectExtensionGroup', '__httpwww_opengis_netkml2_2_ListStyleType_httpwww_opengis_netkml2_2ListStyleObjectExtensionGroup', True)

    
    ListStyleObjectExtensionGroup = property(__ListStyleObjectExtensionGroup.value, __ListStyleObjectExtensionGroup.set, None, None)

    
    # Attribute targetId inherited from {http://www.opengis.net/kml/2.2}AbstractObjectType
    
    # Attribute id inherited from {http://www.opengis.net/kml/2.2}AbstractObjectType

    _ElementMap = AbstractSubStyleType._ElementMap.copy()
    _ElementMap.update({
        __listItemType.name() : __listItemType,
        __maxSnippetLines.name() : __maxSnippetLines,
        __bgColor.name() : __bgColor,
        __ListStyleSimpleExtensionGroup.name() : __ListStyleSimpleExtensionGroup,
        __ItemIcon.name() : __ItemIcon,
        __ListStyleObjectExtensionGroup.name() : __ListStyleObjectExtensionGroup
    })
    _AttributeMap = AbstractSubStyleType._AttributeMap.copy()
    _AttributeMap.update({
        
    })
Namespace.addCategoryObject('typeBinding', u'ListStyleType', ListStyleType)


# Complex type ScreenOverlayType with content type ELEMENT_ONLY
class ScreenOverlayType (AbstractOverlayType):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'ScreenOverlayType')
    # Base type is AbstractOverlayType
    
    # Element link ({http://www.w3.org/2005/Atom}link) inherited from {http://www.opengis.net/kml/2.2}AbstractFeatureType
    
    # Element {http://www.opengis.net/kml/2.2}ScreenOverlaySimpleExtensionGroup uses Python identifier ScreenOverlaySimpleExtensionGroup
    __ScreenOverlaySimpleExtensionGroup = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'ScreenOverlaySimpleExtensionGroup'), 'ScreenOverlaySimpleExtensionGroup', '__httpwww_opengis_netkml2_2_ScreenOverlayType_httpwww_opengis_netkml2_2ScreenOverlaySimpleExtensionGroup', True)

    
    ScreenOverlaySimpleExtensionGroup = property(__ScreenOverlaySimpleExtensionGroup.value, __ScreenOverlaySimpleExtensionGroup.set, None, None)

    
    # Element styleUrl ({http://www.opengis.net/kml/2.2}styleUrl) inherited from {http://www.opengis.net/kml/2.2}AbstractFeatureType
    
    # Element address ({http://www.opengis.net/kml/2.2}address) inherited from {http://www.opengis.net/kml/2.2}AbstractFeatureType
    
    # Element {http://www.opengis.net/kml/2.2}ScreenOverlayObjectExtensionGroup uses Python identifier ScreenOverlayObjectExtensionGroup
    __ScreenOverlayObjectExtensionGroup = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'ScreenOverlayObjectExtensionGroup'), 'ScreenOverlayObjectExtensionGroup', '__httpwww_opengis_netkml2_2_ScreenOverlayType_httpwww_opengis_netkml2_2ScreenOverlayObjectExtensionGroup', True)

    
    ScreenOverlayObjectExtensionGroup = property(__ScreenOverlayObjectExtensionGroup.value, __ScreenOverlayObjectExtensionGroup.set, None, None)

    
    # Element AddressDetails ({urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}AddressDetails) inherited from {http://www.opengis.net/kml/2.2}AbstractFeatureType
    
    # Element AbstractStyleSelectorGroup ({http://www.opengis.net/kml/2.2}AbstractStyleSelectorGroup) inherited from {http://www.opengis.net/kml/2.2}AbstractFeatureType
    
    # Element phoneNumber ({http://www.opengis.net/kml/2.2}phoneNumber) inherited from {http://www.opengis.net/kml/2.2}AbstractFeatureType
    
    # Element Metadata ({http://www.opengis.net/kml/2.2}Metadata) inherited from {http://www.opengis.net/kml/2.2}AbstractFeatureType
    
    # Element visibility ({http://www.opengis.net/kml/2.2}visibility) inherited from {http://www.opengis.net/kml/2.2}AbstractFeatureType
    
    # Element ExtendedData ({http://www.opengis.net/kml/2.2}ExtendedData) inherited from {http://www.opengis.net/kml/2.2}AbstractFeatureType
    
    # Element color ({http://www.opengis.net/kml/2.2}color) inherited from {http://www.opengis.net/kml/2.2}AbstractOverlayType
    
    # Element AbstractViewGroup ({http://www.opengis.net/kml/2.2}AbstractViewGroup) inherited from {http://www.opengis.net/kml/2.2}AbstractFeatureType
    
    # Element AbstractFeatureSimpleExtensionGroup ({http://www.opengis.net/kml/2.2}AbstractFeatureSimpleExtensionGroup) inherited from {http://www.opengis.net/kml/2.2}AbstractFeatureType
    
    # Element {http://www.opengis.net/kml/2.2}rotation uses Python identifier rotation
    __rotation = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'rotation'), 'rotation', '__httpwww_opengis_netkml2_2_ScreenOverlayType_httpwww_opengis_netkml2_2rotation', False)

    
    rotation = property(__rotation.value, __rotation.set, None, None)

    
    # Element {http://www.opengis.net/kml/2.2}overlayXY uses Python identifier overlayXY
    __overlayXY = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'overlayXY'), 'overlayXY', '__httpwww_opengis_netkml2_2_ScreenOverlayType_httpwww_opengis_netkml2_2overlayXY', False)

    
    overlayXY = property(__overlayXY.value, __overlayXY.set, None, None)

    
    # Element AbstractFeatureObjectExtensionGroup ({http://www.opengis.net/kml/2.2}AbstractFeatureObjectExtensionGroup) inherited from {http://www.opengis.net/kml/2.2}AbstractFeatureType
    
    # Element name ({http://www.opengis.net/kml/2.2}name) inherited from {http://www.opengis.net/kml/2.2}AbstractFeatureType
    
    # Element {http://www.opengis.net/kml/2.2}screenXY uses Python identifier screenXY
    __screenXY = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'screenXY'), 'screenXY', '__httpwww_opengis_netkml2_2_ScreenOverlayType_httpwww_opengis_netkml2_2screenXY', False)

    
    screenXY = property(__screenXY.value, __screenXY.set, None, None)

    
    # Element description ({http://www.opengis.net/kml/2.2}description) inherited from {http://www.opengis.net/kml/2.2}AbstractFeatureType
    
    # Element drawOrder ({http://www.opengis.net/kml/2.2}drawOrder) inherited from {http://www.opengis.net/kml/2.2}AbstractOverlayType
    
    # Element {http://www.opengis.net/kml/2.2}rotationXY uses Python identifier rotationXY
    __rotationXY = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'rotationXY'), 'rotationXY', '__httpwww_opengis_netkml2_2_ScreenOverlayType_httpwww_opengis_netkml2_2rotationXY', False)

    
    rotationXY = property(__rotationXY.value, __rotationXY.set, None, None)

    
    # Element ObjectSimpleExtensionGroup ({http://www.opengis.net/kml/2.2}ObjectSimpleExtensionGroup) inherited from {http://www.opengis.net/kml/2.2}AbstractObjectType
    
    # Element Icon ({http://www.opengis.net/kml/2.2}Icon) inherited from {http://www.opengis.net/kml/2.2}AbstractOverlayType
    
    # Element snippet ({http://www.opengis.net/kml/2.2}snippet) inherited from {http://www.opengis.net/kml/2.2}AbstractFeatureType
    
    # Element Region ({http://www.opengis.net/kml/2.2}Region) inherited from {http://www.opengis.net/kml/2.2}AbstractFeatureType
    
    # Element open ({http://www.opengis.net/kml/2.2}open) inherited from {http://www.opengis.net/kml/2.2}AbstractFeatureType
    
    # Element AbstractOverlaySimpleExtensionGroup ({http://www.opengis.net/kml/2.2}AbstractOverlaySimpleExtensionGroup) inherited from {http://www.opengis.net/kml/2.2}AbstractOverlayType
    
    # Element Snippet ({http://www.opengis.net/kml/2.2}Snippet) inherited from {http://www.opengis.net/kml/2.2}AbstractFeatureType
    
    # Element {http://www.opengis.net/kml/2.2}size uses Python identifier size
    __size = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'size'), 'size', '__httpwww_opengis_netkml2_2_ScreenOverlayType_httpwww_opengis_netkml2_2size', False)

    
    size = property(__size.value, __size.set, None, None)

    
    # Element author ({http://www.w3.org/2005/Atom}author) inherited from {http://www.opengis.net/kml/2.2}AbstractFeatureType
    
    # Element AbstractTimePrimitiveGroup ({http://www.opengis.net/kml/2.2}AbstractTimePrimitiveGroup) inherited from {http://www.opengis.net/kml/2.2}AbstractFeatureType
    
    # Element AbstractOverlayObjectExtensionGroup ({http://www.opengis.net/kml/2.2}AbstractOverlayObjectExtensionGroup) inherited from {http://www.opengis.net/kml/2.2}AbstractOverlayType
    
    # Attribute targetId inherited from {http://www.opengis.net/kml/2.2}AbstractObjectType
    
    # Attribute id inherited from {http://www.opengis.net/kml/2.2}AbstractObjectType

    _ElementMap = AbstractOverlayType._ElementMap.copy()
    _ElementMap.update({
        __ScreenOverlaySimpleExtensionGroup.name() : __ScreenOverlaySimpleExtensionGroup,
        __ScreenOverlayObjectExtensionGroup.name() : __ScreenOverlayObjectExtensionGroup,
        __rotation.name() : __rotation,
        __overlayXY.name() : __overlayXY,
        __screenXY.name() : __screenXY,
        __rotationXY.name() : __rotationXY,
        __size.name() : __size
    })
    _AttributeMap = AbstractOverlayType._AttributeMap.copy()
    _AttributeMap.update({
        
    })
Namespace.addCategoryObject('typeBinding', u'ScreenOverlayType', ScreenOverlayType)


# Complex type RegionType with content type ELEMENT_ONLY
class RegionType (AbstractObjectType):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'RegionType')
    # Base type is AbstractObjectType
    
    # Element {http://www.opengis.net/kml/2.2}Lod uses Python identifier Lod
    __Lod = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'Lod'), 'Lod', '__httpwww_opengis_netkml2_2_RegionType_httpwww_opengis_netkml2_2Lod', False)

    
    Lod = property(__Lod.value, __Lod.set, None, None)

    
    # Element ObjectSimpleExtensionGroup ({http://www.opengis.net/kml/2.2}ObjectSimpleExtensionGroup) inherited from {http://www.opengis.net/kml/2.2}AbstractObjectType
    
    # Element {http://www.opengis.net/kml/2.2}RegionSimpleExtensionGroup uses Python identifier RegionSimpleExtensionGroup
    __RegionSimpleExtensionGroup = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'RegionSimpleExtensionGroup'), 'RegionSimpleExtensionGroup', '__httpwww_opengis_netkml2_2_RegionType_httpwww_opengis_netkml2_2RegionSimpleExtensionGroup', True)

    
    RegionSimpleExtensionGroup = property(__RegionSimpleExtensionGroup.value, __RegionSimpleExtensionGroup.set, None, None)

    
    # Element {http://www.opengis.net/kml/2.2}RegionObjectExtensionGroup uses Python identifier RegionObjectExtensionGroup
    __RegionObjectExtensionGroup = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'RegionObjectExtensionGroup'), 'RegionObjectExtensionGroup', '__httpwww_opengis_netkml2_2_RegionType_httpwww_opengis_netkml2_2RegionObjectExtensionGroup', True)

    
    RegionObjectExtensionGroup = property(__RegionObjectExtensionGroup.value, __RegionObjectExtensionGroup.set, None, None)

    
    # Element {http://www.opengis.net/kml/2.2}LatLonAltBox uses Python identifier LatLonAltBox
    __LatLonAltBox = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'LatLonAltBox'), 'LatLonAltBox', '__httpwww_opengis_netkml2_2_RegionType_httpwww_opengis_netkml2_2LatLonAltBox', False)

    
    LatLonAltBox = property(__LatLonAltBox.value, __LatLonAltBox.set, None, None)

    
    # Attribute targetId inherited from {http://www.opengis.net/kml/2.2}AbstractObjectType
    
    # Attribute id inherited from {http://www.opengis.net/kml/2.2}AbstractObjectType

    _ElementMap = AbstractObjectType._ElementMap.copy()
    _ElementMap.update({
        __Lod.name() : __Lod,
        __RegionSimpleExtensionGroup.name() : __RegionSimpleExtensionGroup,
        __RegionObjectExtensionGroup.name() : __RegionObjectExtensionGroup,
        __LatLonAltBox.name() : __LatLonAltBox
    })
    _AttributeMap = AbstractObjectType._AttributeMap.copy()
    _AttributeMap.update({
        
    })
Namespace.addCategoryObject('typeBinding', u'RegionType', RegionType)


# Complex type LatLonAltBoxType with content type ELEMENT_ONLY
class LatLonAltBoxType (AbstractLatLonBoxType):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'LatLonAltBoxType')
    # Base type is AbstractLatLonBoxType
    
    # Element AbstractLatLonBoxSimpleExtensionGroup ({http://www.opengis.net/kml/2.2}AbstractLatLonBoxSimpleExtensionGroup) inherited from {http://www.opengis.net/kml/2.2}AbstractLatLonBoxType
    
    # Element AbstractLatLonBoxObjectExtensionGroup ({http://www.opengis.net/kml/2.2}AbstractLatLonBoxObjectExtensionGroup) inherited from {http://www.opengis.net/kml/2.2}AbstractLatLonBoxType
    
    # Element ObjectSimpleExtensionGroup ({http://www.opengis.net/kml/2.2}ObjectSimpleExtensionGroup) inherited from {http://www.opengis.net/kml/2.2}AbstractObjectType
    
    # Element {http://www.opengis.net/kml/2.2}minAltitude uses Python identifier minAltitude
    __minAltitude = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'minAltitude'), 'minAltitude', '__httpwww_opengis_netkml2_2_LatLonAltBoxType_httpwww_opengis_netkml2_2minAltitude', False)

    
    minAltitude = property(__minAltitude.value, __minAltitude.set, None, None)

    
    # Element north ({http://www.opengis.net/kml/2.2}north) inherited from {http://www.opengis.net/kml/2.2}AbstractLatLonBoxType
    
    # Element {http://www.opengis.net/kml/2.2}LatLonAltBoxSimpleExtensionGroup uses Python identifier LatLonAltBoxSimpleExtensionGroup
    __LatLonAltBoxSimpleExtensionGroup = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'LatLonAltBoxSimpleExtensionGroup'), 'LatLonAltBoxSimpleExtensionGroup', '__httpwww_opengis_netkml2_2_LatLonAltBoxType_httpwww_opengis_netkml2_2LatLonAltBoxSimpleExtensionGroup', True)

    
    LatLonAltBoxSimpleExtensionGroup = property(__LatLonAltBoxSimpleExtensionGroup.value, __LatLonAltBoxSimpleExtensionGroup.set, None, None)

    
    # Element east ({http://www.opengis.net/kml/2.2}east) inherited from {http://www.opengis.net/kml/2.2}AbstractLatLonBoxType
    
    # Element south ({http://www.opengis.net/kml/2.2}south) inherited from {http://www.opengis.net/kml/2.2}AbstractLatLonBoxType
    
    # Element west ({http://www.opengis.net/kml/2.2}west) inherited from {http://www.opengis.net/kml/2.2}AbstractLatLonBoxType
    
    # Element {http://www.opengis.net/kml/2.2}maxAltitude uses Python identifier maxAltitude
    __maxAltitude = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'maxAltitude'), 'maxAltitude', '__httpwww_opengis_netkml2_2_LatLonAltBoxType_httpwww_opengis_netkml2_2maxAltitude', False)

    
    maxAltitude = property(__maxAltitude.value, __maxAltitude.set, None, None)

    
    # Element {http://www.opengis.net/kml/2.2}LatLonAltBoxObjectExtensionGroup uses Python identifier LatLonAltBoxObjectExtensionGroup
    __LatLonAltBoxObjectExtensionGroup = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'LatLonAltBoxObjectExtensionGroup'), 'LatLonAltBoxObjectExtensionGroup', '__httpwww_opengis_netkml2_2_LatLonAltBoxType_httpwww_opengis_netkml2_2LatLonAltBoxObjectExtensionGroup', True)

    
    LatLonAltBoxObjectExtensionGroup = property(__LatLonAltBoxObjectExtensionGroup.value, __LatLonAltBoxObjectExtensionGroup.set, None, None)

    
    # Element {http://www.opengis.net/kml/2.2}altitudeModeGroup uses Python identifier altitudeModeGroup
    __altitudeModeGroup = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'altitudeModeGroup'), 'altitudeModeGroup', '__httpwww_opengis_netkml2_2_LatLonAltBoxType_httpwww_opengis_netkml2_2altitudeModeGroup', False)

    
    altitudeModeGroup = property(__altitudeModeGroup.value, __altitudeModeGroup.set, None, None)

    
    # Attribute targetId inherited from {http://www.opengis.net/kml/2.2}AbstractObjectType
    
    # Attribute id inherited from {http://www.opengis.net/kml/2.2}AbstractObjectType

    _ElementMap = AbstractLatLonBoxType._ElementMap.copy()
    _ElementMap.update({
        __minAltitude.name() : __minAltitude,
        __LatLonAltBoxSimpleExtensionGroup.name() : __LatLonAltBoxSimpleExtensionGroup,
        __maxAltitude.name() : __maxAltitude,
        __LatLonAltBoxObjectExtensionGroup.name() : __LatLonAltBoxObjectExtensionGroup,
        __altitudeModeGroup.name() : __altitudeModeGroup
    })
    _AttributeMap = AbstractLatLonBoxType._AttributeMap.copy()
    _AttributeMap.update({
        
    })
Namespace.addCategoryObject('typeBinding', u'LatLonAltBoxType', LatLonAltBoxType)


# Complex type FolderType with content type ELEMENT_ONLY
class FolderType (AbstractContainerType):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'FolderType')
    # Base type is AbstractContainerType
    
    # Element link ({http://www.w3.org/2005/Atom}link) inherited from {http://www.opengis.net/kml/2.2}AbstractFeatureType
    
    # Element AbstractStyleSelectorGroup ({http://www.opengis.net/kml/2.2}AbstractStyleSelectorGroup) inherited from {http://www.opengis.net/kml/2.2}AbstractFeatureType
    
    # Element address ({http://www.opengis.net/kml/2.2}address) inherited from {http://www.opengis.net/kml/2.2}AbstractFeatureType
    
    # Element Region ({http://www.opengis.net/kml/2.2}Region) inherited from {http://www.opengis.net/kml/2.2}AbstractFeatureType
    
    # Element AddressDetails ({urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}AddressDetails) inherited from {http://www.opengis.net/kml/2.2}AbstractFeatureType
    
    # Element phoneNumber ({http://www.opengis.net/kml/2.2}phoneNumber) inherited from {http://www.opengis.net/kml/2.2}AbstractFeatureType
    
    # Element Metadata ({http://www.opengis.net/kml/2.2}Metadata) inherited from {http://www.opengis.net/kml/2.2}AbstractFeatureType
    
    # Element AbstractViewGroup ({http://www.opengis.net/kml/2.2}AbstractViewGroup) inherited from {http://www.opengis.net/kml/2.2}AbstractFeatureType
    
    # Element ExtendedData ({http://www.opengis.net/kml/2.2}ExtendedData) inherited from {http://www.opengis.net/kml/2.2}AbstractFeatureType
    
    # Element snippet ({http://www.opengis.net/kml/2.2}snippet) inherited from {http://www.opengis.net/kml/2.2}AbstractFeatureType
    
    # Element AbstractFeatureSimpleExtensionGroup ({http://www.opengis.net/kml/2.2}AbstractFeatureSimpleExtensionGroup) inherited from {http://www.opengis.net/kml/2.2}AbstractFeatureType
    
    # Element author ({http://www.w3.org/2005/Atom}author) inherited from {http://www.opengis.net/kml/2.2}AbstractFeatureType
    
    # Element AbstractContainerSimpleExtensionGroup ({http://www.opengis.net/kml/2.2}AbstractContainerSimpleExtensionGroup) inherited from {http://www.opengis.net/kml/2.2}AbstractContainerType
    
    # Element AbstractFeatureObjectExtensionGroup ({http://www.opengis.net/kml/2.2}AbstractFeatureObjectExtensionGroup) inherited from {http://www.opengis.net/kml/2.2}AbstractFeatureType
    
    # Element {http://www.opengis.net/kml/2.2}AbstractFeatureGroup uses Python identifier AbstractFeatureGroup
    __AbstractFeatureGroup = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'AbstractFeatureGroup'), 'AbstractFeatureGroup', '__httpwww_opengis_netkml2_2_FolderType_httpwww_opengis_netkml2_2AbstractFeatureGroup', True)

    
    AbstractFeatureGroup = property(__AbstractFeatureGroup.value, __AbstractFeatureGroup.set, None, None)

    
    # Element AbstractContainerObjectExtensionGroup ({http://www.opengis.net/kml/2.2}AbstractContainerObjectExtensionGroup) inherited from {http://www.opengis.net/kml/2.2}AbstractContainerType
    
    # Element description ({http://www.opengis.net/kml/2.2}description) inherited from {http://www.opengis.net/kml/2.2}AbstractFeatureType
    
    # Element {http://www.opengis.net/kml/2.2}FolderSimpleExtensionGroup uses Python identifier FolderSimpleExtensionGroup
    __FolderSimpleExtensionGroup = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'FolderSimpleExtensionGroup'), 'FolderSimpleExtensionGroup', '__httpwww_opengis_netkml2_2_FolderType_httpwww_opengis_netkml2_2FolderSimpleExtensionGroup', True)

    
    FolderSimpleExtensionGroup = property(__FolderSimpleExtensionGroup.value, __FolderSimpleExtensionGroup.set, None, None)

    
    # Element visibility ({http://www.opengis.net/kml/2.2}visibility) inherited from {http://www.opengis.net/kml/2.2}AbstractFeatureType
    
    # Element ObjectSimpleExtensionGroup ({http://www.opengis.net/kml/2.2}ObjectSimpleExtensionGroup) inherited from {http://www.opengis.net/kml/2.2}AbstractObjectType
    
    # Element {http://www.opengis.net/kml/2.2}FolderObjectExtensionGroup uses Python identifier FolderObjectExtensionGroup
    __FolderObjectExtensionGroup = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'FolderObjectExtensionGroup'), 'FolderObjectExtensionGroup', '__httpwww_opengis_netkml2_2_FolderType_httpwww_opengis_netkml2_2FolderObjectExtensionGroup', True)

    
    FolderObjectExtensionGroup = property(__FolderObjectExtensionGroup.value, __FolderObjectExtensionGroup.set, None, None)

    
    # Element name ({http://www.opengis.net/kml/2.2}name) inherited from {http://www.opengis.net/kml/2.2}AbstractFeatureType
    
    # Element AbstractTimePrimitiveGroup ({http://www.opengis.net/kml/2.2}AbstractTimePrimitiveGroup) inherited from {http://www.opengis.net/kml/2.2}AbstractFeatureType
    
    # Element Snippet ({http://www.opengis.net/kml/2.2}Snippet) inherited from {http://www.opengis.net/kml/2.2}AbstractFeatureType
    
    # Element styleUrl ({http://www.opengis.net/kml/2.2}styleUrl) inherited from {http://www.opengis.net/kml/2.2}AbstractFeatureType
    
    # Element open ({http://www.opengis.net/kml/2.2}open) inherited from {http://www.opengis.net/kml/2.2}AbstractFeatureType
    
    # Attribute targetId inherited from {http://www.opengis.net/kml/2.2}AbstractObjectType
    
    # Attribute id inherited from {http://www.opengis.net/kml/2.2}AbstractObjectType

    _ElementMap = AbstractContainerType._ElementMap.copy()
    _ElementMap.update({
        __AbstractFeatureGroup.name() : __AbstractFeatureGroup,
        __FolderSimpleExtensionGroup.name() : __FolderSimpleExtensionGroup,
        __FolderObjectExtensionGroup.name() : __FolderObjectExtensionGroup
    })
    _AttributeMap = AbstractContainerType._AttributeMap.copy()
    _AttributeMap.update({
        
    })
Namespace.addCategoryObject('typeBinding', u'FolderType', FolderType)


# Complex type LodType with content type ELEMENT_ONLY
class LodType (AbstractObjectType):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'LodType')
    # Base type is AbstractObjectType
    
    # Element {http://www.opengis.net/kml/2.2}maxLodPixels uses Python identifier maxLodPixels
    __maxLodPixels = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'maxLodPixels'), 'maxLodPixels', '__httpwww_opengis_netkml2_2_LodType_httpwww_opengis_netkml2_2maxLodPixels', False)

    
    maxLodPixels = property(__maxLodPixels.value, __maxLodPixels.set, None, None)

    
    # Element ObjectSimpleExtensionGroup ({http://www.opengis.net/kml/2.2}ObjectSimpleExtensionGroup) inherited from {http://www.opengis.net/kml/2.2}AbstractObjectType
    
    # Element {http://www.opengis.net/kml/2.2}minFadeExtent uses Python identifier minFadeExtent
    __minFadeExtent = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'minFadeExtent'), 'minFadeExtent', '__httpwww_opengis_netkml2_2_LodType_httpwww_opengis_netkml2_2minFadeExtent', False)

    
    minFadeExtent = property(__minFadeExtent.value, __minFadeExtent.set, None, None)

    
    # Element {http://www.opengis.net/kml/2.2}minLodPixels uses Python identifier minLodPixels
    __minLodPixels = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'minLodPixels'), 'minLodPixels', '__httpwww_opengis_netkml2_2_LodType_httpwww_opengis_netkml2_2minLodPixels', False)

    
    minLodPixels = property(__minLodPixels.value, __minLodPixels.set, None, None)

    
    # Element {http://www.opengis.net/kml/2.2}LodSimpleExtensionGroup uses Python identifier LodSimpleExtensionGroup
    __LodSimpleExtensionGroup = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'LodSimpleExtensionGroup'), 'LodSimpleExtensionGroup', '__httpwww_opengis_netkml2_2_LodType_httpwww_opengis_netkml2_2LodSimpleExtensionGroup', True)

    
    LodSimpleExtensionGroup = property(__LodSimpleExtensionGroup.value, __LodSimpleExtensionGroup.set, None, None)

    
    # Element {http://www.opengis.net/kml/2.2}maxFadeExtent uses Python identifier maxFadeExtent
    __maxFadeExtent = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'maxFadeExtent'), 'maxFadeExtent', '__httpwww_opengis_netkml2_2_LodType_httpwww_opengis_netkml2_2maxFadeExtent', False)

    
    maxFadeExtent = property(__maxFadeExtent.value, __maxFadeExtent.set, None, None)

    
    # Element {http://www.opengis.net/kml/2.2}LodObjectExtensionGroup uses Python identifier LodObjectExtensionGroup
    __LodObjectExtensionGroup = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'LodObjectExtensionGroup'), 'LodObjectExtensionGroup', '__httpwww_opengis_netkml2_2_LodType_httpwww_opengis_netkml2_2LodObjectExtensionGroup', True)

    
    LodObjectExtensionGroup = property(__LodObjectExtensionGroup.value, __LodObjectExtensionGroup.set, None, None)

    
    # Attribute targetId inherited from {http://www.opengis.net/kml/2.2}AbstractObjectType
    
    # Attribute id inherited from {http://www.opengis.net/kml/2.2}AbstractObjectType

    _ElementMap = AbstractObjectType._ElementMap.copy()
    _ElementMap.update({
        __maxLodPixels.name() : __maxLodPixels,
        __minFadeExtent.name() : __minFadeExtent,
        __minLodPixels.name() : __minLodPixels,
        __LodSimpleExtensionGroup.name() : __LodSimpleExtensionGroup,
        __maxFadeExtent.name() : __maxFadeExtent,
        __LodObjectExtensionGroup.name() : __LodObjectExtensionGroup
    })
    _AttributeMap = AbstractObjectType._AttributeMap.copy()
    _AttributeMap.update({
        
    })
Namespace.addCategoryObject('typeBinding', u'LodType', LodType)


# Complex type ScaleType with content type ELEMENT_ONLY
class ScaleType (AbstractObjectType):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'ScaleType')
    # Base type is AbstractObjectType
    
    # Element {http://www.opengis.net/kml/2.2}x uses Python identifier x
    __x = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'x'), 'x', '__httpwww_opengis_netkml2_2_ScaleType_httpwww_opengis_netkml2_2x', False)

    
    x = property(__x.value, __x.set, None, None)

    
    # Element {http://www.opengis.net/kml/2.2}ScaleSimpleExtensionGroup uses Python identifier ScaleSimpleExtensionGroup
    __ScaleSimpleExtensionGroup = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'ScaleSimpleExtensionGroup'), 'ScaleSimpleExtensionGroup', '__httpwww_opengis_netkml2_2_ScaleType_httpwww_opengis_netkml2_2ScaleSimpleExtensionGroup', True)

    
    ScaleSimpleExtensionGroup = property(__ScaleSimpleExtensionGroup.value, __ScaleSimpleExtensionGroup.set, None, None)

    
    # Element ObjectSimpleExtensionGroup ({http://www.opengis.net/kml/2.2}ObjectSimpleExtensionGroup) inherited from {http://www.opengis.net/kml/2.2}AbstractObjectType
    
    # Element {http://www.opengis.net/kml/2.2}y uses Python identifier y
    __y = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'y'), 'y', '__httpwww_opengis_netkml2_2_ScaleType_httpwww_opengis_netkml2_2y', False)

    
    y = property(__y.value, __y.set, None, None)

    
    # Element {http://www.opengis.net/kml/2.2}ScaleObjectExtensionGroup uses Python identifier ScaleObjectExtensionGroup
    __ScaleObjectExtensionGroup = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'ScaleObjectExtensionGroup'), 'ScaleObjectExtensionGroup', '__httpwww_opengis_netkml2_2_ScaleType_httpwww_opengis_netkml2_2ScaleObjectExtensionGroup', True)

    
    ScaleObjectExtensionGroup = property(__ScaleObjectExtensionGroup.value, __ScaleObjectExtensionGroup.set, None, None)

    
    # Element {http://www.opengis.net/kml/2.2}z uses Python identifier z
    __z = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'z'), 'z', '__httpwww_opengis_netkml2_2_ScaleType_httpwww_opengis_netkml2_2z', False)

    
    z = property(__z.value, __z.set, None, None)

    
    # Attribute targetId inherited from {http://www.opengis.net/kml/2.2}AbstractObjectType
    
    # Attribute id inherited from {http://www.opengis.net/kml/2.2}AbstractObjectType

    _ElementMap = AbstractObjectType._ElementMap.copy()
    _ElementMap.update({
        __x.name() : __x,
        __ScaleSimpleExtensionGroup.name() : __ScaleSimpleExtensionGroup,
        __y.name() : __y,
        __ScaleObjectExtensionGroup.name() : __ScaleObjectExtensionGroup,
        __z.name() : __z
    })
    _AttributeMap = AbstractObjectType._AttributeMap.copy()
    _AttributeMap.update({
        
    })
Namespace.addCategoryObject('typeBinding', u'ScaleType', ScaleType)


# Complex type ResourceMapType with content type ELEMENT_ONLY
class ResourceMapType (AbstractObjectType):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'ResourceMapType')
    # Base type is AbstractObjectType
    
    # Element {http://www.opengis.net/kml/2.2}ResourceMapObjectExtensionGroup uses Python identifier ResourceMapObjectExtensionGroup
    __ResourceMapObjectExtensionGroup = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'ResourceMapObjectExtensionGroup'), 'ResourceMapObjectExtensionGroup', '__httpwww_opengis_netkml2_2_ResourceMapType_httpwww_opengis_netkml2_2ResourceMapObjectExtensionGroup', True)

    
    ResourceMapObjectExtensionGroup = property(__ResourceMapObjectExtensionGroup.value, __ResourceMapObjectExtensionGroup.set, None, None)

    
    # Element {http://www.opengis.net/kml/2.2}ResourceMapSimpleExtensionGroup uses Python identifier ResourceMapSimpleExtensionGroup
    __ResourceMapSimpleExtensionGroup = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'ResourceMapSimpleExtensionGroup'), 'ResourceMapSimpleExtensionGroup', '__httpwww_opengis_netkml2_2_ResourceMapType_httpwww_opengis_netkml2_2ResourceMapSimpleExtensionGroup', True)

    
    ResourceMapSimpleExtensionGroup = property(__ResourceMapSimpleExtensionGroup.value, __ResourceMapSimpleExtensionGroup.set, None, None)

    
    # Element ObjectSimpleExtensionGroup ({http://www.opengis.net/kml/2.2}ObjectSimpleExtensionGroup) inherited from {http://www.opengis.net/kml/2.2}AbstractObjectType
    
    # Element {http://www.opengis.net/kml/2.2}Alias uses Python identifier Alias
    __Alias = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'Alias'), 'Alias', '__httpwww_opengis_netkml2_2_ResourceMapType_httpwww_opengis_netkml2_2Alias', True)

    
    Alias = property(__Alias.value, __Alias.set, None, None)

    
    # Attribute targetId inherited from {http://www.opengis.net/kml/2.2}AbstractObjectType
    
    # Attribute id inherited from {http://www.opengis.net/kml/2.2}AbstractObjectType

    _ElementMap = AbstractObjectType._ElementMap.copy()
    _ElementMap.update({
        __ResourceMapObjectExtensionGroup.name() : __ResourceMapObjectExtensionGroup,
        __ResourceMapSimpleExtensionGroup.name() : __ResourceMapSimpleExtensionGroup,
        __Alias.name() : __Alias
    })
    _AttributeMap = AbstractObjectType._AttributeMap.copy()
    _AttributeMap.update({
        
    })
Namespace.addCategoryObject('typeBinding', u'ResourceMapType', ResourceMapType)


# Complex type SchemaDataType with content type ELEMENT_ONLY
class SchemaDataType (AbstractObjectType):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'SchemaDataType')
    # Base type is AbstractObjectType
    
    # Element {http://www.opengis.net/kml/2.2}SchemaDataExtension uses Python identifier SchemaDataExtension
    __SchemaDataExtension = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'SchemaDataExtension'), 'SchemaDataExtension', '__httpwww_opengis_netkml2_2_SchemaDataType_httpwww_opengis_netkml2_2SchemaDataExtension', True)

    
    SchemaDataExtension = property(__SchemaDataExtension.value, __SchemaDataExtension.set, None, None)

    
    # Element {http://www.opengis.net/kml/2.2}SimpleData uses Python identifier SimpleData
    __SimpleData = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'SimpleData'), 'SimpleData', '__httpwww_opengis_netkml2_2_SchemaDataType_httpwww_opengis_netkml2_2SimpleData', True)

    
    SimpleData = property(__SimpleData.value, __SimpleData.set, None, None)

    
    # Element ObjectSimpleExtensionGroup ({http://www.opengis.net/kml/2.2}ObjectSimpleExtensionGroup) inherited from {http://www.opengis.net/kml/2.2}AbstractObjectType
    
    # Attribute schemaUrl uses Python identifier schemaUrl
    __schemaUrl = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'schemaUrl'), 'schemaUrl', '__httpwww_opengis_netkml2_2_SchemaDataType_schemaUrl', pyxb.binding.datatypes.anyURI)
    
    schemaUrl = property(__schemaUrl.value, __schemaUrl.set, None, None)

    
    # Attribute targetId inherited from {http://www.opengis.net/kml/2.2}AbstractObjectType
    
    # Attribute id inherited from {http://www.opengis.net/kml/2.2}AbstractObjectType

    _ElementMap = AbstractObjectType._ElementMap.copy()
    _ElementMap.update({
        __SchemaDataExtension.name() : __SchemaDataExtension,
        __SimpleData.name() : __SimpleData
    })
    _AttributeMap = AbstractObjectType._AttributeMap.copy()
    _AttributeMap.update({
        __schemaUrl.name() : __schemaUrl
    })
Namespace.addCategoryObject('typeBinding', u'SchemaDataType', SchemaDataType)


# Complex type MultiGeometryType with content type ELEMENT_ONLY
class MultiGeometryType (AbstractGeometryType):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'MultiGeometryType')
    # Base type is AbstractGeometryType
    
    # Element {http://www.opengis.net/kml/2.2}MultiGeometryObjectExtensionGroup uses Python identifier MultiGeometryObjectExtensionGroup
    __MultiGeometryObjectExtensionGroup = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'MultiGeometryObjectExtensionGroup'), 'MultiGeometryObjectExtensionGroup', '__httpwww_opengis_netkml2_2_MultiGeometryType_httpwww_opengis_netkml2_2MultiGeometryObjectExtensionGroup', True)

    
    MultiGeometryObjectExtensionGroup = property(__MultiGeometryObjectExtensionGroup.value, __MultiGeometryObjectExtensionGroup.set, None, None)

    
    # Element AbstractGeometryObjectExtensionGroup ({http://www.opengis.net/kml/2.2}AbstractGeometryObjectExtensionGroup) inherited from {http://www.opengis.net/kml/2.2}AbstractGeometryType
    
    # Element ObjectSimpleExtensionGroup ({http://www.opengis.net/kml/2.2}ObjectSimpleExtensionGroup) inherited from {http://www.opengis.net/kml/2.2}AbstractObjectType
    
    # Element {http://www.opengis.net/kml/2.2}MultiGeometrySimpleExtensionGroup uses Python identifier MultiGeometrySimpleExtensionGroup
    __MultiGeometrySimpleExtensionGroup = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'MultiGeometrySimpleExtensionGroup'), 'MultiGeometrySimpleExtensionGroup', '__httpwww_opengis_netkml2_2_MultiGeometryType_httpwww_opengis_netkml2_2MultiGeometrySimpleExtensionGroup', True)

    
    MultiGeometrySimpleExtensionGroup = property(__MultiGeometrySimpleExtensionGroup.value, __MultiGeometrySimpleExtensionGroup.set, None, None)

    
    # Element {http://www.opengis.net/kml/2.2}AbstractGeometryGroup uses Python identifier AbstractGeometryGroup
    __AbstractGeometryGroup = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'AbstractGeometryGroup'), 'AbstractGeometryGroup', '__httpwww_opengis_netkml2_2_MultiGeometryType_httpwww_opengis_netkml2_2AbstractGeometryGroup', True)

    
    AbstractGeometryGroup = property(__AbstractGeometryGroup.value, __AbstractGeometryGroup.set, None, None)

    
    # Element AbstractGeometrySimpleExtensionGroup ({http://www.opengis.net/kml/2.2}AbstractGeometrySimpleExtensionGroup) inherited from {http://www.opengis.net/kml/2.2}AbstractGeometryType
    
    # Attribute targetId inherited from {http://www.opengis.net/kml/2.2}AbstractObjectType
    
    # Attribute id inherited from {http://www.opengis.net/kml/2.2}AbstractObjectType

    _ElementMap = AbstractGeometryType._ElementMap.copy()
    _ElementMap.update({
        __MultiGeometryObjectExtensionGroup.name() : __MultiGeometryObjectExtensionGroup,
        __MultiGeometrySimpleExtensionGroup.name() : __MultiGeometrySimpleExtensionGroup,
        __AbstractGeometryGroup.name() : __AbstractGeometryGroup
    })
    _AttributeMap = AbstractGeometryType._AttributeMap.copy()
    _AttributeMap.update({
        
    })
Namespace.addCategoryObject('typeBinding', u'MultiGeometryType', MultiGeometryType)


# Complex type StyleType with content type ELEMENT_ONLY
class StyleType (AbstractStyleSelectorType):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'StyleType')
    # Base type is AbstractStyleSelectorType
    
    # Element {http://www.opengis.net/kml/2.2}StyleObjectExtensionGroup uses Python identifier StyleObjectExtensionGroup
    __StyleObjectExtensionGroup = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'StyleObjectExtensionGroup'), 'StyleObjectExtensionGroup', '__httpwww_opengis_netkml2_2_StyleType_httpwww_opengis_netkml2_2StyleObjectExtensionGroup', True)

    
    StyleObjectExtensionGroup = property(__StyleObjectExtensionGroup.value, __StyleObjectExtensionGroup.set, None, None)

    
    # Element {http://www.opengis.net/kml/2.2}ListStyle uses Python identifier ListStyle
    __ListStyle = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'ListStyle'), 'ListStyle', '__httpwww_opengis_netkml2_2_StyleType_httpwww_opengis_netkml2_2ListStyle', False)

    
    ListStyle = property(__ListStyle.value, __ListStyle.set, None, None)

    
    # Element AbstractStyleSelectorSimpleExtensionGroup ({http://www.opengis.net/kml/2.2}AbstractStyleSelectorSimpleExtensionGroup) inherited from {http://www.opengis.net/kml/2.2}AbstractStyleSelectorType
    
    # Element {http://www.opengis.net/kml/2.2}IconStyle uses Python identifier IconStyle
    __IconStyle = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'IconStyle'), 'IconStyle', '__httpwww_opengis_netkml2_2_StyleType_httpwww_opengis_netkml2_2IconStyle', False)

    
    IconStyle = property(__IconStyle.value, __IconStyle.set, None, None)

    
    # Element {http://www.opengis.net/kml/2.2}PolyStyle uses Python identifier PolyStyle
    __PolyStyle = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'PolyStyle'), 'PolyStyle', '__httpwww_opengis_netkml2_2_StyleType_httpwww_opengis_netkml2_2PolyStyle', False)

    
    PolyStyle = property(__PolyStyle.value, __PolyStyle.set, None, None)

    
    # Element {http://www.opengis.net/kml/2.2}StyleSimpleExtensionGroup uses Python identifier StyleSimpleExtensionGroup
    __StyleSimpleExtensionGroup = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'StyleSimpleExtensionGroup'), 'StyleSimpleExtensionGroup', '__httpwww_opengis_netkml2_2_StyleType_httpwww_opengis_netkml2_2StyleSimpleExtensionGroup', True)

    
    StyleSimpleExtensionGroup = property(__StyleSimpleExtensionGroup.value, __StyleSimpleExtensionGroup.set, None, None)

    
    # Element AbstractStyleSelectorObjectExtensionGroup ({http://www.opengis.net/kml/2.2}AbstractStyleSelectorObjectExtensionGroup) inherited from {http://www.opengis.net/kml/2.2}AbstractStyleSelectorType
    
    # Element {http://www.opengis.net/kml/2.2}LabelStyle uses Python identifier LabelStyle
    __LabelStyle = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'LabelStyle'), 'LabelStyle', '__httpwww_opengis_netkml2_2_StyleType_httpwww_opengis_netkml2_2LabelStyle', False)

    
    LabelStyle = property(__LabelStyle.value, __LabelStyle.set, None, None)

    
    # Element {http://www.opengis.net/kml/2.2}BalloonStyle uses Python identifier BalloonStyle
    __BalloonStyle = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'BalloonStyle'), 'BalloonStyle', '__httpwww_opengis_netkml2_2_StyleType_httpwww_opengis_netkml2_2BalloonStyle', False)

    
    BalloonStyle = property(__BalloonStyle.value, __BalloonStyle.set, None, None)

    
    # Element ObjectSimpleExtensionGroup ({http://www.opengis.net/kml/2.2}ObjectSimpleExtensionGroup) inherited from {http://www.opengis.net/kml/2.2}AbstractObjectType
    
    # Element {http://www.opengis.net/kml/2.2}LineStyle uses Python identifier LineStyle
    __LineStyle = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'LineStyle'), 'LineStyle', '__httpwww_opengis_netkml2_2_StyleType_httpwww_opengis_netkml2_2LineStyle', False)

    
    LineStyle = property(__LineStyle.value, __LineStyle.set, None, None)

    
    # Attribute targetId inherited from {http://www.opengis.net/kml/2.2}AbstractObjectType
    
    # Attribute id inherited from {http://www.opengis.net/kml/2.2}AbstractObjectType

    _ElementMap = AbstractStyleSelectorType._ElementMap.copy()
    _ElementMap.update({
        __StyleObjectExtensionGroup.name() : __StyleObjectExtensionGroup,
        __ListStyle.name() : __ListStyle,
        __IconStyle.name() : __IconStyle,
        __PolyStyle.name() : __PolyStyle,
        __StyleSimpleExtensionGroup.name() : __StyleSimpleExtensionGroup,
        __LabelStyle.name() : __LabelStyle,
        __BalloonStyle.name() : __BalloonStyle,
        __LineStyle.name() : __LineStyle
    })
    _AttributeMap = AbstractStyleSelectorType._AttributeMap.copy()
    _AttributeMap.update({
        
    })
Namespace.addCategoryObject('typeBinding', u'StyleType', StyleType)


# Complex type PlacemarkType with content type ELEMENT_ONLY
class PlacemarkType (AbstractFeatureType):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'PlacemarkType')
    # Base type is AbstractFeatureType
    
    # Element link ({http://www.w3.org/2005/Atom}link) inherited from {http://www.opengis.net/kml/2.2}AbstractFeatureType
    
    # Element AbstractStyleSelectorGroup ({http://www.opengis.net/kml/2.2}AbstractStyleSelectorGroup) inherited from {http://www.opengis.net/kml/2.2}AbstractFeatureType
    
    # Element address ({http://www.opengis.net/kml/2.2}address) inherited from {http://www.opengis.net/kml/2.2}AbstractFeatureType
    
    # Element Region ({http://www.opengis.net/kml/2.2}Region) inherited from {http://www.opengis.net/kml/2.2}AbstractFeatureType
    
    # Element AddressDetails ({urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}AddressDetails) inherited from {http://www.opengis.net/kml/2.2}AbstractFeatureType
    
    # Element {http://www.opengis.net/kml/2.2}PlacemarkObjectExtensionGroup uses Python identifier PlacemarkObjectExtensionGroup
    __PlacemarkObjectExtensionGroup = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'PlacemarkObjectExtensionGroup'), 'PlacemarkObjectExtensionGroup', '__httpwww_opengis_netkml2_2_PlacemarkType_httpwww_opengis_netkml2_2PlacemarkObjectExtensionGroup', True)

    
    PlacemarkObjectExtensionGroup = property(__PlacemarkObjectExtensionGroup.value, __PlacemarkObjectExtensionGroup.set, None, None)

    
    # Element phoneNumber ({http://www.opengis.net/kml/2.2}phoneNumber) inherited from {http://www.opengis.net/kml/2.2}AbstractFeatureType
    
    # Element Metadata ({http://www.opengis.net/kml/2.2}Metadata) inherited from {http://www.opengis.net/kml/2.2}AbstractFeatureType
    
    # Element {http://www.opengis.net/kml/2.2}AbstractGeometryGroup uses Python identifier AbstractGeometryGroup
    __AbstractGeometryGroup = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'AbstractGeometryGroup'), 'AbstractGeometryGroup', '__httpwww_opengis_netkml2_2_PlacemarkType_httpwww_opengis_netkml2_2AbstractGeometryGroup', False)

    
    AbstractGeometryGroup = property(__AbstractGeometryGroup.value, __AbstractGeometryGroup.set, None, None)

    
    # Element ExtendedData ({http://www.opengis.net/kml/2.2}ExtendedData) inherited from {http://www.opengis.net/kml/2.2}AbstractFeatureType
    
    # Element visibility ({http://www.opengis.net/kml/2.2}visibility) inherited from {http://www.opengis.net/kml/2.2}AbstractFeatureType
    
    # Element snippet ({http://www.opengis.net/kml/2.2}snippet) inherited from {http://www.opengis.net/kml/2.2}AbstractFeatureType
    
    # Element {http://www.opengis.net/kml/2.2}PlacemarkSimpleExtensionGroup uses Python identifier PlacemarkSimpleExtensionGroup
    __PlacemarkSimpleExtensionGroup = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'PlacemarkSimpleExtensionGroup'), 'PlacemarkSimpleExtensionGroup', '__httpwww_opengis_netkml2_2_PlacemarkType_httpwww_opengis_netkml2_2PlacemarkSimpleExtensionGroup', True)

    
    PlacemarkSimpleExtensionGroup = property(__PlacemarkSimpleExtensionGroup.value, __PlacemarkSimpleExtensionGroup.set, None, None)

    
    # Element Snippet ({http://www.opengis.net/kml/2.2}Snippet) inherited from {http://www.opengis.net/kml/2.2}AbstractFeatureType
    
    # Element author ({http://www.w3.org/2005/Atom}author) inherited from {http://www.opengis.net/kml/2.2}AbstractFeatureType
    
    # Element AbstractFeatureObjectExtensionGroup ({http://www.opengis.net/kml/2.2}AbstractFeatureObjectExtensionGroup) inherited from {http://www.opengis.net/kml/2.2}AbstractFeatureType
    
    # Element description ({http://www.opengis.net/kml/2.2}description) inherited from {http://www.opengis.net/kml/2.2}AbstractFeatureType
    
    # Element AbstractViewGroup ({http://www.opengis.net/kml/2.2}AbstractViewGroup) inherited from {http://www.opengis.net/kml/2.2}AbstractFeatureType
    
    # Element ObjectSimpleExtensionGroup ({http://www.opengis.net/kml/2.2}ObjectSimpleExtensionGroup) inherited from {http://www.opengis.net/kml/2.2}AbstractObjectType
    
    # Element name ({http://www.opengis.net/kml/2.2}name) inherited from {http://www.opengis.net/kml/2.2}AbstractFeatureType
    
    # Element open ({http://www.opengis.net/kml/2.2}open) inherited from {http://www.opengis.net/kml/2.2}AbstractFeatureType
    
    # Element AbstractFeatureSimpleExtensionGroup ({http://www.opengis.net/kml/2.2}AbstractFeatureSimpleExtensionGroup) inherited from {http://www.opengis.net/kml/2.2}AbstractFeatureType
    
    # Element styleUrl ({http://www.opengis.net/kml/2.2}styleUrl) inherited from {http://www.opengis.net/kml/2.2}AbstractFeatureType
    
    # Element AbstractTimePrimitiveGroup ({http://www.opengis.net/kml/2.2}AbstractTimePrimitiveGroup) inherited from {http://www.opengis.net/kml/2.2}AbstractFeatureType
    
    # Attribute targetId inherited from {http://www.opengis.net/kml/2.2}AbstractObjectType
    
    # Attribute id inherited from {http://www.opengis.net/kml/2.2}AbstractObjectType

    _ElementMap = AbstractFeatureType._ElementMap.copy()
    _ElementMap.update({
        __PlacemarkObjectExtensionGroup.name() : __PlacemarkObjectExtensionGroup,
        __AbstractGeometryGroup.name() : __AbstractGeometryGroup,
        __PlacemarkSimpleExtensionGroup.name() : __PlacemarkSimpleExtensionGroup
    })
    _AttributeMap = AbstractFeatureType._AttributeMap.copy()
    _AttributeMap.update({
        
    })
Namespace.addCategoryObject('typeBinding', u'PlacemarkType', PlacemarkType)


# Complex type DocumentType with content type ELEMENT_ONLY
class DocumentType (AbstractContainerType):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'DocumentType')
    # Base type is AbstractContainerType
    
    # Element link ({http://www.w3.org/2005/Atom}link) inherited from {http://www.opengis.net/kml/2.2}AbstractFeatureType
    
    # Element AbstractStyleSelectorGroup ({http://www.opengis.net/kml/2.2}AbstractStyleSelectorGroup) inherited from {http://www.opengis.net/kml/2.2}AbstractFeatureType
    
    # Element address ({http://www.opengis.net/kml/2.2}address) inherited from {http://www.opengis.net/kml/2.2}AbstractFeatureType
    
    # Element {http://www.opengis.net/kml/2.2}Schema uses Python identifier Schema
    __Schema = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'Schema'), 'Schema', '__httpwww_opengis_netkml2_2_DocumentType_httpwww_opengis_netkml2_2Schema', True)

    
    Schema = property(__Schema.value, __Schema.set, None, None)

    
    # Element AddressDetails ({urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}AddressDetails) inherited from {http://www.opengis.net/kml/2.2}AbstractFeatureType
    
    # Element {http://www.opengis.net/kml/2.2}AbstractFeatureGroup uses Python identifier AbstractFeatureGroup
    __AbstractFeatureGroup = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'AbstractFeatureGroup'), 'AbstractFeatureGroup', '__httpwww_opengis_netkml2_2_DocumentType_httpwww_opengis_netkml2_2AbstractFeatureGroup', True)

    
    AbstractFeatureGroup = property(__AbstractFeatureGroup.value, __AbstractFeatureGroup.set, None, None)

    
    # Element open ({http://www.opengis.net/kml/2.2}open) inherited from {http://www.opengis.net/kml/2.2}AbstractFeatureType
    
    # Element phoneNumber ({http://www.opengis.net/kml/2.2}phoneNumber) inherited from {http://www.opengis.net/kml/2.2}AbstractFeatureType
    
    # Element Metadata ({http://www.opengis.net/kml/2.2}Metadata) inherited from {http://www.opengis.net/kml/2.2}AbstractFeatureType
    
    # Element ExtendedData ({http://www.opengis.net/kml/2.2}ExtendedData) inherited from {http://www.opengis.net/kml/2.2}AbstractFeatureType
    
    # Element AbstractViewGroup ({http://www.opengis.net/kml/2.2}AbstractViewGroup) inherited from {http://www.opengis.net/kml/2.2}AbstractFeatureType
    
    # Element {http://www.opengis.net/kml/2.2}DocumentObjectExtensionGroup uses Python identifier DocumentObjectExtensionGroup
    __DocumentObjectExtensionGroup = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'DocumentObjectExtensionGroup'), 'DocumentObjectExtensionGroup', '__httpwww_opengis_netkml2_2_DocumentType_httpwww_opengis_netkml2_2DocumentObjectExtensionGroup', True)

    
    DocumentObjectExtensionGroup = property(__DocumentObjectExtensionGroup.value, __DocumentObjectExtensionGroup.set, None, None)

    
    # Element snippet ({http://www.opengis.net/kml/2.2}snippet) inherited from {http://www.opengis.net/kml/2.2}AbstractFeatureType
    
    # Element Snippet ({http://www.opengis.net/kml/2.2}Snippet) inherited from {http://www.opengis.net/kml/2.2}AbstractFeatureType
    
    # Element author ({http://www.w3.org/2005/Atom}author) inherited from {http://www.opengis.net/kml/2.2}AbstractFeatureType
    
    # Element AbstractContainerSimpleExtensionGroup ({http://www.opengis.net/kml/2.2}AbstractContainerSimpleExtensionGroup) inherited from {http://www.opengis.net/kml/2.2}AbstractContainerType
    
    # Element AbstractFeatureObjectExtensionGroup ({http://www.opengis.net/kml/2.2}AbstractFeatureObjectExtensionGroup) inherited from {http://www.opengis.net/kml/2.2}AbstractFeatureType
    
    # Element AbstractContainerObjectExtensionGroup ({http://www.opengis.net/kml/2.2}AbstractContainerObjectExtensionGroup) inherited from {http://www.opengis.net/kml/2.2}AbstractContainerType
    
    # Element description ({http://www.opengis.net/kml/2.2}description) inherited from {http://www.opengis.net/kml/2.2}AbstractFeatureType
    
    # Element visibility ({http://www.opengis.net/kml/2.2}visibility) inherited from {http://www.opengis.net/kml/2.2}AbstractFeatureType
    
    # Element ObjectSimpleExtensionGroup ({http://www.opengis.net/kml/2.2}ObjectSimpleExtensionGroup) inherited from {http://www.opengis.net/kml/2.2}AbstractObjectType
    
    # Element name ({http://www.opengis.net/kml/2.2}name) inherited from {http://www.opengis.net/kml/2.2}AbstractFeatureType
    
    # Element AbstractTimePrimitiveGroup ({http://www.opengis.net/kml/2.2}AbstractTimePrimitiveGroup) inherited from {http://www.opengis.net/kml/2.2}AbstractFeatureType
    
    # Element AbstractFeatureSimpleExtensionGroup ({http://www.opengis.net/kml/2.2}AbstractFeatureSimpleExtensionGroup) inherited from {http://www.opengis.net/kml/2.2}AbstractFeatureType
    
    # Element Region ({http://www.opengis.net/kml/2.2}Region) inherited from {http://www.opengis.net/kml/2.2}AbstractFeatureType
    
    # Element styleUrl ({http://www.opengis.net/kml/2.2}styleUrl) inherited from {http://www.opengis.net/kml/2.2}AbstractFeatureType
    
    # Element {http://www.opengis.net/kml/2.2}DocumentSimpleExtensionGroup uses Python identifier DocumentSimpleExtensionGroup
    __DocumentSimpleExtensionGroup = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'DocumentSimpleExtensionGroup'), 'DocumentSimpleExtensionGroup', '__httpwww_opengis_netkml2_2_DocumentType_httpwww_opengis_netkml2_2DocumentSimpleExtensionGroup', True)

    
    DocumentSimpleExtensionGroup = property(__DocumentSimpleExtensionGroup.value, __DocumentSimpleExtensionGroup.set, None, None)

    
    # Attribute targetId inherited from {http://www.opengis.net/kml/2.2}AbstractObjectType
    
    # Attribute id inherited from {http://www.opengis.net/kml/2.2}AbstractObjectType

    _ElementMap = AbstractContainerType._ElementMap.copy()
    _ElementMap.update({
        __Schema.name() : __Schema,
        __AbstractFeatureGroup.name() : __AbstractFeatureGroup,
        __DocumentObjectExtensionGroup.name() : __DocumentObjectExtensionGroup,
        __DocumentSimpleExtensionGroup.name() : __DocumentSimpleExtensionGroup
    })
    _AttributeMap = AbstractContainerType._AttributeMap.copy()
    _AttributeMap.update({
        
    })
Namespace.addCategoryObject('typeBinding', u'DocumentType', DocumentType)


# Complex type ItemIconType with content type ELEMENT_ONLY
class ItemIconType (AbstractObjectType):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'ItemIconType')
    # Base type is AbstractObjectType
    
    # Element {http://www.opengis.net/kml/2.2}ItemIconObjectExtensionGroup uses Python identifier ItemIconObjectExtensionGroup
    __ItemIconObjectExtensionGroup = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'ItemIconObjectExtensionGroup'), 'ItemIconObjectExtensionGroup', '__httpwww_opengis_netkml2_2_ItemIconType_httpwww_opengis_netkml2_2ItemIconObjectExtensionGroup', True)

    
    ItemIconObjectExtensionGroup = property(__ItemIconObjectExtensionGroup.value, __ItemIconObjectExtensionGroup.set, None, None)

    
    # Element {http://www.opengis.net/kml/2.2}state uses Python identifier state
    __state = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'state'), 'state', '__httpwww_opengis_netkml2_2_ItemIconType_httpwww_opengis_netkml2_2state', False)

    
    state = property(__state.value, __state.set, None, None)

    
    # Element {http://www.opengis.net/kml/2.2}ItemIconSimpleExtensionGroup uses Python identifier ItemIconSimpleExtensionGroup
    __ItemIconSimpleExtensionGroup = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'ItemIconSimpleExtensionGroup'), 'ItemIconSimpleExtensionGroup', '__httpwww_opengis_netkml2_2_ItemIconType_httpwww_opengis_netkml2_2ItemIconSimpleExtensionGroup', True)

    
    ItemIconSimpleExtensionGroup = property(__ItemIconSimpleExtensionGroup.value, __ItemIconSimpleExtensionGroup.set, None, None)

    
    # Element ObjectSimpleExtensionGroup ({http://www.opengis.net/kml/2.2}ObjectSimpleExtensionGroup) inherited from {http://www.opengis.net/kml/2.2}AbstractObjectType
    
    # Element {http://www.opengis.net/kml/2.2}href uses Python identifier href
    __href = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'href'), 'href', '__httpwww_opengis_netkml2_2_ItemIconType_httpwww_opengis_netkml2_2href', False)

    
    href = property(__href.value, __href.set, None, u'not anyURI due to $[x] substitution in\n      PhotoOverlay')

    
    # Attribute targetId inherited from {http://www.opengis.net/kml/2.2}AbstractObjectType
    
    # Attribute id inherited from {http://www.opengis.net/kml/2.2}AbstractObjectType

    _ElementMap = AbstractObjectType._ElementMap.copy()
    _ElementMap.update({
        __ItemIconObjectExtensionGroup.name() : __ItemIconObjectExtensionGroup,
        __state.name() : __state,
        __ItemIconSimpleExtensionGroup.name() : __ItemIconSimpleExtensionGroup,
        __href.name() : __href
    })
    _AttributeMap = AbstractObjectType._AttributeMap.copy()
    _AttributeMap.update({
        
    })
Namespace.addCategoryObject('typeBinding', u'ItemIconType', ItemIconType)


# Complex type SimpleFieldType with content type ELEMENT_ONLY
class SimpleFieldType (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'SimpleFieldType')
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {http://www.opengis.net/kml/2.2}SimpleFieldExtension uses Python identifier SimpleFieldExtension
    __SimpleFieldExtension = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'SimpleFieldExtension'), 'SimpleFieldExtension', '__httpwww_opengis_netkml2_2_SimpleFieldType_httpwww_opengis_netkml2_2SimpleFieldExtension', True)

    
    SimpleFieldExtension = property(__SimpleFieldExtension.value, __SimpleFieldExtension.set, None, None)

    
    # Element {http://www.opengis.net/kml/2.2}displayName uses Python identifier displayName
    __displayName = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'displayName'), 'displayName', '__httpwww_opengis_netkml2_2_SimpleFieldType_httpwww_opengis_netkml2_2displayName', False)

    
    displayName = property(__displayName.value, __displayName.set, None, None)

    
    # Attribute type uses Python identifier type
    __type = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'type'), 'type', '__httpwww_opengis_netkml2_2_SimpleFieldType_type', pyxb.binding.datatypes.string)
    
    type = property(__type.value, __type.set, None, None)

    
    # Attribute name uses Python identifier name
    __name = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'name'), 'name', '__httpwww_opengis_netkml2_2_SimpleFieldType_name', pyxb.binding.datatypes.string)
    
    name = property(__name.value, __name.set, None, None)


    _ElementMap = {
        __SimpleFieldExtension.name() : __SimpleFieldExtension,
        __displayName.name() : __displayName
    }
    _AttributeMap = {
        __type.name() : __type,
        __name.name() : __name
    }
Namespace.addCategoryObject('typeBinding', u'SimpleFieldType', SimpleFieldType)


# Complex type TimeSpanType with content type ELEMENT_ONLY
class TimeSpanType (AbstractTimePrimitiveType):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'TimeSpanType')
    # Base type is AbstractTimePrimitiveType
    
    # Element {http://www.opengis.net/kml/2.2}end uses Python identifier end
    __end = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'end'), 'end', '__httpwww_opengis_netkml2_2_TimeSpanType_httpwww_opengis_netkml2_2end', False)

    
    end = property(__end.value, __end.set, None, None)

    
    # Element AbstractTimePrimitiveObjectExtensionGroup ({http://www.opengis.net/kml/2.2}AbstractTimePrimitiveObjectExtensionGroup) inherited from {http://www.opengis.net/kml/2.2}AbstractTimePrimitiveType
    
    # Element {http://www.opengis.net/kml/2.2}TimeSpanObjectExtensionGroup uses Python identifier TimeSpanObjectExtensionGroup
    __TimeSpanObjectExtensionGroup = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'TimeSpanObjectExtensionGroup'), 'TimeSpanObjectExtensionGroup', '__httpwww_opengis_netkml2_2_TimeSpanType_httpwww_opengis_netkml2_2TimeSpanObjectExtensionGroup', True)

    
    TimeSpanObjectExtensionGroup = property(__TimeSpanObjectExtensionGroup.value, __TimeSpanObjectExtensionGroup.set, None, None)

    
    # Element {http://www.opengis.net/kml/2.2}TimeSpanSimpleExtensionGroup uses Python identifier TimeSpanSimpleExtensionGroup
    __TimeSpanSimpleExtensionGroup = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'TimeSpanSimpleExtensionGroup'), 'TimeSpanSimpleExtensionGroup', '__httpwww_opengis_netkml2_2_TimeSpanType_httpwww_opengis_netkml2_2TimeSpanSimpleExtensionGroup', True)

    
    TimeSpanSimpleExtensionGroup = property(__TimeSpanSimpleExtensionGroup.value, __TimeSpanSimpleExtensionGroup.set, None, None)

    
    # Element ObjectSimpleExtensionGroup ({http://www.opengis.net/kml/2.2}ObjectSimpleExtensionGroup) inherited from {http://www.opengis.net/kml/2.2}AbstractObjectType
    
    # Element {http://www.opengis.net/kml/2.2}begin uses Python identifier begin
    __begin = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'begin'), 'begin', '__httpwww_opengis_netkml2_2_TimeSpanType_httpwww_opengis_netkml2_2begin', False)

    
    begin = property(__begin.value, __begin.set, None, None)

    
    # Element AbstractTimePrimitiveSimpleExtensionGroup ({http://www.opengis.net/kml/2.2}AbstractTimePrimitiveSimpleExtensionGroup) inherited from {http://www.opengis.net/kml/2.2}AbstractTimePrimitiveType
    
    # Attribute targetId inherited from {http://www.opengis.net/kml/2.2}AbstractObjectType
    
    # Attribute id inherited from {http://www.opengis.net/kml/2.2}AbstractObjectType

    _ElementMap = AbstractTimePrimitiveType._ElementMap.copy()
    _ElementMap.update({
        __end.name() : __end,
        __TimeSpanObjectExtensionGroup.name() : __TimeSpanObjectExtensionGroup,
        __TimeSpanSimpleExtensionGroup.name() : __TimeSpanSimpleExtensionGroup,
        __begin.name() : __begin
    })
    _AttributeMap = AbstractTimePrimitiveType._AttributeMap.copy()
    _AttributeMap.update({
        
    })
Namespace.addCategoryObject('typeBinding', u'TimeSpanType', TimeSpanType)


# Complex type NetworkLinkType with content type ELEMENT_ONLY
class NetworkLinkType (AbstractFeatureType):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'NetworkLinkType')
    # Base type is AbstractFeatureType
    
    # Element link ({http://www.w3.org/2005/Atom}link) inherited from {http://www.opengis.net/kml/2.2}AbstractFeatureType
    
    # Element AbstractStyleSelectorGroup ({http://www.opengis.net/kml/2.2}AbstractStyleSelectorGroup) inherited from {http://www.opengis.net/kml/2.2}AbstractFeatureType
    
    # Element address ({http://www.opengis.net/kml/2.2}address) inherited from {http://www.opengis.net/kml/2.2}AbstractFeatureType
    
    # Element Region ({http://www.opengis.net/kml/2.2}Region) inherited from {http://www.opengis.net/kml/2.2}AbstractFeatureType
    
    # Element {http://www.opengis.net/kml/2.2}Url uses Python identifier Url
    __Url = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'Url'), 'Url', '__httpwww_opengis_netkml2_2_NetworkLinkType_httpwww_opengis_netkml2_2Url', False)

    
    Url = property(__Url.value, __Url.set, None, u'Url deprecated in 2.2')

    
    # Element AddressDetails ({urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}AddressDetails) inherited from {http://www.opengis.net/kml/2.2}AbstractFeatureType
    
    # Element open ({http://www.opengis.net/kml/2.2}open) inherited from {http://www.opengis.net/kml/2.2}AbstractFeatureType
    
    # Element {http://www.opengis.net/kml/2.2}Link uses Python identifier Link
    __Link = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'Link'), 'Link', '__httpwww_opengis_netkml2_2_NetworkLinkType_httpwww_opengis_netkml2_2Link', False)

    
    Link = property(__Link.value, __Link.set, None, None)

    
    # Element phoneNumber ({http://www.opengis.net/kml/2.2}phoneNumber) inherited from {http://www.opengis.net/kml/2.2}AbstractFeatureType
    
    # Element {http://www.opengis.net/kml/2.2}NetworkLinkSimpleExtensionGroup uses Python identifier NetworkLinkSimpleExtensionGroup
    __NetworkLinkSimpleExtensionGroup = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'NetworkLinkSimpleExtensionGroup'), 'NetworkLinkSimpleExtensionGroup', '__httpwww_opengis_netkml2_2_NetworkLinkType_httpwww_opengis_netkml2_2NetworkLinkSimpleExtensionGroup', True)

    
    NetworkLinkSimpleExtensionGroup = property(__NetworkLinkSimpleExtensionGroup.value, __NetworkLinkSimpleExtensionGroup.set, None, None)

    
    # Element ExtendedData ({http://www.opengis.net/kml/2.2}ExtendedData) inherited from {http://www.opengis.net/kml/2.2}AbstractFeatureType
    
    # Element AbstractViewGroup ({http://www.opengis.net/kml/2.2}AbstractViewGroup) inherited from {http://www.opengis.net/kml/2.2}AbstractFeatureType
    
    # Element {http://www.opengis.net/kml/2.2}NetworkLinkObjectExtensionGroup uses Python identifier NetworkLinkObjectExtensionGroup
    __NetworkLinkObjectExtensionGroup = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'NetworkLinkObjectExtensionGroup'), 'NetworkLinkObjectExtensionGroup', '__httpwww_opengis_netkml2_2_NetworkLinkType_httpwww_opengis_netkml2_2NetworkLinkObjectExtensionGroup', True)

    
    NetworkLinkObjectExtensionGroup = property(__NetworkLinkObjectExtensionGroup.value, __NetworkLinkObjectExtensionGroup.set, None, None)

    
    # Element snippet ({http://www.opengis.net/kml/2.2}snippet) inherited from {http://www.opengis.net/kml/2.2}AbstractFeatureType
    
    # Element AbstractFeatureSimpleExtensionGroup ({http://www.opengis.net/kml/2.2}AbstractFeatureSimpleExtensionGroup) inherited from {http://www.opengis.net/kml/2.2}AbstractFeatureType
    
    # Element styleUrl ({http://www.opengis.net/kml/2.2}styleUrl) inherited from {http://www.opengis.net/kml/2.2}AbstractFeatureType
    
    # Element AbstractFeatureObjectExtensionGroup ({http://www.opengis.net/kml/2.2}AbstractFeatureObjectExtensionGroup) inherited from {http://www.opengis.net/kml/2.2}AbstractFeatureType
    
    # Element name ({http://www.opengis.net/kml/2.2}name) inherited from {http://www.opengis.net/kml/2.2}AbstractFeatureType
    
    # Element visibility ({http://www.opengis.net/kml/2.2}visibility) inherited from {http://www.opengis.net/kml/2.2}AbstractFeatureType
    
    # Element ObjectSimpleExtensionGroup ({http://www.opengis.net/kml/2.2}ObjectSimpleExtensionGroup) inherited from {http://www.opengis.net/kml/2.2}AbstractObjectType
    
    # Element description ({http://www.opengis.net/kml/2.2}description) inherited from {http://www.opengis.net/kml/2.2}AbstractFeatureType
    
    # Element AbstractTimePrimitiveGroup ({http://www.opengis.net/kml/2.2}AbstractTimePrimitiveGroup) inherited from {http://www.opengis.net/kml/2.2}AbstractFeatureType
    
    # Element {http://www.opengis.net/kml/2.2}refreshVisibility uses Python identifier refreshVisibility
    __refreshVisibility = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'refreshVisibility'), 'refreshVisibility', '__httpwww_opengis_netkml2_2_NetworkLinkType_httpwww_opengis_netkml2_2refreshVisibility', False)

    
    refreshVisibility = property(__refreshVisibility.value, __refreshVisibility.set, None, None)

    
    # Element Snippet ({http://www.opengis.net/kml/2.2}Snippet) inherited from {http://www.opengis.net/kml/2.2}AbstractFeatureType
    
    # Element author ({http://www.w3.org/2005/Atom}author) inherited from {http://www.opengis.net/kml/2.2}AbstractFeatureType
    
    # Element Metadata ({http://www.opengis.net/kml/2.2}Metadata) inherited from {http://www.opengis.net/kml/2.2}AbstractFeatureType
    
    # Element {http://www.opengis.net/kml/2.2}flyToView uses Python identifier flyToView
    __flyToView = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'flyToView'), 'flyToView', '__httpwww_opengis_netkml2_2_NetworkLinkType_httpwww_opengis_netkml2_2flyToView', False)

    
    flyToView = property(__flyToView.value, __flyToView.set, None, None)

    
    # Attribute targetId inherited from {http://www.opengis.net/kml/2.2}AbstractObjectType
    
    # Attribute id inherited from {http://www.opengis.net/kml/2.2}AbstractObjectType

    _ElementMap = AbstractFeatureType._ElementMap.copy()
    _ElementMap.update({
        __Url.name() : __Url,
        __Link.name() : __Link,
        __NetworkLinkSimpleExtensionGroup.name() : __NetworkLinkSimpleExtensionGroup,
        __NetworkLinkObjectExtensionGroup.name() : __NetworkLinkObjectExtensionGroup,
        __refreshVisibility.name() : __refreshVisibility,
        __flyToView.name() : __flyToView
    })
    _AttributeMap = AbstractFeatureType._AttributeMap.copy()
    _AttributeMap.update({
        
    })
Namespace.addCategoryObject('typeBinding', u'NetworkLinkType', NetworkLinkType)


AbstractGeometryGroup = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'AbstractGeometryGroup'), AbstractGeometryType, abstract=pyxb.binding.datatypes.boolean(1))
Namespace.addCategoryObject('elementBinding', AbstractGeometryGroup.name().localName(), AbstractGeometryGroup)

tessellate = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'tessellate'), pyxb.binding.datatypes.boolean)
Namespace.addCategoryObject('elementBinding', tessellate.name().localName(), tessellate)

AbstractColorStyleObjectExtensionGroup = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'AbstractColorStyleObjectExtensionGroup'), pyxb.binding.datatypes.anyType, abstract=pyxb.binding.datatypes.boolean(1))
Namespace.addCategoryObject('elementBinding', AbstractColorStyleObjectExtensionGroup.name().localName(), AbstractColorStyleObjectExtensionGroup)

IconStyle = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'IconStyle'), IconStyleType)
Namespace.addCategoryObject('elementBinding', IconStyle.name().localName(), IconStyle)

Data = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Data'), DataType)
Namespace.addCategoryObject('elementBinding', Data.name().localName(), Data)

AbstractOverlaySimpleExtensionGroup = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'AbstractOverlaySimpleExtensionGroup'), pyxb.binding.datatypes.anySimpleType, abstract=pyxb.binding.datatypes.boolean(1))
Namespace.addCategoryObject('elementBinding', AbstractOverlaySimpleExtensionGroup.name().localName(), AbstractOverlaySimpleExtensionGroup)

AbstractOverlayObjectExtensionGroup = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'AbstractOverlayObjectExtensionGroup'), pyxb.binding.datatypes.anyType, abstract=pyxb.binding.datatypes.boolean(1))
Namespace.addCategoryObject('elementBinding', AbstractOverlayObjectExtensionGroup.name().localName(), AbstractOverlayObjectExtensionGroup)

AbstractStyleSelectorGroup = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'AbstractStyleSelectorGroup'), AbstractStyleSelectorType, abstract=pyxb.binding.datatypes.boolean(1))
Namespace.addCategoryObject('elementBinding', AbstractStyleSelectorGroup.name().localName(), AbstractStyleSelectorGroup)

altitudeModeGroup = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'altitudeModeGroup'), pyxb.binding.datatypes.anyType, abstract=pyxb.binding.datatypes.boolean(1))
Namespace.addCategoryObject('elementBinding', altitudeModeGroup.name().localName(), altitudeModeGroup)

IconStyleObjectExtensionGroup = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'IconStyleObjectExtensionGroup'), pyxb.binding.datatypes.anyType, abstract=pyxb.binding.datatypes.boolean(1))
Namespace.addCategoryObject('elementBinding', IconStyleObjectExtensionGroup.name().localName(), IconStyleObjectExtensionGroup)

refreshVisibility = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'refreshVisibility'), pyxb.binding.datatypes.boolean)
Namespace.addCategoryObject('elementBinding', refreshVisibility.name().localName(), refreshVisibility)

AbstractStyleSelectorSimpleExtensionGroup = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'AbstractStyleSelectorSimpleExtensionGroup'), pyxb.binding.datatypes.anySimpleType, abstract=pyxb.binding.datatypes.boolean(1))
Namespace.addCategoryObject('elementBinding', AbstractStyleSelectorSimpleExtensionGroup.name().localName(), AbstractStyleSelectorSimpleExtensionGroup)

AbstractTimePrimitiveGroup = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'AbstractTimePrimitiveGroup'), AbstractTimePrimitiveType, abstract=pyxb.binding.datatypes.boolean(1))
Namespace.addCategoryObject('elementBinding', AbstractTimePrimitiveGroup.name().localName(), AbstractTimePrimitiveGroup)

LabelStyle = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'LabelStyle'), LabelStyleType)
Namespace.addCategoryObject('elementBinding', LabelStyle.name().localName(), LabelStyle)

AbstractTimePrimitiveSimpleExtensionGroup = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'AbstractTimePrimitiveSimpleExtensionGroup'), pyxb.binding.datatypes.anySimpleType, abstract=pyxb.binding.datatypes.boolean(1))
Namespace.addCategoryObject('elementBinding', AbstractTimePrimitiveSimpleExtensionGroup.name().localName(), AbstractTimePrimitiveSimpleExtensionGroup)

AbstractContainerSimpleExtensionGroup = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'AbstractContainerSimpleExtensionGroup'), pyxb.binding.datatypes.anySimpleType, abstract=pyxb.binding.datatypes.boolean(1))
Namespace.addCategoryObject('elementBinding', AbstractContainerSimpleExtensionGroup.name().localName(), AbstractContainerSimpleExtensionGroup)

AbstractTimePrimitiveObjectExtensionGroup = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'AbstractTimePrimitiveObjectExtensionGroup'), pyxb.binding.datatypes.anyType, abstract=pyxb.binding.datatypes.boolean(1))
Namespace.addCategoryObject('elementBinding', AbstractTimePrimitiveObjectExtensionGroup.name().localName(), AbstractTimePrimitiveObjectExtensionGroup)

roll = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'roll'), angle180Type)
Namespace.addCategoryObject('elementBinding', roll.name().localName(), roll)

LineStyle = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'LineStyle'), LineStyleType)
Namespace.addCategoryObject('elementBinding', LineStyle.name().localName(), LineStyle)

AbstractGeometrySimpleExtensionGroup = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'AbstractGeometrySimpleExtensionGroup'), pyxb.binding.datatypes.anySimpleType, abstract=pyxb.binding.datatypes.boolean(1))
Namespace.addCategoryObject('elementBinding', AbstractGeometrySimpleExtensionGroup.name().localName(), AbstractGeometrySimpleExtensionGroup)

LineStyleObjectExtensionGroup = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'LineStyleObjectExtensionGroup'), pyxb.binding.datatypes.anyType, abstract=pyxb.binding.datatypes.boolean(1))
Namespace.addCategoryObject('elementBinding', LineStyleObjectExtensionGroup.name().localName(), LineStyleObjectExtensionGroup)

PolyStyle = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'PolyStyle'), PolyStyleType)
Namespace.addCategoryObject('elementBinding', PolyStyle.name().localName(), PolyStyle)

AbstractColorStyleSimpleExtensionGroup = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'AbstractColorStyleSimpleExtensionGroup'), pyxb.binding.datatypes.anySimpleType, abstract=pyxb.binding.datatypes.boolean(1))
Namespace.addCategoryObject('elementBinding', AbstractColorStyleSimpleExtensionGroup.name().localName(), AbstractColorStyleSimpleExtensionGroup)

flyToView = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'flyToView'), pyxb.binding.datatypes.boolean)
Namespace.addCategoryObject('elementBinding', flyToView.name().localName(), flyToView)

scale = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'scale'), pyxb.binding.datatypes.double)
Namespace.addCategoryObject('elementBinding', scale.name().localName(), scale)

AbstractOverlayGroup = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'AbstractOverlayGroup'), AbstractOverlayType, abstract=pyxb.binding.datatypes.boolean(1))
Namespace.addCategoryObject('elementBinding', AbstractOverlayGroup.name().localName(), AbstractOverlayGroup)

PolyStyleObjectExtensionGroup = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'PolyStyleObjectExtensionGroup'), pyxb.binding.datatypes.anyType, abstract=pyxb.binding.datatypes.boolean(1))
Namespace.addCategoryObject('elementBinding', PolyStyleObjectExtensionGroup.name().localName(), PolyStyleObjectExtensionGroup)

UpdateOpExtensionGroup = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'UpdateOpExtensionGroup'), pyxb.binding.datatypes.anyType, abstract=pyxb.binding.datatypes.boolean(1))
Namespace.addCategoryObject('elementBinding', UpdateOpExtensionGroup.name().localName(), UpdateOpExtensionGroup)

shape = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'shape'), shapeEnumType)
Namespace.addCategoryObject('elementBinding', shape.name().localName(), shape)

rightFov = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'rightFov'), angle180Type)
Namespace.addCategoryObject('elementBinding', rightFov.name().localName(), rightFov)

gridOrigin = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'gridOrigin'), gridOriginEnumType)
Namespace.addCategoryObject('elementBinding', gridOrigin.name().localName(), gridOrigin)

AbstractContainerGroup = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'AbstractContainerGroup'), AbstractContainerType, abstract=pyxb.binding.datatypes.boolean(1))
Namespace.addCategoryObject('elementBinding', AbstractContainerGroup.name().localName(), AbstractContainerGroup)

Url = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Url'), LinkType, documentation=u'Url deprecated in 2.2')
Namespace.addCategoryObject('elementBinding', Url.name().localName(), Url)

LodObjectExtensionGroup = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'LodObjectExtensionGroup'), pyxb.binding.datatypes.anyType, abstract=pyxb.binding.datatypes.boolean(1))
Namespace.addCategoryObject('elementBinding', LodObjectExtensionGroup.name().localName(), LodObjectExtensionGroup)

AbstractSubStyleSimpleExtensionGroup = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'AbstractSubStyleSimpleExtensionGroup'), pyxb.binding.datatypes.anySimpleType, abstract=pyxb.binding.datatypes.boolean(1))
Namespace.addCategoryObject('elementBinding', AbstractSubStyleSimpleExtensionGroup.name().localName(), AbstractSubStyleSimpleExtensionGroup)

targetHref = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'targetHref'), pyxb.binding.datatypes.anyURI)
Namespace.addCategoryObject('elementBinding', targetHref.name().localName(), targetHref)

heading = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'heading'), angle360Type)
Namespace.addCategoryObject('elementBinding', heading.name().localName(), heading)

bgColor = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'bgColor'), colorType)
Namespace.addCategoryObject('elementBinding', bgColor.name().localName(), bgColor)

text = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'text'), pyxb.binding.datatypes.string)
Namespace.addCategoryObject('elementBinding', text.name().localName(), text)

AbstractGeometryObjectExtensionGroup = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'AbstractGeometryObjectExtensionGroup'), pyxb.binding.datatypes.anyType, abstract=pyxb.binding.datatypes.boolean(1))
Namespace.addCategoryObject('elementBinding', AbstractGeometryObjectExtensionGroup.name().localName(), AbstractGeometryObjectExtensionGroup)

Camera = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Camera'), CameraType)
Namespace.addCategoryObject('elementBinding', Camera.name().localName(), Camera)

tileSize = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'tileSize'), pyxb.binding.datatypes.int)
Namespace.addCategoryObject('elementBinding', tileSize.name().localName(), tileSize)

ViewVolumeSimpleExtensionGroup = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'ViewVolumeSimpleExtensionGroup'), pyxb.binding.datatypes.anySimpleType, abstract=pyxb.binding.datatypes.boolean(1))
Namespace.addCategoryObject('elementBinding', ViewVolumeSimpleExtensionGroup.name().localName(), ViewVolumeSimpleExtensionGroup)

ViewVolumeObjectExtensionGroup = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'ViewVolumeObjectExtensionGroup'), pyxb.binding.datatypes.anyType, abstract=pyxb.binding.datatypes.boolean(1))
Namespace.addCategoryObject('elementBinding', ViewVolumeObjectExtensionGroup.name().localName(), ViewVolumeObjectExtensionGroup)

GroundOverlay = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'GroundOverlay'), GroundOverlayType)
Namespace.addCategoryObject('elementBinding', GroundOverlay.name().localName(), GroundOverlay)

ImagePyramid = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'ImagePyramid'), ImagePyramidType)
Namespace.addCategoryObject('elementBinding', ImagePyramid.name().localName(), ImagePyramid)

displayName = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'displayName'), pyxb.binding.datatypes.string)
Namespace.addCategoryObject('elementBinding', displayName.name().localName(), displayName)

tilt = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'tilt'), anglepos180Type)
Namespace.addCategoryObject('elementBinding', tilt.name().localName(), tilt)

topFov = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'topFov'), angle90Type)
Namespace.addCategoryObject('elementBinding', topFov.name().localName(), topFov)

href = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'href'), pyxb.binding.datatypes.string, documentation=u'not anyURI due to $[x] substitution in\n      PhotoOverlay')
Namespace.addCategoryObject('elementBinding', href.name().localName(), href)

MultiGeometryObjectExtensionGroup = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'MultiGeometryObjectExtensionGroup'), pyxb.binding.datatypes.anyType, abstract=pyxb.binding.datatypes.boolean(1))
Namespace.addCategoryObject('elementBinding', MultiGeometryObjectExtensionGroup.name().localName(), MultiGeometryObjectExtensionGroup)

CameraSimpleExtensionGroup = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'CameraSimpleExtensionGroup'), pyxb.binding.datatypes.anySimpleType, abstract=pyxb.binding.datatypes.boolean(1))
Namespace.addCategoryObject('elementBinding', CameraSimpleExtensionGroup.name().localName(), CameraSimpleExtensionGroup)

LatLonAltBoxObjectExtensionGroup = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'LatLonAltBoxObjectExtensionGroup'), pyxb.binding.datatypes.anyType, abstract=pyxb.binding.datatypes.boolean(1))
Namespace.addCategoryObject('elementBinding', LatLonAltBoxObjectExtensionGroup.name().localName(), LatLonAltBoxObjectExtensionGroup)

CameraObjectExtensionGroup = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'CameraObjectExtensionGroup'), pyxb.binding.datatypes.anyType, abstract=pyxb.binding.datatypes.boolean(1))
Namespace.addCategoryObject('elementBinding', CameraObjectExtensionGroup.name().localName(), CameraObjectExtensionGroup)

Metadata = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Metadata'), MetadataType, documentation=u'Metadata deprecated in 2.2')
Namespace.addCategoryObject('elementBinding', Metadata.name().localName(), Metadata)

SimpleFieldExtension = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'SimpleFieldExtension'), pyxb.binding.datatypes.anyType, abstract=pyxb.binding.datatypes.boolean(1))
Namespace.addCategoryObject('elementBinding', SimpleFieldExtension.name().localName(), SimpleFieldExtension)

ImagePyramidObjectExtensionGroup = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'ImagePyramidObjectExtensionGroup'), pyxb.binding.datatypes.anyType, abstract=pyxb.binding.datatypes.boolean(1))
Namespace.addCategoryObject('elementBinding', ImagePyramidObjectExtensionGroup.name().localName(), ImagePyramidObjectExtensionGroup)

NetworkLinkControlObjectExtensionGroup = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'NetworkLinkControlObjectExtensionGroup'), pyxb.binding.datatypes.anyType, abstract=pyxb.binding.datatypes.boolean(1))
Namespace.addCategoryObject('elementBinding', NetworkLinkControlObjectExtensionGroup.name().localName(), NetworkLinkControlObjectExtensionGroup)

SchemaExtension = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'SchemaExtension'), pyxb.binding.datatypes.anyType, abstract=pyxb.binding.datatypes.boolean(1))
Namespace.addCategoryObject('elementBinding', SchemaExtension.name().localName(), SchemaExtension)

ExtendedData = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'ExtendedData'), ExtendedDataType)
Namespace.addCategoryObject('elementBinding', ExtendedData.name().localName(), ExtendedData)

viewBoundScale = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'viewBoundScale'), pyxb.binding.datatypes.double)
Namespace.addCategoryObject('elementBinding', viewBoundScale.name().localName(), viewBoundScale)

StyleSimpleExtensionGroup = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'StyleSimpleExtensionGroup'), pyxb.binding.datatypes.anySimpleType, abstract=pyxb.binding.datatypes.boolean(1))
Namespace.addCategoryObject('elementBinding', StyleSimpleExtensionGroup.name().localName(), StyleSimpleExtensionGroup)

StyleObjectExtensionGroup = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'StyleObjectExtensionGroup'), pyxb.binding.datatypes.anyType, abstract=pyxb.binding.datatypes.boolean(1))
Namespace.addCategoryObject('elementBinding', StyleObjectExtensionGroup.name().localName(), StyleObjectExtensionGroup)

StyleMap = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'StyleMap'), StyleMapType)
Namespace.addCategoryObject('elementBinding', StyleMap.name().localName(), StyleMap)

AbstractColorStyleGroup = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'AbstractColorStyleGroup'), AbstractColorStyleType, abstract=pyxb.binding.datatypes.boolean(1))
Namespace.addCategoryObject('elementBinding', AbstractColorStyleGroup.name().localName(), AbstractColorStyleGroup)

AbstractStyleSelectorObjectExtensionGroup = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'AbstractStyleSelectorObjectExtensionGroup'), pyxb.binding.datatypes.anyType, abstract=pyxb.binding.datatypes.boolean(1))
Namespace.addCategoryObject('elementBinding', AbstractStyleSelectorObjectExtensionGroup.name().localName(), AbstractStyleSelectorObjectExtensionGroup)

Pair = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Pair'), PairType)
Namespace.addCategoryObject('elementBinding', Pair.name().localName(), Pair)

BasicLinkSimpleExtensionGroup = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'BasicLinkSimpleExtensionGroup'), pyxb.binding.datatypes.anySimpleType, abstract=pyxb.binding.datatypes.boolean(1))
Namespace.addCategoryObject('elementBinding', BasicLinkSimpleExtensionGroup.name().localName(), BasicLinkSimpleExtensionGroup)

PairSimpleExtensionGroup = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'PairSimpleExtensionGroup'), pyxb.binding.datatypes.anySimpleType, abstract=pyxb.binding.datatypes.boolean(1))
Namespace.addCategoryObject('elementBinding', PairSimpleExtensionGroup.name().localName(), PairSimpleExtensionGroup)

PairObjectExtensionGroup = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'PairObjectExtensionGroup'), pyxb.binding.datatypes.anyType, abstract=pyxb.binding.datatypes.boolean(1))
Namespace.addCategoryObject('elementBinding', PairObjectExtensionGroup.name().localName(), PairObjectExtensionGroup)

AbstractSubStyleGroup = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'AbstractSubStyleGroup'), AbstractSubStyleType, abstract=pyxb.binding.datatypes.boolean(1))
Namespace.addCategoryObject('elementBinding', AbstractSubStyleGroup.name().localName(), AbstractSubStyleGroup)

DataExtension = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'DataExtension'), pyxb.binding.datatypes.anyType, abstract=pyxb.binding.datatypes.boolean(1))
Namespace.addCategoryObject('elementBinding', DataExtension.name().localName(), DataExtension)

ResourceMapSimpleExtensionGroup = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'ResourceMapSimpleExtensionGroup'), pyxb.binding.datatypes.anySimpleType, abstract=pyxb.binding.datatypes.boolean(1))
Namespace.addCategoryObject('elementBinding', ResourceMapSimpleExtensionGroup.name().localName(), ResourceMapSimpleExtensionGroup)

AbstractSubStyleObjectExtensionGroup = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'AbstractSubStyleObjectExtensionGroup'), pyxb.binding.datatypes.anyType, abstract=pyxb.binding.datatypes.boolean(1))
Namespace.addCategoryObject('elementBinding', AbstractSubStyleObjectExtensionGroup.name().localName(), AbstractSubStyleObjectExtensionGroup)

AbstractContainerObjectExtensionGroup = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'AbstractContainerObjectExtensionGroup'), pyxb.binding.datatypes.anyType, abstract=pyxb.binding.datatypes.boolean(1))
Namespace.addCategoryObject('elementBinding', AbstractContainerObjectExtensionGroup.name().localName(), AbstractContainerObjectExtensionGroup)

ResourceMapObjectExtensionGroup = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'ResourceMapObjectExtensionGroup'), pyxb.binding.datatypes.anyType, abstract=pyxb.binding.datatypes.boolean(1))
Namespace.addCategoryObject('elementBinding', ResourceMapObjectExtensionGroup.name().localName(), ResourceMapObjectExtensionGroup)

MultiGeometrySimpleExtensionGroup = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'MultiGeometrySimpleExtensionGroup'), pyxb.binding.datatypes.anySimpleType, abstract=pyxb.binding.datatypes.boolean(1))
Namespace.addCategoryObject('elementBinding', MultiGeometrySimpleExtensionGroup.name().localName(), MultiGeometrySimpleExtensionGroup)

Point = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Point'), PointType)
Namespace.addCategoryObject('elementBinding', Point.name().localName(), Point)

Schema = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Schema'), SchemaType)
Namespace.addCategoryObject('elementBinding', Schema.name().localName(), Schema)

DocumentSimpleExtensionGroup = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'DocumentSimpleExtensionGroup'), pyxb.binding.datatypes.anySimpleType, abstract=pyxb.binding.datatypes.boolean(1))
Namespace.addCategoryObject('elementBinding', DocumentSimpleExtensionGroup.name().localName(), DocumentSimpleExtensionGroup)

GroundOverlaySimpleExtensionGroup = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'GroundOverlaySimpleExtensionGroup'), pyxb.binding.datatypes.anySimpleType, abstract=pyxb.binding.datatypes.boolean(1))
Namespace.addCategoryObject('elementBinding', GroundOverlaySimpleExtensionGroup.name().localName(), GroundOverlaySimpleExtensionGroup)

GroundOverlayObjectExtensionGroup = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'GroundOverlayObjectExtensionGroup'), pyxb.binding.datatypes.anyType, abstract=pyxb.binding.datatypes.boolean(1))
Namespace.addCategoryObject('elementBinding', GroundOverlayObjectExtensionGroup.name().localName(), GroundOverlayObjectExtensionGroup)

x = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'x'), pyxb.binding.datatypes.double)
Namespace.addCategoryObject('elementBinding', x.name().localName(), x)

PointSimpleExtensionGroup = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'PointSimpleExtensionGroup'), pyxb.binding.datatypes.anySimpleType, abstract=pyxb.binding.datatypes.boolean(1))
Namespace.addCategoryObject('elementBinding', PointSimpleExtensionGroup.name().localName(), PointSimpleExtensionGroup)

PointObjectExtensionGroup = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'PointObjectExtensionGroup'), pyxb.binding.datatypes.anyType, abstract=pyxb.binding.datatypes.boolean(1))
Namespace.addCategoryObject('elementBinding', PointObjectExtensionGroup.name().localName(), PointObjectExtensionGroup)

LineString = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'LineString'), LineStringType)
Namespace.addCategoryObject('elementBinding', LineString.name().localName(), LineString)

LinkObjectExtensionGroup = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'LinkObjectExtensionGroup'), pyxb.binding.datatypes.anyType, abstract=pyxb.binding.datatypes.boolean(1))
Namespace.addCategoryObject('elementBinding', LinkObjectExtensionGroup.name().localName(), LinkObjectExtensionGroup)

AbstractLatLonBoxSimpleExtensionGroup = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'AbstractLatLonBoxSimpleExtensionGroup'), pyxb.binding.datatypes.anySimpleType, abstract=pyxb.binding.datatypes.boolean(1))
Namespace.addCategoryObject('elementBinding', AbstractLatLonBoxSimpleExtensionGroup.name().localName(), AbstractLatLonBoxSimpleExtensionGroup)

AbstractLatLonBoxObjectExtensionGroup = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'AbstractLatLonBoxObjectExtensionGroup'), pyxb.binding.datatypes.anyType, abstract=pyxb.binding.datatypes.boolean(1))
Namespace.addCategoryObject('elementBinding', AbstractLatLonBoxObjectExtensionGroup.name().localName(), AbstractLatLonBoxObjectExtensionGroup)

LatLonBox = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'LatLonBox'), LatLonBoxType)
Namespace.addCategoryObject('elementBinding', LatLonBox.name().localName(), LatLonBox)

LineStringSimpleExtensionGroup = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'LineStringSimpleExtensionGroup'), pyxb.binding.datatypes.anySimpleType, abstract=pyxb.binding.datatypes.boolean(1))
Namespace.addCategoryObject('elementBinding', LineStringSimpleExtensionGroup.name().localName(), LineStringSimpleExtensionGroup)

LineStringObjectExtensionGroup = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'LineStringObjectExtensionGroup'), pyxb.binding.datatypes.anyType, abstract=pyxb.binding.datatypes.boolean(1))
Namespace.addCategoryObject('elementBinding', LineStringObjectExtensionGroup.name().localName(), LineStringObjectExtensionGroup)

kml = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'kml'), KmlType, documentation=u'\n\n      <kml> is the root element.\n\n      ')
Namespace.addCategoryObject('elementBinding', kml.name().localName(), kml)

LatLonBoxSimpleExtensionGroup = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'LatLonBoxSimpleExtensionGroup'), pyxb.binding.datatypes.anySimpleType, abstract=pyxb.binding.datatypes.boolean(1))
Namespace.addCategoryObject('elementBinding', LatLonBoxSimpleExtensionGroup.name().localName(), LatLonBoxSimpleExtensionGroup)

LatLonBoxObjectExtensionGroup = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'LatLonBoxObjectExtensionGroup'), pyxb.binding.datatypes.anyType, abstract=pyxb.binding.datatypes.boolean(1))
Namespace.addCategoryObject('elementBinding', LatLonBoxObjectExtensionGroup.name().localName(), LatLonBoxObjectExtensionGroup)

IconStyleSimpleExtensionGroup = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'IconStyleSimpleExtensionGroup'), pyxb.binding.datatypes.anySimpleType, abstract=pyxb.binding.datatypes.boolean(1))
Namespace.addCategoryObject('elementBinding', IconStyleSimpleExtensionGroup.name().localName(), IconStyleSimpleExtensionGroup)

LinearRingSimpleExtensionGroup = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'LinearRingSimpleExtensionGroup'), pyxb.binding.datatypes.anySimpleType, abstract=pyxb.binding.datatypes.boolean(1))
Namespace.addCategoryObject('elementBinding', LinearRingSimpleExtensionGroup.name().localName(), LinearRingSimpleExtensionGroup)

LabelStyleSimpleExtensionGroup = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'LabelStyleSimpleExtensionGroup'), pyxb.binding.datatypes.anySimpleType, abstract=pyxb.binding.datatypes.boolean(1))
Namespace.addCategoryObject('elementBinding', LabelStyleSimpleExtensionGroup.name().localName(), LabelStyleSimpleExtensionGroup)

Polygon = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Polygon'), PolygonType)
Namespace.addCategoryObject('elementBinding', Polygon.name().localName(), Polygon)

maxWidth = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'maxWidth'), pyxb.binding.datatypes.int)
Namespace.addCategoryObject('elementBinding', maxWidth.name().localName(), maxWidth)

address = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'address'), pyxb.binding.datatypes.string)
Namespace.addCategoryObject('elementBinding', address.name().localName(), address)

LabelStyleObjectExtensionGroup = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'LabelStyleObjectExtensionGroup'), pyxb.binding.datatypes.anyType, abstract=pyxb.binding.datatypes.boolean(1))
Namespace.addCategoryObject('elementBinding', LabelStyleObjectExtensionGroup.name().localName(), LabelStyleObjectExtensionGroup)

ScreenOverlayObjectExtensionGroup = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'ScreenOverlayObjectExtensionGroup'), pyxb.binding.datatypes.anyType, abstract=pyxb.binding.datatypes.boolean(1))
Namespace.addCategoryObject('elementBinding', ScreenOverlayObjectExtensionGroup.name().localName(), ScreenOverlayObjectExtensionGroup)

PhotoOverlay = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'PhotoOverlay'), PhotoOverlayType)
Namespace.addCategoryObject('elementBinding', PhotoOverlay.name().localName(), PhotoOverlay)

PolygonSimpleExtensionGroup = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'PolygonSimpleExtensionGroup'), pyxb.binding.datatypes.anySimpleType, abstract=pyxb.binding.datatypes.boolean(1))
Namespace.addCategoryObject('elementBinding', PolygonSimpleExtensionGroup.name().localName(), PolygonSimpleExtensionGroup)

PolygonObjectExtensionGroup = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'PolygonObjectExtensionGroup'), pyxb.binding.datatypes.anyType, abstract=pyxb.binding.datatypes.boolean(1))
Namespace.addCategoryObject('elementBinding', PolygonObjectExtensionGroup.name().localName(), PolygonObjectExtensionGroup)

outerBoundaryIs = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'outerBoundaryIs'), BoundaryType)
Namespace.addCategoryObject('elementBinding', outerBoundaryIs.name().localName(), outerBoundaryIs)

TimeStamp = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'TimeStamp'), TimeStampType)
Namespace.addCategoryObject('elementBinding', TimeStamp.name().localName(), TimeStamp)

innerBoundaryIs = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'innerBoundaryIs'), BoundaryType)
Namespace.addCategoryObject('elementBinding', innerBoundaryIs.name().localName(), innerBoundaryIs)

PhotoOverlaySimpleExtensionGroup = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'PhotoOverlaySimpleExtensionGroup'), pyxb.binding.datatypes.anySimpleType, abstract=pyxb.binding.datatypes.boolean(1))
Namespace.addCategoryObject('elementBinding', PhotoOverlaySimpleExtensionGroup.name().localName(), PhotoOverlaySimpleExtensionGroup)

PhotoOverlayObjectExtensionGroup = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'PhotoOverlayObjectExtensionGroup'), pyxb.binding.datatypes.anyType, abstract=pyxb.binding.datatypes.boolean(1))
Namespace.addCategoryObject('elementBinding', PhotoOverlayObjectExtensionGroup.name().localName(), PhotoOverlayObjectExtensionGroup)

ViewVolume = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'ViewVolume'), ViewVolumeType)
Namespace.addCategoryObject('elementBinding', ViewVolume.name().localName(), ViewVolume)

BoundarySimpleExtensionGroup = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'BoundarySimpleExtensionGroup'), pyxb.binding.datatypes.anySimpleType, abstract=pyxb.binding.datatypes.boolean(1))
Namespace.addCategoryObject('elementBinding', BoundarySimpleExtensionGroup.name().localName(), BoundarySimpleExtensionGroup)

ObjectSimpleExtensionGroup = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'ObjectSimpleExtensionGroup'), pyxb.binding.datatypes.anySimpleType, abstract=pyxb.binding.datatypes.boolean(1))
Namespace.addCategoryObject('elementBinding', ObjectSimpleExtensionGroup.name().localName(), ObjectSimpleExtensionGroup)

BoundaryObjectExtensionGroup = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'BoundaryObjectExtensionGroup'), pyxb.binding.datatypes.anyType, abstract=pyxb.binding.datatypes.boolean(1))
Namespace.addCategoryObject('elementBinding', BoundaryObjectExtensionGroup.name().localName(), BoundaryObjectExtensionGroup)

Model = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Model'), ModelType)
Namespace.addCategoryObject('elementBinding', Model.name().localName(), Model)

AbstractFeatureGroup = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'AbstractFeatureGroup'), AbstractFeatureType, abstract=pyxb.binding.datatypes.boolean(1))
Namespace.addCategoryObject('elementBinding', AbstractFeatureGroup.name().localName(), AbstractFeatureGroup)

LookAtObjectExtensionGroup = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'LookAtObjectExtensionGroup'), pyxb.binding.datatypes.anyType, abstract=pyxb.binding.datatypes.boolean(1))
Namespace.addCategoryObject('elementBinding', LookAtObjectExtensionGroup.name().localName(), LookAtObjectExtensionGroup)

ModelSimpleExtensionGroup = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'ModelSimpleExtensionGroup'), pyxb.binding.datatypes.anySimpleType, abstract=pyxb.binding.datatypes.boolean(1))
Namespace.addCategoryObject('elementBinding', ModelSimpleExtensionGroup.name().localName(), ModelSimpleExtensionGroup)

LineStyleSimpleExtensionGroup = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'LineStyleSimpleExtensionGroup'), pyxb.binding.datatypes.anySimpleType, abstract=pyxb.binding.datatypes.boolean(1))
Namespace.addCategoryObject('elementBinding', LineStyleSimpleExtensionGroup.name().localName(), LineStyleSimpleExtensionGroup)

LinearRing = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'LinearRing'), LinearRingType)
Namespace.addCategoryObject('elementBinding', LinearRing.name().localName(), LinearRing)

latitude = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'latitude'), angle90Type)
Namespace.addCategoryObject('elementBinding', latitude.name().localName(), latitude)

AbstractFeatureObjectExtensionGroup = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'AbstractFeatureObjectExtensionGroup'), pyxb.binding.datatypes.anyType, abstract=pyxb.binding.datatypes.boolean(1))
Namespace.addCategoryObject('elementBinding', AbstractFeatureObjectExtensionGroup.name().localName(), AbstractFeatureObjectExtensionGroup)

AbstractFeatureSimpleExtensionGroup = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'AbstractFeatureSimpleExtensionGroup'), pyxb.binding.datatypes.anySimpleType, abstract=pyxb.binding.datatypes.boolean(1))
Namespace.addCategoryObject('elementBinding', AbstractFeatureSimpleExtensionGroup.name().localName(), AbstractFeatureSimpleExtensionGroup)

Snippet = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Snippet'), SnippetType)
Namespace.addCategoryObject('elementBinding', Snippet.name().localName(), Snippet)

AbstractViewGroup = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'AbstractViewGroup'), AbstractViewType, abstract=pyxb.binding.datatypes.boolean(1))
Namespace.addCategoryObject('elementBinding', AbstractViewGroup.name().localName(), AbstractViewGroup)

Update = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Update'), UpdateType)
Namespace.addCategoryObject('elementBinding', Update.name().localName(), Update)

StyleMapSimpleExtensionGroup = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'StyleMapSimpleExtensionGroup'), pyxb.binding.datatypes.anySimpleType, abstract=pyxb.binding.datatypes.boolean(1))
Namespace.addCategoryObject('elementBinding', StyleMapSimpleExtensionGroup.name().localName(), StyleMapSimpleExtensionGroup)

SimpleData = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'SimpleData'), SimpleDataType)
Namespace.addCategoryObject('elementBinding', SimpleData.name().localName(), SimpleData)

LookAt = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'LookAt'), LookAtType)
Namespace.addCategoryObject('elementBinding', LookAt.name().localName(), LookAt)

listItemType = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'listItemType'), listItemTypeEnumType)
Namespace.addCategoryObject('elementBinding', listItemType.name().localName(), listItemType)

ScreenOverlay = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'ScreenOverlay'), ScreenOverlayType)
Namespace.addCategoryObject('elementBinding', ScreenOverlay.name().localName(), ScreenOverlay)

UpdateExtensionGroup = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'UpdateExtensionGroup'), pyxb.binding.datatypes.anyType, abstract=pyxb.binding.datatypes.boolean(1))
Namespace.addCategoryObject('elementBinding', UpdateExtensionGroup.name().localName(), UpdateExtensionGroup)

Create = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Create'), CreateType)
Namespace.addCategoryObject('elementBinding', Create.name().localName(), Create)

NetworkLinkObjectExtensionGroup = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'NetworkLinkObjectExtensionGroup'), pyxb.binding.datatypes.anyType, abstract=pyxb.binding.datatypes.boolean(1))
Namespace.addCategoryObject('elementBinding', NetworkLinkObjectExtensionGroup.name().localName(), NetworkLinkObjectExtensionGroup)

Region = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Region'), RegionType)
Namespace.addCategoryObject('elementBinding', Region.name().localName(), Region)

minFadeExtent = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'minFadeExtent'), pyxb.binding.datatypes.double)
Namespace.addCategoryObject('elementBinding', minFadeExtent.name().localName(), minFadeExtent)

minLodPixels = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'minLodPixels'), pyxb.binding.datatypes.double)
Namespace.addCategoryObject('elementBinding', minLodPixels.name().localName(), minLodPixels)

Delete = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Delete'), DeleteType)
Namespace.addCategoryObject('elementBinding', Delete.name().localName(), Delete)

maxAltitude = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'maxAltitude'), pyxb.binding.datatypes.double)
Namespace.addCategoryObject('elementBinding', maxAltitude.name().localName(), maxAltitude)

maxFadeExtent = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'maxFadeExtent'), pyxb.binding.datatypes.double)
Namespace.addCategoryObject('elementBinding', maxFadeExtent.name().localName(), maxFadeExtent)

maxLodPixels = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'maxLodPixels'), pyxb.binding.datatypes.double)
Namespace.addCategoryObject('elementBinding', maxLodPixels.name().localName(), maxLodPixels)

maxHeight = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'maxHeight'), pyxb.binding.datatypes.int)
Namespace.addCategoryObject('elementBinding', maxHeight.name().localName(), maxHeight)

altitudeMode = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'altitudeMode'), altitudeModeEnumType)
Namespace.addCategoryObject('elementBinding', altitudeMode.name().localName(), altitudeMode)

RegionSimpleExtensionGroup = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'RegionSimpleExtensionGroup'), pyxb.binding.datatypes.anySimpleType, abstract=pyxb.binding.datatypes.boolean(1))
Namespace.addCategoryObject('elementBinding', RegionSimpleExtensionGroup.name().localName(), RegionSimpleExtensionGroup)

name = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'name'), pyxb.binding.datatypes.string)
Namespace.addCategoryObject('elementBinding', name.name().localName(), name)

LatLonAltBox = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'LatLonAltBox'), LatLonAltBoxType)
Namespace.addCategoryObject('elementBinding', LatLonAltBox.name().localName(), LatLonAltBox)

open = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'open'), pyxb.binding.datatypes.boolean)
Namespace.addCategoryObject('elementBinding', open.name().localName(), open)

phoneNumber = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'phoneNumber'), pyxb.binding.datatypes.string)
Namespace.addCategoryObject('elementBinding', phoneNumber.name().localName(), phoneNumber)

LocationObjectExtensionGroup = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'LocationObjectExtensionGroup'), pyxb.binding.datatypes.anyType, abstract=pyxb.binding.datatypes.boolean(1))
Namespace.addCategoryObject('elementBinding', LocationObjectExtensionGroup.name().localName(), LocationObjectExtensionGroup)

Orientation = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Orientation'), OrientationType)
Namespace.addCategoryObject('elementBinding', Orientation.name().localName(), Orientation)

PolyStyleSimpleExtensionGroup = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'PolyStyleSimpleExtensionGroup'), pyxb.binding.datatypes.anySimpleType, abstract=pyxb.binding.datatypes.boolean(1))
Namespace.addCategoryObject('elementBinding', PolyStyleSimpleExtensionGroup.name().localName(), PolyStyleSimpleExtensionGroup)

refreshInterval = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'refreshInterval'), pyxb.binding.datatypes.double)
Namespace.addCategoryObject('elementBinding', refreshInterval.name().localName(), refreshInterval)

LatLonAltBoxSimpleExtensionGroup = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'LatLonAltBoxSimpleExtensionGroup'), pyxb.binding.datatypes.anySimpleType, abstract=pyxb.binding.datatypes.boolean(1))
Namespace.addCategoryObject('elementBinding', LatLonAltBoxSimpleExtensionGroup.name().localName(), LatLonAltBoxSimpleExtensionGroup)

Folder = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Folder'), FolderType)
Namespace.addCategoryObject('elementBinding', Folder.name().localName(), Folder)

Lod = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Lod'), LodType)
Namespace.addCategoryObject('elementBinding', Lod.name().localName(), Lod)

rotation = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'rotation'), angle180Type)
Namespace.addCategoryObject('elementBinding', rotation.name().localName(), rotation)

KmlSimpleExtensionGroup = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'KmlSimpleExtensionGroup'), pyxb.binding.datatypes.anySimpleType, abstract=pyxb.binding.datatypes.boolean(1))
Namespace.addCategoryObject('elementBinding', KmlSimpleExtensionGroup.name().localName(), KmlSimpleExtensionGroup)

rotationXY = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'rotationXY'), vec2Type)
Namespace.addCategoryObject('elementBinding', rotationXY.name().localName(), rotationXY)

screenXY = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'screenXY'), vec2Type)
Namespace.addCategoryObject('elementBinding', screenXY.name().localName(), screenXY)

LinearRingObjectExtensionGroup = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'LinearRingObjectExtensionGroup'), pyxb.binding.datatypes.anyType, abstract=pyxb.binding.datatypes.boolean(1))
Namespace.addCategoryObject('elementBinding', LinearRingObjectExtensionGroup.name().localName(), LinearRingObjectExtensionGroup)

size = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'size'), vec2Type)
Namespace.addCategoryObject('elementBinding', size.name().localName(), size)

south = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'south'), angle180Type)
Namespace.addCategoryObject('elementBinding', south.name().localName(), south)

sourceHref = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'sourceHref'), pyxb.binding.datatypes.anyURI)
Namespace.addCategoryObject('elementBinding', sourceHref.name().localName(), sourceHref)

BalloonStyle = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'BalloonStyle'), BalloonStyleType)
Namespace.addCategoryObject('elementBinding', BalloonStyle.name().localName(), BalloonStyle)

snippet = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'snippet'), pyxb.binding.datatypes.string)
Namespace.addCategoryObject('elementBinding', snippet.name().localName(), snippet)

Icon = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Icon'), LinkType)
Namespace.addCategoryObject('elementBinding', Icon.name().localName(), Icon)

Link = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Link'), LinkType)
Namespace.addCategoryObject('elementBinding', Link.name().localName(), Link)

textColor = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'textColor'), colorType)
Namespace.addCategoryObject('elementBinding', textColor.name().localName(), textColor)

ScaleSimpleExtensionGroup = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'ScaleSimpleExtensionGroup'), pyxb.binding.datatypes.anySimpleType, abstract=pyxb.binding.datatypes.boolean(1))
Namespace.addCategoryObject('elementBinding', ScaleSimpleExtensionGroup.name().localName(), ScaleSimpleExtensionGroup)

ScaleObjectExtensionGroup = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'ScaleObjectExtensionGroup'), pyxb.binding.datatypes.anyType, abstract=pyxb.binding.datatypes.boolean(1))
Namespace.addCategoryObject('elementBinding', ScaleObjectExtensionGroup.name().localName(), ScaleObjectExtensionGroup)

ResourceMap = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'ResourceMap'), ResourceMapType)
Namespace.addCategoryObject('elementBinding', ResourceMap.name().localName(), ResourceMap)

ImagePyramidSimpleExtensionGroup = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'ImagePyramidSimpleExtensionGroup'), pyxb.binding.datatypes.anySimpleType, abstract=pyxb.binding.datatypes.boolean(1))
Namespace.addCategoryObject('elementBinding', ImagePyramidSimpleExtensionGroup.name().localName(), ImagePyramidSimpleExtensionGroup)

value = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'value'), pyxb.binding.datatypes.string)
Namespace.addCategoryObject('elementBinding', value.name().localName(), value)

viewFormat = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'viewFormat'), pyxb.binding.datatypes.string)
Namespace.addCategoryObject('elementBinding', viewFormat.name().localName(), viewFormat)

viewRefreshMode = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'viewRefreshMode'), viewRefreshModeEnumType)
Namespace.addCategoryObject('elementBinding', viewRefreshMode.name().localName(), viewRefreshMode)

cookie = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'cookie'), pyxb.binding.datatypes.string)
Namespace.addCategoryObject('elementBinding', cookie.name().localName(), cookie)

viewRefreshTime = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'viewRefreshTime'), pyxb.binding.datatypes.double)
Namespace.addCategoryObject('elementBinding', viewRefreshTime.name().localName(), viewRefreshTime)

AbstractViewSimpleExtensionGroup = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'AbstractViewSimpleExtensionGroup'), pyxb.binding.datatypes.anySimpleType, abstract=pyxb.binding.datatypes.boolean(1))
Namespace.addCategoryObject('elementBinding', AbstractViewSimpleExtensionGroup.name().localName(), AbstractViewSimpleExtensionGroup)

visibility = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'visibility'), pyxb.binding.datatypes.boolean)
Namespace.addCategoryObject('elementBinding', visibility.name().localName(), visibility)

west = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'west'), angle180Type)
Namespace.addCategoryObject('elementBinding', west.name().localName(), west)

Alias = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Alias'), AliasType)
Namespace.addCategoryObject('elementBinding', Alias.name().localName(), Alias)

LinkSimpleExtensionGroup = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'LinkSimpleExtensionGroup'), pyxb.binding.datatypes.anySimpleType, abstract=pyxb.binding.datatypes.boolean(1))
Namespace.addCategoryObject('elementBinding', LinkSimpleExtensionGroup.name().localName(), LinkSimpleExtensionGroup)

TimeStampSimpleExtensionGroup = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'TimeStampSimpleExtensionGroup'), pyxb.binding.datatypes.anySimpleType, abstract=pyxb.binding.datatypes.boolean(1))
Namespace.addCategoryObject('elementBinding', TimeStampSimpleExtensionGroup.name().localName(), TimeStampSimpleExtensionGroup)

MultiGeometry = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'MultiGeometry'), MultiGeometryType)
Namespace.addCategoryObject('elementBinding', MultiGeometry.name().localName(), MultiGeometry)

Style = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Style'), StyleType)
Namespace.addCategoryObject('elementBinding', Style.name().localName(), Style)

AbstractObjectGroup = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'AbstractObjectGroup'), AbstractObjectType, abstract=pyxb.binding.datatypes.boolean(1))
Namespace.addCategoryObject('elementBinding', AbstractObjectGroup.name().localName(), AbstractObjectGroup)

when = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'when'), dateTimeType)
Namespace.addCategoryObject('elementBinding', when.name().localName(), when)

LookAtSimpleExtensionGroup = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'LookAtSimpleExtensionGroup'), pyxb.binding.datatypes.anySimpleType, abstract=pyxb.binding.datatypes.boolean(1))
Namespace.addCategoryObject('elementBinding', LookAtSimpleExtensionGroup.name().localName(), LookAtSimpleExtensionGroup)

description = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'description'), pyxb.binding.datatypes.string)
Namespace.addCategoryObject('elementBinding', description.name().localName(), description)

AliasSimpleExtensionGroup = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'AliasSimpleExtensionGroup'), pyxb.binding.datatypes.anySimpleType, abstract=pyxb.binding.datatypes.boolean(1))
Namespace.addCategoryObject('elementBinding', AliasSimpleExtensionGroup.name().localName(), AliasSimpleExtensionGroup)

AliasObjectExtensionGroup = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'AliasObjectExtensionGroup'), pyxb.binding.datatypes.anyType, abstract=pyxb.binding.datatypes.boolean(1))
Namespace.addCategoryObject('elementBinding', AliasObjectExtensionGroup.name().localName(), AliasObjectExtensionGroup)

FolderSimpleExtensionGroup = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'FolderSimpleExtensionGroup'), pyxb.binding.datatypes.anySimpleType, abstract=pyxb.binding.datatypes.boolean(1))
Namespace.addCategoryObject('elementBinding', FolderSimpleExtensionGroup.name().localName(), FolderSimpleExtensionGroup)

OrientationSimpleExtensionGroup = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'OrientationSimpleExtensionGroup'), pyxb.binding.datatypes.anySimpleType, abstract=pyxb.binding.datatypes.boolean(1))
Namespace.addCategoryObject('elementBinding', OrientationSimpleExtensionGroup.name().localName(), OrientationSimpleExtensionGroup)

KmlObjectExtensionGroup = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'KmlObjectExtensionGroup'), pyxb.binding.datatypes.anyType, abstract=pyxb.binding.datatypes.boolean(1))
Namespace.addCategoryObject('elementBinding', KmlObjectExtensionGroup.name().localName(), KmlObjectExtensionGroup)

longitude = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'longitude'), angle180Type)
Namespace.addCategoryObject('elementBinding', longitude.name().localName(), longitude)

AbstractViewObjectExtensionGroup = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'AbstractViewObjectExtensionGroup'), pyxb.binding.datatypes.anyType, abstract=pyxb.binding.datatypes.boolean(1))
Namespace.addCategoryObject('elementBinding', AbstractViewObjectExtensionGroup.name().localName(), AbstractViewObjectExtensionGroup)

width = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'width'), pyxb.binding.datatypes.double)
Namespace.addCategoryObject('elementBinding', width.name().localName(), width)

NetworkLinkSimpleExtensionGroup = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'NetworkLinkSimpleExtensionGroup'), pyxb.binding.datatypes.anySimpleType, abstract=pyxb.binding.datatypes.boolean(1))
Namespace.addCategoryObject('elementBinding', NetworkLinkSimpleExtensionGroup.name().localName(), NetworkLinkSimpleExtensionGroup)

state = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'state'), itemIconStateType)
Namespace.addCategoryObject('elementBinding', state.name().localName(), state)

maxSnippetLines = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'maxSnippetLines'), pyxb.binding.datatypes.int)
Namespace.addCategoryObject('elementBinding', maxSnippetLines.name().localName(), maxSnippetLines)

FolderObjectExtensionGroup = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'FolderObjectExtensionGroup'), pyxb.binding.datatypes.anyType, abstract=pyxb.binding.datatypes.boolean(1))
Namespace.addCategoryObject('elementBinding', FolderObjectExtensionGroup.name().localName(), FolderObjectExtensionGroup)

OrientationObjectExtensionGroup = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'OrientationObjectExtensionGroup'), pyxb.binding.datatypes.anyType, abstract=pyxb.binding.datatypes.boolean(1))
Namespace.addCategoryObject('elementBinding', OrientationObjectExtensionGroup.name().localName(), OrientationObjectExtensionGroup)

NetworkLinkControl = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'NetworkLinkControl'), NetworkLinkControlType)
Namespace.addCategoryObject('elementBinding', NetworkLinkControl.name().localName(), NetworkLinkControl)

SchemaDataExtension = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'SchemaDataExtension'), pyxb.binding.datatypes.anyType, abstract=pyxb.binding.datatypes.boolean(1))
Namespace.addCategoryObject('elementBinding', SchemaDataExtension.name().localName(), SchemaDataExtension)

minRefreshPeriod = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'minRefreshPeriod'), pyxb.binding.datatypes.double)
Namespace.addCategoryObject('elementBinding', minRefreshPeriod.name().localName(), minRefreshPeriod)

styleUrl = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'styleUrl'), pyxb.binding.datatypes.anyURI)
Namespace.addCategoryObject('elementBinding', styleUrl.name().localName(), styleUrl)

TimeSpanObjectExtensionGroup = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'TimeSpanObjectExtensionGroup'), pyxb.binding.datatypes.anyType, abstract=pyxb.binding.datatypes.boolean(1))
Namespace.addCategoryObject('elementBinding', TimeSpanObjectExtensionGroup.name().localName(), TimeSpanObjectExtensionGroup)

maxSessionLength = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'maxSessionLength'), pyxb.binding.datatypes.double)
Namespace.addCategoryObject('elementBinding', maxSessionLength.name().localName(), maxSessionLength)

Placemark = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Placemark'), PlacemarkType)
Namespace.addCategoryObject('elementBinding', Placemark.name().localName(), Placemark)

Scale = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Scale'), ScaleType)
Namespace.addCategoryObject('elementBinding', Scale.name().localName(), Scale)

NetworkLinkControlSimpleExtensionGroup = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'NetworkLinkControlSimpleExtensionGroup'), pyxb.binding.datatypes.anySimpleType, abstract=pyxb.binding.datatypes.boolean(1))
Namespace.addCategoryObject('elementBinding', NetworkLinkControlSimpleExtensionGroup.name().localName(), NetworkLinkControlSimpleExtensionGroup)

ModelObjectExtensionGroup = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'ModelObjectExtensionGroup'), pyxb.binding.datatypes.anyType, abstract=pyxb.binding.datatypes.boolean(1))
Namespace.addCategoryObject('elementBinding', ModelObjectExtensionGroup.name().localName(), ModelObjectExtensionGroup)

Document = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Document'), DocumentType)
Namespace.addCategoryObject('elementBinding', Document.name().localName(), Document)

SchemaData = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'SchemaData'), SchemaDataType)
Namespace.addCategoryObject('elementBinding', SchemaData.name().localName(), SchemaData)

Location = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Location'), LocationType)
Namespace.addCategoryObject('elementBinding', Location.name().localName(), Location)

BalloonStyleSimpleExtensionGroup = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'BalloonStyleSimpleExtensionGroup'), pyxb.binding.datatypes.anySimpleType, abstract=pyxb.binding.datatypes.boolean(1))
Namespace.addCategoryObject('elementBinding', BalloonStyleSimpleExtensionGroup.name().localName(), BalloonStyleSimpleExtensionGroup)

BalloonStyleObjectExtensionGroup = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'BalloonStyleObjectExtensionGroup'), pyxb.binding.datatypes.anyType, abstract=pyxb.binding.datatypes.boolean(1))
Namespace.addCategoryObject('elementBinding', BalloonStyleObjectExtensionGroup.name().localName(), BalloonStyleObjectExtensionGroup)

ListStyle = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'ListStyle'), ListStyleType)
Namespace.addCategoryObject('elementBinding', ListStyle.name().localName(), ListStyle)

DocumentObjectExtensionGroup = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'DocumentObjectExtensionGroup'), pyxb.binding.datatypes.anyType, abstract=pyxb.binding.datatypes.boolean(1))
Namespace.addCategoryObject('elementBinding', DocumentObjectExtensionGroup.name().localName(), DocumentObjectExtensionGroup)

httpQuery = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'httpQuery'), pyxb.binding.datatypes.string)
Namespace.addCategoryObject('elementBinding', httpQuery.name().localName(), httpQuery)

y = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'y'), pyxb.binding.datatypes.double)
Namespace.addCategoryObject('elementBinding', y.name().localName(), y)

Change = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Change'), ChangeType)
Namespace.addCategoryObject('elementBinding', Change.name().localName(), Change)

ListStyleSimpleExtensionGroup = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'ListStyleSimpleExtensionGroup'), pyxb.binding.datatypes.anySimpleType, abstract=pyxb.binding.datatypes.boolean(1))
Namespace.addCategoryObject('elementBinding', ListStyleSimpleExtensionGroup.name().localName(), ListStyleSimpleExtensionGroup)

ListStyleObjectExtensionGroup = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'ListStyleObjectExtensionGroup'), pyxb.binding.datatypes.anyType, abstract=pyxb.binding.datatypes.boolean(1))
Namespace.addCategoryObject('elementBinding', ListStyleObjectExtensionGroup.name().localName(), ListStyleObjectExtensionGroup)

range = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'range'), pyxb.binding.datatypes.double)
Namespace.addCategoryObject('elementBinding', range.name().localName(), range)

ItemIcon = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'ItemIcon'), ItemIconType)
Namespace.addCategoryObject('elementBinding', ItemIcon.name().localName(), ItemIcon)

message = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'message'), pyxb.binding.datatypes.string)
Namespace.addCategoryObject('elementBinding', message.name().localName(), message)

SimpleField = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'SimpleField'), SimpleFieldType)
Namespace.addCategoryObject('elementBinding', SimpleField.name().localName(), SimpleField)

LodSimpleExtensionGroup = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'LodSimpleExtensionGroup'), pyxb.binding.datatypes.anySimpleType, abstract=pyxb.binding.datatypes.boolean(1))
Namespace.addCategoryObject('elementBinding', LodSimpleExtensionGroup.name().localName(), LodSimpleExtensionGroup)

ScreenOverlaySimpleExtensionGroup = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'ScreenOverlaySimpleExtensionGroup'), pyxb.binding.datatypes.anySimpleType, abstract=pyxb.binding.datatypes.boolean(1))
Namespace.addCategoryObject('elementBinding', ScreenOverlaySimpleExtensionGroup.name().localName(), ScreenOverlaySimpleExtensionGroup)

RegionObjectExtensionGroup = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'RegionObjectExtensionGroup'), pyxb.binding.datatypes.anyType, abstract=pyxb.binding.datatypes.boolean(1))
Namespace.addCategoryObject('elementBinding', RegionObjectExtensionGroup.name().localName(), RegionObjectExtensionGroup)

ItemIconSimpleExtensionGroup = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'ItemIconSimpleExtensionGroup'), pyxb.binding.datatypes.anySimpleType, abstract=pyxb.binding.datatypes.boolean(1))
Namespace.addCategoryObject('elementBinding', ItemIconSimpleExtensionGroup.name().localName(), ItemIconSimpleExtensionGroup)

ItemIconObjectExtensionGroup = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'ItemIconObjectExtensionGroup'), pyxb.binding.datatypes.anyType, abstract=pyxb.binding.datatypes.boolean(1))
Namespace.addCategoryObject('elementBinding', ItemIconObjectExtensionGroup.name().localName(), ItemIconObjectExtensionGroup)

near = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'near'), pyxb.binding.datatypes.double)
Namespace.addCategoryObject('elementBinding', near.name().localName(), near)

begin = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'begin'), dateTimeType)
Namespace.addCategoryObject('elementBinding', begin.name().localName(), begin)

bottomFov = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'bottomFov'), angle90Type)
Namespace.addCategoryObject('elementBinding', bottomFov.name().localName(), bottomFov)

color = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'color'), colorType)
Namespace.addCategoryObject('elementBinding', color.name().localName(), color)

colorMode = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'colorMode'), colorModeEnumType)
Namespace.addCategoryObject('elementBinding', colorMode.name().localName(), colorMode)

north = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'north'), angle180Type)
Namespace.addCategoryObject('elementBinding', north.name().localName(), north)

coordinates = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'coordinates'), coordinatesType)
Namespace.addCategoryObject('elementBinding', coordinates.name().localName(), coordinates)

TimeStampObjectExtensionGroup = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'TimeStampObjectExtensionGroup'), pyxb.binding.datatypes.anyType, abstract=pyxb.binding.datatypes.boolean(1))
Namespace.addCategoryObject('elementBinding', TimeStampObjectExtensionGroup.name().localName(), TimeStampObjectExtensionGroup)

TimeSpan = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'TimeSpan'), TimeSpanType)
Namespace.addCategoryObject('elementBinding', TimeSpan.name().localName(), TimeSpan)

displayMode = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'displayMode'), displayModeEnumType)
Namespace.addCategoryObject('elementBinding', displayMode.name().localName(), displayMode)

drawOrder = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'drawOrder'), pyxb.binding.datatypes.int)
Namespace.addCategoryObject('elementBinding', drawOrder.name().localName(), drawOrder)

BasicLinkObjectExtensionGroup = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'BasicLinkObjectExtensionGroup'), pyxb.binding.datatypes.anyType, abstract=pyxb.binding.datatypes.boolean(1))
Namespace.addCategoryObject('elementBinding', BasicLinkObjectExtensionGroup.name().localName(), BasicLinkObjectExtensionGroup)

east = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'east'), angle180Type)
Namespace.addCategoryObject('elementBinding', east.name().localName(), east)

end = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'end'), dateTimeType)
Namespace.addCategoryObject('elementBinding', end.name().localName(), end)

expires = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'expires'), dateTimeType)
Namespace.addCategoryObject('elementBinding', expires.name().localName(), expires)

fill = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'fill'), pyxb.binding.datatypes.boolean)
Namespace.addCategoryObject('elementBinding', fill.name().localName(), fill)

z = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'z'), pyxb.binding.datatypes.double)
Namespace.addCategoryObject('elementBinding', z.name().localName(), z)

TimeSpanSimpleExtensionGroup = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'TimeSpanSimpleExtensionGroup'), pyxb.binding.datatypes.anySimpleType, abstract=pyxb.binding.datatypes.boolean(1))
Namespace.addCategoryObject('elementBinding', TimeSpanSimpleExtensionGroup.name().localName(), TimeSpanSimpleExtensionGroup)

outline = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'outline'), pyxb.binding.datatypes.boolean)
Namespace.addCategoryObject('elementBinding', outline.name().localName(), outline)

PlacemarkSimpleExtensionGroup = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'PlacemarkSimpleExtensionGroup'), pyxb.binding.datatypes.anySimpleType, abstract=pyxb.binding.datatypes.boolean(1))
Namespace.addCategoryObject('elementBinding', PlacemarkSimpleExtensionGroup.name().localName(), PlacemarkSimpleExtensionGroup)

PlacemarkObjectExtensionGroup = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'PlacemarkObjectExtensionGroup'), pyxb.binding.datatypes.anyType, abstract=pyxb.binding.datatypes.boolean(1))
Namespace.addCategoryObject('elementBinding', PlacemarkObjectExtensionGroup.name().localName(), PlacemarkObjectExtensionGroup)

refreshMode = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'refreshMode'), refreshModeEnumType)
Namespace.addCategoryObject('elementBinding', refreshMode.name().localName(), refreshMode)

linkName = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'linkName'), pyxb.binding.datatypes.string)
Namespace.addCategoryObject('elementBinding', linkName.name().localName(), linkName)

NetworkLink = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'NetworkLink'), NetworkLinkType)
Namespace.addCategoryObject('elementBinding', NetworkLink.name().localName(), NetworkLink)

extrude = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'extrude'), pyxb.binding.datatypes.boolean)
Namespace.addCategoryObject('elementBinding', extrude.name().localName(), extrude)

minAltitude = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'minAltitude'), pyxb.binding.datatypes.double)
Namespace.addCategoryObject('elementBinding', minAltitude.name().localName(), minAltitude)

altitude = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'altitude'), pyxb.binding.datatypes.double)
Namespace.addCategoryObject('elementBinding', altitude.name().localName(), altitude)

hotSpot = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'hotSpot'), vec2Type)
Namespace.addCategoryObject('elementBinding', hotSpot.name().localName(), hotSpot)

overlayXY = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'overlayXY'), vec2Type)
Namespace.addCategoryObject('elementBinding', overlayXY.name().localName(), overlayXY)

key = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'key'), styleStateEnumType)
Namespace.addCategoryObject('elementBinding', key.name().localName(), key)

leftFov = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'leftFov'), angle180Type)
Namespace.addCategoryObject('elementBinding', leftFov.name().localName(), leftFov)

linkDescription = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'linkDescription'), pyxb.binding.datatypes.string)
Namespace.addCategoryObject('elementBinding', linkDescription.name().localName(), linkDescription)

StyleMapObjectExtensionGroup = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'StyleMapObjectExtensionGroup'), pyxb.binding.datatypes.anyType, abstract=pyxb.binding.datatypes.boolean(1))
Namespace.addCategoryObject('elementBinding', StyleMapObjectExtensionGroup.name().localName(), StyleMapObjectExtensionGroup)

linkSnippet = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'linkSnippet'), SnippetType)
Namespace.addCategoryObject('elementBinding', linkSnippet.name().localName(), linkSnippet)

LocationSimpleExtensionGroup = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'LocationSimpleExtensionGroup'), pyxb.binding.datatypes.anySimpleType, abstract=pyxb.binding.datatypes.boolean(1))
Namespace.addCategoryObject('elementBinding', LocationSimpleExtensionGroup.name().localName(), LocationSimpleExtensionGroup)



AbstractObjectType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'ObjectSimpleExtensionGroup'), pyxb.binding.datatypes.anySimpleType, abstract=pyxb.binding.datatypes.boolean(1), scope=AbstractObjectType))
AbstractObjectType._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(AbstractObjectType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'ObjectSimpleExtensionGroup')), min_occurs=0L, max_occurs=None)
    )
AbstractObjectType._ContentModel = pyxb.binding.content.ParticleModel(AbstractObjectType._GroupModel, min_occurs=1, max_occurs=1)



AbstractGeometryType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'AbstractGeometrySimpleExtensionGroup'), pyxb.binding.datatypes.anySimpleType, abstract=pyxb.binding.datatypes.boolean(1), scope=AbstractGeometryType))

AbstractGeometryType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'AbstractGeometryObjectExtensionGroup'), pyxb.binding.datatypes.anyType, abstract=pyxb.binding.datatypes.boolean(1), scope=AbstractGeometryType))
AbstractGeometryType._GroupModel_ = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(AbstractGeometryType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'ObjectSimpleExtensionGroup')), min_occurs=0L, max_occurs=None)
    )
AbstractGeometryType._GroupModel_2 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(AbstractGeometryType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'AbstractGeometrySimpleExtensionGroup')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(AbstractGeometryType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'AbstractGeometryObjectExtensionGroup')), min_occurs=0L, max_occurs=None)
    )
AbstractGeometryType._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(AbstractGeometryType._GroupModel_, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(AbstractGeometryType._GroupModel_2, min_occurs=1, max_occurs=1)
    )
AbstractGeometryType._ContentModel = pyxb.binding.content.ParticleModel(AbstractGeometryType._GroupModel, min_occurs=1, max_occurs=1)



LocationType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'latitude'), angle90Type, scope=LocationType))

LocationType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'altitude'), pyxb.binding.datatypes.double, scope=LocationType))

LocationType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'longitude'), angle180Type, scope=LocationType))

LocationType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'LocationObjectExtensionGroup'), pyxb.binding.datatypes.anyType, abstract=pyxb.binding.datatypes.boolean(1), scope=LocationType))

LocationType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'LocationSimpleExtensionGroup'), pyxb.binding.datatypes.anySimpleType, abstract=pyxb.binding.datatypes.boolean(1), scope=LocationType))
LocationType._GroupModel_ = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(LocationType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'ObjectSimpleExtensionGroup')), min_occurs=0L, max_occurs=None)
    )
LocationType._GroupModel_2 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(LocationType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'longitude')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(LocationType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'latitude')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(LocationType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'altitude')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(LocationType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'LocationSimpleExtensionGroup')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(LocationType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'LocationObjectExtensionGroup')), min_occurs=0L, max_occurs=None)
    )
LocationType._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(LocationType._GroupModel_, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(LocationType._GroupModel_2, min_occurs=1, max_occurs=1)
    )
LocationType._ContentModel = pyxb.binding.content.ParticleModel(LocationType._GroupModel, min_occurs=1, max_occurs=1)



AbstractSubStyleType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'AbstractSubStyleObjectExtensionGroup'), pyxb.binding.datatypes.anyType, abstract=pyxb.binding.datatypes.boolean(1), scope=AbstractSubStyleType))

AbstractSubStyleType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'AbstractSubStyleSimpleExtensionGroup'), pyxb.binding.datatypes.anySimpleType, abstract=pyxb.binding.datatypes.boolean(1), scope=AbstractSubStyleType))
AbstractSubStyleType._GroupModel_ = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(AbstractSubStyleType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'ObjectSimpleExtensionGroup')), min_occurs=0L, max_occurs=None)
    )
AbstractSubStyleType._GroupModel_2 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(AbstractSubStyleType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'AbstractSubStyleSimpleExtensionGroup')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(AbstractSubStyleType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'AbstractSubStyleObjectExtensionGroup')), min_occurs=0L, max_occurs=None)
    )
AbstractSubStyleType._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(AbstractSubStyleType._GroupModel_, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(AbstractSubStyleType._GroupModel_2, min_occurs=1, max_occurs=1)
    )
AbstractSubStyleType._ContentModel = pyxb.binding.content.ParticleModel(AbstractSubStyleType._GroupModel, min_occurs=1, max_occurs=1)



AbstractColorStyleType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'AbstractColorStyleSimpleExtensionGroup'), pyxb.binding.datatypes.anySimpleType, abstract=pyxb.binding.datatypes.boolean(1), scope=AbstractColorStyleType))

AbstractColorStyleType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'color'), colorType, scope=AbstractColorStyleType))

AbstractColorStyleType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'AbstractColorStyleObjectExtensionGroup'), pyxb.binding.datatypes.anyType, abstract=pyxb.binding.datatypes.boolean(1), scope=AbstractColorStyleType))

AbstractColorStyleType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'colorMode'), colorModeEnumType, scope=AbstractColorStyleType))
AbstractColorStyleType._GroupModel_2 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(AbstractColorStyleType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'ObjectSimpleExtensionGroup')), min_occurs=0L, max_occurs=None)
    )
AbstractColorStyleType._GroupModel_3 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(AbstractColorStyleType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'AbstractSubStyleSimpleExtensionGroup')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(AbstractColorStyleType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'AbstractSubStyleObjectExtensionGroup')), min_occurs=0L, max_occurs=None)
    )
AbstractColorStyleType._GroupModel_ = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(AbstractColorStyleType._GroupModel_2, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(AbstractColorStyleType._GroupModel_3, min_occurs=1, max_occurs=1)
    )
AbstractColorStyleType._GroupModel_4 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(AbstractColorStyleType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'color')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(AbstractColorStyleType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'colorMode')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(AbstractColorStyleType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'AbstractColorStyleSimpleExtensionGroup')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(AbstractColorStyleType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'AbstractColorStyleObjectExtensionGroup')), min_occurs=0L, max_occurs=None)
    )
AbstractColorStyleType._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(AbstractColorStyleType._GroupModel_, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(AbstractColorStyleType._GroupModel_4, min_occurs=1, max_occurs=1)
    )
AbstractColorStyleType._ContentModel = pyxb.binding.content.ParticleModel(AbstractColorStyleType._GroupModel, min_occurs=1, max_occurs=1)



IconStyleType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Icon'), BasicLinkType, scope=IconStyleType))

IconStyleType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'hotSpot'), vec2Type, scope=IconStyleType))

IconStyleType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'IconStyleSimpleExtensionGroup'), pyxb.binding.datatypes.anySimpleType, abstract=pyxb.binding.datatypes.boolean(1), scope=IconStyleType))

IconStyleType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'IconStyleObjectExtensionGroup'), pyxb.binding.datatypes.anyType, abstract=pyxb.binding.datatypes.boolean(1), scope=IconStyleType))

IconStyleType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'scale'), pyxb.binding.datatypes.double, scope=IconStyleType))

IconStyleType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'heading'), angle360Type, scope=IconStyleType))
IconStyleType._GroupModel_3 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(IconStyleType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'ObjectSimpleExtensionGroup')), min_occurs=0L, max_occurs=None)
    )
IconStyleType._GroupModel_4 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(IconStyleType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'AbstractSubStyleSimpleExtensionGroup')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(IconStyleType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'AbstractSubStyleObjectExtensionGroup')), min_occurs=0L, max_occurs=None)
    )
IconStyleType._GroupModel_2 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(IconStyleType._GroupModel_3, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(IconStyleType._GroupModel_4, min_occurs=1, max_occurs=1)
    )
IconStyleType._GroupModel_5 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(IconStyleType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'color')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(IconStyleType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'colorMode')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(IconStyleType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'AbstractColorStyleSimpleExtensionGroup')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(IconStyleType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'AbstractColorStyleObjectExtensionGroup')), min_occurs=0L, max_occurs=None)
    )
IconStyleType._GroupModel_ = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(IconStyleType._GroupModel_2, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(IconStyleType._GroupModel_5, min_occurs=1, max_occurs=1)
    )
IconStyleType._GroupModel_6 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(IconStyleType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'scale')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(IconStyleType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'heading')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(IconStyleType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Icon')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(IconStyleType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'hotSpot')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(IconStyleType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'IconStyleSimpleExtensionGroup')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(IconStyleType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'IconStyleObjectExtensionGroup')), min_occurs=0L, max_occurs=None)
    )
IconStyleType._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(IconStyleType._GroupModel_, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(IconStyleType._GroupModel_6, min_occurs=1, max_occurs=1)
    )
IconStyleType._ContentModel = pyxb.binding.content.ParticleModel(IconStyleType._GroupModel, min_occurs=1, max_occurs=1)



DataType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'DataExtension'), pyxb.binding.datatypes.anyType, abstract=pyxb.binding.datatypes.boolean(1), scope=DataType))

DataType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'value'), pyxb.binding.datatypes.string, scope=DataType))

DataType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'displayName'), pyxb.binding.datatypes.string, scope=DataType))
DataType._GroupModel_ = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(DataType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'ObjectSimpleExtensionGroup')), min_occurs=0L, max_occurs=None)
    )
DataType._GroupModel_2 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(DataType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'displayName')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(DataType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'value')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(DataType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'DataExtension')), min_occurs=0L, max_occurs=None)
    )
DataType._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(DataType._GroupModel_, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(DataType._GroupModel_2, min_occurs=1, max_occurs=1)
    )
DataType._ContentModel = pyxb.binding.content.ParticleModel(DataType._GroupModel, min_occurs=1, max_occurs=1)



AliasType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'sourceHref'), pyxb.binding.datatypes.anyURI, scope=AliasType))

AliasType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'AliasObjectExtensionGroup'), pyxb.binding.datatypes.anyType, abstract=pyxb.binding.datatypes.boolean(1), scope=AliasType))

AliasType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'targetHref'), pyxb.binding.datatypes.anyURI, scope=AliasType))

AliasType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'AliasSimpleExtensionGroup'), pyxb.binding.datatypes.anySimpleType, abstract=pyxb.binding.datatypes.boolean(1), scope=AliasType))
AliasType._GroupModel_ = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(AliasType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'ObjectSimpleExtensionGroup')), min_occurs=0L, max_occurs=None)
    )
AliasType._GroupModel_2 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(AliasType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'targetHref')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(AliasType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'sourceHref')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(AliasType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'AliasSimpleExtensionGroup')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(AliasType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'AliasObjectExtensionGroup')), min_occurs=0L, max_occurs=None)
    )
AliasType._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(AliasType._GroupModel_, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(AliasType._GroupModel_2, min_occurs=1, max_occurs=1)
    )
AliasType._ContentModel = pyxb.binding.content.ParticleModel(AliasType._GroupModel, min_occurs=1, max_occurs=1)



BasicLinkType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'BasicLinkSimpleExtensionGroup'), pyxb.binding.datatypes.anySimpleType, abstract=pyxb.binding.datatypes.boolean(1), scope=BasicLinkType))

BasicLinkType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'href'), pyxb.binding.datatypes.string, scope=BasicLinkType, documentation=u'not anyURI due to $[x] substitution in\n      PhotoOverlay'))

BasicLinkType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'BasicLinkObjectExtensionGroup'), pyxb.binding.datatypes.anyType, abstract=pyxb.binding.datatypes.boolean(1), scope=BasicLinkType))
BasicLinkType._GroupModel_ = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(BasicLinkType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'ObjectSimpleExtensionGroup')), min_occurs=0L, max_occurs=None)
    )
BasicLinkType._GroupModel_2 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(BasicLinkType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'href')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(BasicLinkType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'BasicLinkSimpleExtensionGroup')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(BasicLinkType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'BasicLinkObjectExtensionGroup')), min_occurs=0L, max_occurs=None)
    )
BasicLinkType._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(BasicLinkType._GroupModel_, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(BasicLinkType._GroupModel_2, min_occurs=1, max_occurs=1)
    )
BasicLinkType._ContentModel = pyxb.binding.content.ParticleModel(BasicLinkType._GroupModel, min_occurs=1, max_occurs=1)



AbstractStyleSelectorType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'AbstractStyleSelectorObjectExtensionGroup'), pyxb.binding.datatypes.anyType, abstract=pyxb.binding.datatypes.boolean(1), scope=AbstractStyleSelectorType))

AbstractStyleSelectorType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'AbstractStyleSelectorSimpleExtensionGroup'), pyxb.binding.datatypes.anySimpleType, abstract=pyxb.binding.datatypes.boolean(1), scope=AbstractStyleSelectorType))
AbstractStyleSelectorType._GroupModel_ = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(AbstractStyleSelectorType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'ObjectSimpleExtensionGroup')), min_occurs=0L, max_occurs=None)
    )
AbstractStyleSelectorType._GroupModel_2 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(AbstractStyleSelectorType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'AbstractStyleSelectorSimpleExtensionGroup')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(AbstractStyleSelectorType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'AbstractStyleSelectorObjectExtensionGroup')), min_occurs=0L, max_occurs=None)
    )
AbstractStyleSelectorType._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(AbstractStyleSelectorType._GroupModel_, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(AbstractStyleSelectorType._GroupModel_2, min_occurs=1, max_occurs=1)
    )
AbstractStyleSelectorType._ContentModel = pyxb.binding.content.ParticleModel(AbstractStyleSelectorType._GroupModel, min_occurs=1, max_occurs=1)



NetworkLinkControlType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'linkName'), pyxb.binding.datatypes.string, scope=NetworkLinkControlType))

NetworkLinkControlType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'expires'), dateTimeType, scope=NetworkLinkControlType))

NetworkLinkControlType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Update'), UpdateType, scope=NetworkLinkControlType))

NetworkLinkControlType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'cookie'), pyxb.binding.datatypes.string, scope=NetworkLinkControlType))

NetworkLinkControlType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'NetworkLinkControlSimpleExtensionGroup'), pyxb.binding.datatypes.anySimpleType, abstract=pyxb.binding.datatypes.boolean(1), scope=NetworkLinkControlType))

NetworkLinkControlType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'linkDescription'), pyxb.binding.datatypes.string, scope=NetworkLinkControlType))

NetworkLinkControlType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'maxSessionLength'), pyxb.binding.datatypes.double, scope=NetworkLinkControlType))

NetworkLinkControlType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'minRefreshPeriod'), pyxb.binding.datatypes.double, scope=NetworkLinkControlType))

NetworkLinkControlType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'message'), pyxb.binding.datatypes.string, scope=NetworkLinkControlType))

NetworkLinkControlType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'NetworkLinkControlObjectExtensionGroup'), pyxb.binding.datatypes.anyType, abstract=pyxb.binding.datatypes.boolean(1), scope=NetworkLinkControlType))

NetworkLinkControlType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'linkSnippet'), SnippetType, scope=NetworkLinkControlType))

NetworkLinkControlType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'AbstractViewGroup'), AbstractViewType, abstract=pyxb.binding.datatypes.boolean(1), scope=NetworkLinkControlType))
NetworkLinkControlType._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(NetworkLinkControlType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'minRefreshPeriod')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(NetworkLinkControlType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'maxSessionLength')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(NetworkLinkControlType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'cookie')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(NetworkLinkControlType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'message')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(NetworkLinkControlType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'linkName')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(NetworkLinkControlType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'linkDescription')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(NetworkLinkControlType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'linkSnippet')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(NetworkLinkControlType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'expires')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(NetworkLinkControlType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Update')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(NetworkLinkControlType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'AbstractViewGroup')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(NetworkLinkControlType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'NetworkLinkControlSimpleExtensionGroup')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(NetworkLinkControlType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'NetworkLinkControlObjectExtensionGroup')), min_occurs=0L, max_occurs=None)
    )
NetworkLinkControlType._ContentModel = pyxb.binding.content.ParticleModel(NetworkLinkControlType._GroupModel, min_occurs=1, max_occurs=1)



AbstractFeatureType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/2005/Atom'), u'link'), pyxb.bundles.opengis._atom.CTD_ANON, scope=AbstractFeatureType))

AbstractFeatureType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'snippet'), pyxb.binding.datatypes.string, scope=AbstractFeatureType))

AbstractFeatureType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'AbstractStyleSelectorGroup'), AbstractStyleSelectorType, abstract=pyxb.binding.datatypes.boolean(1), scope=AbstractFeatureType))

AbstractFeatureType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'AbstractFeatureObjectExtensionGroup'), pyxb.binding.datatypes.anyType, abstract=pyxb.binding.datatypes.boolean(1), scope=AbstractFeatureType))

AbstractFeatureType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'description'), pyxb.binding.datatypes.string, scope=AbstractFeatureType))

AbstractFeatureType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'AbstractTimePrimitiveGroup'), AbstractTimePrimitiveType, abstract=pyxb.binding.datatypes.boolean(1), scope=AbstractFeatureType))

AbstractFeatureType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Region'), RegionType, scope=AbstractFeatureType))

AbstractFeatureType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'address'), pyxb.binding.datatypes.string, scope=AbstractFeatureType))

AbstractFeatureType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'AbstractFeatureSimpleExtensionGroup'), pyxb.binding.datatypes.anySimpleType, abstract=pyxb.binding.datatypes.boolean(1), scope=AbstractFeatureType))

AbstractFeatureType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'name'), pyxb.binding.datatypes.string, scope=AbstractFeatureType))

AbstractFeatureType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'phoneNumber'), pyxb.binding.datatypes.string, scope=AbstractFeatureType))

AbstractFeatureType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Metadata'), MetadataType, scope=AbstractFeatureType, documentation=u'Metadata deprecated in 2.2'))

AbstractFeatureType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/2005/Atom'), u'author'), pyxb.bundles.opengis._atom.atomPersonConstruct, scope=AbstractFeatureType))

AbstractFeatureType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'visibility'), pyxb.binding.datatypes.boolean, scope=AbstractFeatureType))

AbstractFeatureType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'open'), pyxb.binding.datatypes.boolean, scope=AbstractFeatureType))

AbstractFeatureType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'urn:oasis:names:tc:ciq:xsdschema:xAL:2.0'), u'AddressDetails'), pyxb.bundles.opengis.misc.xAL.AddressDetails_, scope=AbstractFeatureType, documentation=u'This container defines the details of the address. Can define multiple addresses including tracking address history'))

AbstractFeatureType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'AbstractViewGroup'), AbstractViewType, abstract=pyxb.binding.datatypes.boolean(1), scope=AbstractFeatureType))

AbstractFeatureType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'ExtendedData'), ExtendedDataType, scope=AbstractFeatureType))

AbstractFeatureType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Snippet'), SnippetType, scope=AbstractFeatureType))

AbstractFeatureType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'styleUrl'), pyxb.binding.datatypes.anyURI, scope=AbstractFeatureType))
AbstractFeatureType._GroupModel_ = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(AbstractFeatureType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'ObjectSimpleExtensionGroup')), min_occurs=0L, max_occurs=None)
    )
AbstractFeatureType._GroupModel_3 = pyxb.binding.content.GroupChoice(
    pyxb.binding.content.ParticleModel(AbstractFeatureType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Snippet')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(AbstractFeatureType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'snippet')), min_occurs=0L, max_occurs=1)
    )
AbstractFeatureType._GroupModel_4 = pyxb.binding.content.GroupChoice(
    pyxb.binding.content.ParticleModel(AbstractFeatureType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Metadata')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(AbstractFeatureType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'ExtendedData')), min_occurs=0L, max_occurs=1)
    )
AbstractFeatureType._GroupModel_2 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(AbstractFeatureType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'name')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(AbstractFeatureType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'visibility')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(AbstractFeatureType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'open')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(AbstractFeatureType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/2005/Atom'), u'author')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(AbstractFeatureType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/2005/Atom'), u'link')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(AbstractFeatureType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'address')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(AbstractFeatureType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'urn:oasis:names:tc:ciq:xsdschema:xAL:2.0'), u'AddressDetails')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(AbstractFeatureType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'phoneNumber')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(AbstractFeatureType._GroupModel_3, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(AbstractFeatureType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'description')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(AbstractFeatureType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'AbstractViewGroup')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(AbstractFeatureType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'AbstractTimePrimitiveGroup')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(AbstractFeatureType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'styleUrl')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(AbstractFeatureType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'AbstractStyleSelectorGroup')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(AbstractFeatureType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Region')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(AbstractFeatureType._GroupModel_4, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(AbstractFeatureType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'AbstractFeatureSimpleExtensionGroup')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(AbstractFeatureType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'AbstractFeatureObjectExtensionGroup')), min_occurs=0L, max_occurs=None)
    )
AbstractFeatureType._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(AbstractFeatureType._GroupModel_, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(AbstractFeatureType._GroupModel_2, min_occurs=1, max_occurs=1)
    )
AbstractFeatureType._ContentModel = pyxb.binding.content.ParticleModel(AbstractFeatureType._GroupModel, min_occurs=1, max_occurs=1)



AbstractTimePrimitiveType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'AbstractTimePrimitiveObjectExtensionGroup'), pyxb.binding.datatypes.anyType, abstract=pyxb.binding.datatypes.boolean(1), scope=AbstractTimePrimitiveType))

AbstractTimePrimitiveType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'AbstractTimePrimitiveSimpleExtensionGroup'), pyxb.binding.datatypes.anySimpleType, abstract=pyxb.binding.datatypes.boolean(1), scope=AbstractTimePrimitiveType))
AbstractTimePrimitiveType._GroupModel_ = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(AbstractTimePrimitiveType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'ObjectSimpleExtensionGroup')), min_occurs=0L, max_occurs=None)
    )
AbstractTimePrimitiveType._GroupModel_2 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(AbstractTimePrimitiveType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'AbstractTimePrimitiveSimpleExtensionGroup')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(AbstractTimePrimitiveType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'AbstractTimePrimitiveObjectExtensionGroup')), min_occurs=0L, max_occurs=None)
    )
AbstractTimePrimitiveType._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(AbstractTimePrimitiveType._GroupModel_, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(AbstractTimePrimitiveType._GroupModel_2, min_occurs=1, max_occurs=1)
    )
AbstractTimePrimitiveType._ContentModel = pyxb.binding.content.ParticleModel(AbstractTimePrimitiveType._GroupModel, min_occurs=1, max_occurs=1)



LabelStyleType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'LabelStyleSimpleExtensionGroup'), pyxb.binding.datatypes.anySimpleType, abstract=pyxb.binding.datatypes.boolean(1), scope=LabelStyleType))

LabelStyleType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'LabelStyleObjectExtensionGroup'), pyxb.binding.datatypes.anyType, abstract=pyxb.binding.datatypes.boolean(1), scope=LabelStyleType))

LabelStyleType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'scale'), pyxb.binding.datatypes.double, scope=LabelStyleType))
LabelStyleType._GroupModel_3 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(LabelStyleType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'ObjectSimpleExtensionGroup')), min_occurs=0L, max_occurs=None)
    )
LabelStyleType._GroupModel_4 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(LabelStyleType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'AbstractSubStyleSimpleExtensionGroup')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(LabelStyleType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'AbstractSubStyleObjectExtensionGroup')), min_occurs=0L, max_occurs=None)
    )
LabelStyleType._GroupModel_2 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(LabelStyleType._GroupModel_3, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(LabelStyleType._GroupModel_4, min_occurs=1, max_occurs=1)
    )
LabelStyleType._GroupModel_5 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(LabelStyleType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'color')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(LabelStyleType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'colorMode')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(LabelStyleType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'AbstractColorStyleSimpleExtensionGroup')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(LabelStyleType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'AbstractColorStyleObjectExtensionGroup')), min_occurs=0L, max_occurs=None)
    )
LabelStyleType._GroupModel_ = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(LabelStyleType._GroupModel_2, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(LabelStyleType._GroupModel_5, min_occurs=1, max_occurs=1)
    )
LabelStyleType._GroupModel_6 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(LabelStyleType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'scale')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(LabelStyleType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'LabelStyleSimpleExtensionGroup')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(LabelStyleType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'LabelStyleObjectExtensionGroup')), min_occurs=0L, max_occurs=None)
    )
LabelStyleType._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(LabelStyleType._GroupModel_, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(LabelStyleType._GroupModel_6, min_occurs=1, max_occurs=1)
    )
LabelStyleType._ContentModel = pyxb.binding.content.ParticleModel(LabelStyleType._GroupModel, min_occurs=1, max_occurs=1)



LineStyleType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'width'), pyxb.binding.datatypes.double, scope=LineStyleType))

LineStyleType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'LineStyleSimpleExtensionGroup'), pyxb.binding.datatypes.anySimpleType, abstract=pyxb.binding.datatypes.boolean(1), scope=LineStyleType))

LineStyleType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'LineStyleObjectExtensionGroup'), pyxb.binding.datatypes.anyType, abstract=pyxb.binding.datatypes.boolean(1), scope=LineStyleType))
LineStyleType._GroupModel_3 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(LineStyleType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'ObjectSimpleExtensionGroup')), min_occurs=0L, max_occurs=None)
    )
LineStyleType._GroupModel_4 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(LineStyleType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'AbstractSubStyleSimpleExtensionGroup')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(LineStyleType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'AbstractSubStyleObjectExtensionGroup')), min_occurs=0L, max_occurs=None)
    )
LineStyleType._GroupModel_2 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(LineStyleType._GroupModel_3, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(LineStyleType._GroupModel_4, min_occurs=1, max_occurs=1)
    )
LineStyleType._GroupModel_5 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(LineStyleType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'color')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(LineStyleType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'colorMode')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(LineStyleType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'AbstractColorStyleSimpleExtensionGroup')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(LineStyleType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'AbstractColorStyleObjectExtensionGroup')), min_occurs=0L, max_occurs=None)
    )
LineStyleType._GroupModel_ = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(LineStyleType._GroupModel_2, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(LineStyleType._GroupModel_5, min_occurs=1, max_occurs=1)
    )
LineStyleType._GroupModel_6 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(LineStyleType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'width')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(LineStyleType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'LineStyleSimpleExtensionGroup')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(LineStyleType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'LineStyleObjectExtensionGroup')), min_occurs=0L, max_occurs=None)
    )
LineStyleType._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(LineStyleType._GroupModel_, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(LineStyleType._GroupModel_6, min_occurs=1, max_occurs=1)
    )
LineStyleType._ContentModel = pyxb.binding.content.ParticleModel(LineStyleType._GroupModel, min_occurs=1, max_occurs=1)



BoundaryType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'BoundarySimpleExtensionGroup'), pyxb.binding.datatypes.anySimpleType, abstract=pyxb.binding.datatypes.boolean(1), scope=BoundaryType))

BoundaryType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'BoundaryObjectExtensionGroup'), pyxb.binding.datatypes.anyType, abstract=pyxb.binding.datatypes.boolean(1), scope=BoundaryType))

BoundaryType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'LinearRing'), LinearRingType, scope=BoundaryType))
BoundaryType._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(BoundaryType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'LinearRing')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(BoundaryType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'BoundarySimpleExtensionGroup')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(BoundaryType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'BoundaryObjectExtensionGroup')), min_occurs=0L, max_occurs=None)
    )
BoundaryType._ContentModel = pyxb.binding.content.ParticleModel(BoundaryType._GroupModel, min_occurs=1, max_occurs=1)



PolyStyleType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'fill'), pyxb.binding.datatypes.boolean, scope=PolyStyleType))

PolyStyleType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'PolyStyleObjectExtensionGroup'), pyxb.binding.datatypes.anyType, abstract=pyxb.binding.datatypes.boolean(1), scope=PolyStyleType))

PolyStyleType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'outline'), pyxb.binding.datatypes.boolean, scope=PolyStyleType))

PolyStyleType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'PolyStyleSimpleExtensionGroup'), pyxb.binding.datatypes.anySimpleType, abstract=pyxb.binding.datatypes.boolean(1), scope=PolyStyleType))
PolyStyleType._GroupModel_3 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(PolyStyleType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'ObjectSimpleExtensionGroup')), min_occurs=0L, max_occurs=None)
    )
PolyStyleType._GroupModel_4 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(PolyStyleType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'AbstractSubStyleSimpleExtensionGroup')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(PolyStyleType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'AbstractSubStyleObjectExtensionGroup')), min_occurs=0L, max_occurs=None)
    )
PolyStyleType._GroupModel_2 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(PolyStyleType._GroupModel_3, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(PolyStyleType._GroupModel_4, min_occurs=1, max_occurs=1)
    )
PolyStyleType._GroupModel_5 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(PolyStyleType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'color')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(PolyStyleType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'colorMode')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(PolyStyleType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'AbstractColorStyleSimpleExtensionGroup')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(PolyStyleType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'AbstractColorStyleObjectExtensionGroup')), min_occurs=0L, max_occurs=None)
    )
PolyStyleType._GroupModel_ = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(PolyStyleType._GroupModel_2, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(PolyStyleType._GroupModel_5, min_occurs=1, max_occurs=1)
    )
PolyStyleType._GroupModel_6 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(PolyStyleType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'fill')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(PolyStyleType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'outline')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(PolyStyleType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'PolyStyleSimpleExtensionGroup')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(PolyStyleType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'PolyStyleObjectExtensionGroup')), min_occurs=0L, max_occurs=None)
    )
PolyStyleType._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(PolyStyleType._GroupModel_, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(PolyStyleType._GroupModel_6, min_occurs=1, max_occurs=1)
    )
PolyStyleType._ContentModel = pyxb.binding.content.ParticleModel(PolyStyleType._GroupModel, min_occurs=1, max_occurs=1)



LinearRingType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'LinearRingSimpleExtensionGroup'), pyxb.binding.datatypes.anySimpleType, abstract=pyxb.binding.datatypes.boolean(1), scope=LinearRingType))

LinearRingType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'altitudeModeGroup'), pyxb.binding.datatypes.anyType, abstract=pyxb.binding.datatypes.boolean(1), scope=LinearRingType))

LinearRingType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'LinearRingObjectExtensionGroup'), pyxb.binding.datatypes.anyType, abstract=pyxb.binding.datatypes.boolean(1), scope=LinearRingType))

LinearRingType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'extrude'), pyxb.binding.datatypes.boolean, scope=LinearRingType))

LinearRingType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'coordinates'), coordinatesType, scope=LinearRingType))

LinearRingType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'tessellate'), pyxb.binding.datatypes.boolean, scope=LinearRingType))
LinearRingType._GroupModel_2 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(LinearRingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'ObjectSimpleExtensionGroup')), min_occurs=0L, max_occurs=None)
    )
LinearRingType._GroupModel_3 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(LinearRingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'AbstractGeometrySimpleExtensionGroup')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(LinearRingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'AbstractGeometryObjectExtensionGroup')), min_occurs=0L, max_occurs=None)
    )
LinearRingType._GroupModel_ = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(LinearRingType._GroupModel_2, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(LinearRingType._GroupModel_3, min_occurs=1, max_occurs=1)
    )
LinearRingType._GroupModel_4 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(LinearRingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'extrude')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(LinearRingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'tessellate')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(LinearRingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'altitudeModeGroup')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(LinearRingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'coordinates')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(LinearRingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'LinearRingSimpleExtensionGroup')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(LinearRingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'LinearRingObjectExtensionGroup')), min_occurs=0L, max_occurs=None)
    )
LinearRingType._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(LinearRingType._GroupModel_, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(LinearRingType._GroupModel_4, min_occurs=1, max_occurs=1)
    )
LinearRingType._ContentModel = pyxb.binding.content.ParticleModel(LinearRingType._GroupModel, min_occurs=1, max_occurs=1)



AbstractOverlayType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'color'), colorType, scope=AbstractOverlayType))

AbstractOverlayType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'drawOrder'), pyxb.binding.datatypes.int, scope=AbstractOverlayType))

AbstractOverlayType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Icon'), LinkType, scope=AbstractOverlayType))

AbstractOverlayType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'AbstractOverlaySimpleExtensionGroup'), pyxb.binding.datatypes.anySimpleType, abstract=pyxb.binding.datatypes.boolean(1), scope=AbstractOverlayType))

AbstractOverlayType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'AbstractOverlayObjectExtensionGroup'), pyxb.binding.datatypes.anyType, abstract=pyxb.binding.datatypes.boolean(1), scope=AbstractOverlayType))
AbstractOverlayType._GroupModel_2 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(AbstractOverlayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'ObjectSimpleExtensionGroup')), min_occurs=0L, max_occurs=None)
    )
AbstractOverlayType._GroupModel_4 = pyxb.binding.content.GroupChoice(
    pyxb.binding.content.ParticleModel(AbstractOverlayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Snippet')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(AbstractOverlayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'snippet')), min_occurs=0L, max_occurs=1)
    )
AbstractOverlayType._GroupModel_5 = pyxb.binding.content.GroupChoice(
    pyxb.binding.content.ParticleModel(AbstractOverlayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Metadata')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(AbstractOverlayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'ExtendedData')), min_occurs=0L, max_occurs=1)
    )
AbstractOverlayType._GroupModel_3 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(AbstractOverlayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'name')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(AbstractOverlayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'visibility')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(AbstractOverlayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'open')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(AbstractOverlayType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/2005/Atom'), u'author')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(AbstractOverlayType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/2005/Atom'), u'link')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(AbstractOverlayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'address')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(AbstractOverlayType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'urn:oasis:names:tc:ciq:xsdschema:xAL:2.0'), u'AddressDetails')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(AbstractOverlayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'phoneNumber')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(AbstractOverlayType._GroupModel_4, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(AbstractOverlayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'description')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(AbstractOverlayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'AbstractViewGroup')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(AbstractOverlayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'AbstractTimePrimitiveGroup')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(AbstractOverlayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'styleUrl')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(AbstractOverlayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'AbstractStyleSelectorGroup')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(AbstractOverlayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Region')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(AbstractOverlayType._GroupModel_5, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(AbstractOverlayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'AbstractFeatureSimpleExtensionGroup')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(AbstractOverlayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'AbstractFeatureObjectExtensionGroup')), min_occurs=0L, max_occurs=None)
    )
AbstractOverlayType._GroupModel_ = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(AbstractOverlayType._GroupModel_2, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(AbstractOverlayType._GroupModel_3, min_occurs=1, max_occurs=1)
    )
AbstractOverlayType._GroupModel_6 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(AbstractOverlayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'color')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(AbstractOverlayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'drawOrder')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(AbstractOverlayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Icon')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(AbstractOverlayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'AbstractOverlaySimpleExtensionGroup')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(AbstractOverlayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'AbstractOverlayObjectExtensionGroup')), min_occurs=0L, max_occurs=None)
    )
AbstractOverlayType._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(AbstractOverlayType._GroupModel_, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(AbstractOverlayType._GroupModel_6, min_occurs=1, max_occurs=1)
    )
AbstractOverlayType._ContentModel = pyxb.binding.content.ParticleModel(AbstractOverlayType._GroupModel, min_occurs=1, max_occurs=1)



LinkType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'viewRefreshTime'), pyxb.binding.datatypes.double, scope=LinkType))

LinkType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'httpQuery'), pyxb.binding.datatypes.string, scope=LinkType))

LinkType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'refreshInterval'), pyxb.binding.datatypes.double, scope=LinkType))

LinkType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'viewBoundScale'), pyxb.binding.datatypes.double, scope=LinkType))

LinkType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'refreshMode'), refreshModeEnumType, scope=LinkType))

LinkType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'LinkSimpleExtensionGroup'), pyxb.binding.datatypes.anySimpleType, abstract=pyxb.binding.datatypes.boolean(1), scope=LinkType))

LinkType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'viewRefreshMode'), viewRefreshModeEnumType, scope=LinkType))

LinkType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'viewFormat'), pyxb.binding.datatypes.string, scope=LinkType))

LinkType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'LinkObjectExtensionGroup'), pyxb.binding.datatypes.anyType, abstract=pyxb.binding.datatypes.boolean(1), scope=LinkType))
LinkType._GroupModel_2 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(LinkType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'ObjectSimpleExtensionGroup')), min_occurs=0L, max_occurs=None)
    )
LinkType._GroupModel_3 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(LinkType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'href')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(LinkType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'BasicLinkSimpleExtensionGroup')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(LinkType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'BasicLinkObjectExtensionGroup')), min_occurs=0L, max_occurs=None)
    )
LinkType._GroupModel_ = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(LinkType._GroupModel_2, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(LinkType._GroupModel_3, min_occurs=1, max_occurs=1)
    )
LinkType._GroupModel_4 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(LinkType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'refreshMode')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(LinkType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'refreshInterval')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(LinkType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'viewRefreshMode')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(LinkType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'viewRefreshTime')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(LinkType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'viewBoundScale')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(LinkType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'viewFormat')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(LinkType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'httpQuery')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(LinkType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'LinkSimpleExtensionGroup')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(LinkType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'LinkObjectExtensionGroup')), min_occurs=0L, max_occurs=None)
    )
LinkType._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(LinkType._GroupModel_, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(LinkType._GroupModel_4, min_occurs=1, max_occurs=1)
    )
LinkType._ContentModel = pyxb.binding.content.ParticleModel(LinkType._GroupModel, min_occurs=1, max_occurs=1)



UpdateType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Create'), CreateType, scope=UpdateType))

UpdateType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Delete'), DeleteType, scope=UpdateType))

UpdateType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'UpdateOpExtensionGroup'), pyxb.binding.datatypes.anyType, abstract=pyxb.binding.datatypes.boolean(1), scope=UpdateType))

UpdateType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'targetHref'), pyxb.binding.datatypes.anyURI, scope=UpdateType))

UpdateType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'UpdateExtensionGroup'), pyxb.binding.datatypes.anyType, abstract=pyxb.binding.datatypes.boolean(1), scope=UpdateType))

UpdateType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Change'), ChangeType, scope=UpdateType))
UpdateType._GroupModel_ = pyxb.binding.content.GroupChoice(
    pyxb.binding.content.ParticleModel(UpdateType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Create')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(UpdateType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Delete')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(UpdateType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Change')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(UpdateType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'UpdateOpExtensionGroup')), min_occurs=1, max_occurs=1)
    )
UpdateType._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(UpdateType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'targetHref')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(UpdateType._GroupModel_, min_occurs=1, max_occurs=None),
    pyxb.binding.content.ParticleModel(UpdateType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'UpdateExtensionGroup')), min_occurs=0L, max_occurs=None)
    )
UpdateType._ContentModel = pyxb.binding.content.ParticleModel(UpdateType._GroupModel, min_occurs=1, max_occurs=1)



AbstractViewType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'AbstractViewSimpleExtensionGroup'), pyxb.binding.datatypes.anySimpleType, abstract=pyxb.binding.datatypes.boolean(1), scope=AbstractViewType))

AbstractViewType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'AbstractViewObjectExtensionGroup'), pyxb.binding.datatypes.anyType, abstract=pyxb.binding.datatypes.boolean(1), scope=AbstractViewType))
AbstractViewType._GroupModel_ = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(AbstractViewType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'ObjectSimpleExtensionGroup')), min_occurs=0L, max_occurs=None)
    )
AbstractViewType._GroupModel_2 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(AbstractViewType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'AbstractViewSimpleExtensionGroup')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(AbstractViewType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'AbstractViewObjectExtensionGroup')), min_occurs=0L, max_occurs=None)
    )
AbstractViewType._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(AbstractViewType._GroupModel_, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(AbstractViewType._GroupModel_2, min_occurs=1, max_occurs=1)
    )
AbstractViewType._ContentModel = pyxb.binding.content.ParticleModel(AbstractViewType._GroupModel, min_occurs=1, max_occurs=1)



AbstractContainerType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'AbstractContainerSimpleExtensionGroup'), pyxb.binding.datatypes.anySimpleType, abstract=pyxb.binding.datatypes.boolean(1), scope=AbstractContainerType))

AbstractContainerType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'AbstractContainerObjectExtensionGroup'), pyxb.binding.datatypes.anyType, abstract=pyxb.binding.datatypes.boolean(1), scope=AbstractContainerType))
AbstractContainerType._GroupModel_2 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(AbstractContainerType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'ObjectSimpleExtensionGroup')), min_occurs=0L, max_occurs=None)
    )
AbstractContainerType._GroupModel_4 = pyxb.binding.content.GroupChoice(
    pyxb.binding.content.ParticleModel(AbstractContainerType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Snippet')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(AbstractContainerType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'snippet')), min_occurs=0L, max_occurs=1)
    )
AbstractContainerType._GroupModel_5 = pyxb.binding.content.GroupChoice(
    pyxb.binding.content.ParticleModel(AbstractContainerType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Metadata')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(AbstractContainerType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'ExtendedData')), min_occurs=0L, max_occurs=1)
    )
AbstractContainerType._GroupModel_3 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(AbstractContainerType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'name')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(AbstractContainerType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'visibility')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(AbstractContainerType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'open')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(AbstractContainerType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/2005/Atom'), u'author')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(AbstractContainerType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/2005/Atom'), u'link')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(AbstractContainerType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'address')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(AbstractContainerType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'urn:oasis:names:tc:ciq:xsdschema:xAL:2.0'), u'AddressDetails')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(AbstractContainerType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'phoneNumber')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(AbstractContainerType._GroupModel_4, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(AbstractContainerType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'description')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(AbstractContainerType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'AbstractViewGroup')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(AbstractContainerType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'AbstractTimePrimitiveGroup')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(AbstractContainerType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'styleUrl')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(AbstractContainerType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'AbstractStyleSelectorGroup')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(AbstractContainerType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Region')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(AbstractContainerType._GroupModel_5, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(AbstractContainerType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'AbstractFeatureSimpleExtensionGroup')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(AbstractContainerType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'AbstractFeatureObjectExtensionGroup')), min_occurs=0L, max_occurs=None)
    )
AbstractContainerType._GroupModel_ = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(AbstractContainerType._GroupModel_2, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(AbstractContainerType._GroupModel_3, min_occurs=1, max_occurs=1)
    )
AbstractContainerType._GroupModel_6 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(AbstractContainerType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'AbstractContainerSimpleExtensionGroup')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(AbstractContainerType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'AbstractContainerObjectExtensionGroup')), min_occurs=0L, max_occurs=None)
    )
AbstractContainerType._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(AbstractContainerType._GroupModel_, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(AbstractContainerType._GroupModel_6, min_occurs=1, max_occurs=1)
    )
AbstractContainerType._ContentModel = pyxb.binding.content.ParticleModel(AbstractContainerType._GroupModel, min_occurs=1, max_occurs=1)



ChangeType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'AbstractObjectGroup'), AbstractObjectType, abstract=pyxb.binding.datatypes.boolean(1), scope=ChangeType))
ChangeType._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(ChangeType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'AbstractObjectGroup')), min_occurs=0L, max_occurs=None)
    )
ChangeType._ContentModel = pyxb.binding.content.ParticleModel(ChangeType._GroupModel, min_occurs=1, max_occurs=1)



SchemaType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'SchemaExtension'), pyxb.binding.datatypes.anyType, abstract=pyxb.binding.datatypes.boolean(1), scope=SchemaType))

SchemaType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'SimpleField'), SimpleFieldType, scope=SchemaType))
SchemaType._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(SchemaType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'SimpleField')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(SchemaType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'SchemaExtension')), min_occurs=0L, max_occurs=None)
    )
SchemaType._ContentModel = pyxb.binding.content.ParticleModel(SchemaType._GroupModel, min_occurs=1, max_occurs=1)



ViewVolumeType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'topFov'), angle90Type, scope=ViewVolumeType))

ViewVolumeType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'ViewVolumeObjectExtensionGroup'), pyxb.binding.datatypes.anyType, abstract=pyxb.binding.datatypes.boolean(1), scope=ViewVolumeType))

ViewVolumeType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'near'), pyxb.binding.datatypes.double, scope=ViewVolumeType))

ViewVolumeType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'bottomFov'), angle90Type, scope=ViewVolumeType))

ViewVolumeType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'rightFov'), angle180Type, scope=ViewVolumeType))

ViewVolumeType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'ViewVolumeSimpleExtensionGroup'), pyxb.binding.datatypes.anySimpleType, abstract=pyxb.binding.datatypes.boolean(1), scope=ViewVolumeType))

ViewVolumeType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'leftFov'), angle180Type, scope=ViewVolumeType))
ViewVolumeType._GroupModel_ = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(ViewVolumeType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'ObjectSimpleExtensionGroup')), min_occurs=0L, max_occurs=None)
    )
ViewVolumeType._GroupModel_2 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(ViewVolumeType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'leftFov')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(ViewVolumeType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'rightFov')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(ViewVolumeType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'bottomFov')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(ViewVolumeType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'topFov')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(ViewVolumeType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'near')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(ViewVolumeType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'ViewVolumeSimpleExtensionGroup')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(ViewVolumeType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'ViewVolumeObjectExtensionGroup')), min_occurs=0L, max_occurs=None)
    )
ViewVolumeType._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(ViewVolumeType._GroupModel_, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(ViewVolumeType._GroupModel_2, min_occurs=1, max_occurs=1)
    )
ViewVolumeType._ContentModel = pyxb.binding.content.ParticleModel(ViewVolumeType._GroupModel, min_occurs=1, max_occurs=1)



CameraType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'altitude'), pyxb.binding.datatypes.double, scope=CameraType))

CameraType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'roll'), angle180Type, scope=CameraType))

CameraType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'longitude'), angle180Type, scope=CameraType))

CameraType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'heading'), angle360Type, scope=CameraType))

CameraType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'altitudeModeGroup'), pyxb.binding.datatypes.anyType, abstract=pyxb.binding.datatypes.boolean(1), scope=CameraType))

CameraType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'latitude'), angle90Type, scope=CameraType))

CameraType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'CameraObjectExtensionGroup'), pyxb.binding.datatypes.anyType, abstract=pyxb.binding.datatypes.boolean(1), scope=CameraType))

CameraType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'tilt'), anglepos180Type, scope=CameraType))

CameraType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'CameraSimpleExtensionGroup'), pyxb.binding.datatypes.anySimpleType, abstract=pyxb.binding.datatypes.boolean(1), scope=CameraType))
CameraType._GroupModel_2 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(CameraType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'ObjectSimpleExtensionGroup')), min_occurs=0L, max_occurs=None)
    )
CameraType._GroupModel_3 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(CameraType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'AbstractViewSimpleExtensionGroup')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(CameraType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'AbstractViewObjectExtensionGroup')), min_occurs=0L, max_occurs=None)
    )
CameraType._GroupModel_ = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(CameraType._GroupModel_2, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(CameraType._GroupModel_3, min_occurs=1, max_occurs=1)
    )
CameraType._GroupModel_4 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(CameraType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'longitude')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(CameraType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'latitude')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(CameraType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'altitude')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(CameraType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'heading')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(CameraType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'tilt')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(CameraType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'roll')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(CameraType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'altitudeModeGroup')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(CameraType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'CameraSimpleExtensionGroup')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(CameraType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'CameraObjectExtensionGroup')), min_occurs=0L, max_occurs=None)
    )
CameraType._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(CameraType._GroupModel_, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(CameraType._GroupModel_4, min_occurs=1, max_occurs=1)
    )
CameraType._ContentModel = pyxb.binding.content.ParticleModel(CameraType._GroupModel, min_occurs=1, max_occurs=1)



ImagePyramidType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'gridOrigin'), gridOriginEnumType, scope=ImagePyramidType))

ImagePyramidType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'maxWidth'), pyxb.binding.datatypes.int, scope=ImagePyramidType))

ImagePyramidType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'ImagePyramidSimpleExtensionGroup'), pyxb.binding.datatypes.anySimpleType, abstract=pyxb.binding.datatypes.boolean(1), scope=ImagePyramidType))

ImagePyramidType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'maxHeight'), pyxb.binding.datatypes.int, scope=ImagePyramidType))

ImagePyramidType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'ImagePyramidObjectExtensionGroup'), pyxb.binding.datatypes.anyType, abstract=pyxb.binding.datatypes.boolean(1), scope=ImagePyramidType))

ImagePyramidType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'tileSize'), pyxb.binding.datatypes.int, scope=ImagePyramidType))
ImagePyramidType._GroupModel_ = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(ImagePyramidType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'ObjectSimpleExtensionGroup')), min_occurs=0L, max_occurs=None)
    )
ImagePyramidType._GroupModel_2 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(ImagePyramidType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'tileSize')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(ImagePyramidType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'maxWidth')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(ImagePyramidType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'maxHeight')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(ImagePyramidType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'gridOrigin')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(ImagePyramidType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'ImagePyramidSimpleExtensionGroup')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(ImagePyramidType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'ImagePyramidObjectExtensionGroup')), min_occurs=0L, max_occurs=None)
    )
ImagePyramidType._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(ImagePyramidType._GroupModel_, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(ImagePyramidType._GroupModel_2, min_occurs=1, max_occurs=1)
    )
ImagePyramidType._ContentModel = pyxb.binding.content.ParticleModel(ImagePyramidType._GroupModel, min_occurs=1, max_occurs=1)



GroundOverlayType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'GroundOverlaySimpleExtensionGroup'), pyxb.binding.datatypes.anySimpleType, abstract=pyxb.binding.datatypes.boolean(1), scope=GroundOverlayType))

GroundOverlayType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'GroundOverlayObjectExtensionGroup'), pyxb.binding.datatypes.anyType, abstract=pyxb.binding.datatypes.boolean(1), scope=GroundOverlayType))

GroundOverlayType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'altitude'), pyxb.binding.datatypes.double, scope=GroundOverlayType))

GroundOverlayType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'altitudeModeGroup'), pyxb.binding.datatypes.anyType, abstract=pyxb.binding.datatypes.boolean(1), scope=GroundOverlayType))

GroundOverlayType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'LatLonBox'), LatLonBoxType, scope=GroundOverlayType))
GroundOverlayType._GroupModel_3 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(GroundOverlayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'ObjectSimpleExtensionGroup')), min_occurs=0L, max_occurs=None)
    )
GroundOverlayType._GroupModel_5 = pyxb.binding.content.GroupChoice(
    pyxb.binding.content.ParticleModel(GroundOverlayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Snippet')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(GroundOverlayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'snippet')), min_occurs=0L, max_occurs=1)
    )
GroundOverlayType._GroupModel_6 = pyxb.binding.content.GroupChoice(
    pyxb.binding.content.ParticleModel(GroundOverlayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Metadata')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(GroundOverlayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'ExtendedData')), min_occurs=0L, max_occurs=1)
    )
GroundOverlayType._GroupModel_4 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(GroundOverlayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'name')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(GroundOverlayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'visibility')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(GroundOverlayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'open')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(GroundOverlayType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/2005/Atom'), u'author')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(GroundOverlayType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/2005/Atom'), u'link')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(GroundOverlayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'address')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(GroundOverlayType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'urn:oasis:names:tc:ciq:xsdschema:xAL:2.0'), u'AddressDetails')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(GroundOverlayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'phoneNumber')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(GroundOverlayType._GroupModel_5, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(GroundOverlayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'description')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(GroundOverlayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'AbstractViewGroup')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(GroundOverlayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'AbstractTimePrimitiveGroup')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(GroundOverlayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'styleUrl')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(GroundOverlayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'AbstractStyleSelectorGroup')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(GroundOverlayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Region')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(GroundOverlayType._GroupModel_6, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(GroundOverlayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'AbstractFeatureSimpleExtensionGroup')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(GroundOverlayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'AbstractFeatureObjectExtensionGroup')), min_occurs=0L, max_occurs=None)
    )
GroundOverlayType._GroupModel_2 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(GroundOverlayType._GroupModel_3, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(GroundOverlayType._GroupModel_4, min_occurs=1, max_occurs=1)
    )
GroundOverlayType._GroupModel_7 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(GroundOverlayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'color')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(GroundOverlayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'drawOrder')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(GroundOverlayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Icon')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(GroundOverlayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'AbstractOverlaySimpleExtensionGroup')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(GroundOverlayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'AbstractOverlayObjectExtensionGroup')), min_occurs=0L, max_occurs=None)
    )
GroundOverlayType._GroupModel_ = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(GroundOverlayType._GroupModel_2, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(GroundOverlayType._GroupModel_7, min_occurs=1, max_occurs=1)
    )
GroundOverlayType._GroupModel_8 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(GroundOverlayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'altitude')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(GroundOverlayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'altitudeModeGroup')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(GroundOverlayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'LatLonBox')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(GroundOverlayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'GroundOverlaySimpleExtensionGroup')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(GroundOverlayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'GroundOverlayObjectExtensionGroup')), min_occurs=0L, max_occurs=None)
    )
GroundOverlayType._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(GroundOverlayType._GroupModel_, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(GroundOverlayType._GroupModel_8, min_occurs=1, max_occurs=1)
    )
GroundOverlayType._ContentModel = pyxb.binding.content.ParticleModel(GroundOverlayType._GroupModel, min_occurs=1, max_occurs=1)


MetadataType._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=pyxb.binding.content.Wildcard.NC_any), min_occurs=0L, max_occurs=None)
    )
MetadataType._ContentModel = pyxb.binding.content.ParticleModel(MetadataType._GroupModel, min_occurs=1, max_occurs=1)



PairType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'key'), styleStateEnumType, scope=PairType))

PairType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'styleUrl'), pyxb.binding.datatypes.anyURI, scope=PairType))

PairType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'PairObjectExtensionGroup'), pyxb.binding.datatypes.anyType, abstract=pyxb.binding.datatypes.boolean(1), scope=PairType))

PairType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'PairSimpleExtensionGroup'), pyxb.binding.datatypes.anySimpleType, abstract=pyxb.binding.datatypes.boolean(1), scope=PairType))

PairType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'AbstractStyleSelectorGroup'), AbstractStyleSelectorType, abstract=pyxb.binding.datatypes.boolean(1), scope=PairType))
PairType._GroupModel_ = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(PairType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'ObjectSimpleExtensionGroup')), min_occurs=0L, max_occurs=None)
    )
PairType._GroupModel_2 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(PairType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'key')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(PairType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'styleUrl')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(PairType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'AbstractStyleSelectorGroup')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(PairType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'PairSimpleExtensionGroup')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(PairType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'PairObjectExtensionGroup')), min_occurs=0L, max_occurs=None)
    )
PairType._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(PairType._GroupModel_, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(PairType._GroupModel_2, min_occurs=1, max_occurs=1)
    )
PairType._ContentModel = pyxb.binding.content.ParticleModel(PairType._GroupModel, min_occurs=1, max_occurs=1)



ExtendedDataType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'SchemaData'), SchemaDataType, scope=ExtendedDataType))

ExtendedDataType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Data'), DataType, scope=ExtendedDataType))
ExtendedDataType._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(ExtendedDataType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Data')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(ExtendedDataType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'SchemaData')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://www.opengis.net/kml/2.2')), min_occurs=0L, max_occurs=None)
    )
ExtendedDataType._ContentModel = pyxb.binding.content.ParticleModel(ExtendedDataType._GroupModel, min_occurs=1, max_occurs=1)



StyleMapType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'StyleMapSimpleExtensionGroup'), pyxb.binding.datatypes.anySimpleType, abstract=pyxb.binding.datatypes.boolean(1), scope=StyleMapType))

StyleMapType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Pair'), PairType, scope=StyleMapType))

StyleMapType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'StyleMapObjectExtensionGroup'), pyxb.binding.datatypes.anyType, abstract=pyxb.binding.datatypes.boolean(1), scope=StyleMapType))
StyleMapType._GroupModel_2 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(StyleMapType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'ObjectSimpleExtensionGroup')), min_occurs=0L, max_occurs=None)
    )
StyleMapType._GroupModel_3 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(StyleMapType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'AbstractStyleSelectorSimpleExtensionGroup')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(StyleMapType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'AbstractStyleSelectorObjectExtensionGroup')), min_occurs=0L, max_occurs=None)
    )
StyleMapType._GroupModel_ = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(StyleMapType._GroupModel_2, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(StyleMapType._GroupModel_3, min_occurs=1, max_occurs=1)
    )
StyleMapType._GroupModel_4 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(StyleMapType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Pair')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(StyleMapType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'StyleMapSimpleExtensionGroup')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(StyleMapType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'StyleMapObjectExtensionGroup')), min_occurs=0L, max_occurs=None)
    )
StyleMapType._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(StyleMapType._GroupModel_, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(StyleMapType._GroupModel_4, min_occurs=1, max_occurs=1)
    )
StyleMapType._ContentModel = pyxb.binding.content.ParticleModel(StyleMapType._GroupModel, min_occurs=1, max_occurs=1)



OrientationType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'OrientationSimpleExtensionGroup'), pyxb.binding.datatypes.anySimpleType, abstract=pyxb.binding.datatypes.boolean(1), scope=OrientationType))

OrientationType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'OrientationObjectExtensionGroup'), pyxb.binding.datatypes.anyType, abstract=pyxb.binding.datatypes.boolean(1), scope=OrientationType))

OrientationType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'roll'), angle180Type, scope=OrientationType))

OrientationType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'tilt'), anglepos180Type, scope=OrientationType))

OrientationType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'heading'), angle360Type, scope=OrientationType))
OrientationType._GroupModel_ = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(OrientationType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'ObjectSimpleExtensionGroup')), min_occurs=0L, max_occurs=None)
    )
OrientationType._GroupModel_2 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(OrientationType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'heading')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(OrientationType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'tilt')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(OrientationType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'roll')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(OrientationType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'OrientationSimpleExtensionGroup')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(OrientationType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'OrientationObjectExtensionGroup')), min_occurs=0L, max_occurs=None)
    )
OrientationType._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(OrientationType._GroupModel_, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(OrientationType._GroupModel_2, min_occurs=1, max_occurs=1)
    )
OrientationType._ContentModel = pyxb.binding.content.ParticleModel(OrientationType._GroupModel, min_occurs=1, max_occurs=1)



PointType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'altitudeModeGroup'), pyxb.binding.datatypes.anyType, abstract=pyxb.binding.datatypes.boolean(1), scope=PointType))

PointType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'PointObjectExtensionGroup'), pyxb.binding.datatypes.anyType, abstract=pyxb.binding.datatypes.boolean(1), scope=PointType))

PointType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'coordinates'), coordinatesType, scope=PointType))

PointType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'extrude'), pyxb.binding.datatypes.boolean, scope=PointType))

PointType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'PointSimpleExtensionGroup'), pyxb.binding.datatypes.anySimpleType, abstract=pyxb.binding.datatypes.boolean(1), scope=PointType))
PointType._GroupModel_2 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(PointType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'ObjectSimpleExtensionGroup')), min_occurs=0L, max_occurs=None)
    )
PointType._GroupModel_3 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(PointType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'AbstractGeometrySimpleExtensionGroup')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(PointType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'AbstractGeometryObjectExtensionGroup')), min_occurs=0L, max_occurs=None)
    )
PointType._GroupModel_ = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(PointType._GroupModel_2, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(PointType._GroupModel_3, min_occurs=1, max_occurs=1)
    )
PointType._GroupModel_4 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(PointType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'extrude')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(PointType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'altitudeModeGroup')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(PointType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'coordinates')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(PointType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'PointSimpleExtensionGroup')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(PointType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'PointObjectExtensionGroup')), min_occurs=0L, max_occurs=None)
    )
PointType._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(PointType._GroupModel_, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(PointType._GroupModel_4, min_occurs=1, max_occurs=1)
    )
PointType._ContentModel = pyxb.binding.content.ParticleModel(PointType._GroupModel, min_occurs=1, max_occurs=1)



AbstractLatLonBoxType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'AbstractLatLonBoxSimpleExtensionGroup'), pyxb.binding.datatypes.anySimpleType, abstract=pyxb.binding.datatypes.boolean(1), scope=AbstractLatLonBoxType))

AbstractLatLonBoxType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'north'), angle180Type, scope=AbstractLatLonBoxType))

AbstractLatLonBoxType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'AbstractLatLonBoxObjectExtensionGroup'), pyxb.binding.datatypes.anyType, abstract=pyxb.binding.datatypes.boolean(1), scope=AbstractLatLonBoxType))

AbstractLatLonBoxType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'east'), angle180Type, scope=AbstractLatLonBoxType))

AbstractLatLonBoxType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'west'), angle180Type, scope=AbstractLatLonBoxType))

AbstractLatLonBoxType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'south'), angle180Type, scope=AbstractLatLonBoxType))
AbstractLatLonBoxType._GroupModel_ = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(AbstractLatLonBoxType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'ObjectSimpleExtensionGroup')), min_occurs=0L, max_occurs=None)
    )
AbstractLatLonBoxType._GroupModel_2 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(AbstractLatLonBoxType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'north')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(AbstractLatLonBoxType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'south')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(AbstractLatLonBoxType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'east')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(AbstractLatLonBoxType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'west')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(AbstractLatLonBoxType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'AbstractLatLonBoxSimpleExtensionGroup')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(AbstractLatLonBoxType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'AbstractLatLonBoxObjectExtensionGroup')), min_occurs=0L, max_occurs=None)
    )
AbstractLatLonBoxType._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(AbstractLatLonBoxType._GroupModel_, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(AbstractLatLonBoxType._GroupModel_2, min_occurs=1, max_occurs=1)
    )
AbstractLatLonBoxType._ContentModel = pyxb.binding.content.ParticleModel(AbstractLatLonBoxType._GroupModel, min_occurs=1, max_occurs=1)



LatLonBoxType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'LatLonBoxObjectExtensionGroup'), pyxb.binding.datatypes.anyType, abstract=pyxb.binding.datatypes.boolean(1), scope=LatLonBoxType))

LatLonBoxType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'rotation'), angle180Type, scope=LatLonBoxType))

LatLonBoxType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'LatLonBoxSimpleExtensionGroup'), pyxb.binding.datatypes.anySimpleType, abstract=pyxb.binding.datatypes.boolean(1), scope=LatLonBoxType))
LatLonBoxType._GroupModel_2 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(LatLonBoxType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'ObjectSimpleExtensionGroup')), min_occurs=0L, max_occurs=None)
    )
LatLonBoxType._GroupModel_3 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(LatLonBoxType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'north')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(LatLonBoxType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'south')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(LatLonBoxType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'east')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(LatLonBoxType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'west')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(LatLonBoxType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'AbstractLatLonBoxSimpleExtensionGroup')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(LatLonBoxType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'AbstractLatLonBoxObjectExtensionGroup')), min_occurs=0L, max_occurs=None)
    )
LatLonBoxType._GroupModel_ = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(LatLonBoxType._GroupModel_2, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(LatLonBoxType._GroupModel_3, min_occurs=1, max_occurs=1)
    )
LatLonBoxType._GroupModel_4 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(LatLonBoxType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'rotation')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(LatLonBoxType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'LatLonBoxSimpleExtensionGroup')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(LatLonBoxType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'LatLonBoxObjectExtensionGroup')), min_occurs=0L, max_occurs=None)
    )
LatLonBoxType._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(LatLonBoxType._GroupModel_, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(LatLonBoxType._GroupModel_4, min_occurs=1, max_occurs=1)
    )
LatLonBoxType._ContentModel = pyxb.binding.content.ParticleModel(LatLonBoxType._GroupModel, min_occurs=1, max_occurs=1)



LineStringType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'coordinates'), coordinatesType, scope=LineStringType))

LineStringType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'tessellate'), pyxb.binding.datatypes.boolean, scope=LineStringType))

LineStringType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'LineStringSimpleExtensionGroup'), pyxb.binding.datatypes.anySimpleType, abstract=pyxb.binding.datatypes.boolean(1), scope=LineStringType))

LineStringType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'altitudeModeGroup'), pyxb.binding.datatypes.anyType, abstract=pyxb.binding.datatypes.boolean(1), scope=LineStringType))

LineStringType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'LineStringObjectExtensionGroup'), pyxb.binding.datatypes.anyType, abstract=pyxb.binding.datatypes.boolean(1), scope=LineStringType))

LineStringType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'extrude'), pyxb.binding.datatypes.boolean, scope=LineStringType))
LineStringType._GroupModel_2 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(LineStringType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'ObjectSimpleExtensionGroup')), min_occurs=0L, max_occurs=None)
    )
LineStringType._GroupModel_3 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(LineStringType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'AbstractGeometrySimpleExtensionGroup')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(LineStringType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'AbstractGeometryObjectExtensionGroup')), min_occurs=0L, max_occurs=None)
    )
LineStringType._GroupModel_ = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(LineStringType._GroupModel_2, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(LineStringType._GroupModel_3, min_occurs=1, max_occurs=1)
    )
LineStringType._GroupModel_4 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(LineStringType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'extrude')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(LineStringType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'tessellate')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(LineStringType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'altitudeModeGroup')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(LineStringType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'coordinates')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(LineStringType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'LineStringSimpleExtensionGroup')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(LineStringType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'LineStringObjectExtensionGroup')), min_occurs=0L, max_occurs=None)
    )
LineStringType._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(LineStringType._GroupModel_, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(LineStringType._GroupModel_4, min_occurs=1, max_occurs=1)
    )
LineStringType._ContentModel = pyxb.binding.content.ParticleModel(LineStringType._GroupModel, min_occurs=1, max_occurs=1)



KmlType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'AbstractFeatureGroup'), AbstractFeatureType, abstract=pyxb.binding.datatypes.boolean(1), scope=KmlType))

KmlType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'KmlSimpleExtensionGroup'), pyxb.binding.datatypes.anySimpleType, abstract=pyxb.binding.datatypes.boolean(1), scope=KmlType))

KmlType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'NetworkLinkControl'), NetworkLinkControlType, scope=KmlType))

KmlType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'KmlObjectExtensionGroup'), pyxb.binding.datatypes.anyType, abstract=pyxb.binding.datatypes.boolean(1), scope=KmlType))
KmlType._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(KmlType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'NetworkLinkControl')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(KmlType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'AbstractFeatureGroup')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(KmlType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'KmlSimpleExtensionGroup')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(KmlType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'KmlObjectExtensionGroup')), min_occurs=0L, max_occurs=None)
    )
KmlType._ContentModel = pyxb.binding.content.ParticleModel(KmlType._GroupModel, min_occurs=1, max_occurs=1)



PolygonType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'extrude'), pyxb.binding.datatypes.boolean, scope=PolygonType))

PolygonType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'PolygonObjectExtensionGroup'), pyxb.binding.datatypes.anyType, abstract=pyxb.binding.datatypes.boolean(1), scope=PolygonType))

PolygonType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'tessellate'), pyxb.binding.datatypes.boolean, scope=PolygonType))

PolygonType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'innerBoundaryIs'), BoundaryType, scope=PolygonType))

PolygonType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'altitudeModeGroup'), pyxb.binding.datatypes.anyType, abstract=pyxb.binding.datatypes.boolean(1), scope=PolygonType))

PolygonType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'PolygonSimpleExtensionGroup'), pyxb.binding.datatypes.anySimpleType, abstract=pyxb.binding.datatypes.boolean(1), scope=PolygonType))

PolygonType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'outerBoundaryIs'), BoundaryType, scope=PolygonType))
PolygonType._GroupModel_2 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(PolygonType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'ObjectSimpleExtensionGroup')), min_occurs=0L, max_occurs=None)
    )
PolygonType._GroupModel_3 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(PolygonType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'AbstractGeometrySimpleExtensionGroup')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(PolygonType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'AbstractGeometryObjectExtensionGroup')), min_occurs=0L, max_occurs=None)
    )
PolygonType._GroupModel_ = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(PolygonType._GroupModel_2, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(PolygonType._GroupModel_3, min_occurs=1, max_occurs=1)
    )
PolygonType._GroupModel_4 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(PolygonType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'extrude')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(PolygonType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'tessellate')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(PolygonType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'altitudeModeGroup')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(PolygonType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'outerBoundaryIs')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(PolygonType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'innerBoundaryIs')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(PolygonType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'PolygonSimpleExtensionGroup')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(PolygonType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'PolygonObjectExtensionGroup')), min_occurs=0L, max_occurs=None)
    )
PolygonType._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(PolygonType._GroupModel_, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(PolygonType._GroupModel_4, min_occurs=1, max_occurs=1)
    )
PolygonType._ContentModel = pyxb.binding.content.ParticleModel(PolygonType._GroupModel, min_occurs=1, max_occurs=1)



PhotoOverlayType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'PhotoOverlayObjectExtensionGroup'), pyxb.binding.datatypes.anyType, abstract=pyxb.binding.datatypes.boolean(1), scope=PhotoOverlayType))

PhotoOverlayType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'rotation'), angle180Type, scope=PhotoOverlayType))

PhotoOverlayType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'ViewVolume'), ViewVolumeType, scope=PhotoOverlayType))

PhotoOverlayType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'ImagePyramid'), ImagePyramidType, scope=PhotoOverlayType))

PhotoOverlayType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Point'), PointType, scope=PhotoOverlayType))

PhotoOverlayType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'shape'), shapeEnumType, scope=PhotoOverlayType))

PhotoOverlayType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'PhotoOverlaySimpleExtensionGroup'), pyxb.binding.datatypes.anySimpleType, abstract=pyxb.binding.datatypes.boolean(1), scope=PhotoOverlayType))
PhotoOverlayType._GroupModel_3 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(PhotoOverlayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'ObjectSimpleExtensionGroup')), min_occurs=0L, max_occurs=None)
    )
PhotoOverlayType._GroupModel_5 = pyxb.binding.content.GroupChoice(
    pyxb.binding.content.ParticleModel(PhotoOverlayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Snippet')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(PhotoOverlayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'snippet')), min_occurs=0L, max_occurs=1)
    )
PhotoOverlayType._GroupModel_6 = pyxb.binding.content.GroupChoice(
    pyxb.binding.content.ParticleModel(PhotoOverlayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Metadata')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(PhotoOverlayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'ExtendedData')), min_occurs=0L, max_occurs=1)
    )
PhotoOverlayType._GroupModel_4 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(PhotoOverlayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'name')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(PhotoOverlayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'visibility')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(PhotoOverlayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'open')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(PhotoOverlayType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/2005/Atom'), u'author')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(PhotoOverlayType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/2005/Atom'), u'link')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(PhotoOverlayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'address')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(PhotoOverlayType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'urn:oasis:names:tc:ciq:xsdschema:xAL:2.0'), u'AddressDetails')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(PhotoOverlayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'phoneNumber')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(PhotoOverlayType._GroupModel_5, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(PhotoOverlayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'description')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(PhotoOverlayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'AbstractViewGroup')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(PhotoOverlayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'AbstractTimePrimitiveGroup')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(PhotoOverlayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'styleUrl')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(PhotoOverlayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'AbstractStyleSelectorGroup')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(PhotoOverlayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Region')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(PhotoOverlayType._GroupModel_6, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(PhotoOverlayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'AbstractFeatureSimpleExtensionGroup')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(PhotoOverlayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'AbstractFeatureObjectExtensionGroup')), min_occurs=0L, max_occurs=None)
    )
PhotoOverlayType._GroupModel_2 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(PhotoOverlayType._GroupModel_3, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(PhotoOverlayType._GroupModel_4, min_occurs=1, max_occurs=1)
    )
PhotoOverlayType._GroupModel_7 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(PhotoOverlayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'color')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(PhotoOverlayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'drawOrder')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(PhotoOverlayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Icon')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(PhotoOverlayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'AbstractOverlaySimpleExtensionGroup')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(PhotoOverlayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'AbstractOverlayObjectExtensionGroup')), min_occurs=0L, max_occurs=None)
    )
PhotoOverlayType._GroupModel_ = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(PhotoOverlayType._GroupModel_2, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(PhotoOverlayType._GroupModel_7, min_occurs=1, max_occurs=1)
    )
PhotoOverlayType._GroupModel_8 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(PhotoOverlayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'rotation')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(PhotoOverlayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'ViewVolume')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(PhotoOverlayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'ImagePyramid')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(PhotoOverlayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Point')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(PhotoOverlayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'shape')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(PhotoOverlayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'PhotoOverlaySimpleExtensionGroup')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(PhotoOverlayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'PhotoOverlayObjectExtensionGroup')), min_occurs=0L, max_occurs=None)
    )
PhotoOverlayType._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(PhotoOverlayType._GroupModel_, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(PhotoOverlayType._GroupModel_8, min_occurs=1, max_occurs=1)
    )
PhotoOverlayType._ContentModel = pyxb.binding.content.ParticleModel(PhotoOverlayType._GroupModel, min_occurs=1, max_occurs=1)



TimeStampType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'TimeStampObjectExtensionGroup'), pyxb.binding.datatypes.anyType, abstract=pyxb.binding.datatypes.boolean(1), scope=TimeStampType))

TimeStampType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'when'), dateTimeType, scope=TimeStampType))

TimeStampType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'TimeStampSimpleExtensionGroup'), pyxb.binding.datatypes.anySimpleType, abstract=pyxb.binding.datatypes.boolean(1), scope=TimeStampType))
TimeStampType._GroupModel_2 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(TimeStampType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'ObjectSimpleExtensionGroup')), min_occurs=0L, max_occurs=None)
    )
TimeStampType._GroupModel_3 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(TimeStampType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'AbstractTimePrimitiveSimpleExtensionGroup')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(TimeStampType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'AbstractTimePrimitiveObjectExtensionGroup')), min_occurs=0L, max_occurs=None)
    )
TimeStampType._GroupModel_ = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(TimeStampType._GroupModel_2, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(TimeStampType._GroupModel_3, min_occurs=1, max_occurs=1)
    )
TimeStampType._GroupModel_4 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(TimeStampType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'when')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(TimeStampType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'TimeStampSimpleExtensionGroup')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(TimeStampType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'TimeStampObjectExtensionGroup')), min_occurs=0L, max_occurs=None)
    )
TimeStampType._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(TimeStampType._GroupModel_, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(TimeStampType._GroupModel_4, min_occurs=1, max_occurs=1)
    )
TimeStampType._ContentModel = pyxb.binding.content.ParticleModel(TimeStampType._GroupModel, min_occurs=1, max_occurs=1)



ModelType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'ModelObjectExtensionGroup'), pyxb.binding.datatypes.anyType, abstract=pyxb.binding.datatypes.boolean(1), scope=ModelType))

ModelType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Orientation'), OrientationType, scope=ModelType))

ModelType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'ResourceMap'), ResourceMapType, scope=ModelType))

ModelType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'altitudeModeGroup'), pyxb.binding.datatypes.anyType, abstract=pyxb.binding.datatypes.boolean(1), scope=ModelType))

ModelType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Scale'), ScaleType, scope=ModelType))

ModelType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'ModelSimpleExtensionGroup'), pyxb.binding.datatypes.anySimpleType, abstract=pyxb.binding.datatypes.boolean(1), scope=ModelType))

ModelType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Location'), LocationType, scope=ModelType))

ModelType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Link'), LinkType, scope=ModelType))
ModelType._GroupModel_2 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(ModelType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'ObjectSimpleExtensionGroup')), min_occurs=0L, max_occurs=None)
    )
ModelType._GroupModel_3 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(ModelType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'AbstractGeometrySimpleExtensionGroup')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(ModelType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'AbstractGeometryObjectExtensionGroup')), min_occurs=0L, max_occurs=None)
    )
ModelType._GroupModel_ = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(ModelType._GroupModel_2, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(ModelType._GroupModel_3, min_occurs=1, max_occurs=1)
    )
ModelType._GroupModel_4 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(ModelType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'altitudeModeGroup')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(ModelType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Location')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(ModelType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Orientation')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(ModelType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Scale')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(ModelType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Link')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(ModelType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'ResourceMap')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(ModelType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'ModelSimpleExtensionGroup')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(ModelType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'ModelObjectExtensionGroup')), min_occurs=0L, max_occurs=None)
    )
ModelType._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(ModelType._GroupModel_, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(ModelType._GroupModel_4, min_occurs=1, max_occurs=1)
    )
ModelType._ContentModel = pyxb.binding.content.ParticleModel(ModelType._GroupModel, min_occurs=1, max_occurs=1)



CreateType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'AbstractContainerGroup'), AbstractContainerType, abstract=pyxb.binding.datatypes.boolean(1), scope=CreateType))
CreateType._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(CreateType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'AbstractContainerGroup')), min_occurs=0L, max_occurs=None)
    )
CreateType._ContentModel = pyxb.binding.content.ParticleModel(CreateType._GroupModel, min_occurs=1, max_occurs=1)



DeleteType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'AbstractFeatureGroup'), AbstractFeatureType, abstract=pyxb.binding.datatypes.boolean(1), scope=DeleteType))
DeleteType._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(DeleteType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'AbstractFeatureGroup')), min_occurs=0L, max_occurs=None)
    )
DeleteType._ContentModel = pyxb.binding.content.ParticleModel(DeleteType._GroupModel, min_occurs=1, max_occurs=1)



LookAtType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'tilt'), anglepos180Type, scope=LookAtType))

LookAtType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'altitude'), pyxb.binding.datatypes.double, scope=LookAtType))

LookAtType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'range'), pyxb.binding.datatypes.double, scope=LookAtType))

LookAtType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'longitude'), angle180Type, scope=LookAtType))

LookAtType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'LookAtObjectExtensionGroup'), pyxb.binding.datatypes.anyType, abstract=pyxb.binding.datatypes.boolean(1), scope=LookAtType))

LookAtType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'LookAtSimpleExtensionGroup'), pyxb.binding.datatypes.anySimpleType, abstract=pyxb.binding.datatypes.boolean(1), scope=LookAtType))

LookAtType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'altitudeModeGroup'), pyxb.binding.datatypes.anyType, abstract=pyxb.binding.datatypes.boolean(1), scope=LookAtType))

LookAtType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'latitude'), angle90Type, scope=LookAtType))

LookAtType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'heading'), angle360Type, scope=LookAtType))
LookAtType._GroupModel_2 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(LookAtType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'ObjectSimpleExtensionGroup')), min_occurs=0L, max_occurs=None)
    )
LookAtType._GroupModel_3 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(LookAtType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'AbstractViewSimpleExtensionGroup')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(LookAtType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'AbstractViewObjectExtensionGroup')), min_occurs=0L, max_occurs=None)
    )
LookAtType._GroupModel_ = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(LookAtType._GroupModel_2, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(LookAtType._GroupModel_3, min_occurs=1, max_occurs=1)
    )
LookAtType._GroupModel_4 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(LookAtType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'longitude')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(LookAtType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'latitude')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(LookAtType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'altitude')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(LookAtType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'heading')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(LookAtType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'tilt')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(LookAtType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'range')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(LookAtType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'altitudeModeGroup')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(LookAtType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'LookAtSimpleExtensionGroup')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(LookAtType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'LookAtObjectExtensionGroup')), min_occurs=0L, max_occurs=None)
    )
LookAtType._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(LookAtType._GroupModel_, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(LookAtType._GroupModel_4, min_occurs=1, max_occurs=1)
    )
LookAtType._ContentModel = pyxb.binding.content.ParticleModel(LookAtType._GroupModel, min_occurs=1, max_occurs=1)



BalloonStyleType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'BalloonStyleSimpleExtensionGroup'), pyxb.binding.datatypes.anySimpleType, abstract=pyxb.binding.datatypes.boolean(1), scope=BalloonStyleType))

BalloonStyleType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'color'), colorType, scope=BalloonStyleType))

BalloonStyleType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'text'), pyxb.binding.datatypes.string, scope=BalloonStyleType))

BalloonStyleType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'BalloonStyleObjectExtensionGroup'), pyxb.binding.datatypes.anyType, abstract=pyxb.binding.datatypes.boolean(1), scope=BalloonStyleType))

BalloonStyleType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'bgColor'), colorType, scope=BalloonStyleType))

BalloonStyleType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'displayMode'), displayModeEnumType, scope=BalloonStyleType))

BalloonStyleType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'textColor'), colorType, scope=BalloonStyleType))
BalloonStyleType._GroupModel_2 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(BalloonStyleType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'ObjectSimpleExtensionGroup')), min_occurs=0L, max_occurs=None)
    )
BalloonStyleType._GroupModel_3 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(BalloonStyleType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'AbstractSubStyleSimpleExtensionGroup')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(BalloonStyleType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'AbstractSubStyleObjectExtensionGroup')), min_occurs=0L, max_occurs=None)
    )
BalloonStyleType._GroupModel_ = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(BalloonStyleType._GroupModel_2, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(BalloonStyleType._GroupModel_3, min_occurs=1, max_occurs=1)
    )
BalloonStyleType._GroupModel_5 = pyxb.binding.content.GroupChoice(
    pyxb.binding.content.ParticleModel(BalloonStyleType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'color')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(BalloonStyleType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'bgColor')), min_occurs=0L, max_occurs=1)
    )
BalloonStyleType._GroupModel_4 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(BalloonStyleType._GroupModel_5, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(BalloonStyleType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'textColor')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(BalloonStyleType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'text')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(BalloonStyleType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'displayMode')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(BalloonStyleType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'BalloonStyleSimpleExtensionGroup')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(BalloonStyleType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'BalloonStyleObjectExtensionGroup')), min_occurs=0L, max_occurs=None)
    )
BalloonStyleType._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(BalloonStyleType._GroupModel_, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(BalloonStyleType._GroupModel_4, min_occurs=1, max_occurs=1)
    )
BalloonStyleType._ContentModel = pyxb.binding.content.ParticleModel(BalloonStyleType._GroupModel, min_occurs=1, max_occurs=1)



ListStyleType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'listItemType'), listItemTypeEnumType, scope=ListStyleType))

ListStyleType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'maxSnippetLines'), pyxb.binding.datatypes.int, scope=ListStyleType))

ListStyleType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'bgColor'), colorType, scope=ListStyleType))

ListStyleType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'ListStyleSimpleExtensionGroup'), pyxb.binding.datatypes.anySimpleType, abstract=pyxb.binding.datatypes.boolean(1), scope=ListStyleType))

ListStyleType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'ItemIcon'), ItemIconType, scope=ListStyleType))

ListStyleType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'ListStyleObjectExtensionGroup'), pyxb.binding.datatypes.anyType, abstract=pyxb.binding.datatypes.boolean(1), scope=ListStyleType))
ListStyleType._GroupModel_2 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(ListStyleType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'ObjectSimpleExtensionGroup')), min_occurs=0L, max_occurs=None)
    )
ListStyleType._GroupModel_3 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(ListStyleType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'AbstractSubStyleSimpleExtensionGroup')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(ListStyleType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'AbstractSubStyleObjectExtensionGroup')), min_occurs=0L, max_occurs=None)
    )
ListStyleType._GroupModel_ = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(ListStyleType._GroupModel_2, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(ListStyleType._GroupModel_3, min_occurs=1, max_occurs=1)
    )
ListStyleType._GroupModel_4 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(ListStyleType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'listItemType')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(ListStyleType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'bgColor')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(ListStyleType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'ItemIcon')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(ListStyleType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'maxSnippetLines')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(ListStyleType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'ListStyleSimpleExtensionGroup')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(ListStyleType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'ListStyleObjectExtensionGroup')), min_occurs=0L, max_occurs=None)
    )
ListStyleType._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(ListStyleType._GroupModel_, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(ListStyleType._GroupModel_4, min_occurs=1, max_occurs=1)
    )
ListStyleType._ContentModel = pyxb.binding.content.ParticleModel(ListStyleType._GroupModel, min_occurs=1, max_occurs=1)



ScreenOverlayType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'ScreenOverlaySimpleExtensionGroup'), pyxb.binding.datatypes.anySimpleType, abstract=pyxb.binding.datatypes.boolean(1), scope=ScreenOverlayType))

ScreenOverlayType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'ScreenOverlayObjectExtensionGroup'), pyxb.binding.datatypes.anyType, abstract=pyxb.binding.datatypes.boolean(1), scope=ScreenOverlayType))

ScreenOverlayType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'rotation'), angle180Type, scope=ScreenOverlayType))

ScreenOverlayType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'overlayXY'), vec2Type, scope=ScreenOverlayType))

ScreenOverlayType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'screenXY'), vec2Type, scope=ScreenOverlayType))

ScreenOverlayType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'rotationXY'), vec2Type, scope=ScreenOverlayType))

ScreenOverlayType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'size'), vec2Type, scope=ScreenOverlayType))
ScreenOverlayType._GroupModel_3 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(ScreenOverlayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'ObjectSimpleExtensionGroup')), min_occurs=0L, max_occurs=None)
    )
ScreenOverlayType._GroupModel_5 = pyxb.binding.content.GroupChoice(
    pyxb.binding.content.ParticleModel(ScreenOverlayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Snippet')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(ScreenOverlayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'snippet')), min_occurs=0L, max_occurs=1)
    )
ScreenOverlayType._GroupModel_6 = pyxb.binding.content.GroupChoice(
    pyxb.binding.content.ParticleModel(ScreenOverlayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Metadata')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(ScreenOverlayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'ExtendedData')), min_occurs=0L, max_occurs=1)
    )
ScreenOverlayType._GroupModel_4 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(ScreenOverlayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'name')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(ScreenOverlayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'visibility')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(ScreenOverlayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'open')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(ScreenOverlayType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/2005/Atom'), u'author')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(ScreenOverlayType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/2005/Atom'), u'link')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(ScreenOverlayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'address')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(ScreenOverlayType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'urn:oasis:names:tc:ciq:xsdschema:xAL:2.0'), u'AddressDetails')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(ScreenOverlayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'phoneNumber')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(ScreenOverlayType._GroupModel_5, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(ScreenOverlayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'description')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(ScreenOverlayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'AbstractViewGroup')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(ScreenOverlayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'AbstractTimePrimitiveGroup')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(ScreenOverlayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'styleUrl')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(ScreenOverlayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'AbstractStyleSelectorGroup')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(ScreenOverlayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Region')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(ScreenOverlayType._GroupModel_6, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(ScreenOverlayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'AbstractFeatureSimpleExtensionGroup')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(ScreenOverlayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'AbstractFeatureObjectExtensionGroup')), min_occurs=0L, max_occurs=None)
    )
ScreenOverlayType._GroupModel_2 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(ScreenOverlayType._GroupModel_3, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(ScreenOverlayType._GroupModel_4, min_occurs=1, max_occurs=1)
    )
ScreenOverlayType._GroupModel_7 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(ScreenOverlayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'color')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(ScreenOverlayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'drawOrder')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(ScreenOverlayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Icon')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(ScreenOverlayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'AbstractOverlaySimpleExtensionGroup')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(ScreenOverlayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'AbstractOverlayObjectExtensionGroup')), min_occurs=0L, max_occurs=None)
    )
ScreenOverlayType._GroupModel_ = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(ScreenOverlayType._GroupModel_2, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(ScreenOverlayType._GroupModel_7, min_occurs=1, max_occurs=1)
    )
ScreenOverlayType._GroupModel_8 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(ScreenOverlayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'overlayXY')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(ScreenOverlayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'screenXY')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(ScreenOverlayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'rotationXY')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(ScreenOverlayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'size')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(ScreenOverlayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'rotation')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(ScreenOverlayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'ScreenOverlaySimpleExtensionGroup')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(ScreenOverlayType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'ScreenOverlayObjectExtensionGroup')), min_occurs=0L, max_occurs=None)
    )
ScreenOverlayType._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(ScreenOverlayType._GroupModel_, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(ScreenOverlayType._GroupModel_8, min_occurs=1, max_occurs=1)
    )
ScreenOverlayType._ContentModel = pyxb.binding.content.ParticleModel(ScreenOverlayType._GroupModel, min_occurs=1, max_occurs=1)



RegionType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Lod'), LodType, scope=RegionType))

RegionType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'RegionSimpleExtensionGroup'), pyxb.binding.datatypes.anySimpleType, abstract=pyxb.binding.datatypes.boolean(1), scope=RegionType))

RegionType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'RegionObjectExtensionGroup'), pyxb.binding.datatypes.anyType, abstract=pyxb.binding.datatypes.boolean(1), scope=RegionType))

RegionType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'LatLonAltBox'), LatLonAltBoxType, scope=RegionType))
RegionType._GroupModel_ = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(RegionType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'ObjectSimpleExtensionGroup')), min_occurs=0L, max_occurs=None)
    )
RegionType._GroupModel_2 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(RegionType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'LatLonAltBox')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(RegionType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Lod')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(RegionType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'RegionSimpleExtensionGroup')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(RegionType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'RegionObjectExtensionGroup')), min_occurs=0L, max_occurs=None)
    )
RegionType._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(RegionType._GroupModel_, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(RegionType._GroupModel_2, min_occurs=1, max_occurs=1)
    )
RegionType._ContentModel = pyxb.binding.content.ParticleModel(RegionType._GroupModel, min_occurs=1, max_occurs=1)



LatLonAltBoxType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'minAltitude'), pyxb.binding.datatypes.double, scope=LatLonAltBoxType))

LatLonAltBoxType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'LatLonAltBoxSimpleExtensionGroup'), pyxb.binding.datatypes.anySimpleType, abstract=pyxb.binding.datatypes.boolean(1), scope=LatLonAltBoxType))

LatLonAltBoxType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'maxAltitude'), pyxb.binding.datatypes.double, scope=LatLonAltBoxType))

LatLonAltBoxType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'LatLonAltBoxObjectExtensionGroup'), pyxb.binding.datatypes.anyType, abstract=pyxb.binding.datatypes.boolean(1), scope=LatLonAltBoxType))

LatLonAltBoxType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'altitudeModeGroup'), pyxb.binding.datatypes.anyType, abstract=pyxb.binding.datatypes.boolean(1), scope=LatLonAltBoxType))
LatLonAltBoxType._GroupModel_2 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(LatLonAltBoxType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'ObjectSimpleExtensionGroup')), min_occurs=0L, max_occurs=None)
    )
LatLonAltBoxType._GroupModel_3 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(LatLonAltBoxType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'north')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(LatLonAltBoxType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'south')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(LatLonAltBoxType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'east')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(LatLonAltBoxType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'west')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(LatLonAltBoxType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'AbstractLatLonBoxSimpleExtensionGroup')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(LatLonAltBoxType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'AbstractLatLonBoxObjectExtensionGroup')), min_occurs=0L, max_occurs=None)
    )
LatLonAltBoxType._GroupModel_ = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(LatLonAltBoxType._GroupModel_2, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(LatLonAltBoxType._GroupModel_3, min_occurs=1, max_occurs=1)
    )
LatLonAltBoxType._GroupModel_4 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(LatLonAltBoxType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'minAltitude')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(LatLonAltBoxType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'maxAltitude')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(LatLonAltBoxType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'altitudeModeGroup')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(LatLonAltBoxType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'LatLonAltBoxSimpleExtensionGroup')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(LatLonAltBoxType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'LatLonAltBoxObjectExtensionGroup')), min_occurs=0L, max_occurs=None)
    )
LatLonAltBoxType._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(LatLonAltBoxType._GroupModel_, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(LatLonAltBoxType._GroupModel_4, min_occurs=1, max_occurs=1)
    )
LatLonAltBoxType._ContentModel = pyxb.binding.content.ParticleModel(LatLonAltBoxType._GroupModel, min_occurs=1, max_occurs=1)



FolderType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'AbstractFeatureGroup'), AbstractFeatureType, abstract=pyxb.binding.datatypes.boolean(1), scope=FolderType))

FolderType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'FolderSimpleExtensionGroup'), pyxb.binding.datatypes.anySimpleType, abstract=pyxb.binding.datatypes.boolean(1), scope=FolderType))

FolderType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'FolderObjectExtensionGroup'), pyxb.binding.datatypes.anyType, abstract=pyxb.binding.datatypes.boolean(1), scope=FolderType))
FolderType._GroupModel_3 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(FolderType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'ObjectSimpleExtensionGroup')), min_occurs=0L, max_occurs=None)
    )
FolderType._GroupModel_5 = pyxb.binding.content.GroupChoice(
    pyxb.binding.content.ParticleModel(FolderType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Snippet')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(FolderType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'snippet')), min_occurs=0L, max_occurs=1)
    )
FolderType._GroupModel_6 = pyxb.binding.content.GroupChoice(
    pyxb.binding.content.ParticleModel(FolderType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Metadata')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(FolderType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'ExtendedData')), min_occurs=0L, max_occurs=1)
    )
FolderType._GroupModel_4 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(FolderType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'name')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(FolderType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'visibility')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(FolderType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'open')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(FolderType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/2005/Atom'), u'author')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(FolderType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/2005/Atom'), u'link')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(FolderType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'address')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(FolderType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'urn:oasis:names:tc:ciq:xsdschema:xAL:2.0'), u'AddressDetails')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(FolderType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'phoneNumber')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(FolderType._GroupModel_5, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(FolderType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'description')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(FolderType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'AbstractViewGroup')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(FolderType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'AbstractTimePrimitiveGroup')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(FolderType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'styleUrl')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(FolderType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'AbstractStyleSelectorGroup')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(FolderType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Region')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(FolderType._GroupModel_6, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(FolderType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'AbstractFeatureSimpleExtensionGroup')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(FolderType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'AbstractFeatureObjectExtensionGroup')), min_occurs=0L, max_occurs=None)
    )
FolderType._GroupModel_2 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(FolderType._GroupModel_3, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(FolderType._GroupModel_4, min_occurs=1, max_occurs=1)
    )
FolderType._GroupModel_7 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(FolderType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'AbstractContainerSimpleExtensionGroup')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(FolderType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'AbstractContainerObjectExtensionGroup')), min_occurs=0L, max_occurs=None)
    )
FolderType._GroupModel_ = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(FolderType._GroupModel_2, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(FolderType._GroupModel_7, min_occurs=1, max_occurs=1)
    )
FolderType._GroupModel_8 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(FolderType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'AbstractFeatureGroup')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(FolderType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'FolderSimpleExtensionGroup')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(FolderType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'FolderObjectExtensionGroup')), min_occurs=0L, max_occurs=None)
    )
FolderType._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(FolderType._GroupModel_, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(FolderType._GroupModel_8, min_occurs=1, max_occurs=1)
    )
FolderType._ContentModel = pyxb.binding.content.ParticleModel(FolderType._GroupModel, min_occurs=1, max_occurs=1)



LodType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'maxLodPixels'), pyxb.binding.datatypes.double, scope=LodType))

LodType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'minFadeExtent'), pyxb.binding.datatypes.double, scope=LodType))

LodType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'minLodPixels'), pyxb.binding.datatypes.double, scope=LodType))

LodType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'LodSimpleExtensionGroup'), pyxb.binding.datatypes.anySimpleType, abstract=pyxb.binding.datatypes.boolean(1), scope=LodType))

LodType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'maxFadeExtent'), pyxb.binding.datatypes.double, scope=LodType))

LodType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'LodObjectExtensionGroup'), pyxb.binding.datatypes.anyType, abstract=pyxb.binding.datatypes.boolean(1), scope=LodType))
LodType._GroupModel_ = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(LodType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'ObjectSimpleExtensionGroup')), min_occurs=0L, max_occurs=None)
    )
LodType._GroupModel_2 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(LodType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'minLodPixels')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(LodType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'maxLodPixels')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(LodType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'minFadeExtent')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(LodType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'maxFadeExtent')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(LodType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'LodSimpleExtensionGroup')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(LodType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'LodObjectExtensionGroup')), min_occurs=0L, max_occurs=None)
    )
LodType._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(LodType._GroupModel_, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(LodType._GroupModel_2, min_occurs=1, max_occurs=1)
    )
LodType._ContentModel = pyxb.binding.content.ParticleModel(LodType._GroupModel, min_occurs=1, max_occurs=1)



ScaleType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'x'), pyxb.binding.datatypes.double, scope=ScaleType))

ScaleType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'ScaleSimpleExtensionGroup'), pyxb.binding.datatypes.anySimpleType, abstract=pyxb.binding.datatypes.boolean(1), scope=ScaleType))

ScaleType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'y'), pyxb.binding.datatypes.double, scope=ScaleType))

ScaleType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'ScaleObjectExtensionGroup'), pyxb.binding.datatypes.anyType, abstract=pyxb.binding.datatypes.boolean(1), scope=ScaleType))

ScaleType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'z'), pyxb.binding.datatypes.double, scope=ScaleType))
ScaleType._GroupModel_ = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(ScaleType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'ObjectSimpleExtensionGroup')), min_occurs=0L, max_occurs=None)
    )
ScaleType._GroupModel_2 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(ScaleType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'x')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(ScaleType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'y')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(ScaleType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'z')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(ScaleType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'ScaleSimpleExtensionGroup')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(ScaleType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'ScaleObjectExtensionGroup')), min_occurs=0L, max_occurs=None)
    )
ScaleType._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(ScaleType._GroupModel_, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(ScaleType._GroupModel_2, min_occurs=1, max_occurs=1)
    )
ScaleType._ContentModel = pyxb.binding.content.ParticleModel(ScaleType._GroupModel, min_occurs=1, max_occurs=1)



ResourceMapType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'ResourceMapObjectExtensionGroup'), pyxb.binding.datatypes.anyType, abstract=pyxb.binding.datatypes.boolean(1), scope=ResourceMapType))

ResourceMapType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'ResourceMapSimpleExtensionGroup'), pyxb.binding.datatypes.anySimpleType, abstract=pyxb.binding.datatypes.boolean(1), scope=ResourceMapType))

ResourceMapType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Alias'), AliasType, scope=ResourceMapType))
ResourceMapType._GroupModel_ = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(ResourceMapType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'ObjectSimpleExtensionGroup')), min_occurs=0L, max_occurs=None)
    )
ResourceMapType._GroupModel_2 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(ResourceMapType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Alias')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(ResourceMapType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'ResourceMapSimpleExtensionGroup')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(ResourceMapType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'ResourceMapObjectExtensionGroup')), min_occurs=0L, max_occurs=None)
    )
ResourceMapType._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(ResourceMapType._GroupModel_, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(ResourceMapType._GroupModel_2, min_occurs=1, max_occurs=1)
    )
ResourceMapType._ContentModel = pyxb.binding.content.ParticleModel(ResourceMapType._GroupModel, min_occurs=1, max_occurs=1)



SchemaDataType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'SchemaDataExtension'), pyxb.binding.datatypes.anyType, abstract=pyxb.binding.datatypes.boolean(1), scope=SchemaDataType))

SchemaDataType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'SimpleData'), SimpleDataType, scope=SchemaDataType))
SchemaDataType._GroupModel_ = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(SchemaDataType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'ObjectSimpleExtensionGroup')), min_occurs=0L, max_occurs=None)
    )
SchemaDataType._GroupModel_2 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(SchemaDataType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'SimpleData')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(SchemaDataType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'SchemaDataExtension')), min_occurs=0L, max_occurs=None)
    )
SchemaDataType._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(SchemaDataType._GroupModel_, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(SchemaDataType._GroupModel_2, min_occurs=1, max_occurs=1)
    )
SchemaDataType._ContentModel = pyxb.binding.content.ParticleModel(SchemaDataType._GroupModel, min_occurs=1, max_occurs=1)



MultiGeometryType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'MultiGeometryObjectExtensionGroup'), pyxb.binding.datatypes.anyType, abstract=pyxb.binding.datatypes.boolean(1), scope=MultiGeometryType))

MultiGeometryType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'MultiGeometrySimpleExtensionGroup'), pyxb.binding.datatypes.anySimpleType, abstract=pyxb.binding.datatypes.boolean(1), scope=MultiGeometryType))

MultiGeometryType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'AbstractGeometryGroup'), AbstractGeometryType, abstract=pyxb.binding.datatypes.boolean(1), scope=MultiGeometryType))
MultiGeometryType._GroupModel_2 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(MultiGeometryType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'ObjectSimpleExtensionGroup')), min_occurs=0L, max_occurs=None)
    )
MultiGeometryType._GroupModel_3 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(MultiGeometryType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'AbstractGeometrySimpleExtensionGroup')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(MultiGeometryType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'AbstractGeometryObjectExtensionGroup')), min_occurs=0L, max_occurs=None)
    )
MultiGeometryType._GroupModel_ = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(MultiGeometryType._GroupModel_2, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(MultiGeometryType._GroupModel_3, min_occurs=1, max_occurs=1)
    )
MultiGeometryType._GroupModel_4 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(MultiGeometryType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'AbstractGeometryGroup')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(MultiGeometryType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'MultiGeometrySimpleExtensionGroup')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(MultiGeometryType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'MultiGeometryObjectExtensionGroup')), min_occurs=0L, max_occurs=None)
    )
MultiGeometryType._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(MultiGeometryType._GroupModel_, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(MultiGeometryType._GroupModel_4, min_occurs=1, max_occurs=1)
    )
MultiGeometryType._ContentModel = pyxb.binding.content.ParticleModel(MultiGeometryType._GroupModel, min_occurs=1, max_occurs=1)



StyleType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'StyleObjectExtensionGroup'), pyxb.binding.datatypes.anyType, abstract=pyxb.binding.datatypes.boolean(1), scope=StyleType))

StyleType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'ListStyle'), ListStyleType, scope=StyleType))

StyleType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'IconStyle'), IconStyleType, scope=StyleType))

StyleType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'PolyStyle'), PolyStyleType, scope=StyleType))

StyleType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'StyleSimpleExtensionGroup'), pyxb.binding.datatypes.anySimpleType, abstract=pyxb.binding.datatypes.boolean(1), scope=StyleType))

StyleType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'LabelStyle'), LabelStyleType, scope=StyleType))

StyleType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'BalloonStyle'), BalloonStyleType, scope=StyleType))

StyleType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'LineStyle'), LineStyleType, scope=StyleType))
StyleType._GroupModel_2 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(StyleType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'ObjectSimpleExtensionGroup')), min_occurs=0L, max_occurs=None)
    )
StyleType._GroupModel_3 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(StyleType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'AbstractStyleSelectorSimpleExtensionGroup')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(StyleType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'AbstractStyleSelectorObjectExtensionGroup')), min_occurs=0L, max_occurs=None)
    )
StyleType._GroupModel_ = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(StyleType._GroupModel_2, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(StyleType._GroupModel_3, min_occurs=1, max_occurs=1)
    )
StyleType._GroupModel_4 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(StyleType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'IconStyle')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(StyleType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'LabelStyle')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(StyleType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'LineStyle')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(StyleType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'PolyStyle')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(StyleType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'BalloonStyle')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(StyleType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'ListStyle')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(StyleType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'StyleSimpleExtensionGroup')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(StyleType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'StyleObjectExtensionGroup')), min_occurs=0L, max_occurs=None)
    )
StyleType._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(StyleType._GroupModel_, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(StyleType._GroupModel_4, min_occurs=1, max_occurs=1)
    )
StyleType._ContentModel = pyxb.binding.content.ParticleModel(StyleType._GroupModel, min_occurs=1, max_occurs=1)



PlacemarkType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'PlacemarkObjectExtensionGroup'), pyxb.binding.datatypes.anyType, abstract=pyxb.binding.datatypes.boolean(1), scope=PlacemarkType))

PlacemarkType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'AbstractGeometryGroup'), AbstractGeometryType, abstract=pyxb.binding.datatypes.boolean(1), scope=PlacemarkType))

PlacemarkType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'PlacemarkSimpleExtensionGroup'), pyxb.binding.datatypes.anySimpleType, abstract=pyxb.binding.datatypes.boolean(1), scope=PlacemarkType))
PlacemarkType._GroupModel_2 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(PlacemarkType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'ObjectSimpleExtensionGroup')), min_occurs=0L, max_occurs=None)
    )
PlacemarkType._GroupModel_4 = pyxb.binding.content.GroupChoice(
    pyxb.binding.content.ParticleModel(PlacemarkType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Snippet')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(PlacemarkType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'snippet')), min_occurs=0L, max_occurs=1)
    )
PlacemarkType._GroupModel_5 = pyxb.binding.content.GroupChoice(
    pyxb.binding.content.ParticleModel(PlacemarkType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Metadata')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(PlacemarkType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'ExtendedData')), min_occurs=0L, max_occurs=1)
    )
PlacemarkType._GroupModel_3 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(PlacemarkType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'name')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(PlacemarkType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'visibility')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(PlacemarkType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'open')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(PlacemarkType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/2005/Atom'), u'author')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(PlacemarkType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/2005/Atom'), u'link')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(PlacemarkType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'address')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(PlacemarkType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'urn:oasis:names:tc:ciq:xsdschema:xAL:2.0'), u'AddressDetails')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(PlacemarkType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'phoneNumber')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(PlacemarkType._GroupModel_4, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(PlacemarkType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'description')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(PlacemarkType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'AbstractViewGroup')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(PlacemarkType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'AbstractTimePrimitiveGroup')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(PlacemarkType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'styleUrl')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(PlacemarkType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'AbstractStyleSelectorGroup')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(PlacemarkType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Region')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(PlacemarkType._GroupModel_5, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(PlacemarkType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'AbstractFeatureSimpleExtensionGroup')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(PlacemarkType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'AbstractFeatureObjectExtensionGroup')), min_occurs=0L, max_occurs=None)
    )
PlacemarkType._GroupModel_ = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(PlacemarkType._GroupModel_2, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(PlacemarkType._GroupModel_3, min_occurs=1, max_occurs=1)
    )
PlacemarkType._GroupModel_6 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(PlacemarkType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'AbstractGeometryGroup')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(PlacemarkType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'PlacemarkSimpleExtensionGroup')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(PlacemarkType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'PlacemarkObjectExtensionGroup')), min_occurs=0L, max_occurs=None)
    )
PlacemarkType._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(PlacemarkType._GroupModel_, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(PlacemarkType._GroupModel_6, min_occurs=1, max_occurs=1)
    )
PlacemarkType._ContentModel = pyxb.binding.content.ParticleModel(PlacemarkType._GroupModel, min_occurs=1, max_occurs=1)



DocumentType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Schema'), SchemaType, scope=DocumentType))

DocumentType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'AbstractFeatureGroup'), AbstractFeatureType, abstract=pyxb.binding.datatypes.boolean(1), scope=DocumentType))

DocumentType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'DocumentObjectExtensionGroup'), pyxb.binding.datatypes.anyType, abstract=pyxb.binding.datatypes.boolean(1), scope=DocumentType))

DocumentType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'DocumentSimpleExtensionGroup'), pyxb.binding.datatypes.anySimpleType, abstract=pyxb.binding.datatypes.boolean(1), scope=DocumentType))
DocumentType._GroupModel_3 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(DocumentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'ObjectSimpleExtensionGroup')), min_occurs=0L, max_occurs=None)
    )
DocumentType._GroupModel_5 = pyxb.binding.content.GroupChoice(
    pyxb.binding.content.ParticleModel(DocumentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Snippet')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(DocumentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'snippet')), min_occurs=0L, max_occurs=1)
    )
DocumentType._GroupModel_6 = pyxb.binding.content.GroupChoice(
    pyxb.binding.content.ParticleModel(DocumentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Metadata')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(DocumentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'ExtendedData')), min_occurs=0L, max_occurs=1)
    )
DocumentType._GroupModel_4 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(DocumentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'name')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(DocumentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'visibility')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(DocumentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'open')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(DocumentType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/2005/Atom'), u'author')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(DocumentType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/2005/Atom'), u'link')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(DocumentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'address')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(DocumentType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'urn:oasis:names:tc:ciq:xsdschema:xAL:2.0'), u'AddressDetails')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(DocumentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'phoneNumber')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(DocumentType._GroupModel_5, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(DocumentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'description')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(DocumentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'AbstractViewGroup')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(DocumentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'AbstractTimePrimitiveGroup')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(DocumentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'styleUrl')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(DocumentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'AbstractStyleSelectorGroup')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(DocumentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Region')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(DocumentType._GroupModel_6, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(DocumentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'AbstractFeatureSimpleExtensionGroup')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(DocumentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'AbstractFeatureObjectExtensionGroup')), min_occurs=0L, max_occurs=None)
    )
DocumentType._GroupModel_2 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(DocumentType._GroupModel_3, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(DocumentType._GroupModel_4, min_occurs=1, max_occurs=1)
    )
DocumentType._GroupModel_7 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(DocumentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'AbstractContainerSimpleExtensionGroup')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(DocumentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'AbstractContainerObjectExtensionGroup')), min_occurs=0L, max_occurs=None)
    )
DocumentType._GroupModel_ = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(DocumentType._GroupModel_2, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(DocumentType._GroupModel_7, min_occurs=1, max_occurs=1)
    )
DocumentType._GroupModel_8 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(DocumentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Schema')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(DocumentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'AbstractFeatureGroup')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(DocumentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'DocumentSimpleExtensionGroup')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(DocumentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'DocumentObjectExtensionGroup')), min_occurs=0L, max_occurs=None)
    )
DocumentType._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(DocumentType._GroupModel_, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(DocumentType._GroupModel_8, min_occurs=1, max_occurs=1)
    )
DocumentType._ContentModel = pyxb.binding.content.ParticleModel(DocumentType._GroupModel, min_occurs=1, max_occurs=1)



ItemIconType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'ItemIconObjectExtensionGroup'), pyxb.binding.datatypes.anyType, abstract=pyxb.binding.datatypes.boolean(1), scope=ItemIconType))

ItemIconType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'state'), itemIconStateType, scope=ItemIconType))

ItemIconType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'ItemIconSimpleExtensionGroup'), pyxb.binding.datatypes.anySimpleType, abstract=pyxb.binding.datatypes.boolean(1), scope=ItemIconType))

ItemIconType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'href'), pyxb.binding.datatypes.string, scope=ItemIconType, documentation=u'not anyURI due to $[x] substitution in\n      PhotoOverlay'))
ItemIconType._GroupModel_ = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(ItemIconType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'ObjectSimpleExtensionGroup')), min_occurs=0L, max_occurs=None)
    )
ItemIconType._GroupModel_2 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(ItemIconType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'state')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(ItemIconType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'href')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(ItemIconType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'ItemIconSimpleExtensionGroup')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(ItemIconType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'ItemIconObjectExtensionGroup')), min_occurs=0L, max_occurs=None)
    )
ItemIconType._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(ItemIconType._GroupModel_, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(ItemIconType._GroupModel_2, min_occurs=1, max_occurs=1)
    )
ItemIconType._ContentModel = pyxb.binding.content.ParticleModel(ItemIconType._GroupModel, min_occurs=1, max_occurs=1)



SimpleFieldType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'SimpleFieldExtension'), pyxb.binding.datatypes.anyType, abstract=pyxb.binding.datatypes.boolean(1), scope=SimpleFieldType))

SimpleFieldType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'displayName'), pyxb.binding.datatypes.string, scope=SimpleFieldType))
SimpleFieldType._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(SimpleFieldType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'displayName')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(SimpleFieldType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'SimpleFieldExtension')), min_occurs=0L, max_occurs=None)
    )
SimpleFieldType._ContentModel = pyxb.binding.content.ParticleModel(SimpleFieldType._GroupModel, min_occurs=1, max_occurs=1)



TimeSpanType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'end'), dateTimeType, scope=TimeSpanType))

TimeSpanType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'TimeSpanObjectExtensionGroup'), pyxb.binding.datatypes.anyType, abstract=pyxb.binding.datatypes.boolean(1), scope=TimeSpanType))

TimeSpanType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'TimeSpanSimpleExtensionGroup'), pyxb.binding.datatypes.anySimpleType, abstract=pyxb.binding.datatypes.boolean(1), scope=TimeSpanType))

TimeSpanType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'begin'), dateTimeType, scope=TimeSpanType))
TimeSpanType._GroupModel_2 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(TimeSpanType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'ObjectSimpleExtensionGroup')), min_occurs=0L, max_occurs=None)
    )
TimeSpanType._GroupModel_3 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(TimeSpanType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'AbstractTimePrimitiveSimpleExtensionGroup')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(TimeSpanType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'AbstractTimePrimitiveObjectExtensionGroup')), min_occurs=0L, max_occurs=None)
    )
TimeSpanType._GroupModel_ = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(TimeSpanType._GroupModel_2, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(TimeSpanType._GroupModel_3, min_occurs=1, max_occurs=1)
    )
TimeSpanType._GroupModel_4 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(TimeSpanType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'begin')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(TimeSpanType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'end')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(TimeSpanType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'TimeSpanSimpleExtensionGroup')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(TimeSpanType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'TimeSpanObjectExtensionGroup')), min_occurs=0L, max_occurs=None)
    )
TimeSpanType._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(TimeSpanType._GroupModel_, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(TimeSpanType._GroupModel_4, min_occurs=1, max_occurs=1)
    )
TimeSpanType._ContentModel = pyxb.binding.content.ParticleModel(TimeSpanType._GroupModel, min_occurs=1, max_occurs=1)



NetworkLinkType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Url'), LinkType, scope=NetworkLinkType, documentation=u'Url deprecated in 2.2'))

NetworkLinkType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Link'), LinkType, scope=NetworkLinkType))

NetworkLinkType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'NetworkLinkSimpleExtensionGroup'), pyxb.binding.datatypes.anySimpleType, abstract=pyxb.binding.datatypes.boolean(1), scope=NetworkLinkType))

NetworkLinkType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'NetworkLinkObjectExtensionGroup'), pyxb.binding.datatypes.anyType, abstract=pyxb.binding.datatypes.boolean(1), scope=NetworkLinkType))

NetworkLinkType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'refreshVisibility'), pyxb.binding.datatypes.boolean, scope=NetworkLinkType))

NetworkLinkType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'flyToView'), pyxb.binding.datatypes.boolean, scope=NetworkLinkType))
NetworkLinkType._GroupModel_2 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(NetworkLinkType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'ObjectSimpleExtensionGroup')), min_occurs=0L, max_occurs=None)
    )
NetworkLinkType._GroupModel_4 = pyxb.binding.content.GroupChoice(
    pyxb.binding.content.ParticleModel(NetworkLinkType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Snippet')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(NetworkLinkType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'snippet')), min_occurs=0L, max_occurs=1)
    )
NetworkLinkType._GroupModel_5 = pyxb.binding.content.GroupChoice(
    pyxb.binding.content.ParticleModel(NetworkLinkType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Metadata')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(NetworkLinkType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'ExtendedData')), min_occurs=0L, max_occurs=1)
    )
NetworkLinkType._GroupModel_3 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(NetworkLinkType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'name')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(NetworkLinkType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'visibility')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(NetworkLinkType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'open')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(NetworkLinkType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/2005/Atom'), u'author')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(NetworkLinkType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/2005/Atom'), u'link')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(NetworkLinkType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'address')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(NetworkLinkType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'urn:oasis:names:tc:ciq:xsdschema:xAL:2.0'), u'AddressDetails')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(NetworkLinkType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'phoneNumber')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(NetworkLinkType._GroupModel_4, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(NetworkLinkType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'description')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(NetworkLinkType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'AbstractViewGroup')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(NetworkLinkType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'AbstractTimePrimitiveGroup')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(NetworkLinkType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'styleUrl')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(NetworkLinkType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'AbstractStyleSelectorGroup')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(NetworkLinkType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Region')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(NetworkLinkType._GroupModel_5, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(NetworkLinkType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'AbstractFeatureSimpleExtensionGroup')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(NetworkLinkType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'AbstractFeatureObjectExtensionGroup')), min_occurs=0L, max_occurs=None)
    )
NetworkLinkType._GroupModel_ = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(NetworkLinkType._GroupModel_2, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(NetworkLinkType._GroupModel_3, min_occurs=1, max_occurs=1)
    )
NetworkLinkType._GroupModel_7 = pyxb.binding.content.GroupChoice(
    pyxb.binding.content.ParticleModel(NetworkLinkType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Url')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(NetworkLinkType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Link')), min_occurs=0L, max_occurs=1)
    )
NetworkLinkType._GroupModel_6 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(NetworkLinkType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'refreshVisibility')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(NetworkLinkType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'flyToView')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(NetworkLinkType._GroupModel_7, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(NetworkLinkType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'NetworkLinkSimpleExtensionGroup')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(NetworkLinkType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'NetworkLinkObjectExtensionGroup')), min_occurs=0L, max_occurs=None)
    )
NetworkLinkType._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(NetworkLinkType._GroupModel_, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(NetworkLinkType._GroupModel_6, min_occurs=1, max_occurs=1)
    )
NetworkLinkType._ContentModel = pyxb.binding.content.ParticleModel(NetworkLinkType._GroupModel, min_occurs=1, max_occurs=1)

AbstractGeometryGroup._setSubstitutionGroup(AbstractObjectGroup)

AbstractColorStyleObjectExtensionGroup._setSubstitutionGroup(AbstractObjectGroup)

IconStyle._setSubstitutionGroup(AbstractColorStyleGroup)

Data._setSubstitutionGroup(AbstractObjectGroup)

AbstractOverlayObjectExtensionGroup._setSubstitutionGroup(AbstractObjectGroup)

AbstractStyleSelectorGroup._setSubstitutionGroup(AbstractObjectGroup)

IconStyleObjectExtensionGroup._setSubstitutionGroup(AbstractObjectGroup)

AbstractTimePrimitiveGroup._setSubstitutionGroup(AbstractObjectGroup)

LabelStyle._setSubstitutionGroup(AbstractColorStyleGroup)

AbstractTimePrimitiveObjectExtensionGroup._setSubstitutionGroup(AbstractObjectGroup)

LineStyle._setSubstitutionGroup(AbstractColorStyleGroup)

LineStyleObjectExtensionGroup._setSubstitutionGroup(AbstractObjectGroup)

PolyStyle._setSubstitutionGroup(AbstractColorStyleGroup)

AbstractOverlayGroup._setSubstitutionGroup(AbstractFeatureGroup)

PolyStyleObjectExtensionGroup._setSubstitutionGroup(AbstractObjectGroup)

AbstractContainerGroup._setSubstitutionGroup(AbstractFeatureGroup)

Url._setSubstitutionGroup(AbstractObjectGroup)

LodObjectExtensionGroup._setSubstitutionGroup(AbstractObjectGroup)

AbstractGeometryObjectExtensionGroup._setSubstitutionGroup(AbstractObjectGroup)

Camera._setSubstitutionGroup(AbstractViewGroup)

ViewVolumeObjectExtensionGroup._setSubstitutionGroup(AbstractObjectGroup)

GroundOverlay._setSubstitutionGroup(AbstractOverlayGroup)

ImagePyramid._setSubstitutionGroup(AbstractObjectGroup)

MultiGeometryObjectExtensionGroup._setSubstitutionGroup(AbstractObjectGroup)

LatLonAltBoxObjectExtensionGroup._setSubstitutionGroup(AbstractObjectGroup)

CameraObjectExtensionGroup._setSubstitutionGroup(AbstractObjectGroup)

ImagePyramidObjectExtensionGroup._setSubstitutionGroup(AbstractObjectGroup)

NetworkLinkControlObjectExtensionGroup._setSubstitutionGroup(AbstractObjectGroup)

StyleObjectExtensionGroup._setSubstitutionGroup(AbstractObjectGroup)

StyleMap._setSubstitutionGroup(AbstractStyleSelectorGroup)

AbstractColorStyleGroup._setSubstitutionGroup(AbstractSubStyleGroup)

AbstractStyleSelectorObjectExtensionGroup._setSubstitutionGroup(AbstractObjectGroup)

Pair._setSubstitutionGroup(AbstractObjectGroup)

PairObjectExtensionGroup._setSubstitutionGroup(AbstractObjectGroup)

AbstractSubStyleGroup._setSubstitutionGroup(AbstractObjectGroup)

AbstractSubStyleObjectExtensionGroup._setSubstitutionGroup(AbstractObjectGroup)

AbstractContainerObjectExtensionGroup._setSubstitutionGroup(AbstractObjectGroup)

ResourceMapObjectExtensionGroup._setSubstitutionGroup(AbstractObjectGroup)

Point._setSubstitutionGroup(AbstractGeometryGroup)

GroundOverlayObjectExtensionGroup._setSubstitutionGroup(AbstractObjectGroup)

PointObjectExtensionGroup._setSubstitutionGroup(AbstractObjectGroup)

LineString._setSubstitutionGroup(AbstractGeometryGroup)

LinkObjectExtensionGroup._setSubstitutionGroup(AbstractObjectGroup)

AbstractLatLonBoxObjectExtensionGroup._setSubstitutionGroup(AbstractObjectGroup)

LatLonBox._setSubstitutionGroup(AbstractObjectGroup)

LineStringObjectExtensionGroup._setSubstitutionGroup(AbstractObjectGroup)

LatLonBoxObjectExtensionGroup._setSubstitutionGroup(AbstractObjectGroup)

Polygon._setSubstitutionGroup(AbstractGeometryGroup)

LabelStyleObjectExtensionGroup._setSubstitutionGroup(AbstractObjectGroup)

ScreenOverlayObjectExtensionGroup._setSubstitutionGroup(AbstractObjectGroup)

PhotoOverlay._setSubstitutionGroup(AbstractOverlayGroup)

PolygonObjectExtensionGroup._setSubstitutionGroup(AbstractObjectGroup)

TimeStamp._setSubstitutionGroup(AbstractTimePrimitiveGroup)

PhotoOverlayObjectExtensionGroup._setSubstitutionGroup(AbstractObjectGroup)

ViewVolume._setSubstitutionGroup(AbstractObjectGroup)

BoundaryObjectExtensionGroup._setSubstitutionGroup(AbstractObjectGroup)

Model._setSubstitutionGroup(AbstractGeometryGroup)

AbstractFeatureGroup._setSubstitutionGroup(AbstractObjectGroup)

LookAtObjectExtensionGroup._setSubstitutionGroup(AbstractObjectGroup)

LinearRing._setSubstitutionGroup(AbstractGeometryGroup)

AbstractFeatureObjectExtensionGroup._setSubstitutionGroup(AbstractObjectGroup)

AbstractViewGroup._setSubstitutionGroup(AbstractObjectGroup)

LookAt._setSubstitutionGroup(AbstractViewGroup)

ScreenOverlay._setSubstitutionGroup(AbstractOverlayGroup)

NetworkLinkObjectExtensionGroup._setSubstitutionGroup(AbstractObjectGroup)

Region._setSubstitutionGroup(AbstractObjectGroup)

altitudeMode._setSubstitutionGroup(altitudeModeGroup)

LatLonAltBox._setSubstitutionGroup(AbstractObjectGroup)

LocationObjectExtensionGroup._setSubstitutionGroup(AbstractObjectGroup)

Orientation._setSubstitutionGroup(AbstractObjectGroup)

Folder._setSubstitutionGroup(AbstractContainerGroup)

Lod._setSubstitutionGroup(AbstractObjectGroup)

LinearRingObjectExtensionGroup._setSubstitutionGroup(AbstractObjectGroup)

BalloonStyle._setSubstitutionGroup(AbstractSubStyleGroup)

Icon._setSubstitutionGroup(AbstractObjectGroup)

Link._setSubstitutionGroup(AbstractObjectGroup)

ScaleObjectExtensionGroup._setSubstitutionGroup(AbstractObjectGroup)

ResourceMap._setSubstitutionGroup(AbstractObjectGroup)

Alias._setSubstitutionGroup(AbstractObjectGroup)

MultiGeometry._setSubstitutionGroup(AbstractGeometryGroup)

Style._setSubstitutionGroup(AbstractStyleSelectorGroup)

AliasObjectExtensionGroup._setSubstitutionGroup(AbstractObjectGroup)

KmlObjectExtensionGroup._setSubstitutionGroup(AbstractObjectGroup)

AbstractViewObjectExtensionGroup._setSubstitutionGroup(AbstractObjectGroup)

FolderObjectExtensionGroup._setSubstitutionGroup(AbstractObjectGroup)

OrientationObjectExtensionGroup._setSubstitutionGroup(AbstractObjectGroup)

TimeSpanObjectExtensionGroup._setSubstitutionGroup(AbstractObjectGroup)

Placemark._setSubstitutionGroup(AbstractFeatureGroup)

Scale._setSubstitutionGroup(AbstractObjectGroup)

ModelObjectExtensionGroup._setSubstitutionGroup(AbstractObjectGroup)

Document._setSubstitutionGroup(AbstractContainerGroup)

SchemaData._setSubstitutionGroup(AbstractObjectGroup)

Location._setSubstitutionGroup(AbstractObjectGroup)

BalloonStyleObjectExtensionGroup._setSubstitutionGroup(AbstractObjectGroup)

ListStyle._setSubstitutionGroup(AbstractSubStyleGroup)

DocumentObjectExtensionGroup._setSubstitutionGroup(AbstractObjectGroup)

ListStyleObjectExtensionGroup._setSubstitutionGroup(AbstractObjectGroup)

ItemIcon._setSubstitutionGroup(AbstractObjectGroup)

RegionObjectExtensionGroup._setSubstitutionGroup(AbstractObjectGroup)

ItemIconObjectExtensionGroup._setSubstitutionGroup(AbstractObjectGroup)

TimeStampObjectExtensionGroup._setSubstitutionGroup(AbstractObjectGroup)

TimeSpan._setSubstitutionGroup(AbstractTimePrimitiveGroup)

BasicLinkObjectExtensionGroup._setSubstitutionGroup(AbstractObjectGroup)

PlacemarkObjectExtensionGroup._setSubstitutionGroup(AbstractObjectGroup)

NetworkLink._setSubstitutionGroup(AbstractFeatureGroup)

StyleMapObjectExtensionGroup._setSubstitutionGroup(AbstractObjectGroup)
