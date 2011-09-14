# ./pyxb/bundles/opengis/citygml/raw/landUse.py
# PyXB bindings for NM:1baea723ddfe80565eb6692188c5d83e2d6075ea
# Generated 2011-09-09 14:19:25.313396 by PyXB version 1.1.3
# Namespace http://www.opengis.net/citygml/landuse/1.0

import pyxb
import pyxb.binding
import pyxb.binding.saxer
import StringIO
import pyxb.utils.utility
import pyxb.utils.domutils
import sys

# Unique identifier for bindings created at the same time
_GenerationUID = pyxb.utils.utility.UniqueIdentifier('urn:uuid:a0abf66e-db18-11e0-b9ad-001fbc013adc')

# Import bindings for namespaces imported into schema
import pyxb.binding.datatypes
import pyxb.bundles.opengis.citygml.base
import pyxb.bundles.opengis.gml

Namespace = pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/landuse/1.0', create_if_missing=True)
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


# Atomic SimpleTypeDefinition
class LandUseUsageType (pyxb.binding.datatypes.string):

    """Usage of a Landuse. The values of this type are defined in the XML file LandUseUsageType.xml,
                according to the dictionary concept of GML3. """

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'LandUseUsageType')
    _Documentation = u'Usage of a Landuse. The values of this type are defined in the XML file LandUseUsageType.xml,\n                according to the dictionary concept of GML3. '
LandUseUsageType._InitializeFacetMap()
Namespace.addCategoryObject('typeBinding', u'LandUseUsageType', LandUseUsageType)

# Atomic SimpleTypeDefinition
class LandUseClassType (pyxb.binding.datatypes.string):

    """Class of a Landuse. The values of this type are defined in the XML file LandUseClassType.xml,
                according to the dictionary concept of GML3. """

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'LandUseClassType')
    _Documentation = u'Class of a Landuse. The values of this type are defined in the XML file LandUseClassType.xml,\n                according to the dictionary concept of GML3. '
LandUseClassType._InitializeFacetMap()
Namespace.addCategoryObject('typeBinding', u'LandUseClassType', LandUseClassType)

# Atomic SimpleTypeDefinition
class LandUseFunctionType (pyxb.binding.datatypes.string):

    """Function of a Landuse. The values of this type are defined in the XML file LandUseFunctionType.xml,
                according to the dictionary concept of GML3. """

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'LandUseFunctionType')
    _Documentation = u'Function of a Landuse. The values of this type are defined in the XML file LandUseFunctionType.xml,\n                according to the dictionary concept of GML3. '
LandUseFunctionType._InitializeFacetMap()
Namespace.addCategoryObject('typeBinding', u'LandUseFunctionType', LandUseFunctionType)

# Complex type LandUseType with content type ELEMENT_ONLY
class LandUseType (pyxb.bundles.opengis.citygml.base.AbstractCityObjectType):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'LandUseType')
    # Base type is pyxb.bundles.opengis.citygml.base.AbstractCityObjectType
    
    # Element externalReference ({http://www.opengis.net/citygml/1.0}externalReference) inherited from {http://www.opengis.net/citygml/1.0}AbstractCityObjectType
    
    # Element GenericApplicationPropertyOfCityObject ({http://www.opengis.net/citygml/1.0}_GenericApplicationPropertyOfCityObject) inherited from {http://www.opengis.net/citygml/1.0}AbstractCityObjectType
    
    # Element terminationDate ({http://www.opengis.net/citygml/1.0}terminationDate) inherited from {http://www.opengis.net/citygml/1.0}AbstractCityObjectType
    
    # Element {http://www.opengis.net/citygml/landuse/1.0}lod4MultiSurface uses Python identifier lod4MultiSurface
    __lod4MultiSurface = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiSurface'), 'lod4MultiSurface', '__httpwww_opengis_netcitygmllanduse1_0_LandUseType_httpwww_opengis_netcitygmllanduse1_0lod4MultiSurface', False)

    
    lod4MultiSurface = property(__lod4MultiSurface.value, __lod4MultiSurface.set, None, None)

    
    # Element metaDataProperty ({http://www.opengis.net/gml}metaDataProperty) inherited from {http://www.opengis.net/gml}AbstractGMLType
    
    # Element description ({http://www.opengis.net/gml}description) inherited from {http://www.opengis.net/gml}AbstractGMLType
    
    # Element boundedBy ({http://www.opengis.net/gml}boundedBy) inherited from {http://www.opengis.net/gml}AbstractFeatureType
    
    # Element {http://www.opengis.net/citygml/landuse/1.0}lod1MultiSurface uses Python identifier lod1MultiSurface
    __lod1MultiSurface = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'lod1MultiSurface'), 'lod1MultiSurface', '__httpwww_opengis_netcitygmllanduse1_0_LandUseType_httpwww_opengis_netcitygmllanduse1_0lod1MultiSurface', False)

    
    lod1MultiSurface = property(__lod1MultiSurface.value, __lod1MultiSurface.set, None, None)

    
    # Element generalizesTo ({http://www.opengis.net/citygml/1.0}generalizesTo) inherited from {http://www.opengis.net/citygml/1.0}AbstractCityObjectType
    
    # Element {http://www.opengis.net/citygml/landuse/1.0}lod3MultiSurface uses Python identifier lod3MultiSurface
    __lod3MultiSurface = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiSurface'), 'lod3MultiSurface', '__httpwww_opengis_netcitygmllanduse1_0_LandUseType_httpwww_opengis_netcitygmllanduse1_0lod3MultiSurface', False)

    
    lod3MultiSurface = property(__lod3MultiSurface.value, __lod3MultiSurface.set, None, None)

    
    # Element creationDate ({http://www.opengis.net/citygml/1.0}creationDate) inherited from {http://www.opengis.net/citygml/1.0}AbstractCityObjectType
    
    # Element {http://www.opengis.net/citygml/landuse/1.0}lod2MultiSurface uses Python identifier lod2MultiSurface
    __lod2MultiSurface = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'lod2MultiSurface'), 'lod2MultiSurface', '__httpwww_opengis_netcitygmllanduse1_0_LandUseType_httpwww_opengis_netcitygmllanduse1_0lod2MultiSurface', False)

    
    lod2MultiSurface = property(__lod2MultiSurface.value, __lod2MultiSurface.set, None, None)

    
    # Element {http://www.opengis.net/citygml/landuse/1.0}function uses Python identifier function
    __function = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'function'), 'function', '__httpwww_opengis_netcitygmllanduse1_0_LandUseType_httpwww_opengis_netcitygmllanduse1_0function', True)

    
    function = property(__function.value, __function.set, None, None)

    
    # Element {http://www.opengis.net/citygml/landuse/1.0}class uses Python identifier class_
    __class = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'class'), 'class_', '__httpwww_opengis_netcitygmllanduse1_0_LandUseType_httpwww_opengis_netcitygmllanduse1_0class', False)

    
    class_ = property(__class.value, __class.set, None, None)

    
    # Element location ({http://www.opengis.net/gml}location) inherited from {http://www.opengis.net/gml}AbstractFeatureType
    
    # Element {http://www.opengis.net/citygml/landuse/1.0}_GenericApplicationPropertyOfLandUse uses Python identifier GenericApplicationPropertyOfLandUse
    __GenericApplicationPropertyOfLandUse = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfLandUse'), 'GenericApplicationPropertyOfLandUse', '__httpwww_opengis_netcitygmllanduse1_0_LandUseType_httpwww_opengis_netcitygmllanduse1_0_GenericApplicationPropertyOfLandUse', True)

    
    GenericApplicationPropertyOfLandUse = property(__GenericApplicationPropertyOfLandUse.value, __GenericApplicationPropertyOfLandUse.set, None, None)

    
    # Element name ({http://www.opengis.net/gml}name) inherited from {http://www.opengis.net/gml}AbstractGMLType
    
    # Element {http://www.opengis.net/citygml/landuse/1.0}usage uses Python identifier usage
    __usage = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'usage'), 'usage', '__httpwww_opengis_netcitygmllanduse1_0_LandUseType_httpwww_opengis_netcitygmllanduse1_0usage', True)

    
    usage = property(__usage.value, __usage.set, None, None)

    
    # Element {http://www.opengis.net/citygml/landuse/1.0}lod0MultiSurface uses Python identifier lod0MultiSurface
    __lod0MultiSurface = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'lod0MultiSurface'), 'lod0MultiSurface', '__httpwww_opengis_netcitygmllanduse1_0_LandUseType_httpwww_opengis_netcitygmllanduse1_0lod0MultiSurface', False)

    
    lod0MultiSurface = property(__lod0MultiSurface.value, __lod0MultiSurface.set, None, None)

    
    # Attribute id inherited from {http://www.opengis.net/gml}AbstractGMLType

    _ElementMap = pyxb.bundles.opengis.citygml.base.AbstractCityObjectType._ElementMap.copy()
    _ElementMap.update({
        __lod4MultiSurface.name() : __lod4MultiSurface,
        __lod1MultiSurface.name() : __lod1MultiSurface,
        __lod3MultiSurface.name() : __lod3MultiSurface,
        __lod2MultiSurface.name() : __lod2MultiSurface,
        __function.name() : __function,
        __class.name() : __class,
        __GenericApplicationPropertyOfLandUse.name() : __GenericApplicationPropertyOfLandUse,
        __usage.name() : __usage,
        __lod0MultiSurface.name() : __lod0MultiSurface
    })
    _AttributeMap = pyxb.bundles.opengis.citygml.base.AbstractCityObjectType._AttributeMap.copy()
    _AttributeMap.update({
        
    })
Namespace.addCategoryObject('typeBinding', u'LandUseType', LandUseType)


LandUse = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'LandUse'), LandUseType)
Namespace.addCategoryObject('elementBinding', LandUse.name().localName(), LandUse)

GenericApplicationPropertyOfLandUse = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfLandUse'), pyxb.binding.datatypes.anyType, abstract=pyxb.binding.datatypes.boolean(1))
Namespace.addCategoryObject('elementBinding', GenericApplicationPropertyOfLandUse.name().localName(), GenericApplicationPropertyOfLandUse)



LandUseType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiSurface'), pyxb.bundles.opengis.gml.MultiSurfacePropertyType, scope=LandUseType))

LandUseType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'lod1MultiSurface'), pyxb.bundles.opengis.gml.MultiSurfacePropertyType, scope=LandUseType))

LandUseType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiSurface'), pyxb.bundles.opengis.gml.MultiSurfacePropertyType, scope=LandUseType))

LandUseType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'lod2MultiSurface'), pyxb.bundles.opengis.gml.MultiSurfacePropertyType, scope=LandUseType))

LandUseType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'function'), LandUseFunctionType, scope=LandUseType))

LandUseType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'class'), LandUseClassType, scope=LandUseType))

LandUseType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfLandUse'), pyxb.binding.datatypes.anyType, abstract=pyxb.binding.datatypes.boolean(1), scope=LandUseType))

LandUseType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'usage'), LandUseUsageType, scope=LandUseType))

LandUseType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'lod0MultiSurface'), pyxb.bundles.opengis.gml.MultiSurfacePropertyType, scope=LandUseType))
LandUseType._GroupModel_14 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(LandUseType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'metaDataProperty')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(LandUseType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'description')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(LandUseType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'name')), min_occurs=0L, max_occurs=None)
    )
LandUseType._GroupModel_13 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(LandUseType._GroupModel_14, min_occurs=1, max_occurs=1)
    )
LandUseType._GroupModel_15 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(LandUseType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'boundedBy')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(LandUseType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'location')), min_occurs=0L, max_occurs=1)
    )
LandUseType._GroupModel_12 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(LandUseType._GroupModel_13, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(LandUseType._GroupModel_15, min_occurs=1, max_occurs=1)
    )
LandUseType._GroupModel_16 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(LandUseType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'creationDate')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(LandUseType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'terminationDate')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(LandUseType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'externalReference')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(LandUseType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'generalizesTo')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(LandUseType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'_GenericApplicationPropertyOfCityObject')), min_occurs=0L, max_occurs=None)
    )
LandUseType._GroupModel_11 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(LandUseType._GroupModel_12, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(LandUseType._GroupModel_16, min_occurs=1, max_occurs=1)
    )
LandUseType._GroupModel_17 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(LandUseType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'class')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(LandUseType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'function')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(LandUseType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'usage')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(LandUseType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod0MultiSurface')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(LandUseType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod1MultiSurface')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(LandUseType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2MultiSurface')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(LandUseType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiSurface')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(LandUseType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiSurface')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(LandUseType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfLandUse')), min_occurs=0L, max_occurs=None)
    )
LandUseType._GroupModel_10 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(LandUseType._GroupModel_11, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(LandUseType._GroupModel_17, min_occurs=1, max_occurs=1)
    )
LandUseType._ContentModel = pyxb.binding.content.ParticleModel(LandUseType._GroupModel_10, min_occurs=1, max_occurs=1)

LandUse._setSubstitutionGroup(pyxb.bundles.opengis.citygml.base.CityObject)
