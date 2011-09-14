# ./pyxb/bundles/opengis/citygml/raw/appearance.py
# PyXB bindings for NM:4eab4d25f54c999b91cd172921f2cc6ee7e6addb
# Generated 2011-09-09 14:19:17.409669 by PyXB version 1.1.3
# Namespace http://www.opengis.net/citygml/appearance/1.0

import pyxb
import pyxb.binding
import pyxb.binding.saxer
import StringIO
import pyxb.utils.utility
import pyxb.utils.domutils
import sys

# Unique identifier for bindings created at the same time
_GenerationUID = pyxb.utils.utility.UniqueIdentifier('urn:uuid:9bf2ba68-db18-11e0-9101-001fbc013adc')

# Import bindings for namespaces imported into schema
import pyxb.bundles.opengis.citygml.base
import pyxb.binding.datatypes
import pyxb.bundles.opengis.gml
import pyxb.bundles.opengis.misc.xlinks

Namespace = pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/appearance/1.0', create_if_missing=True)
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
# superclasses pyxb.bundles.opengis.citygml.base.doubleBetween0and1List
class Color (pyxb.binding.basis.STD_list):

    """List of three values (red, green, blue), separated by spaces. The values must be in the range
                between zero and one. """

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'Color')
    _Documentation = u'List of three values (red, green, blue), separated by spaces. The values must be in the range\n                between zero and one. '

    _ItemType = pyxb.bundles.opengis.citygml.base.doubleBetween0and1
Color._CF_length = pyxb.binding.facets.CF_length(value=pyxb.binding.datatypes.nonNegativeInteger(3L))
Color._InitializeFacetMap(Color._CF_length)
Namespace.addCategoryObject('typeBinding', u'Color', Color)

# Atomic SimpleTypeDefinition
class WrapModeType (pyxb.binding.datatypes.string, pyxb.binding.basis.enumeration_mixin):

    """Fill mode for a texture. "wrap" repeats the texture, "clamp" extends the edges of the texture, and
                "border" fills all undefined areas with "borderColor" """

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'WrapModeType')
    _Documentation = u'Fill mode for a texture. "wrap" repeats the texture, "clamp" extends the edges of the texture, and\n                "border" fills all undefined areas with "borderColor"'
WrapModeType._CF_enumeration = pyxb.binding.facets.CF_enumeration(value_datatype=WrapModeType, enum_prefix=None)
WrapModeType.none = WrapModeType._CF_enumeration.addEnumeration(unicode_value=u'none', tag=u'none')
WrapModeType.wrap = WrapModeType._CF_enumeration.addEnumeration(unicode_value=u'wrap', tag=u'wrap')
WrapModeType.mirror = WrapModeType._CF_enumeration.addEnumeration(unicode_value=u'mirror', tag=u'mirror')
WrapModeType.clamp = WrapModeType._CF_enumeration.addEnumeration(unicode_value=u'clamp', tag=u'clamp')
WrapModeType.border = WrapModeType._CF_enumeration.addEnumeration(unicode_value=u'border', tag=u'border')
WrapModeType._InitializeFacetMap(WrapModeType._CF_enumeration)
Namespace.addCategoryObject('typeBinding', u'WrapModeType', WrapModeType)

# List SimpleTypeDefinition
# superclasses pyxb.bundles.opengis.citygml.base.doubleBetween0and1List
class ColorPlusOpacity (pyxb.binding.basis.STD_list):

    """List of three or four values (red, green, blue, opacity), separated by spaces. The values must be in
                the range between zero and one. If no opacity is given, it is assumed as 1.0."""

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'ColorPlusOpacity')
    _Documentation = u'List of three or four values (red, green, blue, opacity), separated by spaces. The values must be in\n                the range between zero and one. If no opacity is given, it is assumed as 1.0.'

    _ItemType = pyxb.bundles.opengis.citygml.base.doubleBetween0and1
ColorPlusOpacity._CF_maxLength = pyxb.binding.facets.CF_maxLength(value=pyxb.binding.datatypes.nonNegativeInteger(4L))
ColorPlusOpacity._CF_minLength = pyxb.binding.facets.CF_minLength(value=pyxb.binding.datatypes.nonNegativeInteger(3L))
ColorPlusOpacity._InitializeFacetMap(ColorPlusOpacity._CF_maxLength,
   ColorPlusOpacity._CF_minLength)
Namespace.addCategoryObject('typeBinding', u'ColorPlusOpacity', ColorPlusOpacity)

# Atomic SimpleTypeDefinition
class TextureTypeType (pyxb.binding.datatypes.string, pyxb.binding.basis.enumeration_mixin):

    """Textures can be qualified by the attribute textureType. The textureType differentiates between
                textures, which are specific for a certain object and are only used for that object (specific), and prototypic
                textures being typical for that kind of object and are used many times for all objects of that kind (typical). A
                typical texture may be replaced by a specific, if available. Textures may also be classified as unknown.
            """

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'TextureTypeType')
    _Documentation = u'Textures can be qualified by the attribute textureType. The textureType differentiates between\n                textures, which are specific for a certain object and are only used for that object (specific), and prototypic\n                textures being typical for that kind of object and are used many times for all objects of that kind (typical). A\n                typical texture may be replaced by a specific, if available. Textures may also be classified as unknown.\n            '
TextureTypeType._CF_enumeration = pyxb.binding.facets.CF_enumeration(value_datatype=TextureTypeType, enum_prefix=None)
TextureTypeType.specific = TextureTypeType._CF_enumeration.addEnumeration(unicode_value=u'specific', tag=u'specific')
TextureTypeType.typical = TextureTypeType._CF_enumeration.addEnumeration(unicode_value=u'typical', tag=u'typical')
TextureTypeType.unknown = TextureTypeType._CF_enumeration.addEnumeration(unicode_value=u'unknown', tag=u'unknown')
TextureTypeType._InitializeFacetMap(TextureTypeType._CF_enumeration)
Namespace.addCategoryObject('typeBinding', u'TextureTypeType', TextureTypeType)

# Complex type AppearancePropertyType with content type ELEMENT_ONLY
class AppearancePropertyType (pyxb.bundles.opengis.gml.FeaturePropertyType):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'AppearancePropertyType')
    # Base type is pyxb.bundles.opengis.gml.FeaturePropertyType
    
    # Element Feature ({http://www.opengis.net/gml}_Feature) inherited from {http://www.opengis.net/gml}FeaturePropertyType
    
    # Element {http://www.opengis.net/citygml/appearance/1.0}Appearance uses Python identifier Appearance
    __Appearance = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'Appearance'), 'Appearance', '__httpwww_opengis_netcitygmlappearance1_0_AppearancePropertyType_httpwww_opengis_netcitygmlappearance1_0Appearance', False)

    
    Appearance = property(__Appearance.value, __Appearance.set, None, None)

    
    # Attribute arcrole inherited from {http://www.opengis.net/gml}FeaturePropertyType
    
    # Attribute type inherited from {http://www.opengis.net/gml}FeaturePropertyType
    
    # Attribute role inherited from {http://www.opengis.net/gml}FeaturePropertyType
    
    # Attribute href inherited from {http://www.opengis.net/gml}FeaturePropertyType
    
    # Attribute title inherited from {http://www.opengis.net/gml}FeaturePropertyType
    
    # Attribute actuate inherited from {http://www.opengis.net/gml}FeaturePropertyType
    
    # Attribute show inherited from {http://www.opengis.net/gml}FeaturePropertyType
    
    # Attribute remoteSchema inherited from {http://www.opengis.net/gml}FeaturePropertyType

    _ElementMap = pyxb.bundles.opengis.gml.FeaturePropertyType._ElementMap.copy()
    _ElementMap.update({
        __Appearance.name() : __Appearance
    })
    _AttributeMap = pyxb.bundles.opengis.gml.FeaturePropertyType._AttributeMap.copy()
    _AttributeMap.update({
        
    })
Namespace.addCategoryObject('typeBinding', u'AppearancePropertyType', AppearancePropertyType)


# Complex type AbstractSurfaceDataType with content type ELEMENT_ONLY
class AbstractSurfaceDataType (pyxb.bundles.opengis.gml.AbstractFeatureType):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'AbstractSurfaceDataType')
    # Base type is pyxb.bundles.opengis.gml.AbstractFeatureType
    
    # Element description ({http://www.opengis.net/gml}description) inherited from {http://www.opengis.net/gml}AbstractGMLType
    
    # Element metaDataProperty ({http://www.opengis.net/gml}metaDataProperty) inherited from {http://www.opengis.net/gml}AbstractGMLType
    
    # Element {http://www.opengis.net/citygml/appearance/1.0}isFront uses Python identifier isFront
    __isFront = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'isFront'), 'isFront', '__httpwww_opengis_netcitygmlappearance1_0_AbstractSurfaceDataType_httpwww_opengis_netcitygmlappearance1_0isFront', False)

    
    isFront = property(__isFront.value, __isFront.set, None, None)

    
    # Element location ({http://www.opengis.net/gml}location) inherited from {http://www.opengis.net/gml}AbstractFeatureType
    
    # Element {http://www.opengis.net/citygml/appearance/1.0}_GenericApplicationPropertyOfSurfaceData uses Python identifier GenericApplicationPropertyOfSurfaceData
    __GenericApplicationPropertyOfSurfaceData = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfSurfaceData'), 'GenericApplicationPropertyOfSurfaceData', '__httpwww_opengis_netcitygmlappearance1_0_AbstractSurfaceDataType_httpwww_opengis_netcitygmlappearance1_0_GenericApplicationPropertyOfSurfaceData', True)

    
    GenericApplicationPropertyOfSurfaceData = property(__GenericApplicationPropertyOfSurfaceData.value, __GenericApplicationPropertyOfSurfaceData.set, None, None)

    
    # Element boundedBy ({http://www.opengis.net/gml}boundedBy) inherited from {http://www.opengis.net/gml}AbstractFeatureType
    
    # Element name ({http://www.opengis.net/gml}name) inherited from {http://www.opengis.net/gml}AbstractGMLType
    
    # Attribute id inherited from {http://www.opengis.net/gml}AbstractGMLType

    _ElementMap = pyxb.bundles.opengis.gml.AbstractFeatureType._ElementMap.copy()
    _ElementMap.update({
        __isFront.name() : __isFront,
        __GenericApplicationPropertyOfSurfaceData.name() : __GenericApplicationPropertyOfSurfaceData
    })
    _AttributeMap = pyxb.bundles.opengis.gml.AbstractFeatureType._AttributeMap.copy()
    _AttributeMap.update({
        
    })
Namespace.addCategoryObject('typeBinding', u'AbstractSurfaceDataType', AbstractSurfaceDataType)


# Complex type CTD_ANON with content type SIMPLE
class CTD_ANON (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = pyxb.bundles.opengis.citygml.base.TransformationMatrix3x4Type
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_SIMPLE
    _Abstract = False
    _ExpandedName = None
    # Base type is pyxb.bundles.opengis.citygml.base.TransformationMatrix3x4Type
    
    # Attribute axisLabels uses Python identifier axisLabels
    __axisLabels = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'axisLabels'), 'axisLabels', '__httpwww_opengis_netcitygmlappearance1_0_CTD_ANON_axisLabels', pyxb.bundles.opengis.gml.NCNameList)
    
    axisLabels = property(__axisLabels.value, __axisLabels.set, None, u'Ordered list of labels for all the axes of this CRS. The gml:axisAbbrev value should be used for these axis \n\t\t\t\tlabels, after spaces and forbiddden characters are removed. When the srsName attribute is included, this attribute is optional. \n\t\t\t\tWhen the srsName attribute is omitted, this attribute shall also be omitted.')

    
    # Attribute srsName uses Python identifier srsName
    __srsName = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'srsName'), 'srsName', '__httpwww_opengis_netcitygmlappearance1_0_CTD_ANON_srsName', pyxb.binding.datatypes.anyURI)
    
    srsName = property(__srsName.value, __srsName.set, None, u'In general this reference points to a CRS instance of gml:CoordinateReferenceSystemType \n\t\t\t\t(see coordinateReferenceSystems.xsd). For well known references it is not required that the CRS description exists at the \n\t\t\t\tlocation the URI points to. If no srsName attribute is given, the CRS must be specified as part of the larger context this \n\t\t\t\tgeometry element is part of, e.g. a geometric element like point, curve, etc. It is expected that this attribute will be specified \n\t\t\t\tat the direct position level only in rare cases.')

    
    # Attribute srsDimension uses Python identifier srsDimension
    __srsDimension = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'srsDimension'), 'srsDimension', '__httpwww_opengis_netcitygmlappearance1_0_CTD_ANON_srsDimension', pyxb.binding.datatypes.positiveInteger)
    
    srsDimension = property(__srsDimension.value, __srsDimension.set, None, u'The "srsDimension" is the length of coordinate sequence (the number of entries in the list). This dimension is \n\t\t\t\tspecified by the coordinate reference system. When the srsName attribute is omitted, this attribute shall be omitted.')

    
    # Attribute uomLabels uses Python identifier uomLabels
    __uomLabels = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'uomLabels'), 'uomLabels', '__httpwww_opengis_netcitygmlappearance1_0_CTD_ANON_uomLabels', pyxb.bundles.opengis.gml.NCNameList)
    
    uomLabels = property(__uomLabels.value, __uomLabels.set, None, u'Ordered list of unit of measure (uom) labels for all the axes of this CRS. The value of the string in the \n\t\t\t\tgml:catalogSymbol should be used for this uom labels, after spaces and forbiddden characters are removed. When the \n\t\t\t\taxisLabels attribute is included, this attribute shall also be included. When the axisLabels attribute is omitted, this attribute \n\t\t\t\tshall also be omitted.')


    _ElementMap = {
        
    }
    _AttributeMap = {
        __axisLabels.name() : __axisLabels,
        __srsName.name() : __srsName,
        __srsDimension.name() : __srsDimension,
        __uomLabels.name() : __uomLabels
    }



# Complex type TextureAssociationType with content type ELEMENT_ONLY
class TextureAssociationType (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'TextureAssociationType')
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {http://www.opengis.net/citygml/appearance/1.0}_TextureParameterization uses Python identifier TextureParameterization
    __TextureParameterization = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'_TextureParameterization'), 'TextureParameterization', '__httpwww_opengis_netcitygmlappearance1_0_TextureAssociationType_httpwww_opengis_netcitygmlappearance1_0_TextureParameterization', False)

    
    TextureParameterization = property(__TextureParameterization.value, __TextureParameterization.set, None, None)

    
    # Attribute uri uses Python identifier uri
    __uri = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'uri'), 'uri', '__httpwww_opengis_netcitygmlappearance1_0_TextureAssociationType_uri', pyxb.binding.datatypes.anyURI, required=True)
    
    uri = property(__uri.value, __uri.set, None, None)

    
    # Attribute {http://www.w3.org/1999/xlink}show uses Python identifier show
    __show = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'show'), 'show', '__httpwww_opengis_netcitygmlappearance1_0_TextureAssociationType_httpwww_w3_org1999xlinkshow', pyxb.bundles.opengis.misc.xlinks.STD_ANON_)
    
    show = property(__show.value, __show.set, None, u"\n        The 'show' attribute is used to communicate the desired presentation \n        of the ending resource on traversal from the starting resource; it's \n        value should be treated as follows: \n        new - load ending resource in a new window, frame, pane, or other \n              presentation context\n        replace - load the resource in the same window, frame, pane, or \n                  other presentation context\n        embed - load ending resource in place of the presentation of the \n                starting resource\n        other - behavior is unconstrained; examine other markup in the \n                link for hints \n        none - behavior is unconstrained \n      ")

    
    # Attribute {http://www.opengis.net/gml}remoteSchema uses Python identifier remoteSchema
    __remoteSchema = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'remoteSchema'), 'remoteSchema', '__httpwww_opengis_netcitygmlappearance1_0_TextureAssociationType_httpwww_opengis_netgmlremoteSchema', pyxb.binding.datatypes.anyURI)
    
    remoteSchema = property(__remoteSchema.value, __remoteSchema.set, None, u'Reference to an XML Schema fragment that specifies the content model of the propertys value. This is in conformance with the XML Schema Section 4.14 Referencing Schemas from Elsewhere.')

    
    # Attribute {http://www.w3.org/1999/xlink}role uses Python identifier role
    __role = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'role'), 'role', '__httpwww_opengis_netcitygmlappearance1_0_TextureAssociationType_httpwww_w3_org1999xlinkrole', pyxb.binding.datatypes.anyURI)
    
    role = property(__role.value, __role.set, None, None)

    
    # Attribute {http://www.w3.org/1999/xlink}href uses Python identifier href
    __href = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'href'), 'href', '__httpwww_opengis_netcitygmlappearance1_0_TextureAssociationType_httpwww_w3_org1999xlinkhref', pyxb.binding.datatypes.anyURI)
    
    href = property(__href.value, __href.set, None, None)

    
    # Attribute {http://www.w3.org/1999/xlink}title uses Python identifier title
    __title = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'title'), 'title', '__httpwww_opengis_netcitygmlappearance1_0_TextureAssociationType_httpwww_w3_org1999xlinktitle', pyxb.binding.datatypes.string)
    
    title = property(__title.value, __title.set, None, None)

    
    # Attribute {http://www.w3.org/1999/xlink}arcrole uses Python identifier arcrole
    __arcrole = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'arcrole'), 'arcrole', '__httpwww_opengis_netcitygmlappearance1_0_TextureAssociationType_httpwww_w3_org1999xlinkarcrole', pyxb.binding.datatypes.anyURI)
    
    arcrole = property(__arcrole.value, __arcrole.set, None, None)

    
    # Attribute {http://www.w3.org/1999/xlink}type uses Python identifier type
    __type = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'type'), 'type', '__httpwww_opengis_netcitygmlappearance1_0_TextureAssociationType_httpwww_w3_org1999xlinktype', pyxb.binding.datatypes.string, fixed=True, unicode_default=u'simple')
    
    type = property(__type.value, __type.set, None, None)

    
    # Attribute {http://www.w3.org/1999/xlink}actuate uses Python identifier actuate
    __actuate = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'actuate'), 'actuate', '__httpwww_opengis_netcitygmlappearance1_0_TextureAssociationType_httpwww_w3_org1999xlinkactuate', pyxb.bundles.opengis.misc.xlinks.STD_ANON)
    
    actuate = property(__actuate.value, __actuate.set, None, u"\n        The 'actuate' attribute is used to communicate the desired timing \n        of traversal from the starting resource to the ending resource; \n        it's value should be treated as follows:\n        onLoad - traverse to the ending resource immediately on loading \n                 the starting resource \n        onRequest - traverse from the starting resource to the ending \n                    resource only on a post-loading event triggered for \n                    this purpose \n        other - behavior is unconstrained; examine other markup in link \n                for hints \n        none - behavior is unconstrained\n      ")


    _ElementMap = {
        __TextureParameterization.name() : __TextureParameterization
    }
    _AttributeMap = {
        __uri.name() : __uri,
        __show.name() : __show,
        __remoteSchema.name() : __remoteSchema,
        __role.name() : __role,
        __href.name() : __href,
        __title.name() : __title,
        __arcrole.name() : __arcrole,
        __type.name() : __type,
        __actuate.name() : __actuate
    }
Namespace.addCategoryObject('typeBinding', u'TextureAssociationType', TextureAssociationType)


# Complex type AbstractTextureParameterizationType with content type ELEMENT_ONLY
class AbstractTextureParameterizationType (pyxb.bundles.opengis.gml.AbstractGMLType):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = True
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'AbstractTextureParameterizationType')
    # Base type is pyxb.bundles.opengis.gml.AbstractGMLType
    
    # Element metaDataProperty ({http://www.opengis.net/gml}metaDataProperty) inherited from {http://www.opengis.net/gml}AbstractGMLType
    
    # Element {http://www.opengis.net/citygml/appearance/1.0}_GenericApplicationPropertyOfTextureParameterization uses Python identifier GenericApplicationPropertyOfTextureParameterization
    __GenericApplicationPropertyOfTextureParameterization = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfTextureParameterization'), 'GenericApplicationPropertyOfTextureParameterization', '__httpwww_opengis_netcitygmlappearance1_0_AbstractTextureParameterizationType_httpwww_opengis_netcitygmlappearance1_0_GenericApplicationPropertyOfTextureParameterization', True)

    
    GenericApplicationPropertyOfTextureParameterization = property(__GenericApplicationPropertyOfTextureParameterization.value, __GenericApplicationPropertyOfTextureParameterization.set, None, None)

    
    # Element description ({http://www.opengis.net/gml}description) inherited from {http://www.opengis.net/gml}AbstractGMLType
    
    # Element name ({http://www.opengis.net/gml}name) inherited from {http://www.opengis.net/gml}AbstractGMLType
    
    # Attribute id inherited from {http://www.opengis.net/gml}AbstractGMLType

    _ElementMap = pyxb.bundles.opengis.gml.AbstractGMLType._ElementMap.copy()
    _ElementMap.update({
        __GenericApplicationPropertyOfTextureParameterization.name() : __GenericApplicationPropertyOfTextureParameterization
    })
    _AttributeMap = pyxb.bundles.opengis.gml.AbstractGMLType._AttributeMap.copy()
    _AttributeMap.update({
        
    })
Namespace.addCategoryObject('typeBinding', u'AbstractTextureParameterizationType', AbstractTextureParameterizationType)


# Complex type X3DMaterialType with content type ELEMENT_ONLY
class X3DMaterialType (AbstractSurfaceDataType):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'X3DMaterialType')
    # Base type is AbstractSurfaceDataType
    
    # Element {http://www.opengis.net/citygml/appearance/1.0}ambientIntensity uses Python identifier ambientIntensity
    __ambientIntensity = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'ambientIntensity'), 'ambientIntensity', '__httpwww_opengis_netcitygmlappearance1_0_X3DMaterialType_httpwww_opengis_netcitygmlappearance1_0ambientIntensity', False)

    
    ambientIntensity = property(__ambientIntensity.value, __ambientIntensity.set, None, None)

    
    # Element metaDataProperty ({http://www.opengis.net/gml}metaDataProperty) inherited from {http://www.opengis.net/gml}AbstractGMLType
    
    # Element {http://www.opengis.net/citygml/appearance/1.0}_GenericApplicationPropertyOfX3DMaterial uses Python identifier GenericApplicationPropertyOfX3DMaterial
    __GenericApplicationPropertyOfX3DMaterial = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfX3DMaterial'), 'GenericApplicationPropertyOfX3DMaterial', '__httpwww_opengis_netcitygmlappearance1_0_X3DMaterialType_httpwww_opengis_netcitygmlappearance1_0_GenericApplicationPropertyOfX3DMaterial', True)

    
    GenericApplicationPropertyOfX3DMaterial = property(__GenericApplicationPropertyOfX3DMaterial.value, __GenericApplicationPropertyOfX3DMaterial.set, None, None)

    
    # Element {http://www.opengis.net/citygml/appearance/1.0}diffuseColor uses Python identifier diffuseColor
    __diffuseColor = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'diffuseColor'), 'diffuseColor', '__httpwww_opengis_netcitygmlappearance1_0_X3DMaterialType_httpwww_opengis_netcitygmlappearance1_0diffuseColor', False)

    
    diffuseColor = property(__diffuseColor.value, __diffuseColor.set, None, None)

    
    # Element description ({http://www.opengis.net/gml}description) inherited from {http://www.opengis.net/gml}AbstractGMLType
    
    # Element location ({http://www.opengis.net/gml}location) inherited from {http://www.opengis.net/gml}AbstractFeatureType
    
    # Element {http://www.opengis.net/citygml/appearance/1.0}target uses Python identifier target
    __target = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'target'), 'target', '__httpwww_opengis_netcitygmlappearance1_0_X3DMaterialType_httpwww_opengis_netcitygmlappearance1_0target', True)

    
    target = property(__target.value, __target.set, None, None)

    
    # Element {http://www.opengis.net/citygml/appearance/1.0}isSmooth uses Python identifier isSmooth
    __isSmooth = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'isSmooth'), 'isSmooth', '__httpwww_opengis_netcitygmlappearance1_0_X3DMaterialType_httpwww_opengis_netcitygmlappearance1_0isSmooth', False)

    
    isSmooth = property(__isSmooth.value, __isSmooth.set, None, None)

    
    # Element isFront ({http://www.opengis.net/citygml/appearance/1.0}isFront) inherited from {http://www.opengis.net/citygml/appearance/1.0}AbstractSurfaceDataType
    
    # Element GenericApplicationPropertyOfSurfaceData ({http://www.opengis.net/citygml/appearance/1.0}_GenericApplicationPropertyOfSurfaceData) inherited from {http://www.opengis.net/citygml/appearance/1.0}AbstractSurfaceDataType
    
    # Element {http://www.opengis.net/citygml/appearance/1.0}transparency uses Python identifier transparency
    __transparency = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'transparency'), 'transparency', '__httpwww_opengis_netcitygmlappearance1_0_X3DMaterialType_httpwww_opengis_netcitygmlappearance1_0transparency', False)

    
    transparency = property(__transparency.value, __transparency.set, None, None)

    
    # Element {http://www.opengis.net/citygml/appearance/1.0}emissiveColor uses Python identifier emissiveColor
    __emissiveColor = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'emissiveColor'), 'emissiveColor', '__httpwww_opengis_netcitygmlappearance1_0_X3DMaterialType_httpwww_opengis_netcitygmlappearance1_0emissiveColor', False)

    
    emissiveColor = property(__emissiveColor.value, __emissiveColor.set, None, None)

    
    # Element {http://www.opengis.net/citygml/appearance/1.0}specularColor uses Python identifier specularColor
    __specularColor = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'specularColor'), 'specularColor', '__httpwww_opengis_netcitygmlappearance1_0_X3DMaterialType_httpwww_opengis_netcitygmlappearance1_0specularColor', False)

    
    specularColor = property(__specularColor.value, __specularColor.set, None, None)

    
    # Element boundedBy ({http://www.opengis.net/gml}boundedBy) inherited from {http://www.opengis.net/gml}AbstractFeatureType
    
    # Element {http://www.opengis.net/citygml/appearance/1.0}shininess uses Python identifier shininess
    __shininess = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'shininess'), 'shininess', '__httpwww_opengis_netcitygmlappearance1_0_X3DMaterialType_httpwww_opengis_netcitygmlappearance1_0shininess', False)

    
    shininess = property(__shininess.value, __shininess.set, None, None)

    
    # Element name ({http://www.opengis.net/gml}name) inherited from {http://www.opengis.net/gml}AbstractGMLType
    
    # Attribute id inherited from {http://www.opengis.net/gml}AbstractGMLType

    _ElementMap = AbstractSurfaceDataType._ElementMap.copy()
    _ElementMap.update({
        __ambientIntensity.name() : __ambientIntensity,
        __GenericApplicationPropertyOfX3DMaterial.name() : __GenericApplicationPropertyOfX3DMaterial,
        __diffuseColor.name() : __diffuseColor,
        __target.name() : __target,
        __isSmooth.name() : __isSmooth,
        __transparency.name() : __transparency,
        __emissiveColor.name() : __emissiveColor,
        __specularColor.name() : __specularColor,
        __shininess.name() : __shininess
    })
    _AttributeMap = AbstractSurfaceDataType._AttributeMap.copy()
    _AttributeMap.update({
        
    })
Namespace.addCategoryObject('typeBinding', u'X3DMaterialType', X3DMaterialType)


# Complex type CTD_ANON_ with content type SIMPLE
class CTD_ANON_ (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = pyxb.bundles.opengis.gml.doubleList
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_SIMPLE
    _Abstract = False
    _ExpandedName = None
    # Base type is pyxb.bundles.opengis.gml.doubleList
    
    # Attribute ring uses Python identifier ring
    __ring = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'ring'), 'ring', '__httpwww_opengis_netcitygmlappearance1_0_CTD_ANON__ring', pyxb.binding.datatypes.anyURI, required=True)
    
    ring = property(__ring.value, __ring.set, None, None)


    _ElementMap = {
        
    }
    _AttributeMap = {
        __ring.name() : __ring
    }



# Complex type AbstractTextureType with content type ELEMENT_ONLY
class AbstractTextureType (AbstractSurfaceDataType):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'AbstractTextureType')
    # Base type is AbstractSurfaceDataType
    
    # Element {http://www.opengis.net/citygml/appearance/1.0}imageURI uses Python identifier imageURI
    __imageURI = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'imageURI'), 'imageURI', '__httpwww_opengis_netcitygmlappearance1_0_AbstractTextureType_httpwww_opengis_netcitygmlappearance1_0imageURI', False)

    
    imageURI = property(__imageURI.value, __imageURI.set, None, None)

    
    # Element description ({http://www.opengis.net/gml}description) inherited from {http://www.opengis.net/gml}AbstractGMLType
    
    # Element {http://www.opengis.net/citygml/appearance/1.0}borderColor uses Python identifier borderColor
    __borderColor = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'borderColor'), 'borderColor', '__httpwww_opengis_netcitygmlappearance1_0_AbstractTextureType_httpwww_opengis_netcitygmlappearance1_0borderColor', False)

    
    borderColor = property(__borderColor.value, __borderColor.set, None, None)

    
    # Element isFront ({http://www.opengis.net/citygml/appearance/1.0}isFront) inherited from {http://www.opengis.net/citygml/appearance/1.0}AbstractSurfaceDataType
    
    # Element name ({http://www.opengis.net/gml}name) inherited from {http://www.opengis.net/gml}AbstractGMLType
    
    # Element {http://www.opengis.net/citygml/appearance/1.0}_GenericApplicationPropertyOfTexture uses Python identifier GenericApplicationPropertyOfTexture
    __GenericApplicationPropertyOfTexture = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfTexture'), 'GenericApplicationPropertyOfTexture', '__httpwww_opengis_netcitygmlappearance1_0_AbstractTextureType_httpwww_opengis_netcitygmlappearance1_0_GenericApplicationPropertyOfTexture', True)

    
    GenericApplicationPropertyOfTexture = property(__GenericApplicationPropertyOfTexture.value, __GenericApplicationPropertyOfTexture.set, None, None)

    
    # Element location ({http://www.opengis.net/gml}location) inherited from {http://www.opengis.net/gml}AbstractFeatureType
    
    # Element {http://www.opengis.net/citygml/appearance/1.0}textureType uses Python identifier textureType
    __textureType = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'textureType'), 'textureType', '__httpwww_opengis_netcitygmlappearance1_0_AbstractTextureType_httpwww_opengis_netcitygmlappearance1_0textureType', False)

    
    textureType = property(__textureType.value, __textureType.set, None, None)

    
    # Element GenericApplicationPropertyOfSurfaceData ({http://www.opengis.net/citygml/appearance/1.0}_GenericApplicationPropertyOfSurfaceData) inherited from {http://www.opengis.net/citygml/appearance/1.0}AbstractSurfaceDataType
    
    # Element {http://www.opengis.net/citygml/appearance/1.0}mimeType uses Python identifier mimeType
    __mimeType = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'mimeType'), 'mimeType', '__httpwww_opengis_netcitygmlappearance1_0_AbstractTextureType_httpwww_opengis_netcitygmlappearance1_0mimeType', False)

    
    mimeType = property(__mimeType.value, __mimeType.set, None, None)

    
    # Element {http://www.opengis.net/citygml/appearance/1.0}wrapMode uses Python identifier wrapMode
    __wrapMode = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'wrapMode'), 'wrapMode', '__httpwww_opengis_netcitygmlappearance1_0_AbstractTextureType_httpwww_opengis_netcitygmlappearance1_0wrapMode', False)

    
    wrapMode = property(__wrapMode.value, __wrapMode.set, None, None)

    
    # Element boundedBy ({http://www.opengis.net/gml}boundedBy) inherited from {http://www.opengis.net/gml}AbstractFeatureType
    
    # Element metaDataProperty ({http://www.opengis.net/gml}metaDataProperty) inherited from {http://www.opengis.net/gml}AbstractGMLType
    
    # Attribute id inherited from {http://www.opengis.net/gml}AbstractGMLType

    _ElementMap = AbstractSurfaceDataType._ElementMap.copy()
    _ElementMap.update({
        __imageURI.name() : __imageURI,
        __borderColor.name() : __borderColor,
        __GenericApplicationPropertyOfTexture.name() : __GenericApplicationPropertyOfTexture,
        __textureType.name() : __textureType,
        __mimeType.name() : __mimeType,
        __wrapMode.name() : __wrapMode
    })
    _AttributeMap = AbstractSurfaceDataType._AttributeMap.copy()
    _AttributeMap.update({
        
    })
Namespace.addCategoryObject('typeBinding', u'AbstractTextureType', AbstractTextureType)


# Complex type TexCoordListType with content type ELEMENT_ONLY
class TexCoordListType (AbstractTextureParameterizationType):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'TexCoordListType')
    # Base type is AbstractTextureParameterizationType
    
    # Element {http://www.opengis.net/citygml/appearance/1.0}_GenericApplicationPropertyOfTexCoordList uses Python identifier GenericApplicationPropertyOfTexCoordList
    __GenericApplicationPropertyOfTexCoordList = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfTexCoordList'), 'GenericApplicationPropertyOfTexCoordList', '__httpwww_opengis_netcitygmlappearance1_0_TexCoordListType_httpwww_opengis_netcitygmlappearance1_0_GenericApplicationPropertyOfTexCoordList', True)

    
    GenericApplicationPropertyOfTexCoordList = property(__GenericApplicationPropertyOfTexCoordList.value, __GenericApplicationPropertyOfTexCoordList.set, None, None)

    
    # Element metaDataProperty ({http://www.opengis.net/gml}metaDataProperty) inherited from {http://www.opengis.net/gml}AbstractGMLType
    
    # Element {http://www.opengis.net/citygml/appearance/1.0}textureCoordinates uses Python identifier textureCoordinates
    __textureCoordinates = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'textureCoordinates'), 'textureCoordinates', '__httpwww_opengis_netcitygmlappearance1_0_TexCoordListType_httpwww_opengis_netcitygmlappearance1_0textureCoordinates', True)

    
    textureCoordinates = property(__textureCoordinates.value, __textureCoordinates.set, None, None)

    
    # Element description ({http://www.opengis.net/gml}description) inherited from {http://www.opengis.net/gml}AbstractGMLType
    
    # Element GenericApplicationPropertyOfTextureParameterization ({http://www.opengis.net/citygml/appearance/1.0}_GenericApplicationPropertyOfTextureParameterization) inherited from {http://www.opengis.net/citygml/appearance/1.0}AbstractTextureParameterizationType
    
    # Element name ({http://www.opengis.net/gml}name) inherited from {http://www.opengis.net/gml}AbstractGMLType
    
    # Attribute id inherited from {http://www.opengis.net/gml}AbstractGMLType

    _ElementMap = AbstractTextureParameterizationType._ElementMap.copy()
    _ElementMap.update({
        __GenericApplicationPropertyOfTexCoordList.name() : __GenericApplicationPropertyOfTexCoordList,
        __textureCoordinates.name() : __textureCoordinates
    })
    _AttributeMap = AbstractTextureParameterizationType._AttributeMap.copy()
    _AttributeMap.update({
        
    })
Namespace.addCategoryObject('typeBinding', u'TexCoordListType', TexCoordListType)


# Complex type GeoreferencedTextureType with content type ELEMENT_ONLY
class GeoreferencedTextureType (AbstractTextureType):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'GeoreferencedTextureType')
    # Base type is AbstractTextureType
    
    # Element imageURI ({http://www.opengis.net/citygml/appearance/1.0}imageURI) inherited from {http://www.opengis.net/citygml/appearance/1.0}AbstractTextureType
    
    # Element GenericApplicationPropertyOfSurfaceData ({http://www.opengis.net/citygml/appearance/1.0}_GenericApplicationPropertyOfSurfaceData) inherited from {http://www.opengis.net/citygml/appearance/1.0}AbstractSurfaceDataType
    
    # Element borderColor ({http://www.opengis.net/citygml/appearance/1.0}borderColor) inherited from {http://www.opengis.net/citygml/appearance/1.0}AbstractTextureType
    
    # Element description ({http://www.opengis.net/gml}description) inherited from {http://www.opengis.net/gml}AbstractGMLType
    
    # Element {http://www.opengis.net/citygml/appearance/1.0}orientation uses Python identifier orientation
    __orientation = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'orientation'), 'orientation', '__httpwww_opengis_netcitygmlappearance1_0_GeoreferencedTextureType_httpwww_opengis_netcitygmlappearance1_0orientation', False)

    
    orientation = property(__orientation.value, __orientation.set, None, None)

    
    # Element {http://www.opengis.net/citygml/appearance/1.0}target uses Python identifier target
    __target = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'target'), 'target', '__httpwww_opengis_netcitygmlappearance1_0_GeoreferencedTextureType_httpwww_opengis_netcitygmlappearance1_0target', True)

    
    target = property(__target.value, __target.set, None, None)

    
    # Element {http://www.opengis.net/citygml/appearance/1.0}referencePoint uses Python identifier referencePoint
    __referencePoint = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'referencePoint'), 'referencePoint', '__httpwww_opengis_netcitygmlappearance1_0_GeoreferencedTextureType_httpwww_opengis_netcitygmlappearance1_0referencePoint', False)

    
    referencePoint = property(__referencePoint.value, __referencePoint.set, None, None)

    
    # Element name ({http://www.opengis.net/gml}name) inherited from {http://www.opengis.net/gml}AbstractGMLType
    
    # Element GenericApplicationPropertyOfTexture ({http://www.opengis.net/citygml/appearance/1.0}_GenericApplicationPropertyOfTexture) inherited from {http://www.opengis.net/citygml/appearance/1.0}AbstractTextureType
    
    # Element location ({http://www.opengis.net/gml}location) inherited from {http://www.opengis.net/gml}AbstractFeatureType
    
    # Element textureType ({http://www.opengis.net/citygml/appearance/1.0}textureType) inherited from {http://www.opengis.net/citygml/appearance/1.0}AbstractTextureType
    
    # Element {http://www.opengis.net/citygml/appearance/1.0}_GenericApplicationPropertyOfGeoreferencedTexture uses Python identifier GenericApplicationPropertyOfGeoreferencedTexture
    __GenericApplicationPropertyOfGeoreferencedTexture = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfGeoreferencedTexture'), 'GenericApplicationPropertyOfGeoreferencedTexture', '__httpwww_opengis_netcitygmlappearance1_0_GeoreferencedTextureType_httpwww_opengis_netcitygmlappearance1_0_GenericApplicationPropertyOfGeoreferencedTexture', True)

    
    GenericApplicationPropertyOfGeoreferencedTexture = property(__GenericApplicationPropertyOfGeoreferencedTexture.value, __GenericApplicationPropertyOfGeoreferencedTexture.set, None, None)

    
    # Element mimeType ({http://www.opengis.net/citygml/appearance/1.0}mimeType) inherited from {http://www.opengis.net/citygml/appearance/1.0}AbstractTextureType
    
    # Element isFront ({http://www.opengis.net/citygml/appearance/1.0}isFront) inherited from {http://www.opengis.net/citygml/appearance/1.0}AbstractSurfaceDataType
    
    # Element wrapMode ({http://www.opengis.net/citygml/appearance/1.0}wrapMode) inherited from {http://www.opengis.net/citygml/appearance/1.0}AbstractTextureType
    
    # Element {http://www.opengis.net/citygml/appearance/1.0}preferWorldFile uses Python identifier preferWorldFile
    __preferWorldFile = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'preferWorldFile'), 'preferWorldFile', '__httpwww_opengis_netcitygmlappearance1_0_GeoreferencedTextureType_httpwww_opengis_netcitygmlappearance1_0preferWorldFile', False)

    
    preferWorldFile = property(__preferWorldFile.value, __preferWorldFile.set, None, None)

    
    # Element boundedBy ({http://www.opengis.net/gml}boundedBy) inherited from {http://www.opengis.net/gml}AbstractFeatureType
    
    # Element metaDataProperty ({http://www.opengis.net/gml}metaDataProperty) inherited from {http://www.opengis.net/gml}AbstractGMLType
    
    # Attribute id inherited from {http://www.opengis.net/gml}AbstractGMLType

    _ElementMap = AbstractTextureType._ElementMap.copy()
    _ElementMap.update({
        __orientation.name() : __orientation,
        __target.name() : __target,
        __referencePoint.name() : __referencePoint,
        __GenericApplicationPropertyOfGeoreferencedTexture.name() : __GenericApplicationPropertyOfGeoreferencedTexture,
        __preferWorldFile.name() : __preferWorldFile
    })
    _AttributeMap = AbstractTextureType._AttributeMap.copy()
    _AttributeMap.update({
        
    })
Namespace.addCategoryObject('typeBinding', u'GeoreferencedTextureType', GeoreferencedTextureType)


# Complex type ParameterizedTextureType with content type ELEMENT_ONLY
class ParameterizedTextureType (AbstractTextureType):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'ParameterizedTextureType')
    # Base type is AbstractTextureType
    
    # Element imageURI ({http://www.opengis.net/citygml/appearance/1.0}imageURI) inherited from {http://www.opengis.net/citygml/appearance/1.0}AbstractTextureType
    
    # Element {http://www.opengis.net/citygml/appearance/1.0}_GenericApplicationPropertyOfParameterizedTexture uses Python identifier GenericApplicationPropertyOfParameterizedTexture
    __GenericApplicationPropertyOfParameterizedTexture = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfParameterizedTexture'), 'GenericApplicationPropertyOfParameterizedTexture', '__httpwww_opengis_netcitygmlappearance1_0_ParameterizedTextureType_httpwww_opengis_netcitygmlappearance1_0_GenericApplicationPropertyOfParameterizedTexture', True)

    
    GenericApplicationPropertyOfParameterizedTexture = property(__GenericApplicationPropertyOfParameterizedTexture.value, __GenericApplicationPropertyOfParameterizedTexture.set, None, None)

    
    # Element borderColor ({http://www.opengis.net/citygml/appearance/1.0}borderColor) inherited from {http://www.opengis.net/citygml/appearance/1.0}AbstractTextureType
    
    # Element metaDataProperty ({http://www.opengis.net/gml}metaDataProperty) inherited from {http://www.opengis.net/gml}AbstractGMLType
    
    # Element isFront ({http://www.opengis.net/citygml/appearance/1.0}isFront) inherited from {http://www.opengis.net/citygml/appearance/1.0}AbstractSurfaceDataType
    
    # Element description ({http://www.opengis.net/gml}description) inherited from {http://www.opengis.net/gml}AbstractGMLType
    
    # Element GenericApplicationPropertyOfTexture ({http://www.opengis.net/citygml/appearance/1.0}_GenericApplicationPropertyOfTexture) inherited from {http://www.opengis.net/citygml/appearance/1.0}AbstractTextureType
    
    # Element location ({http://www.opengis.net/gml}location) inherited from {http://www.opengis.net/gml}AbstractFeatureType
    
    # Element {http://www.opengis.net/citygml/appearance/1.0}target uses Python identifier target
    __target = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'target'), 'target', '__httpwww_opengis_netcitygmlappearance1_0_ParameterizedTextureType_httpwww_opengis_netcitygmlappearance1_0target', True)

    
    target = property(__target.value, __target.set, None, None)

    
    # Element textureType ({http://www.opengis.net/citygml/appearance/1.0}textureType) inherited from {http://www.opengis.net/citygml/appearance/1.0}AbstractTextureType
    
    # Element GenericApplicationPropertyOfSurfaceData ({http://www.opengis.net/citygml/appearance/1.0}_GenericApplicationPropertyOfSurfaceData) inherited from {http://www.opengis.net/citygml/appearance/1.0}AbstractSurfaceDataType
    
    # Element mimeType ({http://www.opengis.net/citygml/appearance/1.0}mimeType) inherited from {http://www.opengis.net/citygml/appearance/1.0}AbstractTextureType
    
    # Element wrapMode ({http://www.opengis.net/citygml/appearance/1.0}wrapMode) inherited from {http://www.opengis.net/citygml/appearance/1.0}AbstractTextureType
    
    # Element boundedBy ({http://www.opengis.net/gml}boundedBy) inherited from {http://www.opengis.net/gml}AbstractFeatureType
    
    # Element name ({http://www.opengis.net/gml}name) inherited from {http://www.opengis.net/gml}AbstractGMLType
    
    # Attribute id inherited from {http://www.opengis.net/gml}AbstractGMLType

    _ElementMap = AbstractTextureType._ElementMap.copy()
    _ElementMap.update({
        __GenericApplicationPropertyOfParameterizedTexture.name() : __GenericApplicationPropertyOfParameterizedTexture,
        __target.name() : __target
    })
    _AttributeMap = AbstractTextureType._AttributeMap.copy()
    _AttributeMap.update({
        
    })
Namespace.addCategoryObject('typeBinding', u'ParameterizedTextureType', ParameterizedTextureType)


# Complex type SurfaceDataPropertyType with content type ELEMENT_ONLY
class SurfaceDataPropertyType (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'SurfaceDataPropertyType')
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {http://www.opengis.net/citygml/appearance/1.0}_SurfaceData uses Python identifier SurfaceData
    __SurfaceData = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'_SurfaceData'), 'SurfaceData', '__httpwww_opengis_netcitygmlappearance1_0_SurfaceDataPropertyType_httpwww_opengis_netcitygmlappearance1_0_SurfaceData', False)

    
    SurfaceData = property(__SurfaceData.value, __SurfaceData.set, None, None)

    
    # Attribute {http://www.w3.org/1999/xlink}role uses Python identifier role
    __role = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'role'), 'role', '__httpwww_opengis_netcitygmlappearance1_0_SurfaceDataPropertyType_httpwww_w3_org1999xlinkrole', pyxb.binding.datatypes.anyURI)
    
    role = property(__role.value, __role.set, None, None)

    
    # Attribute {http://www.w3.org/1999/xlink}title uses Python identifier title
    __title = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'title'), 'title', '__httpwww_opengis_netcitygmlappearance1_0_SurfaceDataPropertyType_httpwww_w3_org1999xlinktitle', pyxb.binding.datatypes.string)
    
    title = property(__title.value, __title.set, None, None)

    
    # Attribute {http://www.w3.org/1999/xlink}show uses Python identifier show
    __show = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'show'), 'show', '__httpwww_opengis_netcitygmlappearance1_0_SurfaceDataPropertyType_httpwww_w3_org1999xlinkshow', pyxb.bundles.opengis.misc.xlinks.STD_ANON_)
    
    show = property(__show.value, __show.set, None, u"\n        The 'show' attribute is used to communicate the desired presentation \n        of the ending resource on traversal from the starting resource; it's \n        value should be treated as follows: \n        new - load ending resource in a new window, frame, pane, or other \n              presentation context\n        replace - load the resource in the same window, frame, pane, or \n                  other presentation context\n        embed - load ending resource in place of the presentation of the \n                starting resource\n        other - behavior is unconstrained; examine other markup in the \n                link for hints \n        none - behavior is unconstrained \n      ")

    
    # Attribute {http://www.w3.org/1999/xlink}type uses Python identifier type
    __type = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'type'), 'type', '__httpwww_opengis_netcitygmlappearance1_0_SurfaceDataPropertyType_httpwww_w3_org1999xlinktype', pyxb.binding.datatypes.string, fixed=True, unicode_default=u'simple')
    
    type = property(__type.value, __type.set, None, None)

    
    # Attribute {http://www.w3.org/1999/xlink}arcrole uses Python identifier arcrole
    __arcrole = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'arcrole'), 'arcrole', '__httpwww_opengis_netcitygmlappearance1_0_SurfaceDataPropertyType_httpwww_w3_org1999xlinkarcrole', pyxb.binding.datatypes.anyURI)
    
    arcrole = property(__arcrole.value, __arcrole.set, None, None)

    
    # Attribute {http://www.w3.org/1999/xlink}href uses Python identifier href
    __href = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'href'), 'href', '__httpwww_opengis_netcitygmlappearance1_0_SurfaceDataPropertyType_httpwww_w3_org1999xlinkhref', pyxb.binding.datatypes.anyURI)
    
    href = property(__href.value, __href.set, None, None)

    
    # Attribute {http://www.w3.org/1999/xlink}actuate uses Python identifier actuate
    __actuate = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'actuate'), 'actuate', '__httpwww_opengis_netcitygmlappearance1_0_SurfaceDataPropertyType_httpwww_w3_org1999xlinkactuate', pyxb.bundles.opengis.misc.xlinks.STD_ANON)
    
    actuate = property(__actuate.value, __actuate.set, None, u"\n        The 'actuate' attribute is used to communicate the desired timing \n        of traversal from the starting resource to the ending resource; \n        it's value should be treated as follows:\n        onLoad - traverse to the ending resource immediately on loading \n                 the starting resource \n        onRequest - traverse from the starting resource to the ending \n                    resource only on a post-loading event triggered for \n                    this purpose \n        other - behavior is unconstrained; examine other markup in link \n                for hints \n        none - behavior is unconstrained\n      ")

    
    # Attribute {http://www.opengis.net/gml}remoteSchema uses Python identifier remoteSchema
    __remoteSchema = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'remoteSchema'), 'remoteSchema', '__httpwww_opengis_netcitygmlappearance1_0_SurfaceDataPropertyType_httpwww_opengis_netgmlremoteSchema', pyxb.binding.datatypes.anyURI)
    
    remoteSchema = property(__remoteSchema.value, __remoteSchema.set, None, u'Reference to an XML Schema fragment that specifies the content model of the propertys value. This is in conformance with the XML Schema Section 4.14 Referencing Schemas from Elsewhere.')


    _ElementMap = {
        __SurfaceData.name() : __SurfaceData
    }
    _AttributeMap = {
        __role.name() : __role,
        __title.name() : __title,
        __show.name() : __show,
        __type.name() : __type,
        __arcrole.name() : __arcrole,
        __href.name() : __href,
        __actuate.name() : __actuate,
        __remoteSchema.name() : __remoteSchema
    }
Namespace.addCategoryObject('typeBinding', u'SurfaceDataPropertyType', SurfaceDataPropertyType)


# Complex type AppearanceType with content type ELEMENT_ONLY
class AppearanceType (pyxb.bundles.opengis.gml.AbstractFeatureType):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'AppearanceType')
    # Base type is pyxb.bundles.opengis.gml.AbstractFeatureType
    
    # Element description ({http://www.opengis.net/gml}description) inherited from {http://www.opengis.net/gml}AbstractGMLType
    
    # Element {http://www.opengis.net/citygml/appearance/1.0}surfaceDataMember uses Python identifier surfaceDataMember
    __surfaceDataMember = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'surfaceDataMember'), 'surfaceDataMember', '__httpwww_opengis_netcitygmlappearance1_0_AppearanceType_httpwww_opengis_netcitygmlappearance1_0surfaceDataMember', True)

    
    surfaceDataMember = property(__surfaceDataMember.value, __surfaceDataMember.set, None, None)

    
    # Element metaDataProperty ({http://www.opengis.net/gml}metaDataProperty) inherited from {http://www.opengis.net/gml}AbstractGMLType
    
    # Element location ({http://www.opengis.net/gml}location) inherited from {http://www.opengis.net/gml}AbstractFeatureType
    
    # Element {http://www.opengis.net/citygml/appearance/1.0}_GenericApplicationPropertyOfAppearance uses Python identifier GenericApplicationPropertyOfAppearance
    __GenericApplicationPropertyOfAppearance = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfAppearance'), 'GenericApplicationPropertyOfAppearance', '__httpwww_opengis_netcitygmlappearance1_0_AppearanceType_httpwww_opengis_netcitygmlappearance1_0_GenericApplicationPropertyOfAppearance', True)

    
    GenericApplicationPropertyOfAppearance = property(__GenericApplicationPropertyOfAppearance.value, __GenericApplicationPropertyOfAppearance.set, None, None)

    
    # Element {http://www.opengis.net/citygml/appearance/1.0}theme uses Python identifier theme
    __theme = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'theme'), 'theme', '__httpwww_opengis_netcitygmlappearance1_0_AppearanceType_httpwww_opengis_netcitygmlappearance1_0theme', False)

    
    theme = property(__theme.value, __theme.set, None, None)

    
    # Element boundedBy ({http://www.opengis.net/gml}boundedBy) inherited from {http://www.opengis.net/gml}AbstractFeatureType
    
    # Element name ({http://www.opengis.net/gml}name) inherited from {http://www.opengis.net/gml}AbstractGMLType
    
    # Attribute id inherited from {http://www.opengis.net/gml}AbstractGMLType

    _ElementMap = pyxb.bundles.opengis.gml.AbstractFeatureType._ElementMap.copy()
    _ElementMap.update({
        __surfaceDataMember.name() : __surfaceDataMember,
        __GenericApplicationPropertyOfAppearance.name() : __GenericApplicationPropertyOfAppearance,
        __theme.name() : __theme
    })
    _AttributeMap = pyxb.bundles.opengis.gml.AbstractFeatureType._AttributeMap.copy()
    _AttributeMap.update({
        
    })
Namespace.addCategoryObject('typeBinding', u'AppearanceType', AppearanceType)


# Complex type TexCoordGenType with content type ELEMENT_ONLY
class TexCoordGenType (AbstractTextureParameterizationType):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'TexCoordGenType')
    # Base type is AbstractTextureParameterizationType
    
    # Element description ({http://www.opengis.net/gml}description) inherited from {http://www.opengis.net/gml}AbstractGMLType
    
    # Element {http://www.opengis.net/citygml/appearance/1.0}_GenericApplicationPropertyOfTexCoordGen uses Python identifier GenericApplicationPropertyOfTexCoordGen
    __GenericApplicationPropertyOfTexCoordGen = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfTexCoordGen'), 'GenericApplicationPropertyOfTexCoordGen', '__httpwww_opengis_netcitygmlappearance1_0_TexCoordGenType_httpwww_opengis_netcitygmlappearance1_0_GenericApplicationPropertyOfTexCoordGen', True)

    
    GenericApplicationPropertyOfTexCoordGen = property(__GenericApplicationPropertyOfTexCoordGen.value, __GenericApplicationPropertyOfTexCoordGen.set, None, None)

    
    # Element metaDataProperty ({http://www.opengis.net/gml}metaDataProperty) inherited from {http://www.opengis.net/gml}AbstractGMLType
    
    # Element GenericApplicationPropertyOfTextureParameterization ({http://www.opengis.net/citygml/appearance/1.0}_GenericApplicationPropertyOfTextureParameterization) inherited from {http://www.opengis.net/citygml/appearance/1.0}AbstractTextureParameterizationType
    
    # Element {http://www.opengis.net/citygml/appearance/1.0}worldToTexture uses Python identifier worldToTexture
    __worldToTexture = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'worldToTexture'), 'worldToTexture', '__httpwww_opengis_netcitygmlappearance1_0_TexCoordGenType_httpwww_opengis_netcitygmlappearance1_0worldToTexture', False)

    
    worldToTexture = property(__worldToTexture.value, __worldToTexture.set, None, None)

    
    # Element name ({http://www.opengis.net/gml}name) inherited from {http://www.opengis.net/gml}AbstractGMLType
    
    # Attribute id inherited from {http://www.opengis.net/gml}AbstractGMLType

    _ElementMap = AbstractTextureParameterizationType._ElementMap.copy()
    _ElementMap.update({
        __GenericApplicationPropertyOfTexCoordGen.name() : __GenericApplicationPropertyOfTexCoordGen,
        __worldToTexture.name() : __worldToTexture
    })
    _AttributeMap = AbstractTextureParameterizationType._AttributeMap.copy()
    _AttributeMap.update({
        
    })
Namespace.addCategoryObject('typeBinding', u'TexCoordGenType', TexCoordGenType)


GenericApplicationPropertyOfGeoreferencedTexture = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfGeoreferencedTexture'), pyxb.binding.datatypes.anyType, abstract=pyxb.binding.datatypes.boolean(1))
Namespace.addCategoryObject('elementBinding', GenericApplicationPropertyOfGeoreferencedTexture.name().localName(), GenericApplicationPropertyOfGeoreferencedTexture)

appearance = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'appearance'), AppearancePropertyType)
Namespace.addCategoryObject('elementBinding', appearance.name().localName(), appearance)

GenericApplicationPropertyOfTexCoordGen = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfTexCoordGen'), pyxb.binding.datatypes.anyType, abstract=pyxb.binding.datatypes.boolean(1))
Namespace.addCategoryObject('elementBinding', GenericApplicationPropertyOfTexCoordGen.name().localName(), GenericApplicationPropertyOfTexCoordGen)

TextureParameterization = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'_TextureParameterization'), AbstractTextureParameterizationType, abstract=pyxb.binding.datatypes.boolean(1))
Namespace.addCategoryObject('elementBinding', TextureParameterization.name().localName(), TextureParameterization)

GenericApplicationPropertyOfTextureParameterization = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfTextureParameterization'), pyxb.binding.datatypes.anyType, abstract=pyxb.binding.datatypes.boolean(1))
Namespace.addCategoryObject('elementBinding', GenericApplicationPropertyOfTextureParameterization.name().localName(), GenericApplicationPropertyOfTextureParameterization)

GenericApplicationPropertyOfSurfaceData = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfSurfaceData'), pyxb.binding.datatypes.anyType, abstract=pyxb.binding.datatypes.boolean(1))
Namespace.addCategoryObject('elementBinding', GenericApplicationPropertyOfSurfaceData.name().localName(), GenericApplicationPropertyOfSurfaceData)

GenericApplicationPropertyOfParameterizedTexture = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfParameterizedTexture'), pyxb.binding.datatypes.anyType, abstract=pyxb.binding.datatypes.boolean(1))
Namespace.addCategoryObject('elementBinding', GenericApplicationPropertyOfParameterizedTexture.name().localName(), GenericApplicationPropertyOfParameterizedTexture)

X3DMaterial = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'X3DMaterial'), X3DMaterialType)
Namespace.addCategoryObject('elementBinding', X3DMaterial.name().localName(), X3DMaterial)

GenericApplicationPropertyOfTexture = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfTexture'), pyxb.binding.datatypes.anyType, abstract=pyxb.binding.datatypes.boolean(1))
Namespace.addCategoryObject('elementBinding', GenericApplicationPropertyOfTexture.name().localName(), GenericApplicationPropertyOfTexture)

GenericApplicationPropertyOfTexCoordList = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfTexCoordList'), pyxb.binding.datatypes.anyType, abstract=pyxb.binding.datatypes.boolean(1))
Namespace.addCategoryObject('elementBinding', GenericApplicationPropertyOfTexCoordList.name().localName(), GenericApplicationPropertyOfTexCoordList)

Texture = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'_Texture'), AbstractTextureType, abstract=pyxb.binding.datatypes.boolean(1))
Namespace.addCategoryObject('elementBinding', Texture.name().localName(), Texture)

TexCoordList = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'TexCoordList'), TexCoordListType)
Namespace.addCategoryObject('elementBinding', TexCoordList.name().localName(), TexCoordList)

GenericApplicationPropertyOfX3DMaterial = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfX3DMaterial'), pyxb.binding.datatypes.anyType, abstract=pyxb.binding.datatypes.boolean(1))
Namespace.addCategoryObject('elementBinding', GenericApplicationPropertyOfX3DMaterial.name().localName(), GenericApplicationPropertyOfX3DMaterial)

GenericApplicationPropertyOfAppearance = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfAppearance'), pyxb.binding.datatypes.anyType, abstract=pyxb.binding.datatypes.boolean(1))
Namespace.addCategoryObject('elementBinding', GenericApplicationPropertyOfAppearance.name().localName(), GenericApplicationPropertyOfAppearance)

GeoreferencedTexture = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'GeoreferencedTexture'), GeoreferencedTextureType)
Namespace.addCategoryObject('elementBinding', GeoreferencedTexture.name().localName(), GeoreferencedTexture)

ParameterizedTexture = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'ParameterizedTexture'), ParameterizedTextureType)
Namespace.addCategoryObject('elementBinding', ParameterizedTexture.name().localName(), ParameterizedTexture)

TexCoordGen = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'TexCoordGen'), TexCoordGenType)
Namespace.addCategoryObject('elementBinding', TexCoordGen.name().localName(), TexCoordGen)

appearanceMember = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'appearanceMember'), AppearancePropertyType)
Namespace.addCategoryObject('elementBinding', appearanceMember.name().localName(), appearanceMember)

SurfaceData = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'_SurfaceData'), AbstractSurfaceDataType, abstract=pyxb.binding.datatypes.boolean(1))
Namespace.addCategoryObject('elementBinding', SurfaceData.name().localName(), SurfaceData)



AppearancePropertyType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Appearance'), AppearanceType, scope=AppearancePropertyType))
AppearancePropertyType._GroupModel_2 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(AppearancePropertyType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'_Feature')), min_occurs=1, max_occurs=1)
    )
AppearancePropertyType._GroupModel_3 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(AppearancePropertyType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Appearance')), min_occurs=1, max_occurs=1)
    )
AppearancePropertyType._GroupModel_ = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(AppearancePropertyType._GroupModel_2, min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(AppearancePropertyType._GroupModel_3, min_occurs=0L, max_occurs=1)
    )
AppearancePropertyType._ContentModel = pyxb.binding.content.ParticleModel(AppearancePropertyType._GroupModel_, min_occurs=1, max_occurs=1)



AbstractSurfaceDataType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'isFront'), pyxb.binding.datatypes.boolean, scope=AbstractSurfaceDataType))

AbstractSurfaceDataType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfSurfaceData'), pyxb.binding.datatypes.anyType, abstract=pyxb.binding.datatypes.boolean(1), scope=AbstractSurfaceDataType))
AbstractSurfaceDataType._GroupModel_7 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(AbstractSurfaceDataType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'metaDataProperty')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(AbstractSurfaceDataType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'description')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(AbstractSurfaceDataType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'name')), min_occurs=0L, max_occurs=None)
    )
AbstractSurfaceDataType._GroupModel_6 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(AbstractSurfaceDataType._GroupModel_7, min_occurs=1, max_occurs=1)
    )
AbstractSurfaceDataType._GroupModel_8 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(AbstractSurfaceDataType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'boundedBy')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(AbstractSurfaceDataType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'location')), min_occurs=0L, max_occurs=1)
    )
AbstractSurfaceDataType._GroupModel_5 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(AbstractSurfaceDataType._GroupModel_6, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(AbstractSurfaceDataType._GroupModel_8, min_occurs=1, max_occurs=1)
    )
AbstractSurfaceDataType._GroupModel_9 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(AbstractSurfaceDataType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'isFront')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(AbstractSurfaceDataType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfSurfaceData')), min_occurs=0L, max_occurs=None)
    )
AbstractSurfaceDataType._GroupModel_4 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(AbstractSurfaceDataType._GroupModel_5, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(AbstractSurfaceDataType._GroupModel_9, min_occurs=1, max_occurs=1)
    )
AbstractSurfaceDataType._ContentModel = pyxb.binding.content.ParticleModel(AbstractSurfaceDataType._GroupModel_4, min_occurs=1, max_occurs=1)



TextureAssociationType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'_TextureParameterization'), AbstractTextureParameterizationType, abstract=pyxb.binding.datatypes.boolean(1), scope=TextureAssociationType))
TextureAssociationType._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(TextureAssociationType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_TextureParameterization')), min_occurs=1, max_occurs=1)
    )
TextureAssociationType._ContentModel = pyxb.binding.content.ParticleModel(TextureAssociationType._GroupModel, min_occurs=0L, max_occurs=1)



AbstractTextureParameterizationType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfTextureParameterization'), pyxb.binding.datatypes.anyType, abstract=pyxb.binding.datatypes.boolean(1), scope=AbstractTextureParameterizationType))
AbstractTextureParameterizationType._GroupModel_4 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(AbstractTextureParameterizationType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'metaDataProperty')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(AbstractTextureParameterizationType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'description')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(AbstractTextureParameterizationType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'name')), min_occurs=0L, max_occurs=None)
    )
AbstractTextureParameterizationType._GroupModel_3 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(AbstractTextureParameterizationType._GroupModel_4, min_occurs=1, max_occurs=1)
    )
AbstractTextureParameterizationType._GroupModel_5 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(AbstractTextureParameterizationType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfTextureParameterization')), min_occurs=0L, max_occurs=None)
    )
AbstractTextureParameterizationType._GroupModel_2 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(AbstractTextureParameterizationType._GroupModel_3, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(AbstractTextureParameterizationType._GroupModel_5, min_occurs=1, max_occurs=1)
    )
AbstractTextureParameterizationType._ContentModel = pyxb.binding.content.ParticleModel(AbstractTextureParameterizationType._GroupModel_2, min_occurs=1, max_occurs=1)



X3DMaterialType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'ambientIntensity'), pyxb.bundles.opengis.citygml.base.doubleBetween0and1, scope=X3DMaterialType))

X3DMaterialType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfX3DMaterial'), pyxb.binding.datatypes.anyType, abstract=pyxb.binding.datatypes.boolean(1), scope=X3DMaterialType))

X3DMaterialType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'diffuseColor'), Color, scope=X3DMaterialType))

X3DMaterialType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'target'), pyxb.binding.datatypes.anyURI, scope=X3DMaterialType))

X3DMaterialType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'isSmooth'), pyxb.binding.datatypes.boolean, scope=X3DMaterialType))

X3DMaterialType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'transparency'), pyxb.bundles.opengis.citygml.base.doubleBetween0and1, scope=X3DMaterialType))

X3DMaterialType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'emissiveColor'), Color, scope=X3DMaterialType))

X3DMaterialType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'specularColor'), Color, scope=X3DMaterialType))

X3DMaterialType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'shininess'), pyxb.bundles.opengis.citygml.base.doubleBetween0and1, scope=X3DMaterialType))
X3DMaterialType._GroupModel_8 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(X3DMaterialType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'metaDataProperty')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(X3DMaterialType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'description')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(X3DMaterialType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'name')), min_occurs=0L, max_occurs=None)
    )
X3DMaterialType._GroupModel_7 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(X3DMaterialType._GroupModel_8, min_occurs=1, max_occurs=1)
    )
X3DMaterialType._GroupModel_9 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(X3DMaterialType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'boundedBy')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(X3DMaterialType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'location')), min_occurs=0L, max_occurs=1)
    )
X3DMaterialType._GroupModel_6 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(X3DMaterialType._GroupModel_7, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(X3DMaterialType._GroupModel_9, min_occurs=1, max_occurs=1)
    )
X3DMaterialType._GroupModel_10 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(X3DMaterialType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'isFront')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(X3DMaterialType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfSurfaceData')), min_occurs=0L, max_occurs=None)
    )
X3DMaterialType._GroupModel_5 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(X3DMaterialType._GroupModel_6, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(X3DMaterialType._GroupModel_10, min_occurs=1, max_occurs=1)
    )
X3DMaterialType._GroupModel_11 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(X3DMaterialType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'ambientIntensity')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(X3DMaterialType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'diffuseColor')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(X3DMaterialType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'emissiveColor')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(X3DMaterialType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'specularColor')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(X3DMaterialType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'shininess')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(X3DMaterialType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'transparency')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(X3DMaterialType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'isSmooth')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(X3DMaterialType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'target')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(X3DMaterialType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfX3DMaterial')), min_occurs=0L, max_occurs=None)
    )
X3DMaterialType._GroupModel_4 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(X3DMaterialType._GroupModel_5, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(X3DMaterialType._GroupModel_11, min_occurs=1, max_occurs=1)
    )
X3DMaterialType._ContentModel = pyxb.binding.content.ParticleModel(X3DMaterialType._GroupModel_4, min_occurs=1, max_occurs=1)



AbstractTextureType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'imageURI'), pyxb.binding.datatypes.anyURI, scope=AbstractTextureType))

AbstractTextureType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'borderColor'), ColorPlusOpacity, scope=AbstractTextureType))

AbstractTextureType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfTexture'), pyxb.binding.datatypes.anyType, abstract=pyxb.binding.datatypes.boolean(1), scope=AbstractTextureType))

AbstractTextureType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'textureType'), TextureTypeType, scope=AbstractTextureType))

AbstractTextureType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'mimeType'), pyxb.bundles.opengis.citygml.base.MimeTypeType, scope=AbstractTextureType))

AbstractTextureType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'wrapMode'), WrapModeType, scope=AbstractTextureType))
AbstractTextureType._GroupModel_8 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(AbstractTextureType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'metaDataProperty')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(AbstractTextureType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'description')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(AbstractTextureType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'name')), min_occurs=0L, max_occurs=None)
    )
AbstractTextureType._GroupModel_7 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(AbstractTextureType._GroupModel_8, min_occurs=1, max_occurs=1)
    )
AbstractTextureType._GroupModel_9 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(AbstractTextureType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'boundedBy')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(AbstractTextureType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'location')), min_occurs=0L, max_occurs=1)
    )
AbstractTextureType._GroupModel_6 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(AbstractTextureType._GroupModel_7, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(AbstractTextureType._GroupModel_9, min_occurs=1, max_occurs=1)
    )
AbstractTextureType._GroupModel_10 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(AbstractTextureType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'isFront')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(AbstractTextureType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfSurfaceData')), min_occurs=0L, max_occurs=None)
    )
AbstractTextureType._GroupModel_5 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(AbstractTextureType._GroupModel_6, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(AbstractTextureType._GroupModel_10, min_occurs=1, max_occurs=1)
    )
AbstractTextureType._GroupModel_11 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(AbstractTextureType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'imageURI')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(AbstractTextureType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'mimeType')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(AbstractTextureType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'textureType')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(AbstractTextureType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'wrapMode')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(AbstractTextureType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'borderColor')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(AbstractTextureType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfTexture')), min_occurs=0L, max_occurs=None)
    )
AbstractTextureType._GroupModel_4 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(AbstractTextureType._GroupModel_5, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(AbstractTextureType._GroupModel_11, min_occurs=1, max_occurs=1)
    )
AbstractTextureType._ContentModel = pyxb.binding.content.ParticleModel(AbstractTextureType._GroupModel_4, min_occurs=1, max_occurs=1)



TexCoordListType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfTexCoordList'), pyxb.binding.datatypes.anyType, abstract=pyxb.binding.datatypes.boolean(1), scope=TexCoordListType))

TexCoordListType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'textureCoordinates'), CTD_ANON_, scope=TexCoordListType))
TexCoordListType._GroupModel_5 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(TexCoordListType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'metaDataProperty')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(TexCoordListType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'description')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(TexCoordListType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'name')), min_occurs=0L, max_occurs=None)
    )
TexCoordListType._GroupModel_4 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(TexCoordListType._GroupModel_5, min_occurs=1, max_occurs=1)
    )
TexCoordListType._GroupModel_6 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(TexCoordListType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfTextureParameterization')), min_occurs=0L, max_occurs=None)
    )
TexCoordListType._GroupModel_3 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(TexCoordListType._GroupModel_4, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(TexCoordListType._GroupModel_6, min_occurs=1, max_occurs=1)
    )
TexCoordListType._GroupModel_7 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(TexCoordListType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'textureCoordinates')), min_occurs=1, max_occurs=None),
    pyxb.binding.content.ParticleModel(TexCoordListType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfTexCoordList')), min_occurs=0L, max_occurs=None)
    )
TexCoordListType._GroupModel_2 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(TexCoordListType._GroupModel_3, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(TexCoordListType._GroupModel_7, min_occurs=1, max_occurs=1)
    )
TexCoordListType._ContentModel = pyxb.binding.content.ParticleModel(TexCoordListType._GroupModel_2, min_occurs=1, max_occurs=1)



GeoreferencedTextureType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'orientation'), pyxb.bundles.opengis.citygml.base.TransformationMatrix2x2Type, scope=GeoreferencedTextureType))

GeoreferencedTextureType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'target'), pyxb.binding.datatypes.anyURI, scope=GeoreferencedTextureType))

GeoreferencedTextureType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'referencePoint'), pyxb.bundles.opengis.gml.PointPropertyType, scope=GeoreferencedTextureType))

GeoreferencedTextureType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfGeoreferencedTexture'), pyxb.binding.datatypes.anyType, abstract=pyxb.binding.datatypes.boolean(1), scope=GeoreferencedTextureType))

GeoreferencedTextureType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'preferWorldFile'), pyxb.binding.datatypes.boolean, scope=GeoreferencedTextureType))
GeoreferencedTextureType._GroupModel_9 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(GeoreferencedTextureType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'metaDataProperty')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(GeoreferencedTextureType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'description')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(GeoreferencedTextureType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'name')), min_occurs=0L, max_occurs=None)
    )
GeoreferencedTextureType._GroupModel_8 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(GeoreferencedTextureType._GroupModel_9, min_occurs=1, max_occurs=1)
    )
GeoreferencedTextureType._GroupModel_10 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(GeoreferencedTextureType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'boundedBy')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(GeoreferencedTextureType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'location')), min_occurs=0L, max_occurs=1)
    )
GeoreferencedTextureType._GroupModel_7 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(GeoreferencedTextureType._GroupModel_8, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(GeoreferencedTextureType._GroupModel_10, min_occurs=1, max_occurs=1)
    )
GeoreferencedTextureType._GroupModel_11 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(GeoreferencedTextureType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'isFront')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(GeoreferencedTextureType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfSurfaceData')), min_occurs=0L, max_occurs=None)
    )
GeoreferencedTextureType._GroupModel_6 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(GeoreferencedTextureType._GroupModel_7, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(GeoreferencedTextureType._GroupModel_11, min_occurs=1, max_occurs=1)
    )
GeoreferencedTextureType._GroupModel_12 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(GeoreferencedTextureType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'imageURI')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(GeoreferencedTextureType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'mimeType')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(GeoreferencedTextureType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'textureType')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(GeoreferencedTextureType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'wrapMode')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(GeoreferencedTextureType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'borderColor')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(GeoreferencedTextureType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfTexture')), min_occurs=0L, max_occurs=None)
    )
GeoreferencedTextureType._GroupModel_5 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(GeoreferencedTextureType._GroupModel_6, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(GeoreferencedTextureType._GroupModel_12, min_occurs=1, max_occurs=1)
    )
GeoreferencedTextureType._GroupModel_13 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(GeoreferencedTextureType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'preferWorldFile')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(GeoreferencedTextureType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'referencePoint')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(GeoreferencedTextureType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'orientation')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(GeoreferencedTextureType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'target')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(GeoreferencedTextureType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfGeoreferencedTexture')), min_occurs=0L, max_occurs=None)
    )
GeoreferencedTextureType._GroupModel_4 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(GeoreferencedTextureType._GroupModel_5, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(GeoreferencedTextureType._GroupModel_13, min_occurs=1, max_occurs=1)
    )
GeoreferencedTextureType._ContentModel = pyxb.binding.content.ParticleModel(GeoreferencedTextureType._GroupModel_4, min_occurs=1, max_occurs=1)



ParameterizedTextureType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfParameterizedTexture'), pyxb.binding.datatypes.anyType, abstract=pyxb.binding.datatypes.boolean(1), scope=ParameterizedTextureType))

ParameterizedTextureType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'target'), TextureAssociationType, scope=ParameterizedTextureType))
ParameterizedTextureType._GroupModel_9 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(ParameterizedTextureType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'metaDataProperty')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(ParameterizedTextureType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'description')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(ParameterizedTextureType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'name')), min_occurs=0L, max_occurs=None)
    )
ParameterizedTextureType._GroupModel_8 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(ParameterizedTextureType._GroupModel_9, min_occurs=1, max_occurs=1)
    )
ParameterizedTextureType._GroupModel_10 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(ParameterizedTextureType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'boundedBy')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(ParameterizedTextureType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'location')), min_occurs=0L, max_occurs=1)
    )
ParameterizedTextureType._GroupModel_7 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(ParameterizedTextureType._GroupModel_8, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(ParameterizedTextureType._GroupModel_10, min_occurs=1, max_occurs=1)
    )
ParameterizedTextureType._GroupModel_11 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(ParameterizedTextureType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'isFront')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(ParameterizedTextureType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfSurfaceData')), min_occurs=0L, max_occurs=None)
    )
ParameterizedTextureType._GroupModel_6 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(ParameterizedTextureType._GroupModel_7, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(ParameterizedTextureType._GroupModel_11, min_occurs=1, max_occurs=1)
    )
ParameterizedTextureType._GroupModel_12 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(ParameterizedTextureType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'imageURI')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(ParameterizedTextureType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'mimeType')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(ParameterizedTextureType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'textureType')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(ParameterizedTextureType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'wrapMode')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(ParameterizedTextureType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'borderColor')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(ParameterizedTextureType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfTexture')), min_occurs=0L, max_occurs=None)
    )
ParameterizedTextureType._GroupModel_5 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(ParameterizedTextureType._GroupModel_6, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(ParameterizedTextureType._GroupModel_12, min_occurs=1, max_occurs=1)
    )
ParameterizedTextureType._GroupModel_13 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(ParameterizedTextureType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'target')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(ParameterizedTextureType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfParameterizedTexture')), min_occurs=0L, max_occurs=None)
    )
ParameterizedTextureType._GroupModel_4 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(ParameterizedTextureType._GroupModel_5, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(ParameterizedTextureType._GroupModel_13, min_occurs=1, max_occurs=1)
    )
ParameterizedTextureType._ContentModel = pyxb.binding.content.ParticleModel(ParameterizedTextureType._GroupModel_4, min_occurs=1, max_occurs=1)



SurfaceDataPropertyType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'_SurfaceData'), AbstractSurfaceDataType, abstract=pyxb.binding.datatypes.boolean(1), scope=SurfaceDataPropertyType))
SurfaceDataPropertyType._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(SurfaceDataPropertyType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_SurfaceData')), min_occurs=0L, max_occurs=1)
    )
SurfaceDataPropertyType._ContentModel = pyxb.binding.content.ParticleModel(SurfaceDataPropertyType._GroupModel, min_occurs=0L, max_occurs=1)



AppearanceType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'surfaceDataMember'), SurfaceDataPropertyType, scope=AppearanceType))

AppearanceType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfAppearance'), pyxb.binding.datatypes.anyType, abstract=pyxb.binding.datatypes.boolean(1), scope=AppearanceType))

AppearanceType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'theme'), pyxb.binding.datatypes.string, scope=AppearanceType))
AppearanceType._GroupModel_7 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(AppearanceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'metaDataProperty')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(AppearanceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'description')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(AppearanceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'name')), min_occurs=0L, max_occurs=None)
    )
AppearanceType._GroupModel_6 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(AppearanceType._GroupModel_7, min_occurs=1, max_occurs=1)
    )
AppearanceType._GroupModel_8 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(AppearanceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'boundedBy')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(AppearanceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'location')), min_occurs=0L, max_occurs=1)
    )
AppearanceType._GroupModel_5 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(AppearanceType._GroupModel_6, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(AppearanceType._GroupModel_8, min_occurs=1, max_occurs=1)
    )
AppearanceType._GroupModel_9 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(AppearanceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'theme')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(AppearanceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'surfaceDataMember')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(AppearanceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfAppearance')), min_occurs=0L, max_occurs=None)
    )
AppearanceType._GroupModel_4 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(AppearanceType._GroupModel_5, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(AppearanceType._GroupModel_9, min_occurs=1, max_occurs=1)
    )
AppearanceType._ContentModel = pyxb.binding.content.ParticleModel(AppearanceType._GroupModel_4, min_occurs=1, max_occurs=1)



TexCoordGenType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfTexCoordGen'), pyxb.binding.datatypes.anyType, abstract=pyxb.binding.datatypes.boolean(1), scope=TexCoordGenType))

TexCoordGenType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'worldToTexture'), CTD_ANON, scope=TexCoordGenType))
TexCoordGenType._GroupModel_5 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(TexCoordGenType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'metaDataProperty')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(TexCoordGenType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'description')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(TexCoordGenType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'name')), min_occurs=0L, max_occurs=None)
    )
TexCoordGenType._GroupModel_4 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(TexCoordGenType._GroupModel_5, min_occurs=1, max_occurs=1)
    )
TexCoordGenType._GroupModel_6 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(TexCoordGenType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfTextureParameterization')), min_occurs=0L, max_occurs=None)
    )
TexCoordGenType._GroupModel_3 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(TexCoordGenType._GroupModel_4, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(TexCoordGenType._GroupModel_6, min_occurs=1, max_occurs=1)
    )
TexCoordGenType._GroupModel_7 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(TexCoordGenType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'worldToTexture')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(TexCoordGenType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfTexCoordGen')), min_occurs=0L, max_occurs=None)
    )
TexCoordGenType._GroupModel_2 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(TexCoordGenType._GroupModel_3, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(TexCoordGenType._GroupModel_7, min_occurs=1, max_occurs=1)
    )
TexCoordGenType._ContentModel = pyxb.binding.content.ParticleModel(TexCoordGenType._GroupModel_2, min_occurs=1, max_occurs=1)

appearance._setSubstitutionGroup(pyxb.bundles.opengis.citygml.base.GenericApplicationPropertyOfCityObject)

TextureParameterization._setSubstitutionGroup(pyxb.bundles.opengis.gml.GML)

X3DMaterial._setSubstitutionGroup(SurfaceData)

Texture._setSubstitutionGroup(SurfaceData)

TexCoordList._setSubstitutionGroup(TextureParameterization)

GeoreferencedTexture._setSubstitutionGroup(Texture)

ParameterizedTexture._setSubstitutionGroup(Texture)

TexCoordGen._setSubstitutionGroup(TextureParameterization)

appearanceMember._setSubstitutionGroup(pyxb.bundles.opengis.gml.featureMember)

SurfaceData._setSubstitutionGroup(pyxb.bundles.opengis.gml.Feature)
