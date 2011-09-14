# ./pyxb/bundles/opengis/citygml/raw/texturedSurface.py
# PyXB bindings for NM:d0c900ca512ca4d1024bf70ffaa5c66e996a6cdf
# Generated 2011-09-09 14:19:28.212079 by PyXB version 1.1.3
# Namespace http://www.opengis.net/citygml/texturedsurface/1.0

import pyxb
import pyxb.binding
import pyxb.binding.saxer
import StringIO
import pyxb.utils.utility
import pyxb.utils.domutils
import sys

# Unique identifier for bindings created at the same time
_GenerationUID = pyxb.utils.utility.UniqueIdentifier('urn:uuid:a26dbd34-db18-11e0-8853-001fbc013adc')

# Import bindings for namespaces imported into schema
import pyxb.binding.datatypes
import pyxb.bundles.opengis.citygml.base
import pyxb.bundles.opengis.gml
import pyxb.bundles.opengis.misc.xlinks

Namespace = pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/texturedsurface/1.0', create_if_missing=True)
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
class TextureTypeType (pyxb.binding.datatypes.string, pyxb.binding.basis.enumeration_mixin):

    """Deprecated since CityGML version 0.4.0. Use the concepts of the CityGML Appearance module instead.
                Textures can be qualified by the attribute textureType. The textureType differentiates between textures, which are
                specific for a certain object and are only used for that object (specific), and prototypic textures being typical
                for that kind of object and are used many times for all objects of that kind (typical). A typical texture may be
                replaced by a specific, if available. Textures may also be classified as unknown. """

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'TextureTypeType')
    _Documentation = u'Deprecated since CityGML version 0.4.0. Use the concepts of the CityGML Appearance module instead.\n                Textures can be qualified by the attribute textureType. The textureType differentiates between textures, which are\n                specific for a certain object and are only used for that object (specific), and prototypic textures being typical\n                for that kind of object and are used many times for all objects of that kind (typical). A typical texture may be\n                replaced by a specific, if available. Textures may also be classified as unknown. '
TextureTypeType._CF_enumeration = pyxb.binding.facets.CF_enumeration(value_datatype=TextureTypeType, enum_prefix=None)
TextureTypeType.specific = TextureTypeType._CF_enumeration.addEnumeration(unicode_value=u'specific', tag=u'specific')
TextureTypeType.typical = TextureTypeType._CF_enumeration.addEnumeration(unicode_value=u'typical', tag=u'typical')
TextureTypeType.unknown = TextureTypeType._CF_enumeration.addEnumeration(unicode_value=u'unknown', tag=u'unknown')
TextureTypeType._InitializeFacetMap(TextureTypeType._CF_enumeration)
Namespace.addCategoryObject('typeBinding', u'TextureTypeType', TextureTypeType)

# List SimpleTypeDefinition
# superclasses pyxb.bundles.opengis.citygml.base.doubleBetween0and1List
class Color (pyxb.binding.basis.STD_list):

    """Deprecated since CityGML version 0.4.0. Use the concepts of the CityGML Appearance module instead.
                List of three values (red, green, blue), separated by spaces. The values must be in the range between zero and
                one. """

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'Color')
    _Documentation = u'Deprecated since CityGML version 0.4.0. Use the concepts of the CityGML Appearance module instead.\n                List of three values (red, green, blue), separated by spaces. The values must be in the range between zero and\n                one. '

    _ItemType = pyxb.bundles.opengis.citygml.base.doubleBetween0and1
Color._CF_length = pyxb.binding.facets.CF_length(value=pyxb.binding.datatypes.nonNegativeInteger(3L))
Color._InitializeFacetMap(Color._CF_length)
Namespace.addCategoryObject('typeBinding', u'Color', Color)

# Complex type AbstractAppearanceType with content type ELEMENT_ONLY
class AbstractAppearanceType (pyxb.bundles.opengis.gml.AbstractGMLType):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = True
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'AbstractAppearanceType')
    # Base type is pyxb.bundles.opengis.gml.AbstractGMLType
    
    # Element name ({http://www.opengis.net/gml}name) inherited from {http://www.opengis.net/gml}AbstractGMLType
    
    # Element metaDataProperty ({http://www.opengis.net/gml}metaDataProperty) inherited from {http://www.opengis.net/gml}AbstractGMLType
    
    # Element description ({http://www.opengis.net/gml}description) inherited from {http://www.opengis.net/gml}AbstractGMLType
    
    # Attribute id inherited from {http://www.opengis.net/gml}AbstractGMLType

    _ElementMap = pyxb.bundles.opengis.gml.AbstractGMLType._ElementMap.copy()
    _ElementMap.update({
        
    })
    _AttributeMap = pyxb.bundles.opengis.gml.AbstractGMLType._AttributeMap.copy()
    _AttributeMap.update({
        
    })
Namespace.addCategoryObject('typeBinding', u'AbstractAppearanceType', AbstractAppearanceType)


# Complex type TexturedSurfaceType with content type ELEMENT_ONLY
class TexturedSurfaceType (pyxb.bundles.opengis.gml.OrientableSurfaceType):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'TexturedSurfaceType')
    # Base type is pyxb.bundles.opengis.gml.OrientableSurfaceType
    
    # Element {http://www.opengis.net/citygml/texturedsurface/1.0}appearance uses Python identifier appearance
    __appearance = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'appearance'), 'appearance', '__httpwww_opengis_netcitygmltexturedsurface1_0_TexturedSurfaceType_httpwww_opengis_netcitygmltexturedsurface1_0appearance', True)

    
    appearance = property(__appearance.value, __appearance.set, None, None)

    
    # Element name ({http://www.opengis.net/gml}name) inherited from {http://www.opengis.net/gml}AbstractGMLType
    
    # Element description ({http://www.opengis.net/gml}description) inherited from {http://www.opengis.net/gml}AbstractGMLType
    
    # Element metaDataProperty ({http://www.opengis.net/gml}metaDataProperty) inherited from {http://www.opengis.net/gml}AbstractGMLType
    
    # Element baseSurface ({http://www.opengis.net/gml}baseSurface) inherited from {http://www.opengis.net/gml}OrientableSurfaceType
    
    # Attribute srsName inherited from {http://www.opengis.net/gml}AbstractGeometryType
    
    # Attribute axisLabels inherited from {http://www.opengis.net/gml}AbstractGeometryType
    
    # Attribute uomLabels inherited from {http://www.opengis.net/gml}AbstractGeometryType
    
    # Attribute srsDimension inherited from {http://www.opengis.net/gml}AbstractGeometryType
    
    # Attribute gid inherited from {http://www.opengis.net/gml}AbstractGeometryType
    
    # Attribute id inherited from {http://www.opengis.net/gml}AbstractGMLType
    
    # Attribute orientation inherited from {http://www.opengis.net/gml}OrientableSurfaceType

    _ElementMap = pyxb.bundles.opengis.gml.OrientableSurfaceType._ElementMap.copy()
    _ElementMap.update({
        __appearance.name() : __appearance
    })
    _AttributeMap = pyxb.bundles.opengis.gml.OrientableSurfaceType._AttributeMap.copy()
    _AttributeMap.update({
        
    })
Namespace.addCategoryObject('typeBinding', u'TexturedSurfaceType', TexturedSurfaceType)


# Complex type SimpleTextureType with content type ELEMENT_ONLY
class SimpleTextureType (AbstractAppearanceType):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'SimpleTextureType')
    # Base type is AbstractAppearanceType
    
    # Element name ({http://www.opengis.net/gml}name) inherited from {http://www.opengis.net/gml}AbstractGMLType
    
    # Element metaDataProperty ({http://www.opengis.net/gml}metaDataProperty) inherited from {http://www.opengis.net/gml}AbstractGMLType
    
    # Element {http://www.opengis.net/citygml/texturedsurface/1.0}textureType uses Python identifier textureType
    __textureType = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'textureType'), 'textureType', '__httpwww_opengis_netcitygmltexturedsurface1_0_SimpleTextureType_httpwww_opengis_netcitygmltexturedsurface1_0textureType', False)

    
    textureType = property(__textureType.value, __textureType.set, None, None)

    
    # Element {http://www.opengis.net/citygml/texturedsurface/1.0}repeat uses Python identifier repeat
    __repeat = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'repeat'), 'repeat', '__httpwww_opengis_netcitygmltexturedsurface1_0_SimpleTextureType_httpwww_opengis_netcitygmltexturedsurface1_0repeat', False)

    
    repeat = property(__repeat.value, __repeat.set, None, None)

    
    # Element {http://www.opengis.net/citygml/texturedsurface/1.0}textureMap uses Python identifier textureMap
    __textureMap = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'textureMap'), 'textureMap', '__httpwww_opengis_netcitygmltexturedsurface1_0_SimpleTextureType_httpwww_opengis_netcitygmltexturedsurface1_0textureMap', False)

    
    textureMap = property(__textureMap.value, __textureMap.set, None, None)

    
    # Element {http://www.opengis.net/citygml/texturedsurface/1.0}textureCoordinates uses Python identifier textureCoordinates
    __textureCoordinates = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'textureCoordinates'), 'textureCoordinates', '__httpwww_opengis_netcitygmltexturedsurface1_0_SimpleTextureType_httpwww_opengis_netcitygmltexturedsurface1_0textureCoordinates', False)

    
    textureCoordinates = property(__textureCoordinates.value, __textureCoordinates.set, None, None)

    
    # Element description ({http://www.opengis.net/gml}description) inherited from {http://www.opengis.net/gml}AbstractGMLType
    
    # Attribute id inherited from {http://www.opengis.net/gml}AbstractGMLType

    _ElementMap = AbstractAppearanceType._ElementMap.copy()
    _ElementMap.update({
        __textureType.name() : __textureType,
        __repeat.name() : __repeat,
        __textureMap.name() : __textureMap,
        __textureCoordinates.name() : __textureCoordinates
    })
    _AttributeMap = AbstractAppearanceType._AttributeMap.copy()
    _AttributeMap.update({
        
    })
Namespace.addCategoryObject('typeBinding', u'SimpleTextureType', SimpleTextureType)


# Complex type AppearancePropertyType with content type ELEMENT_ONLY
class AppearancePropertyType (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'AppearancePropertyType')
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {http://www.opengis.net/citygml/texturedsurface/1.0}_Appearance uses Python identifier Appearance
    __Appearance = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'_Appearance'), 'Appearance', '__httpwww_opengis_netcitygmltexturedsurface1_0_AppearancePropertyType_httpwww_opengis_netcitygmltexturedsurface1_0_Appearance', False)

    
    Appearance = property(__Appearance.value, __Appearance.set, None, None)

    
    # Attribute {http://www.w3.org/1999/xlink}href uses Python identifier href
    __href = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'href'), 'href', '__httpwww_opengis_netcitygmltexturedsurface1_0_AppearancePropertyType_httpwww_w3_org1999xlinkhref', pyxb.binding.datatypes.anyURI)
    
    href = property(__href.value, __href.set, None, None)

    
    # Attribute {http://www.w3.org/1999/xlink}role uses Python identifier role
    __role = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'role'), 'role', '__httpwww_opengis_netcitygmltexturedsurface1_0_AppearancePropertyType_httpwww_w3_org1999xlinkrole', pyxb.binding.datatypes.anyURI)
    
    role = property(__role.value, __role.set, None, None)

    
    # Attribute {http://www.w3.org/1999/xlink}arcrole uses Python identifier arcrole
    __arcrole = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'arcrole'), 'arcrole', '__httpwww_opengis_netcitygmltexturedsurface1_0_AppearancePropertyType_httpwww_w3_org1999xlinkarcrole', pyxb.binding.datatypes.anyURI)
    
    arcrole = property(__arcrole.value, __arcrole.set, None, None)

    
    # Attribute {http://www.w3.org/1999/xlink}title uses Python identifier title
    __title = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'title'), 'title', '__httpwww_opengis_netcitygmltexturedsurface1_0_AppearancePropertyType_httpwww_w3_org1999xlinktitle', pyxb.binding.datatypes.string)
    
    title = property(__title.value, __title.set, None, None)

    
    # Attribute {http://www.w3.org/1999/xlink}type uses Python identifier type
    __type = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'type'), 'type', '__httpwww_opengis_netcitygmltexturedsurface1_0_AppearancePropertyType_httpwww_w3_org1999xlinktype', pyxb.binding.datatypes.string, fixed=True, unicode_default=u'simple')
    
    type = property(__type.value, __type.set, None, None)

    
    # Attribute orientation uses Python identifier orientation
    __orientation = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'orientation'), 'orientation', '__httpwww_opengis_netcitygmltexturedsurface1_0_AppearancePropertyType_orientation', pyxb.bundles.opengis.gml.SignType, unicode_default=u'+')
    
    orientation = property(__orientation.value, __orientation.set, None, None)

    
    # Attribute {http://www.w3.org/1999/xlink}show uses Python identifier show
    __show = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'show'), 'show', '__httpwww_opengis_netcitygmltexturedsurface1_0_AppearancePropertyType_httpwww_w3_org1999xlinkshow', pyxb.bundles.opengis.misc.xlinks.STD_ANON_)
    
    show = property(__show.value, __show.set, None, u"\n        The 'show' attribute is used to communicate the desired presentation \n        of the ending resource on traversal from the starting resource; it's \n        value should be treated as follows: \n        new - load ending resource in a new window, frame, pane, or other \n              presentation context\n        replace - load the resource in the same window, frame, pane, or \n                  other presentation context\n        embed - load ending resource in place of the presentation of the \n                starting resource\n        other - behavior is unconstrained; examine other markup in the \n                link for hints \n        none - behavior is unconstrained \n      ")

    
    # Attribute {http://www.w3.org/1999/xlink}actuate uses Python identifier actuate
    __actuate = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'actuate'), 'actuate', '__httpwww_opengis_netcitygmltexturedsurface1_0_AppearancePropertyType_httpwww_w3_org1999xlinkactuate', pyxb.bundles.opengis.misc.xlinks.STD_ANON)
    
    actuate = property(__actuate.value, __actuate.set, None, u"\n        The 'actuate' attribute is used to communicate the desired timing \n        of traversal from the starting resource to the ending resource; \n        it's value should be treated as follows:\n        onLoad - traverse to the ending resource immediately on loading \n                 the starting resource \n        onRequest - traverse from the starting resource to the ending \n                    resource only on a post-loading event triggered for \n                    this purpose \n        other - behavior is unconstrained; examine other markup in link \n                for hints \n        none - behavior is unconstrained\n      ")

    
    # Attribute {http://www.opengis.net/gml}remoteSchema uses Python identifier remoteSchema
    __remoteSchema = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'remoteSchema'), 'remoteSchema', '__httpwww_opengis_netcitygmltexturedsurface1_0_AppearancePropertyType_httpwww_opengis_netgmlremoteSchema', pyxb.binding.datatypes.anyURI)
    
    remoteSchema = property(__remoteSchema.value, __remoteSchema.set, None, u'Reference to an XML Schema fragment that specifies the content model of the propertys value. This is in conformance with the XML Schema Section 4.14 Referencing Schemas from Elsewhere.')


    _ElementMap = {
        __Appearance.name() : __Appearance
    }
    _AttributeMap = {
        __href.name() : __href,
        __role.name() : __role,
        __arcrole.name() : __arcrole,
        __title.name() : __title,
        __type.name() : __type,
        __orientation.name() : __orientation,
        __show.name() : __show,
        __actuate.name() : __actuate,
        __remoteSchema.name() : __remoteSchema
    }
Namespace.addCategoryObject('typeBinding', u'AppearancePropertyType', AppearancePropertyType)


# Complex type MaterialType with content type ELEMENT_ONLY
class MaterialType (AbstractAppearanceType):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'MaterialType')
    # Base type is AbstractAppearanceType
    
    # Element name ({http://www.opengis.net/gml}name) inherited from {http://www.opengis.net/gml}AbstractGMLType
    
    # Element {http://www.opengis.net/citygml/texturedsurface/1.0}shininess uses Python identifier shininess
    __shininess = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'shininess'), 'shininess', '__httpwww_opengis_netcitygmltexturedsurface1_0_MaterialType_httpwww_opengis_netcitygmltexturedsurface1_0shininess', False)

    
    shininess = property(__shininess.value, __shininess.set, None, None)

    
    # Element {http://www.opengis.net/citygml/texturedsurface/1.0}diffuseColor uses Python identifier diffuseColor
    __diffuseColor = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'diffuseColor'), 'diffuseColor', '__httpwww_opengis_netcitygmltexturedsurface1_0_MaterialType_httpwww_opengis_netcitygmltexturedsurface1_0diffuseColor', False)

    
    diffuseColor = property(__diffuseColor.value, __diffuseColor.set, None, None)

    
    # Element {http://www.opengis.net/citygml/texturedsurface/1.0}ambientIntensity uses Python identifier ambientIntensity
    __ambientIntensity = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'ambientIntensity'), 'ambientIntensity', '__httpwww_opengis_netcitygmltexturedsurface1_0_MaterialType_httpwww_opengis_netcitygmltexturedsurface1_0ambientIntensity', False)

    
    ambientIntensity = property(__ambientIntensity.value, __ambientIntensity.set, None, None)

    
    # Element {http://www.opengis.net/citygml/texturedsurface/1.0}emissiveColor uses Python identifier emissiveColor
    __emissiveColor = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'emissiveColor'), 'emissiveColor', '__httpwww_opengis_netcitygmltexturedsurface1_0_MaterialType_httpwww_opengis_netcitygmltexturedsurface1_0emissiveColor', False)

    
    emissiveColor = property(__emissiveColor.value, __emissiveColor.set, None, None)

    
    # Element metaDataProperty ({http://www.opengis.net/gml}metaDataProperty) inherited from {http://www.opengis.net/gml}AbstractGMLType
    
    # Element {http://www.opengis.net/citygml/texturedsurface/1.0}transparency uses Python identifier transparency
    __transparency = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'transparency'), 'transparency', '__httpwww_opengis_netcitygmltexturedsurface1_0_MaterialType_httpwww_opengis_netcitygmltexturedsurface1_0transparency', False)

    
    transparency = property(__transparency.value, __transparency.set, None, None)

    
    # Element {http://www.opengis.net/citygml/texturedsurface/1.0}specularColor uses Python identifier specularColor
    __specularColor = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'specularColor'), 'specularColor', '__httpwww_opengis_netcitygmltexturedsurface1_0_MaterialType_httpwww_opengis_netcitygmltexturedsurface1_0specularColor', False)

    
    specularColor = property(__specularColor.value, __specularColor.set, None, None)

    
    # Element description ({http://www.opengis.net/gml}description) inherited from {http://www.opengis.net/gml}AbstractGMLType
    
    # Attribute id inherited from {http://www.opengis.net/gml}AbstractGMLType

    _ElementMap = AbstractAppearanceType._ElementMap.copy()
    _ElementMap.update({
        __shininess.name() : __shininess,
        __diffuseColor.name() : __diffuseColor,
        __ambientIntensity.name() : __ambientIntensity,
        __emissiveColor.name() : __emissiveColor,
        __transparency.name() : __transparency,
        __specularColor.name() : __specularColor
    })
    _AttributeMap = AbstractAppearanceType._AttributeMap.copy()
    _AttributeMap.update({
        
    })
Namespace.addCategoryObject('typeBinding', u'MaterialType', MaterialType)


Appearance = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'_Appearance'), AbstractAppearanceType, abstract=pyxb.binding.datatypes.boolean(1))
Namespace.addCategoryObject('elementBinding', Appearance.name().localName(), Appearance)

TexturedSurface = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'TexturedSurface'), TexturedSurfaceType)
Namespace.addCategoryObject('elementBinding', TexturedSurface.name().localName(), TexturedSurface)

SimpleTexture = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'SimpleTexture'), SimpleTextureType)
Namespace.addCategoryObject('elementBinding', SimpleTexture.name().localName(), SimpleTexture)

appearance = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'appearance'), AppearancePropertyType)
Namespace.addCategoryObject('elementBinding', appearance.name().localName(), appearance)

Material = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Material'), MaterialType)
Namespace.addCategoryObject('elementBinding', Material.name().localName(), Material)


AbstractAppearanceType._GroupModel_3 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(AbstractAppearanceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'metaDataProperty')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(AbstractAppearanceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'description')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(AbstractAppearanceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'name')), min_occurs=0L, max_occurs=None)
    )
AbstractAppearanceType._GroupModel_2 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(AbstractAppearanceType._GroupModel_3, min_occurs=1, max_occurs=1)
    )
AbstractAppearanceType._ContentModel = pyxb.binding.content.ParticleModel(AbstractAppearanceType._GroupModel_2, min_occurs=1, max_occurs=1)



TexturedSurfaceType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'appearance'), AppearancePropertyType, scope=TexturedSurfaceType))
TexturedSurfaceType._GroupModel_7 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(TexturedSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'metaDataProperty')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(TexturedSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'description')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(TexturedSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'name')), min_occurs=0L, max_occurs=None)
    )
TexturedSurfaceType._GroupModel_6 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(TexturedSurfaceType._GroupModel_7, min_occurs=1, max_occurs=1)
    )
TexturedSurfaceType._GroupModel_8 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(TexturedSurfaceType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'baseSurface')), min_occurs=1, max_occurs=1)
    )
TexturedSurfaceType._GroupModel_5 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(TexturedSurfaceType._GroupModel_6, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(TexturedSurfaceType._GroupModel_8, min_occurs=1, max_occurs=1)
    )
TexturedSurfaceType._GroupModel_9 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(TexturedSurfaceType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'appearance')), min_occurs=1, max_occurs=None)
    )
TexturedSurfaceType._GroupModel_4 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(TexturedSurfaceType._GroupModel_5, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(TexturedSurfaceType._GroupModel_9, min_occurs=1, max_occurs=1)
    )
TexturedSurfaceType._ContentModel = pyxb.binding.content.ParticleModel(TexturedSurfaceType._GroupModel_4, min_occurs=1, max_occurs=1)



SimpleTextureType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'textureType'), TextureTypeType, scope=SimpleTextureType))

SimpleTextureType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'repeat'), pyxb.binding.datatypes.boolean, scope=SimpleTextureType))

SimpleTextureType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'textureMap'), pyxb.binding.datatypes.anyURI, scope=SimpleTextureType))

SimpleTextureType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'textureCoordinates'), pyxb.bundles.opengis.gml.doubleList, scope=SimpleTextureType))
SimpleTextureType._GroupModel_4 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(SimpleTextureType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'metaDataProperty')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(SimpleTextureType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'description')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(SimpleTextureType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'name')), min_occurs=0L, max_occurs=None)
    )
SimpleTextureType._GroupModel_3 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(SimpleTextureType._GroupModel_4, min_occurs=1, max_occurs=1)
    )
SimpleTextureType._GroupModel_5 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(SimpleTextureType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'textureMap')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(SimpleTextureType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'textureCoordinates')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(SimpleTextureType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'textureType')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(SimpleTextureType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'repeat')), min_occurs=0L, max_occurs=1)
    )
SimpleTextureType._GroupModel_2 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(SimpleTextureType._GroupModel_3, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(SimpleTextureType._GroupModel_5, min_occurs=1, max_occurs=1)
    )
SimpleTextureType._ContentModel = pyxb.binding.content.ParticleModel(SimpleTextureType._GroupModel_2, min_occurs=1, max_occurs=1)



AppearancePropertyType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'_Appearance'), AbstractAppearanceType, abstract=pyxb.binding.datatypes.boolean(1), scope=AppearancePropertyType))
AppearancePropertyType._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(AppearancePropertyType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_Appearance')), min_occurs=1, max_occurs=1)
    )
AppearancePropertyType._ContentModel = pyxb.binding.content.ParticleModel(AppearancePropertyType._GroupModel, min_occurs=0L, max_occurs=1)



MaterialType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'shininess'), pyxb.bundles.opengis.citygml.base.doubleBetween0and1, scope=MaterialType))

MaterialType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'diffuseColor'), Color, scope=MaterialType))

MaterialType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'ambientIntensity'), pyxb.bundles.opengis.citygml.base.doubleBetween0and1, scope=MaterialType))

MaterialType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'emissiveColor'), Color, scope=MaterialType))

MaterialType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'transparency'), pyxb.bundles.opengis.citygml.base.doubleBetween0and1, scope=MaterialType))

MaterialType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'specularColor'), Color, scope=MaterialType))
MaterialType._GroupModel_4 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(MaterialType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'metaDataProperty')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(MaterialType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'description')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(MaterialType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'name')), min_occurs=0L, max_occurs=None)
    )
MaterialType._GroupModel_3 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(MaterialType._GroupModel_4, min_occurs=1, max_occurs=1)
    )
MaterialType._GroupModel_5 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(MaterialType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'shininess')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(MaterialType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'transparency')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(MaterialType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'ambientIntensity')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(MaterialType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'specularColor')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(MaterialType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'diffuseColor')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(MaterialType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'emissiveColor')), min_occurs=0L, max_occurs=1)
    )
MaterialType._GroupModel_2 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(MaterialType._GroupModel_3, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(MaterialType._GroupModel_5, min_occurs=1, max_occurs=1)
    )
MaterialType._ContentModel = pyxb.binding.content.ParticleModel(MaterialType._GroupModel_2, min_occurs=1, max_occurs=1)

Appearance._setSubstitutionGroup(pyxb.bundles.opengis.gml.GML)

TexturedSurface._setSubstitutionGroup(pyxb.bundles.opengis.gml.OrientableSurface)

SimpleTexture._setSubstitutionGroup(Appearance)

Material._setSubstitutionGroup(Appearance)
