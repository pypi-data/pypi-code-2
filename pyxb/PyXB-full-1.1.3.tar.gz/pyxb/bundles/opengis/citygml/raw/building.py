# ./pyxb/bundles/opengis/citygml/raw/building.py
# PyXB bindings for NM:1b4db361dcbc3199fe760558a815e57bc06d92f7
# Generated 2011-09-09 14:19:19.090787 by PyXB version 1.1.3
# Namespace http://www.opengis.net/citygml/building/1.0

import pyxb
import pyxb.binding
import pyxb.binding.saxer
import StringIO
import pyxb.utils.utility
import pyxb.utils.domutils
import sys

# Unique identifier for bindings created at the same time
_GenerationUID = pyxb.utils.utility.UniqueIdentifier('urn:uuid:9cea76a4-db18-11e0-8480-001fbc013adc')

# Import bindings for namespaces imported into schema
import pyxb.binding.datatypes
import pyxb.bundles.opengis.citygml.base
import pyxb.bundles.opengis.gml

Namespace = pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/building/1.0', create_if_missing=True)
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
class BuildingInstallationFunctionType (pyxb.binding.datatypes.string):

    """Function of a building installation. The values of this type are defined in the XML file
                BuildingInstallationFunctionType.xml, according to the dictionary concept of GML3. """

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'BuildingInstallationFunctionType')
    _Documentation = u'Function of a building installation. The values of this type are defined in the XML file\n                BuildingInstallationFunctionType.xml, according to the dictionary concept of GML3. '
BuildingInstallationFunctionType._InitializeFacetMap()
Namespace.addCategoryObject('typeBinding', u'BuildingInstallationFunctionType', BuildingInstallationFunctionType)

# Atomic SimpleTypeDefinition
class BuildingFurnitureFunctionType (pyxb.binding.datatypes.string):

    """ Function of a building furniture. The values of this type are defined in the XML file
                BuildingFurnitureFunctionType.xml, according to the dictionary concept of GML3. """

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'BuildingFurnitureFunctionType')
    _Documentation = u' Function of a building furniture. The values of this type are defined in the XML file\n                BuildingFurnitureFunctionType.xml, according to the dictionary concept of GML3. '
BuildingFurnitureFunctionType._InitializeFacetMap()
Namespace.addCategoryObject('typeBinding', u'BuildingFurnitureFunctionType', BuildingFurnitureFunctionType)

# Atomic SimpleTypeDefinition
class IntBuildingInstallationUsageType (pyxb.binding.datatypes.string):

    """Actual Usage of an interior building installation. The values of this type are defined in the XML
                file IntBuildingInstallationUsageType.xml, according to the dictionary concept of GML3. """

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'IntBuildingInstallationUsageType')
    _Documentation = u'Actual Usage of an interior building installation. The values of this type are defined in the XML\n                file IntBuildingInstallationUsageType.xml, according to the dictionary concept of GML3. '
IntBuildingInstallationUsageType._InitializeFacetMap()
Namespace.addCategoryObject('typeBinding', u'IntBuildingInstallationUsageType', IntBuildingInstallationUsageType)

# Atomic SimpleTypeDefinition
class BuildingInstallationClassType (pyxb.binding.datatypes.string):

    """Class of a building installation. The values of this type are defined in the XML file
                BuildingInstallationClassType.xml, according to the dictionary concept of GML3. """

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'BuildingInstallationClassType')
    _Documentation = u'Class of a building installation. The values of this type are defined in the XML file\n                BuildingInstallationClassType.xml, according to the dictionary concept of GML3. '
BuildingInstallationClassType._InitializeFacetMap()
Namespace.addCategoryObject('typeBinding', u'BuildingInstallationClassType', BuildingInstallationClassType)

# Atomic SimpleTypeDefinition
class BuildingInstallationUsageType (pyxb.binding.datatypes.string):

    """Actual usage of a building installation. The values of this type are defined in the XML file
                BuildingInstallationUsageType.xml, according to the dictionary concept of GML3. """

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'BuildingInstallationUsageType')
    _Documentation = u'Actual usage of a building installation. The values of this type are defined in the XML file\n                BuildingInstallationUsageType.xml, according to the dictionary concept of GML3. '
BuildingInstallationUsageType._InitializeFacetMap()
Namespace.addCategoryObject('typeBinding', u'BuildingInstallationUsageType', BuildingInstallationUsageType)

# Atomic SimpleTypeDefinition
class RoomClassType (pyxb.binding.datatypes.string):

    """Class of a room . The values of this type are defined in the XML file RoomClassType.xml, according
                to the dictionary concept of GML3. """

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'RoomClassType')
    _Documentation = u'Class of a room . The values of this type are defined in the XML file RoomClassType.xml, according\n                to the dictionary concept of GML3. '
RoomClassType._InitializeFacetMap()
Namespace.addCategoryObject('typeBinding', u'RoomClassType', RoomClassType)

# Atomic SimpleTypeDefinition
class RoomFunctionType (pyxb.binding.datatypes.string):

    """Function of a room. The values of this type are defined in the XML file RoomFunctionType.xml,
                according to the dictionary concept of GML3. """

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'RoomFunctionType')
    _Documentation = u'Function of a room. The values of this type are defined in the XML file RoomFunctionType.xml,\n                according to the dictionary concept of GML3. '
RoomFunctionType._InitializeFacetMap()
Namespace.addCategoryObject('typeBinding', u'RoomFunctionType', RoomFunctionType)

# Atomic SimpleTypeDefinition
class BuildingClassType (pyxb.binding.datatypes.string):

    """ Class of a building. The values of this type are defined in the XML file BuildingClassType.xml,
                according to the dictionary concept of GML3."""

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'BuildingClassType')
    _Documentation = u' Class of a building. The values of this type are defined in the XML file BuildingClassType.xml,\n                according to the dictionary concept of GML3.'
BuildingClassType._InitializeFacetMap()
Namespace.addCategoryObject('typeBinding', u'BuildingClassType', BuildingClassType)

# Atomic SimpleTypeDefinition
class RoomUsageType (pyxb.binding.datatypes.string):

    """Actual Usage of a room. The values of this type are defined in the XML file RoomUsageType.xml,
                according to the dictionary concept of GML3. """

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'RoomUsageType')
    _Documentation = u'Actual Usage of a room. The values of this type are defined in the XML file RoomUsageType.xml,\n                according to the dictionary concept of GML3. '
RoomUsageType._InitializeFacetMap()
Namespace.addCategoryObject('typeBinding', u'RoomUsageType', RoomUsageType)

# Atomic SimpleTypeDefinition
class IntBuildingInstallationClassType (pyxb.binding.datatypes.string):

    """Class of an interior building installation. The values of this type are defined in the XML file
                IntBuildingInstallationClassType.xml, according to the dictionary concept of GML3. """

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'IntBuildingInstallationClassType')
    _Documentation = u'Class of an interior building installation. The values of this type are defined in the XML file\n                IntBuildingInstallationClassType.xml, according to the dictionary concept of GML3. '
IntBuildingInstallationClassType._InitializeFacetMap()
Namespace.addCategoryObject('typeBinding', u'IntBuildingInstallationClassType', IntBuildingInstallationClassType)

# Atomic SimpleTypeDefinition
class BuildingFunctionType (pyxb.binding.datatypes.string):

    """ Intended function of a building. The values of this type are defined in the XML file
                BuildingFunctionType.xml, according to the dictionary concept of GML3. The values may be adopted from ALKIS, the
                german standard for cadastre modelling. If the cadastre models from other countries differ in the building
                functions, these values may be compiled in another codelist to be used with CityGML. """

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'BuildingFunctionType')
    _Documentation = u' Intended function of a building. The values of this type are defined in the XML file\n                BuildingFunctionType.xml, according to the dictionary concept of GML3. The values may be adopted from ALKIS, the\n                german standard for cadastre modelling. If the cadastre models from other countries differ in the building\n                functions, these values may be compiled in another codelist to be used with CityGML. '
BuildingFunctionType._InitializeFacetMap()
Namespace.addCategoryObject('typeBinding', u'BuildingFunctionType', BuildingFunctionType)

# Atomic SimpleTypeDefinition
class IntBuildingInstallationFunctionType (pyxb.binding.datatypes.string):

    """Function of an interior building installation. The values of this type are defined in the XML file
                IntBuildingInstallationFunctionType.xml, according to the dictionary concept of GML3. """

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'IntBuildingInstallationFunctionType')
    _Documentation = u'Function of an interior building installation. The values of this type are defined in the XML file\n                IntBuildingInstallationFunctionType.xml, according to the dictionary concept of GML3. '
IntBuildingInstallationFunctionType._InitializeFacetMap()
Namespace.addCategoryObject('typeBinding', u'IntBuildingInstallationFunctionType', IntBuildingInstallationFunctionType)

# Atomic SimpleTypeDefinition
class BuildingUsageType (pyxb.binding.datatypes.string):

    """ Actual usage of a building. The values of this type are defined in the XML file
                BuildingUsageType.xml, according to the dictionary concept of GML3."""

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'BuildingUsageType')
    _Documentation = u' Actual usage of a building. The values of this type are defined in the XML file\n                BuildingUsageType.xml, according to the dictionary concept of GML3.'
BuildingUsageType._InitializeFacetMap()
Namespace.addCategoryObject('typeBinding', u'BuildingUsageType', BuildingUsageType)

# Atomic SimpleTypeDefinition
class BuildingFurnitureClassType (pyxb.binding.datatypes.string):

    """ Class of a building furniture. The values of this type are defined in the XML file
                BuildingFurnitureClassType.xml, according to the dictionary concept of GML3. """

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'BuildingFurnitureClassType')
    _Documentation = u' Class of a building furniture. The values of this type are defined in the XML file\n                BuildingFurnitureClassType.xml, according to the dictionary concept of GML3. '
BuildingFurnitureClassType._InitializeFacetMap()
Namespace.addCategoryObject('typeBinding', u'BuildingFurnitureClassType', BuildingFurnitureClassType)

# Atomic SimpleTypeDefinition
class RoofTypeType (pyxb.binding.datatypes.string):

    """Roof Types. The values of this type are defined in the XML file RoofTypeType.xml, according to the
                dictionary concept of GML3."""

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'RoofTypeType')
    _Documentation = u'Roof Types. The values of this type are defined in the XML file RoofTypeType.xml, according to the\n                dictionary concept of GML3.'
RoofTypeType._InitializeFacetMap()
Namespace.addCategoryObject('typeBinding', u'RoofTypeType', RoofTypeType)

# Atomic SimpleTypeDefinition
class BuildingFurnitureUsageType (pyxb.binding.datatypes.string):

    """ Actual Usage of a building Furniture. The values of this type are defined in the XML file
                BuildingFurnitureUsageType.xml, according to the dictionary concept of GML3. """

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'BuildingFurnitureUsageType')
    _Documentation = u' Actual Usage of a building Furniture. The values of this type are defined in the XML file\n                BuildingFurnitureUsageType.xml, according to the dictionary concept of GML3. '
BuildingFurnitureUsageType._InitializeFacetMap()
Namespace.addCategoryObject('typeBinding', u'BuildingFurnitureUsageType', BuildingFurnitureUsageType)

# Complex type RoomType with content type ELEMENT_ONLY
class RoomType (pyxb.bundles.opengis.citygml.base.AbstractCityObjectType):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'RoomType')
    # Base type is pyxb.bundles.opengis.citygml.base.AbstractCityObjectType
    
    # Element {http://www.opengis.net/citygml/building/1.0}interiorFurniture uses Python identifier interiorFurniture
    __interiorFurniture = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'interiorFurniture'), 'interiorFurniture', '__httpwww_opengis_netcitygmlbuilding1_0_RoomType_httpwww_opengis_netcitygmlbuilding1_0interiorFurniture', True)

    
    interiorFurniture = property(__interiorFurniture.value, __interiorFurniture.set, None, None)

    
    # Element description ({http://www.opengis.net/gml}description) inherited from {http://www.opengis.net/gml}AbstractGMLType
    
    # Element {http://www.opengis.net/citygml/building/1.0}usage uses Python identifier usage
    __usage = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'usage'), 'usage', '__httpwww_opengis_netcitygmlbuilding1_0_RoomType_httpwww_opengis_netcitygmlbuilding1_0usage', True)

    
    usage = property(__usage.value, __usage.set, None, None)

    
    # Element {http://www.opengis.net/citygml/building/1.0}roomInstallation uses Python identifier roomInstallation
    __roomInstallation = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'roomInstallation'), 'roomInstallation', '__httpwww_opengis_netcitygmlbuilding1_0_RoomType_httpwww_opengis_netcitygmlbuilding1_0roomInstallation', True)

    
    roomInstallation = property(__roomInstallation.value, __roomInstallation.set, None, None)

    
    # Element externalReference ({http://www.opengis.net/citygml/1.0}externalReference) inherited from {http://www.opengis.net/citygml/1.0}AbstractCityObjectType
    
    # Element GenericApplicationPropertyOfCityObject ({http://www.opengis.net/citygml/1.0}_GenericApplicationPropertyOfCityObject) inherited from {http://www.opengis.net/citygml/1.0}AbstractCityObjectType
    
    # Element generalizesTo ({http://www.opengis.net/citygml/1.0}generalizesTo) inherited from {http://www.opengis.net/citygml/1.0}AbstractCityObjectType
    
    # Element {http://www.opengis.net/citygml/building/1.0}lod4MultiSurface uses Python identifier lod4MultiSurface
    __lod4MultiSurface = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiSurface'), 'lod4MultiSurface', '__httpwww_opengis_netcitygmlbuilding1_0_RoomType_httpwww_opengis_netcitygmlbuilding1_0lod4MultiSurface', False)

    
    lod4MultiSurface = property(__lod4MultiSurface.value, __lod4MultiSurface.set, None, None)

    
    # Element name ({http://www.opengis.net/gml}name) inherited from {http://www.opengis.net/gml}AbstractGMLType
    
    # Element {http://www.opengis.net/citygml/building/1.0}class uses Python identifier class_
    __class = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'class'), 'class_', '__httpwww_opengis_netcitygmlbuilding1_0_RoomType_httpwww_opengis_netcitygmlbuilding1_0class', False)

    
    class_ = property(__class.value, __class.set, None, None)

    
    # Element location ({http://www.opengis.net/gml}location) inherited from {http://www.opengis.net/gml}AbstractFeatureType
    
    # Element boundedBy ({http://www.opengis.net/gml}boundedBy) inherited from {http://www.opengis.net/gml}AbstractFeatureType
    
    # Element {http://www.opengis.net/citygml/building/1.0}boundedBy uses Python identifier boundedBy_
    __boundedBy_ = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'boundedBy'), 'boundedBy_', '__httpwww_opengis_netcitygmlbuilding1_0_RoomType_httpwww_opengis_netcitygmlbuilding1_0boundedBy', True)

    
    boundedBy_ = property(__boundedBy_.value, __boundedBy_.set, None, None)

    
    # Element {http://www.opengis.net/citygml/building/1.0}function uses Python identifier function
    __function = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'function'), 'function', '__httpwww_opengis_netcitygmlbuilding1_0_RoomType_httpwww_opengis_netcitygmlbuilding1_0function', True)

    
    function = property(__function.value, __function.set, None, None)

    
    # Element creationDate ({http://www.opengis.net/citygml/1.0}creationDate) inherited from {http://www.opengis.net/citygml/1.0}AbstractCityObjectType
    
    # Element metaDataProperty ({http://www.opengis.net/gml}metaDataProperty) inherited from {http://www.opengis.net/gml}AbstractGMLType
    
    # Element {http://www.opengis.net/citygml/building/1.0}_GenericApplicationPropertyOfRoom uses Python identifier GenericApplicationPropertyOfRoom
    __GenericApplicationPropertyOfRoom = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfRoom'), 'GenericApplicationPropertyOfRoom', '__httpwww_opengis_netcitygmlbuilding1_0_RoomType_httpwww_opengis_netcitygmlbuilding1_0_GenericApplicationPropertyOfRoom', True)

    
    GenericApplicationPropertyOfRoom = property(__GenericApplicationPropertyOfRoom.value, __GenericApplicationPropertyOfRoom.set, None, None)

    
    # Element terminationDate ({http://www.opengis.net/citygml/1.0}terminationDate) inherited from {http://www.opengis.net/citygml/1.0}AbstractCityObjectType
    
    # Element {http://www.opengis.net/citygml/building/1.0}lod4Solid uses Python identifier lod4Solid
    __lod4Solid = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'lod4Solid'), 'lod4Solid', '__httpwww_opengis_netcitygmlbuilding1_0_RoomType_httpwww_opengis_netcitygmlbuilding1_0lod4Solid', False)

    
    lod4Solid = property(__lod4Solid.value, __lod4Solid.set, None, None)

    
    # Attribute id inherited from {http://www.opengis.net/gml}AbstractGMLType

    _ElementMap = pyxb.bundles.opengis.citygml.base.AbstractCityObjectType._ElementMap.copy()
    _ElementMap.update({
        __interiorFurniture.name() : __interiorFurniture,
        __usage.name() : __usage,
        __roomInstallation.name() : __roomInstallation,
        __lod4MultiSurface.name() : __lod4MultiSurface,
        __class.name() : __class,
        __boundedBy_.name() : __boundedBy_,
        __function.name() : __function,
        __GenericApplicationPropertyOfRoom.name() : __GenericApplicationPropertyOfRoom,
        __lod4Solid.name() : __lod4Solid
    })
    _AttributeMap = pyxb.bundles.opengis.citygml.base.AbstractCityObjectType._AttributeMap.copy()
    _AttributeMap.update({
        
    })
Namespace.addCategoryObject('typeBinding', u'RoomType', RoomType)


# Complex type AbstractOpeningType with content type ELEMENT_ONLY
class AbstractOpeningType (pyxb.bundles.opengis.citygml.base.AbstractCityObjectType):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = True
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'AbstractOpeningType')
    # Base type is pyxb.bundles.opengis.citygml.base.AbstractCityObjectType
    
    # Element {http://www.opengis.net/citygml/building/1.0}lod3MultiSurface uses Python identifier lod3MultiSurface
    __lod3MultiSurface = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiSurface'), 'lod3MultiSurface', '__httpwww_opengis_netcitygmlbuilding1_0_AbstractOpeningType_httpwww_opengis_netcitygmlbuilding1_0lod3MultiSurface', False)

    
    lod3MultiSurface = property(__lod3MultiSurface.value, __lod3MultiSurface.set, None, None)

    
    # Element creationDate ({http://www.opengis.net/citygml/1.0}creationDate) inherited from {http://www.opengis.net/citygml/1.0}AbstractCityObjectType
    
    # Element location ({http://www.opengis.net/gml}location) inherited from {http://www.opengis.net/gml}AbstractFeatureType
    
    # Element generalizesTo ({http://www.opengis.net/citygml/1.0}generalizesTo) inherited from {http://www.opengis.net/citygml/1.0}AbstractCityObjectType
    
    # Element terminationDate ({http://www.opengis.net/citygml/1.0}terminationDate) inherited from {http://www.opengis.net/citygml/1.0}AbstractCityObjectType
    
    # Element GenericApplicationPropertyOfCityObject ({http://www.opengis.net/citygml/1.0}_GenericApplicationPropertyOfCityObject) inherited from {http://www.opengis.net/citygml/1.0}AbstractCityObjectType
    
    # Element externalReference ({http://www.opengis.net/citygml/1.0}externalReference) inherited from {http://www.opengis.net/citygml/1.0}AbstractCityObjectType
    
    # Element {http://www.opengis.net/citygml/building/1.0}_GenericApplicationPropertyOfOpening uses Python identifier GenericApplicationPropertyOfOpening
    __GenericApplicationPropertyOfOpening = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfOpening'), 'GenericApplicationPropertyOfOpening', '__httpwww_opengis_netcitygmlbuilding1_0_AbstractOpeningType_httpwww_opengis_netcitygmlbuilding1_0_GenericApplicationPropertyOfOpening', True)

    
    GenericApplicationPropertyOfOpening = property(__GenericApplicationPropertyOfOpening.value, __GenericApplicationPropertyOfOpening.set, None, None)

    
    # Element description ({http://www.opengis.net/gml}description) inherited from {http://www.opengis.net/gml}AbstractGMLType
    
    # Element name ({http://www.opengis.net/gml}name) inherited from {http://www.opengis.net/gml}AbstractGMLType
    
    # Element metaDataProperty ({http://www.opengis.net/gml}metaDataProperty) inherited from {http://www.opengis.net/gml}AbstractGMLType
    
    # Element {http://www.opengis.net/citygml/building/1.0}lod4MultiSurface uses Python identifier lod4MultiSurface
    __lod4MultiSurface = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiSurface'), 'lod4MultiSurface', '__httpwww_opengis_netcitygmlbuilding1_0_AbstractOpeningType_httpwww_opengis_netcitygmlbuilding1_0lod4MultiSurface', False)

    
    lod4MultiSurface = property(__lod4MultiSurface.value, __lod4MultiSurface.set, None, None)

    
    # Element boundedBy ({http://www.opengis.net/gml}boundedBy) inherited from {http://www.opengis.net/gml}AbstractFeatureType
    
    # Attribute id inherited from {http://www.opengis.net/gml}AbstractGMLType

    _ElementMap = pyxb.bundles.opengis.citygml.base.AbstractCityObjectType._ElementMap.copy()
    _ElementMap.update({
        __lod3MultiSurface.name() : __lod3MultiSurface,
        __GenericApplicationPropertyOfOpening.name() : __GenericApplicationPropertyOfOpening,
        __lod4MultiSurface.name() : __lod4MultiSurface
    })
    _AttributeMap = pyxb.bundles.opengis.citygml.base.AbstractCityObjectType._AttributeMap.copy()
    _AttributeMap.update({
        
    })
Namespace.addCategoryObject('typeBinding', u'AbstractOpeningType', AbstractOpeningType)


# Complex type BuildingFurnitureType with content type ELEMENT_ONLY
class BuildingFurnitureType (pyxb.bundles.opengis.citygml.base.AbstractCityObjectType):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'BuildingFurnitureType')
    # Base type is pyxb.bundles.opengis.citygml.base.AbstractCityObjectType
    
    # Element location ({http://www.opengis.net/gml}location) inherited from {http://www.opengis.net/gml}AbstractFeatureType
    
    # Element description ({http://www.opengis.net/gml}description) inherited from {http://www.opengis.net/gml}AbstractGMLType
    
    # Element {http://www.opengis.net/citygml/building/1.0}lod4ImplicitRepresentation uses Python identifier lod4ImplicitRepresentation
    __lod4ImplicitRepresentation = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'lod4ImplicitRepresentation'), 'lod4ImplicitRepresentation', '__httpwww_opengis_netcitygmlbuilding1_0_BuildingFurnitureType_httpwww_opengis_netcitygmlbuilding1_0lod4ImplicitRepresentation', False)

    
    lod4ImplicitRepresentation = property(__lod4ImplicitRepresentation.value, __lod4ImplicitRepresentation.set, None, None)

    
    # Element {http://www.opengis.net/citygml/building/1.0}class uses Python identifier class_
    __class = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'class'), 'class_', '__httpwww_opengis_netcitygmlbuilding1_0_BuildingFurnitureType_httpwww_opengis_netcitygmlbuilding1_0class', False)

    
    class_ = property(__class.value, __class.set, None, None)

    
    # Element generalizesTo ({http://www.opengis.net/citygml/1.0}generalizesTo) inherited from {http://www.opengis.net/citygml/1.0}AbstractCityObjectType
    
    # Element {http://www.opengis.net/citygml/building/1.0}usage uses Python identifier usage
    __usage = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'usage'), 'usage', '__httpwww_opengis_netcitygmlbuilding1_0_BuildingFurnitureType_httpwww_opengis_netcitygmlbuilding1_0usage', True)

    
    usage = property(__usage.value, __usage.set, None, None)

    
    # Element terminationDate ({http://www.opengis.net/citygml/1.0}terminationDate) inherited from {http://www.opengis.net/citygml/1.0}AbstractCityObjectType
    
    # Element {http://www.opengis.net/citygml/building/1.0}function uses Python identifier function
    __function = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'function'), 'function', '__httpwww_opengis_netcitygmlbuilding1_0_BuildingFurnitureType_httpwww_opengis_netcitygmlbuilding1_0function', True)

    
    function = property(__function.value, __function.set, None, None)

    
    # Element externalReference ({http://www.opengis.net/citygml/1.0}externalReference) inherited from {http://www.opengis.net/citygml/1.0}AbstractCityObjectType
    
    # Element boundedBy ({http://www.opengis.net/gml}boundedBy) inherited from {http://www.opengis.net/gml}AbstractFeatureType
    
    # Element creationDate ({http://www.opengis.net/citygml/1.0}creationDate) inherited from {http://www.opengis.net/citygml/1.0}AbstractCityObjectType
    
    # Element name ({http://www.opengis.net/gml}name) inherited from {http://www.opengis.net/gml}AbstractGMLType
    
    # Element metaDataProperty ({http://www.opengis.net/gml}metaDataProperty) inherited from {http://www.opengis.net/gml}AbstractGMLType
    
    # Element {http://www.opengis.net/citygml/building/1.0}lod4Geometry uses Python identifier lod4Geometry
    __lod4Geometry = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'lod4Geometry'), 'lod4Geometry', '__httpwww_opengis_netcitygmlbuilding1_0_BuildingFurnitureType_httpwww_opengis_netcitygmlbuilding1_0lod4Geometry', False)

    
    lod4Geometry = property(__lod4Geometry.value, __lod4Geometry.set, None, None)

    
    # Element GenericApplicationPropertyOfCityObject ({http://www.opengis.net/citygml/1.0}_GenericApplicationPropertyOfCityObject) inherited from {http://www.opengis.net/citygml/1.0}AbstractCityObjectType
    
    # Element {http://www.opengis.net/citygml/building/1.0}_GenericApplicationPropertyOfBuildingFurniture uses Python identifier GenericApplicationPropertyOfBuildingFurniture
    __GenericApplicationPropertyOfBuildingFurniture = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfBuildingFurniture'), 'GenericApplicationPropertyOfBuildingFurniture', '__httpwww_opengis_netcitygmlbuilding1_0_BuildingFurnitureType_httpwww_opengis_netcitygmlbuilding1_0_GenericApplicationPropertyOfBuildingFurniture', True)

    
    GenericApplicationPropertyOfBuildingFurniture = property(__GenericApplicationPropertyOfBuildingFurniture.value, __GenericApplicationPropertyOfBuildingFurniture.set, None, None)

    
    # Attribute id inherited from {http://www.opengis.net/gml}AbstractGMLType

    _ElementMap = pyxb.bundles.opengis.citygml.base.AbstractCityObjectType._ElementMap.copy()
    _ElementMap.update({
        __lod4ImplicitRepresentation.name() : __lod4ImplicitRepresentation,
        __class.name() : __class,
        __usage.name() : __usage,
        __function.name() : __function,
        __lod4Geometry.name() : __lod4Geometry,
        __GenericApplicationPropertyOfBuildingFurniture.name() : __GenericApplicationPropertyOfBuildingFurniture
    })
    _AttributeMap = pyxb.bundles.opengis.citygml.base.AbstractCityObjectType._AttributeMap.copy()
    _AttributeMap.update({
        
    })
Namespace.addCategoryObject('typeBinding', u'BuildingFurnitureType', BuildingFurnitureType)


# Complex type BoundarySurfacePropertyType with content type ELEMENT_ONLY
class BoundarySurfacePropertyType (pyxb.bundles.opengis.gml.AssociationType):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'BoundarySurfacePropertyType')
    # Base type is pyxb.bundles.opengis.gml.AssociationType
    
    # Element {http://www.opengis.net/citygml/building/1.0}_BoundarySurface uses Python identifier BoundarySurface
    __BoundarySurface = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'_BoundarySurface'), 'BoundarySurface', '__httpwww_opengis_netcitygmlbuilding1_0_BoundarySurfacePropertyType_httpwww_opengis_netcitygmlbuilding1_0_BoundarySurface', False)

    
    BoundarySurface = property(__BoundarySurface.value, __BoundarySurface.set, None, None)

    
    # Attribute arcrole inherited from {http://www.opengis.net/gml}AssociationType
    
    # Attribute title inherited from {http://www.opengis.net/gml}AssociationType
    
    # Attribute remoteSchema inherited from {http://www.opengis.net/gml}AssociationType
    
    # Attribute href inherited from {http://www.opengis.net/gml}AssociationType
    
    # Attribute type inherited from {http://www.opengis.net/gml}AssociationType
    
    # Attribute actuate inherited from {http://www.opengis.net/gml}AssociationType
    
    # Attribute show inherited from {http://www.opengis.net/gml}AssociationType
    
    # Attribute role inherited from {http://www.opengis.net/gml}AssociationType

    _ElementMap = pyxb.bundles.opengis.gml.AssociationType._ElementMap.copy()
    _ElementMap.update({
        __BoundarySurface.name() : __BoundarySurface
    })
    _AttributeMap = pyxb.bundles.opengis.gml.AssociationType._AttributeMap.copy()
    _AttributeMap.update({
        
    })
Namespace.addCategoryObject('typeBinding', u'BoundarySurfacePropertyType', BoundarySurfacePropertyType)


# Complex type AbstractBoundarySurfaceType with content type ELEMENT_ONLY
class AbstractBoundarySurfaceType (pyxb.bundles.opengis.citygml.base.AbstractCityObjectType):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = True
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'AbstractBoundarySurfaceType')
    # Base type is pyxb.bundles.opengis.citygml.base.AbstractCityObjectType
    
    # Element {http://www.opengis.net/citygml/building/1.0}lod4MultiSurface uses Python identifier lod4MultiSurface
    __lod4MultiSurface = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiSurface'), 'lod4MultiSurface', '__httpwww_opengis_netcitygmlbuilding1_0_AbstractBoundarySurfaceType_httpwww_opengis_netcitygmlbuilding1_0lod4MultiSurface', False)

    
    lod4MultiSurface = property(__lod4MultiSurface.value, __lod4MultiSurface.set, None, None)

    
    # Element description ({http://www.opengis.net/gml}description) inherited from {http://www.opengis.net/gml}AbstractGMLType
    
    # Element location ({http://www.opengis.net/gml}location) inherited from {http://www.opengis.net/gml}AbstractFeatureType
    
    # Element {http://www.opengis.net/citygml/building/1.0}opening uses Python identifier opening
    __opening = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'opening'), 'opening', '__httpwww_opengis_netcitygmlbuilding1_0_AbstractBoundarySurfaceType_httpwww_opengis_netcitygmlbuilding1_0opening', True)

    
    opening = property(__opening.value, __opening.set, None, None)

    
    # Element GenericApplicationPropertyOfCityObject ({http://www.opengis.net/citygml/1.0}_GenericApplicationPropertyOfCityObject) inherited from {http://www.opengis.net/citygml/1.0}AbstractCityObjectType
    
    # Element generalizesTo ({http://www.opengis.net/citygml/1.0}generalizesTo) inherited from {http://www.opengis.net/citygml/1.0}AbstractCityObjectType
    
    # Element terminationDate ({http://www.opengis.net/citygml/1.0}terminationDate) inherited from {http://www.opengis.net/citygml/1.0}AbstractCityObjectType
    
    # Element name ({http://www.opengis.net/gml}name) inherited from {http://www.opengis.net/gml}AbstractGMLType
    
    # Element externalReference ({http://www.opengis.net/citygml/1.0}externalReference) inherited from {http://www.opengis.net/citygml/1.0}AbstractCityObjectType
    
    # Element {http://www.opengis.net/citygml/building/1.0}lod2MultiSurface uses Python identifier lod2MultiSurface
    __lod2MultiSurface = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'lod2MultiSurface'), 'lod2MultiSurface', '__httpwww_opengis_netcitygmlbuilding1_0_AbstractBoundarySurfaceType_httpwww_opengis_netcitygmlbuilding1_0lod2MultiSurface', False)

    
    lod2MultiSurface = property(__lod2MultiSurface.value, __lod2MultiSurface.set, None, None)

    
    # Element {http://www.opengis.net/citygml/building/1.0}_GenericApplicationPropertyOfBoundarySurface uses Python identifier GenericApplicationPropertyOfBoundarySurface
    __GenericApplicationPropertyOfBoundarySurface = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfBoundarySurface'), 'GenericApplicationPropertyOfBoundarySurface', '__httpwww_opengis_netcitygmlbuilding1_0_AbstractBoundarySurfaceType_httpwww_opengis_netcitygmlbuilding1_0_GenericApplicationPropertyOfBoundarySurface', True)

    
    GenericApplicationPropertyOfBoundarySurface = property(__GenericApplicationPropertyOfBoundarySurface.value, __GenericApplicationPropertyOfBoundarySurface.set, None, None)

    
    # Element {http://www.opengis.net/citygml/building/1.0}lod3MultiSurface uses Python identifier lod3MultiSurface
    __lod3MultiSurface = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiSurface'), 'lod3MultiSurface', '__httpwww_opengis_netcitygmlbuilding1_0_AbstractBoundarySurfaceType_httpwww_opengis_netcitygmlbuilding1_0lod3MultiSurface', False)

    
    lod3MultiSurface = property(__lod3MultiSurface.value, __lod3MultiSurface.set, None, None)

    
    # Element creationDate ({http://www.opengis.net/citygml/1.0}creationDate) inherited from {http://www.opengis.net/citygml/1.0}AbstractCityObjectType
    
    # Element metaDataProperty ({http://www.opengis.net/gml}metaDataProperty) inherited from {http://www.opengis.net/gml}AbstractGMLType
    
    # Element boundedBy ({http://www.opengis.net/gml}boundedBy) inherited from {http://www.opengis.net/gml}AbstractFeatureType
    
    # Attribute id inherited from {http://www.opengis.net/gml}AbstractGMLType

    _ElementMap = pyxb.bundles.opengis.citygml.base.AbstractCityObjectType._ElementMap.copy()
    _ElementMap.update({
        __lod4MultiSurface.name() : __lod4MultiSurface,
        __opening.name() : __opening,
        __lod2MultiSurface.name() : __lod2MultiSurface,
        __GenericApplicationPropertyOfBoundarySurface.name() : __GenericApplicationPropertyOfBoundarySurface,
        __lod3MultiSurface.name() : __lod3MultiSurface
    })
    _AttributeMap = pyxb.bundles.opengis.citygml.base.AbstractCityObjectType._AttributeMap.copy()
    _AttributeMap.update({
        
    })
Namespace.addCategoryObject('typeBinding', u'AbstractBoundarySurfaceType', AbstractBoundarySurfaceType)


# Complex type GroundSurfaceType with content type ELEMENT_ONLY
class GroundSurfaceType (AbstractBoundarySurfaceType):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'GroundSurfaceType')
    # Base type is AbstractBoundarySurfaceType
    
    # Element location ({http://www.opengis.net/gml}location) inherited from {http://www.opengis.net/gml}AbstractFeatureType
    
    # Element opening ({http://www.opengis.net/citygml/building/1.0}opening) inherited from {http://www.opengis.net/citygml/building/1.0}AbstractBoundarySurfaceType
    
    # Element lod4MultiSurface ({http://www.opengis.net/citygml/building/1.0}lod4MultiSurface) inherited from {http://www.opengis.net/citygml/building/1.0}AbstractBoundarySurfaceType
    
    # Element description ({http://www.opengis.net/gml}description) inherited from {http://www.opengis.net/gml}AbstractGMLType
    
    # Element generalizesTo ({http://www.opengis.net/citygml/1.0}generalizesTo) inherited from {http://www.opengis.net/citygml/1.0}AbstractCityObjectType
    
    # Element GenericApplicationPropertyOfCityObject ({http://www.opengis.net/citygml/1.0}_GenericApplicationPropertyOfCityObject) inherited from {http://www.opengis.net/citygml/1.0}AbstractCityObjectType
    
    # Element terminationDate ({http://www.opengis.net/citygml/1.0}terminationDate) inherited from {http://www.opengis.net/citygml/1.0}AbstractCityObjectType
    
    # Element name ({http://www.opengis.net/gml}name) inherited from {http://www.opengis.net/gml}AbstractGMLType
    
    # Element externalReference ({http://www.opengis.net/citygml/1.0}externalReference) inherited from {http://www.opengis.net/citygml/1.0}AbstractCityObjectType
    
    # Element lod2MultiSurface ({http://www.opengis.net/citygml/building/1.0}lod2MultiSurface) inherited from {http://www.opengis.net/citygml/building/1.0}AbstractBoundarySurfaceType
    
    # Element {http://www.opengis.net/citygml/building/1.0}_GenericApplicationPropertyOfGroundSurface uses Python identifier GenericApplicationPropertyOfGroundSurface
    __GenericApplicationPropertyOfGroundSurface = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfGroundSurface'), 'GenericApplicationPropertyOfGroundSurface', '__httpwww_opengis_netcitygmlbuilding1_0_GroundSurfaceType_httpwww_opengis_netcitygmlbuilding1_0_GenericApplicationPropertyOfGroundSurface', True)

    
    GenericApplicationPropertyOfGroundSurface = property(__GenericApplicationPropertyOfGroundSurface.value, __GenericApplicationPropertyOfGroundSurface.set, None, None)

    
    # Element GenericApplicationPropertyOfBoundarySurface ({http://www.opengis.net/citygml/building/1.0}_GenericApplicationPropertyOfBoundarySurface) inherited from {http://www.opengis.net/citygml/building/1.0}AbstractBoundarySurfaceType
    
    # Element lod3MultiSurface ({http://www.opengis.net/citygml/building/1.0}lod3MultiSurface) inherited from {http://www.opengis.net/citygml/building/1.0}AbstractBoundarySurfaceType
    
    # Element metaDataProperty ({http://www.opengis.net/gml}metaDataProperty) inherited from {http://www.opengis.net/gml}AbstractGMLType
    
    # Element creationDate ({http://www.opengis.net/citygml/1.0}creationDate) inherited from {http://www.opengis.net/citygml/1.0}AbstractCityObjectType
    
    # Element boundedBy ({http://www.opengis.net/gml}boundedBy) inherited from {http://www.opengis.net/gml}AbstractFeatureType
    
    # Attribute id inherited from {http://www.opengis.net/gml}AbstractGMLType

    _ElementMap = AbstractBoundarySurfaceType._ElementMap.copy()
    _ElementMap.update({
        __GenericApplicationPropertyOfGroundSurface.name() : __GenericApplicationPropertyOfGroundSurface
    })
    _AttributeMap = AbstractBoundarySurfaceType._AttributeMap.copy()
    _AttributeMap.update({
        
    })
Namespace.addCategoryObject('typeBinding', u'GroundSurfaceType', GroundSurfaceType)


# Complex type InteriorRoomPropertyType with content type ELEMENT_ONLY
class InteriorRoomPropertyType (pyxb.bundles.opengis.gml.AssociationType):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'InteriorRoomPropertyType')
    # Base type is pyxb.bundles.opengis.gml.AssociationType
    
    # Element {http://www.opengis.net/citygml/building/1.0}Room uses Python identifier Room
    __Room = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'Room'), 'Room', '__httpwww_opengis_netcitygmlbuilding1_0_InteriorRoomPropertyType_httpwww_opengis_netcitygmlbuilding1_0Room', False)

    
    Room = property(__Room.value, __Room.set, None, None)

    
    # Attribute arcrole inherited from {http://www.opengis.net/gml}AssociationType
    
    # Attribute title inherited from {http://www.opengis.net/gml}AssociationType
    
    # Attribute remoteSchema inherited from {http://www.opengis.net/gml}AssociationType
    
    # Attribute href inherited from {http://www.opengis.net/gml}AssociationType
    
    # Attribute type inherited from {http://www.opengis.net/gml}AssociationType
    
    # Attribute actuate inherited from {http://www.opengis.net/gml}AssociationType
    
    # Attribute show inherited from {http://www.opengis.net/gml}AssociationType
    
    # Attribute role inherited from {http://www.opengis.net/gml}AssociationType

    _ElementMap = pyxb.bundles.opengis.gml.AssociationType._ElementMap.copy()
    _ElementMap.update({
        __Room.name() : __Room
    })
    _AttributeMap = pyxb.bundles.opengis.gml.AssociationType._AttributeMap.copy()
    _AttributeMap.update({
        
    })
Namespace.addCategoryObject('typeBinding', u'InteriorRoomPropertyType', InteriorRoomPropertyType)


# Complex type ClosureSurfaceType with content type ELEMENT_ONLY
class ClosureSurfaceType (AbstractBoundarySurfaceType):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'ClosureSurfaceType')
    # Base type is AbstractBoundarySurfaceType
    
    # Element location ({http://www.opengis.net/gml}location) inherited from {http://www.opengis.net/gml}AbstractFeatureType
    
    # Element opening ({http://www.opengis.net/citygml/building/1.0}opening) inherited from {http://www.opengis.net/citygml/building/1.0}AbstractBoundarySurfaceType
    
    # Element lod4MultiSurface ({http://www.opengis.net/citygml/building/1.0}lod4MultiSurface) inherited from {http://www.opengis.net/citygml/building/1.0}AbstractBoundarySurfaceType
    
    # Element description ({http://www.opengis.net/gml}description) inherited from {http://www.opengis.net/gml}AbstractGMLType
    
    # Element generalizesTo ({http://www.opengis.net/citygml/1.0}generalizesTo) inherited from {http://www.opengis.net/citygml/1.0}AbstractCityObjectType
    
    # Element GenericApplicationPropertyOfCityObject ({http://www.opengis.net/citygml/1.0}_GenericApplicationPropertyOfCityObject) inherited from {http://www.opengis.net/citygml/1.0}AbstractCityObjectType
    
    # Element metaDataProperty ({http://www.opengis.net/gml}metaDataProperty) inherited from {http://www.opengis.net/gml}AbstractGMLType
    
    # Element terminationDate ({http://www.opengis.net/citygml/1.0}terminationDate) inherited from {http://www.opengis.net/citygml/1.0}AbstractCityObjectType
    
    # Element name ({http://www.opengis.net/gml}name) inherited from {http://www.opengis.net/gml}AbstractGMLType
    
    # Element externalReference ({http://www.opengis.net/citygml/1.0}externalReference) inherited from {http://www.opengis.net/citygml/1.0}AbstractCityObjectType
    
    # Element lod2MultiSurface ({http://www.opengis.net/citygml/building/1.0}lod2MultiSurface) inherited from {http://www.opengis.net/citygml/building/1.0}AbstractBoundarySurfaceType
    
    # Element GenericApplicationPropertyOfBoundarySurface ({http://www.opengis.net/citygml/building/1.0}_GenericApplicationPropertyOfBoundarySurface) inherited from {http://www.opengis.net/citygml/building/1.0}AbstractBoundarySurfaceType
    
    # Element lod3MultiSurface ({http://www.opengis.net/citygml/building/1.0}lod3MultiSurface) inherited from {http://www.opengis.net/citygml/building/1.0}AbstractBoundarySurfaceType
    
    # Element {http://www.opengis.net/citygml/building/1.0}_GenericApplicationPropertyOfClosureSurface uses Python identifier GenericApplicationPropertyOfClosureSurface
    __GenericApplicationPropertyOfClosureSurface = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfClosureSurface'), 'GenericApplicationPropertyOfClosureSurface', '__httpwww_opengis_netcitygmlbuilding1_0_ClosureSurfaceType_httpwww_opengis_netcitygmlbuilding1_0_GenericApplicationPropertyOfClosureSurface', True)

    
    GenericApplicationPropertyOfClosureSurface = property(__GenericApplicationPropertyOfClosureSurface.value, __GenericApplicationPropertyOfClosureSurface.set, None, None)

    
    # Element creationDate ({http://www.opengis.net/citygml/1.0}creationDate) inherited from {http://www.opengis.net/citygml/1.0}AbstractCityObjectType
    
    # Element boundedBy ({http://www.opengis.net/gml}boundedBy) inherited from {http://www.opengis.net/gml}AbstractFeatureType
    
    # Attribute id inherited from {http://www.opengis.net/gml}AbstractGMLType

    _ElementMap = AbstractBoundarySurfaceType._ElementMap.copy()
    _ElementMap.update({
        __GenericApplicationPropertyOfClosureSurface.name() : __GenericApplicationPropertyOfClosureSurface
    })
    _AttributeMap = AbstractBoundarySurfaceType._AttributeMap.copy()
    _AttributeMap.update({
        
    })
Namespace.addCategoryObject('typeBinding', u'ClosureSurfaceType', ClosureSurfaceType)


# Complex type RoofSurfaceType with content type ELEMENT_ONLY
class RoofSurfaceType (AbstractBoundarySurfaceType):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'RoofSurfaceType')
    # Base type is AbstractBoundarySurfaceType
    
    # Element location ({http://www.opengis.net/gml}location) inherited from {http://www.opengis.net/gml}AbstractFeatureType
    
    # Element opening ({http://www.opengis.net/citygml/building/1.0}opening) inherited from {http://www.opengis.net/citygml/building/1.0}AbstractBoundarySurfaceType
    
    # Element creationDate ({http://www.opengis.net/citygml/1.0}creationDate) inherited from {http://www.opengis.net/citygml/1.0}AbstractCityObjectType
    
    # Element lod4MultiSurface ({http://www.opengis.net/citygml/building/1.0}lod4MultiSurface) inherited from {http://www.opengis.net/citygml/building/1.0}AbstractBoundarySurfaceType
    
    # Element description ({http://www.opengis.net/gml}description) inherited from {http://www.opengis.net/gml}AbstractGMLType
    
    # Element generalizesTo ({http://www.opengis.net/citygml/1.0}generalizesTo) inherited from {http://www.opengis.net/citygml/1.0}AbstractCityObjectType
    
    # Element GenericApplicationPropertyOfCityObject ({http://www.opengis.net/citygml/1.0}_GenericApplicationPropertyOfCityObject) inherited from {http://www.opengis.net/citygml/1.0}AbstractCityObjectType
    
    # Element terminationDate ({http://www.opengis.net/citygml/1.0}terminationDate) inherited from {http://www.opengis.net/citygml/1.0}AbstractCityObjectType
    
    # Element name ({http://www.opengis.net/gml}name) inherited from {http://www.opengis.net/gml}AbstractGMLType
    
    # Element externalReference ({http://www.opengis.net/citygml/1.0}externalReference) inherited from {http://www.opengis.net/citygml/1.0}AbstractCityObjectType
    
    # Element lod2MultiSurface ({http://www.opengis.net/citygml/building/1.0}lod2MultiSurface) inherited from {http://www.opengis.net/citygml/building/1.0}AbstractBoundarySurfaceType
    
    # Element GenericApplicationPropertyOfBoundarySurface ({http://www.opengis.net/citygml/building/1.0}_GenericApplicationPropertyOfBoundarySurface) inherited from {http://www.opengis.net/citygml/building/1.0}AbstractBoundarySurfaceType
    
    # Element lod3MultiSurface ({http://www.opengis.net/citygml/building/1.0}lod3MultiSurface) inherited from {http://www.opengis.net/citygml/building/1.0}AbstractBoundarySurfaceType
    
    # Element {http://www.opengis.net/citygml/building/1.0}_GenericApplicationPropertyOfRoofSurface uses Python identifier GenericApplicationPropertyOfRoofSurface
    __GenericApplicationPropertyOfRoofSurface = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfRoofSurface'), 'GenericApplicationPropertyOfRoofSurface', '__httpwww_opengis_netcitygmlbuilding1_0_RoofSurfaceType_httpwww_opengis_netcitygmlbuilding1_0_GenericApplicationPropertyOfRoofSurface', True)

    
    GenericApplicationPropertyOfRoofSurface = property(__GenericApplicationPropertyOfRoofSurface.value, __GenericApplicationPropertyOfRoofSurface.set, None, None)

    
    # Element metaDataProperty ({http://www.opengis.net/gml}metaDataProperty) inherited from {http://www.opengis.net/gml}AbstractGMLType
    
    # Element boundedBy ({http://www.opengis.net/gml}boundedBy) inherited from {http://www.opengis.net/gml}AbstractFeatureType
    
    # Attribute id inherited from {http://www.opengis.net/gml}AbstractGMLType

    _ElementMap = AbstractBoundarySurfaceType._ElementMap.copy()
    _ElementMap.update({
        __GenericApplicationPropertyOfRoofSurface.name() : __GenericApplicationPropertyOfRoofSurface
    })
    _AttributeMap = AbstractBoundarySurfaceType._AttributeMap.copy()
    _AttributeMap.update({
        
    })
Namespace.addCategoryObject('typeBinding', u'RoofSurfaceType', RoofSurfaceType)


# Complex type AbstractBuildingType with content type ELEMENT_ONLY
class AbstractBuildingType (pyxb.bundles.opengis.citygml.base.AbstractSiteType):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = True
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'AbstractBuildingType')
    # Base type is pyxb.bundles.opengis.citygml.base.AbstractSiteType
    
    # Element {http://www.opengis.net/citygml/building/1.0}yearOfDemolition uses Python identifier yearOfDemolition
    __yearOfDemolition = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'yearOfDemolition'), 'yearOfDemolition', '__httpwww_opengis_netcitygmlbuilding1_0_AbstractBuildingType_httpwww_opengis_netcitygmlbuilding1_0yearOfDemolition', False)

    
    yearOfDemolition = property(__yearOfDemolition.value, __yearOfDemolition.set, None, None)

    
    # Element location ({http://www.opengis.net/gml}location) inherited from {http://www.opengis.net/gml}AbstractFeatureType
    
    # Element {http://www.opengis.net/citygml/building/1.0}boundedBy uses Python identifier boundedBy_
    __boundedBy_ = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'boundedBy'), 'boundedBy_', '__httpwww_opengis_netcitygmlbuilding1_0_AbstractBuildingType_httpwww_opengis_netcitygmlbuilding1_0boundedBy', True)

    
    boundedBy_ = property(__boundedBy_.value, __boundedBy_.set, None, None)

    
    # Element {http://www.opengis.net/citygml/building/1.0}roofType uses Python identifier roofType
    __roofType = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'roofType'), 'roofType', '__httpwww_opengis_netcitygmlbuilding1_0_AbstractBuildingType_httpwww_opengis_netcitygmlbuilding1_0roofType', False)

    
    roofType = property(__roofType.value, __roofType.set, None, None)

    
    # Element {http://www.opengis.net/citygml/building/1.0}function uses Python identifier function
    __function = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'function'), 'function', '__httpwww_opengis_netcitygmlbuilding1_0_AbstractBuildingType_httpwww_opengis_netcitygmlbuilding1_0function', True)

    
    function = property(__function.value, __function.set, None, None)

    
    # Element {http://www.opengis.net/citygml/building/1.0}lod3Solid uses Python identifier lod3Solid
    __lod3Solid = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'lod3Solid'), 'lod3Solid', '__httpwww_opengis_netcitygmlbuilding1_0_AbstractBuildingType_httpwww_opengis_netcitygmlbuilding1_0lod3Solid', False)

    
    lod3Solid = property(__lod3Solid.value, __lod3Solid.set, None, None)

    
    # Element {http://www.opengis.net/citygml/building/1.0}measuredHeight uses Python identifier measuredHeight
    __measuredHeight = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'measuredHeight'), 'measuredHeight', '__httpwww_opengis_netcitygmlbuilding1_0_AbstractBuildingType_httpwww_opengis_netcitygmlbuilding1_0measuredHeight', False)

    
    measuredHeight = property(__measuredHeight.value, __measuredHeight.set, None, None)

    
    # Element metaDataProperty ({http://www.opengis.net/gml}metaDataProperty) inherited from {http://www.opengis.net/gml}AbstractGMLType
    
    # Element {http://www.opengis.net/citygml/building/1.0}lod3MultiSurface uses Python identifier lod3MultiSurface
    __lod3MultiSurface = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiSurface'), 'lod3MultiSurface', '__httpwww_opengis_netcitygmlbuilding1_0_AbstractBuildingType_httpwww_opengis_netcitygmlbuilding1_0lod3MultiSurface', False)

    
    lod3MultiSurface = property(__lod3MultiSurface.value, __lod3MultiSurface.set, None, None)

    
    # Element {http://www.opengis.net/citygml/building/1.0}storeysAboveGround uses Python identifier storeysAboveGround
    __storeysAboveGround = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'storeysAboveGround'), 'storeysAboveGround', '__httpwww_opengis_netcitygmlbuilding1_0_AbstractBuildingType_httpwww_opengis_netcitygmlbuilding1_0storeysAboveGround', False)

    
    storeysAboveGround = property(__storeysAboveGround.value, __storeysAboveGround.set, None, None)

    
    # Element {http://www.opengis.net/citygml/building/1.0}lod3MultiCurve uses Python identifier lod3MultiCurve
    __lod3MultiCurve = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiCurve'), 'lod3MultiCurve', '__httpwww_opengis_netcitygmlbuilding1_0_AbstractBuildingType_httpwww_opengis_netcitygmlbuilding1_0lod3MultiCurve', False)

    
    lod3MultiCurve = property(__lod3MultiCurve.value, __lod3MultiCurve.set, None, None)

    
    # Element {http://www.opengis.net/citygml/building/1.0}storeysBelowGround uses Python identifier storeysBelowGround
    __storeysBelowGround = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'storeysBelowGround'), 'storeysBelowGround', '__httpwww_opengis_netcitygmlbuilding1_0_AbstractBuildingType_httpwww_opengis_netcitygmlbuilding1_0storeysBelowGround', False)

    
    storeysBelowGround = property(__storeysBelowGround.value, __storeysBelowGround.set, None, None)

    
    # Element {http://www.opengis.net/citygml/building/1.0}lod3TerrainIntersection uses Python identifier lod3TerrainIntersection
    __lod3TerrainIntersection = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'lod3TerrainIntersection'), 'lod3TerrainIntersection', '__httpwww_opengis_netcitygmlbuilding1_0_AbstractBuildingType_httpwww_opengis_netcitygmlbuilding1_0lod3TerrainIntersection', False)

    
    lod3TerrainIntersection = property(__lod3TerrainIntersection.value, __lod3TerrainIntersection.set, None, None)

    
    # Element {http://www.opengis.net/citygml/building/1.0}storeyHeightsAboveGround uses Python identifier storeyHeightsAboveGround
    __storeyHeightsAboveGround = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'storeyHeightsAboveGround'), 'storeyHeightsAboveGround', '__httpwww_opengis_netcitygmlbuilding1_0_AbstractBuildingType_httpwww_opengis_netcitygmlbuilding1_0storeyHeightsAboveGround', False)

    
    storeyHeightsAboveGround = property(__storeyHeightsAboveGround.value, __storeyHeightsAboveGround.set, None, None)

    
    # Element {http://www.opengis.net/citygml/building/1.0}class uses Python identifier class_
    __class = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'class'), 'class_', '__httpwww_opengis_netcitygmlbuilding1_0_AbstractBuildingType_httpwww_opengis_netcitygmlbuilding1_0class', False)

    
    class_ = property(__class.value, __class.set, None, None)

    
    # Element {http://www.opengis.net/citygml/building/1.0}lod4Solid uses Python identifier lod4Solid
    __lod4Solid = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'lod4Solid'), 'lod4Solid', '__httpwww_opengis_netcitygmlbuilding1_0_AbstractBuildingType_httpwww_opengis_netcitygmlbuilding1_0lod4Solid', False)

    
    lod4Solid = property(__lod4Solid.value, __lod4Solid.set, None, None)

    
    # Element {http://www.opengis.net/citygml/building/1.0}storeyHeightsBelowGround uses Python identifier storeyHeightsBelowGround
    __storeyHeightsBelowGround = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'storeyHeightsBelowGround'), 'storeyHeightsBelowGround', '__httpwww_opengis_netcitygmlbuilding1_0_AbstractBuildingType_httpwww_opengis_netcitygmlbuilding1_0storeyHeightsBelowGround', False)

    
    storeyHeightsBelowGround = property(__storeyHeightsBelowGround.value, __storeyHeightsBelowGround.set, None, None)

    
    # Element generalizesTo ({http://www.opengis.net/citygml/1.0}generalizesTo) inherited from {http://www.opengis.net/citygml/1.0}AbstractCityObjectType
    
    # Element {http://www.opengis.net/citygml/building/1.0}lod4MultiSurface uses Python identifier lod4MultiSurface
    __lod4MultiSurface = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiSurface'), 'lod4MultiSurface', '__httpwww_opengis_netcitygmlbuilding1_0_AbstractBuildingType_httpwww_opengis_netcitygmlbuilding1_0lod4MultiSurface', False)

    
    lod4MultiSurface = property(__lod4MultiSurface.value, __lod4MultiSurface.set, None, None)

    
    # Element {http://www.opengis.net/citygml/building/1.0}lod1Solid uses Python identifier lod1Solid
    __lod1Solid = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'lod1Solid'), 'lod1Solid', '__httpwww_opengis_netcitygmlbuilding1_0_AbstractBuildingType_httpwww_opengis_netcitygmlbuilding1_0lod1Solid', False)

    
    lod1Solid = property(__lod1Solid.value, __lod1Solid.set, None, None)

    
    # Element {http://www.opengis.net/citygml/building/1.0}outerBuildingInstallation uses Python identifier outerBuildingInstallation
    __outerBuildingInstallation = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'outerBuildingInstallation'), 'outerBuildingInstallation', '__httpwww_opengis_netcitygmlbuilding1_0_AbstractBuildingType_httpwww_opengis_netcitygmlbuilding1_0outerBuildingInstallation', True)

    
    outerBuildingInstallation = property(__outerBuildingInstallation.value, __outerBuildingInstallation.set, None, None)

    
    # Element {http://www.opengis.net/citygml/building/1.0}lod4MultiCurve uses Python identifier lod4MultiCurve
    __lod4MultiCurve = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiCurve'), 'lod4MultiCurve', '__httpwww_opengis_netcitygmlbuilding1_0_AbstractBuildingType_httpwww_opengis_netcitygmlbuilding1_0lod4MultiCurve', False)

    
    lod4MultiCurve = property(__lod4MultiCurve.value, __lod4MultiCurve.set, None, None)

    
    # Element {http://www.opengis.net/citygml/building/1.0}lod1MultiSurface uses Python identifier lod1MultiSurface
    __lod1MultiSurface = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'lod1MultiSurface'), 'lod1MultiSurface', '__httpwww_opengis_netcitygmlbuilding1_0_AbstractBuildingType_httpwww_opengis_netcitygmlbuilding1_0lod1MultiSurface', False)

    
    lod1MultiSurface = property(__lod1MultiSurface.value, __lod1MultiSurface.set, None, None)

    
    # Element {http://www.opengis.net/citygml/building/1.0}lod4TerrainIntersection uses Python identifier lod4TerrainIntersection
    __lod4TerrainIntersection = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'lod4TerrainIntersection'), 'lod4TerrainIntersection', '__httpwww_opengis_netcitygmlbuilding1_0_AbstractBuildingType_httpwww_opengis_netcitygmlbuilding1_0lod4TerrainIntersection', False)

    
    lod4TerrainIntersection = property(__lod4TerrainIntersection.value, __lod4TerrainIntersection.set, None, None)

    
    # Element GenericApplicationPropertyOfCityObject ({http://www.opengis.net/citygml/1.0}_GenericApplicationPropertyOfCityObject) inherited from {http://www.opengis.net/citygml/1.0}AbstractCityObjectType
    
    # Element {http://www.opengis.net/citygml/building/1.0}lod1TerrainIntersection uses Python identifier lod1TerrainIntersection
    __lod1TerrainIntersection = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'lod1TerrainIntersection'), 'lod1TerrainIntersection', '__httpwww_opengis_netcitygmlbuilding1_0_AbstractBuildingType_httpwww_opengis_netcitygmlbuilding1_0lod1TerrainIntersection', False)

    
    lod1TerrainIntersection = property(__lod1TerrainIntersection.value, __lod1TerrainIntersection.set, None, None)

    
    # Element {http://www.opengis.net/citygml/building/1.0}_GenericApplicationPropertyOfAbstractBuilding uses Python identifier GenericApplicationPropertyOfAbstractBuilding
    __GenericApplicationPropertyOfAbstractBuilding = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfAbstractBuilding'), 'GenericApplicationPropertyOfAbstractBuilding', '__httpwww_opengis_netcitygmlbuilding1_0_AbstractBuildingType_httpwww_opengis_netcitygmlbuilding1_0_GenericApplicationPropertyOfAbstractBuilding', True)

    
    GenericApplicationPropertyOfAbstractBuilding = property(__GenericApplicationPropertyOfAbstractBuilding.value, __GenericApplicationPropertyOfAbstractBuilding.set, None, None)

    
    # Element {http://www.opengis.net/citygml/building/1.0}lod2Solid uses Python identifier lod2Solid
    __lod2Solid = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'lod2Solid'), 'lod2Solid', '__httpwww_opengis_netcitygmlbuilding1_0_AbstractBuildingType_httpwww_opengis_netcitygmlbuilding1_0lod2Solid', False)

    
    lod2Solid = property(__lod2Solid.value, __lod2Solid.set, None, None)

    
    # Element description ({http://www.opengis.net/gml}description) inherited from {http://www.opengis.net/gml}AbstractGMLType
    
    # Element {http://www.opengis.net/citygml/building/1.0}consistsOfBuildingPart uses Python identifier consistsOfBuildingPart
    __consistsOfBuildingPart = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'consistsOfBuildingPart'), 'consistsOfBuildingPart', '__httpwww_opengis_netcitygmlbuilding1_0_AbstractBuildingType_httpwww_opengis_netcitygmlbuilding1_0consistsOfBuildingPart', True)

    
    consistsOfBuildingPart = property(__consistsOfBuildingPart.value, __consistsOfBuildingPart.set, None, None)

    
    # Element creationDate ({http://www.opengis.net/citygml/1.0}creationDate) inherited from {http://www.opengis.net/citygml/1.0}AbstractCityObjectType
    
    # Element {http://www.opengis.net/citygml/building/1.0}lod2MultiSurface uses Python identifier lod2MultiSurface
    __lod2MultiSurface = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'lod2MultiSurface'), 'lod2MultiSurface', '__httpwww_opengis_netcitygmlbuilding1_0_AbstractBuildingType_httpwww_opengis_netcitygmlbuilding1_0lod2MultiSurface', False)

    
    lod2MultiSurface = property(__lod2MultiSurface.value, __lod2MultiSurface.set, None, None)

    
    # Element {http://www.opengis.net/citygml/building/1.0}address uses Python identifier address
    __address = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'address'), 'address', '__httpwww_opengis_netcitygmlbuilding1_0_AbstractBuildingType_httpwww_opengis_netcitygmlbuilding1_0address', True)

    
    address = property(__address.value, __address.set, None, None)

    
    # Element {http://www.opengis.net/citygml/building/1.0}lod2MultiCurve uses Python identifier lod2MultiCurve
    __lod2MultiCurve = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'lod2MultiCurve'), 'lod2MultiCurve', '__httpwww_opengis_netcitygmlbuilding1_0_AbstractBuildingType_httpwww_opengis_netcitygmlbuilding1_0lod2MultiCurve', False)

    
    lod2MultiCurve = property(__lod2MultiCurve.value, __lod2MultiCurve.set, None, None)

    
    # Element {http://www.opengis.net/citygml/building/1.0}interiorRoom uses Python identifier interiorRoom
    __interiorRoom = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'interiorRoom'), 'interiorRoom', '__httpwww_opengis_netcitygmlbuilding1_0_AbstractBuildingType_httpwww_opengis_netcitygmlbuilding1_0interiorRoom', True)

    
    interiorRoom = property(__interiorRoom.value, __interiorRoom.set, None, None)

    
    # Element GenericApplicationPropertyOfSite ({http://www.opengis.net/citygml/1.0}_GenericApplicationPropertyOfSite) inherited from {http://www.opengis.net/citygml/1.0}AbstractSiteType
    
    # Element {http://www.opengis.net/citygml/building/1.0}lod2TerrainIntersection uses Python identifier lod2TerrainIntersection
    __lod2TerrainIntersection = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'lod2TerrainIntersection'), 'lod2TerrainIntersection', '__httpwww_opengis_netcitygmlbuilding1_0_AbstractBuildingType_httpwww_opengis_netcitygmlbuilding1_0lod2TerrainIntersection', False)

    
    lod2TerrainIntersection = property(__lod2TerrainIntersection.value, __lod2TerrainIntersection.set, None, None)

    
    # Element {http://www.opengis.net/citygml/building/1.0}yearOfConstruction uses Python identifier yearOfConstruction
    __yearOfConstruction = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'yearOfConstruction'), 'yearOfConstruction', '__httpwww_opengis_netcitygmlbuilding1_0_AbstractBuildingType_httpwww_opengis_netcitygmlbuilding1_0yearOfConstruction', False)

    
    yearOfConstruction = property(__yearOfConstruction.value, __yearOfConstruction.set, None, None)

    
    # Element externalReference ({http://www.opengis.net/citygml/1.0}externalReference) inherited from {http://www.opengis.net/citygml/1.0}AbstractCityObjectType
    
    # Element terminationDate ({http://www.opengis.net/citygml/1.0}terminationDate) inherited from {http://www.opengis.net/citygml/1.0}AbstractCityObjectType
    
    # Element {http://www.opengis.net/citygml/building/1.0}usage uses Python identifier usage
    __usage = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'usage'), 'usage', '__httpwww_opengis_netcitygmlbuilding1_0_AbstractBuildingType_httpwww_opengis_netcitygmlbuilding1_0usage', True)

    
    usage = property(__usage.value, __usage.set, None, None)

    
    # Element name ({http://www.opengis.net/gml}name) inherited from {http://www.opengis.net/gml}AbstractGMLType
    
    # Element {http://www.opengis.net/citygml/building/1.0}interiorBuildingInstallation uses Python identifier interiorBuildingInstallation
    __interiorBuildingInstallation = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'interiorBuildingInstallation'), 'interiorBuildingInstallation', '__httpwww_opengis_netcitygmlbuilding1_0_AbstractBuildingType_httpwww_opengis_netcitygmlbuilding1_0interiorBuildingInstallation', True)

    
    interiorBuildingInstallation = property(__interiorBuildingInstallation.value, __interiorBuildingInstallation.set, None, None)

    
    # Element boundedBy ({http://www.opengis.net/gml}boundedBy) inherited from {http://www.opengis.net/gml}AbstractFeatureType
    
    # Attribute id inherited from {http://www.opengis.net/gml}AbstractGMLType

    _ElementMap = pyxb.bundles.opengis.citygml.base.AbstractSiteType._ElementMap.copy()
    _ElementMap.update({
        __yearOfDemolition.name() : __yearOfDemolition,
        __boundedBy_.name() : __boundedBy_,
        __roofType.name() : __roofType,
        __function.name() : __function,
        __lod3Solid.name() : __lod3Solid,
        __measuredHeight.name() : __measuredHeight,
        __lod3MultiSurface.name() : __lod3MultiSurface,
        __storeysAboveGround.name() : __storeysAboveGround,
        __lod3MultiCurve.name() : __lod3MultiCurve,
        __storeysBelowGround.name() : __storeysBelowGround,
        __lod3TerrainIntersection.name() : __lod3TerrainIntersection,
        __storeyHeightsAboveGround.name() : __storeyHeightsAboveGround,
        __class.name() : __class,
        __lod4Solid.name() : __lod4Solid,
        __storeyHeightsBelowGround.name() : __storeyHeightsBelowGround,
        __lod4MultiSurface.name() : __lod4MultiSurface,
        __lod1Solid.name() : __lod1Solid,
        __outerBuildingInstallation.name() : __outerBuildingInstallation,
        __lod4MultiCurve.name() : __lod4MultiCurve,
        __lod1MultiSurface.name() : __lod1MultiSurface,
        __lod4TerrainIntersection.name() : __lod4TerrainIntersection,
        __lod1TerrainIntersection.name() : __lod1TerrainIntersection,
        __GenericApplicationPropertyOfAbstractBuilding.name() : __GenericApplicationPropertyOfAbstractBuilding,
        __lod2Solid.name() : __lod2Solid,
        __consistsOfBuildingPart.name() : __consistsOfBuildingPart,
        __lod2MultiSurface.name() : __lod2MultiSurface,
        __address.name() : __address,
        __lod2MultiCurve.name() : __lod2MultiCurve,
        __interiorRoom.name() : __interiorRoom,
        __lod2TerrainIntersection.name() : __lod2TerrainIntersection,
        __yearOfConstruction.name() : __yearOfConstruction,
        __usage.name() : __usage,
        __interiorBuildingInstallation.name() : __interiorBuildingInstallation
    })
    _AttributeMap = pyxb.bundles.opengis.citygml.base.AbstractSiteType._AttributeMap.copy()
    _AttributeMap.update({
        
    })
Namespace.addCategoryObject('typeBinding', u'AbstractBuildingType', AbstractBuildingType)


# Complex type IntBuildingInstallationType with content type ELEMENT_ONLY
class IntBuildingInstallationType (pyxb.bundles.opengis.citygml.base.AbstractCityObjectType):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'IntBuildingInstallationType')
    # Base type is pyxb.bundles.opengis.citygml.base.AbstractCityObjectType
    
    # Element {http://www.opengis.net/citygml/building/1.0}lod4Geometry uses Python identifier lod4Geometry
    __lod4Geometry = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'lod4Geometry'), 'lod4Geometry', '__httpwww_opengis_netcitygmlbuilding1_0_IntBuildingInstallationType_httpwww_opengis_netcitygmlbuilding1_0lod4Geometry', False)

    
    lod4Geometry = property(__lod4Geometry.value, __lod4Geometry.set, None, None)

    
    # Element description ({http://www.opengis.net/gml}description) inherited from {http://www.opengis.net/gml}AbstractGMLType
    
    # Element location ({http://www.opengis.net/gml}location) inherited from {http://www.opengis.net/gml}AbstractFeatureType
    
    # Element {http://www.opengis.net/citygml/building/1.0}class uses Python identifier class_
    __class = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'class'), 'class_', '__httpwww_opengis_netcitygmlbuilding1_0_IntBuildingInstallationType_httpwww_opengis_netcitygmlbuilding1_0class', False)

    
    class_ = property(__class.value, __class.set, None, None)

    
    # Element externalReference ({http://www.opengis.net/citygml/1.0}externalReference) inherited from {http://www.opengis.net/citygml/1.0}AbstractCityObjectType
    
    # Element GenericApplicationPropertyOfCityObject ({http://www.opengis.net/citygml/1.0}_GenericApplicationPropertyOfCityObject) inherited from {http://www.opengis.net/citygml/1.0}AbstractCityObjectType
    
    # Element generalizesTo ({http://www.opengis.net/citygml/1.0}generalizesTo) inherited from {http://www.opengis.net/citygml/1.0}AbstractCityObjectType
    
    # Element terminationDate ({http://www.opengis.net/citygml/1.0}terminationDate) inherited from {http://www.opengis.net/citygml/1.0}AbstractCityObjectType
    
    # Element {http://www.opengis.net/citygml/building/1.0}function uses Python identifier function
    __function = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'function'), 'function', '__httpwww_opengis_netcitygmlbuilding1_0_IntBuildingInstallationType_httpwww_opengis_netcitygmlbuilding1_0function', True)

    
    function = property(__function.value, __function.set, None, None)

    
    # Element boundedBy ({http://www.opengis.net/gml}boundedBy) inherited from {http://www.opengis.net/gml}AbstractFeatureType
    
    # Element name ({http://www.opengis.net/gml}name) inherited from {http://www.opengis.net/gml}AbstractGMLType
    
    # Element creationDate ({http://www.opengis.net/citygml/1.0}creationDate) inherited from {http://www.opengis.net/citygml/1.0}AbstractCityObjectType
    
    # Element metaDataProperty ({http://www.opengis.net/gml}metaDataProperty) inherited from {http://www.opengis.net/gml}AbstractGMLType
    
    # Element {http://www.opengis.net/citygml/building/1.0}_GenericApplicationPropertyOfIntBuildingInstallation uses Python identifier GenericApplicationPropertyOfIntBuildingInstallation
    __GenericApplicationPropertyOfIntBuildingInstallation = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfIntBuildingInstallation'), 'GenericApplicationPropertyOfIntBuildingInstallation', '__httpwww_opengis_netcitygmlbuilding1_0_IntBuildingInstallationType_httpwww_opengis_netcitygmlbuilding1_0_GenericApplicationPropertyOfIntBuildingInstallation', True)

    
    GenericApplicationPropertyOfIntBuildingInstallation = property(__GenericApplicationPropertyOfIntBuildingInstallation.value, __GenericApplicationPropertyOfIntBuildingInstallation.set, None, None)

    
    # Element {http://www.opengis.net/citygml/building/1.0}usage uses Python identifier usage
    __usage = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'usage'), 'usage', '__httpwww_opengis_netcitygmlbuilding1_0_IntBuildingInstallationType_httpwww_opengis_netcitygmlbuilding1_0usage', True)

    
    usage = property(__usage.value, __usage.set, None, None)

    
    # Attribute id inherited from {http://www.opengis.net/gml}AbstractGMLType

    _ElementMap = pyxb.bundles.opengis.citygml.base.AbstractCityObjectType._ElementMap.copy()
    _ElementMap.update({
        __lod4Geometry.name() : __lod4Geometry,
        __class.name() : __class,
        __function.name() : __function,
        __GenericApplicationPropertyOfIntBuildingInstallation.name() : __GenericApplicationPropertyOfIntBuildingInstallation,
        __usage.name() : __usage
    })
    _AttributeMap = pyxb.bundles.opengis.citygml.base.AbstractCityObjectType._AttributeMap.copy()
    _AttributeMap.update({
        
    })
Namespace.addCategoryObject('typeBinding', u'IntBuildingInstallationType', IntBuildingInstallationType)


# Complex type FloorSurfaceType with content type ELEMENT_ONLY
class FloorSurfaceType (AbstractBoundarySurfaceType):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'FloorSurfaceType')
    # Base type is AbstractBoundarySurfaceType
    
    # Element location ({http://www.opengis.net/gml}location) inherited from {http://www.opengis.net/gml}AbstractFeatureType
    
    # Element opening ({http://www.opengis.net/citygml/building/1.0}opening) inherited from {http://www.opengis.net/citygml/building/1.0}AbstractBoundarySurfaceType
    
    # Element lod4MultiSurface ({http://www.opengis.net/citygml/building/1.0}lod4MultiSurface) inherited from {http://www.opengis.net/citygml/building/1.0}AbstractBoundarySurfaceType
    
    # Element description ({http://www.opengis.net/gml}description) inherited from {http://www.opengis.net/gml}AbstractGMLType
    
    # Element generalizesTo ({http://www.opengis.net/citygml/1.0}generalizesTo) inherited from {http://www.opengis.net/citygml/1.0}AbstractCityObjectType
    
    # Element GenericApplicationPropertyOfCityObject ({http://www.opengis.net/citygml/1.0}_GenericApplicationPropertyOfCityObject) inherited from {http://www.opengis.net/citygml/1.0}AbstractCityObjectType
    
    # Element terminationDate ({http://www.opengis.net/citygml/1.0}terminationDate) inherited from {http://www.opengis.net/citygml/1.0}AbstractCityObjectType
    
    # Element name ({http://www.opengis.net/gml}name) inherited from {http://www.opengis.net/gml}AbstractGMLType
    
    # Element externalReference ({http://www.opengis.net/citygml/1.0}externalReference) inherited from {http://www.opengis.net/citygml/1.0}AbstractCityObjectType
    
    # Element lod2MultiSurface ({http://www.opengis.net/citygml/building/1.0}lod2MultiSurface) inherited from {http://www.opengis.net/citygml/building/1.0}AbstractBoundarySurfaceType
    
    # Element GenericApplicationPropertyOfBoundarySurface ({http://www.opengis.net/citygml/building/1.0}_GenericApplicationPropertyOfBoundarySurface) inherited from {http://www.opengis.net/citygml/building/1.0}AbstractBoundarySurfaceType
    
    # Element lod3MultiSurface ({http://www.opengis.net/citygml/building/1.0}lod3MultiSurface) inherited from {http://www.opengis.net/citygml/building/1.0}AbstractBoundarySurfaceType
    
    # Element metaDataProperty ({http://www.opengis.net/gml}metaDataProperty) inherited from {http://www.opengis.net/gml}AbstractGMLType
    
    # Element creationDate ({http://www.opengis.net/citygml/1.0}creationDate) inherited from {http://www.opengis.net/citygml/1.0}AbstractCityObjectType
    
    # Element {http://www.opengis.net/citygml/building/1.0}_GenericApplicationPropertyOfFloorSurface uses Python identifier GenericApplicationPropertyOfFloorSurface
    __GenericApplicationPropertyOfFloorSurface = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfFloorSurface'), 'GenericApplicationPropertyOfFloorSurface', '__httpwww_opengis_netcitygmlbuilding1_0_FloorSurfaceType_httpwww_opengis_netcitygmlbuilding1_0_GenericApplicationPropertyOfFloorSurface', True)

    
    GenericApplicationPropertyOfFloorSurface = property(__GenericApplicationPropertyOfFloorSurface.value, __GenericApplicationPropertyOfFloorSurface.set, None, None)

    
    # Element boundedBy ({http://www.opengis.net/gml}boundedBy) inherited from {http://www.opengis.net/gml}AbstractFeatureType
    
    # Attribute id inherited from {http://www.opengis.net/gml}AbstractGMLType

    _ElementMap = AbstractBoundarySurfaceType._ElementMap.copy()
    _ElementMap.update({
        __GenericApplicationPropertyOfFloorSurface.name() : __GenericApplicationPropertyOfFloorSurface
    })
    _AttributeMap = AbstractBoundarySurfaceType._AttributeMap.copy()
    _AttributeMap.update({
        
    })
Namespace.addCategoryObject('typeBinding', u'FloorSurfaceType', FloorSurfaceType)


# Complex type BuildingType with content type ELEMENT_ONLY
class BuildingType (AbstractBuildingType):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'BuildingType')
    # Base type is AbstractBuildingType
    
    # Element yearOfDemolition ({http://www.opengis.net/citygml/building/1.0}yearOfDemolition) inherited from {http://www.opengis.net/citygml/building/1.0}AbstractBuildingType
    
    # Element location ({http://www.opengis.net/gml}location) inherited from {http://www.opengis.net/gml}AbstractFeatureType
    
    # Element boundedBy_ ({http://www.opengis.net/citygml/building/1.0}boundedBy) inherited from {http://www.opengis.net/citygml/building/1.0}AbstractBuildingType
    
    # Element roofType ({http://www.opengis.net/citygml/building/1.0}roofType) inherited from {http://www.opengis.net/citygml/building/1.0}AbstractBuildingType
    
    # Element function ({http://www.opengis.net/citygml/building/1.0}function) inherited from {http://www.opengis.net/citygml/building/1.0}AbstractBuildingType
    
    # Element lod3Solid ({http://www.opengis.net/citygml/building/1.0}lod3Solid) inherited from {http://www.opengis.net/citygml/building/1.0}AbstractBuildingType
    
    # Element measuredHeight ({http://www.opengis.net/citygml/building/1.0}measuredHeight) inherited from {http://www.opengis.net/citygml/building/1.0}AbstractBuildingType
    
    # Element metaDataProperty ({http://www.opengis.net/gml}metaDataProperty) inherited from {http://www.opengis.net/gml}AbstractGMLType
    
    # Element lod3MultiSurface ({http://www.opengis.net/citygml/building/1.0}lod3MultiSurface) inherited from {http://www.opengis.net/citygml/building/1.0}AbstractBuildingType
    
    # Element storeysAboveGround ({http://www.opengis.net/citygml/building/1.0}storeysAboveGround) inherited from {http://www.opengis.net/citygml/building/1.0}AbstractBuildingType
    
    # Element lod3MultiCurve ({http://www.opengis.net/citygml/building/1.0}lod3MultiCurve) inherited from {http://www.opengis.net/citygml/building/1.0}AbstractBuildingType
    
    # Element storeysBelowGround ({http://www.opengis.net/citygml/building/1.0}storeysBelowGround) inherited from {http://www.opengis.net/citygml/building/1.0}AbstractBuildingType
    
    # Element lod4Solid ({http://www.opengis.net/citygml/building/1.0}lod4Solid) inherited from {http://www.opengis.net/citygml/building/1.0}AbstractBuildingType
    
    # Element lod3TerrainIntersection ({http://www.opengis.net/citygml/building/1.0}lod3TerrainIntersection) inherited from {http://www.opengis.net/citygml/building/1.0}AbstractBuildingType
    
    # Element storeyHeightsAboveGround ({http://www.opengis.net/citygml/building/1.0}storeyHeightsAboveGround) inherited from {http://www.opengis.net/citygml/building/1.0}AbstractBuildingType
    
    # Element class_ ({http://www.opengis.net/citygml/building/1.0}class) inherited from {http://www.opengis.net/citygml/building/1.0}AbstractBuildingType
    
    # Element {http://www.opengis.net/citygml/building/1.0}_GenericApplicationPropertyOfBuilding uses Python identifier GenericApplicationPropertyOfBuilding
    __GenericApplicationPropertyOfBuilding = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfBuilding'), 'GenericApplicationPropertyOfBuilding', '__httpwww_opengis_netcitygmlbuilding1_0_BuildingType_httpwww_opengis_netcitygmlbuilding1_0_GenericApplicationPropertyOfBuilding', True)

    
    GenericApplicationPropertyOfBuilding = property(__GenericApplicationPropertyOfBuilding.value, __GenericApplicationPropertyOfBuilding.set, None, None)

    
    # Element storeyHeightsBelowGround ({http://www.opengis.net/citygml/building/1.0}storeyHeightsBelowGround) inherited from {http://www.opengis.net/citygml/building/1.0}AbstractBuildingType
    
    # Element generalizesTo ({http://www.opengis.net/citygml/1.0}generalizesTo) inherited from {http://www.opengis.net/citygml/1.0}AbstractCityObjectType
    
    # Element lod4MultiSurface ({http://www.opengis.net/citygml/building/1.0}lod4MultiSurface) inherited from {http://www.opengis.net/citygml/building/1.0}AbstractBuildingType
    
    # Element lod1Solid ({http://www.opengis.net/citygml/building/1.0}lod1Solid) inherited from {http://www.opengis.net/citygml/building/1.0}AbstractBuildingType
    
    # Element outerBuildingInstallation ({http://www.opengis.net/citygml/building/1.0}outerBuildingInstallation) inherited from {http://www.opengis.net/citygml/building/1.0}AbstractBuildingType
    
    # Element lod4MultiCurve ({http://www.opengis.net/citygml/building/1.0}lod4MultiCurve) inherited from {http://www.opengis.net/citygml/building/1.0}AbstractBuildingType
    
    # Element lod1MultiSurface ({http://www.opengis.net/citygml/building/1.0}lod1MultiSurface) inherited from {http://www.opengis.net/citygml/building/1.0}AbstractBuildingType
    
    # Element lod4TerrainIntersection ({http://www.opengis.net/citygml/building/1.0}lod4TerrainIntersection) inherited from {http://www.opengis.net/citygml/building/1.0}AbstractBuildingType
    
    # Element GenericApplicationPropertyOfCityObject ({http://www.opengis.net/citygml/1.0}_GenericApplicationPropertyOfCityObject) inherited from {http://www.opengis.net/citygml/1.0}AbstractCityObjectType
    
    # Element lod1TerrainIntersection ({http://www.opengis.net/citygml/building/1.0}lod1TerrainIntersection) inherited from {http://www.opengis.net/citygml/building/1.0}AbstractBuildingType
    
    # Element GenericApplicationPropertyOfAbstractBuilding ({http://www.opengis.net/citygml/building/1.0}_GenericApplicationPropertyOfAbstractBuilding) inherited from {http://www.opengis.net/citygml/building/1.0}AbstractBuildingType
    
    # Element lod2Solid ({http://www.opengis.net/citygml/building/1.0}lod2Solid) inherited from {http://www.opengis.net/citygml/building/1.0}AbstractBuildingType
    
    # Element description ({http://www.opengis.net/gml}description) inherited from {http://www.opengis.net/gml}AbstractGMLType
    
    # Element consistsOfBuildingPart ({http://www.opengis.net/citygml/building/1.0}consistsOfBuildingPart) inherited from {http://www.opengis.net/citygml/building/1.0}AbstractBuildingType
    
    # Element creationDate ({http://www.opengis.net/citygml/1.0}creationDate) inherited from {http://www.opengis.net/citygml/1.0}AbstractCityObjectType
    
    # Element lod2MultiSurface ({http://www.opengis.net/citygml/building/1.0}lod2MultiSurface) inherited from {http://www.opengis.net/citygml/building/1.0}AbstractBuildingType
    
    # Element address ({http://www.opengis.net/citygml/building/1.0}address) inherited from {http://www.opengis.net/citygml/building/1.0}AbstractBuildingType
    
    # Element lod2MultiCurve ({http://www.opengis.net/citygml/building/1.0}lod2MultiCurve) inherited from {http://www.opengis.net/citygml/building/1.0}AbstractBuildingType
    
    # Element interiorRoom ({http://www.opengis.net/citygml/building/1.0}interiorRoom) inherited from {http://www.opengis.net/citygml/building/1.0}AbstractBuildingType
    
    # Element GenericApplicationPropertyOfSite ({http://www.opengis.net/citygml/1.0}_GenericApplicationPropertyOfSite) inherited from {http://www.opengis.net/citygml/1.0}AbstractSiteType
    
    # Element lod2TerrainIntersection ({http://www.opengis.net/citygml/building/1.0}lod2TerrainIntersection) inherited from {http://www.opengis.net/citygml/building/1.0}AbstractBuildingType
    
    # Element yearOfConstruction ({http://www.opengis.net/citygml/building/1.0}yearOfConstruction) inherited from {http://www.opengis.net/citygml/building/1.0}AbstractBuildingType
    
    # Element externalReference ({http://www.opengis.net/citygml/1.0}externalReference) inherited from {http://www.opengis.net/citygml/1.0}AbstractCityObjectType
    
    # Element terminationDate ({http://www.opengis.net/citygml/1.0}terminationDate) inherited from {http://www.opengis.net/citygml/1.0}AbstractCityObjectType
    
    # Element usage ({http://www.opengis.net/citygml/building/1.0}usage) inherited from {http://www.opengis.net/citygml/building/1.0}AbstractBuildingType
    
    # Element name ({http://www.opengis.net/gml}name) inherited from {http://www.opengis.net/gml}AbstractGMLType
    
    # Element interiorBuildingInstallation ({http://www.opengis.net/citygml/building/1.0}interiorBuildingInstallation) inherited from {http://www.opengis.net/citygml/building/1.0}AbstractBuildingType
    
    # Element boundedBy ({http://www.opengis.net/gml}boundedBy) inherited from {http://www.opengis.net/gml}AbstractFeatureType
    
    # Attribute id inherited from {http://www.opengis.net/gml}AbstractGMLType

    _ElementMap = AbstractBuildingType._ElementMap.copy()
    _ElementMap.update({
        __GenericApplicationPropertyOfBuilding.name() : __GenericApplicationPropertyOfBuilding
    })
    _AttributeMap = AbstractBuildingType._AttributeMap.copy()
    _AttributeMap.update({
        
    })
Namespace.addCategoryObject('typeBinding', u'BuildingType', BuildingType)


# Complex type WallSurfaceType with content type ELEMENT_ONLY
class WallSurfaceType (AbstractBoundarySurfaceType):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'WallSurfaceType')
    # Base type is AbstractBoundarySurfaceType
    
    # Element lod4MultiSurface ({http://www.opengis.net/citygml/building/1.0}lod4MultiSurface) inherited from {http://www.opengis.net/citygml/building/1.0}AbstractBoundarySurfaceType
    
    # Element opening ({http://www.opengis.net/citygml/building/1.0}opening) inherited from {http://www.opengis.net/citygml/building/1.0}AbstractBoundarySurfaceType
    
    # Element creationDate ({http://www.opengis.net/citygml/1.0}creationDate) inherited from {http://www.opengis.net/citygml/1.0}AbstractCityObjectType
    
    # Element location ({http://www.opengis.net/gml}location) inherited from {http://www.opengis.net/gml}AbstractFeatureType
    
    # Element description ({http://www.opengis.net/gml}description) inherited from {http://www.opengis.net/gml}AbstractGMLType
    
    # Element generalizesTo ({http://www.opengis.net/citygml/1.0}generalizesTo) inherited from {http://www.opengis.net/citygml/1.0}AbstractCityObjectType
    
    # Element GenericApplicationPropertyOfCityObject ({http://www.opengis.net/citygml/1.0}_GenericApplicationPropertyOfCityObject) inherited from {http://www.opengis.net/citygml/1.0}AbstractCityObjectType
    
    # Element terminationDate ({http://www.opengis.net/citygml/1.0}terminationDate) inherited from {http://www.opengis.net/citygml/1.0}AbstractCityObjectType
    
    # Element name ({http://www.opengis.net/gml}name) inherited from {http://www.opengis.net/gml}AbstractGMLType
    
    # Element externalReference ({http://www.opengis.net/citygml/1.0}externalReference) inherited from {http://www.opengis.net/citygml/1.0}AbstractCityObjectType
    
    # Element lod2MultiSurface ({http://www.opengis.net/citygml/building/1.0}lod2MultiSurface) inherited from {http://www.opengis.net/citygml/building/1.0}AbstractBoundarySurfaceType
    
    # Element GenericApplicationPropertyOfBoundarySurface ({http://www.opengis.net/citygml/building/1.0}_GenericApplicationPropertyOfBoundarySurface) inherited from {http://www.opengis.net/citygml/building/1.0}AbstractBoundarySurfaceType
    
    # Element lod3MultiSurface ({http://www.opengis.net/citygml/building/1.0}lod3MultiSurface) inherited from {http://www.opengis.net/citygml/building/1.0}AbstractBoundarySurfaceType
    
    # Element {http://www.opengis.net/citygml/building/1.0}_GenericApplicationPropertyOfWallSurface uses Python identifier GenericApplicationPropertyOfWallSurface
    __GenericApplicationPropertyOfWallSurface = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfWallSurface'), 'GenericApplicationPropertyOfWallSurface', '__httpwww_opengis_netcitygmlbuilding1_0_WallSurfaceType_httpwww_opengis_netcitygmlbuilding1_0_GenericApplicationPropertyOfWallSurface', True)

    
    GenericApplicationPropertyOfWallSurface = property(__GenericApplicationPropertyOfWallSurface.value, __GenericApplicationPropertyOfWallSurface.set, None, None)

    
    # Element metaDataProperty ({http://www.opengis.net/gml}metaDataProperty) inherited from {http://www.opengis.net/gml}AbstractGMLType
    
    # Element boundedBy ({http://www.opengis.net/gml}boundedBy) inherited from {http://www.opengis.net/gml}AbstractFeatureType
    
    # Attribute id inherited from {http://www.opengis.net/gml}AbstractGMLType

    _ElementMap = AbstractBoundarySurfaceType._ElementMap.copy()
    _ElementMap.update({
        __GenericApplicationPropertyOfWallSurface.name() : __GenericApplicationPropertyOfWallSurface
    })
    _AttributeMap = AbstractBoundarySurfaceType._AttributeMap.copy()
    _AttributeMap.update({
        
    })
Namespace.addCategoryObject('typeBinding', u'WallSurfaceType', WallSurfaceType)


# Complex type BuildingInstallationType with content type ELEMENT_ONLY
class BuildingInstallationType (pyxb.bundles.opengis.citygml.base.AbstractCityObjectType):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'BuildingInstallationType')
    # Base type is pyxb.bundles.opengis.citygml.base.AbstractCityObjectType
    
    # Element location ({http://www.opengis.net/gml}location) inherited from {http://www.opengis.net/gml}AbstractFeatureType
    
    # Element description ({http://www.opengis.net/gml}description) inherited from {http://www.opengis.net/gml}AbstractGMLType
    
    # Element {http://www.opengis.net/citygml/building/1.0}lod3Geometry uses Python identifier lod3Geometry
    __lod3Geometry = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'lod3Geometry'), 'lod3Geometry', '__httpwww_opengis_netcitygmlbuilding1_0_BuildingInstallationType_httpwww_opengis_netcitygmlbuilding1_0lod3Geometry', False)

    
    lod3Geometry = property(__lod3Geometry.value, __lod3Geometry.set, None, None)

    
    # Element {http://www.opengis.net/citygml/building/1.0}lod2Geometry uses Python identifier lod2Geometry
    __lod2Geometry = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'lod2Geometry'), 'lod2Geometry', '__httpwww_opengis_netcitygmlbuilding1_0_BuildingInstallationType_httpwww_opengis_netcitygmlbuilding1_0lod2Geometry', False)

    
    lod2Geometry = property(__lod2Geometry.value, __lod2Geometry.set, None, None)

    
    # Element terminationDate ({http://www.opengis.net/citygml/1.0}terminationDate) inherited from {http://www.opengis.net/citygml/1.0}AbstractCityObjectType
    
    # Element generalizesTo ({http://www.opengis.net/citygml/1.0}generalizesTo) inherited from {http://www.opengis.net/citygml/1.0}AbstractCityObjectType
    
    # Element GenericApplicationPropertyOfCityObject ({http://www.opengis.net/citygml/1.0}_GenericApplicationPropertyOfCityObject) inherited from {http://www.opengis.net/citygml/1.0}AbstractCityObjectType
    
    # Element externalReference ({http://www.opengis.net/citygml/1.0}externalReference) inherited from {http://www.opengis.net/citygml/1.0}AbstractCityObjectType
    
    # Element {http://www.opengis.net/citygml/building/1.0}class uses Python identifier class_
    __class = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'class'), 'class_', '__httpwww_opengis_netcitygmlbuilding1_0_BuildingInstallationType_httpwww_opengis_netcitygmlbuilding1_0class', False)

    
    class_ = property(__class.value, __class.set, None, None)

    
    # Element boundedBy ({http://www.opengis.net/gml}boundedBy) inherited from {http://www.opengis.net/gml}AbstractFeatureType
    
    # Element {http://www.opengis.net/citygml/building/1.0}_GenericApplicationPropertyOfBuildingInstallation uses Python identifier GenericApplicationPropertyOfBuildingInstallation
    __GenericApplicationPropertyOfBuildingInstallation = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfBuildingInstallation'), 'GenericApplicationPropertyOfBuildingInstallation', '__httpwww_opengis_netcitygmlbuilding1_0_BuildingInstallationType_httpwww_opengis_netcitygmlbuilding1_0_GenericApplicationPropertyOfBuildingInstallation', True)

    
    GenericApplicationPropertyOfBuildingInstallation = property(__GenericApplicationPropertyOfBuildingInstallation.value, __GenericApplicationPropertyOfBuildingInstallation.set, None, None)

    
    # Element name ({http://www.opengis.net/gml}name) inherited from {http://www.opengis.net/gml}AbstractGMLType
    
    # Element metaDataProperty ({http://www.opengis.net/gml}metaDataProperty) inherited from {http://www.opengis.net/gml}AbstractGMLType
    
    # Element creationDate ({http://www.opengis.net/citygml/1.0}creationDate) inherited from {http://www.opengis.net/citygml/1.0}AbstractCityObjectType
    
    # Element {http://www.opengis.net/citygml/building/1.0}lod4Geometry uses Python identifier lod4Geometry
    __lod4Geometry = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'lod4Geometry'), 'lod4Geometry', '__httpwww_opengis_netcitygmlbuilding1_0_BuildingInstallationType_httpwww_opengis_netcitygmlbuilding1_0lod4Geometry', False)

    
    lod4Geometry = property(__lod4Geometry.value, __lod4Geometry.set, None, None)

    
    # Element {http://www.opengis.net/citygml/building/1.0}usage uses Python identifier usage
    __usage = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'usage'), 'usage', '__httpwww_opengis_netcitygmlbuilding1_0_BuildingInstallationType_httpwww_opengis_netcitygmlbuilding1_0usage', True)

    
    usage = property(__usage.value, __usage.set, None, None)

    
    # Element {http://www.opengis.net/citygml/building/1.0}function uses Python identifier function
    __function = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'function'), 'function', '__httpwww_opengis_netcitygmlbuilding1_0_BuildingInstallationType_httpwww_opengis_netcitygmlbuilding1_0function', True)

    
    function = property(__function.value, __function.set, None, None)

    
    # Attribute id inherited from {http://www.opengis.net/gml}AbstractGMLType

    _ElementMap = pyxb.bundles.opengis.citygml.base.AbstractCityObjectType._ElementMap.copy()
    _ElementMap.update({
        __lod3Geometry.name() : __lod3Geometry,
        __lod2Geometry.name() : __lod2Geometry,
        __class.name() : __class,
        __GenericApplicationPropertyOfBuildingInstallation.name() : __GenericApplicationPropertyOfBuildingInstallation,
        __lod4Geometry.name() : __lod4Geometry,
        __usage.name() : __usage,
        __function.name() : __function
    })
    _AttributeMap = pyxb.bundles.opengis.citygml.base.AbstractCityObjectType._AttributeMap.copy()
    _AttributeMap.update({
        
    })
Namespace.addCategoryObject('typeBinding', u'BuildingInstallationType', BuildingInstallationType)


# Complex type BuildingPartType with content type ELEMENT_ONLY
class BuildingPartType (AbstractBuildingType):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'BuildingPartType')
    # Base type is AbstractBuildingType
    
    # Element yearOfDemolition ({http://www.opengis.net/citygml/building/1.0}yearOfDemolition) inherited from {http://www.opengis.net/citygml/building/1.0}AbstractBuildingType
    
    # Element location ({http://www.opengis.net/gml}location) inherited from {http://www.opengis.net/gml}AbstractFeatureType
    
    # Element boundedBy_ ({http://www.opengis.net/citygml/building/1.0}boundedBy) inherited from {http://www.opengis.net/citygml/building/1.0}AbstractBuildingType
    
    # Element {http://www.opengis.net/citygml/building/1.0}_GenericApplicationPropertyOfBuildingPart uses Python identifier GenericApplicationPropertyOfBuildingPart
    __GenericApplicationPropertyOfBuildingPart = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfBuildingPart'), 'GenericApplicationPropertyOfBuildingPart', '__httpwww_opengis_netcitygmlbuilding1_0_BuildingPartType_httpwww_opengis_netcitygmlbuilding1_0_GenericApplicationPropertyOfBuildingPart', True)

    
    GenericApplicationPropertyOfBuildingPart = property(__GenericApplicationPropertyOfBuildingPart.value, __GenericApplicationPropertyOfBuildingPart.set, None, None)

    
    # Element function ({http://www.opengis.net/citygml/building/1.0}function) inherited from {http://www.opengis.net/citygml/building/1.0}AbstractBuildingType
    
    # Element lod3Solid ({http://www.opengis.net/citygml/building/1.0}lod3Solid) inherited from {http://www.opengis.net/citygml/building/1.0}AbstractBuildingType
    
    # Element measuredHeight ({http://www.opengis.net/citygml/building/1.0}measuredHeight) inherited from {http://www.opengis.net/citygml/building/1.0}AbstractBuildingType
    
    # Element metaDataProperty ({http://www.opengis.net/gml}metaDataProperty) inherited from {http://www.opengis.net/gml}AbstractGMLType
    
    # Element lod3MultiSurface ({http://www.opengis.net/citygml/building/1.0}lod3MultiSurface) inherited from {http://www.opengis.net/citygml/building/1.0}AbstractBuildingType
    
    # Element storeysAboveGround ({http://www.opengis.net/citygml/building/1.0}storeysAboveGround) inherited from {http://www.opengis.net/citygml/building/1.0}AbstractBuildingType
    
    # Element lod3MultiCurve ({http://www.opengis.net/citygml/building/1.0}lod3MultiCurve) inherited from {http://www.opengis.net/citygml/building/1.0}AbstractBuildingType
    
    # Element storeysBelowGround ({http://www.opengis.net/citygml/building/1.0}storeysBelowGround) inherited from {http://www.opengis.net/citygml/building/1.0}AbstractBuildingType
    
    # Element lod3TerrainIntersection ({http://www.opengis.net/citygml/building/1.0}lod3TerrainIntersection) inherited from {http://www.opengis.net/citygml/building/1.0}AbstractBuildingType
    
    # Element storeyHeightsAboveGround ({http://www.opengis.net/citygml/building/1.0}storeyHeightsAboveGround) inherited from {http://www.opengis.net/citygml/building/1.0}AbstractBuildingType
    
    # Element class_ ({http://www.opengis.net/citygml/building/1.0}class) inherited from {http://www.opengis.net/citygml/building/1.0}AbstractBuildingType
    
    # Element lod4Solid ({http://www.opengis.net/citygml/building/1.0}lod4Solid) inherited from {http://www.opengis.net/citygml/building/1.0}AbstractBuildingType
    
    # Element storeyHeightsBelowGround ({http://www.opengis.net/citygml/building/1.0}storeyHeightsBelowGround) inherited from {http://www.opengis.net/citygml/building/1.0}AbstractBuildingType
    
    # Element generalizesTo ({http://www.opengis.net/citygml/1.0}generalizesTo) inherited from {http://www.opengis.net/citygml/1.0}AbstractCityObjectType
    
    # Element lod4MultiSurface ({http://www.opengis.net/citygml/building/1.0}lod4MultiSurface) inherited from {http://www.opengis.net/citygml/building/1.0}AbstractBuildingType
    
    # Element lod1Solid ({http://www.opengis.net/citygml/building/1.0}lod1Solid) inherited from {http://www.opengis.net/citygml/building/1.0}AbstractBuildingType
    
    # Element outerBuildingInstallation ({http://www.opengis.net/citygml/building/1.0}outerBuildingInstallation) inherited from {http://www.opengis.net/citygml/building/1.0}AbstractBuildingType
    
    # Element lod4MultiCurve ({http://www.opengis.net/citygml/building/1.0}lod4MultiCurve) inherited from {http://www.opengis.net/citygml/building/1.0}AbstractBuildingType
    
    # Element lod1MultiSurface ({http://www.opengis.net/citygml/building/1.0}lod1MultiSurface) inherited from {http://www.opengis.net/citygml/building/1.0}AbstractBuildingType
    
    # Element lod4TerrainIntersection ({http://www.opengis.net/citygml/building/1.0}lod4TerrainIntersection) inherited from {http://www.opengis.net/citygml/building/1.0}AbstractBuildingType
    
    # Element GenericApplicationPropertyOfCityObject ({http://www.opengis.net/citygml/1.0}_GenericApplicationPropertyOfCityObject) inherited from {http://www.opengis.net/citygml/1.0}AbstractCityObjectType
    
    # Element roofType ({http://www.opengis.net/citygml/building/1.0}roofType) inherited from {http://www.opengis.net/citygml/building/1.0}AbstractBuildingType
    
    # Element GenericApplicationPropertyOfAbstractBuilding ({http://www.opengis.net/citygml/building/1.0}_GenericApplicationPropertyOfAbstractBuilding) inherited from {http://www.opengis.net/citygml/building/1.0}AbstractBuildingType
    
    # Element lod2Solid ({http://www.opengis.net/citygml/building/1.0}lod2Solid) inherited from {http://www.opengis.net/citygml/building/1.0}AbstractBuildingType
    
    # Element description ({http://www.opengis.net/gml}description) inherited from {http://www.opengis.net/gml}AbstractGMLType
    
    # Element creationDate ({http://www.opengis.net/citygml/1.0}creationDate) inherited from {http://www.opengis.net/citygml/1.0}AbstractCityObjectType
    
    # Element lod1TerrainIntersection ({http://www.opengis.net/citygml/building/1.0}lod1TerrainIntersection) inherited from {http://www.opengis.net/citygml/building/1.0}AbstractBuildingType
    
    # Element lod2MultiSurface ({http://www.opengis.net/citygml/building/1.0}lod2MultiSurface) inherited from {http://www.opengis.net/citygml/building/1.0}AbstractBuildingType
    
    # Element address ({http://www.opengis.net/citygml/building/1.0}address) inherited from {http://www.opengis.net/citygml/building/1.0}AbstractBuildingType
    
    # Element lod2MultiCurve ({http://www.opengis.net/citygml/building/1.0}lod2MultiCurve) inherited from {http://www.opengis.net/citygml/building/1.0}AbstractBuildingType
    
    # Element interiorRoom ({http://www.opengis.net/citygml/building/1.0}interiorRoom) inherited from {http://www.opengis.net/citygml/building/1.0}AbstractBuildingType
    
    # Element GenericApplicationPropertyOfSite ({http://www.opengis.net/citygml/1.0}_GenericApplicationPropertyOfSite) inherited from {http://www.opengis.net/citygml/1.0}AbstractSiteType
    
    # Element lod2TerrainIntersection ({http://www.opengis.net/citygml/building/1.0}lod2TerrainIntersection) inherited from {http://www.opengis.net/citygml/building/1.0}AbstractBuildingType
    
    # Element yearOfConstruction ({http://www.opengis.net/citygml/building/1.0}yearOfConstruction) inherited from {http://www.opengis.net/citygml/building/1.0}AbstractBuildingType
    
    # Element externalReference ({http://www.opengis.net/citygml/1.0}externalReference) inherited from {http://www.opengis.net/citygml/1.0}AbstractCityObjectType
    
    # Element terminationDate ({http://www.opengis.net/citygml/1.0}terminationDate) inherited from {http://www.opengis.net/citygml/1.0}AbstractCityObjectType
    
    # Element usage ({http://www.opengis.net/citygml/building/1.0}usage) inherited from {http://www.opengis.net/citygml/building/1.0}AbstractBuildingType
    
    # Element consistsOfBuildingPart ({http://www.opengis.net/citygml/building/1.0}consistsOfBuildingPart) inherited from {http://www.opengis.net/citygml/building/1.0}AbstractBuildingType
    
    # Element name ({http://www.opengis.net/gml}name) inherited from {http://www.opengis.net/gml}AbstractGMLType
    
    # Element interiorBuildingInstallation ({http://www.opengis.net/citygml/building/1.0}interiorBuildingInstallation) inherited from {http://www.opengis.net/citygml/building/1.0}AbstractBuildingType
    
    # Element boundedBy ({http://www.opengis.net/gml}boundedBy) inherited from {http://www.opengis.net/gml}AbstractFeatureType
    
    # Attribute id inherited from {http://www.opengis.net/gml}AbstractGMLType

    _ElementMap = AbstractBuildingType._ElementMap.copy()
    _ElementMap.update({
        __GenericApplicationPropertyOfBuildingPart.name() : __GenericApplicationPropertyOfBuildingPart
    })
    _AttributeMap = AbstractBuildingType._AttributeMap.copy()
    _AttributeMap.update({
        
    })
Namespace.addCategoryObject('typeBinding', u'BuildingPartType', BuildingPartType)


# Complex type WindowType with content type ELEMENT_ONLY
class WindowType (AbstractOpeningType):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'WindowType')
    # Base type is AbstractOpeningType
    
    # Element location ({http://www.opengis.net/gml}location) inherited from {http://www.opengis.net/gml}AbstractFeatureType
    
    # Element description ({http://www.opengis.net/gml}description) inherited from {http://www.opengis.net/gml}AbstractGMLType
    
    # Element lod3MultiSurface ({http://www.opengis.net/citygml/building/1.0}lod3MultiSurface) inherited from {http://www.opengis.net/citygml/building/1.0}AbstractOpeningType
    
    # Element {http://www.opengis.net/citygml/building/1.0}_GenericApplicationPropertyOfWindow uses Python identifier GenericApplicationPropertyOfWindow
    __GenericApplicationPropertyOfWindow = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfWindow'), 'GenericApplicationPropertyOfWindow', '__httpwww_opengis_netcitygmlbuilding1_0_WindowType_httpwww_opengis_netcitygmlbuilding1_0_GenericApplicationPropertyOfWindow', True)

    
    GenericApplicationPropertyOfWindow = property(__GenericApplicationPropertyOfWindow.value, __GenericApplicationPropertyOfWindow.set, None, None)

    
    # Element GenericApplicationPropertyOfCityObject ({http://www.opengis.net/citygml/1.0}_GenericApplicationPropertyOfCityObject) inherited from {http://www.opengis.net/citygml/1.0}AbstractCityObjectType
    
    # Element metaDataProperty ({http://www.opengis.net/gml}metaDataProperty) inherited from {http://www.opengis.net/gml}AbstractGMLType
    
    # Element terminationDate ({http://www.opengis.net/citygml/1.0}terminationDate) inherited from {http://www.opengis.net/citygml/1.0}AbstractCityObjectType
    
    # Element externalReference ({http://www.opengis.net/citygml/1.0}externalReference) inherited from {http://www.opengis.net/citygml/1.0}AbstractCityObjectType
    
    # Element GenericApplicationPropertyOfOpening ({http://www.opengis.net/citygml/building/1.0}_GenericApplicationPropertyOfOpening) inherited from {http://www.opengis.net/citygml/building/1.0}AbstractOpeningType
    
    # Element generalizesTo ({http://www.opengis.net/citygml/1.0}generalizesTo) inherited from {http://www.opengis.net/citygml/1.0}AbstractCityObjectType
    
    # Element name ({http://www.opengis.net/gml}name) inherited from {http://www.opengis.net/gml}AbstractGMLType
    
    # Element creationDate ({http://www.opengis.net/citygml/1.0}creationDate) inherited from {http://www.opengis.net/citygml/1.0}AbstractCityObjectType
    
    # Element lod4MultiSurface ({http://www.opengis.net/citygml/building/1.0}lod4MultiSurface) inherited from {http://www.opengis.net/citygml/building/1.0}AbstractOpeningType
    
    # Element boundedBy ({http://www.opengis.net/gml}boundedBy) inherited from {http://www.opengis.net/gml}AbstractFeatureType
    
    # Attribute id inherited from {http://www.opengis.net/gml}AbstractGMLType

    _ElementMap = AbstractOpeningType._ElementMap.copy()
    _ElementMap.update({
        __GenericApplicationPropertyOfWindow.name() : __GenericApplicationPropertyOfWindow
    })
    _AttributeMap = AbstractOpeningType._AttributeMap.copy()
    _AttributeMap.update({
        
    })
Namespace.addCategoryObject('typeBinding', u'WindowType', WindowType)


# Complex type InteriorWallSurfaceType with content type ELEMENT_ONLY
class InteriorWallSurfaceType (AbstractBoundarySurfaceType):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'InteriorWallSurfaceType')
    # Base type is AbstractBoundarySurfaceType
    
    # Element location ({http://www.opengis.net/gml}location) inherited from {http://www.opengis.net/gml}AbstractFeatureType
    
    # Element opening ({http://www.opengis.net/citygml/building/1.0}opening) inherited from {http://www.opengis.net/citygml/building/1.0}AbstractBoundarySurfaceType
    
    # Element lod4MultiSurface ({http://www.opengis.net/citygml/building/1.0}lod4MultiSurface) inherited from {http://www.opengis.net/citygml/building/1.0}AbstractBoundarySurfaceType
    
    # Element description ({http://www.opengis.net/gml}description) inherited from {http://www.opengis.net/gml}AbstractGMLType
    
    # Element generalizesTo ({http://www.opengis.net/citygml/1.0}generalizesTo) inherited from {http://www.opengis.net/citygml/1.0}AbstractCityObjectType
    
    # Element GenericApplicationPropertyOfCityObject ({http://www.opengis.net/citygml/1.0}_GenericApplicationPropertyOfCityObject) inherited from {http://www.opengis.net/citygml/1.0}AbstractCityObjectType
    
    # Element terminationDate ({http://www.opengis.net/citygml/1.0}terminationDate) inherited from {http://www.opengis.net/citygml/1.0}AbstractCityObjectType
    
    # Element name ({http://www.opengis.net/gml}name) inherited from {http://www.opengis.net/gml}AbstractGMLType
    
    # Element externalReference ({http://www.opengis.net/citygml/1.0}externalReference) inherited from {http://www.opengis.net/citygml/1.0}AbstractCityObjectType
    
    # Element lod2MultiSurface ({http://www.opengis.net/citygml/building/1.0}lod2MultiSurface) inherited from {http://www.opengis.net/citygml/building/1.0}AbstractBoundarySurfaceType
    
    # Element GenericApplicationPropertyOfBoundarySurface ({http://www.opengis.net/citygml/building/1.0}_GenericApplicationPropertyOfBoundarySurface) inherited from {http://www.opengis.net/citygml/building/1.0}AbstractBoundarySurfaceType
    
    # Element lod3MultiSurface ({http://www.opengis.net/citygml/building/1.0}lod3MultiSurface) inherited from {http://www.opengis.net/citygml/building/1.0}AbstractBoundarySurfaceType
    
    # Element metaDataProperty ({http://www.opengis.net/gml}metaDataProperty) inherited from {http://www.opengis.net/gml}AbstractGMLType
    
    # Element creationDate ({http://www.opengis.net/citygml/1.0}creationDate) inherited from {http://www.opengis.net/citygml/1.0}AbstractCityObjectType
    
    # Element {http://www.opengis.net/citygml/building/1.0}_GenericApplicationPropertyOfInteriorWallSurface uses Python identifier GenericApplicationPropertyOfInteriorWallSurface
    __GenericApplicationPropertyOfInteriorWallSurface = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfInteriorWallSurface'), 'GenericApplicationPropertyOfInteriorWallSurface', '__httpwww_opengis_netcitygmlbuilding1_0_InteriorWallSurfaceType_httpwww_opengis_netcitygmlbuilding1_0_GenericApplicationPropertyOfInteriorWallSurface', True)

    
    GenericApplicationPropertyOfInteriorWallSurface = property(__GenericApplicationPropertyOfInteriorWallSurface.value, __GenericApplicationPropertyOfInteriorWallSurface.set, None, None)

    
    # Element boundedBy ({http://www.opengis.net/gml}boundedBy) inherited from {http://www.opengis.net/gml}AbstractFeatureType
    
    # Attribute id inherited from {http://www.opengis.net/gml}AbstractGMLType

    _ElementMap = AbstractBoundarySurfaceType._ElementMap.copy()
    _ElementMap.update({
        __GenericApplicationPropertyOfInteriorWallSurface.name() : __GenericApplicationPropertyOfInteriorWallSurface
    })
    _AttributeMap = AbstractBoundarySurfaceType._AttributeMap.copy()
    _AttributeMap.update({
        
    })
Namespace.addCategoryObject('typeBinding', u'InteriorWallSurfaceType', InteriorWallSurfaceType)


# Complex type DoorType with content type ELEMENT_ONLY
class DoorType (AbstractOpeningType):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'DoorType')
    # Base type is AbstractOpeningType
    
    # Element {http://www.opengis.net/citygml/building/1.0}_GenericApplicationPropertyOfDoor uses Python identifier GenericApplicationPropertyOfDoor
    __GenericApplicationPropertyOfDoor = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfDoor'), 'GenericApplicationPropertyOfDoor', '__httpwww_opengis_netcitygmlbuilding1_0_DoorType_httpwww_opengis_netcitygmlbuilding1_0_GenericApplicationPropertyOfDoor', True)

    
    GenericApplicationPropertyOfDoor = property(__GenericApplicationPropertyOfDoor.value, __GenericApplicationPropertyOfDoor.set, None, None)

    
    # Element lod3MultiSurface ({http://www.opengis.net/citygml/building/1.0}lod3MultiSurface) inherited from {http://www.opengis.net/citygml/building/1.0}AbstractOpeningType
    
    # Element generalizesTo ({http://www.opengis.net/citygml/1.0}generalizesTo) inherited from {http://www.opengis.net/citygml/1.0}AbstractCityObjectType
    
    # Element {http://www.opengis.net/citygml/building/1.0}address uses Python identifier address
    __address = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'address'), 'address', '__httpwww_opengis_netcitygmlbuilding1_0_DoorType_httpwww_opengis_netcitygmlbuilding1_0address', True)

    
    address = property(__address.value, __address.set, None, None)

    
    # Element metaDataProperty ({http://www.opengis.net/gml}metaDataProperty) inherited from {http://www.opengis.net/gml}AbstractGMLType
    
    # Element GenericApplicationPropertyOfCityObject ({http://www.opengis.net/citygml/1.0}_GenericApplicationPropertyOfCityObject) inherited from {http://www.opengis.net/citygml/1.0}AbstractCityObjectType
    
    # Element externalReference ({http://www.opengis.net/citygml/1.0}externalReference) inherited from {http://www.opengis.net/citygml/1.0}AbstractCityObjectType
    
    # Element location ({http://www.opengis.net/gml}location) inherited from {http://www.opengis.net/gml}AbstractFeatureType
    
    # Element GenericApplicationPropertyOfOpening ({http://www.opengis.net/citygml/building/1.0}_GenericApplicationPropertyOfOpening) inherited from {http://www.opengis.net/citygml/building/1.0}AbstractOpeningType
    
    # Element description ({http://www.opengis.net/gml}description) inherited from {http://www.opengis.net/gml}AbstractGMLType
    
    # Element name ({http://www.opengis.net/gml}name) inherited from {http://www.opengis.net/gml}AbstractGMLType
    
    # Element creationDate ({http://www.opengis.net/citygml/1.0}creationDate) inherited from {http://www.opengis.net/citygml/1.0}AbstractCityObjectType
    
    # Element lod4MultiSurface ({http://www.opengis.net/citygml/building/1.0}lod4MultiSurface) inherited from {http://www.opengis.net/citygml/building/1.0}AbstractOpeningType
    
    # Element terminationDate ({http://www.opengis.net/citygml/1.0}terminationDate) inherited from {http://www.opengis.net/citygml/1.0}AbstractCityObjectType
    
    # Element boundedBy ({http://www.opengis.net/gml}boundedBy) inherited from {http://www.opengis.net/gml}AbstractFeatureType
    
    # Attribute id inherited from {http://www.opengis.net/gml}AbstractGMLType

    _ElementMap = AbstractOpeningType._ElementMap.copy()
    _ElementMap.update({
        __GenericApplicationPropertyOfDoor.name() : __GenericApplicationPropertyOfDoor,
        __address.name() : __address
    })
    _AttributeMap = AbstractOpeningType._AttributeMap.copy()
    _AttributeMap.update({
        
    })
Namespace.addCategoryObject('typeBinding', u'DoorType', DoorType)


# Complex type InteriorFurniturePropertyType with content type ELEMENT_ONLY
class InteriorFurniturePropertyType (pyxb.bundles.opengis.gml.AssociationType):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'InteriorFurniturePropertyType')
    # Base type is pyxb.bundles.opengis.gml.AssociationType
    
    # Element {http://www.opengis.net/citygml/building/1.0}BuildingFurniture uses Python identifier BuildingFurniture
    __BuildingFurniture = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'BuildingFurniture'), 'BuildingFurniture', '__httpwww_opengis_netcitygmlbuilding1_0_InteriorFurniturePropertyType_httpwww_opengis_netcitygmlbuilding1_0BuildingFurniture', False)

    
    BuildingFurniture = property(__BuildingFurniture.value, __BuildingFurniture.set, None, None)

    
    # Attribute arcrole inherited from {http://www.opengis.net/gml}AssociationType
    
    # Attribute title inherited from {http://www.opengis.net/gml}AssociationType
    
    # Attribute remoteSchema inherited from {http://www.opengis.net/gml}AssociationType
    
    # Attribute href inherited from {http://www.opengis.net/gml}AssociationType
    
    # Attribute type inherited from {http://www.opengis.net/gml}AssociationType
    
    # Attribute actuate inherited from {http://www.opengis.net/gml}AssociationType
    
    # Attribute show inherited from {http://www.opengis.net/gml}AssociationType
    
    # Attribute role inherited from {http://www.opengis.net/gml}AssociationType

    _ElementMap = pyxb.bundles.opengis.gml.AssociationType._ElementMap.copy()
    _ElementMap.update({
        __BuildingFurniture.name() : __BuildingFurniture
    })
    _AttributeMap = pyxb.bundles.opengis.gml.AssociationType._AttributeMap.copy()
    _AttributeMap.update({
        
    })
Namespace.addCategoryObject('typeBinding', u'InteriorFurniturePropertyType', InteriorFurniturePropertyType)


# Complex type IntBuildingInstallationPropertyType with content type ELEMENT_ONLY
class IntBuildingInstallationPropertyType (pyxb.bundles.opengis.gml.AssociationType):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'IntBuildingInstallationPropertyType')
    # Base type is pyxb.bundles.opengis.gml.AssociationType
    
    # Element {http://www.opengis.net/citygml/building/1.0}IntBuildingInstallation uses Python identifier IntBuildingInstallation
    __IntBuildingInstallation = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'IntBuildingInstallation'), 'IntBuildingInstallation', '__httpwww_opengis_netcitygmlbuilding1_0_IntBuildingInstallationPropertyType_httpwww_opengis_netcitygmlbuilding1_0IntBuildingInstallation', False)

    
    IntBuildingInstallation = property(__IntBuildingInstallation.value, __IntBuildingInstallation.set, None, None)

    
    # Attribute arcrole inherited from {http://www.opengis.net/gml}AssociationType
    
    # Attribute title inherited from {http://www.opengis.net/gml}AssociationType
    
    # Attribute remoteSchema inherited from {http://www.opengis.net/gml}AssociationType
    
    # Attribute href inherited from {http://www.opengis.net/gml}AssociationType
    
    # Attribute type inherited from {http://www.opengis.net/gml}AssociationType
    
    # Attribute actuate inherited from {http://www.opengis.net/gml}AssociationType
    
    # Attribute show inherited from {http://www.opengis.net/gml}AssociationType
    
    # Attribute role inherited from {http://www.opengis.net/gml}AssociationType

    _ElementMap = pyxb.bundles.opengis.gml.AssociationType._ElementMap.copy()
    _ElementMap.update({
        __IntBuildingInstallation.name() : __IntBuildingInstallation
    })
    _AttributeMap = pyxb.bundles.opengis.gml.AssociationType._AttributeMap.copy()
    _AttributeMap.update({
        
    })
Namespace.addCategoryObject('typeBinding', u'IntBuildingInstallationPropertyType', IntBuildingInstallationPropertyType)


# Complex type BuildingInstallationPropertyType with content type ELEMENT_ONLY
class BuildingInstallationPropertyType (pyxb.bundles.opengis.gml.AssociationType):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'BuildingInstallationPropertyType')
    # Base type is pyxb.bundles.opengis.gml.AssociationType
    
    # Element {http://www.opengis.net/citygml/building/1.0}BuildingInstallation uses Python identifier BuildingInstallation
    __BuildingInstallation = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'BuildingInstallation'), 'BuildingInstallation', '__httpwww_opengis_netcitygmlbuilding1_0_BuildingInstallationPropertyType_httpwww_opengis_netcitygmlbuilding1_0BuildingInstallation', False)

    
    BuildingInstallation = property(__BuildingInstallation.value, __BuildingInstallation.set, None, None)

    
    # Attribute arcrole inherited from {http://www.opengis.net/gml}AssociationType
    
    # Attribute title inherited from {http://www.opengis.net/gml}AssociationType
    
    # Attribute remoteSchema inherited from {http://www.opengis.net/gml}AssociationType
    
    # Attribute href inherited from {http://www.opengis.net/gml}AssociationType
    
    # Attribute type inherited from {http://www.opengis.net/gml}AssociationType
    
    # Attribute actuate inherited from {http://www.opengis.net/gml}AssociationType
    
    # Attribute show inherited from {http://www.opengis.net/gml}AssociationType
    
    # Attribute role inherited from {http://www.opengis.net/gml}AssociationType

    _ElementMap = pyxb.bundles.opengis.gml.AssociationType._ElementMap.copy()
    _ElementMap.update({
        __BuildingInstallation.name() : __BuildingInstallation
    })
    _AttributeMap = pyxb.bundles.opengis.gml.AssociationType._AttributeMap.copy()
    _AttributeMap.update({
        
    })
Namespace.addCategoryObject('typeBinding', u'BuildingInstallationPropertyType', BuildingInstallationPropertyType)


# Complex type CeilingSurfaceType with content type ELEMENT_ONLY
class CeilingSurfaceType (AbstractBoundarySurfaceType):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'CeilingSurfaceType')
    # Base type is AbstractBoundarySurfaceType
    
    # Element lod4MultiSurface ({http://www.opengis.net/citygml/building/1.0}lod4MultiSurface) inherited from {http://www.opengis.net/citygml/building/1.0}AbstractBoundarySurfaceType
    
    # Element description ({http://www.opengis.net/gml}description) inherited from {http://www.opengis.net/gml}AbstractGMLType
    
    # Element location ({http://www.opengis.net/gml}location) inherited from {http://www.opengis.net/gml}AbstractFeatureType
    
    # Element opening ({http://www.opengis.net/citygml/building/1.0}opening) inherited from {http://www.opengis.net/citygml/building/1.0}AbstractBoundarySurfaceType
    
    # Element GenericApplicationPropertyOfCityObject ({http://www.opengis.net/citygml/1.0}_GenericApplicationPropertyOfCityObject) inherited from {http://www.opengis.net/citygml/1.0}AbstractCityObjectType
    
    # Element generalizesTo ({http://www.opengis.net/citygml/1.0}generalizesTo) inherited from {http://www.opengis.net/citygml/1.0}AbstractCityObjectType
    
    # Element terminationDate ({http://www.opengis.net/citygml/1.0}terminationDate) inherited from {http://www.opengis.net/citygml/1.0}AbstractCityObjectType
    
    # Element name ({http://www.opengis.net/gml}name) inherited from {http://www.opengis.net/gml}AbstractGMLType
    
    # Element externalReference ({http://www.opengis.net/citygml/1.0}externalReference) inherited from {http://www.opengis.net/citygml/1.0}AbstractCityObjectType
    
    # Element lod2MultiSurface ({http://www.opengis.net/citygml/building/1.0}lod2MultiSurface) inherited from {http://www.opengis.net/citygml/building/1.0}AbstractBoundarySurfaceType
    
    # Element GenericApplicationPropertyOfBoundarySurface ({http://www.opengis.net/citygml/building/1.0}_GenericApplicationPropertyOfBoundarySurface) inherited from {http://www.opengis.net/citygml/building/1.0}AbstractBoundarySurfaceType
    
    # Element metaDataProperty ({http://www.opengis.net/gml}metaDataProperty) inherited from {http://www.opengis.net/gml}AbstractGMLType
    
    # Element lod3MultiSurface ({http://www.opengis.net/citygml/building/1.0}lod3MultiSurface) inherited from {http://www.opengis.net/citygml/building/1.0}AbstractBoundarySurfaceType
    
    # Element creationDate ({http://www.opengis.net/citygml/1.0}creationDate) inherited from {http://www.opengis.net/citygml/1.0}AbstractCityObjectType
    
    # Element boundedBy ({http://www.opengis.net/gml}boundedBy) inherited from {http://www.opengis.net/gml}AbstractFeatureType
    
    # Element {http://www.opengis.net/citygml/building/1.0}_GenericApplicationPropertyOfCeilingSurface uses Python identifier GenericApplicationPropertyOfCeilingSurface
    __GenericApplicationPropertyOfCeilingSurface = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfCeilingSurface'), 'GenericApplicationPropertyOfCeilingSurface', '__httpwww_opengis_netcitygmlbuilding1_0_CeilingSurfaceType_httpwww_opengis_netcitygmlbuilding1_0_GenericApplicationPropertyOfCeilingSurface', True)

    
    GenericApplicationPropertyOfCeilingSurface = property(__GenericApplicationPropertyOfCeilingSurface.value, __GenericApplicationPropertyOfCeilingSurface.set, None, None)

    
    # Attribute id inherited from {http://www.opengis.net/gml}AbstractGMLType

    _ElementMap = AbstractBoundarySurfaceType._ElementMap.copy()
    _ElementMap.update({
        __GenericApplicationPropertyOfCeilingSurface.name() : __GenericApplicationPropertyOfCeilingSurface
    })
    _AttributeMap = AbstractBoundarySurfaceType._AttributeMap.copy()
    _AttributeMap.update({
        
    })
Namespace.addCategoryObject('typeBinding', u'CeilingSurfaceType', CeilingSurfaceType)


# Complex type OpeningPropertyType with content type ELEMENT_ONLY
class OpeningPropertyType (pyxb.bundles.opengis.gml.AssociationType):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'OpeningPropertyType')
    # Base type is pyxb.bundles.opengis.gml.AssociationType
    
    # Element {http://www.opengis.net/citygml/building/1.0}_Opening uses Python identifier Opening
    __Opening = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'_Opening'), 'Opening', '__httpwww_opengis_netcitygmlbuilding1_0_OpeningPropertyType_httpwww_opengis_netcitygmlbuilding1_0_Opening', False)

    
    Opening = property(__Opening.value, __Opening.set, None, None)

    
    # Attribute arcrole inherited from {http://www.opengis.net/gml}AssociationType
    
    # Attribute title inherited from {http://www.opengis.net/gml}AssociationType
    
    # Attribute remoteSchema inherited from {http://www.opengis.net/gml}AssociationType
    
    # Attribute href inherited from {http://www.opengis.net/gml}AssociationType
    
    # Attribute type inherited from {http://www.opengis.net/gml}AssociationType
    
    # Attribute actuate inherited from {http://www.opengis.net/gml}AssociationType
    
    # Attribute show inherited from {http://www.opengis.net/gml}AssociationType
    
    # Attribute role inherited from {http://www.opengis.net/gml}AssociationType

    _ElementMap = pyxb.bundles.opengis.gml.AssociationType._ElementMap.copy()
    _ElementMap.update({
        __Opening.name() : __Opening
    })
    _AttributeMap = pyxb.bundles.opengis.gml.AssociationType._AttributeMap.copy()
    _AttributeMap.update({
        
    })
Namespace.addCategoryObject('typeBinding', u'OpeningPropertyType', OpeningPropertyType)


# Complex type BuildingPartPropertyType with content type ELEMENT_ONLY
class BuildingPartPropertyType (pyxb.bundles.opengis.gml.AssociationType):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'BuildingPartPropertyType')
    # Base type is pyxb.bundles.opengis.gml.AssociationType
    
    # Element {http://www.opengis.net/citygml/building/1.0}BuildingPart uses Python identifier BuildingPart
    __BuildingPart = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'BuildingPart'), 'BuildingPart', '__httpwww_opengis_netcitygmlbuilding1_0_BuildingPartPropertyType_httpwww_opengis_netcitygmlbuilding1_0BuildingPart', False)

    
    BuildingPart = property(__BuildingPart.value, __BuildingPart.set, None, None)

    
    # Attribute arcrole inherited from {http://www.opengis.net/gml}AssociationType
    
    # Attribute title inherited from {http://www.opengis.net/gml}AssociationType
    
    # Attribute remoteSchema inherited from {http://www.opengis.net/gml}AssociationType
    
    # Attribute href inherited from {http://www.opengis.net/gml}AssociationType
    
    # Attribute type inherited from {http://www.opengis.net/gml}AssociationType
    
    # Attribute actuate inherited from {http://www.opengis.net/gml}AssociationType
    
    # Attribute show inherited from {http://www.opengis.net/gml}AssociationType
    
    # Attribute role inherited from {http://www.opengis.net/gml}AssociationType

    _ElementMap = pyxb.bundles.opengis.gml.AssociationType._ElementMap.copy()
    _ElementMap.update({
        __BuildingPart.name() : __BuildingPart
    })
    _AttributeMap = pyxb.bundles.opengis.gml.AssociationType._AttributeMap.copy()
    _AttributeMap.update({
        
    })
Namespace.addCategoryObject('typeBinding', u'BuildingPartPropertyType', BuildingPartPropertyType)


GenericApplicationPropertyOfRoofSurface = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfRoofSurface'), pyxb.binding.datatypes.anyType, abstract=pyxb.binding.datatypes.boolean(1))
Namespace.addCategoryObject('elementBinding', GenericApplicationPropertyOfRoofSurface.name().localName(), GenericApplicationPropertyOfRoofSurface)

GenericApplicationPropertyOfWallSurface = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfWallSurface'), pyxb.binding.datatypes.anyType, abstract=pyxb.binding.datatypes.boolean(1))
Namespace.addCategoryObject('elementBinding', GenericApplicationPropertyOfWallSurface.name().localName(), GenericApplicationPropertyOfWallSurface)

GroundSurface = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'GroundSurface'), GroundSurfaceType)
Namespace.addCategoryObject('elementBinding', GroundSurface.name().localName(), GroundSurface)

GenericApplicationPropertyOfGroundSurface = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfGroundSurface'), pyxb.binding.datatypes.anyType, abstract=pyxb.binding.datatypes.boolean(1))
Namespace.addCategoryObject('elementBinding', GenericApplicationPropertyOfGroundSurface.name().localName(), GenericApplicationPropertyOfGroundSurface)

ClosureSurface = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'ClosureSurface'), ClosureSurfaceType)
Namespace.addCategoryObject('elementBinding', ClosureSurface.name().localName(), ClosureSurface)

GenericApplicationPropertyOfClosureSurface = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfClosureSurface'), pyxb.binding.datatypes.anyType, abstract=pyxb.binding.datatypes.boolean(1))
Namespace.addCategoryObject('elementBinding', GenericApplicationPropertyOfClosureSurface.name().localName(), GenericApplicationPropertyOfClosureSurface)

RoofSurface = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'RoofSurface'), RoofSurfaceType)
Namespace.addCategoryObject('elementBinding', RoofSurface.name().localName(), RoofSurface)

AbstractBuilding = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'_AbstractBuilding'), AbstractBuildingType, abstract=pyxb.binding.datatypes.boolean(1))
Namespace.addCategoryObject('elementBinding', AbstractBuilding.name().localName(), AbstractBuilding)

GenericApplicationPropertyOfFloorSurface = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfFloorSurface'), pyxb.binding.datatypes.anyType, abstract=pyxb.binding.datatypes.boolean(1))
Namespace.addCategoryObject('elementBinding', GenericApplicationPropertyOfFloorSurface.name().localName(), GenericApplicationPropertyOfFloorSurface)

GenericApplicationPropertyOfInteriorWallSurface = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfInteriorWallSurface'), pyxb.binding.datatypes.anyType, abstract=pyxb.binding.datatypes.boolean(1))
Namespace.addCategoryObject('elementBinding', GenericApplicationPropertyOfInteriorWallSurface.name().localName(), GenericApplicationPropertyOfInteriorWallSurface)

GenericApplicationPropertyOfCeilingSurface = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfCeilingSurface'), pyxb.binding.datatypes.anyType, abstract=pyxb.binding.datatypes.boolean(1))
Namespace.addCategoryObject('elementBinding', GenericApplicationPropertyOfCeilingSurface.name().localName(), GenericApplicationPropertyOfCeilingSurface)

FloorSurface = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'FloorSurface'), FloorSurfaceType)
Namespace.addCategoryObject('elementBinding', FloorSurface.name().localName(), FloorSurface)

Building = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Building'), BuildingType)
Namespace.addCategoryObject('elementBinding', Building.name().localName(), Building)

GenericApplicationPropertyOfBuilding = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfBuilding'), pyxb.binding.datatypes.anyType, abstract=pyxb.binding.datatypes.boolean(1))
Namespace.addCategoryObject('elementBinding', GenericApplicationPropertyOfBuilding.name().localName(), GenericApplicationPropertyOfBuilding)

WallSurface = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'WallSurface'), WallSurfaceType)
Namespace.addCategoryObject('elementBinding', WallSurface.name().localName(), WallSurface)

GenericApplicationPropertyOfAbstractBuilding = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfAbstractBuilding'), pyxb.binding.datatypes.anyType, abstract=pyxb.binding.datatypes.boolean(1))
Namespace.addCategoryObject('elementBinding', GenericApplicationPropertyOfAbstractBuilding.name().localName(), GenericApplicationPropertyOfAbstractBuilding)

BuildingPart = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'BuildingPart'), BuildingPartType)
Namespace.addCategoryObject('elementBinding', BuildingPart.name().localName(), BuildingPart)

GenericApplicationPropertyOfBuildingPart = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfBuildingPart'), pyxb.binding.datatypes.anyType, abstract=pyxb.binding.datatypes.boolean(1))
Namespace.addCategoryObject('elementBinding', GenericApplicationPropertyOfBuildingPart.name().localName(), GenericApplicationPropertyOfBuildingPart)

Opening = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'_Opening'), AbstractOpeningType, abstract=pyxb.binding.datatypes.boolean(1))
Namespace.addCategoryObject('elementBinding', Opening.name().localName(), Opening)

GenericApplicationPropertyOfOpening = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfOpening'), pyxb.binding.datatypes.anyType, abstract=pyxb.binding.datatypes.boolean(1))
Namespace.addCategoryObject('elementBinding', GenericApplicationPropertyOfOpening.name().localName(), GenericApplicationPropertyOfOpening)

Window = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Window'), WindowType)
Namespace.addCategoryObject('elementBinding', Window.name().localName(), Window)

BuildingInstallation = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'BuildingInstallation'), BuildingInstallationType)
Namespace.addCategoryObject('elementBinding', BuildingInstallation.name().localName(), BuildingInstallation)

GenericApplicationPropertyOfBuildingInstallation = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfBuildingInstallation'), pyxb.binding.datatypes.anyType, abstract=pyxb.binding.datatypes.boolean(1))
Namespace.addCategoryObject('elementBinding', GenericApplicationPropertyOfBuildingInstallation.name().localName(), GenericApplicationPropertyOfBuildingInstallation)

InteriorWallSurface = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'InteriorWallSurface'), InteriorWallSurfaceType)
Namespace.addCategoryObject('elementBinding', InteriorWallSurface.name().localName(), InteriorWallSurface)

Door = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Door'), DoorType)
Namespace.addCategoryObject('elementBinding', Door.name().localName(), Door)

GenericApplicationPropertyOfDoor = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfDoor'), pyxb.binding.datatypes.anyType, abstract=pyxb.binding.datatypes.boolean(1))
Namespace.addCategoryObject('elementBinding', GenericApplicationPropertyOfDoor.name().localName(), GenericApplicationPropertyOfDoor)

IntBuildingInstallation = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'IntBuildingInstallation'), IntBuildingInstallationType)
Namespace.addCategoryObject('elementBinding', IntBuildingInstallation.name().localName(), IntBuildingInstallation)

GenericApplicationPropertyOfIntBuildingInstallation = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfIntBuildingInstallation'), pyxb.binding.datatypes.anyType, abstract=pyxb.binding.datatypes.boolean(1))
Namespace.addCategoryObject('elementBinding', GenericApplicationPropertyOfIntBuildingInstallation.name().localName(), GenericApplicationPropertyOfIntBuildingInstallation)

Room = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Room'), RoomType)
Namespace.addCategoryObject('elementBinding', Room.name().localName(), Room)

GenericApplicationPropertyOfRoom = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfRoom'), pyxb.binding.datatypes.anyType, abstract=pyxb.binding.datatypes.boolean(1))
Namespace.addCategoryObject('elementBinding', GenericApplicationPropertyOfRoom.name().localName(), GenericApplicationPropertyOfRoom)

GenericApplicationPropertyOfBuildingFurniture = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfBuildingFurniture'), pyxb.binding.datatypes.anyType, abstract=pyxb.binding.datatypes.boolean(1))
Namespace.addCategoryObject('elementBinding', GenericApplicationPropertyOfBuildingFurniture.name().localName(), GenericApplicationPropertyOfBuildingFurniture)

CeilingSurface = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'CeilingSurface'), CeilingSurfaceType)
Namespace.addCategoryObject('elementBinding', CeilingSurface.name().localName(), CeilingSurface)

GenericApplicationPropertyOfWindow = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfWindow'), pyxb.binding.datatypes.anyType, abstract=pyxb.binding.datatypes.boolean(1))
Namespace.addCategoryObject('elementBinding', GenericApplicationPropertyOfWindow.name().localName(), GenericApplicationPropertyOfWindow)

BuildingFurniture = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'BuildingFurniture'), BuildingFurnitureType)
Namespace.addCategoryObject('elementBinding', BuildingFurniture.name().localName(), BuildingFurniture)

BoundarySurface = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'_BoundarySurface'), AbstractBoundarySurfaceType, abstract=pyxb.binding.datatypes.boolean(1))
Namespace.addCategoryObject('elementBinding', BoundarySurface.name().localName(), BoundarySurface)

GenericApplicationPropertyOfBoundarySurface = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfBoundarySurface'), pyxb.binding.datatypes.anyType, abstract=pyxb.binding.datatypes.boolean(1))
Namespace.addCategoryObject('elementBinding', GenericApplicationPropertyOfBoundarySurface.name().localName(), GenericApplicationPropertyOfBoundarySurface)



RoomType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'interiorFurniture'), InteriorFurniturePropertyType, scope=RoomType))

RoomType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'usage'), RoomUsageType, scope=RoomType))

RoomType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'roomInstallation'), IntBuildingInstallationPropertyType, scope=RoomType))

RoomType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiSurface'), pyxb.bundles.opengis.gml.MultiSurfacePropertyType, scope=RoomType))

RoomType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'class'), RoomClassType, scope=RoomType))

RoomType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'boundedBy'), BoundarySurfacePropertyType, scope=RoomType))

RoomType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'function'), RoomFunctionType, scope=RoomType))

RoomType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfRoom'), pyxb.binding.datatypes.anyType, abstract=pyxb.binding.datatypes.boolean(1), scope=RoomType))

RoomType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'lod4Solid'), pyxb.bundles.opengis.gml.SolidPropertyType, scope=RoomType))
RoomType._GroupModel_14 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(RoomType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'metaDataProperty')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(RoomType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'description')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(RoomType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'name')), min_occurs=0L, max_occurs=None)
    )
RoomType._GroupModel_13 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(RoomType._GroupModel_14, min_occurs=1, max_occurs=1)
    )
RoomType._GroupModel_15 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(RoomType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'boundedBy')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(RoomType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'location')), min_occurs=0L, max_occurs=1)
    )
RoomType._GroupModel_12 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(RoomType._GroupModel_13, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(RoomType._GroupModel_15, min_occurs=1, max_occurs=1)
    )
RoomType._GroupModel_16 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(RoomType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'creationDate')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(RoomType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'terminationDate')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(RoomType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'externalReference')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(RoomType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'generalizesTo')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(RoomType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'_GenericApplicationPropertyOfCityObject')), min_occurs=0L, max_occurs=None)
    )
RoomType._GroupModel_11 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(RoomType._GroupModel_12, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(RoomType._GroupModel_16, min_occurs=1, max_occurs=1)
    )
RoomType._GroupModel_17 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(RoomType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'class')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(RoomType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'function')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(RoomType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'usage')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(RoomType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4Solid')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(RoomType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiSurface')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(RoomType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'boundedBy')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(RoomType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'interiorFurniture')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(RoomType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'roomInstallation')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(RoomType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfRoom')), min_occurs=0L, max_occurs=None)
    )
RoomType._GroupModel_10 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(RoomType._GroupModel_11, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(RoomType._GroupModel_17, min_occurs=1, max_occurs=1)
    )
RoomType._ContentModel = pyxb.binding.content.ParticleModel(RoomType._GroupModel_10, min_occurs=1, max_occurs=1)



AbstractOpeningType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiSurface'), pyxb.bundles.opengis.gml.MultiSurfacePropertyType, scope=AbstractOpeningType))

AbstractOpeningType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfOpening'), pyxb.binding.datatypes.anyType, abstract=pyxb.binding.datatypes.boolean(1), scope=AbstractOpeningType))

AbstractOpeningType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiSurface'), pyxb.bundles.opengis.gml.MultiSurfacePropertyType, scope=AbstractOpeningType))
AbstractOpeningType._GroupModel_14 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(AbstractOpeningType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'metaDataProperty')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(AbstractOpeningType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'description')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(AbstractOpeningType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'name')), min_occurs=0L, max_occurs=None)
    )
AbstractOpeningType._GroupModel_13 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(AbstractOpeningType._GroupModel_14, min_occurs=1, max_occurs=1)
    )
AbstractOpeningType._GroupModel_15 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(AbstractOpeningType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'boundedBy')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(AbstractOpeningType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'location')), min_occurs=0L, max_occurs=1)
    )
AbstractOpeningType._GroupModel_12 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(AbstractOpeningType._GroupModel_13, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(AbstractOpeningType._GroupModel_15, min_occurs=1, max_occurs=1)
    )
AbstractOpeningType._GroupModel_16 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(AbstractOpeningType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'creationDate')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(AbstractOpeningType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'terminationDate')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(AbstractOpeningType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'externalReference')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(AbstractOpeningType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'generalizesTo')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(AbstractOpeningType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'_GenericApplicationPropertyOfCityObject')), min_occurs=0L, max_occurs=None)
    )
AbstractOpeningType._GroupModel_11 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(AbstractOpeningType._GroupModel_12, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(AbstractOpeningType._GroupModel_16, min_occurs=1, max_occurs=1)
    )
AbstractOpeningType._GroupModel_17 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(AbstractOpeningType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiSurface')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(AbstractOpeningType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiSurface')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(AbstractOpeningType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfOpening')), min_occurs=0L, max_occurs=None)
    )
AbstractOpeningType._GroupModel_10 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(AbstractOpeningType._GroupModel_11, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(AbstractOpeningType._GroupModel_17, min_occurs=1, max_occurs=1)
    )
AbstractOpeningType._ContentModel = pyxb.binding.content.ParticleModel(AbstractOpeningType._GroupModel_10, min_occurs=1, max_occurs=1)



BuildingFurnitureType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'lod4ImplicitRepresentation'), pyxb.bundles.opengis.citygml.base.ImplicitRepresentationPropertyType, scope=BuildingFurnitureType))

BuildingFurnitureType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'class'), BuildingFurnitureClassType, scope=BuildingFurnitureType))

BuildingFurnitureType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'usage'), BuildingFurnitureUsageType, scope=BuildingFurnitureType))

BuildingFurnitureType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'function'), BuildingFurnitureFunctionType, scope=BuildingFurnitureType))

BuildingFurnitureType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'lod4Geometry'), pyxb.bundles.opengis.gml.GeometryPropertyType, scope=BuildingFurnitureType))

BuildingFurnitureType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfBuildingFurniture'), pyxb.binding.datatypes.anyType, abstract=pyxb.binding.datatypes.boolean(1), scope=BuildingFurnitureType))
BuildingFurnitureType._GroupModel_14 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(BuildingFurnitureType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'metaDataProperty')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(BuildingFurnitureType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'description')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(BuildingFurnitureType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'name')), min_occurs=0L, max_occurs=None)
    )
BuildingFurnitureType._GroupModel_13 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(BuildingFurnitureType._GroupModel_14, min_occurs=1, max_occurs=1)
    )
BuildingFurnitureType._GroupModel_15 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(BuildingFurnitureType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'boundedBy')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(BuildingFurnitureType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'location')), min_occurs=0L, max_occurs=1)
    )
BuildingFurnitureType._GroupModel_12 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(BuildingFurnitureType._GroupModel_13, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(BuildingFurnitureType._GroupModel_15, min_occurs=1, max_occurs=1)
    )
BuildingFurnitureType._GroupModel_16 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(BuildingFurnitureType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'creationDate')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(BuildingFurnitureType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'terminationDate')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(BuildingFurnitureType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'externalReference')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(BuildingFurnitureType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'generalizesTo')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(BuildingFurnitureType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'_GenericApplicationPropertyOfCityObject')), min_occurs=0L, max_occurs=None)
    )
BuildingFurnitureType._GroupModel_11 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(BuildingFurnitureType._GroupModel_12, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(BuildingFurnitureType._GroupModel_16, min_occurs=1, max_occurs=1)
    )
BuildingFurnitureType._GroupModel_17 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(BuildingFurnitureType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'class')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(BuildingFurnitureType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'function')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(BuildingFurnitureType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'usage')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(BuildingFurnitureType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4Geometry')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(BuildingFurnitureType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4ImplicitRepresentation')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(BuildingFurnitureType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfBuildingFurniture')), min_occurs=0L, max_occurs=None)
    )
BuildingFurnitureType._GroupModel_10 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(BuildingFurnitureType._GroupModel_11, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(BuildingFurnitureType._GroupModel_17, min_occurs=1, max_occurs=1)
    )
BuildingFurnitureType._ContentModel = pyxb.binding.content.ParticleModel(BuildingFurnitureType._GroupModel_10, min_occurs=1, max_occurs=1)



BoundarySurfacePropertyType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'_BoundarySurface'), AbstractBoundarySurfaceType, abstract=pyxb.binding.datatypes.boolean(1), scope=BoundarySurfacePropertyType))
BoundarySurfacePropertyType._GroupModel_ = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(BoundarySurfacePropertyType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_BoundarySurface')), min_occurs=1, max_occurs=1)
    )
BoundarySurfacePropertyType._ContentModel = pyxb.binding.content.ParticleModel(BoundarySurfacePropertyType._GroupModel_, min_occurs=0L, max_occurs=1)



AbstractBoundarySurfaceType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiSurface'), pyxb.bundles.opengis.gml.MultiSurfacePropertyType, scope=AbstractBoundarySurfaceType))

AbstractBoundarySurfaceType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'opening'), OpeningPropertyType, scope=AbstractBoundarySurfaceType))

AbstractBoundarySurfaceType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'lod2MultiSurface'), pyxb.bundles.opengis.gml.MultiSurfacePropertyType, scope=AbstractBoundarySurfaceType))

AbstractBoundarySurfaceType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfBoundarySurface'), pyxb.binding.datatypes.anyType, abstract=pyxb.binding.datatypes.boolean(1), scope=AbstractBoundarySurfaceType))

AbstractBoundarySurfaceType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiSurface'), pyxb.bundles.opengis.gml.MultiSurfacePropertyType, scope=AbstractBoundarySurfaceType))
AbstractBoundarySurfaceType._GroupModel_14 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(AbstractBoundarySurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'metaDataProperty')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(AbstractBoundarySurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'description')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(AbstractBoundarySurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'name')), min_occurs=0L, max_occurs=None)
    )
AbstractBoundarySurfaceType._GroupModel_13 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(AbstractBoundarySurfaceType._GroupModel_14, min_occurs=1, max_occurs=1)
    )
AbstractBoundarySurfaceType._GroupModel_15 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(AbstractBoundarySurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'boundedBy')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(AbstractBoundarySurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'location')), min_occurs=0L, max_occurs=1)
    )
AbstractBoundarySurfaceType._GroupModel_12 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(AbstractBoundarySurfaceType._GroupModel_13, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(AbstractBoundarySurfaceType._GroupModel_15, min_occurs=1, max_occurs=1)
    )
AbstractBoundarySurfaceType._GroupModel_16 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(AbstractBoundarySurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'creationDate')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(AbstractBoundarySurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'terminationDate')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(AbstractBoundarySurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'externalReference')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(AbstractBoundarySurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'generalizesTo')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(AbstractBoundarySurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'_GenericApplicationPropertyOfCityObject')), min_occurs=0L, max_occurs=None)
    )
AbstractBoundarySurfaceType._GroupModel_11 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(AbstractBoundarySurfaceType._GroupModel_12, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(AbstractBoundarySurfaceType._GroupModel_16, min_occurs=1, max_occurs=1)
    )
AbstractBoundarySurfaceType._GroupModel_17 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(AbstractBoundarySurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2MultiSurface')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(AbstractBoundarySurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiSurface')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(AbstractBoundarySurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiSurface')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(AbstractBoundarySurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'opening')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(AbstractBoundarySurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfBoundarySurface')), min_occurs=0L, max_occurs=None)
    )
AbstractBoundarySurfaceType._GroupModel_10 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(AbstractBoundarySurfaceType._GroupModel_11, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(AbstractBoundarySurfaceType._GroupModel_17, min_occurs=1, max_occurs=1)
    )
AbstractBoundarySurfaceType._ContentModel = pyxb.binding.content.ParticleModel(AbstractBoundarySurfaceType._GroupModel_10, min_occurs=1, max_occurs=1)



GroundSurfaceType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfGroundSurface'), pyxb.binding.datatypes.anyType, abstract=pyxb.binding.datatypes.boolean(1), scope=GroundSurfaceType))
GroundSurfaceType._GroupModel_15 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(GroundSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'metaDataProperty')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(GroundSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'description')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(GroundSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'name')), min_occurs=0L, max_occurs=None)
    )
GroundSurfaceType._GroupModel_14 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(GroundSurfaceType._GroupModel_15, min_occurs=1, max_occurs=1)
    )
GroundSurfaceType._GroupModel_16 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(GroundSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'boundedBy')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(GroundSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'location')), min_occurs=0L, max_occurs=1)
    )
GroundSurfaceType._GroupModel_13 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(GroundSurfaceType._GroupModel_14, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(GroundSurfaceType._GroupModel_16, min_occurs=1, max_occurs=1)
    )
GroundSurfaceType._GroupModel_17 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(GroundSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'creationDate')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(GroundSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'terminationDate')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(GroundSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'externalReference')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(GroundSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'generalizesTo')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(GroundSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'_GenericApplicationPropertyOfCityObject')), min_occurs=0L, max_occurs=None)
    )
GroundSurfaceType._GroupModel_12 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(GroundSurfaceType._GroupModel_13, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(GroundSurfaceType._GroupModel_17, min_occurs=1, max_occurs=1)
    )
GroundSurfaceType._GroupModel_18 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(GroundSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2MultiSurface')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(GroundSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiSurface')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(GroundSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiSurface')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(GroundSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'opening')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(GroundSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfBoundarySurface')), min_occurs=0L, max_occurs=None)
    )
GroundSurfaceType._GroupModel_11 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(GroundSurfaceType._GroupModel_12, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(GroundSurfaceType._GroupModel_18, min_occurs=1, max_occurs=1)
    )
GroundSurfaceType._GroupModel_19 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(GroundSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfGroundSurface')), min_occurs=0L, max_occurs=None)
    )
GroundSurfaceType._GroupModel_10 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(GroundSurfaceType._GroupModel_11, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(GroundSurfaceType._GroupModel_19, min_occurs=1, max_occurs=1)
    )
GroundSurfaceType._ContentModel = pyxb.binding.content.ParticleModel(GroundSurfaceType._GroupModel_10, min_occurs=1, max_occurs=1)



InteriorRoomPropertyType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Room'), RoomType, scope=InteriorRoomPropertyType))
InteriorRoomPropertyType._GroupModel_ = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(InteriorRoomPropertyType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Room')), min_occurs=1, max_occurs=1)
    )
InteriorRoomPropertyType._ContentModel = pyxb.binding.content.ParticleModel(InteriorRoomPropertyType._GroupModel_, min_occurs=0L, max_occurs=1)



ClosureSurfaceType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfClosureSurface'), pyxb.binding.datatypes.anyType, abstract=pyxb.binding.datatypes.boolean(1), scope=ClosureSurfaceType))
ClosureSurfaceType._GroupModel_15 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(ClosureSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'metaDataProperty')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(ClosureSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'description')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(ClosureSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'name')), min_occurs=0L, max_occurs=None)
    )
ClosureSurfaceType._GroupModel_14 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(ClosureSurfaceType._GroupModel_15, min_occurs=1, max_occurs=1)
    )
ClosureSurfaceType._GroupModel_16 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(ClosureSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'boundedBy')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(ClosureSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'location')), min_occurs=0L, max_occurs=1)
    )
ClosureSurfaceType._GroupModel_13 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(ClosureSurfaceType._GroupModel_14, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(ClosureSurfaceType._GroupModel_16, min_occurs=1, max_occurs=1)
    )
ClosureSurfaceType._GroupModel_17 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(ClosureSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'creationDate')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(ClosureSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'terminationDate')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(ClosureSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'externalReference')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(ClosureSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'generalizesTo')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(ClosureSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'_GenericApplicationPropertyOfCityObject')), min_occurs=0L, max_occurs=None)
    )
ClosureSurfaceType._GroupModel_12 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(ClosureSurfaceType._GroupModel_13, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(ClosureSurfaceType._GroupModel_17, min_occurs=1, max_occurs=1)
    )
ClosureSurfaceType._GroupModel_18 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(ClosureSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2MultiSurface')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(ClosureSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiSurface')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(ClosureSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiSurface')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(ClosureSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'opening')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(ClosureSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfBoundarySurface')), min_occurs=0L, max_occurs=None)
    )
ClosureSurfaceType._GroupModel_11 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(ClosureSurfaceType._GroupModel_12, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(ClosureSurfaceType._GroupModel_18, min_occurs=1, max_occurs=1)
    )
ClosureSurfaceType._GroupModel_19 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(ClosureSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfClosureSurface')), min_occurs=0L, max_occurs=None)
    )
ClosureSurfaceType._GroupModel_10 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(ClosureSurfaceType._GroupModel_11, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(ClosureSurfaceType._GroupModel_19, min_occurs=1, max_occurs=1)
    )
ClosureSurfaceType._ContentModel = pyxb.binding.content.ParticleModel(ClosureSurfaceType._GroupModel_10, min_occurs=1, max_occurs=1)



RoofSurfaceType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfRoofSurface'), pyxb.binding.datatypes.anyType, abstract=pyxb.binding.datatypes.boolean(1), scope=RoofSurfaceType))
RoofSurfaceType._GroupModel_15 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(RoofSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'metaDataProperty')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(RoofSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'description')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(RoofSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'name')), min_occurs=0L, max_occurs=None)
    )
RoofSurfaceType._GroupModel_14 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(RoofSurfaceType._GroupModel_15, min_occurs=1, max_occurs=1)
    )
RoofSurfaceType._GroupModel_16 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(RoofSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'boundedBy')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(RoofSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'location')), min_occurs=0L, max_occurs=1)
    )
RoofSurfaceType._GroupModel_13 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(RoofSurfaceType._GroupModel_14, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(RoofSurfaceType._GroupModel_16, min_occurs=1, max_occurs=1)
    )
RoofSurfaceType._GroupModel_17 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(RoofSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'creationDate')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(RoofSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'terminationDate')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(RoofSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'externalReference')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(RoofSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'generalizesTo')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(RoofSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'_GenericApplicationPropertyOfCityObject')), min_occurs=0L, max_occurs=None)
    )
RoofSurfaceType._GroupModel_12 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(RoofSurfaceType._GroupModel_13, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(RoofSurfaceType._GroupModel_17, min_occurs=1, max_occurs=1)
    )
RoofSurfaceType._GroupModel_18 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(RoofSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2MultiSurface')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(RoofSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiSurface')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(RoofSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiSurface')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(RoofSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'opening')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(RoofSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfBoundarySurface')), min_occurs=0L, max_occurs=None)
    )
RoofSurfaceType._GroupModel_11 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(RoofSurfaceType._GroupModel_12, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(RoofSurfaceType._GroupModel_18, min_occurs=1, max_occurs=1)
    )
RoofSurfaceType._GroupModel_19 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(RoofSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfRoofSurface')), min_occurs=0L, max_occurs=None)
    )
RoofSurfaceType._GroupModel_10 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(RoofSurfaceType._GroupModel_11, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(RoofSurfaceType._GroupModel_19, min_occurs=1, max_occurs=1)
    )
RoofSurfaceType._ContentModel = pyxb.binding.content.ParticleModel(RoofSurfaceType._GroupModel_10, min_occurs=1, max_occurs=1)



AbstractBuildingType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'yearOfDemolition'), pyxb.binding.datatypes.gYear, scope=AbstractBuildingType))

AbstractBuildingType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'boundedBy'), BoundarySurfacePropertyType, scope=AbstractBuildingType))

AbstractBuildingType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'roofType'), RoofTypeType, scope=AbstractBuildingType))

AbstractBuildingType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'function'), BuildingFunctionType, scope=AbstractBuildingType))

AbstractBuildingType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'lod3Solid'), pyxb.bundles.opengis.gml.SolidPropertyType, scope=AbstractBuildingType))

AbstractBuildingType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'measuredHeight'), pyxb.bundles.opengis.gml.LengthType, scope=AbstractBuildingType))

AbstractBuildingType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiSurface'), pyxb.bundles.opengis.gml.MultiSurfacePropertyType, scope=AbstractBuildingType))

AbstractBuildingType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'storeysAboveGround'), pyxb.binding.datatypes.nonNegativeInteger, scope=AbstractBuildingType))

AbstractBuildingType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiCurve'), pyxb.bundles.opengis.gml.MultiCurvePropertyType, scope=AbstractBuildingType))

AbstractBuildingType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'storeysBelowGround'), pyxb.binding.datatypes.nonNegativeInteger, scope=AbstractBuildingType))

AbstractBuildingType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'lod3TerrainIntersection'), pyxb.bundles.opengis.gml.MultiCurvePropertyType, scope=AbstractBuildingType))

AbstractBuildingType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'storeyHeightsAboveGround'), pyxb.bundles.opengis.gml.MeasureOrNullListType, scope=AbstractBuildingType))

AbstractBuildingType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'class'), BuildingClassType, scope=AbstractBuildingType))

AbstractBuildingType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'lod4Solid'), pyxb.bundles.opengis.gml.SolidPropertyType, scope=AbstractBuildingType))

AbstractBuildingType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'storeyHeightsBelowGround'), pyxb.bundles.opengis.gml.MeasureOrNullListType, scope=AbstractBuildingType))

AbstractBuildingType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiSurface'), pyxb.bundles.opengis.gml.MultiSurfacePropertyType, scope=AbstractBuildingType))

AbstractBuildingType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'lod1Solid'), pyxb.bundles.opengis.gml.SolidPropertyType, scope=AbstractBuildingType))

AbstractBuildingType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'outerBuildingInstallation'), BuildingInstallationPropertyType, scope=AbstractBuildingType))

AbstractBuildingType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiCurve'), pyxb.bundles.opengis.gml.MultiCurvePropertyType, scope=AbstractBuildingType))

AbstractBuildingType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'lod1MultiSurface'), pyxb.bundles.opengis.gml.MultiSurfacePropertyType, scope=AbstractBuildingType))

AbstractBuildingType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'lod4TerrainIntersection'), pyxb.bundles.opengis.gml.MultiCurvePropertyType, scope=AbstractBuildingType))

AbstractBuildingType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'lod1TerrainIntersection'), pyxb.bundles.opengis.gml.MultiCurvePropertyType, scope=AbstractBuildingType))

AbstractBuildingType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfAbstractBuilding'), pyxb.binding.datatypes.anyType, abstract=pyxb.binding.datatypes.boolean(1), scope=AbstractBuildingType))

AbstractBuildingType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'lod2Solid'), pyxb.bundles.opengis.gml.SolidPropertyType, scope=AbstractBuildingType))

AbstractBuildingType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'consistsOfBuildingPart'), BuildingPartPropertyType, scope=AbstractBuildingType))

AbstractBuildingType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'lod2MultiSurface'), pyxb.bundles.opengis.gml.MultiSurfacePropertyType, scope=AbstractBuildingType))

AbstractBuildingType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'address'), pyxb.bundles.opengis.citygml.base.AddressPropertyType, scope=AbstractBuildingType))

AbstractBuildingType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'lod2MultiCurve'), pyxb.bundles.opengis.gml.MultiCurvePropertyType, scope=AbstractBuildingType))

AbstractBuildingType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'interiorRoom'), InteriorRoomPropertyType, scope=AbstractBuildingType))

AbstractBuildingType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'lod2TerrainIntersection'), pyxb.bundles.opengis.gml.MultiCurvePropertyType, scope=AbstractBuildingType))

AbstractBuildingType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'yearOfConstruction'), pyxb.binding.datatypes.gYear, scope=AbstractBuildingType))

AbstractBuildingType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'usage'), BuildingUsageType, scope=AbstractBuildingType))

AbstractBuildingType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'interiorBuildingInstallation'), IntBuildingInstallationPropertyType, scope=AbstractBuildingType))
AbstractBuildingType._GroupModel_17 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'metaDataProperty')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'description')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'name')), min_occurs=0L, max_occurs=None)
    )
AbstractBuildingType._GroupModel_16 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(AbstractBuildingType._GroupModel_17, min_occurs=1, max_occurs=1)
    )
AbstractBuildingType._GroupModel_18 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'boundedBy')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'location')), min_occurs=0L, max_occurs=1)
    )
AbstractBuildingType._GroupModel_15 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(AbstractBuildingType._GroupModel_16, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(AbstractBuildingType._GroupModel_18, min_occurs=1, max_occurs=1)
    )
AbstractBuildingType._GroupModel_19 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'creationDate')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'terminationDate')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'externalReference')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'generalizesTo')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'_GenericApplicationPropertyOfCityObject')), min_occurs=0L, max_occurs=None)
    )
AbstractBuildingType._GroupModel_14 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(AbstractBuildingType._GroupModel_15, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(AbstractBuildingType._GroupModel_19, min_occurs=1, max_occurs=1)
    )
AbstractBuildingType._GroupModel_20 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'_GenericApplicationPropertyOfSite')), min_occurs=0L, max_occurs=None)
    )
AbstractBuildingType._GroupModel_13 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(AbstractBuildingType._GroupModel_14, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(AbstractBuildingType._GroupModel_20, min_occurs=1, max_occurs=1)
    )
AbstractBuildingType._GroupModel_21 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'class')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'function')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'usage')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'yearOfConstruction')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'yearOfDemolition')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'roofType')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'measuredHeight')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'storeysAboveGround')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'storeysBelowGround')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'storeyHeightsAboveGround')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'storeyHeightsBelowGround')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod1Solid')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod1MultiSurface')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod1TerrainIntersection')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2Solid')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2MultiSurface')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2MultiCurve')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2TerrainIntersection')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'outerBuildingInstallation')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'interiorBuildingInstallation')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'boundedBy')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3Solid')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiSurface')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiCurve')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3TerrainIntersection')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4Solid')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiSurface')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiCurve')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4TerrainIntersection')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'interiorRoom')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'consistsOfBuildingPart')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'address')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(AbstractBuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfAbstractBuilding')), min_occurs=0L, max_occurs=None)
    )
AbstractBuildingType._GroupModel_12 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(AbstractBuildingType._GroupModel_13, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(AbstractBuildingType._GroupModel_21, min_occurs=1, max_occurs=1)
    )
AbstractBuildingType._ContentModel = pyxb.binding.content.ParticleModel(AbstractBuildingType._GroupModel_12, min_occurs=1, max_occurs=1)



IntBuildingInstallationType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'lod4Geometry'), pyxb.bundles.opengis.gml.GeometryPropertyType, scope=IntBuildingInstallationType))

IntBuildingInstallationType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'class'), IntBuildingInstallationClassType, scope=IntBuildingInstallationType))

IntBuildingInstallationType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'function'), IntBuildingInstallationFunctionType, scope=IntBuildingInstallationType))

IntBuildingInstallationType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfIntBuildingInstallation'), pyxb.binding.datatypes.anyType, abstract=pyxb.binding.datatypes.boolean(1), scope=IntBuildingInstallationType))

IntBuildingInstallationType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'usage'), IntBuildingInstallationUsageType, scope=IntBuildingInstallationType))
IntBuildingInstallationType._GroupModel_14 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(IntBuildingInstallationType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'metaDataProperty')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(IntBuildingInstallationType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'description')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(IntBuildingInstallationType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'name')), min_occurs=0L, max_occurs=None)
    )
IntBuildingInstallationType._GroupModel_13 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(IntBuildingInstallationType._GroupModel_14, min_occurs=1, max_occurs=1)
    )
IntBuildingInstallationType._GroupModel_15 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(IntBuildingInstallationType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'boundedBy')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(IntBuildingInstallationType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'location')), min_occurs=0L, max_occurs=1)
    )
IntBuildingInstallationType._GroupModel_12 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(IntBuildingInstallationType._GroupModel_13, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(IntBuildingInstallationType._GroupModel_15, min_occurs=1, max_occurs=1)
    )
IntBuildingInstallationType._GroupModel_16 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(IntBuildingInstallationType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'creationDate')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(IntBuildingInstallationType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'terminationDate')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(IntBuildingInstallationType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'externalReference')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(IntBuildingInstallationType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'generalizesTo')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(IntBuildingInstallationType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'_GenericApplicationPropertyOfCityObject')), min_occurs=0L, max_occurs=None)
    )
IntBuildingInstallationType._GroupModel_11 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(IntBuildingInstallationType._GroupModel_12, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(IntBuildingInstallationType._GroupModel_16, min_occurs=1, max_occurs=1)
    )
IntBuildingInstallationType._GroupModel_17 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(IntBuildingInstallationType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'class')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(IntBuildingInstallationType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'function')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(IntBuildingInstallationType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'usage')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(IntBuildingInstallationType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4Geometry')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(IntBuildingInstallationType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfIntBuildingInstallation')), min_occurs=0L, max_occurs=None)
    )
IntBuildingInstallationType._GroupModel_10 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(IntBuildingInstallationType._GroupModel_11, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(IntBuildingInstallationType._GroupModel_17, min_occurs=1, max_occurs=1)
    )
IntBuildingInstallationType._ContentModel = pyxb.binding.content.ParticleModel(IntBuildingInstallationType._GroupModel_10, min_occurs=1, max_occurs=1)



FloorSurfaceType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfFloorSurface'), pyxb.binding.datatypes.anyType, abstract=pyxb.binding.datatypes.boolean(1), scope=FloorSurfaceType))
FloorSurfaceType._GroupModel_15 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(FloorSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'metaDataProperty')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(FloorSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'description')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(FloorSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'name')), min_occurs=0L, max_occurs=None)
    )
FloorSurfaceType._GroupModel_14 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(FloorSurfaceType._GroupModel_15, min_occurs=1, max_occurs=1)
    )
FloorSurfaceType._GroupModel_16 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(FloorSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'boundedBy')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(FloorSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'location')), min_occurs=0L, max_occurs=1)
    )
FloorSurfaceType._GroupModel_13 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(FloorSurfaceType._GroupModel_14, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(FloorSurfaceType._GroupModel_16, min_occurs=1, max_occurs=1)
    )
FloorSurfaceType._GroupModel_17 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(FloorSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'creationDate')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(FloorSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'terminationDate')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(FloorSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'externalReference')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(FloorSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'generalizesTo')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(FloorSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'_GenericApplicationPropertyOfCityObject')), min_occurs=0L, max_occurs=None)
    )
FloorSurfaceType._GroupModel_12 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(FloorSurfaceType._GroupModel_13, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(FloorSurfaceType._GroupModel_17, min_occurs=1, max_occurs=1)
    )
FloorSurfaceType._GroupModel_18 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(FloorSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2MultiSurface')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(FloorSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiSurface')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(FloorSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiSurface')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(FloorSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'opening')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(FloorSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfBoundarySurface')), min_occurs=0L, max_occurs=None)
    )
FloorSurfaceType._GroupModel_11 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(FloorSurfaceType._GroupModel_12, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(FloorSurfaceType._GroupModel_18, min_occurs=1, max_occurs=1)
    )
FloorSurfaceType._GroupModel_19 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(FloorSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfFloorSurface')), min_occurs=0L, max_occurs=None)
    )
FloorSurfaceType._GroupModel_10 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(FloorSurfaceType._GroupModel_11, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(FloorSurfaceType._GroupModel_19, min_occurs=1, max_occurs=1)
    )
FloorSurfaceType._ContentModel = pyxb.binding.content.ParticleModel(FloorSurfaceType._GroupModel_10, min_occurs=1, max_occurs=1)



BuildingType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfBuilding'), pyxb.binding.datatypes.anyType, abstract=pyxb.binding.datatypes.boolean(1), scope=BuildingType))
BuildingType._GroupModel_18 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(BuildingType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'metaDataProperty')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(BuildingType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'description')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(BuildingType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'name')), min_occurs=0L, max_occurs=None)
    )
BuildingType._GroupModel_17 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(BuildingType._GroupModel_18, min_occurs=1, max_occurs=1)
    )
BuildingType._GroupModel_19 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(BuildingType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'boundedBy')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(BuildingType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'location')), min_occurs=0L, max_occurs=1)
    )
BuildingType._GroupModel_16 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(BuildingType._GroupModel_17, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(BuildingType._GroupModel_19, min_occurs=1, max_occurs=1)
    )
BuildingType._GroupModel_20 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(BuildingType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'creationDate')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(BuildingType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'terminationDate')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(BuildingType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'externalReference')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(BuildingType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'generalizesTo')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(BuildingType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'_GenericApplicationPropertyOfCityObject')), min_occurs=0L, max_occurs=None)
    )
BuildingType._GroupModel_15 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(BuildingType._GroupModel_16, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(BuildingType._GroupModel_20, min_occurs=1, max_occurs=1)
    )
BuildingType._GroupModel_21 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(BuildingType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'_GenericApplicationPropertyOfSite')), min_occurs=0L, max_occurs=None)
    )
BuildingType._GroupModel_14 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(BuildingType._GroupModel_15, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(BuildingType._GroupModel_21, min_occurs=1, max_occurs=1)
    )
BuildingType._GroupModel_22 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'class')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'function')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'usage')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'yearOfConstruction')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'yearOfDemolition')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'roofType')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'measuredHeight')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'storeysAboveGround')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'storeysBelowGround')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'storeyHeightsAboveGround')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'storeyHeightsBelowGround')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod1Solid')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod1MultiSurface')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod1TerrainIntersection')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2Solid')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2MultiSurface')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2MultiCurve')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2TerrainIntersection')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'outerBuildingInstallation')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'interiorBuildingInstallation')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'boundedBy')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3Solid')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiSurface')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiCurve')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3TerrainIntersection')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4Solid')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiSurface')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiCurve')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4TerrainIntersection')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'interiorRoom')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'consistsOfBuildingPart')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'address')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfAbstractBuilding')), min_occurs=0L, max_occurs=None)
    )
BuildingType._GroupModel_13 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(BuildingType._GroupModel_14, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(BuildingType._GroupModel_22, min_occurs=1, max_occurs=1)
    )
BuildingType._GroupModel_23 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(BuildingType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfBuilding')), min_occurs=0L, max_occurs=None)
    )
BuildingType._GroupModel_12 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(BuildingType._GroupModel_13, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(BuildingType._GroupModel_23, min_occurs=1, max_occurs=1)
    )
BuildingType._ContentModel = pyxb.binding.content.ParticleModel(BuildingType._GroupModel_12, min_occurs=1, max_occurs=1)



WallSurfaceType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfWallSurface'), pyxb.binding.datatypes.anyType, abstract=pyxb.binding.datatypes.boolean(1), scope=WallSurfaceType))
WallSurfaceType._GroupModel_15 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(WallSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'metaDataProperty')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(WallSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'description')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(WallSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'name')), min_occurs=0L, max_occurs=None)
    )
WallSurfaceType._GroupModel_14 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(WallSurfaceType._GroupModel_15, min_occurs=1, max_occurs=1)
    )
WallSurfaceType._GroupModel_16 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(WallSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'boundedBy')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(WallSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'location')), min_occurs=0L, max_occurs=1)
    )
WallSurfaceType._GroupModel_13 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(WallSurfaceType._GroupModel_14, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(WallSurfaceType._GroupModel_16, min_occurs=1, max_occurs=1)
    )
WallSurfaceType._GroupModel_17 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(WallSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'creationDate')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(WallSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'terminationDate')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(WallSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'externalReference')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(WallSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'generalizesTo')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(WallSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'_GenericApplicationPropertyOfCityObject')), min_occurs=0L, max_occurs=None)
    )
WallSurfaceType._GroupModel_12 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(WallSurfaceType._GroupModel_13, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(WallSurfaceType._GroupModel_17, min_occurs=1, max_occurs=1)
    )
WallSurfaceType._GroupModel_18 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(WallSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2MultiSurface')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(WallSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiSurface')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(WallSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiSurface')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(WallSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'opening')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(WallSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfBoundarySurface')), min_occurs=0L, max_occurs=None)
    )
WallSurfaceType._GroupModel_11 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(WallSurfaceType._GroupModel_12, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(WallSurfaceType._GroupModel_18, min_occurs=1, max_occurs=1)
    )
WallSurfaceType._GroupModel_19 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(WallSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfWallSurface')), min_occurs=0L, max_occurs=None)
    )
WallSurfaceType._GroupModel_10 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(WallSurfaceType._GroupModel_11, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(WallSurfaceType._GroupModel_19, min_occurs=1, max_occurs=1)
    )
WallSurfaceType._ContentModel = pyxb.binding.content.ParticleModel(WallSurfaceType._GroupModel_10, min_occurs=1, max_occurs=1)



BuildingInstallationType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'lod3Geometry'), pyxb.bundles.opengis.gml.GeometryPropertyType, scope=BuildingInstallationType))

BuildingInstallationType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'lod2Geometry'), pyxb.bundles.opengis.gml.GeometryPropertyType, scope=BuildingInstallationType))

BuildingInstallationType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'class'), BuildingInstallationClassType, scope=BuildingInstallationType))

BuildingInstallationType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfBuildingInstallation'), pyxb.binding.datatypes.anyType, abstract=pyxb.binding.datatypes.boolean(1), scope=BuildingInstallationType))

BuildingInstallationType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'lod4Geometry'), pyxb.bundles.opengis.gml.GeometryPropertyType, scope=BuildingInstallationType))

BuildingInstallationType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'usage'), BuildingInstallationUsageType, scope=BuildingInstallationType))

BuildingInstallationType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'function'), BuildingInstallationFunctionType, scope=BuildingInstallationType))
BuildingInstallationType._GroupModel_14 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(BuildingInstallationType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'metaDataProperty')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(BuildingInstallationType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'description')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(BuildingInstallationType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'name')), min_occurs=0L, max_occurs=None)
    )
BuildingInstallationType._GroupModel_13 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(BuildingInstallationType._GroupModel_14, min_occurs=1, max_occurs=1)
    )
BuildingInstallationType._GroupModel_15 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(BuildingInstallationType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'boundedBy')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(BuildingInstallationType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'location')), min_occurs=0L, max_occurs=1)
    )
BuildingInstallationType._GroupModel_12 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(BuildingInstallationType._GroupModel_13, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(BuildingInstallationType._GroupModel_15, min_occurs=1, max_occurs=1)
    )
BuildingInstallationType._GroupModel_16 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(BuildingInstallationType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'creationDate')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(BuildingInstallationType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'terminationDate')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(BuildingInstallationType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'externalReference')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(BuildingInstallationType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'generalizesTo')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(BuildingInstallationType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'_GenericApplicationPropertyOfCityObject')), min_occurs=0L, max_occurs=None)
    )
BuildingInstallationType._GroupModel_11 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(BuildingInstallationType._GroupModel_12, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(BuildingInstallationType._GroupModel_16, min_occurs=1, max_occurs=1)
    )
BuildingInstallationType._GroupModel_17 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(BuildingInstallationType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'class')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(BuildingInstallationType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'function')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(BuildingInstallationType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'usage')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(BuildingInstallationType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2Geometry')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(BuildingInstallationType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3Geometry')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(BuildingInstallationType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4Geometry')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(BuildingInstallationType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfBuildingInstallation')), min_occurs=0L, max_occurs=None)
    )
BuildingInstallationType._GroupModel_10 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(BuildingInstallationType._GroupModel_11, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(BuildingInstallationType._GroupModel_17, min_occurs=1, max_occurs=1)
    )
BuildingInstallationType._ContentModel = pyxb.binding.content.ParticleModel(BuildingInstallationType._GroupModel_10, min_occurs=1, max_occurs=1)



BuildingPartType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfBuildingPart'), pyxb.binding.datatypes.anyType, abstract=pyxb.binding.datatypes.boolean(1), scope=BuildingPartType))
BuildingPartType._GroupModel_18 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'metaDataProperty')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'description')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'name')), min_occurs=0L, max_occurs=None)
    )
BuildingPartType._GroupModel_17 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(BuildingPartType._GroupModel_18, min_occurs=1, max_occurs=1)
    )
BuildingPartType._GroupModel_19 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'boundedBy')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'location')), min_occurs=0L, max_occurs=1)
    )
BuildingPartType._GroupModel_16 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(BuildingPartType._GroupModel_17, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(BuildingPartType._GroupModel_19, min_occurs=1, max_occurs=1)
    )
BuildingPartType._GroupModel_20 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'creationDate')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'terminationDate')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'externalReference')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'generalizesTo')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'_GenericApplicationPropertyOfCityObject')), min_occurs=0L, max_occurs=None)
    )
BuildingPartType._GroupModel_15 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(BuildingPartType._GroupModel_16, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(BuildingPartType._GroupModel_20, min_occurs=1, max_occurs=1)
    )
BuildingPartType._GroupModel_21 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'_GenericApplicationPropertyOfSite')), min_occurs=0L, max_occurs=None)
    )
BuildingPartType._GroupModel_14 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(BuildingPartType._GroupModel_15, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(BuildingPartType._GroupModel_21, min_occurs=1, max_occurs=1)
    )
BuildingPartType._GroupModel_22 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'class')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'function')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'usage')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'yearOfConstruction')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'yearOfDemolition')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'roofType')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'measuredHeight')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'storeysAboveGround')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'storeysBelowGround')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'storeyHeightsAboveGround')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'storeyHeightsBelowGround')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod1Solid')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod1MultiSurface')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod1TerrainIntersection')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2Solid')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2MultiSurface')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2MultiCurve')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2TerrainIntersection')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'outerBuildingInstallation')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'interiorBuildingInstallation')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'boundedBy')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3Solid')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiSurface')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiCurve')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3TerrainIntersection')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4Solid')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiSurface')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiCurve')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4TerrainIntersection')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'interiorRoom')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'consistsOfBuildingPart')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'address')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfAbstractBuilding')), min_occurs=0L, max_occurs=None)
    )
BuildingPartType._GroupModel_13 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(BuildingPartType._GroupModel_14, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(BuildingPartType._GroupModel_22, min_occurs=1, max_occurs=1)
    )
BuildingPartType._GroupModel_23 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(BuildingPartType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfBuildingPart')), min_occurs=0L, max_occurs=None)
    )
BuildingPartType._GroupModel_12 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(BuildingPartType._GroupModel_13, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(BuildingPartType._GroupModel_23, min_occurs=1, max_occurs=1)
    )
BuildingPartType._ContentModel = pyxb.binding.content.ParticleModel(BuildingPartType._GroupModel_12, min_occurs=1, max_occurs=1)



WindowType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfWindow'), pyxb.binding.datatypes.anyType, abstract=pyxb.binding.datatypes.boolean(1), scope=WindowType))
WindowType._GroupModel_15 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(WindowType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'metaDataProperty')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(WindowType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'description')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(WindowType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'name')), min_occurs=0L, max_occurs=None)
    )
WindowType._GroupModel_14 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(WindowType._GroupModel_15, min_occurs=1, max_occurs=1)
    )
WindowType._GroupModel_16 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(WindowType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'boundedBy')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(WindowType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'location')), min_occurs=0L, max_occurs=1)
    )
WindowType._GroupModel_13 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(WindowType._GroupModel_14, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(WindowType._GroupModel_16, min_occurs=1, max_occurs=1)
    )
WindowType._GroupModel_17 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(WindowType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'creationDate')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(WindowType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'terminationDate')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(WindowType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'externalReference')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(WindowType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'generalizesTo')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(WindowType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'_GenericApplicationPropertyOfCityObject')), min_occurs=0L, max_occurs=None)
    )
WindowType._GroupModel_12 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(WindowType._GroupModel_13, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(WindowType._GroupModel_17, min_occurs=1, max_occurs=1)
    )
WindowType._GroupModel_18 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(WindowType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiSurface')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(WindowType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiSurface')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(WindowType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfOpening')), min_occurs=0L, max_occurs=None)
    )
WindowType._GroupModel_11 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(WindowType._GroupModel_12, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(WindowType._GroupModel_18, min_occurs=1, max_occurs=1)
    )
WindowType._GroupModel_19 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(WindowType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfWindow')), min_occurs=0L, max_occurs=None)
    )
WindowType._GroupModel_10 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(WindowType._GroupModel_11, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(WindowType._GroupModel_19, min_occurs=1, max_occurs=1)
    )
WindowType._ContentModel = pyxb.binding.content.ParticleModel(WindowType._GroupModel_10, min_occurs=1, max_occurs=1)



InteriorWallSurfaceType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfInteriorWallSurface'), pyxb.binding.datatypes.anyType, abstract=pyxb.binding.datatypes.boolean(1), scope=InteriorWallSurfaceType))
InteriorWallSurfaceType._GroupModel_15 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(InteriorWallSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'metaDataProperty')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(InteriorWallSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'description')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(InteriorWallSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'name')), min_occurs=0L, max_occurs=None)
    )
InteriorWallSurfaceType._GroupModel_14 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(InteriorWallSurfaceType._GroupModel_15, min_occurs=1, max_occurs=1)
    )
InteriorWallSurfaceType._GroupModel_16 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(InteriorWallSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'boundedBy')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(InteriorWallSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'location')), min_occurs=0L, max_occurs=1)
    )
InteriorWallSurfaceType._GroupModel_13 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(InteriorWallSurfaceType._GroupModel_14, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(InteriorWallSurfaceType._GroupModel_16, min_occurs=1, max_occurs=1)
    )
InteriorWallSurfaceType._GroupModel_17 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(InteriorWallSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'creationDate')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(InteriorWallSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'terminationDate')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(InteriorWallSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'externalReference')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(InteriorWallSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'generalizesTo')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(InteriorWallSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'_GenericApplicationPropertyOfCityObject')), min_occurs=0L, max_occurs=None)
    )
InteriorWallSurfaceType._GroupModel_12 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(InteriorWallSurfaceType._GroupModel_13, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(InteriorWallSurfaceType._GroupModel_17, min_occurs=1, max_occurs=1)
    )
InteriorWallSurfaceType._GroupModel_18 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(InteriorWallSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2MultiSurface')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(InteriorWallSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiSurface')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(InteriorWallSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiSurface')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(InteriorWallSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'opening')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(InteriorWallSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfBoundarySurface')), min_occurs=0L, max_occurs=None)
    )
InteriorWallSurfaceType._GroupModel_11 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(InteriorWallSurfaceType._GroupModel_12, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(InteriorWallSurfaceType._GroupModel_18, min_occurs=1, max_occurs=1)
    )
InteriorWallSurfaceType._GroupModel_19 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(InteriorWallSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfInteriorWallSurface')), min_occurs=0L, max_occurs=None)
    )
InteriorWallSurfaceType._GroupModel_10 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(InteriorWallSurfaceType._GroupModel_11, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(InteriorWallSurfaceType._GroupModel_19, min_occurs=1, max_occurs=1)
    )
InteriorWallSurfaceType._ContentModel = pyxb.binding.content.ParticleModel(InteriorWallSurfaceType._GroupModel_10, min_occurs=1, max_occurs=1)



DoorType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfDoor'), pyxb.binding.datatypes.anyType, abstract=pyxb.binding.datatypes.boolean(1), scope=DoorType))

DoorType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'address'), pyxb.bundles.opengis.citygml.base.AddressPropertyType, scope=DoorType))
DoorType._GroupModel_15 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(DoorType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'metaDataProperty')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(DoorType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'description')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(DoorType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'name')), min_occurs=0L, max_occurs=None)
    )
DoorType._GroupModel_14 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(DoorType._GroupModel_15, min_occurs=1, max_occurs=1)
    )
DoorType._GroupModel_16 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(DoorType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'boundedBy')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(DoorType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'location')), min_occurs=0L, max_occurs=1)
    )
DoorType._GroupModel_13 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(DoorType._GroupModel_14, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(DoorType._GroupModel_16, min_occurs=1, max_occurs=1)
    )
DoorType._GroupModel_17 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(DoorType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'creationDate')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(DoorType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'terminationDate')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(DoorType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'externalReference')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(DoorType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'generalizesTo')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(DoorType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'_GenericApplicationPropertyOfCityObject')), min_occurs=0L, max_occurs=None)
    )
DoorType._GroupModel_12 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(DoorType._GroupModel_13, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(DoorType._GroupModel_17, min_occurs=1, max_occurs=1)
    )
DoorType._GroupModel_18 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(DoorType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiSurface')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(DoorType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiSurface')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(DoorType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfOpening')), min_occurs=0L, max_occurs=None)
    )
DoorType._GroupModel_11 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(DoorType._GroupModel_12, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(DoorType._GroupModel_18, min_occurs=1, max_occurs=1)
    )
DoorType._GroupModel_19 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(DoorType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'address')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(DoorType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfDoor')), min_occurs=0L, max_occurs=None)
    )
DoorType._GroupModel_10 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(DoorType._GroupModel_11, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(DoorType._GroupModel_19, min_occurs=1, max_occurs=1)
    )
DoorType._ContentModel = pyxb.binding.content.ParticleModel(DoorType._GroupModel_10, min_occurs=1, max_occurs=1)



InteriorFurniturePropertyType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'BuildingFurniture'), BuildingFurnitureType, scope=InteriorFurniturePropertyType))
InteriorFurniturePropertyType._GroupModel_ = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(InteriorFurniturePropertyType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'BuildingFurniture')), min_occurs=1, max_occurs=1)
    )
InteriorFurniturePropertyType._ContentModel = pyxb.binding.content.ParticleModel(InteriorFurniturePropertyType._GroupModel_, min_occurs=0L, max_occurs=1)



IntBuildingInstallationPropertyType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'IntBuildingInstallation'), IntBuildingInstallationType, scope=IntBuildingInstallationPropertyType))
IntBuildingInstallationPropertyType._GroupModel_ = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(IntBuildingInstallationPropertyType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'IntBuildingInstallation')), min_occurs=1, max_occurs=1)
    )
IntBuildingInstallationPropertyType._ContentModel = pyxb.binding.content.ParticleModel(IntBuildingInstallationPropertyType._GroupModel_, min_occurs=0L, max_occurs=1)



BuildingInstallationPropertyType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'BuildingInstallation'), BuildingInstallationType, scope=BuildingInstallationPropertyType))
BuildingInstallationPropertyType._GroupModel_ = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(BuildingInstallationPropertyType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'BuildingInstallation')), min_occurs=1, max_occurs=1)
    )
BuildingInstallationPropertyType._ContentModel = pyxb.binding.content.ParticleModel(BuildingInstallationPropertyType._GroupModel_, min_occurs=0L, max_occurs=1)



CeilingSurfaceType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfCeilingSurface'), pyxb.binding.datatypes.anyType, abstract=pyxb.binding.datatypes.boolean(1), scope=CeilingSurfaceType))
CeilingSurfaceType._GroupModel_15 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(CeilingSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'metaDataProperty')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(CeilingSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'description')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(CeilingSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'name')), min_occurs=0L, max_occurs=None)
    )
CeilingSurfaceType._GroupModel_14 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(CeilingSurfaceType._GroupModel_15, min_occurs=1, max_occurs=1)
    )
CeilingSurfaceType._GroupModel_16 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(CeilingSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'boundedBy')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(CeilingSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'location')), min_occurs=0L, max_occurs=1)
    )
CeilingSurfaceType._GroupModel_13 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(CeilingSurfaceType._GroupModel_14, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(CeilingSurfaceType._GroupModel_16, min_occurs=1, max_occurs=1)
    )
CeilingSurfaceType._GroupModel_17 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(CeilingSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'creationDate')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(CeilingSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'terminationDate')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(CeilingSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'externalReference')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(CeilingSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'generalizesTo')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(CeilingSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'_GenericApplicationPropertyOfCityObject')), min_occurs=0L, max_occurs=None)
    )
CeilingSurfaceType._GroupModel_12 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(CeilingSurfaceType._GroupModel_13, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(CeilingSurfaceType._GroupModel_17, min_occurs=1, max_occurs=1)
    )
CeilingSurfaceType._GroupModel_18 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(CeilingSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod2MultiSurface')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(CeilingSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod3MultiSurface')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(CeilingSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'lod4MultiSurface')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(CeilingSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'opening')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(CeilingSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfBoundarySurface')), min_occurs=0L, max_occurs=None)
    )
CeilingSurfaceType._GroupModel_11 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(CeilingSurfaceType._GroupModel_12, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(CeilingSurfaceType._GroupModel_18, min_occurs=1, max_occurs=1)
    )
CeilingSurfaceType._GroupModel_19 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(CeilingSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfCeilingSurface')), min_occurs=0L, max_occurs=None)
    )
CeilingSurfaceType._GroupModel_10 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(CeilingSurfaceType._GroupModel_11, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(CeilingSurfaceType._GroupModel_19, min_occurs=1, max_occurs=1)
    )
CeilingSurfaceType._ContentModel = pyxb.binding.content.ParticleModel(CeilingSurfaceType._GroupModel_10, min_occurs=1, max_occurs=1)



OpeningPropertyType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'_Opening'), AbstractOpeningType, abstract=pyxb.binding.datatypes.boolean(1), scope=OpeningPropertyType))
OpeningPropertyType._GroupModel_ = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(OpeningPropertyType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_Opening')), min_occurs=1, max_occurs=1)
    )
OpeningPropertyType._ContentModel = pyxb.binding.content.ParticleModel(OpeningPropertyType._GroupModel_, min_occurs=0L, max_occurs=1)



BuildingPartPropertyType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'BuildingPart'), BuildingPartType, scope=BuildingPartPropertyType))
BuildingPartPropertyType._GroupModel_ = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(BuildingPartPropertyType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'BuildingPart')), min_occurs=1, max_occurs=1)
    )
BuildingPartPropertyType._ContentModel = pyxb.binding.content.ParticleModel(BuildingPartPropertyType._GroupModel_, min_occurs=0L, max_occurs=1)

GroundSurface._setSubstitutionGroup(BoundarySurface)

ClosureSurface._setSubstitutionGroup(BoundarySurface)

RoofSurface._setSubstitutionGroup(BoundarySurface)

AbstractBuilding._setSubstitutionGroup(pyxb.bundles.opengis.citygml.base.Site)

FloorSurface._setSubstitutionGroup(BoundarySurface)

Building._setSubstitutionGroup(AbstractBuilding)

WallSurface._setSubstitutionGroup(BoundarySurface)

BuildingPart._setSubstitutionGroup(AbstractBuilding)

Opening._setSubstitutionGroup(pyxb.bundles.opengis.citygml.base.CityObject)

Window._setSubstitutionGroup(Opening)

BuildingInstallation._setSubstitutionGroup(pyxb.bundles.opengis.citygml.base.CityObject)

InteriorWallSurface._setSubstitutionGroup(BoundarySurface)

Door._setSubstitutionGroup(Opening)

IntBuildingInstallation._setSubstitutionGroup(pyxb.bundles.opengis.citygml.base.CityObject)

Room._setSubstitutionGroup(pyxb.bundles.opengis.citygml.base.CityObject)

CeilingSurface._setSubstitutionGroup(BoundarySurface)

BuildingFurniture._setSubstitutionGroup(pyxb.bundles.opengis.citygml.base.CityObject)

BoundarySurface._setSubstitutionGroup(pyxb.bundles.opengis.citygml.base.CityObject)
