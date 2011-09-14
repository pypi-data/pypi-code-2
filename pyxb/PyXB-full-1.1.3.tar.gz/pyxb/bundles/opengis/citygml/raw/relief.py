# ./pyxb/bundles/opengis/citygml/raw/relief.py
# PyXB bindings for NM:774feb5808f6b9c56c8f74b268bba511fd91e0ab
# Generated 2011-09-09 14:19:26.717222 by PyXB version 1.1.3
# Namespace http://www.opengis.net/citygml/relief/1.0

import pyxb
import pyxb.binding
import pyxb.binding.saxer
import StringIO
import pyxb.utils.utility
import pyxb.utils.domutils
import sys

# Unique identifier for bindings created at the same time
_GenerationUID = pyxb.utils.utility.UniqueIdentifier('urn:uuid:a185ba5c-db18-11e0-87b1-001fbc013adc')

# Import bindings for namespaces imported into schema
import pyxb.bundles.opengis.gml
import pyxb.bundles.opengis.citygml.base
import pyxb.binding.datatypes

Namespace = pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/relief/1.0', create_if_missing=True)
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


# Complex type tinPropertyType with content type ELEMENT_ONLY
class tinPropertyType (pyxb.bundles.opengis.gml.AssociationType):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'tinPropertyType')
    # Base type is pyxb.bundles.opengis.gml.AssociationType
    
    # Element {http://www.opengis.net/gml}TriangulatedSurface uses Python identifier TriangulatedSurface
    __TriangulatedSurface = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'TriangulatedSurface'), 'TriangulatedSurface', '__httpwww_opengis_netcitygmlrelief1_0_tinPropertyType_httpwww_opengis_netgmlTriangulatedSurface', False)

    
    TriangulatedSurface = property(__TriangulatedSurface.value, __TriangulatedSurface.set, None, None)

    
    # Attribute show inherited from {http://www.opengis.net/gml}AssociationType
    
    # Attribute remoteSchema inherited from {http://www.opengis.net/gml}AssociationType
    
    # Attribute title inherited from {http://www.opengis.net/gml}AssociationType
    
    # Attribute arcrole inherited from {http://www.opengis.net/gml}AssociationType
    
    # Attribute href inherited from {http://www.opengis.net/gml}AssociationType
    
    # Attribute role inherited from {http://www.opengis.net/gml}AssociationType
    
    # Attribute actuate inherited from {http://www.opengis.net/gml}AssociationType
    
    # Attribute type inherited from {http://www.opengis.net/gml}AssociationType

    _ElementMap = pyxb.bundles.opengis.gml.AssociationType._ElementMap.copy()
    _ElementMap.update({
        __TriangulatedSurface.name() : __TriangulatedSurface
    })
    _AttributeMap = pyxb.bundles.opengis.gml.AssociationType._AttributeMap.copy()
    _AttributeMap.update({
        
    })
Namespace.addCategoryObject('typeBinding', u'tinPropertyType', tinPropertyType)


# Complex type AbstractReliefComponentType with content type ELEMENT_ONLY
class AbstractReliefComponentType (pyxb.bundles.opengis.citygml.base.AbstractCityObjectType):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = True
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'AbstractReliefComponentType')
    # Base type is pyxb.bundles.opengis.citygml.base.AbstractCityObjectType
    
    # Element name ({http://www.opengis.net/gml}name) inherited from {http://www.opengis.net/gml}AbstractGMLType
    
    # Element {http://www.opengis.net/citygml/relief/1.0}lod uses Python identifier lod
    __lod = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'lod'), 'lod', '__httpwww_opengis_netcitygmlrelief1_0_AbstractReliefComponentType_httpwww_opengis_netcitygmlrelief1_0lod', False)

    
    lod = property(__lod.value, __lod.set, None, None)

    
    # Element GenericApplicationPropertyOfCityObject ({http://www.opengis.net/citygml/1.0}_GenericApplicationPropertyOfCityObject) inherited from {http://www.opengis.net/citygml/1.0}AbstractCityObjectType
    
    # Element generalizesTo ({http://www.opengis.net/citygml/1.0}generalizesTo) inherited from {http://www.opengis.net/citygml/1.0}AbstractCityObjectType
    
    # Element terminationDate ({http://www.opengis.net/citygml/1.0}terminationDate) inherited from {http://www.opengis.net/citygml/1.0}AbstractCityObjectType
    
    # Element {http://www.opengis.net/citygml/relief/1.0}_GenericApplicationPropertyOfReliefComponent uses Python identifier GenericApplicationPropertyOfReliefComponent
    __GenericApplicationPropertyOfReliefComponent = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfReliefComponent'), 'GenericApplicationPropertyOfReliefComponent', '__httpwww_opengis_netcitygmlrelief1_0_AbstractReliefComponentType_httpwww_opengis_netcitygmlrelief1_0_GenericApplicationPropertyOfReliefComponent', True)

    
    GenericApplicationPropertyOfReliefComponent = property(__GenericApplicationPropertyOfReliefComponent.value, __GenericApplicationPropertyOfReliefComponent.set, None, None)

    
    # Element externalReference ({http://www.opengis.net/citygml/1.0}externalReference) inherited from {http://www.opengis.net/citygml/1.0}AbstractCityObjectType
    
    # Element creationDate ({http://www.opengis.net/citygml/1.0}creationDate) inherited from {http://www.opengis.net/citygml/1.0}AbstractCityObjectType
    
    # Element {http://www.opengis.net/citygml/relief/1.0}extent uses Python identifier extent
    __extent = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'extent'), 'extent', '__httpwww_opengis_netcitygmlrelief1_0_AbstractReliefComponentType_httpwww_opengis_netcitygmlrelief1_0extent', False)

    
    extent = property(__extent.value, __extent.set, None, None)

    
    # Element boundedBy ({http://www.opengis.net/gml}boundedBy) inherited from {http://www.opengis.net/gml}AbstractFeatureType
    
    # Element metaDataProperty ({http://www.opengis.net/gml}metaDataProperty) inherited from {http://www.opengis.net/gml}AbstractGMLType
    
    # Element description ({http://www.opengis.net/gml}description) inherited from {http://www.opengis.net/gml}AbstractGMLType
    
    # Element location ({http://www.opengis.net/gml}location) inherited from {http://www.opengis.net/gml}AbstractFeatureType
    
    # Attribute id inherited from {http://www.opengis.net/gml}AbstractGMLType

    _ElementMap = pyxb.bundles.opengis.citygml.base.AbstractCityObjectType._ElementMap.copy()
    _ElementMap.update({
        __lod.name() : __lod,
        __GenericApplicationPropertyOfReliefComponent.name() : __GenericApplicationPropertyOfReliefComponent,
        __extent.name() : __extent
    })
    _AttributeMap = pyxb.bundles.opengis.citygml.base.AbstractCityObjectType._AttributeMap.copy()
    _AttributeMap.update({
        
    })
Namespace.addCategoryObject('typeBinding', u'AbstractReliefComponentType', AbstractReliefComponentType)


# Complex type TINReliefType with content type ELEMENT_ONLY
class TINReliefType (AbstractReliefComponentType):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'TINReliefType')
    # Base type is AbstractReliefComponentType
    
    # Element name ({http://www.opengis.net/gml}name) inherited from {http://www.opengis.net/gml}AbstractGMLType
    
    # Element lod ({http://www.opengis.net/citygml/relief/1.0}lod) inherited from {http://www.opengis.net/citygml/relief/1.0}AbstractReliefComponentType
    
    # Element extent ({http://www.opengis.net/citygml/relief/1.0}extent) inherited from {http://www.opengis.net/citygml/relief/1.0}AbstractReliefComponentType
    
    # Element GenericApplicationPropertyOfCityObject ({http://www.opengis.net/citygml/1.0}_GenericApplicationPropertyOfCityObject) inherited from {http://www.opengis.net/citygml/1.0}AbstractCityObjectType
    
    # Element generalizesTo ({http://www.opengis.net/citygml/1.0}generalizesTo) inherited from {http://www.opengis.net/citygml/1.0}AbstractCityObjectType
    
    # Element terminationDate ({http://www.opengis.net/citygml/1.0}terminationDate) inherited from {http://www.opengis.net/citygml/1.0}AbstractCityObjectType
    
    # Element GenericApplicationPropertyOfReliefComponent ({http://www.opengis.net/citygml/relief/1.0}_GenericApplicationPropertyOfReliefComponent) inherited from {http://www.opengis.net/citygml/relief/1.0}AbstractReliefComponentType
    
    # Element externalReference ({http://www.opengis.net/citygml/1.0}externalReference) inherited from {http://www.opengis.net/citygml/1.0}AbstractCityObjectType
    
    # Element creationDate ({http://www.opengis.net/citygml/1.0}creationDate) inherited from {http://www.opengis.net/citygml/1.0}AbstractCityObjectType
    
    # Element {http://www.opengis.net/citygml/relief/1.0}_GenericApplicationPropertyOfTinRelief uses Python identifier GenericApplicationPropertyOfTinRelief
    __GenericApplicationPropertyOfTinRelief = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfTinRelief'), 'GenericApplicationPropertyOfTinRelief', '__httpwww_opengis_netcitygmlrelief1_0_TINReliefType_httpwww_opengis_netcitygmlrelief1_0_GenericApplicationPropertyOfTinRelief', True)

    
    GenericApplicationPropertyOfTinRelief = property(__GenericApplicationPropertyOfTinRelief.value, __GenericApplicationPropertyOfTinRelief.set, None, None)

    
    # Element location ({http://www.opengis.net/gml}location) inherited from {http://www.opengis.net/gml}AbstractFeatureType
    
    # Element boundedBy ({http://www.opengis.net/gml}boundedBy) inherited from {http://www.opengis.net/gml}AbstractFeatureType
    
    # Element metaDataProperty ({http://www.opengis.net/gml}metaDataProperty) inherited from {http://www.opengis.net/gml}AbstractGMLType
    
    # Element description ({http://www.opengis.net/gml}description) inherited from {http://www.opengis.net/gml}AbstractGMLType
    
    # Element {http://www.opengis.net/citygml/relief/1.0}tin uses Python identifier tin
    __tin = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'tin'), 'tin', '__httpwww_opengis_netcitygmlrelief1_0_TINReliefType_httpwww_opengis_netcitygmlrelief1_0tin', False)

    
    tin = property(__tin.value, __tin.set, None, None)

    
    # Attribute id inherited from {http://www.opengis.net/gml}AbstractGMLType

    _ElementMap = AbstractReliefComponentType._ElementMap.copy()
    _ElementMap.update({
        __GenericApplicationPropertyOfTinRelief.name() : __GenericApplicationPropertyOfTinRelief,
        __tin.name() : __tin
    })
    _AttributeMap = AbstractReliefComponentType._AttributeMap.copy()
    _AttributeMap.update({
        
    })
Namespace.addCategoryObject('typeBinding', u'TINReliefType', TINReliefType)


# Complex type ReliefFeatureType with content type ELEMENT_ONLY
class ReliefFeatureType (pyxb.bundles.opengis.citygml.base.AbstractCityObjectType):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'ReliefFeatureType')
    # Base type is pyxb.bundles.opengis.citygml.base.AbstractCityObjectType
    
    # Element generalizesTo ({http://www.opengis.net/citygml/1.0}generalizesTo) inherited from {http://www.opengis.net/citygml/1.0}AbstractCityObjectType
    
    # Element GenericApplicationPropertyOfCityObject ({http://www.opengis.net/citygml/1.0}_GenericApplicationPropertyOfCityObject) inherited from {http://www.opengis.net/citygml/1.0}AbstractCityObjectType
    
    # Element terminationDate ({http://www.opengis.net/citygml/1.0}terminationDate) inherited from {http://www.opengis.net/citygml/1.0}AbstractCityObjectType
    
    # Element {http://www.opengis.net/citygml/relief/1.0}lod uses Python identifier lod
    __lod = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'lod'), 'lod', '__httpwww_opengis_netcitygmlrelief1_0_ReliefFeatureType_httpwww_opengis_netcitygmlrelief1_0lod', False)

    
    lod = property(__lod.value, __lod.set, None, None)

    
    # Element name ({http://www.opengis.net/gml}name) inherited from {http://www.opengis.net/gml}AbstractGMLType
    
    # Element externalReference ({http://www.opengis.net/citygml/1.0}externalReference) inherited from {http://www.opengis.net/citygml/1.0}AbstractCityObjectType
    
    # Element creationDate ({http://www.opengis.net/citygml/1.0}creationDate) inherited from {http://www.opengis.net/citygml/1.0}AbstractCityObjectType
    
    # Element boundedBy ({http://www.opengis.net/gml}boundedBy) inherited from {http://www.opengis.net/gml}AbstractFeatureType
    
    # Element {http://www.opengis.net/citygml/relief/1.0}reliefComponent uses Python identifier reliefComponent
    __reliefComponent = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'reliefComponent'), 'reliefComponent', '__httpwww_opengis_netcitygmlrelief1_0_ReliefFeatureType_httpwww_opengis_netcitygmlrelief1_0reliefComponent', True)

    
    reliefComponent = property(__reliefComponent.value, __reliefComponent.set, None, None)

    
    # Element {http://www.opengis.net/citygml/relief/1.0}_GenericApplicationPropertyOfReliefFeature uses Python identifier GenericApplicationPropertyOfReliefFeature
    __GenericApplicationPropertyOfReliefFeature = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfReliefFeature'), 'GenericApplicationPropertyOfReliefFeature', '__httpwww_opengis_netcitygmlrelief1_0_ReliefFeatureType_httpwww_opengis_netcitygmlrelief1_0_GenericApplicationPropertyOfReliefFeature', True)

    
    GenericApplicationPropertyOfReliefFeature = property(__GenericApplicationPropertyOfReliefFeature.value, __GenericApplicationPropertyOfReliefFeature.set, None, None)

    
    # Element metaDataProperty ({http://www.opengis.net/gml}metaDataProperty) inherited from {http://www.opengis.net/gml}AbstractGMLType
    
    # Element description ({http://www.opengis.net/gml}description) inherited from {http://www.opengis.net/gml}AbstractGMLType
    
    # Element location ({http://www.opengis.net/gml}location) inherited from {http://www.opengis.net/gml}AbstractFeatureType
    
    # Attribute id inherited from {http://www.opengis.net/gml}AbstractGMLType

    _ElementMap = pyxb.bundles.opengis.citygml.base.AbstractCityObjectType._ElementMap.copy()
    _ElementMap.update({
        __lod.name() : __lod,
        __reliefComponent.name() : __reliefComponent,
        __GenericApplicationPropertyOfReliefFeature.name() : __GenericApplicationPropertyOfReliefFeature
    })
    _AttributeMap = pyxb.bundles.opengis.citygml.base.AbstractCityObjectType._AttributeMap.copy()
    _AttributeMap.update({
        
    })
Namespace.addCategoryObject('typeBinding', u'ReliefFeatureType', ReliefFeatureType)


# Complex type ReliefComponentPropertyType with content type ELEMENT_ONLY
class ReliefComponentPropertyType (pyxb.bundles.opengis.gml.AssociationType):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'ReliefComponentPropertyType')
    # Base type is pyxb.bundles.opengis.gml.AssociationType
    
    # Element {http://www.opengis.net/citygml/relief/1.0}_ReliefComponent uses Python identifier ReliefComponent
    __ReliefComponent = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'_ReliefComponent'), 'ReliefComponent', '__httpwww_opengis_netcitygmlrelief1_0_ReliefComponentPropertyType_httpwww_opengis_netcitygmlrelief1_0_ReliefComponent', False)

    
    ReliefComponent = property(__ReliefComponent.value, __ReliefComponent.set, None, None)

    
    # Attribute show inherited from {http://www.opengis.net/gml}AssociationType
    
    # Attribute remoteSchema inherited from {http://www.opengis.net/gml}AssociationType
    
    # Attribute title inherited from {http://www.opengis.net/gml}AssociationType
    
    # Attribute arcrole inherited from {http://www.opengis.net/gml}AssociationType
    
    # Attribute href inherited from {http://www.opengis.net/gml}AssociationType
    
    # Attribute role inherited from {http://www.opengis.net/gml}AssociationType
    
    # Attribute actuate inherited from {http://www.opengis.net/gml}AssociationType
    
    # Attribute type inherited from {http://www.opengis.net/gml}AssociationType

    _ElementMap = pyxb.bundles.opengis.gml.AssociationType._ElementMap.copy()
    _ElementMap.update({
        __ReliefComponent.name() : __ReliefComponent
    })
    _AttributeMap = pyxb.bundles.opengis.gml.AssociationType._AttributeMap.copy()
    _AttributeMap.update({
        
    })
Namespace.addCategoryObject('typeBinding', u'ReliefComponentPropertyType', ReliefComponentPropertyType)


# Complex type gridPropertyType with content type ELEMENT_ONLY
class gridPropertyType (pyxb.bundles.opengis.gml.AssociationType):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'gridPropertyType')
    # Base type is pyxb.bundles.opengis.gml.AssociationType
    
    # Element {http://www.opengis.net/gml}RectifiedGridCoverage uses Python identifier RectifiedGridCoverage
    __RectifiedGridCoverage = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'RectifiedGridCoverage'), 'RectifiedGridCoverage', '__httpwww_opengis_netcitygmlrelief1_0_gridPropertyType_httpwww_opengis_netgmlRectifiedGridCoverage', False)

    
    RectifiedGridCoverage = property(__RectifiedGridCoverage.value, __RectifiedGridCoverage.set, None, None)

    
    # Attribute show inherited from {http://www.opengis.net/gml}AssociationType
    
    # Attribute remoteSchema inherited from {http://www.opengis.net/gml}AssociationType
    
    # Attribute title inherited from {http://www.opengis.net/gml}AssociationType
    
    # Attribute arcrole inherited from {http://www.opengis.net/gml}AssociationType
    
    # Attribute href inherited from {http://www.opengis.net/gml}AssociationType
    
    # Attribute role inherited from {http://www.opengis.net/gml}AssociationType
    
    # Attribute actuate inherited from {http://www.opengis.net/gml}AssociationType
    
    # Attribute type inherited from {http://www.opengis.net/gml}AssociationType

    _ElementMap = pyxb.bundles.opengis.gml.AssociationType._ElementMap.copy()
    _ElementMap.update({
        __RectifiedGridCoverage.name() : __RectifiedGridCoverage
    })
    _AttributeMap = pyxb.bundles.opengis.gml.AssociationType._AttributeMap.copy()
    _AttributeMap.update({
        
    })
Namespace.addCategoryObject('typeBinding', u'gridPropertyType', gridPropertyType)


# Complex type RasterReliefType with content type ELEMENT_ONLY
class RasterReliefType (AbstractReliefComponentType):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'RasterReliefType')
    # Base type is AbstractReliefComponentType
    
    # Element name ({http://www.opengis.net/gml}name) inherited from {http://www.opengis.net/gml}AbstractGMLType
    
    # Element {http://www.opengis.net/citygml/relief/1.0}_GenericApplicationPropertyOfRasterRelief uses Python identifier GenericApplicationPropertyOfRasterRelief
    __GenericApplicationPropertyOfRasterRelief = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfRasterRelief'), 'GenericApplicationPropertyOfRasterRelief', '__httpwww_opengis_netcitygmlrelief1_0_RasterReliefType_httpwww_opengis_netcitygmlrelief1_0_GenericApplicationPropertyOfRasterRelief', True)

    
    GenericApplicationPropertyOfRasterRelief = property(__GenericApplicationPropertyOfRasterRelief.value, __GenericApplicationPropertyOfRasterRelief.set, None, None)

    
    # Element extent ({http://www.opengis.net/citygml/relief/1.0}extent) inherited from {http://www.opengis.net/citygml/relief/1.0}AbstractReliefComponentType
    
    # Element GenericApplicationPropertyOfCityObject ({http://www.opengis.net/citygml/1.0}_GenericApplicationPropertyOfCityObject) inherited from {http://www.opengis.net/citygml/1.0}AbstractCityObjectType
    
    # Element lod ({http://www.opengis.net/citygml/relief/1.0}lod) inherited from {http://www.opengis.net/citygml/relief/1.0}AbstractReliefComponentType
    
    # Element {http://www.opengis.net/citygml/relief/1.0}grid uses Python identifier grid
    __grid = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'grid'), 'grid', '__httpwww_opengis_netcitygmlrelief1_0_RasterReliefType_httpwww_opengis_netcitygmlrelief1_0grid', False)

    
    grid = property(__grid.value, __grid.set, None, None)

    
    # Element GenericApplicationPropertyOfReliefComponent ({http://www.opengis.net/citygml/relief/1.0}_GenericApplicationPropertyOfReliefComponent) inherited from {http://www.opengis.net/citygml/relief/1.0}AbstractReliefComponentType
    
    # Element externalReference ({http://www.opengis.net/citygml/1.0}externalReference) inherited from {http://www.opengis.net/citygml/1.0}AbstractCityObjectType
    
    # Element creationDate ({http://www.opengis.net/citygml/1.0}creationDate) inherited from {http://www.opengis.net/citygml/1.0}AbstractCityObjectType
    
    # Element terminationDate ({http://www.opengis.net/citygml/1.0}terminationDate) inherited from {http://www.opengis.net/citygml/1.0}AbstractCityObjectType
    
    # Element boundedBy ({http://www.opengis.net/gml}boundedBy) inherited from {http://www.opengis.net/gml}AbstractFeatureType
    
    # Element generalizesTo ({http://www.opengis.net/citygml/1.0}generalizesTo) inherited from {http://www.opengis.net/citygml/1.0}AbstractCityObjectType
    
    # Element metaDataProperty ({http://www.opengis.net/gml}metaDataProperty) inherited from {http://www.opengis.net/gml}AbstractGMLType
    
    # Element description ({http://www.opengis.net/gml}description) inherited from {http://www.opengis.net/gml}AbstractGMLType
    
    # Element location ({http://www.opengis.net/gml}location) inherited from {http://www.opengis.net/gml}AbstractFeatureType
    
    # Attribute id inherited from {http://www.opengis.net/gml}AbstractGMLType

    _ElementMap = AbstractReliefComponentType._ElementMap.copy()
    _ElementMap.update({
        __GenericApplicationPropertyOfRasterRelief.name() : __GenericApplicationPropertyOfRasterRelief,
        __grid.name() : __grid
    })
    _AttributeMap = AbstractReliefComponentType._AttributeMap.copy()
    _AttributeMap.update({
        
    })
Namespace.addCategoryObject('typeBinding', u'RasterReliefType', RasterReliefType)


# Complex type BreaklineReliefType with content type ELEMENT_ONLY
class BreaklineReliefType (AbstractReliefComponentType):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'BreaklineReliefType')
    # Base type is AbstractReliefComponentType
    
    # Element name ({http://www.opengis.net/gml}name) inherited from {http://www.opengis.net/gml}AbstractGMLType
    
    # Element generalizesTo ({http://www.opengis.net/citygml/1.0}generalizesTo) inherited from {http://www.opengis.net/citygml/1.0}AbstractCityObjectType
    
    # Element terminationDate ({http://www.opengis.net/citygml/1.0}terminationDate) inherited from {http://www.opengis.net/citygml/1.0}AbstractCityObjectType
    
    # Element boundedBy ({http://www.opengis.net/gml}boundedBy) inherited from {http://www.opengis.net/gml}AbstractFeatureType
    
    # Element GenericApplicationPropertyOfCityObject ({http://www.opengis.net/citygml/1.0}_GenericApplicationPropertyOfCityObject) inherited from {http://www.opengis.net/citygml/1.0}AbstractCityObjectType
    
    # Element lod ({http://www.opengis.net/citygml/relief/1.0}lod) inherited from {http://www.opengis.net/citygml/relief/1.0}AbstractReliefComponentType
    
    # Element extent ({http://www.opengis.net/citygml/relief/1.0}extent) inherited from {http://www.opengis.net/citygml/relief/1.0}AbstractReliefComponentType
    
    # Element GenericApplicationPropertyOfReliefComponent ({http://www.opengis.net/citygml/relief/1.0}_GenericApplicationPropertyOfReliefComponent) inherited from {http://www.opengis.net/citygml/relief/1.0}AbstractReliefComponentType
    
    # Element externalReference ({http://www.opengis.net/citygml/1.0}externalReference) inherited from {http://www.opengis.net/citygml/1.0}AbstractCityObjectType
    
    # Element {http://www.opengis.net/citygml/relief/1.0}ridgeOrValleyLines uses Python identifier ridgeOrValleyLines
    __ridgeOrValleyLines = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'ridgeOrValleyLines'), 'ridgeOrValleyLines', '__httpwww_opengis_netcitygmlrelief1_0_BreaklineReliefType_httpwww_opengis_netcitygmlrelief1_0ridgeOrValleyLines', False)

    
    ridgeOrValleyLines = property(__ridgeOrValleyLines.value, __ridgeOrValleyLines.set, None, None)

    
    # Element creationDate ({http://www.opengis.net/citygml/1.0}creationDate) inherited from {http://www.opengis.net/citygml/1.0}AbstractCityObjectType
    
    # Element {http://www.opengis.net/citygml/relief/1.0}breaklines uses Python identifier breaklines
    __breaklines = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'breaklines'), 'breaklines', '__httpwww_opengis_netcitygmlrelief1_0_BreaklineReliefType_httpwww_opengis_netcitygmlrelief1_0breaklines', False)

    
    breaklines = property(__breaklines.value, __breaklines.set, None, None)

    
    # Element {http://www.opengis.net/citygml/relief/1.0}_GenericApplicationPropertyOfBreaklineRelief uses Python identifier GenericApplicationPropertyOfBreaklineRelief
    __GenericApplicationPropertyOfBreaklineRelief = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfBreaklineRelief'), 'GenericApplicationPropertyOfBreaklineRelief', '__httpwww_opengis_netcitygmlrelief1_0_BreaklineReliefType_httpwww_opengis_netcitygmlrelief1_0_GenericApplicationPropertyOfBreaklineRelief', True)

    
    GenericApplicationPropertyOfBreaklineRelief = property(__GenericApplicationPropertyOfBreaklineRelief.value, __GenericApplicationPropertyOfBreaklineRelief.set, None, None)

    
    # Element metaDataProperty ({http://www.opengis.net/gml}metaDataProperty) inherited from {http://www.opengis.net/gml}AbstractGMLType
    
    # Element description ({http://www.opengis.net/gml}description) inherited from {http://www.opengis.net/gml}AbstractGMLType
    
    # Element location ({http://www.opengis.net/gml}location) inherited from {http://www.opengis.net/gml}AbstractFeatureType
    
    # Attribute id inherited from {http://www.opengis.net/gml}AbstractGMLType

    _ElementMap = AbstractReliefComponentType._ElementMap.copy()
    _ElementMap.update({
        __ridgeOrValleyLines.name() : __ridgeOrValleyLines,
        __breaklines.name() : __breaklines,
        __GenericApplicationPropertyOfBreaklineRelief.name() : __GenericApplicationPropertyOfBreaklineRelief
    })
    _AttributeMap = AbstractReliefComponentType._AttributeMap.copy()
    _AttributeMap.update({
        
    })
Namespace.addCategoryObject('typeBinding', u'BreaklineReliefType', BreaklineReliefType)


# Complex type MassPointReliefType with content type ELEMENT_ONLY
class MassPointReliefType (AbstractReliefComponentType):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'MassPointReliefType')
    # Base type is AbstractReliefComponentType
    
    # Element name ({http://www.opengis.net/gml}name) inherited from {http://www.opengis.net/gml}AbstractGMLType
    
    # Element lod ({http://www.opengis.net/citygml/relief/1.0}lod) inherited from {http://www.opengis.net/citygml/relief/1.0}AbstractReliefComponentType
    
    # Element boundedBy ({http://www.opengis.net/gml}boundedBy) inherited from {http://www.opengis.net/gml}AbstractFeatureType
    
    # Element GenericApplicationPropertyOfCityObject ({http://www.opengis.net/citygml/1.0}_GenericApplicationPropertyOfCityObject) inherited from {http://www.opengis.net/citygml/1.0}AbstractCityObjectType
    
    # Element generalizesTo ({http://www.opengis.net/citygml/1.0}generalizesTo) inherited from {http://www.opengis.net/citygml/1.0}AbstractCityObjectType
    
    # Element terminationDate ({http://www.opengis.net/citygml/1.0}terminationDate) inherited from {http://www.opengis.net/citygml/1.0}AbstractCityObjectType
    
    # Element {http://www.opengis.net/citygml/relief/1.0}reliefPoints uses Python identifier reliefPoints
    __reliefPoints = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'reliefPoints'), 'reliefPoints', '__httpwww_opengis_netcitygmlrelief1_0_MassPointReliefType_httpwww_opengis_netcitygmlrelief1_0reliefPoints', False)

    
    reliefPoints = property(__reliefPoints.value, __reliefPoints.set, None, None)

    
    # Element GenericApplicationPropertyOfReliefComponent ({http://www.opengis.net/citygml/relief/1.0}_GenericApplicationPropertyOfReliefComponent) inherited from {http://www.opengis.net/citygml/relief/1.0}AbstractReliefComponentType
    
    # Element externalReference ({http://www.opengis.net/citygml/1.0}externalReference) inherited from {http://www.opengis.net/citygml/1.0}AbstractCityObjectType
    
    # Element creationDate ({http://www.opengis.net/citygml/1.0}creationDate) inherited from {http://www.opengis.net/citygml/1.0}AbstractCityObjectType
    
    # Element extent ({http://www.opengis.net/citygml/relief/1.0}extent) inherited from {http://www.opengis.net/citygml/relief/1.0}AbstractReliefComponentType
    
    # Element {http://www.opengis.net/citygml/relief/1.0}_GenericApplicationPropertyOfMassPointRelief uses Python identifier GenericApplicationPropertyOfMassPointRelief
    __GenericApplicationPropertyOfMassPointRelief = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfMassPointRelief'), 'GenericApplicationPropertyOfMassPointRelief', '__httpwww_opengis_netcitygmlrelief1_0_MassPointReliefType_httpwww_opengis_netcitygmlrelief1_0_GenericApplicationPropertyOfMassPointRelief', True)

    
    GenericApplicationPropertyOfMassPointRelief = property(__GenericApplicationPropertyOfMassPointRelief.value, __GenericApplicationPropertyOfMassPointRelief.set, None, None)

    
    # Element metaDataProperty ({http://www.opengis.net/gml}metaDataProperty) inherited from {http://www.opengis.net/gml}AbstractGMLType
    
    # Element description ({http://www.opengis.net/gml}description) inherited from {http://www.opengis.net/gml}AbstractGMLType
    
    # Element location ({http://www.opengis.net/gml}location) inherited from {http://www.opengis.net/gml}AbstractFeatureType
    
    # Attribute id inherited from {http://www.opengis.net/gml}AbstractGMLType

    _ElementMap = AbstractReliefComponentType._ElementMap.copy()
    _ElementMap.update({
        __reliefPoints.name() : __reliefPoints,
        __GenericApplicationPropertyOfMassPointRelief.name() : __GenericApplicationPropertyOfMassPointRelief
    })
    _AttributeMap = AbstractReliefComponentType._AttributeMap.copy()
    _AttributeMap.update({
        
    })
Namespace.addCategoryObject('typeBinding', u'MassPointReliefType', MassPointReliefType)


TINRelief = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'TINRelief'), TINReliefType)
Namespace.addCategoryObject('elementBinding', TINRelief.name().localName(), TINRelief)

GenericApplicationPropertyOfBreaklineRelief = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfBreaklineRelief'), pyxb.binding.datatypes.anyType, abstract=pyxb.binding.datatypes.boolean(1))
Namespace.addCategoryObject('elementBinding', GenericApplicationPropertyOfBreaklineRelief.name().localName(), GenericApplicationPropertyOfBreaklineRelief)

GenericApplicationPropertyOfTinRelief = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfTinRelief'), pyxb.binding.datatypes.anyType, abstract=pyxb.binding.datatypes.boolean(1))
Namespace.addCategoryObject('elementBinding', GenericApplicationPropertyOfTinRelief.name().localName(), GenericApplicationPropertyOfTinRelief)

ReliefFeature = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'ReliefFeature'), ReliefFeatureType)
Namespace.addCategoryObject('elementBinding', ReliefFeature.name().localName(), ReliefFeature)

GenericApplicationPropertyOfReliefFeature = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfReliefFeature'), pyxb.binding.datatypes.anyType, abstract=pyxb.binding.datatypes.boolean(1))
Namespace.addCategoryObject('elementBinding', GenericApplicationPropertyOfReliefFeature.name().localName(), GenericApplicationPropertyOfReliefFeature)

Elevation = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Elevation'), pyxb.bundles.opengis.gml.LengthType)
Namespace.addCategoryObject('elementBinding', Elevation.name().localName(), Elevation)

RasterRelief = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'RasterRelief'), RasterReliefType)
Namespace.addCategoryObject('elementBinding', RasterRelief.name().localName(), RasterRelief)

GenericApplicationPropertyOfReliefComponent = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfReliefComponent'), pyxb.binding.datatypes.anyType, abstract=pyxb.binding.datatypes.boolean(1))
Namespace.addCategoryObject('elementBinding', GenericApplicationPropertyOfReliefComponent.name().localName(), GenericApplicationPropertyOfReliefComponent)

GenericApplicationPropertyOfRasterRelief = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfRasterRelief'), pyxb.binding.datatypes.anyType, abstract=pyxb.binding.datatypes.boolean(1))
Namespace.addCategoryObject('elementBinding', GenericApplicationPropertyOfRasterRelief.name().localName(), GenericApplicationPropertyOfRasterRelief)

BreaklineRelief = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'BreaklineRelief'), BreaklineReliefType)
Namespace.addCategoryObject('elementBinding', BreaklineRelief.name().localName(), BreaklineRelief)

GenericApplicationPropertyOfMassPointRelief = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfMassPointRelief'), pyxb.binding.datatypes.anyType, abstract=pyxb.binding.datatypes.boolean(1))
Namespace.addCategoryObject('elementBinding', GenericApplicationPropertyOfMassPointRelief.name().localName(), GenericApplicationPropertyOfMassPointRelief)

ReliefComponent = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'_ReliefComponent'), AbstractReliefComponentType, abstract=pyxb.binding.datatypes.boolean(1))
Namespace.addCategoryObject('elementBinding', ReliefComponent.name().localName(), ReliefComponent)

MassPointRelief = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'MassPointRelief'), MassPointReliefType)
Namespace.addCategoryObject('elementBinding', MassPointRelief.name().localName(), MassPointRelief)



tinPropertyType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'TriangulatedSurface'), pyxb.bundles.opengis.gml.TriangulatedSurfaceType, scope=tinPropertyType))
tinPropertyType._GroupModel_ = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(tinPropertyType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'TriangulatedSurface')), min_occurs=1, max_occurs=1)
    )
tinPropertyType._ContentModel = pyxb.binding.content.ParticleModel(tinPropertyType._GroupModel_, min_occurs=0L, max_occurs=1)



AbstractReliefComponentType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'lod'), pyxb.bundles.opengis.citygml.base.integerBetween0and4, scope=AbstractReliefComponentType))

AbstractReliefComponentType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfReliefComponent'), pyxb.binding.datatypes.anyType, abstract=pyxb.binding.datatypes.boolean(1), scope=AbstractReliefComponentType))

AbstractReliefComponentType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'extent'), pyxb.bundles.opengis.gml.PolygonPropertyType, scope=AbstractReliefComponentType))
AbstractReliefComponentType._GroupModel_14 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(AbstractReliefComponentType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'metaDataProperty')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(AbstractReliefComponentType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'description')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(AbstractReliefComponentType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'name')), min_occurs=0L, max_occurs=None)
    )
AbstractReliefComponentType._GroupModel_13 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(AbstractReliefComponentType._GroupModel_14, min_occurs=1, max_occurs=1)
    )
AbstractReliefComponentType._GroupModel_15 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(AbstractReliefComponentType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'boundedBy')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(AbstractReliefComponentType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'location')), min_occurs=0L, max_occurs=1)
    )
AbstractReliefComponentType._GroupModel_12 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(AbstractReliefComponentType._GroupModel_13, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(AbstractReliefComponentType._GroupModel_15, min_occurs=1, max_occurs=1)
    )
AbstractReliefComponentType._GroupModel_16 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(AbstractReliefComponentType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'creationDate')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(AbstractReliefComponentType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'terminationDate')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(AbstractReliefComponentType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'externalReference')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(AbstractReliefComponentType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'generalizesTo')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(AbstractReliefComponentType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'_GenericApplicationPropertyOfCityObject')), min_occurs=0L, max_occurs=None)
    )
AbstractReliefComponentType._GroupModel_11 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(AbstractReliefComponentType._GroupModel_12, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(AbstractReliefComponentType._GroupModel_16, min_occurs=1, max_occurs=1)
    )
AbstractReliefComponentType._GroupModel_17 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(AbstractReliefComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(AbstractReliefComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'extent')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(AbstractReliefComponentType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfReliefComponent')), min_occurs=0L, max_occurs=None)
    )
AbstractReliefComponentType._GroupModel_10 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(AbstractReliefComponentType._GroupModel_11, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(AbstractReliefComponentType._GroupModel_17, min_occurs=1, max_occurs=1)
    )
AbstractReliefComponentType._ContentModel = pyxb.binding.content.ParticleModel(AbstractReliefComponentType._GroupModel_10, min_occurs=1, max_occurs=1)



TINReliefType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfTinRelief'), pyxb.binding.datatypes.anyType, abstract=pyxb.binding.datatypes.boolean(1), scope=TINReliefType))

TINReliefType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'tin'), tinPropertyType, scope=TINReliefType))
TINReliefType._GroupModel_15 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(TINReliefType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'metaDataProperty')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(TINReliefType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'description')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(TINReliefType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'name')), min_occurs=0L, max_occurs=None)
    )
TINReliefType._GroupModel_14 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(TINReliefType._GroupModel_15, min_occurs=1, max_occurs=1)
    )
TINReliefType._GroupModel_16 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(TINReliefType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'boundedBy')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(TINReliefType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'location')), min_occurs=0L, max_occurs=1)
    )
TINReliefType._GroupModel_13 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(TINReliefType._GroupModel_14, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(TINReliefType._GroupModel_16, min_occurs=1, max_occurs=1)
    )
TINReliefType._GroupModel_17 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(TINReliefType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'creationDate')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(TINReliefType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'terminationDate')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(TINReliefType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'externalReference')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(TINReliefType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'generalizesTo')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(TINReliefType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'_GenericApplicationPropertyOfCityObject')), min_occurs=0L, max_occurs=None)
    )
TINReliefType._GroupModel_12 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(TINReliefType._GroupModel_13, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(TINReliefType._GroupModel_17, min_occurs=1, max_occurs=1)
    )
TINReliefType._GroupModel_18 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(TINReliefType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(TINReliefType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'extent')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(TINReliefType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfReliefComponent')), min_occurs=0L, max_occurs=None)
    )
TINReliefType._GroupModel_11 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(TINReliefType._GroupModel_12, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(TINReliefType._GroupModel_18, min_occurs=1, max_occurs=1)
    )
TINReliefType._GroupModel_19 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(TINReliefType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'tin')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(TINReliefType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfTinRelief')), min_occurs=0L, max_occurs=None)
    )
TINReliefType._GroupModel_10 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(TINReliefType._GroupModel_11, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(TINReliefType._GroupModel_19, min_occurs=1, max_occurs=1)
    )
TINReliefType._ContentModel = pyxb.binding.content.ParticleModel(TINReliefType._GroupModel_10, min_occurs=1, max_occurs=1)



ReliefFeatureType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'lod'), pyxb.bundles.opengis.citygml.base.integerBetween0and4, scope=ReliefFeatureType))

ReliefFeatureType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'reliefComponent'), ReliefComponentPropertyType, scope=ReliefFeatureType))

ReliefFeatureType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfReliefFeature'), pyxb.binding.datatypes.anyType, abstract=pyxb.binding.datatypes.boolean(1), scope=ReliefFeatureType))
ReliefFeatureType._GroupModel_14 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(ReliefFeatureType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'metaDataProperty')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(ReliefFeatureType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'description')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(ReliefFeatureType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'name')), min_occurs=0L, max_occurs=None)
    )
ReliefFeatureType._GroupModel_13 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(ReliefFeatureType._GroupModel_14, min_occurs=1, max_occurs=1)
    )
ReliefFeatureType._GroupModel_15 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(ReliefFeatureType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'boundedBy')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(ReliefFeatureType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'location')), min_occurs=0L, max_occurs=1)
    )
ReliefFeatureType._GroupModel_12 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(ReliefFeatureType._GroupModel_13, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(ReliefFeatureType._GroupModel_15, min_occurs=1, max_occurs=1)
    )
ReliefFeatureType._GroupModel_16 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(ReliefFeatureType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'creationDate')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(ReliefFeatureType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'terminationDate')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(ReliefFeatureType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'externalReference')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(ReliefFeatureType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'generalizesTo')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(ReliefFeatureType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'_GenericApplicationPropertyOfCityObject')), min_occurs=0L, max_occurs=None)
    )
ReliefFeatureType._GroupModel_11 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(ReliefFeatureType._GroupModel_12, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(ReliefFeatureType._GroupModel_16, min_occurs=1, max_occurs=1)
    )
ReliefFeatureType._GroupModel_17 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(ReliefFeatureType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(ReliefFeatureType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'reliefComponent')), min_occurs=1, max_occurs=None),
    pyxb.binding.content.ParticleModel(ReliefFeatureType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfReliefFeature')), min_occurs=0L, max_occurs=None)
    )
ReliefFeatureType._GroupModel_10 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(ReliefFeatureType._GroupModel_11, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(ReliefFeatureType._GroupModel_17, min_occurs=1, max_occurs=1)
    )
ReliefFeatureType._ContentModel = pyxb.binding.content.ParticleModel(ReliefFeatureType._GroupModel_10, min_occurs=1, max_occurs=1)



ReliefComponentPropertyType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'_ReliefComponent'), AbstractReliefComponentType, abstract=pyxb.binding.datatypes.boolean(1), scope=ReliefComponentPropertyType))
ReliefComponentPropertyType._GroupModel_ = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(ReliefComponentPropertyType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_ReliefComponent')), min_occurs=1, max_occurs=1)
    )
ReliefComponentPropertyType._ContentModel = pyxb.binding.content.ParticleModel(ReliefComponentPropertyType._GroupModel_, min_occurs=0L, max_occurs=1)



gridPropertyType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'RectifiedGridCoverage'), pyxb.bundles.opengis.gml.RectifiedGridCoverageType, scope=gridPropertyType))
gridPropertyType._GroupModel_ = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(gridPropertyType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'RectifiedGridCoverage')), min_occurs=1, max_occurs=1)
    )
gridPropertyType._ContentModel = pyxb.binding.content.ParticleModel(gridPropertyType._GroupModel_, min_occurs=0L, max_occurs=1)



RasterReliefType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfRasterRelief'), pyxb.binding.datatypes.anyType, abstract=pyxb.binding.datatypes.boolean(1), scope=RasterReliefType))

RasterReliefType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'grid'), gridPropertyType, scope=RasterReliefType))
RasterReliefType._GroupModel_15 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(RasterReliefType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'metaDataProperty')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(RasterReliefType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'description')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(RasterReliefType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'name')), min_occurs=0L, max_occurs=None)
    )
RasterReliefType._GroupModel_14 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(RasterReliefType._GroupModel_15, min_occurs=1, max_occurs=1)
    )
RasterReliefType._GroupModel_16 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(RasterReliefType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'boundedBy')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(RasterReliefType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'location')), min_occurs=0L, max_occurs=1)
    )
RasterReliefType._GroupModel_13 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(RasterReliefType._GroupModel_14, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(RasterReliefType._GroupModel_16, min_occurs=1, max_occurs=1)
    )
RasterReliefType._GroupModel_17 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(RasterReliefType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'creationDate')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(RasterReliefType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'terminationDate')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(RasterReliefType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'externalReference')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(RasterReliefType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'generalizesTo')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(RasterReliefType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'_GenericApplicationPropertyOfCityObject')), min_occurs=0L, max_occurs=None)
    )
RasterReliefType._GroupModel_12 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(RasterReliefType._GroupModel_13, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(RasterReliefType._GroupModel_17, min_occurs=1, max_occurs=1)
    )
RasterReliefType._GroupModel_18 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(RasterReliefType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(RasterReliefType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'extent')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(RasterReliefType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfReliefComponent')), min_occurs=0L, max_occurs=None)
    )
RasterReliefType._GroupModel_11 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(RasterReliefType._GroupModel_12, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(RasterReliefType._GroupModel_18, min_occurs=1, max_occurs=1)
    )
RasterReliefType._GroupModel_19 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(RasterReliefType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'grid')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(RasterReliefType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfRasterRelief')), min_occurs=0L, max_occurs=None)
    )
RasterReliefType._GroupModel_10 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(RasterReliefType._GroupModel_11, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(RasterReliefType._GroupModel_19, min_occurs=1, max_occurs=1)
    )
RasterReliefType._ContentModel = pyxb.binding.content.ParticleModel(RasterReliefType._GroupModel_10, min_occurs=1, max_occurs=1)



BreaklineReliefType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'ridgeOrValleyLines'), pyxb.bundles.opengis.gml.MultiCurvePropertyType, scope=BreaklineReliefType))

BreaklineReliefType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'breaklines'), pyxb.bundles.opengis.gml.MultiCurvePropertyType, scope=BreaklineReliefType))

BreaklineReliefType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfBreaklineRelief'), pyxb.binding.datatypes.anyType, abstract=pyxb.binding.datatypes.boolean(1), scope=BreaklineReliefType))
BreaklineReliefType._GroupModel_15 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(BreaklineReliefType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'metaDataProperty')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(BreaklineReliefType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'description')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(BreaklineReliefType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'name')), min_occurs=0L, max_occurs=None)
    )
BreaklineReliefType._GroupModel_14 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(BreaklineReliefType._GroupModel_15, min_occurs=1, max_occurs=1)
    )
BreaklineReliefType._GroupModel_16 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(BreaklineReliefType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'boundedBy')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(BreaklineReliefType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'location')), min_occurs=0L, max_occurs=1)
    )
BreaklineReliefType._GroupModel_13 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(BreaklineReliefType._GroupModel_14, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(BreaklineReliefType._GroupModel_16, min_occurs=1, max_occurs=1)
    )
BreaklineReliefType._GroupModel_17 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(BreaklineReliefType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'creationDate')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(BreaklineReliefType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'terminationDate')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(BreaklineReliefType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'externalReference')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(BreaklineReliefType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'generalizesTo')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(BreaklineReliefType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'_GenericApplicationPropertyOfCityObject')), min_occurs=0L, max_occurs=None)
    )
BreaklineReliefType._GroupModel_12 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(BreaklineReliefType._GroupModel_13, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(BreaklineReliefType._GroupModel_17, min_occurs=1, max_occurs=1)
    )
BreaklineReliefType._GroupModel_18 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(BreaklineReliefType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(BreaklineReliefType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'extent')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(BreaklineReliefType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfReliefComponent')), min_occurs=0L, max_occurs=None)
    )
BreaklineReliefType._GroupModel_11 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(BreaklineReliefType._GroupModel_12, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(BreaklineReliefType._GroupModel_18, min_occurs=1, max_occurs=1)
    )
BreaklineReliefType._GroupModel_19 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(BreaklineReliefType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'ridgeOrValleyLines')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(BreaklineReliefType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'breaklines')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(BreaklineReliefType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfBreaklineRelief')), min_occurs=0L, max_occurs=None)
    )
BreaklineReliefType._GroupModel_10 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(BreaklineReliefType._GroupModel_11, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(BreaklineReliefType._GroupModel_19, min_occurs=1, max_occurs=1)
    )
BreaklineReliefType._ContentModel = pyxb.binding.content.ParticleModel(BreaklineReliefType._GroupModel_10, min_occurs=1, max_occurs=1)



MassPointReliefType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'reliefPoints'), pyxb.bundles.opengis.gml.MultiPointPropertyType, scope=MassPointReliefType))

MassPointReliefType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfMassPointRelief'), pyxb.binding.datatypes.anyType, abstract=pyxb.binding.datatypes.boolean(1), scope=MassPointReliefType))
MassPointReliefType._GroupModel_15 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(MassPointReliefType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'metaDataProperty')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(MassPointReliefType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'description')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(MassPointReliefType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'name')), min_occurs=0L, max_occurs=None)
    )
MassPointReliefType._GroupModel_14 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(MassPointReliefType._GroupModel_15, min_occurs=1, max_occurs=1)
    )
MassPointReliefType._GroupModel_16 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(MassPointReliefType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'boundedBy')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(MassPointReliefType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'location')), min_occurs=0L, max_occurs=1)
    )
MassPointReliefType._GroupModel_13 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(MassPointReliefType._GroupModel_14, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(MassPointReliefType._GroupModel_16, min_occurs=1, max_occurs=1)
    )
MassPointReliefType._GroupModel_17 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(MassPointReliefType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'creationDate')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(MassPointReliefType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'terminationDate')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(MassPointReliefType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'externalReference')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(MassPointReliefType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'generalizesTo')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(MassPointReliefType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'_GenericApplicationPropertyOfCityObject')), min_occurs=0L, max_occurs=None)
    )
MassPointReliefType._GroupModel_12 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(MassPointReliefType._GroupModel_13, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(MassPointReliefType._GroupModel_17, min_occurs=1, max_occurs=1)
    )
MassPointReliefType._GroupModel_18 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(MassPointReliefType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(MassPointReliefType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'extent')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(MassPointReliefType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfReliefComponent')), min_occurs=0L, max_occurs=None)
    )
MassPointReliefType._GroupModel_11 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(MassPointReliefType._GroupModel_12, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(MassPointReliefType._GroupModel_18, min_occurs=1, max_occurs=1)
    )
MassPointReliefType._GroupModel_19 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(MassPointReliefType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'reliefPoints')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(MassPointReliefType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfMassPointRelief')), min_occurs=0L, max_occurs=None)
    )
MassPointReliefType._GroupModel_10 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(MassPointReliefType._GroupModel_11, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(MassPointReliefType._GroupModel_19, min_occurs=1, max_occurs=1)
    )
MassPointReliefType._ContentModel = pyxb.binding.content.ParticleModel(MassPointReliefType._GroupModel_10, min_occurs=1, max_occurs=1)

TINRelief._setSubstitutionGroup(ReliefComponent)

ReliefFeature._setSubstitutionGroup(pyxb.bundles.opengis.citygml.base.CityObject)

Elevation._setSubstitutionGroup(pyxb.bundles.opengis.gml.Object)

RasterRelief._setSubstitutionGroup(ReliefComponent)

BreaklineRelief._setSubstitutionGroup(ReliefComponent)

ReliefComponent._setSubstitutionGroup(pyxb.bundles.opengis.citygml.base.CityObject)

MassPointRelief._setSubstitutionGroup(ReliefComponent)
