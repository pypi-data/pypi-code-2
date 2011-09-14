# ./pyxb/bundles/common/raw/xsd_hfp.py
# PyXB bindings for NM:c53ce1768a4a63294762e2dee968b656ae0d44d0
# Generated 2011-09-09 14:09:01.769270 by PyXB version 1.1.3
# Namespace http://www.w3.org/2001/XMLSchema-hasFacetAndProperty

import pyxb
import pyxb.binding
import pyxb.binding.saxer
import StringIO
import pyxb.utils.utility
import pyxb.utils.domutils
import sys

# Unique identifier for bindings created at the same time
_GenerationUID = pyxb.utils.utility.UniqueIdentifier('urn:uuid:2da1d3d8-db17-11e0-b761-001fbc013adc')

# Import bindings for namespaces imported into schema
import pyxb.binding.datatypes

Namespace = pyxb.namespace.NamespaceForURI('http://www.w3.org/2001/XMLSchema-hasFacetAndProperty', create_if_missing=True)
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
class STD_ANON (pyxb.binding.datatypes.NMTOKEN, pyxb.binding.basis.enumeration_mixin):

    """
       
       
      """

    _ExpandedName = None
    _Documentation = u'\n       \n       \n      '
STD_ANON._CF_enumeration = pyxb.binding.facets.CF_enumeration(value_datatype=STD_ANON, enum_prefix=None)
STD_ANON.ordered = STD_ANON._CF_enumeration.addEnumeration(unicode_value=u'ordered', tag=u'ordered')
STD_ANON.bounded = STD_ANON._CF_enumeration.addEnumeration(unicode_value=u'bounded', tag=u'bounded')
STD_ANON.cardinality = STD_ANON._CF_enumeration.addEnumeration(unicode_value=u'cardinality', tag=u'cardinality')
STD_ANON.numeric = STD_ANON._CF_enumeration.addEnumeration(unicode_value=u'numeric', tag=u'numeric')
STD_ANON._InitializeFacetMap(STD_ANON._CF_enumeration)

# Atomic SimpleTypeDefinition
class STD_ANON_ (pyxb.binding.datatypes.NMTOKEN, pyxb.binding.basis.enumeration_mixin):

    """
       
       
      """

    _ExpandedName = None
    _Documentation = u'\n       \n       \n      '
STD_ANON_._CF_enumeration = pyxb.binding.facets.CF_enumeration(value_datatype=STD_ANON_, enum_prefix=None)
STD_ANON_.length = STD_ANON_._CF_enumeration.addEnumeration(unicode_value=u'length', tag=u'length')
STD_ANON_.minLength = STD_ANON_._CF_enumeration.addEnumeration(unicode_value=u'minLength', tag=u'minLength')
STD_ANON_.maxLength = STD_ANON_._CF_enumeration.addEnumeration(unicode_value=u'maxLength', tag=u'maxLength')
STD_ANON_.pattern = STD_ANON_._CF_enumeration.addEnumeration(unicode_value=u'pattern', tag=u'pattern')
STD_ANON_.enumeration = STD_ANON_._CF_enumeration.addEnumeration(unicode_value=u'enumeration', tag=u'enumeration')
STD_ANON_.maxInclusive = STD_ANON_._CF_enumeration.addEnumeration(unicode_value=u'maxInclusive', tag=u'maxInclusive')
STD_ANON_.maxExclusive = STD_ANON_._CF_enumeration.addEnumeration(unicode_value=u'maxExclusive', tag=u'maxExclusive')
STD_ANON_.minInclusive = STD_ANON_._CF_enumeration.addEnumeration(unicode_value=u'minInclusive', tag=u'minInclusive')
STD_ANON_.minExclusive = STD_ANON_._CF_enumeration.addEnumeration(unicode_value=u'minExclusive', tag=u'minExclusive')
STD_ANON_.totalDigits = STD_ANON_._CF_enumeration.addEnumeration(unicode_value=u'totalDigits', tag=u'totalDigits')
STD_ANON_.fractionDigits = STD_ANON_._CF_enumeration.addEnumeration(unicode_value=u'fractionDigits', tag=u'fractionDigits')
STD_ANON_.whiteSpace = STD_ANON_._CF_enumeration.addEnumeration(unicode_value=u'whiteSpace', tag=u'whiteSpace')
STD_ANON_.maxScale = STD_ANON_._CF_enumeration.addEnumeration(unicode_value=u'maxScale', tag=u'maxScale')
STD_ANON_.minScale = STD_ANON_._CF_enumeration.addEnumeration(unicode_value=u'minScale', tag=u'minScale')
STD_ANON_._InitializeFacetMap(STD_ANON_._CF_enumeration)

# Complex type CTD_ANON with content type EMPTY
class CTD_ANON (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_EMPTY
    _Abstract = False
    _ExpandedName = None
    # Base type is pyxb.binding.datatypes.anyType
    
    # Attribute name uses Python identifier name
    __name = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'name'), 'name', '__httpwww_w3_org2001XMLSchema_hasFacetAndProperty_CTD_ANON_name', STD_ANON, required=True)
    
    name = property(__name.value, __name.set, None, None)

    
    # Attribute value uses Python identifier value_
    __value = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'value'), 'value_', '__httpwww_w3_org2001XMLSchema_hasFacetAndProperty_CTD_ANON_value', pyxb.binding.datatypes.normalizedString, required=True)
    
    value_ = property(__value.value, __value.set, None, None)


    _ElementMap = {
        
    }
    _AttributeMap = {
        __name.name() : __name,
        __value.name() : __value
    }



# Complex type CTD_ANON_ with content type EMPTY
class CTD_ANON_ (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_EMPTY
    _Abstract = False
    _ExpandedName = None
    # Base type is pyxb.binding.datatypes.anyType
    
    # Attribute name uses Python identifier name
    __name = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'name'), 'name', '__httpwww_w3_org2001XMLSchema_hasFacetAndProperty_CTD_ANON__name', STD_ANON_, required=True)
    
    name = property(__name.value, __name.set, None, None)


    _ElementMap = {
        
    }
    _AttributeMap = {
        __name.name() : __name
    }



hasProperty = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'hasProperty'), CTD_ANON, documentation=u'\n    \n    \n    \n   ')
Namespace.addCategoryObject('elementBinding', hasProperty.name().localName(), hasProperty)

hasFacet = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'hasFacet'), CTD_ANON_, documentation=u'\n   \n   \n   \n   ')
Namespace.addCategoryObject('elementBinding', hasFacet.name().localName(), hasFacet)
