# ./pyxb/bundles/opengis/citygml/raw/cityObjectGroup.py
# PyXB bindings for NM:e6932fbb101c5dffa115bf309ae8f51978213e97
# Generated 2011-09-09 14:19:22.437339 by PyXB version 1.1.3
# Namespace http://www.opengis.net/citygml/cityobjectgroup/1.0

import pyxb
import pyxb.binding
import pyxb.binding.saxer
import StringIO
import pyxb.utils.utility
import pyxb.utils.domutils
import sys

# Unique identifier for bindings created at the same time
_GenerationUID = pyxb.utils.utility.UniqueIdentifier('urn:uuid:9efb83d4-db18-11e0-b0aa-001fbc013adc')

# Import bindings for namespaces imported into schema
import pyxb.bundles.opengis.citygml.base
import pyxb.binding.datatypes
import pyxb.bundles.opengis.gml
import pyxb.bundles.opengis.misc.xlinks

Namespace = pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/cityobjectgroup/1.0', create_if_missing=True)
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


# Complex type CityObjectGroupType with content type ELEMENT_ONLY
class CityObjectGroupType (pyxb.bundles.opengis.citygml.base.AbstractCityObjectType):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'CityObjectGroupType')
    # Base type is pyxb.bundles.opengis.citygml.base.AbstractCityObjectType
    
    # Element name ({http://www.opengis.net/gml}name) inherited from {http://www.opengis.net/gml}AbstractGMLType
    
    # Element creationDate ({http://www.opengis.net/citygml/1.0}creationDate) inherited from {http://www.opengis.net/citygml/1.0}AbstractCityObjectType
    
    # Element {http://www.opengis.net/citygml/cityobjectgroup/1.0}usage uses Python identifier usage
    __usage = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'usage'), 'usage', '__httpwww_opengis_netcitygmlcityobjectgroup1_0_CityObjectGroupType_httpwww_opengis_netcitygmlcityobjectgroup1_0usage', True)

    
    usage = property(__usage.value, __usage.set, None, None)

    
    # Element metaDataProperty ({http://www.opengis.net/gml}metaDataProperty) inherited from {http://www.opengis.net/gml}AbstractGMLType
    
    # Element location ({http://www.opengis.net/gml}location) inherited from {http://www.opengis.net/gml}AbstractFeatureType
    
    # Element {http://www.opengis.net/citygml/cityobjectgroup/1.0}_GenericApplicationPropertyOfCityObjectGroup uses Python identifier GenericApplicationPropertyOfCityObjectGroup
    __GenericApplicationPropertyOfCityObjectGroup = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfCityObjectGroup'), 'GenericApplicationPropertyOfCityObjectGroup', '__httpwww_opengis_netcitygmlcityobjectgroup1_0_CityObjectGroupType_httpwww_opengis_netcitygmlcityobjectgroup1_0_GenericApplicationPropertyOfCityObjectGroup', True)

    
    GenericApplicationPropertyOfCityObjectGroup = property(__GenericApplicationPropertyOfCityObjectGroup.value, __GenericApplicationPropertyOfCityObjectGroup.set, None, None)

    
    # Element {http://www.opengis.net/citygml/cityobjectgroup/1.0}class uses Python identifier class_
    __class = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'class'), 'class_', '__httpwww_opengis_netcitygmlcityobjectgroup1_0_CityObjectGroupType_httpwww_opengis_netcitygmlcityobjectgroup1_0class', False)

    
    class_ = property(__class.value, __class.set, None, None)

    
    # Element {http://www.opengis.net/citygml/cityobjectgroup/1.0}groupMember uses Python identifier groupMember
    __groupMember = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'groupMember'), 'groupMember', '__httpwww_opengis_netcitygmlcityobjectgroup1_0_CityObjectGroupType_httpwww_opengis_netcitygmlcityobjectgroup1_0groupMember', True)

    
    groupMember = property(__groupMember.value, __groupMember.set, None, None)

    
    # Element generalizesTo ({http://www.opengis.net/citygml/1.0}generalizesTo) inherited from {http://www.opengis.net/citygml/1.0}AbstractCityObjectType
    
    # Element {http://www.opengis.net/citygml/cityobjectgroup/1.0}function uses Python identifier function
    __function = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'function'), 'function', '__httpwww_opengis_netcitygmlcityobjectgroup1_0_CityObjectGroupType_httpwww_opengis_netcitygmlcityobjectgroup1_0function', True)

    
    function = property(__function.value, __function.set, None, None)

    
    # Element {http://www.opengis.net/citygml/cityobjectgroup/1.0}geometry uses Python identifier geometry
    __geometry = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'geometry'), 'geometry', '__httpwww_opengis_netcitygmlcityobjectgroup1_0_CityObjectGroupType_httpwww_opengis_netcitygmlcityobjectgroup1_0geometry', False)

    
    geometry = property(__geometry.value, __geometry.set, None, None)

    
    # Element {http://www.opengis.net/citygml/cityobjectgroup/1.0}parent uses Python identifier parent
    __parent = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'parent'), 'parent', '__httpwww_opengis_netcitygmlcityobjectgroup1_0_CityObjectGroupType_httpwww_opengis_netcitygmlcityobjectgroup1_0parent', False)

    
    parent = property(__parent.value, __parent.set, None, None)

    
    # Element externalReference ({http://www.opengis.net/citygml/1.0}externalReference) inherited from {http://www.opengis.net/citygml/1.0}AbstractCityObjectType
    
    # Element terminationDate ({http://www.opengis.net/citygml/1.0}terminationDate) inherited from {http://www.opengis.net/citygml/1.0}AbstractCityObjectType
    
    # Element boundedBy ({http://www.opengis.net/gml}boundedBy) inherited from {http://www.opengis.net/gml}AbstractFeatureType
    
    # Element GenericApplicationPropertyOfCityObject ({http://www.opengis.net/citygml/1.0}_GenericApplicationPropertyOfCityObject) inherited from {http://www.opengis.net/citygml/1.0}AbstractCityObjectType
    
    # Element description ({http://www.opengis.net/gml}description) inherited from {http://www.opengis.net/gml}AbstractGMLType
    
    # Attribute id inherited from {http://www.opengis.net/gml}AbstractGMLType

    _ElementMap = pyxb.bundles.opengis.citygml.base.AbstractCityObjectType._ElementMap.copy()
    _ElementMap.update({
        __usage.name() : __usage,
        __GenericApplicationPropertyOfCityObjectGroup.name() : __GenericApplicationPropertyOfCityObjectGroup,
        __class.name() : __class,
        __groupMember.name() : __groupMember,
        __function.name() : __function,
        __geometry.name() : __geometry,
        __parent.name() : __parent
    })
    _AttributeMap = pyxb.bundles.opengis.citygml.base.AbstractCityObjectType._AttributeMap.copy()
    _AttributeMap.update({
        
    })
Namespace.addCategoryObject('typeBinding', u'CityObjectGroupType', CityObjectGroupType)


# Complex type CityObjectGroupMemberType with content type ELEMENT_ONLY
class CityObjectGroupMemberType (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'CityObjectGroupMemberType')
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {http://www.opengis.net/citygml/1.0}_CityObject uses Python identifier CityObject
    __CityObject = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'_CityObject'), 'CityObject', '__httpwww_opengis_netcitygmlcityobjectgroup1_0_CityObjectGroupMemberType_httpwww_opengis_netcitygml1_0_CityObject', False)

    
    CityObject = property(__CityObject.value, __CityObject.set, None, None)

    
    # Attribute {http://www.w3.org/1999/xlink}role uses Python identifier role_
    __role_ = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'role'), 'role_', '__httpwww_opengis_netcitygmlcityobjectgroup1_0_CityObjectGroupMemberType_httpwww_w3_org1999xlinkrole', pyxb.binding.datatypes.anyURI)
    
    role_ = property(__role_.value, __role_.set, None, None)

    
    # Attribute {http://www.w3.org/1999/xlink}arcrole uses Python identifier arcrole
    __arcrole = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'arcrole'), 'arcrole', '__httpwww_opengis_netcitygmlcityobjectgroup1_0_CityObjectGroupMemberType_httpwww_w3_org1999xlinkarcrole', pyxb.binding.datatypes.anyURI)
    
    arcrole = property(__arcrole.value, __arcrole.set, None, None)

    
    # Attribute {http://www.w3.org/1999/xlink}show uses Python identifier show
    __show = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'show'), 'show', '__httpwww_opengis_netcitygmlcityobjectgroup1_0_CityObjectGroupMemberType_httpwww_w3_org1999xlinkshow', pyxb.bundles.opengis.misc.xlinks.STD_ANON_)
    
    show = property(__show.value, __show.set, None, u"\n        The 'show' attribute is used to communicate the desired presentation \n        of the ending resource on traversal from the starting resource; it's \n        value should be treated as follows: \n        new - load ending resource in a new window, frame, pane, or other \n              presentation context\n        replace - load the resource in the same window, frame, pane, or \n                  other presentation context\n        embed - load ending resource in place of the presentation of the \n                starting resource\n        other - behavior is unconstrained; examine other markup in the \n                link for hints \n        none - behavior is unconstrained \n      ")

    
    # Attribute {http://www.w3.org/1999/xlink}title uses Python identifier title
    __title = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'title'), 'title', '__httpwww_opengis_netcitygmlcityobjectgroup1_0_CityObjectGroupMemberType_httpwww_w3_org1999xlinktitle', pyxb.binding.datatypes.string)
    
    title = property(__title.value, __title.set, None, None)

    
    # Attribute {http://www.w3.org/1999/xlink}type uses Python identifier type
    __type = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'type'), 'type', '__httpwww_opengis_netcitygmlcityobjectgroup1_0_CityObjectGroupMemberType_httpwww_w3_org1999xlinktype', pyxb.binding.datatypes.string, fixed=True, unicode_default=u'simple')
    
    type = property(__type.value, __type.set, None, None)

    
    # Attribute {http://www.w3.org/1999/xlink}actuate uses Python identifier actuate
    __actuate = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'actuate'), 'actuate', '__httpwww_opengis_netcitygmlcityobjectgroup1_0_CityObjectGroupMemberType_httpwww_w3_org1999xlinkactuate', pyxb.bundles.opengis.misc.xlinks.STD_ANON)
    
    actuate = property(__actuate.value, __actuate.set, None, u"\n        The 'actuate' attribute is used to communicate the desired timing \n        of traversal from the starting resource to the ending resource; \n        it's value should be treated as follows:\n        onLoad - traverse to the ending resource immediately on loading \n                 the starting resource \n        onRequest - traverse from the starting resource to the ending \n                    resource only on a post-loading event triggered for \n                    this purpose \n        other - behavior is unconstrained; examine other markup in link \n                for hints \n        none - behavior is unconstrained\n      ")

    
    # Attribute {http://www.opengis.net/gml}remoteSchema uses Python identifier remoteSchema
    __remoteSchema = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'remoteSchema'), 'remoteSchema', '__httpwww_opengis_netcitygmlcityobjectgroup1_0_CityObjectGroupMemberType_httpwww_opengis_netgmlremoteSchema', pyxb.binding.datatypes.anyURI)
    
    remoteSchema = property(__remoteSchema.value, __remoteSchema.set, None, u'Reference to an XML Schema fragment that specifies the content model of the propertys value. This is in conformance with the XML Schema Section 4.14 Referencing Schemas from Elsewhere.')

    
    # Attribute role uses Python identifier role
    __role = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'role'), 'role', '__httpwww_opengis_netcitygmlcityobjectgroup1_0_CityObjectGroupMemberType_role', pyxb.binding.datatypes.string)
    
    role = property(__role.value, __role.set, None, None)

    
    # Attribute {http://www.w3.org/1999/xlink}href uses Python identifier href
    __href = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'href'), 'href', '__httpwww_opengis_netcitygmlcityobjectgroup1_0_CityObjectGroupMemberType_httpwww_w3_org1999xlinkhref', pyxb.binding.datatypes.anyURI)
    
    href = property(__href.value, __href.set, None, None)


    _ElementMap = {
        __CityObject.name() : __CityObject
    }
    _AttributeMap = {
        __role_.name() : __role_,
        __arcrole.name() : __arcrole,
        __show.name() : __show,
        __title.name() : __title,
        __type.name() : __type,
        __actuate.name() : __actuate,
        __remoteSchema.name() : __remoteSchema,
        __role.name() : __role,
        __href.name() : __href
    }
Namespace.addCategoryObject('typeBinding', u'CityObjectGroupMemberType', CityObjectGroupMemberType)


# Complex type CityObjectGroupParentType with content type ELEMENT_ONLY
class CityObjectGroupParentType (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'CityObjectGroupParentType')
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {http://www.opengis.net/citygml/1.0}_CityObject uses Python identifier CityObject
    __CityObject = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'_CityObject'), 'CityObject', '__httpwww_opengis_netcitygmlcityobjectgroup1_0_CityObjectGroupParentType_httpwww_opengis_netcitygml1_0_CityObject', False)

    
    CityObject = property(__CityObject.value, __CityObject.set, None, None)

    
    # Attribute {http://www.w3.org/1999/xlink}actuate uses Python identifier actuate
    __actuate = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'actuate'), 'actuate', '__httpwww_opengis_netcitygmlcityobjectgroup1_0_CityObjectGroupParentType_httpwww_w3_org1999xlinkactuate', pyxb.bundles.opengis.misc.xlinks.STD_ANON)
    
    actuate = property(__actuate.value, __actuate.set, None, u"\n        The 'actuate' attribute is used to communicate the desired timing \n        of traversal from the starting resource to the ending resource; \n        it's value should be treated as follows:\n        onLoad - traverse to the ending resource immediately on loading \n                 the starting resource \n        onRequest - traverse from the starting resource to the ending \n                    resource only on a post-loading event triggered for \n                    this purpose \n        other - behavior is unconstrained; examine other markup in link \n                for hints \n        none - behavior is unconstrained\n      ")

    
    # Attribute {http://www.w3.org/1999/xlink}show uses Python identifier show
    __show = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'show'), 'show', '__httpwww_opengis_netcitygmlcityobjectgroup1_0_CityObjectGroupParentType_httpwww_w3_org1999xlinkshow', pyxb.bundles.opengis.misc.xlinks.STD_ANON_)
    
    show = property(__show.value, __show.set, None, u"\n        The 'show' attribute is used to communicate the desired presentation \n        of the ending resource on traversal from the starting resource; it's \n        value should be treated as follows: \n        new - load ending resource in a new window, frame, pane, or other \n              presentation context\n        replace - load the resource in the same window, frame, pane, or \n                  other presentation context\n        embed - load ending resource in place of the presentation of the \n                starting resource\n        other - behavior is unconstrained; examine other markup in the \n                link for hints \n        none - behavior is unconstrained \n      ")

    
    # Attribute {http://www.w3.org/1999/xlink}role uses Python identifier role
    __role = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'role'), 'role', '__httpwww_opengis_netcitygmlcityobjectgroup1_0_CityObjectGroupParentType_httpwww_w3_org1999xlinkrole', pyxb.binding.datatypes.anyURI)
    
    role = property(__role.value, __role.set, None, None)

    
    # Attribute {http://www.w3.org/1999/xlink}type uses Python identifier type
    __type = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'type'), 'type', '__httpwww_opengis_netcitygmlcityobjectgroup1_0_CityObjectGroupParentType_httpwww_w3_org1999xlinktype', pyxb.binding.datatypes.string, fixed=True, unicode_default=u'simple')
    
    type = property(__type.value, __type.set, None, None)

    
    # Attribute {http://www.w3.org/1999/xlink}href uses Python identifier href
    __href = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'href'), 'href', '__httpwww_opengis_netcitygmlcityobjectgroup1_0_CityObjectGroupParentType_httpwww_w3_org1999xlinkhref', pyxb.binding.datatypes.anyURI)
    
    href = property(__href.value, __href.set, None, None)

    
    # Attribute {http://www.w3.org/1999/xlink}title uses Python identifier title
    __title = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'title'), 'title', '__httpwww_opengis_netcitygmlcityobjectgroup1_0_CityObjectGroupParentType_httpwww_w3_org1999xlinktitle', pyxb.binding.datatypes.string)
    
    title = property(__title.value, __title.set, None, None)

    
    # Attribute {http://www.w3.org/1999/xlink}arcrole uses Python identifier arcrole
    __arcrole = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/1999/xlink'), u'arcrole'), 'arcrole', '__httpwww_opengis_netcitygmlcityobjectgroup1_0_CityObjectGroupParentType_httpwww_w3_org1999xlinkarcrole', pyxb.binding.datatypes.anyURI)
    
    arcrole = property(__arcrole.value, __arcrole.set, None, None)

    
    # Attribute {http://www.opengis.net/gml}remoteSchema uses Python identifier remoteSchema
    __remoteSchema = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'remoteSchema'), 'remoteSchema', '__httpwww_opengis_netcitygmlcityobjectgroup1_0_CityObjectGroupParentType_httpwww_opengis_netgmlremoteSchema', pyxb.binding.datatypes.anyURI)
    
    remoteSchema = property(__remoteSchema.value, __remoteSchema.set, None, u'Reference to an XML Schema fragment that specifies the content model of the propertys value. This is in conformance with the XML Schema Section 4.14 Referencing Schemas from Elsewhere.')


    _ElementMap = {
        __CityObject.name() : __CityObject
    }
    _AttributeMap = {
        __actuate.name() : __actuate,
        __show.name() : __show,
        __role.name() : __role,
        __type.name() : __type,
        __href.name() : __href,
        __title.name() : __title,
        __arcrole.name() : __arcrole,
        __remoteSchema.name() : __remoteSchema
    }
Namespace.addCategoryObject('typeBinding', u'CityObjectGroupParentType', CityObjectGroupParentType)


CityObjectGroup = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'CityObjectGroup'), CityObjectGroupType)
Namespace.addCategoryObject('elementBinding', CityObjectGroup.name().localName(), CityObjectGroup)

GenericApplicationPropertyOfCityObjectGroup = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfCityObjectGroup'), pyxb.binding.datatypes.anyType, abstract=pyxb.binding.datatypes.boolean(1))
Namespace.addCategoryObject('elementBinding', GenericApplicationPropertyOfCityObjectGroup.name().localName(), GenericApplicationPropertyOfCityObjectGroup)



CityObjectGroupType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'usage'), pyxb.binding.datatypes.string, scope=CityObjectGroupType))

CityObjectGroupType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfCityObjectGroup'), pyxb.binding.datatypes.anyType, abstract=pyxb.binding.datatypes.boolean(1), scope=CityObjectGroupType))

CityObjectGroupType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'class'), pyxb.binding.datatypes.string, scope=CityObjectGroupType))

CityObjectGroupType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'groupMember'), CityObjectGroupMemberType, scope=CityObjectGroupType))

CityObjectGroupType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'function'), pyxb.binding.datatypes.string, scope=CityObjectGroupType))

CityObjectGroupType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'geometry'), pyxb.bundles.opengis.gml.GeometryPropertyType, scope=CityObjectGroupType))

CityObjectGroupType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'parent'), CityObjectGroupParentType, scope=CityObjectGroupType))
CityObjectGroupType._GroupModel_14 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(CityObjectGroupType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'metaDataProperty')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(CityObjectGroupType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'description')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(CityObjectGroupType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'name')), min_occurs=0L, max_occurs=None)
    )
CityObjectGroupType._GroupModel_13 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(CityObjectGroupType._GroupModel_14, min_occurs=1, max_occurs=1)
    )
CityObjectGroupType._GroupModel_15 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(CityObjectGroupType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'boundedBy')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(CityObjectGroupType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gml'), u'location')), min_occurs=0L, max_occurs=1)
    )
CityObjectGroupType._GroupModel_12 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(CityObjectGroupType._GroupModel_13, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(CityObjectGroupType._GroupModel_15, min_occurs=1, max_occurs=1)
    )
CityObjectGroupType._GroupModel_16 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(CityObjectGroupType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'creationDate')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(CityObjectGroupType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'terminationDate')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(CityObjectGroupType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'externalReference')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(CityObjectGroupType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'generalizesTo')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(CityObjectGroupType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'_GenericApplicationPropertyOfCityObject')), min_occurs=0L, max_occurs=None)
    )
CityObjectGroupType._GroupModel_11 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(CityObjectGroupType._GroupModel_12, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(CityObjectGroupType._GroupModel_16, min_occurs=1, max_occurs=1)
    )
CityObjectGroupType._GroupModel_17 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(CityObjectGroupType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'class')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(CityObjectGroupType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'function')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(CityObjectGroupType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'usage')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(CityObjectGroupType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'groupMember')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(CityObjectGroupType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'parent')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(CityObjectGroupType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'geometry')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(CityObjectGroupType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'_GenericApplicationPropertyOfCityObjectGroup')), min_occurs=0L, max_occurs=None)
    )
CityObjectGroupType._GroupModel_10 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(CityObjectGroupType._GroupModel_11, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(CityObjectGroupType._GroupModel_17, min_occurs=1, max_occurs=1)
    )
CityObjectGroupType._ContentModel = pyxb.binding.content.ParticleModel(CityObjectGroupType._GroupModel_10, min_occurs=1, max_occurs=1)



CityObjectGroupMemberType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'_CityObject'), pyxb.bundles.opengis.citygml.base.AbstractCityObjectType, abstract=pyxb.binding.datatypes.boolean(1), scope=CityObjectGroupMemberType))
CityObjectGroupMemberType._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(CityObjectGroupMemberType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'_CityObject')), min_occurs=1, max_occurs=1)
    )
CityObjectGroupMemberType._ContentModel = pyxb.binding.content.ParticleModel(CityObjectGroupMemberType._GroupModel, min_occurs=0L, max_occurs=1)



CityObjectGroupParentType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'_CityObject'), pyxb.bundles.opengis.citygml.base.AbstractCityObjectType, abstract=pyxb.binding.datatypes.boolean(1), scope=CityObjectGroupParentType))
CityObjectGroupParentType._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(CityObjectGroupParentType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/citygml/1.0'), u'_CityObject')), min_occurs=1, max_occurs=1)
    )
CityObjectGroupParentType._ContentModel = pyxb.binding.content.ParticleModel(CityObjectGroupParentType._GroupModel, min_occurs=0L, max_occurs=1)

CityObjectGroup._setSubstitutionGroup(pyxb.bundles.opengis.citygml.base.CityObject)
