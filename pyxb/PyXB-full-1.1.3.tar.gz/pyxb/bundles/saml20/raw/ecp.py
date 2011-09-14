# ./pyxb/bundles/saml20/raw/ecp.py
# PyXB bindings for NM:2fcdef609f6a0a75f54ed59ff0ad0ce2350eb6e6
# Generated 2011-09-09 14:19:37.305942 by PyXB version 1.1.3
# Namespace urn:oasis:names:tc:SAML:2.0:profiles:SSO:ecp

import pyxb
import pyxb.binding
import pyxb.binding.saxer
import StringIO
import pyxb.utils.utility
import pyxb.utils.domutils
import sys

# Unique identifier for bindings created at the same time
_GenerationUID = pyxb.utils.utility.UniqueIdentifier('urn:uuid:a86aa008-db18-11e0-9c55-001fbc013adc')

# Import bindings for namespaces imported into schema
import pyxb.binding.datatypes
import pyxb.bundles.saml20.protocol
import pyxb.bundles.saml20.assertion
import pyxb.bundles.wssplat.soap11

Namespace = pyxb.namespace.NamespaceForURI(u'urn:oasis:names:tc:SAML:2.0:profiles:SSO:ecp', create_if_missing=True)
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


# Complex type RequestType with content type ELEMENT_ONLY
class RequestType (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'RequestType')
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {urn:oasis:names:tc:SAML:2.0:protocol}IDPList uses Python identifier IDPList
    __IDPList = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'urn:oasis:names:tc:SAML:2.0:protocol'), u'IDPList'), 'IDPList', '__urnoasisnamestcSAML2_0profilesSSOecp_RequestType_urnoasisnamestcSAML2_0protocolIDPList', False)

    
    IDPList = property(__IDPList.value, __IDPList.set, None, None)

    
    # Element {urn:oasis:names:tc:SAML:2.0:assertion}Issuer uses Python identifier Issuer
    __Issuer = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'urn:oasis:names:tc:SAML:2.0:assertion'), u'Issuer'), 'Issuer', '__urnoasisnamestcSAML2_0profilesSSOecp_RequestType_urnoasisnamestcSAML2_0assertionIssuer', False)

    
    Issuer = property(__Issuer.value, __Issuer.set, None, None)

    
    # Attribute {http://schemas.xmlsoap.org/soap/envelope/}actor uses Python identifier actor
    __actor = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://schemas.xmlsoap.org/soap/envelope/'), u'actor'), 'actor', '__urnoasisnamestcSAML2_0profilesSSOecp_RequestType_httpschemas_xmlsoap_orgsoapenvelopeactor', pyxb.binding.datatypes.anyURI, required=True)
    
    actor = property(__actor.value, __actor.set, None, None)

    
    # Attribute IsPassive uses Python identifier IsPassive
    __IsPassive = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'IsPassive'), 'IsPassive', '__urnoasisnamestcSAML2_0profilesSSOecp_RequestType_IsPassive', pyxb.binding.datatypes.boolean)
    
    IsPassive = property(__IsPassive.value, __IsPassive.set, None, None)

    
    # Attribute {http://schemas.xmlsoap.org/soap/envelope/}mustUnderstand uses Python identifier mustUnderstand
    __mustUnderstand = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://schemas.xmlsoap.org/soap/envelope/'), u'mustUnderstand'), 'mustUnderstand', '__urnoasisnamestcSAML2_0profilesSSOecp_RequestType_httpschemas_xmlsoap_orgsoapenvelopemustUnderstand', pyxb.bundles.wssplat.soap11.STD_ANON, required=True)
    
    mustUnderstand = property(__mustUnderstand.value, __mustUnderstand.set, None, None)

    
    # Attribute ProviderName uses Python identifier ProviderName
    __ProviderName = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'ProviderName'), 'ProviderName', '__urnoasisnamestcSAML2_0profilesSSOecp_RequestType_ProviderName', pyxb.binding.datatypes.string)
    
    ProviderName = property(__ProviderName.value, __ProviderName.set, None, None)


    _ElementMap = {
        __IDPList.name() : __IDPList,
        __Issuer.name() : __Issuer
    }
    _AttributeMap = {
        __actor.name() : __actor,
        __IsPassive.name() : __IsPassive,
        __mustUnderstand.name() : __mustUnderstand,
        __ProviderName.name() : __ProviderName
    }
Namespace.addCategoryObject('typeBinding', u'RequestType', RequestType)


# Complex type RelayStateType with content type SIMPLE
class RelayStateType (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = pyxb.binding.datatypes.string
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_SIMPLE
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'RelayStateType')
    # Base type is pyxb.binding.datatypes.string
    
    # Attribute {http://schemas.xmlsoap.org/soap/envelope/}mustUnderstand uses Python identifier mustUnderstand
    __mustUnderstand = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://schemas.xmlsoap.org/soap/envelope/'), u'mustUnderstand'), 'mustUnderstand', '__urnoasisnamestcSAML2_0profilesSSOecp_RelayStateType_httpschemas_xmlsoap_orgsoapenvelopemustUnderstand', pyxb.bundles.wssplat.soap11.STD_ANON, required=True)
    
    mustUnderstand = property(__mustUnderstand.value, __mustUnderstand.set, None, None)

    
    # Attribute {http://schemas.xmlsoap.org/soap/envelope/}actor uses Python identifier actor
    __actor = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://schemas.xmlsoap.org/soap/envelope/'), u'actor'), 'actor', '__urnoasisnamestcSAML2_0profilesSSOecp_RelayStateType_httpschemas_xmlsoap_orgsoapenvelopeactor', pyxb.binding.datatypes.anyURI, required=True)
    
    actor = property(__actor.value, __actor.set, None, None)


    _ElementMap = {
        
    }
    _AttributeMap = {
        __mustUnderstand.name() : __mustUnderstand,
        __actor.name() : __actor
    }
Namespace.addCategoryObject('typeBinding', u'RelayStateType', RelayStateType)


# Complex type ResponseType with content type EMPTY
class ResponseType (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_EMPTY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'ResponseType')
    # Base type is pyxb.binding.datatypes.anyType
    
    # Attribute {http://schemas.xmlsoap.org/soap/envelope/}mustUnderstand uses Python identifier mustUnderstand
    __mustUnderstand = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://schemas.xmlsoap.org/soap/envelope/'), u'mustUnderstand'), 'mustUnderstand', '__urnoasisnamestcSAML2_0profilesSSOecp_ResponseType_httpschemas_xmlsoap_orgsoapenvelopemustUnderstand', pyxb.bundles.wssplat.soap11.STD_ANON, required=True)
    
    mustUnderstand = property(__mustUnderstand.value, __mustUnderstand.set, None, None)

    
    # Attribute AssertionConsumerServiceURL uses Python identifier AssertionConsumerServiceURL
    __AssertionConsumerServiceURL = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'AssertionConsumerServiceURL'), 'AssertionConsumerServiceURL', '__urnoasisnamestcSAML2_0profilesSSOecp_ResponseType_AssertionConsumerServiceURL', pyxb.binding.datatypes.anyURI, required=True)
    
    AssertionConsumerServiceURL = property(__AssertionConsumerServiceURL.value, __AssertionConsumerServiceURL.set, None, None)

    
    # Attribute {http://schemas.xmlsoap.org/soap/envelope/}actor uses Python identifier actor
    __actor = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://schemas.xmlsoap.org/soap/envelope/'), u'actor'), 'actor', '__urnoasisnamestcSAML2_0profilesSSOecp_ResponseType_httpschemas_xmlsoap_orgsoapenvelopeactor', pyxb.binding.datatypes.anyURI, required=True)
    
    actor = property(__actor.value, __actor.set, None, None)


    _ElementMap = {
        
    }
    _AttributeMap = {
        __mustUnderstand.name() : __mustUnderstand,
        __AssertionConsumerServiceURL.name() : __AssertionConsumerServiceURL,
        __actor.name() : __actor
    }
Namespace.addCategoryObject('typeBinding', u'ResponseType', ResponseType)


Request = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Request'), RequestType)
Namespace.addCategoryObject('elementBinding', Request.name().localName(), Request)

RelayState = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'RelayState'), RelayStateType)
Namespace.addCategoryObject('elementBinding', RelayState.name().localName(), RelayState)

Response = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Response'), ResponseType)
Namespace.addCategoryObject('elementBinding', Response.name().localName(), Response)



RequestType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'urn:oasis:names:tc:SAML:2.0:protocol'), u'IDPList'), pyxb.bundles.saml20.protocol.IDPListType, scope=RequestType))

RequestType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'urn:oasis:names:tc:SAML:2.0:assertion'), u'Issuer'), pyxb.bundles.saml20.assertion.NameIDType, scope=RequestType))
RequestType._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(RequestType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'urn:oasis:names:tc:SAML:2.0:assertion'), u'Issuer')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(RequestType._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'urn:oasis:names:tc:SAML:2.0:protocol'), u'IDPList')), min_occurs=0L, max_occurs=1)
    )
RequestType._ContentModel = pyxb.binding.content.ParticleModel(RequestType._GroupModel, min_occurs=1, max_occurs=1)
