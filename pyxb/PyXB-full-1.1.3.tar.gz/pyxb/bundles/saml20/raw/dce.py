# ./pyxb/bundles/saml20/raw/dce.py
# PyXB bindings for NM:f6fa0461f265c04a0bd0017089ca6057a2aade76
# Generated 2011-09-09 14:19:36.754479 by PyXB version 1.1.3
# Namespace urn:oasis:names:tc:SAML:2.0:profiles:attribute:DCE

import pyxb
import pyxb.binding
import pyxb.binding.saxer
import StringIO
import pyxb.utils.utility
import pyxb.utils.domutils
import sys

# Unique identifier for bindings created at the same time
_GenerationUID = pyxb.utils.utility.UniqueIdentifier('urn:uuid:a81ea072-db18-11e0-a7df-001fbc013adc')

# Import bindings for namespaces imported into schema
import pyxb.binding.datatypes

Namespace = pyxb.namespace.NamespaceForURI(u'urn:oasis:names:tc:SAML:2.0:profiles:attribute:DCE', create_if_missing=True)
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


# Complex type DCEValueType with content type SIMPLE
class DCEValueType (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = pyxb.binding.datatypes.anyURI
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_SIMPLE
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'DCEValueType')
    # Base type is pyxb.binding.datatypes.anyURI
    
    # Attribute {urn:oasis:names:tc:SAML:2.0:profiles:attribute:DCE}FriendlyName uses Python identifier FriendlyName
    __FriendlyName = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(Namespace, u'FriendlyName'), 'FriendlyName', '__urnoasisnamestcSAML2_0profilesattributeDCE_DCEValueType_urnoasisnamestcSAML2_0profilesattributeDCEFriendlyName', pyxb.binding.datatypes.string)
    
    FriendlyName = property(__FriendlyName.value, __FriendlyName.set, None, None)

    
    # Attribute {urn:oasis:names:tc:SAML:2.0:profiles:attribute:DCE}Realm uses Python identifier Realm
    __Realm = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(Namespace, u'Realm'), 'Realm', '__urnoasisnamestcSAML2_0profilesattributeDCE_DCEValueType_urnoasisnamestcSAML2_0profilesattributeDCERealm', pyxb.binding.datatypes.anyURI)
    
    Realm = property(__Realm.value, __Realm.set, None, None)


    _ElementMap = {
        
    }
    _AttributeMap = {
        __FriendlyName.name() : __FriendlyName,
        __Realm.name() : __Realm
    }
Namespace.addCategoryObject('typeBinding', u'DCEValueType', DCEValueType)

