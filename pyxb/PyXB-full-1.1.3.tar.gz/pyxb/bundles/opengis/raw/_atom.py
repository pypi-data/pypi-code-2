# ./pyxb/bundles/opengis/raw/_atom.py
# PyXB bindings for NM:741a4e51acfa398449878d8690bb692b0b09b93a
# Generated 2011-09-09 14:18:59.939321 by PyXB version 1.1.3
# Namespace http://www.w3.org/2005/Atom [xmlns:atom]

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

Namespace = pyxb.namespace.NamespaceForURI(u'http://www.w3.org/2005/Atom', create_if_missing=True)
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
class atomEmailAddress (pyxb.binding.datatypes.string):

    """An atomic simple type."""

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'atomEmailAddress')
    _Documentation = None
atomEmailAddress._CF_pattern = pyxb.binding.facets.CF_pattern()
atomEmailAddress._CF_pattern.addPattern(pattern=u'.+@.+')
atomEmailAddress._InitializeFacetMap(atomEmailAddress._CF_pattern)
Namespace.addCategoryObject('typeBinding', u'atomEmailAddress', atomEmailAddress)

# Atomic SimpleTypeDefinition
class atomLanguageTag (pyxb.binding.datatypes.string):

    """An atomic simple type."""

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'atomLanguageTag')
    _Documentation = None
atomLanguageTag._CF_pattern = pyxb.binding.facets.CF_pattern()
atomLanguageTag._CF_pattern.addPattern(pattern=u'[A-Za-z]{1,8}(-[A-Za-z0-9]{1,8})*')
atomLanguageTag._InitializeFacetMap(atomLanguageTag._CF_pattern)
Namespace.addCategoryObject('typeBinding', u'atomLanguageTag', atomLanguageTag)

# Atomic SimpleTypeDefinition
class atomMediaType (pyxb.binding.datatypes.string):

    """An atomic simple type."""

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'atomMediaType')
    _Documentation = None
atomMediaType._CF_pattern = pyxb.binding.facets.CF_pattern()
atomMediaType._CF_pattern.addPattern(pattern=u'.+/.+')
atomMediaType._InitializeFacetMap(atomMediaType._CF_pattern)
Namespace.addCategoryObject('typeBinding', u'atomMediaType', atomMediaType)

# Complex type atomPersonConstruct with content type ELEMENT_ONLY
class atomPersonConstruct (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'atomPersonConstruct')
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {http://www.w3.org/2005/Atom}email uses Python identifier email
    __email = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'email'), 'email', '__httpwww_w3_org2005Atom_atomPersonConstruct_httpwww_w3_org2005Atomemail', True)

    
    email = property(__email.value, __email.set, None, None)

    
    # Element {http://www.w3.org/2005/Atom}uri uses Python identifier uri
    __uri = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'uri'), 'uri', '__httpwww_w3_org2005Atom_atomPersonConstruct_httpwww_w3_org2005Atomuri', True)

    
    uri = property(__uri.value, __uri.set, None, None)

    
    # Element {http://www.w3.org/2005/Atom}name uses Python identifier name
    __name = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'name'), 'name', '__httpwww_w3_org2005Atom_atomPersonConstruct_httpwww_w3_org2005Atomname', True)

    
    name = property(__name.value, __name.set, None, None)


    _ElementMap = {
        __email.name() : __email,
        __uri.name() : __uri,
        __name.name() : __name
    }
    _AttributeMap = {
        
    }
Namespace.addCategoryObject('typeBinding', u'atomPersonConstruct', atomPersonConstruct)


# Complex type CTD_ANON with content type EMPTY
class CTD_ANON (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_EMPTY
    _Abstract = False
    _ExpandedName = None
    # Base type is pyxb.binding.datatypes.anyType
    
    # Attribute hreflang uses Python identifier hreflang
    __hreflang = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'hreflang'), 'hreflang', '__httpwww_w3_org2005Atom_CTD_ANON_hreflang', atomLanguageTag)
    
    hreflang = property(__hreflang.value, __hreflang.set, None, None)

    
    # Attribute length uses Python identifier length
    __length = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'length'), 'length', '__httpwww_w3_org2005Atom_CTD_ANON_length', pyxb.binding.datatypes.anySimpleType)
    
    length = property(__length.value, __length.set, None, None)

    
    # Attribute title uses Python identifier title
    __title = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'title'), 'title', '__httpwww_w3_org2005Atom_CTD_ANON_title', pyxb.binding.datatypes.anySimpleType)
    
    title = property(__title.value, __title.set, None, None)

    
    # Attribute rel uses Python identifier rel
    __rel = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'rel'), 'rel', '__httpwww_w3_org2005Atom_CTD_ANON_rel', pyxb.binding.datatypes.anySimpleType)
    
    rel = property(__rel.value, __rel.set, None, None)

    
    # Attribute href uses Python identifier href
    __href = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'href'), 'href', '__httpwww_w3_org2005Atom_CTD_ANON_href', pyxb.binding.datatypes.anySimpleType, required=True)
    
    href = property(__href.value, __href.set, None, None)

    
    # Attribute type uses Python identifier type
    __type = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'type'), 'type', '__httpwww_w3_org2005Atom_CTD_ANON_type', atomMediaType)
    
    type = property(__type.value, __type.set, None, None)


    _ElementMap = {
        
    }
    _AttributeMap = {
        __hreflang.name() : __hreflang,
        __length.name() : __length,
        __title.name() : __title,
        __rel.name() : __rel,
        __href.name() : __href,
        __type.name() : __type
    }



author = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'author'), atomPersonConstruct)
Namespace.addCategoryObject('elementBinding', author.name().localName(), author)

link = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'link'), CTD_ANON)
Namespace.addCategoryObject('elementBinding', link.name().localName(), link)

name = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'name'), pyxb.binding.datatypes.string)
Namespace.addCategoryObject('elementBinding', name.name().localName(), name)

uri = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'uri'), pyxb.binding.datatypes.string)
Namespace.addCategoryObject('elementBinding', uri.name().localName(), uri)

email = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'email'), atomEmailAddress)
Namespace.addCategoryObject('elementBinding', email.name().localName(), email)



atomPersonConstruct._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'email'), atomEmailAddress, scope=atomPersonConstruct))

atomPersonConstruct._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'uri'), pyxb.binding.datatypes.string, scope=atomPersonConstruct))

atomPersonConstruct._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'name'), pyxb.binding.datatypes.string, scope=atomPersonConstruct))
atomPersonConstruct._GroupModel = pyxb.binding.content.GroupChoice(
    pyxb.binding.content.ParticleModel(atomPersonConstruct._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'name')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(atomPersonConstruct._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'uri')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(atomPersonConstruct._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'email')), min_occurs=1, max_occurs=1)
    )
atomPersonConstruct._ContentModel = pyxb.binding.content.ParticleModel(atomPersonConstruct._GroupModel, min_occurs=0L, max_occurs=None)
