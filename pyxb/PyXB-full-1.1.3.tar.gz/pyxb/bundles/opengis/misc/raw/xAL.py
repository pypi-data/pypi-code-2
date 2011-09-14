# ./pyxb/bundles/opengis/misc/raw/xAL.py
# PyXB bindings for NM:28237b706ea7dd7f30e1bac6f6949d1f2f8264f7
# Generated 2011-09-09 14:18:36.303094 by PyXB version 1.1.3
# Namespace urn:oasis:names:tc:ciq:xsdschema:xAL:2.0

import pyxb
import pyxb.binding
import pyxb.binding.saxer
import StringIO
import pyxb.utils.utility
import pyxb.utils.domutils
import sys

# Unique identifier for bindings created at the same time
_GenerationUID = pyxb.utils.utility.UniqueIdentifier('urn:uuid:83dc9df4-db18-11e0-b61d-001fbc013adc')

# Import bindings for namespaces imported into schema
import pyxb.binding.datatypes

Namespace = pyxb.namespace.NamespaceForURI(u'urn:oasis:names:tc:ciq:xsdschema:xAL:2.0', create_if_missing=True)
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

    """An atomic simple type."""

    _ExpandedName = None
    _Documentation = None
STD_ANON._CF_enumeration = pyxb.binding.facets.CF_enumeration(value_datatype=STD_ANON, enum_prefix=None)
STD_ANON.Before = STD_ANON._CF_enumeration.addEnumeration(unicode_value=u'Before', tag=u'Before')
STD_ANON.After = STD_ANON._CF_enumeration.addEnumeration(unicode_value=u'After', tag=u'After')
STD_ANON._InitializeFacetMap(STD_ANON._CF_enumeration)

# Atomic SimpleTypeDefinition
class STD_ANON_ (pyxb.binding.datatypes.NMTOKEN, pyxb.binding.basis.enumeration_mixin):

    """An atomic simple type."""

    _ExpandedName = None
    _Documentation = None
STD_ANON_._CF_enumeration = pyxb.binding.facets.CF_enumeration(value_datatype=STD_ANON_, enum_prefix=None)
STD_ANON_.Before = STD_ANON_._CF_enumeration.addEnumeration(unicode_value=u'Before', tag=u'Before')
STD_ANON_.After = STD_ANON_._CF_enumeration.addEnumeration(unicode_value=u'After', tag=u'After')
STD_ANON_._InitializeFacetMap(STD_ANON_._CF_enumeration)

# Atomic SimpleTypeDefinition
class STD_ANON_2 (pyxb.binding.datatypes.NMTOKEN, pyxb.binding.basis.enumeration_mixin):

    """An atomic simple type."""

    _ExpandedName = None
    _Documentation = None
STD_ANON_2._CF_enumeration = pyxb.binding.facets.CF_enumeration(value_datatype=STD_ANON_2, enum_prefix=None)
STD_ANON_2.Before = STD_ANON_2._CF_enumeration.addEnumeration(unicode_value=u'Before', tag=u'Before')
STD_ANON_2.After = STD_ANON_2._CF_enumeration.addEnumeration(unicode_value=u'After', tag=u'After')
STD_ANON_2._InitializeFacetMap(STD_ANON_2._CF_enumeration)

# Atomic SimpleTypeDefinition
class STD_ANON_3 (pyxb.binding.datatypes.NMTOKEN, pyxb.binding.basis.enumeration_mixin):

    """An atomic simple type."""

    _ExpandedName = None
    _Documentation = None
STD_ANON_3._CF_enumeration = pyxb.binding.facets.CF_enumeration(value_datatype=STD_ANON_3, enum_prefix=None)
STD_ANON_3.Yes = STD_ANON_3._CF_enumeration.addEnumeration(unicode_value=u'Yes', tag=u'Yes')
STD_ANON_3.No = STD_ANON_3._CF_enumeration.addEnumeration(unicode_value=u'No', tag=u'No')
STD_ANON_3._InitializeFacetMap(STD_ANON_3._CF_enumeration)

# Atomic SimpleTypeDefinition
class STD_ANON_4 (pyxb.binding.datatypes.NMTOKEN, pyxb.binding.basis.enumeration_mixin):

    """An atomic simple type."""

    _ExpandedName = None
    _Documentation = None
STD_ANON_4._CF_enumeration = pyxb.binding.facets.CF_enumeration(value_datatype=STD_ANON_4, enum_prefix=None)
STD_ANON_4.Before = STD_ANON_4._CF_enumeration.addEnumeration(unicode_value=u'Before', tag=u'Before')
STD_ANON_4.After = STD_ANON_4._CF_enumeration.addEnumeration(unicode_value=u'After', tag=u'After')
STD_ANON_4._InitializeFacetMap(STD_ANON_4._CF_enumeration)

# Atomic SimpleTypeDefinition
class STD_ANON_5 (pyxb.binding.datatypes.NMTOKEN, pyxb.binding.basis.enumeration_mixin):

    """An atomic simple type."""

    _ExpandedName = None
    _Documentation = None
STD_ANON_5._CF_enumeration = pyxb.binding.facets.CF_enumeration(value_datatype=STD_ANON_5, enum_prefix=None)
STD_ANON_5.Before = STD_ANON_5._CF_enumeration.addEnumeration(unicode_value=u'Before', tag=u'Before')
STD_ANON_5.After = STD_ANON_5._CF_enumeration.addEnumeration(unicode_value=u'After', tag=u'After')
STD_ANON_5._InitializeFacetMap(STD_ANON_5._CF_enumeration)

# Atomic SimpleTypeDefinition
class STD_ANON_6 (pyxb.binding.datatypes.NMTOKEN, pyxb.binding.basis.enumeration_mixin):

    """An atomic simple type."""

    _ExpandedName = None
    _Documentation = None
STD_ANON_6._CF_enumeration = pyxb.binding.facets.CF_enumeration(value_datatype=STD_ANON_6, enum_prefix=None)
STD_ANON_6.Single = STD_ANON_6._CF_enumeration.addEnumeration(unicode_value=u'Single', tag=u'Single')
STD_ANON_6.Range = STD_ANON_6._CF_enumeration.addEnumeration(unicode_value=u'Range', tag=u'Range')
STD_ANON_6._InitializeFacetMap(STD_ANON_6._CF_enumeration)

# Atomic SimpleTypeDefinition
class STD_ANON_7 (pyxb.binding.datatypes.NMTOKEN, pyxb.binding.basis.enumeration_mixin):

    """An atomic simple type."""

    _ExpandedName = None
    _Documentation = None
STD_ANON_7._CF_enumeration = pyxb.binding.facets.CF_enumeration(value_datatype=STD_ANON_7, enum_prefix=None)
STD_ANON_7.BeforeName = STD_ANON_7._CF_enumeration.addEnumeration(unicode_value=u'BeforeName', tag=u'BeforeName')
STD_ANON_7.AfterName = STD_ANON_7._CF_enumeration.addEnumeration(unicode_value=u'AfterName', tag=u'AfterName')
STD_ANON_7.BeforeType = STD_ANON_7._CF_enumeration.addEnumeration(unicode_value=u'BeforeType', tag=u'BeforeType')
STD_ANON_7.AfterType = STD_ANON_7._CF_enumeration.addEnumeration(unicode_value=u'AfterType', tag=u'AfterType')
STD_ANON_7._InitializeFacetMap(STD_ANON_7._CF_enumeration)

# Atomic SimpleTypeDefinition
class STD_ANON_8 (pyxb.binding.datatypes.NMTOKEN, pyxb.binding.basis.enumeration_mixin):

    """An atomic simple type."""

    _ExpandedName = None
    _Documentation = None
STD_ANON_8._CF_enumeration = pyxb.binding.facets.CF_enumeration(value_datatype=STD_ANON_8, enum_prefix=None)
STD_ANON_8.Before = STD_ANON_8._CF_enumeration.addEnumeration(unicode_value=u'Before', tag=u'Before')
STD_ANON_8.After = STD_ANON_8._CF_enumeration.addEnumeration(unicode_value=u'After', tag=u'After')
STD_ANON_8._InitializeFacetMap(STD_ANON_8._CF_enumeration)

# Atomic SimpleTypeDefinition
class STD_ANON_9 (pyxb.binding.datatypes.NMTOKEN, pyxb.binding.basis.enumeration_mixin):

    """An atomic simple type."""

    _ExpandedName = None
    _Documentation = None
STD_ANON_9._CF_enumeration = pyxb.binding.facets.CF_enumeration(value_datatype=STD_ANON_9, enum_prefix=None)
STD_ANON_9.Before = STD_ANON_9._CF_enumeration.addEnumeration(unicode_value=u'Before', tag=u'Before')
STD_ANON_9.After = STD_ANON_9._CF_enumeration.addEnumeration(unicode_value=u'After', tag=u'After')
STD_ANON_9._InitializeFacetMap(STD_ANON_9._CF_enumeration)

# Atomic SimpleTypeDefinition
class STD_ANON_10 (pyxb.binding.datatypes.NMTOKEN, pyxb.binding.basis.enumeration_mixin):

    """An atomic simple type."""

    _ExpandedName = None
    _Documentation = None
STD_ANON_10._CF_enumeration = pyxb.binding.facets.CF_enumeration(value_datatype=STD_ANON_10, enum_prefix=None)
STD_ANON_10.BeforeName = STD_ANON_10._CF_enumeration.addEnumeration(unicode_value=u'BeforeName', tag=u'BeforeName')
STD_ANON_10.AfterName = STD_ANON_10._CF_enumeration.addEnumeration(unicode_value=u'AfterName', tag=u'AfterName')
STD_ANON_10.BeforeType = STD_ANON_10._CF_enumeration.addEnumeration(unicode_value=u'BeforeType', tag=u'BeforeType')
STD_ANON_10.AfterType = STD_ANON_10._CF_enumeration.addEnumeration(unicode_value=u'AfterType', tag=u'AfterType')
STD_ANON_10._InitializeFacetMap(STD_ANON_10._CF_enumeration)

# Atomic SimpleTypeDefinition
class STD_ANON_11 (pyxb.binding.datatypes.NMTOKEN, pyxb.binding.basis.enumeration_mixin):

    """An atomic simple type."""

    _ExpandedName = None
    _Documentation = None
STD_ANON_11._CF_enumeration = pyxb.binding.facets.CF_enumeration(value_datatype=STD_ANON_11, enum_prefix=None)
STD_ANON_11.Single = STD_ANON_11._CF_enumeration.addEnumeration(unicode_value=u'Single', tag=u'Single')
STD_ANON_11.Range = STD_ANON_11._CF_enumeration.addEnumeration(unicode_value=u'Range', tag=u'Range')
STD_ANON_11._InitializeFacetMap(STD_ANON_11._CF_enumeration)

# Atomic SimpleTypeDefinition
class STD_ANON_12 (pyxb.binding.datatypes.NMTOKEN, pyxb.binding.basis.enumeration_mixin):

    """An atomic simple type."""

    _ExpandedName = None
    _Documentation = None
STD_ANON_12._CF_enumeration = pyxb.binding.facets.CF_enumeration(value_datatype=STD_ANON_12, enum_prefix=None)
STD_ANON_12.Before = STD_ANON_12._CF_enumeration.addEnumeration(unicode_value=u'Before', tag=u'Before')
STD_ANON_12.After = STD_ANON_12._CF_enumeration.addEnumeration(unicode_value=u'After', tag=u'After')
STD_ANON_12._InitializeFacetMap(STD_ANON_12._CF_enumeration)

# Atomic SimpleTypeDefinition
class STD_ANON_13 (pyxb.binding.datatypes.NMTOKEN, pyxb.binding.basis.enumeration_mixin):

    """An atomic simple type."""

    _ExpandedName = None
    _Documentation = None
STD_ANON_13._CF_enumeration = pyxb.binding.facets.CF_enumeration(value_datatype=STD_ANON_13, enum_prefix=None)
STD_ANON_13.Before = STD_ANON_13._CF_enumeration.addEnumeration(unicode_value=u'Before', tag=u'Before')
STD_ANON_13.After = STD_ANON_13._CF_enumeration.addEnumeration(unicode_value=u'After', tag=u'After')
STD_ANON_13._InitializeFacetMap(STD_ANON_13._CF_enumeration)

# Atomic SimpleTypeDefinition
class STD_ANON_14 (pyxb.binding.datatypes.NMTOKEN, pyxb.binding.basis.enumeration_mixin):

    """An atomic simple type."""

    _ExpandedName = None
    _Documentation = None
STD_ANON_14._CF_enumeration = pyxb.binding.facets.CF_enumeration(value_datatype=STD_ANON_14, enum_prefix=None)
STD_ANON_14.Before = STD_ANON_14._CF_enumeration.addEnumeration(unicode_value=u'Before', tag=u'Before')
STD_ANON_14.After = STD_ANON_14._CF_enumeration.addEnumeration(unicode_value=u'After', tag=u'After')
STD_ANON_14._InitializeFacetMap(STD_ANON_14._CF_enumeration)

# Atomic SimpleTypeDefinition
class STD_ANON_15 (pyxb.binding.datatypes.NMTOKEN, pyxb.binding.basis.enumeration_mixin):

    """An atomic simple type."""

    _ExpandedName = None
    _Documentation = None
STD_ANON_15._CF_enumeration = pyxb.binding.facets.CF_enumeration(value_datatype=STD_ANON_15, enum_prefix=None)
STD_ANON_15.Before = STD_ANON_15._CF_enumeration.addEnumeration(unicode_value=u'Before', tag=u'Before')
STD_ANON_15.After = STD_ANON_15._CF_enumeration.addEnumeration(unicode_value=u'After', tag=u'After')
STD_ANON_15._InitializeFacetMap(STD_ANON_15._CF_enumeration)

# Atomic SimpleTypeDefinition
class STD_ANON_16 (pyxb.binding.datatypes.NMTOKEN, pyxb.binding.basis.enumeration_mixin):

    """An atomic simple type."""

    _ExpandedName = None
    _Documentation = None
STD_ANON_16._CF_enumeration = pyxb.binding.facets.CF_enumeration(value_datatype=STD_ANON_16, enum_prefix=None)
STD_ANON_16.Before = STD_ANON_16._CF_enumeration.addEnumeration(unicode_value=u'Before', tag=u'Before')
STD_ANON_16.After = STD_ANON_16._CF_enumeration.addEnumeration(unicode_value=u'After', tag=u'After')
STD_ANON_16._InitializeFacetMap(STD_ANON_16._CF_enumeration)

# Atomic SimpleTypeDefinition
class STD_ANON_17 (pyxb.binding.datatypes.NMTOKEN, pyxb.binding.basis.enumeration_mixin):

    """An atomic simple type."""

    _ExpandedName = None
    _Documentation = None
STD_ANON_17._CF_enumeration = pyxb.binding.facets.CF_enumeration(value_datatype=STD_ANON_17, enum_prefix=None)
STD_ANON_17.Odd = STD_ANON_17._CF_enumeration.addEnumeration(unicode_value=u'Odd', tag=u'Odd')
STD_ANON_17.Even = STD_ANON_17._CF_enumeration.addEnumeration(unicode_value=u'Even', tag=u'Even')
STD_ANON_17._InitializeFacetMap(STD_ANON_17._CF_enumeration)

# Atomic SimpleTypeDefinition
class STD_ANON_18 (pyxb.binding.datatypes.NMTOKEN, pyxb.binding.basis.enumeration_mixin):

    """An atomic simple type."""

    _ExpandedName = None
    _Documentation = None
STD_ANON_18._CF_enumeration = pyxb.binding.facets.CF_enumeration(value_datatype=STD_ANON_18, enum_prefix=None)
STD_ANON_18.BeforeName = STD_ANON_18._CF_enumeration.addEnumeration(unicode_value=u'BeforeName', tag=u'BeforeName')
STD_ANON_18.AfterName = STD_ANON_18._CF_enumeration.addEnumeration(unicode_value=u'AfterName', tag=u'AfterName')
STD_ANON_18.BeforeType = STD_ANON_18._CF_enumeration.addEnumeration(unicode_value=u'BeforeType', tag=u'BeforeType')
STD_ANON_18.AfterType = STD_ANON_18._CF_enumeration.addEnumeration(unicode_value=u'AfterType', tag=u'AfterType')
STD_ANON_18._InitializeFacetMap(STD_ANON_18._CF_enumeration)

# Complex type PostalRouteType with content type ELEMENT_ONLY
class PostalRouteType (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'PostalRouteType')
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}AddressLine uses Python identifier AddressLine
    __AddressLine = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'AddressLine'), 'AddressLine', '__urnoasisnamestcciqxsdschemaxAL2_0_PostalRouteType_urnoasisnamestcciqxsdschemaxAL2_0AddressLine', True)

    
    AddressLine = property(__AddressLine.value, __AddressLine.set, None, u'Free format address representation. An address can have more than one line. The order of the AddressLine elements must be preserved.')

    
    # Element {urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}PostalRouteName uses Python identifier PostalRouteName
    __PostalRouteName = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'PostalRouteName'), 'PostalRouteName', '__urnoasisnamestcciqxsdschemaxAL2_0_PostalRouteType_urnoasisnamestcciqxsdschemaxAL2_0PostalRouteName', True)

    
    PostalRouteName = property(__PostalRouteName.value, __PostalRouteName.set, None, u' Name of the Postal Route')

    
    # Element {urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}PostalRouteNumber uses Python identifier PostalRouteNumber
    __PostalRouteNumber = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'PostalRouteNumber'), 'PostalRouteNumber', '__urnoasisnamestcciqxsdschemaxAL2_0_PostalRouteType_urnoasisnamestcciqxsdschemaxAL2_0PostalRouteNumber', False)

    
    PostalRouteNumber = property(__PostalRouteNumber.value, __PostalRouteNumber.set, None, u' Number of the Postal Route')

    
    # Element {urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}PostBox uses Python identifier PostBox
    __PostBox = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'PostBox'), 'PostBox', '__urnoasisnamestcciqxsdschemaxAL2_0_PostalRouteType_urnoasisnamestcciqxsdschemaxAL2_0PostBox', False)

    
    PostBox = property(__PostBox.value, __PostBox.set, None, u'Specification of a postbox like mail delivery point. Only a single postbox number can be specified. Examples of postboxes are POBox, free mail numbers, etc.')

    
    # Attribute Type uses Python identifier Type
    __Type = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Type'), 'Type', '__urnoasisnamestcciqxsdschemaxAL2_0_PostalRouteType_Type', pyxb.binding.datatypes.anySimpleType)
    
    Type = property(__Type.value, __Type.set, None, None)

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_strict, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'urn:oasis:names:tc:ciq:xsdschema:xAL:2.0'))
    _HasWildcardElement = True

    _ElementMap = {
        __AddressLine.name() : __AddressLine,
        __PostalRouteName.name() : __PostalRouteName,
        __PostalRouteNumber.name() : __PostalRouteNumber,
        __PostBox.name() : __PostBox
    }
    _AttributeMap = {
        __Type.name() : __Type
    }
Namespace.addCategoryObject('typeBinding', u'PostalRouteType', PostalRouteType)


# Complex type CTD_ANON with content type MIXED
class CTD_ANON (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_MIXED
    _Abstract = False
    _ExpandedName = None
    # Base type is pyxb.binding.datatypes.anyType
    
    # Attribute Code uses Python identifier Code
    __Code = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Code'), 'Code', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_Code', pyxb.binding.datatypes.anySimpleType)
    
    Code = property(__Code.value, __Code.set, None, u'Used by postal services to encode the name of the element.')

    
    # Attribute Type uses Python identifier Type
    __Type = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Type'), 'Type', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_Type', pyxb.binding.datatypes.anySimpleType)
    
    Type = property(__Type.value, __Type.set, None, u'Defines the type of address line. eg. Street, Address Line 1, etc.')

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_strict, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'urn:oasis:names:tc:ciq:xsdschema:xAL:2.0'))

    _ElementMap = {
        
    }
    _AttributeMap = {
        __Code.name() : __Code,
        __Type.name() : __Type
    }



# Complex type DependentLocalityType with content type ELEMENT_ONLY
class DependentLocalityType (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'DependentLocalityType')
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}DependentLocalityName uses Python identifier DependentLocalityName
    __DependentLocalityName = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'DependentLocalityName'), 'DependentLocalityName', '__urnoasisnamestcciqxsdschemaxAL2_0_DependentLocalityType_urnoasisnamestcciqxsdschemaxAL2_0DependentLocalityName', True)

    
    DependentLocalityName = property(__DependentLocalityName.value, __DependentLocalityName.set, None, u'Name of the dependent locality')

    
    # Element {urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}Thoroughfare uses Python identifier Thoroughfare
    __Thoroughfare = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'Thoroughfare'), 'Thoroughfare', '__urnoasisnamestcciqxsdschemaxAL2_0_DependentLocalityType_urnoasisnamestcciqxsdschemaxAL2_0Thoroughfare', False)

    
    Thoroughfare = property(__Thoroughfare.value, __Thoroughfare.set, None, u'Specification of a thoroughfare. A thoroughfare could be a rd, street, canal, river, etc.  Note dependentlocality in a street. For example, in some countries, a large street will \nhave many subdivisions with numbers. Normally the subdivision name is the same as the road name, but with a number to identifiy it. Eg. SOI SUKUMVIT 3, SUKUMVIT RD, BANGKOK')

    
    # Element {urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}PostalRoute uses Python identifier PostalRoute
    __PostalRoute = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'PostalRoute'), 'PostalRoute', '__urnoasisnamestcciqxsdschemaxAL2_0_DependentLocalityType_urnoasisnamestcciqxsdschemaxAL2_0PostalRoute', False)

    
    PostalRoute = property(__PostalRoute.value, __PostalRoute.set, None, u' A Postal van is specific for a route as in Is`rael, Rural route')

    
    # Element {urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}PostalCode uses Python identifier PostalCode
    __PostalCode = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'PostalCode'), 'PostalCode', '__urnoasisnamestcciqxsdschemaxAL2_0_DependentLocalityType_urnoasisnamestcciqxsdschemaxAL2_0PostalCode', False)

    
    PostalCode = property(__PostalCode.value, __PostalCode.set, None, u'PostalCode is the container element for either simple or complex (extended) postal codes. Type: Area Code, Postcode, etc.')

    
    # Element {urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}DependentLocality uses Python identifier DependentLocality
    __DependentLocality = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'DependentLocality'), 'DependentLocality', '__urnoasisnamestcciqxsdschemaxAL2_0_DependentLocalityType_urnoasisnamestcciqxsdschemaxAL2_0DependentLocality', False)

    
    DependentLocality = property(__DependentLocality.value, __DependentLocality.set, None, u'Dependent localities are Districts within cities/towns, locality divisions, postal \ndivisions of cities, suburbs, etc. DependentLocality is a recursive element, but no nesting deeper than two exists (Locality-DependentLocality-DependentLocality).')

    
    # Element {urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}Premise uses Python identifier Premise
    __Premise = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'Premise'), 'Premise', '__urnoasisnamestcciqxsdschemaxAL2_0_DependentLocalityType_urnoasisnamestcciqxsdschemaxAL2_0Premise', False)

    
    Premise = property(__Premise.value, __Premise.set, None, u'Specification of a single premise, for example a house or a building. The premise as a whole has a unique premise (house) number or a premise name.  There could be more than \none premise in a street referenced in an address. For example a building address near a major shopping centre or raiwlay station')

    
    # Element {urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}DependentLocalityNumber uses Python identifier DependentLocalityNumber
    __DependentLocalityNumber = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'DependentLocalityNumber'), 'DependentLocalityNumber', '__urnoasisnamestcciqxsdschemaxAL2_0_DependentLocalityType_urnoasisnamestcciqxsdschemaxAL2_0DependentLocalityNumber', False)

    
    DependentLocalityNumber = property(__DependentLocalityNumber.value, __DependentLocalityNumber.set, None, u'Number of the dependent locality. Some areas are numbered. Eg. SECTOR 5 in a Suburb as in India or SOI SUKUMVIT 10 as in Thailand')

    
    # Element {urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}PostOffice uses Python identifier PostOffice
    __PostOffice = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'PostOffice'), 'PostOffice', '__urnoasisnamestcciqxsdschemaxAL2_0_DependentLocalityType_urnoasisnamestcciqxsdschemaxAL2_0PostOffice', False)

    
    PostOffice = property(__PostOffice.value, __PostOffice.set, None, u'Specification of a post office. Examples are a rural post office where post is delivered and a post office containing post office boxes.')

    
    # Element {urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}AddressLine uses Python identifier AddressLine
    __AddressLine = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'AddressLine'), 'AddressLine', '__urnoasisnamestcciqxsdschemaxAL2_0_DependentLocalityType_urnoasisnamestcciqxsdschemaxAL2_0AddressLine', True)

    
    AddressLine = property(__AddressLine.value, __AddressLine.set, None, u'Free format address representation. An address can have more than one line. The order of the AddressLine elements must be preserved.')

    
    # Element {urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}LargeMailUser uses Python identifier LargeMailUser
    __LargeMailUser = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'LargeMailUser'), 'LargeMailUser', '__urnoasisnamestcciqxsdschemaxAL2_0_DependentLocalityType_urnoasisnamestcciqxsdschemaxAL2_0LargeMailUser', False)

    
    LargeMailUser = property(__LargeMailUser.value, __LargeMailUser.set, None, u'Specification of a large mail user address. Examples of large mail users are postal companies, companies in France with a cedex number, hospitals and airports with their own post code. Large mail user addresses do not have a street name with premise name or premise number in countries like Netherlands. But they have a POBox and street also in countries like France')

    
    # Element {urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}PostBox uses Python identifier PostBox
    __PostBox = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'PostBox'), 'PostBox', '__urnoasisnamestcciqxsdschemaxAL2_0_DependentLocalityType_urnoasisnamestcciqxsdschemaxAL2_0PostBox', False)

    
    PostBox = property(__PostBox.value, __PostBox.set, None, u'Specification of a postbox like mail delivery point. Only a single postbox number can be specified. Examples of postboxes are POBox, free mail numbers, etc.')

    
    # Attribute Connector uses Python identifier Connector
    __Connector = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Connector'), 'Connector', '__urnoasisnamestcciqxsdschemaxAL2_0_DependentLocalityType_Connector', pyxb.binding.datatypes.anySimpleType)
    
    Connector = property(__Connector.value, __Connector.set, None, u'"VIA" as in Hill Top VIA Parish where Parish is a locality and Hill Top is a dependent locality')

    
    # Attribute UsageType uses Python identifier UsageType
    __UsageType = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'UsageType'), 'UsageType', '__urnoasisnamestcciqxsdschemaxAL2_0_DependentLocalityType_UsageType', pyxb.binding.datatypes.anySimpleType)
    
    UsageType = property(__UsageType.value, __UsageType.set, None, u'Postal or Political - Sometimes locations must be distinguished between postal system, and physical locations as defined by a political system')

    
    # Attribute Type uses Python identifier Type
    __Type = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Type'), 'Type', '__urnoasisnamestcciqxsdschemaxAL2_0_DependentLocalityType_Type', pyxb.binding.datatypes.anySimpleType)
    
    Type = property(__Type.value, __Type.set, None, u'City or IndustrialEstate, etc')

    
    # Attribute Indicator uses Python identifier Indicator
    __Indicator = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Indicator'), 'Indicator', '__urnoasisnamestcciqxsdschemaxAL2_0_DependentLocalityType_Indicator', pyxb.binding.datatypes.anySimpleType)
    
    Indicator = property(__Indicator.value, __Indicator.set, None, u'Eg. Erode (Dist) where (Dist) is the Indicator')

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_strict, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'urn:oasis:names:tc:ciq:xsdschema:xAL:2.0'))
    _HasWildcardElement = True

    _ElementMap = {
        __DependentLocalityName.name() : __DependentLocalityName,
        __Thoroughfare.name() : __Thoroughfare,
        __PostalRoute.name() : __PostalRoute,
        __PostalCode.name() : __PostalCode,
        __DependentLocality.name() : __DependentLocality,
        __Premise.name() : __Premise,
        __DependentLocalityNumber.name() : __DependentLocalityNumber,
        __PostOffice.name() : __PostOffice,
        __AddressLine.name() : __AddressLine,
        __LargeMailUser.name() : __LargeMailUser,
        __PostBox.name() : __PostBox
    }
    _AttributeMap = {
        __Connector.name() : __Connector,
        __UsageType.name() : __UsageType,
        __Type.name() : __Type,
        __Indicator.name() : __Indicator
    }
Namespace.addCategoryObject('typeBinding', u'DependentLocalityType', DependentLocalityType)


# Complex type CTD_ANON_ with content type MIXED
class CTD_ANON_ (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_MIXED
    _Abstract = False
    _ExpandedName = None
    # Base type is pyxb.binding.datatypes.anyType
    
    # Attribute Code uses Python identifier Code
    __Code = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Code'), 'Code', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON__Code', pyxb.binding.datatypes.anySimpleType)
    
    Code = property(__Code.value, __Code.set, None, u'Used by postal services to encode the name of the element.')

    
    # Attribute Type uses Python identifier Type
    __Type = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Type'), 'Type', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON__Type', pyxb.binding.datatypes.anySimpleType)
    
    Type = property(__Type.value, __Type.set, None, u'Old name, new name, etc')

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_strict, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'urn:oasis:names:tc:ciq:xsdschema:xAL:2.0'))

    _ElementMap = {
        
    }
    _AttributeMap = {
        __Code.name() : __Code,
        __Type.name() : __Type
    }



# Complex type CTD_ANON_2 with content type MIXED
class CTD_ANON_2 (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_MIXED
    _Abstract = False
    _ExpandedName = None
    # Base type is pyxb.binding.datatypes.anyType
    
    # Attribute Code uses Python identifier Code
    __Code = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Code'), 'Code', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_2_Code', pyxb.binding.datatypes.anySimpleType)
    
    Code = property(__Code.value, __Code.set, None, u'Used by postal services to encode the name of the element.')

    
    # Attribute NameNumberOccurrence uses Python identifier NameNumberOccurrence
    __NameNumberOccurrence = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'NameNumberOccurrence'), 'NameNumberOccurrence', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_2_NameNumberOccurrence', STD_ANON)
    
    NameNumberOccurrence = property(__NameNumberOccurrence.value, __NameNumberOccurrence.set, None, u'Eg. SECTOR occurs before 5 in SECTOR 5')

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_strict, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'urn:oasis:names:tc:ciq:xsdschema:xAL:2.0'))

    _ElementMap = {
        
    }
    _AttributeMap = {
        __Code.name() : __Code,
        __NameNumberOccurrence.name() : __NameNumberOccurrence
    }



# Complex type CTD_ANON_3 with content type ELEMENT_ONLY
class CTD_ANON_3 (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = None
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}PremiseNumber uses Python identifier PremiseNumber
    __PremiseNumber = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'PremiseNumber'), 'PremiseNumber', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_3_urnoasisnamestcciqxsdschemaxAL2_0PremiseNumber', True)

    
    PremiseNumber = property(__PremiseNumber.value, __PremiseNumber.set, None, u'Specification of the identifier of the premise (house, building, etc). Premises in a street are often uniquely identified by means of consecutive identifiers. The identifier can be a number, a letter or any combination of the two.')

    
    # Element {urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}PostalCode uses Python identifier PostalCode
    __PostalCode = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'PostalCode'), 'PostalCode', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_3_urnoasisnamestcciqxsdschemaxAL2_0PostalCode', False)

    
    PostalCode = property(__PostalCode.value, __PostalCode.set, None, u'PostalCode is the container element for either simple or complex (extended) postal codes. Type: Area Code, Postcode, etc.')

    
    # Element {urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}Firm uses Python identifier Firm
    __Firm = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'Firm'), 'Firm', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_3_urnoasisnamestcciqxsdschemaxAL2_0Firm', False)

    
    Firm = property(__Firm.value, __Firm.set, None, u'Specification of a firm, company, organization, etc. It can be specified as part of an address that contains a street or a postbox. It is therefore different from a large mail user address, which contains no street.')

    
    # Element {urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}MailStop uses Python identifier MailStop
    __MailStop = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'MailStop'), 'MailStop', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_3_urnoasisnamestcciqxsdschemaxAL2_0MailStop', False)

    
    MailStop = property(__MailStop.value, __MailStop.set, None, u'A MailStop is where the the mail is delivered to within a premise/subpremise/firm or a facility.')

    
    # Element {urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}AddressLine uses Python identifier AddressLine
    __AddressLine = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'AddressLine'), 'AddressLine', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_3_urnoasisnamestcciqxsdschemaxAL2_0AddressLine', True)

    
    AddressLine = property(__AddressLine.value, __AddressLine.set, None, u'Free format address representation. An address can have more than one line. The order of the AddressLine elements must be preserved.')

    
    # Element {urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}PremiseNumberSuffix uses Python identifier PremiseNumberSuffix
    __PremiseNumberSuffix = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'PremiseNumberSuffix'), 'PremiseNumberSuffix', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_3_urnoasisnamestcciqxsdschemaxAL2_0PremiseNumberSuffix', True)

    
    PremiseNumberSuffix = property(__PremiseNumberSuffix.value, __PremiseNumberSuffix.set, None, u'A in 12A')

    
    # Element {urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}SubPremise uses Python identifier SubPremise
    __SubPremise = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'SubPremise'), 'SubPremise', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_3_urnoasisnamestcciqxsdschemaxAL2_0SubPremise', True)

    
    SubPremise = property(__SubPremise.value, __SubPremise.set, None, u'Specification of a single sub-premise. Examples of sub-premises are apartments and suites. Each sub-premise should be uniquely identifiable.')

    
    # Element {urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}PremiseLocation uses Python identifier PremiseLocation
    __PremiseLocation = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'PremiseLocation'), 'PremiseLocation', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_3_urnoasisnamestcciqxsdschemaxAL2_0PremiseLocation', False)

    
    PremiseLocation = property(__PremiseLocation.value, __PremiseLocation.set, None, u'LOBBY, BASEMENT, GROUND FLOOR, etc...')

    
    # Element {urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}BuildingName uses Python identifier BuildingName
    __BuildingName = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'BuildingName'), 'BuildingName', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_3_urnoasisnamestcciqxsdschemaxAL2_0BuildingName', True)

    
    BuildingName = property(__BuildingName.value, __BuildingName.set, None, u'Specification of the name of a building.')

    
    # Element {urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}PremiseNumberRange uses Python identifier PremiseNumberRange
    __PremiseNumberRange = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'PremiseNumberRange'), 'PremiseNumberRange', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_3_urnoasisnamestcciqxsdschemaxAL2_0PremiseNumberRange', False)

    
    PremiseNumberRange = property(__PremiseNumberRange.value, __PremiseNumberRange.set, None, u'Specification for defining the premise number range. Some premises have number as Building C1-C7')

    
    # Element {urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}Premise uses Python identifier Premise
    __Premise = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'Premise'), 'Premise', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_3_urnoasisnamestcciqxsdschemaxAL2_0Premise', False)

    
    Premise = property(__Premise.value, __Premise.set, None, u'Specification of a single premise, for example a house or a building. The premise as a whole has a unique premise (house) number or a premise name.  There could be more than \none premise in a street referenced in an address. For example a building address near a major shopping centre or raiwlay station')

    
    # Element {urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}PremiseName uses Python identifier PremiseName
    __PremiseName = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'PremiseName'), 'PremiseName', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_3_urnoasisnamestcciqxsdschemaxAL2_0PremiseName', True)

    
    PremiseName = property(__PremiseName.value, __PremiseName.set, None, u'Specification of the name of the premise (house, building, park, farm, etc). A premise name is specified when the premise cannot be addressed using a street name plus premise (house) number.')

    
    # Element {urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}PremiseNumberPrefix uses Python identifier PremiseNumberPrefix
    __PremiseNumberPrefix = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'PremiseNumberPrefix'), 'PremiseNumberPrefix', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_3_urnoasisnamestcciqxsdschemaxAL2_0PremiseNumberPrefix', True)

    
    PremiseNumberPrefix = property(__PremiseNumberPrefix.value, __PremiseNumberPrefix.set, None, u'A in A12')

    
    # Attribute Type uses Python identifier Type
    __Type = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Type'), 'Type', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_3_Type', pyxb.binding.datatypes.anySimpleType)
    
    Type = property(__Type.value, __Type.set, None, u'COMPLEXE in COMPLEX DES JARDINS, A building, station, etc')

    
    # Attribute PremiseDependencyType uses Python identifier PremiseDependencyType
    __PremiseDependencyType = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'PremiseDependencyType'), 'PremiseDependencyType', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_3_PremiseDependencyType', pyxb.binding.datatypes.anySimpleType)
    
    PremiseDependencyType = property(__PremiseDependencyType.value, __PremiseDependencyType.set, None, u'NEAR, ADJACENT TO, etc')

    
    # Attribute PremiseThoroughfareConnector uses Python identifier PremiseThoroughfareConnector
    __PremiseThoroughfareConnector = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'PremiseThoroughfareConnector'), 'PremiseThoroughfareConnector', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_3_PremiseThoroughfareConnector', pyxb.binding.datatypes.anySimpleType)
    
    PremiseThoroughfareConnector = property(__PremiseThoroughfareConnector.value, __PremiseThoroughfareConnector.set, None, u'DES, DE, LA, LA, DU in RUE DU BOIS. These terms connect a premise/thoroughfare type and premise/thoroughfare name. Terms may appear with names AVE DU BOIS')

    
    # Attribute PremiseDependency uses Python identifier PremiseDependency
    __PremiseDependency = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'PremiseDependency'), 'PremiseDependency', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_3_PremiseDependency', pyxb.binding.datatypes.anySimpleType)
    
    PremiseDependency = property(__PremiseDependency.value, __PremiseDependency.set, None, u'STREET, PREMISE, SUBPREMISE, PARK, FARM, etc')

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_strict, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'urn:oasis:names:tc:ciq:xsdschema:xAL:2.0'))
    _HasWildcardElement = True

    _ElementMap = {
        __PremiseNumber.name() : __PremiseNumber,
        __PostalCode.name() : __PostalCode,
        __Firm.name() : __Firm,
        __MailStop.name() : __MailStop,
        __AddressLine.name() : __AddressLine,
        __PremiseNumberSuffix.name() : __PremiseNumberSuffix,
        __SubPremise.name() : __SubPremise,
        __PremiseLocation.name() : __PremiseLocation,
        __BuildingName.name() : __BuildingName,
        __PremiseNumberRange.name() : __PremiseNumberRange,
        __Premise.name() : __Premise,
        __PremiseName.name() : __PremiseName,
        __PremiseNumberPrefix.name() : __PremiseNumberPrefix
    }
    _AttributeMap = {
        __Type.name() : __Type,
        __PremiseDependencyType.name() : __PremiseDependencyType,
        __PremiseThoroughfareConnector.name() : __PremiseThoroughfareConnector,
        __PremiseDependency.name() : __PremiseDependency
    }



# Complex type CTD_ANON_4 with content type ELEMENT_ONLY
class CTD_ANON_4 (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = None
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}AddressLine uses Python identifier AddressLine
    __AddressLine = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'AddressLine'), 'AddressLine', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_4_urnoasisnamestcciqxsdschemaxAL2_0AddressLine', True)

    
    AddressLine = property(__AddressLine.value, __AddressLine.set, None, u'Free format address representation. An address can have more than one line. The order of the AddressLine elements must be preserved.')

    
    # Element {urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}PostalCodeNumberExtension uses Python identifier PostalCodeNumberExtension
    __PostalCodeNumberExtension = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'PostalCodeNumberExtension'), 'PostalCodeNumberExtension', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_4_urnoasisnamestcciqxsdschemaxAL2_0PostalCodeNumberExtension', True)

    
    PostalCodeNumberExtension = property(__PostalCodeNumberExtension.value, __PostalCodeNumberExtension.set, None, u'Examples are: 1234 (USA), 1G (UK), etc.')

    
    # Element {urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}PostTown uses Python identifier PostTown
    __PostTown = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'PostTown'), 'PostTown', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_4_urnoasisnamestcciqxsdschemaxAL2_0PostTown', False)

    
    PostTown = property(__PostTown.value, __PostTown.set, None, u'A post town is not the same as a locality. A post town can encompass a collection of (small) localities. It can also be a subpart of a locality. An actual post town in Norway is "Bergen".')

    
    # Element {urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}PostalCodeNumber uses Python identifier PostalCodeNumber
    __PostalCodeNumber = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'PostalCodeNumber'), 'PostalCodeNumber', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_4_urnoasisnamestcciqxsdschemaxAL2_0PostalCodeNumber', True)

    
    PostalCodeNumber = property(__PostalCodeNumber.value, __PostalCodeNumber.set, None, u'Specification of a postcode. The postcode is formatted according to country-specific rules. Example: SW3 0A8-1A, 600074, 2067')

    
    # Attribute Type uses Python identifier Type
    __Type = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Type'), 'Type', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_4_Type', pyxb.binding.datatypes.anySimpleType)
    
    Type = property(__Type.value, __Type.set, None, u'Area Code, Postcode, Delivery code as in NZ, etc')

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_strict, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'urn:oasis:names:tc:ciq:xsdschema:xAL:2.0'))
    _HasWildcardElement = True

    _ElementMap = {
        __AddressLine.name() : __AddressLine,
        __PostalCodeNumberExtension.name() : __PostalCodeNumberExtension,
        __PostTown.name() : __PostTown,
        __PostalCodeNumber.name() : __PostalCodeNumber
    }
    _AttributeMap = {
        __Type.name() : __Type
    }



# Complex type CTD_ANON_5 with content type MIXED
class CTD_ANON_5 (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_MIXED
    _Abstract = False
    _ExpandedName = None
    # Base type is pyxb.binding.datatypes.anyType
    
    # Attribute Type uses Python identifier Type
    __Type = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Type'), 'Type', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_5_Type', pyxb.binding.datatypes.anySimpleType)
    
    Type = property(__Type.value, __Type.set, None, u'Specific to postal service')

    
    # Attribute Code uses Python identifier Code
    __Code = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Code'), 'Code', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_5_Code', pyxb.binding.datatypes.anySimpleType)
    
    Code = property(__Code.value, __Code.set, None, u'Used by postal services to encode the name of the element.')

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_strict, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'urn:oasis:names:tc:ciq:xsdschema:xAL:2.0'))

    _ElementMap = {
        
    }
    _AttributeMap = {
        __Type.name() : __Type,
        __Code.name() : __Code
    }



# Complex type CTD_ANON_6 with content type MIXED
class CTD_ANON_6 (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_MIXED
    _Abstract = False
    _ExpandedName = None
    # Base type is pyxb.binding.datatypes.anyType
    
    # Attribute Code uses Python identifier Code
    __Code = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Code'), 'Code', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_6_Code', pyxb.binding.datatypes.anySimpleType)
    
    Code = property(__Code.value, __Code.set, None, u'Used by postal services to encode the name of the element.')

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_strict, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'urn:oasis:names:tc:ciq:xsdschema:xAL:2.0'))

    _ElementMap = {
        
    }
    _AttributeMap = {
        __Code.name() : __Code
    }



# Complex type CTD_ANON_7 with content type MIXED
class CTD_ANON_7 (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_MIXED
    _Abstract = False
    _ExpandedName = None
    # Base type is pyxb.binding.datatypes.anyType
    
    # Attribute NumberPrefixSeparator uses Python identifier NumberPrefixSeparator
    __NumberPrefixSeparator = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'NumberPrefixSeparator'), 'NumberPrefixSeparator', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_7_NumberPrefixSeparator', pyxb.binding.datatypes.anySimpleType)
    
    NumberPrefixSeparator = property(__NumberPrefixSeparator.value, __NumberPrefixSeparator.set, None, None)

    
    # Attribute Code uses Python identifier Code
    __Code = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Code'), 'Code', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_7_Code', pyxb.binding.datatypes.anySimpleType)
    
    Code = property(__Code.value, __Code.set, None, u'Used by postal services to encode the name of the element.')

    
    # Attribute Type uses Python identifier Type
    __Type = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Type'), 'Type', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_7_Type', pyxb.binding.datatypes.anySimpleType)
    
    Type = property(__Type.value, __Type.set, None, None)

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_strict, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'urn:oasis:names:tc:ciq:xsdschema:xAL:2.0'))

    _ElementMap = {
        
    }
    _AttributeMap = {
        __NumberPrefixSeparator.name() : __NumberPrefixSeparator,
        __Code.name() : __Code,
        __Type.name() : __Type
    }



# Complex type ThoroughfareNameType with content type MIXED
class ThoroughfareNameType (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_MIXED
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'ThoroughfareNameType')
    # Base type is pyxb.binding.datatypes.anyType
    
    # Attribute Code uses Python identifier Code
    __Code = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Code'), 'Code', '__urnoasisnamestcciqxsdschemaxAL2_0_ThoroughfareNameType_Code', pyxb.binding.datatypes.anySimpleType)
    
    Code = property(__Code.value, __Code.set, None, u'Used by postal services to encode the name of the element.')

    
    # Attribute Type uses Python identifier Type
    __Type = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Type'), 'Type', '__urnoasisnamestcciqxsdschemaxAL2_0_ThoroughfareNameType_Type', pyxb.binding.datatypes.anySimpleType)
    
    Type = property(__Type.value, __Type.set, None, None)

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_strict, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'urn:oasis:names:tc:ciq:xsdschema:xAL:2.0'))

    _ElementMap = {
        
    }
    _AttributeMap = {
        __Code.name() : __Code,
        __Type.name() : __Type
    }
Namespace.addCategoryObject('typeBinding', u'ThoroughfareNameType', ThoroughfareNameType)


# Complex type CTD_ANON_8 with content type ELEMENT_ONLY
class CTD_ANON_8 (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = None
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}PostalRoute uses Python identifier PostalRoute
    __PostalRoute = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'PostalRoute'), 'PostalRoute', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_8_urnoasisnamestcciqxsdschemaxAL2_0PostalRoute', False)

    
    PostalRoute = property(__PostalRoute.value, __PostalRoute.set, None, u'A Postal van is specific for a route as in Is`rael, Rural route')

    
    # Element {urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}PostOfficeNumber uses Python identifier PostOfficeNumber
    __PostOfficeNumber = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'PostOfficeNumber'), 'PostOfficeNumber', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_8_urnoasisnamestcciqxsdschemaxAL2_0PostOfficeNumber', False)

    
    PostOfficeNumber = property(__PostOfficeNumber.value, __PostOfficeNumber.set, None, u'Specification of the number of the postoffice. Common in rural postoffices')

    
    # Element {urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}PostBox uses Python identifier PostBox
    __PostBox = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'PostBox'), 'PostBox', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_8_urnoasisnamestcciqxsdschemaxAL2_0PostBox', False)

    
    PostBox = property(__PostBox.value, __PostBox.set, None, u'Specification of a postbox like mail delivery point. Only a single postbox number can be specified. Examples of postboxes are POBox, free mail numbers, etc.')

    
    # Element {urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}PostOfficeName uses Python identifier PostOfficeName
    __PostOfficeName = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'PostOfficeName'), 'PostOfficeName', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_8_urnoasisnamestcciqxsdschemaxAL2_0PostOfficeName', True)

    
    PostOfficeName = property(__PostOfficeName.value, __PostOfficeName.set, None, u'Specification of the name of the post office. This can be a rural postoffice where post is delivered or a post office containing post office boxes.')

    
    # Element {urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}PostalCode uses Python identifier PostalCode
    __PostalCode = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'PostalCode'), 'PostalCode', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_8_urnoasisnamestcciqxsdschemaxAL2_0PostalCode', False)

    
    PostalCode = property(__PostalCode.value, __PostalCode.set, None, u'PostalCode is the container element for either simple or complex (extended) postal codes. Type: Area Code, Postcode, etc.')

    
    # Element {urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}AddressLine uses Python identifier AddressLine
    __AddressLine = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'AddressLine'), 'AddressLine', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_8_urnoasisnamestcciqxsdschemaxAL2_0AddressLine', True)

    
    AddressLine = property(__AddressLine.value, __AddressLine.set, None, u'Free format address representation. An address can have more than one line. The order of the AddressLine elements must be preserved.')

    
    # Attribute Indicator uses Python identifier Indicator
    __Indicator = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Indicator'), 'Indicator', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_8_Indicator', pyxb.binding.datatypes.anySimpleType)
    
    Indicator = property(__Indicator.value, __Indicator.set, None, u'eg. Kottivakkam (P.O) here (P.O) is the Indicator')

    
    # Attribute Type uses Python identifier Type
    __Type = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Type'), 'Type', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_8_Type', pyxb.binding.datatypes.anySimpleType)
    
    Type = property(__Type.value, __Type.set, None, u'Could be a Mobile Postoffice Van as in Isreal')

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_strict, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'urn:oasis:names:tc:ciq:xsdschema:xAL:2.0'))
    _HasWildcardElement = True

    _ElementMap = {
        __PostalRoute.name() : __PostalRoute,
        __PostOfficeNumber.name() : __PostOfficeNumber,
        __PostBox.name() : __PostBox,
        __PostOfficeName.name() : __PostOfficeName,
        __PostalCode.name() : __PostalCode,
        __AddressLine.name() : __AddressLine
    }
    _AttributeMap = {
        __Indicator.name() : __Indicator,
        __Type.name() : __Type
    }



# Complex type CTD_ANON_9 with content type ELEMENT_ONLY
class CTD_ANON_9 (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = None
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}PostOffice uses Python identifier PostOffice
    __PostOffice = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'PostOffice'), 'PostOffice', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_9_urnoasisnamestcciqxsdschemaxAL2_0PostOffice', False)

    
    PostOffice = property(__PostOffice.value, __PostOffice.set, None, u'Specification of a post office. Examples are a rural post office where post is delivered and a post office containing post office boxes.')

    
    # Element {urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}PostalCode uses Python identifier PostalCode
    __PostalCode = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'PostalCode'), 'PostalCode', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_9_urnoasisnamestcciqxsdschemaxAL2_0PostalCode', False)

    
    PostalCode = property(__PostalCode.value, __PostalCode.set, None, u'PostalCode is the container element for either simple or complex (extended) postal codes. Type: Area Code, Postcode, etc.')

    
    # Element {urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}AdministrativeAreaName uses Python identifier AdministrativeAreaName
    __AdministrativeAreaName = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'AdministrativeAreaName'), 'AdministrativeAreaName', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_9_urnoasisnamestcciqxsdschemaxAL2_0AdministrativeAreaName', True)

    
    AdministrativeAreaName = property(__AdministrativeAreaName.value, __AdministrativeAreaName.set, None, u' Name of the administrative area. eg. MI in USA, NSW in Australia')

    
    # Element {urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}AddressLine uses Python identifier AddressLine
    __AddressLine = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'AddressLine'), 'AddressLine', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_9_urnoasisnamestcciqxsdschemaxAL2_0AddressLine', True)

    
    AddressLine = property(__AddressLine.value, __AddressLine.set, None, u'Free format address representation. An address can have more than one line. The order of the AddressLine elements must be preserved.')

    
    # Element {urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}Locality uses Python identifier Locality
    __Locality = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'Locality'), 'Locality', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_9_urnoasisnamestcciqxsdschemaxAL2_0Locality', False)

    
    Locality = property(__Locality.value, __Locality.set, None, u'Locality is one level lower than adminisstrative area. Eg.: cities, reservations and any other built-up areas.')

    
    # Element {urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}SubAdministrativeArea uses Python identifier SubAdministrativeArea
    __SubAdministrativeArea = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'SubAdministrativeArea'), 'SubAdministrativeArea', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_9_urnoasisnamestcciqxsdschemaxAL2_0SubAdministrativeArea', False)

    
    SubAdministrativeArea = property(__SubAdministrativeArea.value, __SubAdministrativeArea.set, None, u' Specification of a sub-administrative area. An example of a sub-administrative areas is a county. There are two places where the name of an administrative \narea can be specified and in this case, one becomes sub-administrative area.')

    
    # Attribute UsageType uses Python identifier UsageType
    __UsageType = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'UsageType'), 'UsageType', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_9_UsageType', pyxb.binding.datatypes.anySimpleType)
    
    UsageType = property(__UsageType.value, __UsageType.set, None, u'Postal or Political - Sometimes locations must be distinguished between postal system, and physical locations as defined by a political system')

    
    # Attribute Type uses Python identifier Type
    __Type = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Type'), 'Type', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_9_Type', pyxb.binding.datatypes.anySimpleType)
    
    Type = property(__Type.value, __Type.set, None, u'Province or State or County or Kanton, etc')

    
    # Attribute Indicator uses Python identifier Indicator
    __Indicator = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Indicator'), 'Indicator', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_9_Indicator', pyxb.binding.datatypes.anySimpleType)
    
    Indicator = property(__Indicator.value, __Indicator.set, None, u'Erode (Dist) where (Dist) is the Indicator')

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_strict, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'urn:oasis:names:tc:ciq:xsdschema:xAL:2.0'))
    _HasWildcardElement = True

    _ElementMap = {
        __PostOffice.name() : __PostOffice,
        __PostalCode.name() : __PostalCode,
        __AdministrativeAreaName.name() : __AdministrativeAreaName,
        __AddressLine.name() : __AddressLine,
        __Locality.name() : __Locality,
        __SubAdministrativeArea.name() : __SubAdministrativeArea
    }
    _AttributeMap = {
        __UsageType.name() : __UsageType,
        __Type.name() : __Type,
        __Indicator.name() : __Indicator
    }



# Complex type CTD_ANON_10 with content type MIXED
class CTD_ANON_10 (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_MIXED
    _Abstract = False
    _ExpandedName = None
    # Base type is pyxb.binding.datatypes.anyType
    
    # Attribute Indicator uses Python identifier Indicator
    __Indicator = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Indicator'), 'Indicator', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_10_Indicator', pyxb.binding.datatypes.anySimpleType)
    
    Indicator = property(__Indicator.value, __Indicator.set, None, u'MS in MS 62, # in MS # 12, etc.')

    
    # Attribute IndicatorOccurrence uses Python identifier IndicatorOccurrence
    __IndicatorOccurrence = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'IndicatorOccurrence'), 'IndicatorOccurrence', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_10_IndicatorOccurrence', STD_ANON_)
    
    IndicatorOccurrence = property(__IndicatorOccurrence.value, __IndicatorOccurrence.set, None, u'MS occurs before 62 in MS 62')

    
    # Attribute Code uses Python identifier Code
    __Code = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Code'), 'Code', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_10_Code', pyxb.binding.datatypes.anySimpleType)
    
    Code = property(__Code.value, __Code.set, None, u'Used by postal services to encode the name of the element.')

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_strict, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'urn:oasis:names:tc:ciq:xsdschema:xAL:2.0'))

    _ElementMap = {
        
    }
    _AttributeMap = {
        __Indicator.name() : __Indicator,
        __IndicatorOccurrence.name() : __IndicatorOccurrence,
        __Code.name() : __Code
    }



# Complex type CTD_ANON_11 with content type ELEMENT_ONLY
class CTD_ANON_11 (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = None
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}PostalCode uses Python identifier PostalCode
    __PostalCode = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'PostalCode'), 'PostalCode', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_11_urnoasisnamestcciqxsdschemaxAL2_0PostalCode', False)

    
    PostalCode = property(__PostalCode.value, __PostalCode.set, None, u'PostalCode is the container element for either simple or complex (extended) postal codes. Type: Area Code, Postcode, etc.')

    
    # Element {urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}PostBoxNumberPrefix uses Python identifier PostBoxNumberPrefix
    __PostBoxNumberPrefix = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'PostBoxNumberPrefix'), 'PostBoxNumberPrefix', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_11_urnoasisnamestcciqxsdschemaxAL2_0PostBoxNumberPrefix', False)

    
    PostBoxNumberPrefix = property(__PostBoxNumberPrefix.value, __PostBoxNumberPrefix.set, None, u'Specification of the prefix of the post box number. eg. A in POBox:A-123')

    
    # Element {urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}AddressLine uses Python identifier AddressLine
    __AddressLine = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'AddressLine'), 'AddressLine', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_11_urnoasisnamestcciqxsdschemaxAL2_0AddressLine', True)

    
    AddressLine = property(__AddressLine.value, __AddressLine.set, None, u'Free format address representation. An address can have more than one line. The order of the AddressLine elements must be preserved.')

    
    # Element {urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}PostBoxNumber uses Python identifier PostBoxNumber
    __PostBoxNumber = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'PostBoxNumber'), 'PostBoxNumber', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_11_urnoasisnamestcciqxsdschemaxAL2_0PostBoxNumber', False)

    
    PostBoxNumber = property(__PostBoxNumber.value, __PostBoxNumber.set, None, u'Specification of the number of a postbox')

    
    # Element {urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}PostBoxNumberExtension uses Python identifier PostBoxNumberExtension
    __PostBoxNumberExtension = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'PostBoxNumberExtension'), 'PostBoxNumberExtension', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_11_urnoasisnamestcciqxsdschemaxAL2_0PostBoxNumberExtension', False)

    
    PostBoxNumberExtension = property(__PostBoxNumberExtension.value, __PostBoxNumberExtension.set, None, u'Some countries like USA have POBox as 12345-123')

    
    # Element {urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}Firm uses Python identifier Firm
    __Firm = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'Firm'), 'Firm', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_11_urnoasisnamestcciqxsdschemaxAL2_0Firm', False)

    
    Firm = property(__Firm.value, __Firm.set, None, u'Specification of a firm, company, organization, etc. It can be specified as part of an address that contains a street or a postbox. It is therefore different from \na large mail user address, which contains no street.')

    
    # Element {urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}PostBoxNumberSuffix uses Python identifier PostBoxNumberSuffix
    __PostBoxNumberSuffix = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'PostBoxNumberSuffix'), 'PostBoxNumberSuffix', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_11_urnoasisnamestcciqxsdschemaxAL2_0PostBoxNumberSuffix', False)

    
    PostBoxNumberSuffix = property(__PostBoxNumberSuffix.value, __PostBoxNumberSuffix.set, None, u'Specification of the suffix of the post box number. eg. A in POBox:123A')

    
    # Attribute Type uses Python identifier Type
    __Type = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Type'), 'Type', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_11_Type', pyxb.binding.datatypes.anySimpleType)
    
    Type = property(__Type.value, __Type.set, None, u'Possible values are, not limited to: POBox and Freepost.')

    
    # Attribute Indicator uses Python identifier Indicator
    __Indicator = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Indicator'), 'Indicator', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_11_Indicator', pyxb.binding.datatypes.anySimpleType)
    
    Indicator = property(__Indicator.value, __Indicator.set, None, u'LOCKED BAG NO:1234 where the Indicator is NO: and Type is LOCKED BAG')

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_strict, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'urn:oasis:names:tc:ciq:xsdschema:xAL:2.0'))
    _HasWildcardElement = True

    _ElementMap = {
        __PostalCode.name() : __PostalCode,
        __PostBoxNumberPrefix.name() : __PostBoxNumberPrefix,
        __AddressLine.name() : __AddressLine,
        __PostBoxNumber.name() : __PostBoxNumber,
        __PostBoxNumberExtension.name() : __PostBoxNumberExtension,
        __Firm.name() : __Firm,
        __PostBoxNumberSuffix.name() : __PostBoxNumberSuffix
    }
    _AttributeMap = {
        __Type.name() : __Type,
        __Indicator.name() : __Indicator
    }



# Complex type CTD_ANON_12 with content type MIXED
class CTD_ANON_12 (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_MIXED
    _Abstract = False
    _ExpandedName = None
    # Base type is pyxb.binding.datatypes.anyType
    
    # Attribute TypeOccurrence uses Python identifier TypeOccurrence
    __TypeOccurrence = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'TypeOccurrence'), 'TypeOccurrence', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_12_TypeOccurrence', STD_ANON_2)
    
    TypeOccurrence = property(__TypeOccurrence.value, __TypeOccurrence.set, None, u'EGIS Building where EGIS occurs before Building, DES JARDINS occurs after COMPLEXE DES JARDINS')

    
    # Attribute Type uses Python identifier Type
    __Type = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Type'), 'Type', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_12_Type', pyxb.binding.datatypes.anySimpleType)
    
    Type = property(__Type.value, __Type.set, None, None)

    
    # Attribute Code uses Python identifier Code
    __Code = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Code'), 'Code', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_12_Code', pyxb.binding.datatypes.anySimpleType)
    
    Code = property(__Code.value, __Code.set, None, u'Used by postal services to encode the name of the element.')

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_strict, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'urn:oasis:names:tc:ciq:xsdschema:xAL:2.0'))

    _ElementMap = {
        
    }
    _AttributeMap = {
        __TypeOccurrence.name() : __TypeOccurrence,
        __Type.name() : __Type,
        __Code.name() : __Code
    }



# Complex type CTD_ANON_13 with content type MIXED
class CTD_ANON_13 (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_MIXED
    _Abstract = False
    _ExpandedName = None
    # Base type is pyxb.binding.datatypes.anyType
    
    # Attribute NumberPrefixSeparator uses Python identifier NumberPrefixSeparator
    __NumberPrefixSeparator = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'NumberPrefixSeparator'), 'NumberPrefixSeparator', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_13_NumberPrefixSeparator', pyxb.binding.datatypes.anySimpleType)
    
    NumberPrefixSeparator = property(__NumberPrefixSeparator.value, __NumberPrefixSeparator.set, None, u'A-12 where 12 is number and A is prefix and "-" is the separator')

    
    # Attribute Code uses Python identifier Code
    __Code = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Code'), 'Code', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_13_Code', pyxb.binding.datatypes.anySimpleType)
    
    Code = property(__Code.value, __Code.set, None, u'Used by postal services to encode the name of the element.')

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_strict, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'urn:oasis:names:tc:ciq:xsdschema:xAL:2.0'))

    _ElementMap = {
        
    }
    _AttributeMap = {
        __NumberPrefixSeparator.name() : __NumberPrefixSeparator,
        __Code.name() : __Code
    }



# Complex type CTD_ANON_14 with content type MIXED
class CTD_ANON_14 (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_MIXED
    _Abstract = False
    _ExpandedName = None
    # Base type is pyxb.binding.datatypes.anyType
    
    # Attribute Code uses Python identifier Code
    __Code = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Code'), 'Code', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_14_Code', pyxb.binding.datatypes.anySimpleType)
    
    Code = property(__Code.value, __Code.set, None, u'Used by postal services to encode the name of the element.')

    
    # Attribute Type uses Python identifier Type
    __Type = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Type'), 'Type', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_14_Type', pyxb.binding.datatypes.anySimpleType)
    
    Type = property(__Type.value, __Type.set, None, u'Specific to postal service')

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_strict, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'urn:oasis:names:tc:ciq:xsdschema:xAL:2.0'))

    _ElementMap = {
        
    }
    _AttributeMap = {
        __Code.name() : __Code,
        __Type.name() : __Type
    }



# Complex type CTD_ANON_15 with content type ELEMENT_ONLY
class CTD_ANON_15 (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = None
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}DependentLocality uses Python identifier DependentLocality
    __DependentLocality = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'DependentLocality'), 'DependentLocality', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_15_urnoasisnamestcciqxsdschemaxAL2_0DependentLocality', False)

    
    DependentLocality = property(__DependentLocality.value, __DependentLocality.set, None, u'Dependent localities are Districts within cities/towns, locality divisions, postal \ndivisions of cities, suburbs, etc. DependentLocality is a recursive element, but no nesting deeper than two exists (Locality-DependentLocality-DependentLocality).')

    
    # Element {urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}ThoroughfareNumberRange uses Python identifier ThoroughfareNumberRange
    __ThoroughfareNumberRange = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'ThoroughfareNumberRange'), 'ThoroughfareNumberRange', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_15_urnoasisnamestcciqxsdschemaxAL2_0ThoroughfareNumberRange', True)

    
    ThoroughfareNumberRange = property(__ThoroughfareNumberRange.value, __ThoroughfareNumberRange.set, None, u'A container to represent a range of numbers (from x thru y)for a thoroughfare. eg. 1-2 Albert Av')

    
    # Element {urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}PostalCode uses Python identifier PostalCode
    __PostalCode = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'PostalCode'), 'PostalCode', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_15_urnoasisnamestcciqxsdschemaxAL2_0PostalCode', False)

    
    PostalCode = property(__PostalCode.value, __PostalCode.set, None, u'PostalCode is the container element for either simple or complex (extended) postal codes. Type: Area Code, Postcode, etc.')

    
    # Element {urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}DependentThoroughfare uses Python identifier DependentThoroughfare
    __DependentThoroughfare = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'DependentThoroughfare'), 'DependentThoroughfare', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_15_urnoasisnamestcciqxsdschemaxAL2_0DependentThoroughfare', False)

    
    DependentThoroughfare = property(__DependentThoroughfare.value, __DependentThoroughfare.set, None, u'DependentThroughfare is related to a street; occurs in GB, IE, ES, PT')

    
    # Element {urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}ThoroughfareName uses Python identifier ThoroughfareName
    __ThoroughfareName = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'ThoroughfareName'), 'ThoroughfareName', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_15_urnoasisnamestcciqxsdschemaxAL2_0ThoroughfareName', True)

    
    ThoroughfareName = property(__ThoroughfareName.value, __ThoroughfareName.set, None, u'Specification of the name of a Thoroughfare (also dependant street name): street name, canal name, etc.')

    
    # Element {urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}ThoroughfarePreDirection uses Python identifier ThoroughfarePreDirection
    __ThoroughfarePreDirection = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'ThoroughfarePreDirection'), 'ThoroughfarePreDirection', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_15_urnoasisnamestcciqxsdschemaxAL2_0ThoroughfarePreDirection', False)

    
    ThoroughfarePreDirection = property(__ThoroughfarePreDirection.value, __ThoroughfarePreDirection.set, None, u'North Baker Street, where North is the pre-direction. The direction appears before the name.')

    
    # Element {urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}ThoroughfareNumber uses Python identifier ThoroughfareNumber
    __ThoroughfareNumber = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'ThoroughfareNumber'), 'ThoroughfareNumber', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_15_urnoasisnamestcciqxsdschemaxAL2_0ThoroughfareNumber', True)

    
    ThoroughfareNumber = property(__ThoroughfareNumber.value, __ThoroughfareNumber.set, None, u'Eg.: 23 Archer street or 25/15 Zero Avenue, etc')

    
    # Element {urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}Firm uses Python identifier Firm
    __Firm = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'Firm'), 'Firm', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_15_urnoasisnamestcciqxsdschemaxAL2_0Firm', False)

    
    Firm = property(__Firm.value, __Firm.set, None, u'Specification of a firm, company, organization, etc. It can be specified as part of an address that contains a street or a postbox. It is therefore different from \na large mail user address, which contains no street.')

    
    # Element {urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}ThoroughfareTrailingType uses Python identifier ThoroughfareTrailingType
    __ThoroughfareTrailingType = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'ThoroughfareTrailingType'), 'ThoroughfareTrailingType', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_15_urnoasisnamestcciqxsdschemaxAL2_0ThoroughfareTrailingType', False)

    
    ThoroughfareTrailingType = property(__ThoroughfareTrailingType.value, __ThoroughfareTrailingType.set, None, u'Appears after the thoroughfare name. Ed. British: Baker Lane, where Lane is the trailing type.')

    
    # Element {urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}AddressLine uses Python identifier AddressLine
    __AddressLine = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'AddressLine'), 'AddressLine', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_15_urnoasisnamestcciqxsdschemaxAL2_0AddressLine', True)

    
    AddressLine = property(__AddressLine.value, __AddressLine.set, None, u'Free format address representation. An address can have more than one line. The order of the AddressLine elements must be preserved.')

    
    # Element {urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}ThoroughfareLeadingType uses Python identifier ThoroughfareLeadingType
    __ThoroughfareLeadingType = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'ThoroughfareLeadingType'), 'ThoroughfareLeadingType', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_15_urnoasisnamestcciqxsdschemaxAL2_0ThoroughfareLeadingType', False)

    
    ThoroughfareLeadingType = property(__ThoroughfareLeadingType.value, __ThoroughfareLeadingType.set, None, u'Appears before the thoroughfare name. Ed. Spanish: Avenida Aurora, where Avenida is the leading type / French: Rue Moliere, where Rue is the leading type.')

    
    # Element {urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}ThoroughfareNumberSuffix uses Python identifier ThoroughfareNumberSuffix
    __ThoroughfareNumberSuffix = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'ThoroughfareNumberSuffix'), 'ThoroughfareNumberSuffix', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_15_urnoasisnamestcciqxsdschemaxAL2_0ThoroughfareNumberSuffix', True)

    
    ThoroughfareNumberSuffix = property(__ThoroughfareNumberSuffix.value, __ThoroughfareNumberSuffix.set, None, u'Suffix after the number. A in 12A Archer Street')

    
    # Element {urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}Premise uses Python identifier Premise
    __Premise = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'Premise'), 'Premise', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_15_urnoasisnamestcciqxsdschemaxAL2_0Premise', False)

    
    Premise = property(__Premise.value, __Premise.set, None, u'Specification of a single premise, for example a house or a building. The premise as a whole has a unique premise (house) number or a premise name.  There could be more than \none premise in a street referenced in an address. For example a building address near a major shopping centre or raiwlay station')

    
    # Element {urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}ThoroughfarePostDirection uses Python identifier ThoroughfarePostDirection
    __ThoroughfarePostDirection = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'ThoroughfarePostDirection'), 'ThoroughfarePostDirection', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_15_urnoasisnamestcciqxsdschemaxAL2_0ThoroughfarePostDirection', False)

    
    ThoroughfarePostDirection = property(__ThoroughfarePostDirection.value, __ThoroughfarePostDirection.set, None, u'221-bis Baker Street North, where North is the post-direction. The post-direction appears after the name.')

    
    # Element {urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}ThoroughfareNumberPrefix uses Python identifier ThoroughfareNumberPrefix
    __ThoroughfareNumberPrefix = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'ThoroughfareNumberPrefix'), 'ThoroughfareNumberPrefix', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_15_urnoasisnamestcciqxsdschemaxAL2_0ThoroughfareNumberPrefix', True)

    
    ThoroughfareNumberPrefix = property(__ThoroughfareNumberPrefix.value, __ThoroughfareNumberPrefix.set, None, u'Prefix before the number. A in A12 Archer Street')

    
    # Attribute DependentThoroughfaresIndicator uses Python identifier DependentThoroughfaresIndicator
    __DependentThoroughfaresIndicator = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'DependentThoroughfaresIndicator'), 'DependentThoroughfaresIndicator', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_15_DependentThoroughfaresIndicator', pyxb.binding.datatypes.anySimpleType)
    
    DependentThoroughfaresIndicator = property(__DependentThoroughfaresIndicator.value, __DependentThoroughfaresIndicator.set, None, u'Corner of, Intersection of')

    
    # Attribute DependentThoroughfaresConnector uses Python identifier DependentThoroughfaresConnector
    __DependentThoroughfaresConnector = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'DependentThoroughfaresConnector'), 'DependentThoroughfaresConnector', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_15_DependentThoroughfaresConnector', pyxb.binding.datatypes.anySimpleType)
    
    DependentThoroughfaresConnector = property(__DependentThoroughfaresConnector.value, __DependentThoroughfaresConnector.set, None, u'Corner of Street1 AND Street 2 where AND is the Connector')

    
    # Attribute DependentThoroughfares uses Python identifier DependentThoroughfares
    __DependentThoroughfares = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'DependentThoroughfares'), 'DependentThoroughfares', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_15_DependentThoroughfares', STD_ANON_3)
    
    DependentThoroughfares = property(__DependentThoroughfares.value, __DependentThoroughfares.set, None, u'Does this thoroughfare have a a dependent thoroughfare? Corner of street X, etc')

    
    # Attribute DependentThoroughfaresType uses Python identifier DependentThoroughfaresType
    __DependentThoroughfaresType = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'DependentThoroughfaresType'), 'DependentThoroughfaresType', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_15_DependentThoroughfaresType', pyxb.binding.datatypes.anySimpleType)
    
    DependentThoroughfaresType = property(__DependentThoroughfaresType.value, __DependentThoroughfaresType.set, None, u'STS in GEORGE and ADELAIDE STS, RDS IN A and B RDS, etc. Use only when both the street types are the same')

    
    # Attribute Type uses Python identifier Type
    __Type = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Type'), 'Type', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_15_Type', pyxb.binding.datatypes.anySimpleType)
    
    Type = property(__Type.value, __Type.set, None, None)

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_strict, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'urn:oasis:names:tc:ciq:xsdschema:xAL:2.0'))
    _HasWildcardElement = True

    _ElementMap = {
        __DependentLocality.name() : __DependentLocality,
        __ThoroughfareNumberRange.name() : __ThoroughfareNumberRange,
        __PostalCode.name() : __PostalCode,
        __DependentThoroughfare.name() : __DependentThoroughfare,
        __ThoroughfareName.name() : __ThoroughfareName,
        __ThoroughfarePreDirection.name() : __ThoroughfarePreDirection,
        __ThoroughfareNumber.name() : __ThoroughfareNumber,
        __Firm.name() : __Firm,
        __ThoroughfareTrailingType.name() : __ThoroughfareTrailingType,
        __AddressLine.name() : __AddressLine,
        __ThoroughfareLeadingType.name() : __ThoroughfareLeadingType,
        __ThoroughfareNumberSuffix.name() : __ThoroughfareNumberSuffix,
        __Premise.name() : __Premise,
        __ThoroughfarePostDirection.name() : __ThoroughfarePostDirection,
        __ThoroughfareNumberPrefix.name() : __ThoroughfareNumberPrefix
    }
    _AttributeMap = {
        __DependentThoroughfaresIndicator.name() : __DependentThoroughfaresIndicator,
        __DependentThoroughfaresConnector.name() : __DependentThoroughfaresConnector,
        __DependentThoroughfares.name() : __DependentThoroughfares,
        __DependentThoroughfaresType.name() : __DependentThoroughfaresType,
        __Type.name() : __Type
    }



# Complex type CTD_ANON_16 with content type MIXED
class CTD_ANON_16 (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_MIXED
    _Abstract = False
    _ExpandedName = None
    # Base type is pyxb.binding.datatypes.anyType
    
    # Attribute Code uses Python identifier Code
    __Code = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Code'), 'Code', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_16_Code', pyxb.binding.datatypes.anySimpleType)
    
    Code = property(__Code.value, __Code.set, None, u'Used by postal services to encode the name of the element.')

    
    # Attribute Type uses Python identifier Type
    __Type = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Type'), 'Type', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_16_Type', pyxb.binding.datatypes.anySimpleType)
    
    Type = property(__Type.value, __Type.set, None, None)

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_strict, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'urn:oasis:names:tc:ciq:xsdschema:xAL:2.0'))

    _ElementMap = {
        
    }
    _AttributeMap = {
        __Code.name() : __Code,
        __Type.name() : __Type
    }



# Complex type CTD_ANON_17 with content type ELEMENT_ONLY
class CTD_ANON_17 (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = None
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}DepartmentName uses Python identifier DepartmentName
    __DepartmentName = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'DepartmentName'), 'DepartmentName', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_17_urnoasisnamestcciqxsdschemaxAL2_0DepartmentName', True)

    
    DepartmentName = property(__DepartmentName.value, __DepartmentName.set, None, u'Specification of the name of a department.')

    
    # Element {urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}PostalCode uses Python identifier PostalCode
    __PostalCode = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'PostalCode'), 'PostalCode', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_17_urnoasisnamestcciqxsdschemaxAL2_0PostalCode', False)

    
    PostalCode = property(__PostalCode.value, __PostalCode.set, None, u'PostalCode is the container element for either simple or complex (extended) postal codes. Type: Area Code, Postcode, etc.')

    
    # Element {urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}AddressLine uses Python identifier AddressLine
    __AddressLine = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'AddressLine'), 'AddressLine', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_17_urnoasisnamestcciqxsdschemaxAL2_0AddressLine', True)

    
    AddressLine = property(__AddressLine.value, __AddressLine.set, None, u'Free format address representation. An address can have more than one line. The order of the AddressLine elements must be preserved.')

    
    # Element {urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}MailStop uses Python identifier MailStop
    __MailStop = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'MailStop'), 'MailStop', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_17_urnoasisnamestcciqxsdschemaxAL2_0MailStop', False)

    
    MailStop = property(__MailStop.value, __MailStop.set, None, u'A MailStop is where the the mail is delivered to within a premise/subpremise/firm or a facility.')

    
    # Attribute Type uses Python identifier Type
    __Type = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Type'), 'Type', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_17_Type', pyxb.binding.datatypes.anySimpleType)
    
    Type = property(__Type.value, __Type.set, None, u'School in Physics School, Division in Radiology division of school of physics')

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_strict, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'urn:oasis:names:tc:ciq:xsdschema:xAL:2.0'))
    _HasWildcardElement = True

    _ElementMap = {
        __DepartmentName.name() : __DepartmentName,
        __PostalCode.name() : __PostalCode,
        __AddressLine.name() : __AddressLine,
        __MailStop.name() : __MailStop
    }
    _AttributeMap = {
        __Type.name() : __Type
    }



# Complex type FirmType with content type ELEMENT_ONLY
class FirmType (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'FirmType')
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}AddressLine uses Python identifier AddressLine
    __AddressLine = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'AddressLine'), 'AddressLine', '__urnoasisnamestcciqxsdschemaxAL2_0_FirmType_urnoasisnamestcciqxsdschemaxAL2_0AddressLine', True)

    
    AddressLine = property(__AddressLine.value, __AddressLine.set, None, u'Free format address representation. An address can have more than one line. The order of the AddressLine elements must be preserved.')

    
    # Element {urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}FirmName uses Python identifier FirmName
    __FirmName = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'FirmName'), 'FirmName', '__urnoasisnamestcciqxsdschemaxAL2_0_FirmType_urnoasisnamestcciqxsdschemaxAL2_0FirmName', True)

    
    FirmName = property(__FirmName.value, __FirmName.set, None, u'Name of the firm')

    
    # Element {urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}MailStop uses Python identifier MailStop
    __MailStop = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'MailStop'), 'MailStop', '__urnoasisnamestcciqxsdschemaxAL2_0_FirmType_urnoasisnamestcciqxsdschemaxAL2_0MailStop', False)

    
    MailStop = property(__MailStop.value, __MailStop.set, None, u'A MailStop is where the the mail is delivered to within a premise/subpremise/firm or a facility.')

    
    # Element {urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}Department uses Python identifier Department
    __Department = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'Department'), 'Department', '__urnoasisnamestcciqxsdschemaxAL2_0_FirmType_urnoasisnamestcciqxsdschemaxAL2_0Department', True)

    
    Department = property(__Department.value, __Department.set, None, u'Subdivision in the firm: School of Physics at Victoria University (School of Physics is the department)')

    
    # Element {urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}PostalCode uses Python identifier PostalCode
    __PostalCode = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'PostalCode'), 'PostalCode', '__urnoasisnamestcciqxsdschemaxAL2_0_FirmType_urnoasisnamestcciqxsdschemaxAL2_0PostalCode', False)

    
    PostalCode = property(__PostalCode.value, __PostalCode.set, None, u'PostalCode is the container element for either simple or complex (extended) postal codes. Type: Area Code, Postcode, etc.')

    
    # Attribute Type uses Python identifier Type
    __Type = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Type'), 'Type', '__urnoasisnamestcciqxsdschemaxAL2_0_FirmType_Type', pyxb.binding.datatypes.anySimpleType)
    
    Type = property(__Type.value, __Type.set, None, None)

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_strict, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'urn:oasis:names:tc:ciq:xsdschema:xAL:2.0'))
    _HasWildcardElement = True

    _ElementMap = {
        __AddressLine.name() : __AddressLine,
        __FirmName.name() : __FirmName,
        __MailStop.name() : __MailStop,
        __Department.name() : __Department,
        __PostalCode.name() : __PostalCode
    }
    _AttributeMap = {
        __Type.name() : __Type
    }
Namespace.addCategoryObject('typeBinding', u'FirmType', FirmType)


# Complex type CTD_ANON_18 with content type MIXED
class CTD_ANON_18 (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_MIXED
    _Abstract = False
    _ExpandedName = None
    # Base type is pyxb.binding.datatypes.anyType
    
    # Attribute PremiseNumberSeparator uses Python identifier PremiseNumberSeparator
    __PremiseNumberSeparator = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'PremiseNumberSeparator'), 'PremiseNumberSeparator', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_18_PremiseNumberSeparator', pyxb.binding.datatypes.anySimpleType)
    
    PremiseNumberSeparator = property(__PremiseNumberSeparator.value, __PremiseNumberSeparator.set, None, u'"/" in 12/14 Archer Street where 12 is sub-premise number and 14 is premise number')

    
    # Attribute IndicatorOccurrence uses Python identifier IndicatorOccurrence
    __IndicatorOccurrence = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'IndicatorOccurrence'), 'IndicatorOccurrence', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_18_IndicatorOccurrence', STD_ANON_4)
    
    IndicatorOccurrence = property(__IndicatorOccurrence.value, __IndicatorOccurrence.set, None, u'"No." occurs before 1 in No.1, or TH occurs after 12 in 12TH')

    
    # Attribute Type uses Python identifier Type
    __Type = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Type'), 'Type', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_18_Type', pyxb.binding.datatypes.anySimpleType)
    
    Type = property(__Type.value, __Type.set, None, None)

    
    # Attribute NumberTypeOccurrence uses Python identifier NumberTypeOccurrence
    __NumberTypeOccurrence = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'NumberTypeOccurrence'), 'NumberTypeOccurrence', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_18_NumberTypeOccurrence', STD_ANON_5)
    
    NumberTypeOccurrence = property(__NumberTypeOccurrence.value, __NumberTypeOccurrence.set, None, u'12TH occurs "before" FLOOR (a type of subpremise) in 12TH FLOOR')

    
    # Attribute Indicator uses Python identifier Indicator
    __Indicator = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Indicator'), 'Indicator', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_18_Indicator', pyxb.binding.datatypes.anySimpleType)
    
    Indicator = property(__Indicator.value, __Indicator.set, None, u'"TH" in 12TH which is a floor number, "NO." in NO.1, "#" in APT #12, etc.')

    
    # Attribute Code uses Python identifier Code
    __Code = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Code'), 'Code', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_18_Code', pyxb.binding.datatypes.anySimpleType)
    
    Code = property(__Code.value, __Code.set, None, u'Used by postal services to encode the name of the element.')

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_strict, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'urn:oasis:names:tc:ciq:xsdschema:xAL:2.0'))

    _ElementMap = {
        
    }
    _AttributeMap = {
        __PremiseNumberSeparator.name() : __PremiseNumberSeparator,
        __IndicatorOccurrence.name() : __IndicatorOccurrence,
        __Type.name() : __Type,
        __NumberTypeOccurrence.name() : __NumberTypeOccurrence,
        __Indicator.name() : __Indicator,
        __Code.name() : __Code
    }



# Complex type CTD_ANON_19 with content type MIXED
class CTD_ANON_19 (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_MIXED
    _Abstract = False
    _ExpandedName = None
    # Base type is pyxb.binding.datatypes.anyType
    
    # Attribute NumberExtensionSeparator uses Python identifier NumberExtensionSeparator
    __NumberExtensionSeparator = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'NumberExtensionSeparator'), 'NumberExtensionSeparator', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_19_NumberExtensionSeparator', pyxb.binding.datatypes.anySimpleType)
    
    NumberExtensionSeparator = property(__NumberExtensionSeparator.value, __NumberExtensionSeparator.set, None, u'The separator between postal code number and the extension. Eg. "-"')

    
    # Attribute Code uses Python identifier Code
    __Code = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Code'), 'Code', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_19_Code', pyxb.binding.datatypes.anySimpleType)
    
    Code = property(__Code.value, __Code.set, None, u'Used by postal services to encode the name of the element.')

    
    # Attribute Type uses Python identifier Type
    __Type = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Type'), 'Type', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_19_Type', pyxb.binding.datatypes.anySimpleType)
    
    Type = property(__Type.value, __Type.set, None, u'Delivery Point Suffix, New Postal Code, etc..')

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_strict, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'urn:oasis:names:tc:ciq:xsdschema:xAL:2.0'))

    _ElementMap = {
        
    }
    _AttributeMap = {
        __NumberExtensionSeparator.name() : __NumberExtensionSeparator,
        __Code.name() : __Code,
        __Type.name() : __Type
    }



# Complex type CTD_ANON_20 with content type MIXED
class CTD_ANON_20 (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_MIXED
    _Abstract = False
    _ExpandedName = None
    # Base type is pyxb.binding.datatypes.anyType
    
    # Attribute Code uses Python identifier Code
    __Code = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Code'), 'Code', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_20_Code', pyxb.binding.datatypes.anySimpleType)
    
    Code = property(__Code.value, __Code.set, None, u'Used by postal services to encode the name of the element.')

    
    # Attribute NumberType uses Python identifier NumberType
    __NumberType = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'NumberType'), 'NumberType', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_20_NumberType', STD_ANON_6)
    
    NumberType = property(__NumberType.value, __NumberType.set, None, u'12 Archer Street is "Single" and 12-14 Archer Street is "Range"')

    
    # Attribute IndicatorOccurrence uses Python identifier IndicatorOccurrence
    __IndicatorOccurrence = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'IndicatorOccurrence'), 'IndicatorOccurrence', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_20_IndicatorOccurrence', STD_ANON_8)
    
    IndicatorOccurrence = property(__IndicatorOccurrence.value, __IndicatorOccurrence.set, None, u'No.12 where "No." is before actual street number')

    
    # Attribute Type uses Python identifier Type
    __Type = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Type'), 'Type', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_20_Type', pyxb.binding.datatypes.anySimpleType)
    
    Type = property(__Type.value, __Type.set, None, None)

    
    # Attribute NumberOccurrence uses Python identifier NumberOccurrence
    __NumberOccurrence = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'NumberOccurrence'), 'NumberOccurrence', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_20_NumberOccurrence', STD_ANON_7)
    
    NumberOccurrence = property(__NumberOccurrence.value, __NumberOccurrence.set, None, u'23 Archer St, Archer Street 23, St Archer 23')

    
    # Attribute Indicator uses Python identifier Indicator
    __Indicator = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Indicator'), 'Indicator', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_20_Indicator', pyxb.binding.datatypes.anySimpleType)
    
    Indicator = property(__Indicator.value, __Indicator.set, None, u'No. in Street No.12 or "#" in Street # 12, etc.')

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_strict, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'urn:oasis:names:tc:ciq:xsdschema:xAL:2.0'))

    _ElementMap = {
        
    }
    _AttributeMap = {
        __Code.name() : __Code,
        __NumberType.name() : __NumberType,
        __IndicatorOccurrence.name() : __IndicatorOccurrence,
        __Type.name() : __Type,
        __NumberOccurrence.name() : __NumberOccurrence,
        __Indicator.name() : __Indicator
    }



# Complex type CTD_ANON_21 with content type ELEMENT_ONLY
class CTD_ANON_21 (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = None
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}PremiseNumberRangeFrom uses Python identifier PremiseNumberRangeFrom
    __PremiseNumberRangeFrom = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'PremiseNumberRangeFrom'), 'PremiseNumberRangeFrom', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_21_urnoasisnamestcciqxsdschemaxAL2_0PremiseNumberRangeFrom', False)

    
    PremiseNumberRangeFrom = property(__PremiseNumberRangeFrom.value, __PremiseNumberRangeFrom.set, None, u'Start number details of the premise number range')

    
    # Element {urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}PremiseNumberRangeTo uses Python identifier PremiseNumberRangeTo
    __PremiseNumberRangeTo = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'PremiseNumberRangeTo'), 'PremiseNumberRangeTo', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_21_urnoasisnamestcciqxsdschemaxAL2_0PremiseNumberRangeTo', False)

    
    PremiseNumberRangeTo = property(__PremiseNumberRangeTo.value, __PremiseNumberRangeTo.set, None, u'End number details of the premise number range')

    
    # Attribute Separator uses Python identifier Separator
    __Separator = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Separator'), 'Separator', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_21_Separator', pyxb.binding.datatypes.anySimpleType)
    
    Separator = property(__Separator.value, __Separator.set, None, u'"-" in 12-14  or "Thru" in 12 Thru 14 etc.')

    
    # Attribute RangeType uses Python identifier RangeType
    __RangeType = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'RangeType'), 'RangeType', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_21_RangeType', pyxb.binding.datatypes.anySimpleType)
    
    RangeType = property(__RangeType.value, __RangeType.set, None, u'Eg. Odd or even number range')

    
    # Attribute Type uses Python identifier Type
    __Type = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Type'), 'Type', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_21_Type', pyxb.binding.datatypes.anySimpleType)
    
    Type = property(__Type.value, __Type.set, None, None)

    
    # Attribute Indicator uses Python identifier Indicator
    __Indicator = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Indicator'), 'Indicator', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_21_Indicator', pyxb.binding.datatypes.anySimpleType)
    
    Indicator = property(__Indicator.value, __Indicator.set, None, u'Eg. No. in Building No:C1-C5')

    
    # Attribute NumberRangeOccurence uses Python identifier NumberRangeOccurence
    __NumberRangeOccurence = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'NumberRangeOccurence'), 'NumberRangeOccurence', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_21_NumberRangeOccurence', STD_ANON_10)
    
    NumberRangeOccurence = property(__NumberRangeOccurence.value, __NumberRangeOccurence.set, None, u'Building 23-25 where the number occurs after building name')

    
    # Attribute IndicatorOccurence uses Python identifier IndicatorOccurence
    __IndicatorOccurence = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'IndicatorOccurence'), 'IndicatorOccurence', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_21_IndicatorOccurence', STD_ANON_9)
    
    IndicatorOccurence = property(__IndicatorOccurence.value, __IndicatorOccurence.set, None, u'No.12-14 where "No." is before actual street number')


    _ElementMap = {
        __PremiseNumberRangeFrom.name() : __PremiseNumberRangeFrom,
        __PremiseNumberRangeTo.name() : __PremiseNumberRangeTo
    }
    _AttributeMap = {
        __Separator.name() : __Separator,
        __RangeType.name() : __RangeType,
        __Type.name() : __Type,
        __Indicator.name() : __Indicator,
        __NumberRangeOccurence.name() : __NumberRangeOccurence,
        __IndicatorOccurence.name() : __IndicatorOccurence
    }



# Complex type MailStopType with content type ELEMENT_ONLY
class MailStopType (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'MailStopType')
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}MailStopName uses Python identifier MailStopName
    __MailStopName = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'MailStopName'), 'MailStopName', '__urnoasisnamestcciqxsdschemaxAL2_0_MailStopType_urnoasisnamestcciqxsdschemaxAL2_0MailStopName', False)

    
    MailStopName = property(__MailStopName.value, __MailStopName.set, None, u'Name of the the Mail Stop. eg. MSP, MS, etc')

    
    # Element {urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}AddressLine uses Python identifier AddressLine
    __AddressLine = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'AddressLine'), 'AddressLine', '__urnoasisnamestcciqxsdschemaxAL2_0_MailStopType_urnoasisnamestcciqxsdschemaxAL2_0AddressLine', True)

    
    AddressLine = property(__AddressLine.value, __AddressLine.set, None, u'Free format address representation. An address can have more than one line. The order of the AddressLine elements must be preserved.')

    
    # Element {urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}MailStopNumber uses Python identifier MailStopNumber
    __MailStopNumber = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'MailStopNumber'), 'MailStopNumber', '__urnoasisnamestcciqxsdschemaxAL2_0_MailStopType_urnoasisnamestcciqxsdschemaxAL2_0MailStopNumber', False)

    
    MailStopNumber = property(__MailStopNumber.value, __MailStopNumber.set, None, u'Number of the Mail stop. eg. 123 in MS 123')

    
    # Attribute Type uses Python identifier Type
    __Type = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Type'), 'Type', '__urnoasisnamestcciqxsdschemaxAL2_0_MailStopType_Type', pyxb.binding.datatypes.anySimpleType)
    
    Type = property(__Type.value, __Type.set, None, None)

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_strict, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'urn:oasis:names:tc:ciq:xsdschema:xAL:2.0'))
    _HasWildcardElement = True

    _ElementMap = {
        __MailStopName.name() : __MailStopName,
        __AddressLine.name() : __AddressLine,
        __MailStopNumber.name() : __MailStopNumber
    }
    _AttributeMap = {
        __Type.name() : __Type
    }
Namespace.addCategoryObject('typeBinding', u'MailStopType', MailStopType)


# Complex type CTD_ANON_22 with content type MIXED
class CTD_ANON_22 (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_MIXED
    _Abstract = False
    _ExpandedName = None
    # Base type is pyxb.binding.datatypes.anyType
    
    # Attribute Code uses Python identifier Code
    __Code = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Code'), 'Code', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_22_Code', pyxb.binding.datatypes.anySimpleType)
    
    Code = property(__Code.value, __Code.set, None, u'Used by postal services to encode the name of the element.')

    
    # Attribute Type uses Python identifier Type
    __Type = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Type'), 'Type', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_22_Type', pyxb.binding.datatypes.anySimpleType)
    
    Type = property(__Type.value, __Type.set, None, None)

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_strict, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'urn:oasis:names:tc:ciq:xsdschema:xAL:2.0'))

    _ElementMap = {
        
    }
    _AttributeMap = {
        __Code.name() : __Code,
        __Type.name() : __Type
    }



# Complex type CTD_ANON_23 with content type ELEMENT_ONLY
class CTD_ANON_23 (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = None
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}PostTownSuffix uses Python identifier PostTownSuffix
    __PostTownSuffix = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'PostTownSuffix'), 'PostTownSuffix', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_23_urnoasisnamestcciqxsdschemaxAL2_0PostTownSuffix', False)

    
    PostTownSuffix = property(__PostTownSuffix.value, __PostTownSuffix.set, None, u'GENERAL PO in MIAMI GENERAL PO')

    
    # Element {urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}AddressLine uses Python identifier AddressLine
    __AddressLine = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'AddressLine'), 'AddressLine', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_23_urnoasisnamestcciqxsdschemaxAL2_0AddressLine', True)

    
    AddressLine = property(__AddressLine.value, __AddressLine.set, None, u'Free format address representation. An address can have more than one line. The order of the AddressLine elements must be preserved.')

    
    # Element {urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}PostTownName uses Python identifier PostTownName
    __PostTownName = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'PostTownName'), 'PostTownName', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_23_urnoasisnamestcciqxsdschemaxAL2_0PostTownName', True)

    
    PostTownName = property(__PostTownName.value, __PostTownName.set, None, u'Name of the post town')

    
    # Attribute Type uses Python identifier Type
    __Type = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Type'), 'Type', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_23_Type', pyxb.binding.datatypes.anySimpleType)
    
    Type = property(__Type.value, __Type.set, None, u'eg. village, town, suburb, etc')

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_strict, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'urn:oasis:names:tc:ciq:xsdschema:xAL:2.0'))

    _ElementMap = {
        __PostTownSuffix.name() : __PostTownSuffix,
        __AddressLine.name() : __AddressLine,
        __PostTownName.name() : __PostTownName
    }
    _AttributeMap = {
        __Type.name() : __Type
    }



# Complex type CTD_ANON_24 with content type ELEMENT_ONLY
class CTD_ANON_24 (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = None
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}AddressDetails uses Python identifier AddressDetails
    __AddressDetails = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'AddressDetails'), 'AddressDetails', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_24_urnoasisnamestcciqxsdschemaxAL2_0AddressDetails', True)

    
    AddressDetails = property(__AddressDetails.value, __AddressDetails.set, None, u'This container defines the details of the address. Can define multiple addresses including tracking address history')

    
    # Attribute Version uses Python identifier Version
    __Version = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Version'), 'Version', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_24_Version', pyxb.binding.datatypes.anySimpleType)
    
    Version = property(__Version.value, __Version.set, None, u'Specific to DTD to specify the version number of DTD')

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_strict, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'urn:oasis:names:tc:ciq:xsdschema:xAL:2.0'))
    _HasWildcardElement = True

    _ElementMap = {
        __AddressDetails.name() : __AddressDetails
    }
    _AttributeMap = {
        __Version.name() : __Version
    }



# Complex type CTD_ANON_25 with content type MIXED
class CTD_ANON_25 (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_MIXED
    _Abstract = False
    _ExpandedName = None
    # Base type is pyxb.binding.datatypes.anyType
    
    # Attribute Code uses Python identifier Code
    __Code = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Code'), 'Code', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_25_Code', pyxb.binding.datatypes.string)
    
    Code = property(__Code.value, __Code.set, None, None)

    
    # Attribute Type uses Python identifier Type
    __Type = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Type'), 'Type', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_25_Type', pyxb.binding.datatypes.string)
    
    Type = property(__Type.value, __Type.set, None, u'Airport, Hospital, etc')

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_strict, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'urn:oasis:names:tc:ciq:xsdschema:xAL:2.0'))

    _ElementMap = {
        
    }
    _AttributeMap = {
        __Code.name() : __Code,
        __Type.name() : __Type
    }



# Complex type CTD_ANON_26 with content type MIXED
class CTD_ANON_26 (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_MIXED
    _Abstract = False
    _ExpandedName = None
    # Base type is pyxb.binding.datatypes.anyType
    
    # Attribute Code uses Python identifier Code
    __Code = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Code'), 'Code', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_26_Code', pyxb.binding.datatypes.anySimpleType)
    
    Code = property(__Code.value, __Code.set, None, u'Used by postal services to encode the name of the element.')

    
    # Attribute NumberPrefixSeparator uses Python identifier NumberPrefixSeparator
    __NumberPrefixSeparator = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'NumberPrefixSeparator'), 'NumberPrefixSeparator', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_26_NumberPrefixSeparator', pyxb.binding.datatypes.anySimpleType)
    
    NumberPrefixSeparator = property(__NumberPrefixSeparator.value, __NumberPrefixSeparator.set, None, u'A-12 where 12 is number and A is prefix and "-" is the separator')

    
    # Attribute Type uses Python identifier Type
    __Type = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Type'), 'Type', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_26_Type', pyxb.binding.datatypes.anySimpleType)
    
    Type = property(__Type.value, __Type.set, None, None)

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_strict, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'urn:oasis:names:tc:ciq:xsdschema:xAL:2.0'))

    _ElementMap = {
        
    }
    _AttributeMap = {
        __Code.name() : __Code,
        __NumberPrefixSeparator.name() : __NumberPrefixSeparator,
        __Type.name() : __Type
    }



# Complex type CTD_ANON_27 with content type MIXED
class CTD_ANON_27 (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_MIXED
    _Abstract = False
    _ExpandedName = None
    # Base type is pyxb.binding.datatypes.anyType
    
    # Attribute IndicatorOccurrence uses Python identifier IndicatorOccurrence
    __IndicatorOccurrence = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'IndicatorOccurrence'), 'IndicatorOccurrence', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_27_IndicatorOccurrence', STD_ANON_12)
    
    IndicatorOccurrence = property(__IndicatorOccurrence.value, __IndicatorOccurrence.set, None, u'No. occurs before 12 No.12')

    
    # Attribute NumberTypeOccurrence uses Python identifier NumberTypeOccurrence
    __NumberTypeOccurrence = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'NumberTypeOccurrence'), 'NumberTypeOccurrence', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_27_NumberTypeOccurrence', STD_ANON_13)
    
    NumberTypeOccurrence = property(__NumberTypeOccurrence.value, __NumberTypeOccurrence.set, None, u'12 in BUILDING 12 occurs "after" premise type BUILDING')

    
    # Attribute Type uses Python identifier Type
    __Type = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Type'), 'Type', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_27_Type', pyxb.binding.datatypes.anySimpleType)
    
    Type = property(__Type.value, __Type.set, None, None)

    
    # Attribute Code uses Python identifier Code
    __Code = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Code'), 'Code', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_27_Code', pyxb.binding.datatypes.anySimpleType)
    
    Code = property(__Code.value, __Code.set, None, u'Used by postal services to encode the name of the element.')

    
    # Attribute Indicator uses Python identifier Indicator
    __Indicator = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Indicator'), 'Indicator', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_27_Indicator', pyxb.binding.datatypes.anySimpleType)
    
    Indicator = property(__Indicator.value, __Indicator.set, None, u'No. in House No.12, # in #12, etc.')

    
    # Attribute NumberType uses Python identifier NumberType
    __NumberType = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'NumberType'), 'NumberType', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_27_NumberType', STD_ANON_11)
    
    NumberType = property(__NumberType.value, __NumberType.set, None, u'Building 12-14 is "Range" and Building 12 is "Single"')

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_strict, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'urn:oasis:names:tc:ciq:xsdschema:xAL:2.0'))

    _ElementMap = {
        
    }
    _AttributeMap = {
        __IndicatorOccurrence.name() : __IndicatorOccurrence,
        __NumberTypeOccurrence.name() : __NumberTypeOccurrence,
        __Type.name() : __Type,
        __Code.name() : __Code,
        __Indicator.name() : __Indicator,
        __NumberType.name() : __NumberType
    }



# Complex type CTD_ANON_28 with content type MIXED
class CTD_ANON_28 (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_MIXED
    _Abstract = False
    _ExpandedName = None
    # Base type is pyxb.binding.datatypes.anyType
    
    # Attribute Code uses Python identifier Code
    __Code = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Code'), 'Code', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_28_Code', pyxb.binding.datatypes.anySimpleType)
    
    Code = property(__Code.value, __Code.set, None, u'Used by postal services to encode the name of the element.')

    
    # Attribute Type uses Python identifier Type
    __Type = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Type'), 'Type', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_28_Type', pyxb.binding.datatypes.anySimpleType)
    
    Type = property(__Type.value, __Type.set, None, None)

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_strict, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'urn:oasis:names:tc:ciq:xsdschema:xAL:2.0'))

    _ElementMap = {
        
    }
    _AttributeMap = {
        __Code.name() : __Code,
        __Type.name() : __Type
    }



# Complex type CTD_ANON_29 with content type ELEMENT_ONLY
class CTD_ANON_29 (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = None
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}AddressLongitude uses Python identifier AddressLongitude
    __AddressLongitude = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'AddressLongitude'), 'AddressLongitude', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_29_urnoasisnamestcciqxsdschemaxAL2_0AddressLongitude', False)

    
    AddressLongitude = property(__AddressLongitude.value, __AddressLongitude.set, None, u'Longtitude of delivery address')

    
    # Element {urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}AddressLongitudeDirection uses Python identifier AddressLongitudeDirection
    __AddressLongitudeDirection = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'AddressLongitudeDirection'), 'AddressLongitudeDirection', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_29_urnoasisnamestcciqxsdschemaxAL2_0AddressLongitudeDirection', False)

    
    AddressLongitudeDirection = property(__AddressLongitudeDirection.value, __AddressLongitudeDirection.set, None, u'Longtitude direction of delivery address;N=North and S=South')

    
    # Element {urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}SupplementaryPostalServiceData uses Python identifier SupplementaryPostalServiceData
    __SupplementaryPostalServiceData = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'SupplementaryPostalServiceData'), 'SupplementaryPostalServiceData', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_29_urnoasisnamestcciqxsdschemaxAL2_0SupplementaryPostalServiceData', True)

    
    SupplementaryPostalServiceData = property(__SupplementaryPostalServiceData.value, __SupplementaryPostalServiceData.set, None, u'any postal service elements not covered by the container can be represented using this element')

    
    # Element {urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}SortingCode uses Python identifier SortingCode
    __SortingCode = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'SortingCode'), 'SortingCode', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_29_urnoasisnamestcciqxsdschemaxAL2_0SortingCode', False)

    
    SortingCode = property(__SortingCode.value, __SortingCode.set, None, u'Used for sorting addresses. Values may for example be CEDEX 16 (France)')

    
    # Element {urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}EndorsementLineCode uses Python identifier EndorsementLineCode
    __EndorsementLineCode = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'EndorsementLineCode'), 'EndorsementLineCode', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_29_urnoasisnamestcciqxsdschemaxAL2_0EndorsementLineCode', False)

    
    EndorsementLineCode = property(__EndorsementLineCode.value, __EndorsementLineCode.set, None, u'Directly affects postal service distribution')

    
    # Element {urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}KeyLineCode uses Python identifier KeyLineCode
    __KeyLineCode = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'KeyLineCode'), 'KeyLineCode', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_29_urnoasisnamestcciqxsdschemaxAL2_0KeyLineCode', False)

    
    KeyLineCode = property(__KeyLineCode.value, __KeyLineCode.set, None, u'Required for some postal services')

    
    # Element {urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}AddressLatitude uses Python identifier AddressLatitude
    __AddressLatitude = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'AddressLatitude'), 'AddressLatitude', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_29_urnoasisnamestcciqxsdschemaxAL2_0AddressLatitude', False)

    
    AddressLatitude = property(__AddressLatitude.value, __AddressLatitude.set, None, u'Latitude of delivery address')

    
    # Element {urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}Barcode uses Python identifier Barcode
    __Barcode = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'Barcode'), 'Barcode', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_29_urnoasisnamestcciqxsdschemaxAL2_0Barcode', False)

    
    Barcode = property(__Barcode.value, __Barcode.set, None, u'Required for some postal services')

    
    # Element {urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}AddressIdentifier uses Python identifier AddressIdentifier
    __AddressIdentifier = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'AddressIdentifier'), 'AddressIdentifier', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_29_urnoasisnamestcciqxsdschemaxAL2_0AddressIdentifier', True)

    
    AddressIdentifier = property(__AddressIdentifier.value, __AddressIdentifier.set, None, u'A unique identifier of an address assigned by postal authorities. Example: DPID in Australia')

    
    # Element {urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}AddressLatitudeDirection uses Python identifier AddressLatitudeDirection
    __AddressLatitudeDirection = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'AddressLatitudeDirection'), 'AddressLatitudeDirection', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_29_urnoasisnamestcciqxsdschemaxAL2_0AddressLatitudeDirection', False)

    
    AddressLatitudeDirection = property(__AddressLatitudeDirection.value, __AddressLatitudeDirection.set, None, u'Latitude direction of delivery address;N = North and S = South')

    
    # Attribute Type uses Python identifier Type
    __Type = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Type'), 'Type', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_29_Type', pyxb.binding.datatypes.anySimpleType)
    
    Type = property(__Type.value, __Type.set, None, u'USPS, ECMA, UN/PROLIST, etc')

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_strict, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'urn:oasis:names:tc:ciq:xsdschema:xAL:2.0'))
    _HasWildcardElement = True

    _ElementMap = {
        __AddressLongitude.name() : __AddressLongitude,
        __AddressLongitudeDirection.name() : __AddressLongitudeDirection,
        __SupplementaryPostalServiceData.name() : __SupplementaryPostalServiceData,
        __SortingCode.name() : __SortingCode,
        __EndorsementLineCode.name() : __EndorsementLineCode,
        __KeyLineCode.name() : __KeyLineCode,
        __AddressLatitude.name() : __AddressLatitude,
        __Barcode.name() : __Barcode,
        __AddressIdentifier.name() : __AddressIdentifier,
        __AddressLatitudeDirection.name() : __AddressLatitudeDirection
    }
    _AttributeMap = {
        __Type.name() : __Type
    }



# Complex type CTD_ANON_30 with content type MIXED
class CTD_ANON_30 (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_MIXED
    _Abstract = False
    _ExpandedName = None
    # Base type is pyxb.binding.datatypes.anyType
    
    # Attribute Code uses Python identifier Code
    __Code = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Code'), 'Code', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_30_Code', pyxb.binding.datatypes.anySimpleType)
    
    Code = property(__Code.value, __Code.set, None, u'Used by postal services to encode the name of the element.')

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_strict, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'urn:oasis:names:tc:ciq:xsdschema:xAL:2.0'))

    _ElementMap = {
        
    }
    _AttributeMap = {
        __Code.name() : __Code
    }



# Complex type CTD_ANON_31 with content type MIXED
class CTD_ANON_31 (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_MIXED
    _Abstract = False
    _ExpandedName = None
    # Base type is pyxb.binding.datatypes.anyType
    
    # Attribute NumberSuffixSeparator uses Python identifier NumberSuffixSeparator
    __NumberSuffixSeparator = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'NumberSuffixSeparator'), 'NumberSuffixSeparator', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_31_NumberSuffixSeparator', pyxb.binding.datatypes.anySimpleType)
    
    NumberSuffixSeparator = property(__NumberSuffixSeparator.value, __NumberSuffixSeparator.set, None, u'12-A where 12 is number and A is suffix and "-" is the separator')

    
    # Attribute Type uses Python identifier Type
    __Type = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Type'), 'Type', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_31_Type', pyxb.binding.datatypes.anySimpleType)
    
    Type = property(__Type.value, __Type.set, None, None)

    
    # Attribute Code uses Python identifier Code
    __Code = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Code'), 'Code', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_31_Code', pyxb.binding.datatypes.anySimpleType)
    
    Code = property(__Code.value, __Code.set, None, u'Used by postal services to encode the name of the element.')

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_strict, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'urn:oasis:names:tc:ciq:xsdschema:xAL:2.0'))

    _ElementMap = {
        
    }
    _AttributeMap = {
        __NumberSuffixSeparator.name() : __NumberSuffixSeparator,
        __Type.name() : __Type,
        __Code.name() : __Code
    }



# Complex type CTD_ANON_32 with content type SIMPLE
class CTD_ANON_32 (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = pyxb.binding.datatypes.string
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_SIMPLE
    _Abstract = False
    _ExpandedName = None
    # Base type is pyxb.binding.datatypes.string
    
    # Attribute Code uses Python identifier Code
    __Code = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Code'), 'Code', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_32_Code', pyxb.binding.datatypes.anySimpleType)
    
    Code = property(__Code.value, __Code.set, None, u'Used by postal services to encode the name of the element.')

    
    # Attribute NumberPrefixSeparator uses Python identifier NumberPrefixSeparator
    __NumberPrefixSeparator = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'NumberPrefixSeparator'), 'NumberPrefixSeparator', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_32_NumberPrefixSeparator', pyxb.binding.datatypes.anySimpleType)
    
    NumberPrefixSeparator = property(__NumberPrefixSeparator.value, __NumberPrefixSeparator.set, None, u'A-12 where 12 is number and A is prefix and "-" is the separator')

    
    # Attribute Type uses Python identifier Type
    __Type = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Type'), 'Type', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_32_Type', pyxb.binding.datatypes.anySimpleType)
    
    Type = property(__Type.value, __Type.set, None, None)

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_strict, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'urn:oasis:names:tc:ciq:xsdschema:xAL:2.0'))

    _ElementMap = {
        
    }
    _AttributeMap = {
        __Code.name() : __Code,
        __NumberPrefixSeparator.name() : __NumberPrefixSeparator,
        __Type.name() : __Type
    }



# Complex type CTD_ANON_33 with content type MIXED
class CTD_ANON_33 (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_MIXED
    _Abstract = False
    _ExpandedName = None
    # Base type is pyxb.binding.datatypes.anyType
    
    # Attribute Code uses Python identifier Code
    __Code = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Code'), 'Code', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_33_Code', pyxb.binding.datatypes.anySimpleType)
    
    Code = property(__Code.value, __Code.set, None, u'Used by postal services to encode the name of the element.')

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_strict, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'urn:oasis:names:tc:ciq:xsdschema:xAL:2.0'))

    _ElementMap = {
        
    }
    _AttributeMap = {
        __Code.name() : __Code
    }



# Complex type CTD_ANON_34 with content type MIXED
class CTD_ANON_34 (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_MIXED
    _Abstract = False
    _ExpandedName = None
    # Base type is pyxb.binding.datatypes.anyType
    
    # Attribute Type uses Python identifier Type
    __Type = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Type'), 'Type', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_34_Type', pyxb.binding.datatypes.anySimpleType)
    
    Type = property(__Type.value, __Type.set, None, None)

    
    # Attribute NumberSuffixSeparator uses Python identifier NumberSuffixSeparator
    __NumberSuffixSeparator = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'NumberSuffixSeparator'), 'NumberSuffixSeparator', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_34_NumberSuffixSeparator', pyxb.binding.datatypes.anySimpleType)
    
    NumberSuffixSeparator = property(__NumberSuffixSeparator.value, __NumberSuffixSeparator.set, None, u'12-A where 12 is number and A is suffix and "-" is the separator')

    
    # Attribute Code uses Python identifier Code
    __Code = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Code'), 'Code', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_34_Code', pyxb.binding.datatypes.anySimpleType)
    
    Code = property(__Code.value, __Code.set, None, u'Used by postal services to encode the name of the element.')

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_strict, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'urn:oasis:names:tc:ciq:xsdschema:xAL:2.0'))

    _ElementMap = {
        
    }
    _AttributeMap = {
        __Type.name() : __Type,
        __NumberSuffixSeparator.name() : __NumberSuffixSeparator,
        __Code.name() : __Code
    }



# Complex type CTD_ANON_35 with content type MIXED
class CTD_ANON_35 (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_MIXED
    _Abstract = False
    _ExpandedName = None
    # Base type is pyxb.binding.datatypes.anyType
    
    # Attribute NumberExtensionSeparator uses Python identifier NumberExtensionSeparator
    __NumberExtensionSeparator = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'NumberExtensionSeparator'), 'NumberExtensionSeparator', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_35_NumberExtensionSeparator', pyxb.binding.datatypes.anySimpleType)
    
    NumberExtensionSeparator = property(__NumberExtensionSeparator.value, __NumberExtensionSeparator.set, None, u'"-" is the NumberExtensionSeparator in POBOX:12345-123')

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_strict, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'urn:oasis:names:tc:ciq:xsdschema:xAL:2.0'))

    _ElementMap = {
        
    }
    _AttributeMap = {
        __NumberExtensionSeparator.name() : __NumberExtensionSeparator
    }



# Complex type CTD_ANON_36 with content type MIXED
class CTD_ANON_36 (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_MIXED
    _Abstract = False
    _ExpandedName = None
    # Base type is pyxb.binding.datatypes.anyType
    
    # Attribute Type uses Python identifier Type
    __Type = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Type'), 'Type', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_36_Type', pyxb.binding.datatypes.anySimpleType)
    
    Type = property(__Type.value, __Type.set, None, None)

    
    # Attribute Code uses Python identifier Code
    __Code = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Code'), 'Code', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_36_Code', pyxb.binding.datatypes.anySimpleType)
    
    Code = property(__Code.value, __Code.set, None, u'Used by postal services to encode the name of the element.')

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_strict, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'urn:oasis:names:tc:ciq:xsdschema:xAL:2.0'))

    _ElementMap = {
        
    }
    _AttributeMap = {
        __Type.name() : __Type,
        __Code.name() : __Code
    }



# Complex type LargeMailUserType with content type ELEMENT_ONLY
class LargeMailUserType (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'LargeMailUserType')
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}Thoroughfare uses Python identifier Thoroughfare
    __Thoroughfare = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'Thoroughfare'), 'Thoroughfare', '__urnoasisnamestcciqxsdschemaxAL2_0_LargeMailUserType_urnoasisnamestcciqxsdschemaxAL2_0Thoroughfare', False)

    
    Thoroughfare = property(__Thoroughfare.value, __Thoroughfare.set, None, u'Specification of a thoroughfare. A thoroughfare could be a rd, street, canal, river, etc.  Note dependentlocality in a street. For example, in some countries, a large street will \nhave many subdivisions with numbers. Normally the subdivision name is the same as the road name, but with a number to identifiy it. Eg. SOI SUKUMVIT 3, SUKUMVIT RD, BANGKOK')

    
    # Element {urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}BuildingName uses Python identifier BuildingName
    __BuildingName = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'BuildingName'), 'BuildingName', '__urnoasisnamestcciqxsdschemaxAL2_0_LargeMailUserType_urnoasisnamestcciqxsdschemaxAL2_0BuildingName', True)

    
    BuildingName = property(__BuildingName.value, __BuildingName.set, None, u'Name of the building')

    
    # Element {urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}LargeMailUserName uses Python identifier LargeMailUserName
    __LargeMailUserName = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'LargeMailUserName'), 'LargeMailUserName', '__urnoasisnamestcciqxsdschemaxAL2_0_LargeMailUserType_urnoasisnamestcciqxsdschemaxAL2_0LargeMailUserName', True)

    
    LargeMailUserName = property(__LargeMailUserName.value, __LargeMailUserName.set, None, u'Name of the large mail user. eg. Smith Ford International airport')

    
    # Element {urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}Department uses Python identifier Department
    __Department = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'Department'), 'Department', '__urnoasisnamestcciqxsdschemaxAL2_0_LargeMailUserType_urnoasisnamestcciqxsdschemaxAL2_0Department', False)

    
    Department = property(__Department.value, __Department.set, None, u'Subdivision in the firm: School of Physics at Victoria University (School of Physics is the department)')

    
    # Element {urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}PostalCode uses Python identifier PostalCode
    __PostalCode = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'PostalCode'), 'PostalCode', '__urnoasisnamestcciqxsdschemaxAL2_0_LargeMailUserType_urnoasisnamestcciqxsdschemaxAL2_0PostalCode', False)

    
    PostalCode = property(__PostalCode.value, __PostalCode.set, None, u'PostalCode is the container element for either simple or complex (extended) postal codes. Type: Area Code, Postcode, etc.')

    
    # Element {urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}AddressLine uses Python identifier AddressLine
    __AddressLine = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'AddressLine'), 'AddressLine', '__urnoasisnamestcciqxsdschemaxAL2_0_LargeMailUserType_urnoasisnamestcciqxsdschemaxAL2_0AddressLine', True)

    
    AddressLine = property(__AddressLine.value, __AddressLine.set, None, u'Free format address representation. An address can have more than one line. The order of the AddressLine elements must be preserved.')

    
    # Element {urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}PostBox uses Python identifier PostBox
    __PostBox = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'PostBox'), 'PostBox', '__urnoasisnamestcciqxsdschemaxAL2_0_LargeMailUserType_urnoasisnamestcciqxsdschemaxAL2_0PostBox', False)

    
    PostBox = property(__PostBox.value, __PostBox.set, None, u'Specification of a postbox like mail delivery point. Only a single postbox number can be specified. Examples of postboxes are POBox, free mail numbers, etc.')

    
    # Element {urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}LargeMailUserIdentifier uses Python identifier LargeMailUserIdentifier
    __LargeMailUserIdentifier = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'LargeMailUserIdentifier'), 'LargeMailUserIdentifier', '__urnoasisnamestcciqxsdschemaxAL2_0_LargeMailUserType_urnoasisnamestcciqxsdschemaxAL2_0LargeMailUserIdentifier', False)

    
    LargeMailUserIdentifier = property(__LargeMailUserIdentifier.value, __LargeMailUserIdentifier.set, None, u'Specification of the identification number of a large mail user. An example are the Cedex codes in France.')

    
    # Attribute Type uses Python identifier Type
    __Type = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Type'), 'Type', '__urnoasisnamestcciqxsdschemaxAL2_0_LargeMailUserType_Type', pyxb.binding.datatypes.string)
    
    Type = property(__Type.value, __Type.set, None, None)

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_strict, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'urn:oasis:names:tc:ciq:xsdschema:xAL:2.0'))
    _HasWildcardElement = True

    _ElementMap = {
        __Thoroughfare.name() : __Thoroughfare,
        __BuildingName.name() : __BuildingName,
        __LargeMailUserName.name() : __LargeMailUserName,
        __Department.name() : __Department,
        __PostalCode.name() : __PostalCode,
        __AddressLine.name() : __AddressLine,
        __PostBox.name() : __PostBox,
        __LargeMailUserIdentifier.name() : __LargeMailUserIdentifier
    }
    _AttributeMap = {
        __Type.name() : __Type
    }
Namespace.addCategoryObject('typeBinding', u'LargeMailUserType', LargeMailUserType)


# Complex type AddressDetails_ with content type ELEMENT_ONLY
class AddressDetails_ (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'AddressDetails')
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}Address uses Python identifier Address
    __Address = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'Address'), 'Address', '__urnoasisnamestcciqxsdschemaxAL2_0_AddressDetails__urnoasisnamestcciqxsdschemaxAL2_0Address', False)

    
    Address = property(__Address.value, __Address.set, None, u'Address as one line of free text')

    
    # Element {urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}AddressLines uses Python identifier AddressLines
    __AddressLines = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'AddressLines'), 'AddressLines', '__urnoasisnamestcciqxsdschemaxAL2_0_AddressDetails__urnoasisnamestcciqxsdschemaxAL2_0AddressLines', False)

    
    AddressLines = property(__AddressLines.value, __AddressLines.set, None, u'Container for Address lines')

    
    # Element {urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}AdministrativeArea uses Python identifier AdministrativeArea
    __AdministrativeArea = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'AdministrativeArea'), 'AdministrativeArea', '__urnoasisnamestcciqxsdschemaxAL2_0_AddressDetails__urnoasisnamestcciqxsdschemaxAL2_0AdministrativeArea', False)

    
    AdministrativeArea = property(__AdministrativeArea.value, __AdministrativeArea.set, None, u'Examples of administrative areas are provinces counties, special regions (such as "Rijnmond"), etc.')

    
    # Element {urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}Locality uses Python identifier Locality
    __Locality = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'Locality'), 'Locality', '__urnoasisnamestcciqxsdschemaxAL2_0_AddressDetails__urnoasisnamestcciqxsdschemaxAL2_0Locality', False)

    
    Locality = property(__Locality.value, __Locality.set, None, u'Locality is one level lower than adminisstrative area. Eg.: cities, reservations and any other built-up areas.')

    
    # Element {urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}PostalServiceElements uses Python identifier PostalServiceElements
    __PostalServiceElements = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'PostalServiceElements'), 'PostalServiceElements', '__urnoasisnamestcciqxsdschemaxAL2_0_AddressDetails__urnoasisnamestcciqxsdschemaxAL2_0PostalServiceElements', False)

    
    PostalServiceElements = property(__PostalServiceElements.value, __PostalServiceElements.set, None, u'Postal authorities use specific postal service data to expedient delivery of mail')

    
    # Element {urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}Country uses Python identifier Country
    __Country = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'Country'), 'Country', '__urnoasisnamestcciqxsdschemaxAL2_0_AddressDetails__urnoasisnamestcciqxsdschemaxAL2_0Country', False)

    
    Country = property(__Country.value, __Country.set, None, u'Specification of a country')

    
    # Element {urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}Thoroughfare uses Python identifier Thoroughfare
    __Thoroughfare = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'Thoroughfare'), 'Thoroughfare', '__urnoasisnamestcciqxsdschemaxAL2_0_AddressDetails__urnoasisnamestcciqxsdschemaxAL2_0Thoroughfare', False)

    
    Thoroughfare = property(__Thoroughfare.value, __Thoroughfare.set, None, u'Specification of a thoroughfare. A thoroughfare could be a rd, street, canal, river, etc.  Note dependentlocality in a street. For example, in some countries, a large street will \nhave many subdivisions with numbers. Normally the subdivision name is the same as the road name, but with a number to identifiy it. Eg. SOI SUKUMVIT 3, SUKUMVIT RD, BANGKOK')

    
    # Attribute ValidToDate uses Python identifier ValidToDate
    __ValidToDate = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'ValidToDate'), 'ValidToDate', '__urnoasisnamestcciqxsdschemaxAL2_0_AddressDetails__ValidToDate', pyxb.binding.datatypes.anySimpleType)
    
    ValidToDate = property(__ValidToDate.value, __ValidToDate.set, None, u'End date of the validity of address')

    
    # Attribute Code uses Python identifier Code
    __Code = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Code'), 'Code', '__urnoasisnamestcciqxsdschemaxAL2_0_AddressDetails__Code', pyxb.binding.datatypes.anySimpleType)
    
    Code = property(__Code.value, __Code.set, None, u'Used by postal services to encode the name of the element.')

    
    # Attribute CurrentStatus uses Python identifier CurrentStatus
    __CurrentStatus = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'CurrentStatus'), 'CurrentStatus', '__urnoasisnamestcciqxsdschemaxAL2_0_AddressDetails__CurrentStatus', pyxb.binding.datatypes.anySimpleType)
    
    CurrentStatus = property(__CurrentStatus.value, __CurrentStatus.set, None, u'Moved, Living, Investment, Deceased, etc..')

    
    # Attribute Usage uses Python identifier Usage
    __Usage = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Usage'), 'Usage', '__urnoasisnamestcciqxsdschemaxAL2_0_AddressDetails__Usage', pyxb.binding.datatypes.anySimpleType)
    
    Usage = property(__Usage.value, __Usage.set, None, u'Communication, Contact, etc.')

    
    # Attribute ValidFromDate uses Python identifier ValidFromDate
    __ValidFromDate = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'ValidFromDate'), 'ValidFromDate', '__urnoasisnamestcciqxsdschemaxAL2_0_AddressDetails__ValidFromDate', pyxb.binding.datatypes.anySimpleType)
    
    ValidFromDate = property(__ValidFromDate.value, __ValidFromDate.set, None, u'Start Date of the validity of address')

    
    # Attribute AddressDetailsKey uses Python identifier AddressDetailsKey
    __AddressDetailsKey = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'AddressDetailsKey'), 'AddressDetailsKey', '__urnoasisnamestcciqxsdschemaxAL2_0_AddressDetails__AddressDetailsKey', pyxb.binding.datatypes.anySimpleType)
    
    AddressDetailsKey = property(__AddressDetailsKey.value, __AddressDetailsKey.set, None, u'Key identifier for the element for not reinforced references from other elements. Not required to be unique for the document to be valid, but application may get confused if not unique. Extend this schema adding unique contraint if needed.')

    
    # Attribute AddressType uses Python identifier AddressType
    __AddressType = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'AddressType'), 'AddressType', '__urnoasisnamestcciqxsdschemaxAL2_0_AddressDetails__AddressType', pyxb.binding.datatypes.anySimpleType)
    
    AddressType = property(__AddressType.value, __AddressType.set, None, u'Type of address. Example: Postal, residential,business, primary, secondary, etc')

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_strict, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'urn:oasis:names:tc:ciq:xsdschema:xAL:2.0'))
    _HasWildcardElement = True

    _ElementMap = {
        __Address.name() : __Address,
        __AddressLines.name() : __AddressLines,
        __AdministrativeArea.name() : __AdministrativeArea,
        __Locality.name() : __Locality,
        __PostalServiceElements.name() : __PostalServiceElements,
        __Country.name() : __Country,
        __Thoroughfare.name() : __Thoroughfare
    }
    _AttributeMap = {
        __ValidToDate.name() : __ValidToDate,
        __Code.name() : __Code,
        __CurrentStatus.name() : __CurrentStatus,
        __Usage.name() : __Usage,
        __ValidFromDate.name() : __ValidFromDate,
        __AddressDetailsKey.name() : __AddressDetailsKey,
        __AddressType.name() : __AddressType
    }
Namespace.addCategoryObject('typeBinding', u'AddressDetails', AddressDetails_)


# Complex type BuildingNameType with content type MIXED
class BuildingNameType (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_MIXED
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'BuildingNameType')
    # Base type is pyxb.binding.datatypes.anyType
    
    # Attribute Type uses Python identifier Type
    __Type = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Type'), 'Type', '__urnoasisnamestcciqxsdschemaxAL2_0_BuildingNameType_Type', pyxb.binding.datatypes.anySimpleType)
    
    Type = property(__Type.value, __Type.set, None, None)

    
    # Attribute TypeOccurrence uses Python identifier TypeOccurrence
    __TypeOccurrence = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'TypeOccurrence'), 'TypeOccurrence', '__urnoasisnamestcciqxsdschemaxAL2_0_BuildingNameType_TypeOccurrence', STD_ANON_14)
    
    TypeOccurrence = property(__TypeOccurrence.value, __TypeOccurrence.set, None, u'Occurrence of the building name before/after the type. eg. EGIS BUILDING where name appears before type')

    
    # Attribute Code uses Python identifier Code
    __Code = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Code'), 'Code', '__urnoasisnamestcciqxsdschemaxAL2_0_BuildingNameType_Code', pyxb.binding.datatypes.anySimpleType)
    
    Code = property(__Code.value, __Code.set, None, u'Used by postal services to encode the name of the element.')

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_strict, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'urn:oasis:names:tc:ciq:xsdschema:xAL:2.0'))

    _ElementMap = {
        
    }
    _AttributeMap = {
        __Type.name() : __Type,
        __TypeOccurrence.name() : __TypeOccurrence,
        __Code.name() : __Code
    }
Namespace.addCategoryObject('typeBinding', u'BuildingNameType', BuildingNameType)


# Complex type CTD_ANON_37 with content type MIXED
class CTD_ANON_37 (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_MIXED
    _Abstract = False
    _ExpandedName = None
    # Base type is pyxb.binding.datatypes.anyType
    
    # Attribute NumberSuffixSeparator uses Python identifier NumberSuffixSeparator
    __NumberSuffixSeparator = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'NumberSuffixSeparator'), 'NumberSuffixSeparator', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_37_NumberSuffixSeparator', pyxb.binding.datatypes.anySimpleType)
    
    NumberSuffixSeparator = property(__NumberSuffixSeparator.value, __NumberSuffixSeparator.set, None, u'NEAR, ADJACENT TO, etc12-A where 12 is number and A is suffix and "-" is the separator')

    
    # Attribute Code uses Python identifier Code
    __Code = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Code'), 'Code', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_37_Code', pyxb.binding.datatypes.anySimpleType)
    
    Code = property(__Code.value, __Code.set, None, u'Used by postal services to encode the name of the element.')

    
    # Attribute Type uses Python identifier Type
    __Type = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Type'), 'Type', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_37_Type', pyxb.binding.datatypes.anySimpleType)
    
    Type = property(__Type.value, __Type.set, None, None)

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_strict, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'urn:oasis:names:tc:ciq:xsdschema:xAL:2.0'))

    _ElementMap = {
        
    }
    _AttributeMap = {
        __NumberSuffixSeparator.name() : __NumberSuffixSeparator,
        __Code.name() : __Code,
        __Type.name() : __Type
    }



# Complex type CTD_ANON_38 with content type EMPTY
class CTD_ANON_38 (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_EMPTY
    _Abstract = False
    _ExpandedName = None
    # Base type is pyxb.binding.datatypes.anyType
    
    # Attribute Code uses Python identifier Code
    __Code = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Code'), 'Code', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_38_Code', pyxb.binding.datatypes.anySimpleType)
    
    Code = property(__Code.value, __Code.set, None, u'Used by postal services to encode the name of the element.')

    
    # Attribute Type uses Python identifier Type
    __Type = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Type'), 'Type', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_38_Type', pyxb.binding.datatypes.anySimpleType)
    
    Type = property(__Type.value, __Type.set, None, u'Specific to postal service')


    _ElementMap = {
        
    }
    _AttributeMap = {
        __Code.name() : __Code,
        __Type.name() : __Type
    }



# Complex type CTD_ANON_39 with content type MIXED
class CTD_ANON_39 (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_MIXED
    _Abstract = False
    _ExpandedName = None
    # Base type is pyxb.binding.datatypes.anyType
    
    # Attribute Type uses Python identifier Type
    __Type = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Type'), 'Type', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_39_Type', pyxb.binding.datatypes.anySimpleType)
    
    Type = property(__Type.value, __Type.set, None, None)

    
    # Attribute Code uses Python identifier Code
    __Code = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Code'), 'Code', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_39_Code', pyxb.binding.datatypes.anySimpleType)
    
    Code = property(__Code.value, __Code.set, None, u'Used by postal services to encode the name of the element.')

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_strict, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'urn:oasis:names:tc:ciq:xsdschema:xAL:2.0'))

    _ElementMap = {
        
    }
    _AttributeMap = {
        __Type.name() : __Type,
        __Code.name() : __Code
    }



# Complex type ThoroughfareTrailingTypeType with content type MIXED
class ThoroughfareTrailingTypeType (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_MIXED
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'ThoroughfareTrailingTypeType')
    # Base type is pyxb.binding.datatypes.anyType
    
    # Attribute Type uses Python identifier Type
    __Type = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Type'), 'Type', '__urnoasisnamestcciqxsdschemaxAL2_0_ThoroughfareTrailingTypeType_Type', pyxb.binding.datatypes.anySimpleType)
    
    Type = property(__Type.value, __Type.set, None, None)

    
    # Attribute Code uses Python identifier Code
    __Code = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Code'), 'Code', '__urnoasisnamestcciqxsdschemaxAL2_0_ThoroughfareTrailingTypeType_Code', pyxb.binding.datatypes.anySimpleType)
    
    Code = property(__Code.value, __Code.set, None, u'Used by postal services to encode the name of the element.')

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_strict, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'urn:oasis:names:tc:ciq:xsdschema:xAL:2.0'))

    _ElementMap = {
        
    }
    _AttributeMap = {
        __Type.name() : __Type,
        __Code.name() : __Code
    }
Namespace.addCategoryObject('typeBinding', u'ThoroughfareTrailingTypeType', ThoroughfareTrailingTypeType)


# Complex type CTD_ANON_40 with content type MIXED
class CTD_ANON_40 (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_MIXED
    _Abstract = False
    _ExpandedName = None
    # Base type is pyxb.binding.datatypes.anyType
    
    # Attribute Type uses Python identifier Type
    __Type = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Type'), 'Type', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_40_Type', pyxb.binding.datatypes.anySimpleType)
    
    Type = property(__Type.value, __Type.set, None, u'Old Postal Code, new code, etc')

    
    # Attribute Code uses Python identifier Code
    __Code = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Code'), 'Code', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_40_Code', pyxb.binding.datatypes.anySimpleType)
    
    Code = property(__Code.value, __Code.set, None, u'Used by postal services to encode the name of the element.')

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_strict, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'urn:oasis:names:tc:ciq:xsdschema:xAL:2.0'))

    _ElementMap = {
        
    }
    _AttributeMap = {
        __Type.name() : __Type,
        __Code.name() : __Code
    }



# Complex type CTD_ANON_41 with content type MIXED
class CTD_ANON_41 (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_MIXED
    _Abstract = False
    _ExpandedName = None
    # Base type is pyxb.binding.datatypes.anyType
    
    # Attribute Code uses Python identifier Code
    __Code = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Code'), 'Code', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_41_Code', pyxb.binding.datatypes.anySimpleType)
    
    Code = property(__Code.value, __Code.set, None, u'Used by postal services to encode the name of the element.')

    
    # Attribute Type uses Python identifier Type
    __Type = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Type'), 'Type', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_41_Type', pyxb.binding.datatypes.anySimpleType)
    
    Type = property(__Type.value, __Type.set, None, u'Specific to postal service')

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_strict, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'urn:oasis:names:tc:ciq:xsdschema:xAL:2.0'))

    _ElementMap = {
        
    }
    _AttributeMap = {
        __Code.name() : __Code,
        __Type.name() : __Type
    }



# Complex type CTD_ANON_42 with content type MIXED
class CTD_ANON_42 (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_MIXED
    _Abstract = False
    _ExpandedName = None
    # Base type is pyxb.binding.datatypes.anyType
    
    # Attribute Code uses Python identifier Code
    __Code = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Code'), 'Code', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_42_Code', pyxb.binding.datatypes.anySimpleType)
    
    Code = property(__Code.value, __Code.set, None, u'Used by postal services to encode the name of the element.')


    _ElementMap = {
        
    }
    _AttributeMap = {
        __Code.name() : __Code
    }



# Complex type CTD_ANON_43 with content type MIXED
class CTD_ANON_43 (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_MIXED
    _Abstract = False
    _ExpandedName = None
    # Base type is pyxb.binding.datatypes.anyType
    
    # Attribute Type uses Python identifier Type
    __Type = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Type'), 'Type', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_43_Type', pyxb.binding.datatypes.anySimpleType)
    
    Type = property(__Type.value, __Type.set, None, u'Specific to postal service')

    
    # Attribute Code uses Python identifier Code
    __Code = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Code'), 'Code', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_43_Code', pyxb.binding.datatypes.anySimpleType)
    
    Code = property(__Code.value, __Code.set, None, u'Used by postal services to encode the name of the element.')

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_strict, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'urn:oasis:names:tc:ciq:xsdschema:xAL:2.0'))

    _ElementMap = {
        
    }
    _AttributeMap = {
        __Type.name() : __Type,
        __Code.name() : __Code
    }



# Complex type ThoroughfarePostDirectionType with content type MIXED
class ThoroughfarePostDirectionType (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_MIXED
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'ThoroughfarePostDirectionType')
    # Base type is pyxb.binding.datatypes.anyType
    
    # Attribute Type uses Python identifier Type
    __Type = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Type'), 'Type', '__urnoasisnamestcciqxsdschemaxAL2_0_ThoroughfarePostDirectionType_Type', pyxb.binding.datatypes.anySimpleType)
    
    Type = property(__Type.value, __Type.set, None, None)

    
    # Attribute Code uses Python identifier Code
    __Code = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Code'), 'Code', '__urnoasisnamestcciqxsdschemaxAL2_0_ThoroughfarePostDirectionType_Code', pyxb.binding.datatypes.anySimpleType)
    
    Code = property(__Code.value, __Code.set, None, u'Used by postal services to encode the name of the element.')

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_strict, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'urn:oasis:names:tc:ciq:xsdschema:xAL:2.0'))

    _ElementMap = {
        
    }
    _AttributeMap = {
        __Type.name() : __Type,
        __Code.name() : __Code
    }
Namespace.addCategoryObject('typeBinding', u'ThoroughfarePostDirectionType', ThoroughfarePostDirectionType)


# Complex type AddressLinesType with content type ELEMENT_ONLY
class AddressLinesType (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'AddressLinesType')
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}AddressLine uses Python identifier AddressLine
    __AddressLine = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'AddressLine'), 'AddressLine', '__urnoasisnamestcciqxsdschemaxAL2_0_AddressLinesType_urnoasisnamestcciqxsdschemaxAL2_0AddressLine', True)

    
    AddressLine = property(__AddressLine.value, __AddressLine.set, None, u'Free format address representation. An address can have more than one line. The order of the AddressLine elements must be preserved.')

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_strict, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'urn:oasis:names:tc:ciq:xsdschema:xAL:2.0'))
    _HasWildcardElement = True

    _ElementMap = {
        __AddressLine.name() : __AddressLine
    }
    _AttributeMap = {
        
    }
Namespace.addCategoryObject('typeBinding', u'AddressLinesType', AddressLinesType)


# Complex type CTD_ANON_44 with content type ELEMENT_ONLY
class CTD_ANON_44 (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = None
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}AddressLine uses Python identifier AddressLine
    __AddressLine = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'AddressLine'), 'AddressLine', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_44_urnoasisnamestcciqxsdschemaxAL2_0AddressLine', True)

    
    AddressLine = property(__AddressLine.value, __AddressLine.set, None, u'Free format address representation. An address can have more than one line. The order of the AddressLine elements must be preserved.')

    
    # Element {urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}PremiseNumberPrefix uses Python identifier PremiseNumberPrefix
    __PremiseNumberPrefix = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'PremiseNumberPrefix'), 'PremiseNumberPrefix', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_44_urnoasisnamestcciqxsdschemaxAL2_0PremiseNumberPrefix', True)

    
    PremiseNumberPrefix = property(__PremiseNumberPrefix.value, __PremiseNumberPrefix.set, None, u'A in A12')

    
    # Element {urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}PremiseNumber uses Python identifier PremiseNumber
    __PremiseNumber = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'PremiseNumber'), 'PremiseNumber', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_44_urnoasisnamestcciqxsdschemaxAL2_0PremiseNumber', True)

    
    PremiseNumber = property(__PremiseNumber.value, __PremiseNumber.set, None, u'Specification of the identifier of the premise (house, building, etc). Premises in a street are often uniquely identified by means of consecutive identifiers. The identifier can be a number, a letter or any combination of the two.')

    
    # Element {urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}PremiseNumberSuffix uses Python identifier PremiseNumberSuffix
    __PremiseNumberSuffix = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'PremiseNumberSuffix'), 'PremiseNumberSuffix', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_44_urnoasisnamestcciqxsdschemaxAL2_0PremiseNumberSuffix', True)

    
    PremiseNumberSuffix = property(__PremiseNumberSuffix.value, __PremiseNumberSuffix.set, None, u'A in 12A')


    _ElementMap = {
        __AddressLine.name() : __AddressLine,
        __PremiseNumberPrefix.name() : __PremiseNumberPrefix,
        __PremiseNumber.name() : __PremiseNumber,
        __PremiseNumberSuffix.name() : __PremiseNumberSuffix
    }
    _AttributeMap = {
        
    }



# Complex type CTD_ANON_45 with content type ELEMENT_ONLY
class CTD_ANON_45 (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = None
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}PostalRoute uses Python identifier PostalRoute
    __PostalRoute = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'PostalRoute'), 'PostalRoute', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_45_urnoasisnamestcciqxsdschemaxAL2_0PostalRoute', False)

    
    PostalRoute = property(__PostalRoute.value, __PostalRoute.set, None, u'A Postal van is specific for a route as in Is`rael, Rural route')

    
    # Element {urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}AddressLine uses Python identifier AddressLine
    __AddressLine = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'AddressLine'), 'AddressLine', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_45_urnoasisnamestcciqxsdschemaxAL2_0AddressLine', True)

    
    AddressLine = property(__AddressLine.value, __AddressLine.set, None, u'Free format address representation. An address can have more than one line. The order of the AddressLine elements must be preserved.')

    
    # Element {urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}PostalCode uses Python identifier PostalCode
    __PostalCode = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'PostalCode'), 'PostalCode', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_45_urnoasisnamestcciqxsdschemaxAL2_0PostalCode', False)

    
    PostalCode = property(__PostalCode.value, __PostalCode.set, None, u'PostalCode is the container element for either simple or complex (extended) postal codes. Type: Area Code, Postcode, etc.')

    
    # Element {urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}DependentLocality uses Python identifier DependentLocality
    __DependentLocality = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'DependentLocality'), 'DependentLocality', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_45_urnoasisnamestcciqxsdschemaxAL2_0DependentLocality', False)

    
    DependentLocality = property(__DependentLocality.value, __DependentLocality.set, None, u'Dependent localities are Districts within cities/towns, locality divisions, postal \ndivisions of cities, suburbs, etc. DependentLocality is a recursive element, but no nesting deeper than two exists (Locality-DependentLocality-DependentLocality).')

    
    # Element {urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}Premise uses Python identifier Premise
    __Premise = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'Premise'), 'Premise', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_45_urnoasisnamestcciqxsdschemaxAL2_0Premise', False)

    
    Premise = property(__Premise.value, __Premise.set, None, u'Specification of a single premise, for example a house or a building. The premise as a whole has a unique premise (house) number or a premise name.  There could be more than \none premise in a street referenced in an address. For example a building address near a major shopping centre or raiwlay station')

    
    # Element {urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}Thoroughfare uses Python identifier Thoroughfare
    __Thoroughfare = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'Thoroughfare'), 'Thoroughfare', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_45_urnoasisnamestcciqxsdschemaxAL2_0Thoroughfare', False)

    
    Thoroughfare = property(__Thoroughfare.value, __Thoroughfare.set, None, u'Specification of a thoroughfare. A thoroughfare could be a rd, street, canal, river, etc.  Note dependentlocality in a street. For example, in some countries, a large street will \nhave many subdivisions with numbers. Normally the subdivision name is the same as the road name, but with a number to identifiy it. Eg. SOI SUKUMVIT 3, SUKUMVIT RD, BANGKOK')

    
    # Element {urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}LargeMailUser uses Python identifier LargeMailUser
    __LargeMailUser = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'LargeMailUser'), 'LargeMailUser', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_45_urnoasisnamestcciqxsdschemaxAL2_0LargeMailUser', False)

    
    LargeMailUser = property(__LargeMailUser.value, __LargeMailUser.set, None, u'Specification of a large mail user address. Examples of large mail users are postal companies, companies in France with a cedex number, hospitals and airports with their own post code. Large mail user addresses do not have a street name with premise name or premise number in countries like Netherlands. But they have a POBox and street also in countries like France')

    
    # Element {urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}PostOffice uses Python identifier PostOffice
    __PostOffice = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'PostOffice'), 'PostOffice', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_45_urnoasisnamestcciqxsdschemaxAL2_0PostOffice', False)

    
    PostOffice = property(__PostOffice.value, __PostOffice.set, None, u'Specification of a post office. Examples are a rural post office where post is delivered and a post office containing post office boxes.')

    
    # Element {urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}PostBox uses Python identifier PostBox
    __PostBox = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'PostBox'), 'PostBox', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_45_urnoasisnamestcciqxsdschemaxAL2_0PostBox', False)

    
    PostBox = property(__PostBox.value, __PostBox.set, None, u'Specification of a postbox like mail delivery point. Only a single postbox number can be specified. Examples of postboxes are POBox, free mail numbers, etc.')

    
    # Element {urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}LocalityName uses Python identifier LocalityName
    __LocalityName = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'LocalityName'), 'LocalityName', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_45_urnoasisnamestcciqxsdschemaxAL2_0LocalityName', True)

    
    LocalityName = property(__LocalityName.value, __LocalityName.set, None, u'Name of the locality')

    
    # Attribute UsageType uses Python identifier UsageType
    __UsageType = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'UsageType'), 'UsageType', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_45_UsageType', pyxb.binding.datatypes.anySimpleType)
    
    UsageType = property(__UsageType.value, __UsageType.set, None, u'Postal or Political - Sometimes locations must be distinguished between postal system, and physical locations as defined by a political system')

    
    # Attribute Type uses Python identifier Type
    __Type = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Type'), 'Type', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_45_Type', pyxb.binding.datatypes.anySimpleType)
    
    Type = property(__Type.value, __Type.set, None, u'Possible values not limited to: City, IndustrialEstate, etc')

    
    # Attribute Indicator uses Python identifier Indicator
    __Indicator = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Indicator'), 'Indicator', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_45_Indicator', pyxb.binding.datatypes.anySimpleType)
    
    Indicator = property(__Indicator.value, __Indicator.set, None, u'Erode (Dist) where (Dist) is the Indicator')

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_strict, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'urn:oasis:names:tc:ciq:xsdschema:xAL:2.0'))
    _HasWildcardElement = True

    _ElementMap = {
        __PostalRoute.name() : __PostalRoute,
        __AddressLine.name() : __AddressLine,
        __PostalCode.name() : __PostalCode,
        __DependentLocality.name() : __DependentLocality,
        __Premise.name() : __Premise,
        __Thoroughfare.name() : __Thoroughfare,
        __LargeMailUser.name() : __LargeMailUser,
        __PostOffice.name() : __PostOffice,
        __PostBox.name() : __PostBox,
        __LocalityName.name() : __LocalityName
    }
    _AttributeMap = {
        __UsageType.name() : __UsageType,
        __Type.name() : __Type,
        __Indicator.name() : __Indicator
    }



# Complex type SubPremiseType with content type ELEMENT_ONLY
class SubPremiseType (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'SubPremiseType')
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}SubPremise uses Python identifier SubPremise
    __SubPremise = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'SubPremise'), 'SubPremise', '__urnoasisnamestcciqxsdschemaxAL2_0_SubPremiseType_urnoasisnamestcciqxsdschemaxAL2_0SubPremise', False)

    
    SubPremise = property(__SubPremise.value, __SubPremise.set, None, u'Specification of a single sub-premise. Examples of sub-premises are apartments and suites. \nEach sub-premise should be uniquely identifiable. SubPremiseType: Specification of the name of a sub-premise type. Possible values not limited to: Suite, Appartment, Floor, Unknown\nMultiple levels within a premise by recursively calling SubPremise Eg. Level 4, Suite 2, Block C')

    
    # Element {urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}Firm uses Python identifier Firm
    __Firm = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'Firm'), 'Firm', '__urnoasisnamestcciqxsdschemaxAL2_0_SubPremiseType_urnoasisnamestcciqxsdschemaxAL2_0Firm', False)

    
    Firm = property(__Firm.value, __Firm.set, None, u'Specification of a firm, company, organization, etc. It can be specified as part of an address that contains a street or a postbox. It is therefore different from a large mail user address, which contains no street.')

    
    # Element {urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}MailStop uses Python identifier MailStop
    __MailStop = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'MailStop'), 'MailStop', '__urnoasisnamestcciqxsdschemaxAL2_0_SubPremiseType_urnoasisnamestcciqxsdschemaxAL2_0MailStop', False)

    
    MailStop = property(__MailStop.value, __MailStop.set, None, u'A MailStop is where the the mail is delivered to within a premise/subpremise/firm or a facility.')

    
    # Element {urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}SubPremiseNumberSuffix uses Python identifier SubPremiseNumberSuffix
    __SubPremiseNumberSuffix = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'SubPremiseNumberSuffix'), 'SubPremiseNumberSuffix', '__urnoasisnamestcciqxsdschemaxAL2_0_SubPremiseType_urnoasisnamestcciqxsdschemaxAL2_0SubPremiseNumberSuffix', True)

    
    SubPremiseNumberSuffix = property(__SubPremiseNumberSuffix.value, __SubPremiseNumberSuffix.set, None, u' Suffix of the sub premise number. eg. A in 12A')

    
    # Element {urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}SubPremiseLocation uses Python identifier SubPremiseLocation
    __SubPremiseLocation = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'SubPremiseLocation'), 'SubPremiseLocation', '__urnoasisnamestcciqxsdschemaxAL2_0_SubPremiseType_urnoasisnamestcciqxsdschemaxAL2_0SubPremiseLocation', False)

    
    SubPremiseLocation = property(__SubPremiseLocation.value, __SubPremiseLocation.set, None, u' Name of the SubPremise Location. eg. LOBBY, BASEMENT, GROUND FLOOR, etc...')

    
    # Element {urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}AddressLine uses Python identifier AddressLine
    __AddressLine = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'AddressLine'), 'AddressLine', '__urnoasisnamestcciqxsdschemaxAL2_0_SubPremiseType_urnoasisnamestcciqxsdschemaxAL2_0AddressLine', True)

    
    AddressLine = property(__AddressLine.value, __AddressLine.set, None, u'Free format address representation. An address can have more than one line. The order of the AddressLine elements must be preserved.')

    
    # Element {urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}SubPremiseName uses Python identifier SubPremiseName
    __SubPremiseName = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'SubPremiseName'), 'SubPremiseName', '__urnoasisnamestcciqxsdschemaxAL2_0_SubPremiseType_urnoasisnamestcciqxsdschemaxAL2_0SubPremiseName', True)

    
    SubPremiseName = property(__SubPremiseName.value, __SubPremiseName.set, None, u' Name of the SubPremise')

    
    # Element {urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}BuildingName uses Python identifier BuildingName
    __BuildingName = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'BuildingName'), 'BuildingName', '__urnoasisnamestcciqxsdschemaxAL2_0_SubPremiseType_urnoasisnamestcciqxsdschemaxAL2_0BuildingName', True)

    
    BuildingName = property(__BuildingName.value, __BuildingName.set, None, u'Name of the building')

    
    # Element {urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}SubPremiseNumberPrefix uses Python identifier SubPremiseNumberPrefix
    __SubPremiseNumberPrefix = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'SubPremiseNumberPrefix'), 'SubPremiseNumberPrefix', '__urnoasisnamestcciqxsdschemaxAL2_0_SubPremiseType_urnoasisnamestcciqxsdschemaxAL2_0SubPremiseNumberPrefix', True)

    
    SubPremiseNumberPrefix = property(__SubPremiseNumberPrefix.value, __SubPremiseNumberPrefix.set, None, u' Prefix of the sub premise number. eg. A in A-12')

    
    # Element {urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}SubPremiseNumber uses Python identifier SubPremiseNumber
    __SubPremiseNumber = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'SubPremiseNumber'), 'SubPremiseNumber', '__urnoasisnamestcciqxsdschemaxAL2_0_SubPremiseType_urnoasisnamestcciqxsdschemaxAL2_0SubPremiseNumber', True)

    
    SubPremiseNumber = property(__SubPremiseNumber.value, __SubPremiseNumber.set, None, u' Specification of the identifier of a sub-premise. Examples of sub-premises are apartments and suites. sub-premises in a building are often uniquely identified by means of consecutive\nidentifiers. The identifier can be a number, a letter or any combination of the two. In the latter case, the identifier includes exactly one variable (range) part, which is either a \nnumber or a single letter that is surrounded by fixed parts at the left (prefix) or the right (postfix).')

    
    # Element {urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}PostalCode uses Python identifier PostalCode
    __PostalCode = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'PostalCode'), 'PostalCode', '__urnoasisnamestcciqxsdschemaxAL2_0_SubPremiseType_urnoasisnamestcciqxsdschemaxAL2_0PostalCode', False)

    
    PostalCode = property(__PostalCode.value, __PostalCode.set, None, u'PostalCode is the container element for either simple or complex (extended) postal codes. Type: Area Code, Postcode, etc.')

    
    # Attribute Type uses Python identifier Type
    __Type = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Type'), 'Type', '__urnoasisnamestcciqxsdschemaxAL2_0_SubPremiseType_Type', pyxb.binding.datatypes.anySimpleType)
    
    Type = property(__Type.value, __Type.set, None, None)

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_strict, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'urn:oasis:names:tc:ciq:xsdschema:xAL:2.0'))
    _HasWildcardElement = True

    _ElementMap = {
        __SubPremise.name() : __SubPremise,
        __Firm.name() : __Firm,
        __MailStop.name() : __MailStop,
        __SubPremiseNumberSuffix.name() : __SubPremiseNumberSuffix,
        __SubPremiseLocation.name() : __SubPremiseLocation,
        __AddressLine.name() : __AddressLine,
        __SubPremiseName.name() : __SubPremiseName,
        __BuildingName.name() : __BuildingName,
        __SubPremiseNumberPrefix.name() : __SubPremiseNumberPrefix,
        __SubPremiseNumber.name() : __SubPremiseNumber,
        __PostalCode.name() : __PostalCode
    }
    _AttributeMap = {
        __Type.name() : __Type
    }
Namespace.addCategoryObject('typeBinding', u'SubPremiseType', SubPremiseType)


# Complex type CTD_ANON_46 with content type MIXED
class CTD_ANON_46 (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_MIXED
    _Abstract = False
    _ExpandedName = None
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}AddressLine uses Python identifier AddressLine
    __AddressLine = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'AddressLine'), 'AddressLine', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_46_urnoasisnamestcciqxsdschemaxAL2_0AddressLine', True)

    
    AddressLine = property(__AddressLine.value, __AddressLine.set, None, u'Free format address representation. An address can have more than one line. The order of the AddressLine elements must be preserved.')

    
    # Element {urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}ThoroughfareNumber uses Python identifier ThoroughfareNumber
    __ThoroughfareNumber = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'ThoroughfareNumber'), 'ThoroughfareNumber', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_46_urnoasisnamestcciqxsdschemaxAL2_0ThoroughfareNumber', True)

    
    ThoroughfareNumber = property(__ThoroughfareNumber.value, __ThoroughfareNumber.set, None, u'Eg.: 23 Archer street or 25/15 Zero Avenue, etc')

    
    # Element {urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}ThoroughfareNumberPrefix uses Python identifier ThoroughfareNumberPrefix
    __ThoroughfareNumberPrefix = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'ThoroughfareNumberPrefix'), 'ThoroughfareNumberPrefix', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_46_urnoasisnamestcciqxsdschemaxAL2_0ThoroughfareNumberPrefix', True)

    
    ThoroughfareNumberPrefix = property(__ThoroughfareNumberPrefix.value, __ThoroughfareNumberPrefix.set, None, u'Prefix before the number. A in A12 Archer Street')

    
    # Element {urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}ThoroughfareNumberSuffix uses Python identifier ThoroughfareNumberSuffix
    __ThoroughfareNumberSuffix = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'ThoroughfareNumberSuffix'), 'ThoroughfareNumberSuffix', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_46_urnoasisnamestcciqxsdschemaxAL2_0ThoroughfareNumberSuffix', True)

    
    ThoroughfareNumberSuffix = property(__ThoroughfareNumberSuffix.value, __ThoroughfareNumberSuffix.set, None, u'Suffix after the number. A in 12A Archer Street')

    
    # Attribute Code uses Python identifier Code
    __Code = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Code'), 'Code', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_46_Code', pyxb.binding.datatypes.anySimpleType)
    
    Code = property(__Code.value, __Code.set, None, u'Used by postal services to encode the name of the element.')

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_strict, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'urn:oasis:names:tc:ciq:xsdschema:xAL:2.0'))

    _ElementMap = {
        __AddressLine.name() : __AddressLine,
        __ThoroughfareNumber.name() : __ThoroughfareNumber,
        __ThoroughfareNumberPrefix.name() : __ThoroughfareNumberPrefix,
        __ThoroughfareNumberSuffix.name() : __ThoroughfareNumberSuffix
    }
    _AttributeMap = {
        __Code.name() : __Code
    }



# Complex type CTD_ANON_47 with content type MIXED
class CTD_ANON_47 (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_MIXED
    _Abstract = False
    _ExpandedName = None
    # Base type is pyxb.binding.datatypes.anyType
    
    # Attribute Code uses Python identifier Code
    __Code = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Code'), 'Code', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_47_Code', pyxb.binding.datatypes.anySimpleType)
    
    Code = property(__Code.value, __Code.set, None, u'Used by postal services to encode the name of the element.')

    
    # Attribute Type uses Python identifier Type
    __Type = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Type'), 'Type', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_47_Type', pyxb.binding.datatypes.anySimpleType)
    
    Type = property(__Type.value, __Type.set, None, u'Specific to postal service')

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_strict, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'urn:oasis:names:tc:ciq:xsdschema:xAL:2.0'))

    _ElementMap = {
        
    }
    _AttributeMap = {
        __Code.name() : __Code,
        __Type.name() : __Type
    }



# Complex type CTD_ANON_48 with content type ELEMENT_ONLY
class CTD_ANON_48 (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = None
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}PremiseNumberPrefix uses Python identifier PremiseNumberPrefix
    __PremiseNumberPrefix = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'PremiseNumberPrefix'), 'PremiseNumberPrefix', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_48_urnoasisnamestcciqxsdschemaxAL2_0PremiseNumberPrefix', True)

    
    PremiseNumberPrefix = property(__PremiseNumberPrefix.value, __PremiseNumberPrefix.set, None, u'A in A12')

    
    # Element {urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}PremiseNumberSuffix uses Python identifier PremiseNumberSuffix
    __PremiseNumberSuffix = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'PremiseNumberSuffix'), 'PremiseNumberSuffix', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_48_urnoasisnamestcciqxsdschemaxAL2_0PremiseNumberSuffix', True)

    
    PremiseNumberSuffix = property(__PremiseNumberSuffix.value, __PremiseNumberSuffix.set, None, u'A in 12A')

    
    # Element {urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}AddressLine uses Python identifier AddressLine
    __AddressLine = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'AddressLine'), 'AddressLine', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_48_urnoasisnamestcciqxsdschemaxAL2_0AddressLine', True)

    
    AddressLine = property(__AddressLine.value, __AddressLine.set, None, u'Free format address representation. An address can have more than one line. The order of the AddressLine elements must be preserved.')

    
    # Element {urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}PremiseNumber uses Python identifier PremiseNumber
    __PremiseNumber = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'PremiseNumber'), 'PremiseNumber', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_48_urnoasisnamestcciqxsdschemaxAL2_0PremiseNumber', True)

    
    PremiseNumber = property(__PremiseNumber.value, __PremiseNumber.set, None, u'Specification of the identifier of the premise (house, building, etc). Premises in a street are often uniquely identified by means of consecutive identifiers. The identifier can be a number, a letter or any combination of the two.')


    _ElementMap = {
        __PremiseNumberPrefix.name() : __PremiseNumberPrefix,
        __PremiseNumberSuffix.name() : __PremiseNumberSuffix,
        __AddressLine.name() : __AddressLine,
        __PremiseNumber.name() : __PremiseNumber
    }
    _AttributeMap = {
        
    }



# Complex type CTD_ANON_49 with content type MIXED
class CTD_ANON_49 (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_MIXED
    _Abstract = False
    _ExpandedName = None
    # Base type is pyxb.binding.datatypes.anyType
    
    # Attribute Code uses Python identifier Code
    __Code = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Code'), 'Code', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_49_Code', pyxb.binding.datatypes.anySimpleType)
    
    Code = property(__Code.value, __Code.set, None, u'Used by postal services to encode the name of the element.')

    
    # Attribute Type uses Python identifier Type
    __Type = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Type'), 'Type', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_49_Type', pyxb.binding.datatypes.anySimpleType)
    
    Type = property(__Type.value, __Type.set, None, None)

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_strict, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'urn:oasis:names:tc:ciq:xsdschema:xAL:2.0'))

    _ElementMap = {
        
    }
    _AttributeMap = {
        __Code.name() : __Code,
        __Type.name() : __Type
    }



# Complex type CTD_ANON_50 with content type MIXED
class CTD_ANON_50 (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_MIXED
    _Abstract = False
    _ExpandedName = None
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}ThoroughfareNumberPrefix uses Python identifier ThoroughfareNumberPrefix
    __ThoroughfareNumberPrefix = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'ThoroughfareNumberPrefix'), 'ThoroughfareNumberPrefix', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_50_urnoasisnamestcciqxsdschemaxAL2_0ThoroughfareNumberPrefix', True)

    
    ThoroughfareNumberPrefix = property(__ThoroughfareNumberPrefix.value, __ThoroughfareNumberPrefix.set, None, u'Prefix before the number. A in A12 Archer Street')

    
    # Element {urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}AddressLine uses Python identifier AddressLine
    __AddressLine = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'AddressLine'), 'AddressLine', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_50_urnoasisnamestcciqxsdschemaxAL2_0AddressLine', True)

    
    AddressLine = property(__AddressLine.value, __AddressLine.set, None, u'Free format address representation. An address can have more than one line. The order of the AddressLine elements must be preserved.')

    
    # Element {urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}ThoroughfareNumber uses Python identifier ThoroughfareNumber
    __ThoroughfareNumber = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'ThoroughfareNumber'), 'ThoroughfareNumber', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_50_urnoasisnamestcciqxsdschemaxAL2_0ThoroughfareNumber', True)

    
    ThoroughfareNumber = property(__ThoroughfareNumber.value, __ThoroughfareNumber.set, None, u'Eg.: 23 Archer street or 25/15 Zero Avenue, etc')

    
    # Element {urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}ThoroughfareNumberSuffix uses Python identifier ThoroughfareNumberSuffix
    __ThoroughfareNumberSuffix = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'ThoroughfareNumberSuffix'), 'ThoroughfareNumberSuffix', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_50_urnoasisnamestcciqxsdschemaxAL2_0ThoroughfareNumberSuffix', True)

    
    ThoroughfareNumberSuffix = property(__ThoroughfareNumberSuffix.value, __ThoroughfareNumberSuffix.set, None, u'Suffix after the number. A in 12A Archer Street')

    
    # Attribute Code uses Python identifier Code
    __Code = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Code'), 'Code', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_50_Code', pyxb.binding.datatypes.anySimpleType)
    
    Code = property(__Code.value, __Code.set, None, u'Used by postal services to encode the name of the element.')

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_strict, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'urn:oasis:names:tc:ciq:xsdschema:xAL:2.0'))

    _ElementMap = {
        __ThoroughfareNumberPrefix.name() : __ThoroughfareNumberPrefix,
        __AddressLine.name() : __AddressLine,
        __ThoroughfareNumber.name() : __ThoroughfareNumber,
        __ThoroughfareNumberSuffix.name() : __ThoroughfareNumberSuffix
    }
    _AttributeMap = {
        __Code.name() : __Code
    }



# Complex type CTD_ANON_51 with content type MIXED
class CTD_ANON_51 (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_MIXED
    _Abstract = False
    _ExpandedName = None
    # Base type is pyxb.binding.datatypes.anyType
    
    # Attribute Type uses Python identifier Type
    __Type = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Type'), 'Type', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_51_Type', pyxb.binding.datatypes.anySimpleType)
    
    Type = property(__Type.value, __Type.set, None, u'Postal, residential, corporate, etc')

    
    # Attribute Code uses Python identifier Code
    __Code = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Code'), 'Code', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_51_Code', pyxb.binding.datatypes.anySimpleType)
    
    Code = property(__Code.value, __Code.set, None, u'Used by postal services to encode the name of the element.')

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_strict, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'urn:oasis:names:tc:ciq:xsdschema:xAL:2.0'))

    _ElementMap = {
        
    }
    _AttributeMap = {
        __Type.name() : __Type,
        __Code.name() : __Code
    }



# Complex type CTD_ANON_52 with content type MIXED
class CTD_ANON_52 (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_MIXED
    _Abstract = False
    _ExpandedName = None
    # Base type is pyxb.binding.datatypes.anyType
    
    # Attribute Type uses Python identifier Type
    __Type = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Type'), 'Type', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_52_Type', pyxb.binding.datatypes.anySimpleType)
    
    Type = property(__Type.value, __Type.set, None, None)

    
    # Attribute Code uses Python identifier Code
    __Code = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Code'), 'Code', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_52_Code', pyxb.binding.datatypes.anySimpleType)
    
    Code = property(__Code.value, __Code.set, None, u'Used by postal services to encode the name of the element.')

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_strict, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'urn:oasis:names:tc:ciq:xsdschema:xAL:2.0'))

    _ElementMap = {
        
    }
    _AttributeMap = {
        __Type.name() : __Type,
        __Code.name() : __Code
    }



# Complex type CTD_ANON_53 with content type MIXED
class CTD_ANON_53 (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_MIXED
    _Abstract = False
    _ExpandedName = None
    # Base type is pyxb.binding.datatypes.anyType
    
    # Attribute Code uses Python identifier Code
    __Code = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Code'), 'Code', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_53_Code', pyxb.binding.datatypes.anySimpleType)
    
    Code = property(__Code.value, __Code.set, None, u'Used by postal services to encode the name of the element.')

    
    # Attribute Type uses Python identifier Type
    __Type = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Type'), 'Type', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_53_Type', pyxb.binding.datatypes.anySimpleType)
    
    Type = property(__Type.value, __Type.set, None, None)

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_strict, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'urn:oasis:names:tc:ciq:xsdschema:xAL:2.0'))

    _ElementMap = {
        
    }
    _AttributeMap = {
        __Code.name() : __Code,
        __Type.name() : __Type
    }



# Complex type ThoroughfarePreDirectionType with content type MIXED
class ThoroughfarePreDirectionType (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_MIXED
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'ThoroughfarePreDirectionType')
    # Base type is pyxb.binding.datatypes.anyType
    
    # Attribute Code uses Python identifier Code
    __Code = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Code'), 'Code', '__urnoasisnamestcciqxsdschemaxAL2_0_ThoroughfarePreDirectionType_Code', pyxb.binding.datatypes.anySimpleType)
    
    Code = property(__Code.value, __Code.set, None, u'Used by postal services to encode the name of the element.')

    
    # Attribute Type uses Python identifier Type
    __Type = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Type'), 'Type', '__urnoasisnamestcciqxsdschemaxAL2_0_ThoroughfarePreDirectionType_Type', pyxb.binding.datatypes.anySimpleType)
    
    Type = property(__Type.value, __Type.set, None, None)

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_strict, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'urn:oasis:names:tc:ciq:xsdschema:xAL:2.0'))

    _ElementMap = {
        
    }
    _AttributeMap = {
        __Code.name() : __Code,
        __Type.name() : __Type
    }
Namespace.addCategoryObject('typeBinding', u'ThoroughfarePreDirectionType', ThoroughfarePreDirectionType)


# Complex type CTD_ANON_54 with content type MIXED
class CTD_ANON_54 (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_MIXED
    _Abstract = False
    _ExpandedName = None
    # Base type is pyxb.binding.datatypes.anyType
    
    # Attribute Code uses Python identifier Code
    __Code = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Code'), 'Code', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_54_Code', pyxb.binding.datatypes.anySimpleType)
    
    Code = property(__Code.value, __Code.set, None, u'Used by postal services to encode the name of the element.')

    
    # Attribute Type uses Python identifier Type
    __Type = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Type'), 'Type', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_54_Type', pyxb.binding.datatypes.anySimpleType)
    
    Type = property(__Type.value, __Type.set, None, None)

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_strict, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'urn:oasis:names:tc:ciq:xsdschema:xAL:2.0'))

    _ElementMap = {
        
    }
    _AttributeMap = {
        __Code.name() : __Code,
        __Type.name() : __Type
    }



# Complex type CTD_ANON_55 with content type MIXED
class CTD_ANON_55 (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_MIXED
    _Abstract = False
    _ExpandedName = None
    # Base type is pyxb.binding.datatypes.anyType
    
    # Attribute Type uses Python identifier Type
    __Type = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Type'), 'Type', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_55_Type', pyxb.binding.datatypes.string)
    
    Type = property(__Type.value, __Type.set, None, u'CEDEX Code')

    
    # Attribute Indicator uses Python identifier Indicator
    __Indicator = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Indicator'), 'Indicator', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_55_Indicator', pyxb.binding.datatypes.anySimpleType)
    
    Indicator = property(__Indicator.value, __Indicator.set, None, u'eg. Building 429 in which Building is the Indicator')

    
    # Attribute Code uses Python identifier Code
    __Code = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Code'), 'Code', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_55_Code', pyxb.binding.datatypes.anySimpleType)
    
    Code = property(__Code.value, __Code.set, None, u'Used by postal services to encode the name of the element.')

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_strict, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'urn:oasis:names:tc:ciq:xsdschema:xAL:2.0'))

    _ElementMap = {
        
    }
    _AttributeMap = {
        __Type.name() : __Type,
        __Indicator.name() : __Indicator,
        __Code.name() : __Code
    }



# Complex type ThoroughfareLeadingTypeType with content type MIXED
class ThoroughfareLeadingTypeType (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_MIXED
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'ThoroughfareLeadingTypeType')
    # Base type is pyxb.binding.datatypes.anyType
    
    # Attribute Type uses Python identifier Type
    __Type = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Type'), 'Type', '__urnoasisnamestcciqxsdschemaxAL2_0_ThoroughfareLeadingTypeType_Type', pyxb.binding.datatypes.anySimpleType)
    
    Type = property(__Type.value, __Type.set, None, None)

    
    # Attribute Code uses Python identifier Code
    __Code = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Code'), 'Code', '__urnoasisnamestcciqxsdschemaxAL2_0_ThoroughfareLeadingTypeType_Code', pyxb.binding.datatypes.anySimpleType)
    
    Code = property(__Code.value, __Code.set, None, u'Used by postal services to encode the name of the element.')

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_strict, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'urn:oasis:names:tc:ciq:xsdschema:xAL:2.0'))

    _ElementMap = {
        
    }
    _AttributeMap = {
        __Type.name() : __Type,
        __Code.name() : __Code
    }
Namespace.addCategoryObject('typeBinding', u'ThoroughfareLeadingTypeType', ThoroughfareLeadingTypeType)


# Complex type CTD_ANON_56 with content type MIXED
class CTD_ANON_56 (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_MIXED
    _Abstract = False
    _ExpandedName = None
    # Base type is pyxb.binding.datatypes.anyType
    
    # Attribute Code uses Python identifier Code
    __Code = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Code'), 'Code', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_56_Code', pyxb.binding.datatypes.anySimpleType)
    
    Code = property(__Code.value, __Code.set, None, u'Used by postal services to encode the name of the element.')

    
    # Attribute Type uses Python identifier Type
    __Type = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Type'), 'Type', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_56_Type', pyxb.binding.datatypes.anySimpleType)
    
    Type = property(__Type.value, __Type.set, None, u'Specific to postal service')

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_strict, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'urn:oasis:names:tc:ciq:xsdschema:xAL:2.0'))

    _ElementMap = {
        
    }
    _AttributeMap = {
        __Code.name() : __Code,
        __Type.name() : __Type
    }



# Complex type CTD_ANON_57 with content type MIXED
class CTD_ANON_57 (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_MIXED
    _Abstract = False
    _ExpandedName = None
    # Base type is pyxb.binding.datatypes.anyType
    
    # Attribute Code uses Python identifier Code
    __Code = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Code'), 'Code', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_57_Code', pyxb.binding.datatypes.anySimpleType)
    
    Code = property(__Code.value, __Code.set, None, u'Used by postal services to encode the name of the element.')

    
    # Attribute Scheme uses Python identifier Scheme
    __Scheme = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Scheme'), 'Scheme', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_57_Scheme', pyxb.binding.datatypes.anySimpleType)
    
    Scheme = property(__Scheme.value, __Scheme.set, None, u'Country code scheme possible values, but not limited to: iso.3166-2, iso.3166-3 for two and three character country codes.')

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_strict, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'urn:oasis:names:tc:ciq:xsdschema:xAL:2.0'))

    _ElementMap = {
        
    }
    _AttributeMap = {
        __Code.name() : __Code,
        __Scheme.name() : __Scheme
    }



# Complex type CTD_ANON_58 with content type MIXED
class CTD_ANON_58 (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_MIXED
    _Abstract = False
    _ExpandedName = None
    # Base type is pyxb.binding.datatypes.anyType
    
    # Attribute Code uses Python identifier Code
    __Code = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Code'), 'Code', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_58_Code', pyxb.binding.datatypes.anySimpleType)
    
    Code = property(__Code.value, __Code.set, None, u'Used by postal services to encode the name of the element.')

    
    # Attribute TypeOccurrence uses Python identifier TypeOccurrence
    __TypeOccurrence = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'TypeOccurrence'), 'TypeOccurrence', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_58_TypeOccurrence', STD_ANON_15)
    
    TypeOccurrence = property(__TypeOccurrence.value, __TypeOccurrence.set, None, u'EGIS Building where EGIS occurs before Building')

    
    # Attribute Type uses Python identifier Type
    __Type = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Type'), 'Type', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_58_Type', pyxb.binding.datatypes.anySimpleType)
    
    Type = property(__Type.value, __Type.set, None, None)

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_strict, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'urn:oasis:names:tc:ciq:xsdschema:xAL:2.0'))

    _ElementMap = {
        
    }
    _AttributeMap = {
        __Code.name() : __Code,
        __TypeOccurrence.name() : __TypeOccurrence,
        __Type.name() : __Type
    }



# Complex type CTD_ANON_59 with content type MIXED
class CTD_ANON_59 (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_MIXED
    _Abstract = False
    _ExpandedName = None
    # Base type is pyxb.binding.datatypes.anyType
    
    # Attribute Code uses Python identifier Code
    __Code = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Code'), 'Code', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_59_Code', pyxb.binding.datatypes.anySimpleType)
    
    Code = property(__Code.value, __Code.set, None, u'Used by postal services to encode the name of the element.')

    
    # Attribute NameNumberSeparator uses Python identifier NameNumberSeparator
    __NameNumberSeparator = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'NameNumberSeparator'), 'NameNumberSeparator', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_59_NameNumberSeparator', pyxb.binding.datatypes.anySimpleType)
    
    NameNumberSeparator = property(__NameNumberSeparator.value, __NameNumberSeparator.set, None, u'"-" in MS-123')

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_strict, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'urn:oasis:names:tc:ciq:xsdschema:xAL:2.0'))

    _ElementMap = {
        
    }
    _AttributeMap = {
        __Code.name() : __Code,
        __NameNumberSeparator.name() : __NameNumberSeparator
    }



# Complex type CTD_ANON_60 with content type ELEMENT_ONLY
class CTD_ANON_60 (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = None
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}PostOffice uses Python identifier PostOffice
    __PostOffice = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'PostOffice'), 'PostOffice', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_60_urnoasisnamestcciqxsdschemaxAL2_0PostOffice', False)

    
    PostOffice = property(__PostOffice.value, __PostOffice.set, None, u'Specification of a post office. Examples are a rural post office where post is delivered and a post office containing post office boxes.')

    
    # Element {urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}AddressLine uses Python identifier AddressLine
    __AddressLine = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'AddressLine'), 'AddressLine', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_60_urnoasisnamestcciqxsdschemaxAL2_0AddressLine', True)

    
    AddressLine = property(__AddressLine.value, __AddressLine.set, None, u'Free format address representation. An address can have more than one line. The order of the AddressLine elements must be preserved.')

    
    # Element {urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}SubAdministrativeAreaName uses Python identifier SubAdministrativeAreaName
    __SubAdministrativeAreaName = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'SubAdministrativeAreaName'), 'SubAdministrativeAreaName', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_60_urnoasisnamestcciqxsdschemaxAL2_0SubAdministrativeAreaName', True)

    
    SubAdministrativeAreaName = property(__SubAdministrativeAreaName.value, __SubAdministrativeAreaName.set, None, u' Name of the sub-administrative area')

    
    # Element {urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}PostalCode uses Python identifier PostalCode
    __PostalCode = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'PostalCode'), 'PostalCode', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_60_urnoasisnamestcciqxsdschemaxAL2_0PostalCode', False)

    
    PostalCode = property(__PostalCode.value, __PostalCode.set, None, u'PostalCode is the container element for either simple or complex (extended) postal codes. Type: Area Code, Postcode, etc.')

    
    # Element {urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}Locality uses Python identifier Locality
    __Locality = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'Locality'), 'Locality', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_60_urnoasisnamestcciqxsdschemaxAL2_0Locality', False)

    
    Locality = property(__Locality.value, __Locality.set, None, u'Locality is one level lower than adminisstrative area. Eg.: cities, reservations and any other built-up areas.')

    
    # Attribute UsageType uses Python identifier UsageType
    __UsageType = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'UsageType'), 'UsageType', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_60_UsageType', pyxb.binding.datatypes.anySimpleType)
    
    UsageType = property(__UsageType.value, __UsageType.set, None, u'Postal or Political - Sometimes locations must be distinguished between postal system, and physical locations as defined by a political system')

    
    # Attribute Type uses Python identifier Type
    __Type = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Type'), 'Type', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_60_Type', pyxb.binding.datatypes.anySimpleType)
    
    Type = property(__Type.value, __Type.set, None, u'Province or State or County or Kanton, etc')

    
    # Attribute Indicator uses Python identifier Indicator
    __Indicator = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Indicator'), 'Indicator', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_60_Indicator', pyxb.binding.datatypes.anySimpleType)
    
    Indicator = property(__Indicator.value, __Indicator.set, None, u'Erode (Dist) where (Dist) is the Indicator')

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_strict, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'urn:oasis:names:tc:ciq:xsdschema:xAL:2.0'))
    _HasWildcardElement = True

    _ElementMap = {
        __PostOffice.name() : __PostOffice,
        __AddressLine.name() : __AddressLine,
        __SubAdministrativeAreaName.name() : __SubAdministrativeAreaName,
        __PostalCode.name() : __PostalCode,
        __Locality.name() : __Locality
    }
    _AttributeMap = {
        __UsageType.name() : __UsageType,
        __Type.name() : __Type,
        __Indicator.name() : __Indicator
    }



# Complex type CTD_ANON_61 with content type MIXED
class CTD_ANON_61 (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_MIXED
    _Abstract = False
    _ExpandedName = None
    # Base type is pyxb.binding.datatypes.anyType
    
    # Attribute Type uses Python identifier Type
    __Type = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Type'), 'Type', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_61_Type', pyxb.binding.datatypes.anySimpleType)
    
    Type = property(__Type.value, __Type.set, None, None)

    
    # Attribute Code uses Python identifier Code
    __Code = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Code'), 'Code', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_61_Code', pyxb.binding.datatypes.anySimpleType)
    
    Code = property(__Code.value, __Code.set, None, u'Used by postal services to encode the name of the element.')

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_strict, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'urn:oasis:names:tc:ciq:xsdschema:xAL:2.0'))

    _ElementMap = {
        
    }
    _AttributeMap = {
        __Type.name() : __Type,
        __Code.name() : __Code
    }



# Complex type CTD_ANON_62 with content type ELEMENT_ONLY
class CTD_ANON_62 (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = None
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}ThoroughfareNumberTo uses Python identifier ThoroughfareNumberTo
    __ThoroughfareNumberTo = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'ThoroughfareNumberTo'), 'ThoroughfareNumberTo', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_62_urnoasisnamestcciqxsdschemaxAL2_0ThoroughfareNumberTo', False)

    
    ThoroughfareNumberTo = property(__ThoroughfareNumberTo.value, __ThoroughfareNumberTo.set, None, u'Ending number in the range')

    
    # Element {urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}AddressLine uses Python identifier AddressLine
    __AddressLine = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'AddressLine'), 'AddressLine', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_62_urnoasisnamestcciqxsdschemaxAL2_0AddressLine', True)

    
    AddressLine = property(__AddressLine.value, __AddressLine.set, None, u'Free format address representation. An address can have more than one line. The order of the AddressLine elements must be preserved.')

    
    # Element {urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}ThoroughfareNumberFrom uses Python identifier ThoroughfareNumberFrom
    __ThoroughfareNumberFrom = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'ThoroughfareNumberFrom'), 'ThoroughfareNumberFrom', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_62_urnoasisnamestcciqxsdschemaxAL2_0ThoroughfareNumberFrom', False)

    
    ThoroughfareNumberFrom = property(__ThoroughfareNumberFrom.value, __ThoroughfareNumberFrom.set, None, u'Starting number in the range')

    
    # Attribute Indicator uses Python identifier Indicator
    __Indicator = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Indicator'), 'Indicator', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_62_Indicator', pyxb.binding.datatypes.anySimpleType)
    
    Indicator = property(__Indicator.value, __Indicator.set, None, u'"No." No.12-13')

    
    # Attribute Separator uses Python identifier Separator
    __Separator = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Separator'), 'Separator', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_62_Separator', pyxb.binding.datatypes.anySimpleType)
    
    Separator = property(__Separator.value, __Separator.set, None, u'"-" in 12-14  or "Thru" in 12 Thru 14 etc.')

    
    # Attribute NumberRangeOccurrence uses Python identifier NumberRangeOccurrence
    __NumberRangeOccurrence = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'NumberRangeOccurrence'), 'NumberRangeOccurrence', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_62_NumberRangeOccurrence', STD_ANON_18)
    
    NumberRangeOccurrence = property(__NumberRangeOccurrence.value, __NumberRangeOccurrence.set, None, u'23-25 Archer St, where number appears before name')

    
    # Attribute RangeType uses Python identifier RangeType
    __RangeType = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'RangeType'), 'RangeType', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_62_RangeType', STD_ANON_17)
    
    RangeType = property(__RangeType.value, __RangeType.set, None, u'Thoroughfare number ranges are odd or even')

    
    # Attribute Type uses Python identifier Type
    __Type = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Type'), 'Type', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_62_Type', pyxb.binding.datatypes.anySimpleType)
    
    Type = property(__Type.value, __Type.set, None, None)

    
    # Attribute IndicatorOccurrence uses Python identifier IndicatorOccurrence
    __IndicatorOccurrence = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'IndicatorOccurrence'), 'IndicatorOccurrence', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_62_IndicatorOccurrence', STD_ANON_16)
    
    IndicatorOccurrence = property(__IndicatorOccurrence.value, __IndicatorOccurrence.set, None, u'No.12-14 where "No." is before actual street number')

    
    # Attribute Code uses Python identifier Code
    __Code = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Code'), 'Code', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_62_Code', pyxb.binding.datatypes.anySimpleType)
    
    Code = property(__Code.value, __Code.set, None, u'Used by postal services to encode the name of the element.')

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_strict, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'urn:oasis:names:tc:ciq:xsdschema:xAL:2.0'))

    _ElementMap = {
        __ThoroughfareNumberTo.name() : __ThoroughfareNumberTo,
        __AddressLine.name() : __AddressLine,
        __ThoroughfareNumberFrom.name() : __ThoroughfareNumberFrom
    }
    _AttributeMap = {
        __Indicator.name() : __Indicator,
        __Separator.name() : __Separator,
        __NumberRangeOccurrence.name() : __NumberRangeOccurrence,
        __RangeType.name() : __RangeType,
        __Type.name() : __Type,
        __IndicatorOccurrence.name() : __IndicatorOccurrence,
        __Code.name() : __Code
    }



# Complex type CTD_ANON_63 with content type MIXED
class CTD_ANON_63 (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_MIXED
    _Abstract = False
    _ExpandedName = None
    # Base type is pyxb.binding.datatypes.anyType
    
    # Attribute Code uses Python identifier Code
    __Code = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Code'), 'Code', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_63_Code', pyxb.binding.datatypes.anySimpleType)
    
    Code = property(__Code.value, __Code.set, None, u'Used by postal services to encode the name of the element.')

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_strict, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'urn:oasis:names:tc:ciq:xsdschema:xAL:2.0'))

    _ElementMap = {
        
    }
    _AttributeMap = {
        __Code.name() : __Code
    }



# Complex type CTD_ANON_64 with content type MIXED
class CTD_ANON_64 (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_MIXED
    _Abstract = False
    _ExpandedName = None
    # Base type is pyxb.binding.datatypes.anyType
    
    # Attribute Type uses Python identifier Type
    __Type = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Type'), 'Type', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_64_Type', pyxb.binding.datatypes.anySimpleType)
    
    Type = property(__Type.value, __Type.set, None, u'Specific to postal service')

    
    # Attribute Code uses Python identifier Code
    __Code = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Code'), 'Code', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_64_Code', pyxb.binding.datatypes.anySimpleType)
    
    Code = property(__Code.value, __Code.set, None, u'Used by postal services to encode the name of the element.')

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_strict, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'urn:oasis:names:tc:ciq:xsdschema:xAL:2.0'))

    _ElementMap = {
        
    }
    _AttributeMap = {
        __Type.name() : __Type,
        __Code.name() : __Code
    }



# Complex type CTD_ANON_65 with content type ELEMENT_ONLY
class CTD_ANON_65 (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = None
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}ThoroughfareName uses Python identifier ThoroughfareName
    __ThoroughfareName = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'ThoroughfareName'), 'ThoroughfareName', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_65_urnoasisnamestcciqxsdschemaxAL2_0ThoroughfareName', True)

    
    ThoroughfareName = property(__ThoroughfareName.value, __ThoroughfareName.set, None, u'Specification of the name of a Thoroughfare (also dependant street name): street name, canal name, etc.')

    
    # Element {urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}ThoroughfarePreDirection uses Python identifier ThoroughfarePreDirection
    __ThoroughfarePreDirection = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'ThoroughfarePreDirection'), 'ThoroughfarePreDirection', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_65_urnoasisnamestcciqxsdschemaxAL2_0ThoroughfarePreDirection', False)

    
    ThoroughfarePreDirection = property(__ThoroughfarePreDirection.value, __ThoroughfarePreDirection.set, None, u'North Baker Street, where North is the pre-direction. The direction appears before the name.')

    
    # Element {urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}ThoroughfarePostDirection uses Python identifier ThoroughfarePostDirection
    __ThoroughfarePostDirection = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'ThoroughfarePostDirection'), 'ThoroughfarePostDirection', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_65_urnoasisnamestcciqxsdschemaxAL2_0ThoroughfarePostDirection', False)

    
    ThoroughfarePostDirection = property(__ThoroughfarePostDirection.value, __ThoroughfarePostDirection.set, None, u'221-bis Baker Street North, where North is the post-direction. The post-direction appears after the name.')

    
    # Element {urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}ThoroughfareTrailingType uses Python identifier ThoroughfareTrailingType
    __ThoroughfareTrailingType = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'ThoroughfareTrailingType'), 'ThoroughfareTrailingType', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_65_urnoasisnamestcciqxsdschemaxAL2_0ThoroughfareTrailingType', False)

    
    ThoroughfareTrailingType = property(__ThoroughfareTrailingType.value, __ThoroughfareTrailingType.set, None, u'Appears after the thoroughfare name. Ed. British: Baker Lane, where Lane is the trailing type.')

    
    # Element {urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}ThoroughfareLeadingType uses Python identifier ThoroughfareLeadingType
    __ThoroughfareLeadingType = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'ThoroughfareLeadingType'), 'ThoroughfareLeadingType', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_65_urnoasisnamestcciqxsdschemaxAL2_0ThoroughfareLeadingType', False)

    
    ThoroughfareLeadingType = property(__ThoroughfareLeadingType.value, __ThoroughfareLeadingType.set, None, u'Appears before the thoroughfare name. Ed. Spanish: Avenida Aurora, where Avenida is the leading type / French: Rue Moliere, where Rue is the leading type.')

    
    # Element {urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}AddressLine uses Python identifier AddressLine
    __AddressLine = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'AddressLine'), 'AddressLine', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_65_urnoasisnamestcciqxsdschemaxAL2_0AddressLine', True)

    
    AddressLine = property(__AddressLine.value, __AddressLine.set, None, u'Free format address representation. An address can have more than one line. The order of the AddressLine elements must be preserved.')

    
    # Attribute Type uses Python identifier Type
    __Type = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Type'), 'Type', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_65_Type', pyxb.binding.datatypes.anySimpleType)
    
    Type = property(__Type.value, __Type.set, None, None)

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_strict, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'urn:oasis:names:tc:ciq:xsdschema:xAL:2.0'))
    _HasWildcardElement = True

    _ElementMap = {
        __ThoroughfareName.name() : __ThoroughfareName,
        __ThoroughfarePreDirection.name() : __ThoroughfarePreDirection,
        __ThoroughfarePostDirection.name() : __ThoroughfarePostDirection,
        __ThoroughfareTrailingType.name() : __ThoroughfareTrailingType,
        __ThoroughfareLeadingType.name() : __ThoroughfareLeadingType,
        __AddressLine.name() : __AddressLine
    }
    _AttributeMap = {
        __Type.name() : __Type
    }



# Complex type CTD_ANON_66 with content type ELEMENT_ONLY
class CTD_ANON_66 (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = None
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}AddressLine uses Python identifier AddressLine
    __AddressLine = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'AddressLine'), 'AddressLine', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_66_urnoasisnamestcciqxsdschemaxAL2_0AddressLine', True)

    
    AddressLine = property(__AddressLine.value, __AddressLine.set, None, u'Free format address representation. An address can have more than one line. The order of the AddressLine elements must be preserved.')

    
    # Element {urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}AdministrativeArea uses Python identifier AdministrativeArea
    __AdministrativeArea = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'AdministrativeArea'), 'AdministrativeArea', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_66_urnoasisnamestcciqxsdschemaxAL2_0AdministrativeArea', False)

    
    AdministrativeArea = property(__AdministrativeArea.value, __AdministrativeArea.set, None, u'Examples of administrative areas are provinces counties, special regions (such as "Rijnmond"), etc.')

    
    # Element {urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}CountryName uses Python identifier CountryName
    __CountryName = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'CountryName'), 'CountryName', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_66_urnoasisnamestcciqxsdschemaxAL2_0CountryName', True)

    
    CountryName = property(__CountryName.value, __CountryName.set, None, u'Specification of the name of a country.')

    
    # Element {urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}CountryNameCode uses Python identifier CountryNameCode
    __CountryNameCode = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'CountryNameCode'), 'CountryNameCode', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_66_urnoasisnamestcciqxsdschemaxAL2_0CountryNameCode', True)

    
    CountryNameCode = property(__CountryNameCode.value, __CountryNameCode.set, None, u'A country code according to the specified scheme')

    
    # Element {urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}Locality uses Python identifier Locality
    __Locality = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'Locality'), 'Locality', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_66_urnoasisnamestcciqxsdschemaxAL2_0Locality', False)

    
    Locality = property(__Locality.value, __Locality.set, None, u'Locality is one level lower than adminisstrative area. Eg.: cities, reservations and any other built-up areas.')

    
    # Element {urn:oasis:names:tc:ciq:xsdschema:xAL:2.0}Thoroughfare uses Python identifier Thoroughfare
    __Thoroughfare = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'Thoroughfare'), 'Thoroughfare', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_66_urnoasisnamestcciqxsdschemaxAL2_0Thoroughfare', False)

    
    Thoroughfare = property(__Thoroughfare.value, __Thoroughfare.set, None, u'Specification of a thoroughfare. A thoroughfare could be a rd, street, canal, river, etc.  Note dependentlocality in a street. For example, in some countries, a large street will \nhave many subdivisions with numbers. Normally the subdivision name is the same as the road name, but with a number to identifiy it. Eg. SOI SUKUMVIT 3, SUKUMVIT RD, BANGKOK')

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_strict, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'urn:oasis:names:tc:ciq:xsdschema:xAL:2.0'))
    _HasWildcardElement = True

    _ElementMap = {
        __AddressLine.name() : __AddressLine,
        __AdministrativeArea.name() : __AdministrativeArea,
        __CountryName.name() : __CountryName,
        __CountryNameCode.name() : __CountryNameCode,
        __Locality.name() : __Locality,
        __Thoroughfare.name() : __Thoroughfare
    }
    _AttributeMap = {
        
    }



# Complex type CTD_ANON_67 with content type MIXED
class CTD_ANON_67 (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_MIXED
    _Abstract = False
    _ExpandedName = None
    # Base type is pyxb.binding.datatypes.anyType
    
    # Attribute IdentifierType uses Python identifier IdentifierType
    __IdentifierType = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'IdentifierType'), 'IdentifierType', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_67_IdentifierType', pyxb.binding.datatypes.anySimpleType)
    
    IdentifierType = property(__IdentifierType.value, __IdentifierType.set, None, u'Type of identifier. eg. DPID as in Australia')

    
    # Attribute Code uses Python identifier Code
    __Code = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Code'), 'Code', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_67_Code', pyxb.binding.datatypes.anySimpleType)
    
    Code = property(__Code.value, __Code.set, None, u'Used by postal services to encode the name of the element.')

    
    # Attribute Type uses Python identifier Type
    __Type = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Type'), 'Type', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_67_Type', pyxb.binding.datatypes.anySimpleType)
    
    Type = property(__Type.value, __Type.set, None, None)

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_strict, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'urn:oasis:names:tc:ciq:xsdschema:xAL:2.0'))

    _ElementMap = {
        
    }
    _AttributeMap = {
        __IdentifierType.name() : __IdentifierType,
        __Code.name() : __Code,
        __Type.name() : __Type
    }



# Complex type CTD_ANON_68 with content type MIXED
class CTD_ANON_68 (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_MIXED
    _Abstract = False
    _ExpandedName = None
    # Base type is pyxb.binding.datatypes.anyType
    
    # Attribute Type uses Python identifier Type
    __Type = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Type'), 'Type', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_68_Type', pyxb.binding.datatypes.anySimpleType)
    
    Type = property(__Type.value, __Type.set, None, None)

    
    # Attribute Code uses Python identifier Code
    __Code = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Code'), 'Code', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_68_Code', pyxb.binding.datatypes.anySimpleType)
    
    Code = property(__Code.value, __Code.set, None, u'Used by postal services to encode the name of the element.')

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_strict, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'urn:oasis:names:tc:ciq:xsdschema:xAL:2.0'))

    _ElementMap = {
        
    }
    _AttributeMap = {
        __Type.name() : __Type,
        __Code.name() : __Code
    }



# Complex type CTD_ANON_69 with content type MIXED
class CTD_ANON_69 (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_MIXED
    _Abstract = False
    _ExpandedName = None
    # Base type is pyxb.binding.datatypes.anyType
    
    # Attribute Code uses Python identifier Code
    __Code = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'Code'), 'Code', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_69_Code', pyxb.binding.datatypes.anySimpleType)
    
    Code = property(__Code.value, __Code.set, None, u'Used by postal services to encode the name of the element.')

    
    # Attribute NumberSuffixSeparator uses Python identifier NumberSuffixSeparator
    __NumberSuffixSeparator = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'NumberSuffixSeparator'), 'NumberSuffixSeparator', '__urnoasisnamestcciqxsdschemaxAL2_0_CTD_ANON_69_NumberSuffixSeparator', pyxb.binding.datatypes.anySimpleType)
    
    NumberSuffixSeparator = property(__NumberSuffixSeparator.value, __NumberSuffixSeparator.set, None, u'12-A where 12 is number and A is suffix and "-" is the separator')

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_strict, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'urn:oasis:names:tc:ciq:xsdschema:xAL:2.0'))

    _ElementMap = {
        
    }
    _AttributeMap = {
        __Code.name() : __Code,
        __NumberSuffixSeparator.name() : __NumberSuffixSeparator
    }



Premise = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Premise'), CTD_ANON_3, documentation=u'Specification of a single premise, for example a house or a building. The premise as a whole has a unique premise (house) number or a premise name.  There could be more than \none premise in a street referenced in an address. For example a building address near a major shopping centre or raiwlay station')
Namespace.addCategoryObject('elementBinding', Premise.name().localName(), Premise)

Department = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Department'), CTD_ANON_17, documentation=u'Subdivision in the firm: School of Physics at Victoria University (School of Physics is the department)')
Namespace.addCategoryObject('elementBinding', Department.name().localName(), Department)

CountryName = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'CountryName'), CTD_ANON_, documentation=u'Specification of the name of a country.')
Namespace.addCategoryObject('elementBinding', CountryName.name().localName(), CountryName)

xAL = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'xAL'), CTD_ANON_24, documentation=u'Root element for a list of addresses')
Namespace.addCategoryObject('elementBinding', xAL.name().localName(), xAL)

ThoroughfareNumberPrefix = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'ThoroughfareNumberPrefix'), CTD_ANON_7, documentation=u'Prefix before the number. A in A12 Archer Street')
Namespace.addCategoryObject('elementBinding', ThoroughfareNumberPrefix.name().localName(), ThoroughfareNumberPrefix)

PostalCode = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'PostalCode'), CTD_ANON_4, documentation=u'PostalCode is the container element for either simple or complex (extended) postal codes. Type: Area Code, Postcode, etc.')
Namespace.addCategoryObject('elementBinding', PostalCode.name().localName(), PostalCode)

PremiseNumberSuffix = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'PremiseNumberSuffix'), CTD_ANON_34, documentation=u'A in 12A')
Namespace.addCategoryObject('elementBinding', PremiseNumberSuffix.name().localName(), PremiseNumberSuffix)

AddressDetails = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'AddressDetails'), AddressDetails_, documentation=u'This container defines the details of the address. Can define multiple addresses including tracking address history')
Namespace.addCategoryObject('elementBinding', AddressDetails.name().localName(), AddressDetails)

PostOffice = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'PostOffice'), CTD_ANON_8, documentation=u'Specification of a post office. Examples are a rural post office where post is delivered and a post office containing post office boxes.')
Namespace.addCategoryObject('elementBinding', PostOffice.name().localName(), PostOffice)

ThoroughfareNumber = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'ThoroughfareNumber'), CTD_ANON_20, documentation=u'Eg.: 23 Archer street or 25/15 Zero Avenue, etc')
Namespace.addCategoryObject('elementBinding', ThoroughfareNumber.name().localName(), ThoroughfareNumber)

PremiseNumber = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'PremiseNumber'), CTD_ANON_27, documentation=u'Specification of the identifier of the premise (house, building, etc). Premises in a street are often uniquely identified by means of consecutive identifiers. The identifier can be a number, a letter or any combination of the two.')
Namespace.addCategoryObject('elementBinding', PremiseNumber.name().localName(), PremiseNumber)

Thoroughfare = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Thoroughfare'), CTD_ANON_15, documentation=u'Specification of a thoroughfare. A thoroughfare could be a rd, street, canal, river, etc.  Note dependentlocality in a street. For example, in some countries, a large street will \nhave many subdivisions with numbers. Normally the subdivision name is the same as the road name, but with a number to identifiy it. Eg. SOI SUKUMVIT 3, SUKUMVIT RD, BANGKOK')
Namespace.addCategoryObject('elementBinding', Thoroughfare.name().localName(), Thoroughfare)

Locality = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Locality'), CTD_ANON_45, documentation=u'Locality is one level lower than adminisstrative area. Eg.: cities, reservations and any other built-up areas.')
Namespace.addCategoryObject('elementBinding', Locality.name().localName(), Locality)

PostBox = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'PostBox'), CTD_ANON_11, documentation=u'Specification of a postbox like mail delivery point. Only a single postbox number can be specified. Examples of postboxes are POBox, free mail numbers, etc.')
Namespace.addCategoryObject('elementBinding', PostBox.name().localName(), PostBox)

PremiseNumberPrefix = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'PremiseNumberPrefix'), CTD_ANON_32, documentation=u'A in A12')
Namespace.addCategoryObject('elementBinding', PremiseNumberPrefix.name().localName(), PremiseNumberPrefix)

AdministrativeArea = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'AdministrativeArea'), CTD_ANON_9, documentation=u'Examples of administrative areas are provinces counties, special regions (such as "Rijnmond"), etc.')
Namespace.addCategoryObject('elementBinding', AdministrativeArea.name().localName(), AdministrativeArea)

AddressLine = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'AddressLine'), CTD_ANON, documentation=u'Free format address representation. An address can have more than one line. The order of the AddressLine elements must be preserved.')
Namespace.addCategoryObject('elementBinding', AddressLine.name().localName(), AddressLine)

ThoroughfareNumberSuffix = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'ThoroughfareNumberSuffix'), CTD_ANON_37, documentation=u'Suffix after the number. A in 12A Archer Street')
Namespace.addCategoryObject('elementBinding', ThoroughfareNumberSuffix.name().localName(), ThoroughfareNumberSuffix)



PostalRouteType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'AddressLine'), CTD_ANON, scope=PostalRouteType, documentation=u'Free format address representation. An address can have more than one line. The order of the AddressLine elements must be preserved.'))

PostalRouteType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'PostalRouteName'), CTD_ANON_54, scope=PostalRouteType, documentation=u' Name of the Postal Route'))

PostalRouteType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'PostalRouteNumber'), CTD_ANON_30, scope=PostalRouteType, documentation=u' Number of the Postal Route'))

PostalRouteType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'PostBox'), CTD_ANON_11, scope=PostalRouteType, documentation=u'Specification of a postbox like mail delivery point. Only a single postbox number can be specified. Examples of postboxes are POBox, free mail numbers, etc.'))
PostalRouteType._GroupModel_ = pyxb.binding.content.GroupChoice(
    pyxb.binding.content.ParticleModel(PostalRouteType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'PostalRouteName')), min_occurs=1, max_occurs=None),
    pyxb.binding.content.ParticleModel(PostalRouteType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'PostalRouteNumber')), min_occurs=1, max_occurs=1)
    )
PostalRouteType._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(PostalRouteType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'AddressLine')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(PostalRouteType._GroupModel_, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(PostalRouteType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'PostBox')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_strict, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'urn:oasis:names:tc:ciq:xsdschema:xAL:2.0')), min_occurs=0L, max_occurs=None)
    )
PostalRouteType._ContentModel = pyxb.binding.content.ParticleModel(PostalRouteType._GroupModel, min_occurs=1, max_occurs=1)


CTD_ANON._GroupModel = pyxb.binding.content.GroupSequence(
    
    )
CTD_ANON._ContentModel = pyxb.binding.content.ParticleModel(CTD_ANON._GroupModel, min_occurs=1, max_occurs=1)



DependentLocalityType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'DependentLocalityName'), CTD_ANON_16, scope=DependentLocalityType, documentation=u'Name of the dependent locality'))

DependentLocalityType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Thoroughfare'), CTD_ANON_15, scope=DependentLocalityType, documentation=u'Specification of a thoroughfare. A thoroughfare could be a rd, street, canal, river, etc.  Note dependentlocality in a street. For example, in some countries, a large street will \nhave many subdivisions with numbers. Normally the subdivision name is the same as the road name, but with a number to identifiy it. Eg. SOI SUKUMVIT 3, SUKUMVIT RD, BANGKOK'))

DependentLocalityType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'PostalRoute'), PostalRouteType, scope=DependentLocalityType, documentation=u' A Postal van is specific for a route as in Is`rael, Rural route'))

DependentLocalityType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'PostalCode'), CTD_ANON_4, scope=DependentLocalityType, documentation=u'PostalCode is the container element for either simple or complex (extended) postal codes. Type: Area Code, Postcode, etc.'))

DependentLocalityType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'DependentLocality'), DependentLocalityType, scope=DependentLocalityType, documentation=u'Dependent localities are Districts within cities/towns, locality divisions, postal \ndivisions of cities, suburbs, etc. DependentLocality is a recursive element, but no nesting deeper than two exists (Locality-DependentLocality-DependentLocality).'))

DependentLocalityType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Premise'), CTD_ANON_3, scope=DependentLocalityType, documentation=u'Specification of a single premise, for example a house or a building. The premise as a whole has a unique premise (house) number or a premise name.  There could be more than \none premise in a street referenced in an address. For example a building address near a major shopping centre or raiwlay station'))

DependentLocalityType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'DependentLocalityNumber'), CTD_ANON_2, scope=DependentLocalityType, documentation=u'Number of the dependent locality. Some areas are numbered. Eg. SECTOR 5 in a Suburb as in India or SOI SUKUMVIT 10 as in Thailand'))

DependentLocalityType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'PostOffice'), CTD_ANON_8, scope=DependentLocalityType, documentation=u'Specification of a post office. Examples are a rural post office where post is delivered and a post office containing post office boxes.'))

DependentLocalityType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'AddressLine'), CTD_ANON, scope=DependentLocalityType, documentation=u'Free format address representation. An address can have more than one line. The order of the AddressLine elements must be preserved.'))

DependentLocalityType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'LargeMailUser'), LargeMailUserType, scope=DependentLocalityType, documentation=u'Specification of a large mail user address. Examples of large mail users are postal companies, companies in France with a cedex number, hospitals and airports with their own post code. Large mail user addresses do not have a street name with premise name or premise number in countries like Netherlands. But they have a POBox and street also in countries like France'))

DependentLocalityType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'PostBox'), CTD_ANON_11, scope=DependentLocalityType, documentation=u'Specification of a postbox like mail delivery point. Only a single postbox number can be specified. Examples of postboxes are POBox, free mail numbers, etc.'))
DependentLocalityType._GroupModel_ = pyxb.binding.content.GroupChoice(
    pyxb.binding.content.ParticleModel(DependentLocalityType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'PostBox')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(DependentLocalityType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'LargeMailUser')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(DependentLocalityType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'PostOffice')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(DependentLocalityType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'PostalRoute')), min_occurs=1, max_occurs=1)
    )
DependentLocalityType._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(DependentLocalityType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'AddressLine')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(DependentLocalityType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'DependentLocalityName')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(DependentLocalityType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'DependentLocalityNumber')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(DependentLocalityType._GroupModel_, min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(DependentLocalityType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Thoroughfare')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(DependentLocalityType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Premise')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(DependentLocalityType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'DependentLocality')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(DependentLocalityType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'PostalCode')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_strict, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'urn:oasis:names:tc:ciq:xsdschema:xAL:2.0')), min_occurs=0L, max_occurs=None)
    )
DependentLocalityType._ContentModel = pyxb.binding.content.ParticleModel(DependentLocalityType._GroupModel, min_occurs=1, max_occurs=1)


CTD_ANON_._GroupModel = pyxb.binding.content.GroupSequence(
    
    )
CTD_ANON_._ContentModel = pyxb.binding.content.ParticleModel(CTD_ANON_._GroupModel, min_occurs=1, max_occurs=1)


CTD_ANON_2._GroupModel = pyxb.binding.content.GroupSequence(
    
    )
CTD_ANON_2._ContentModel = pyxb.binding.content.ParticleModel(CTD_ANON_2._GroupModel, min_occurs=0L, max_occurs=1)



CTD_ANON_3._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'PremiseNumber'), CTD_ANON_27, scope=CTD_ANON_3, documentation=u'Specification of the identifier of the premise (house, building, etc). Premises in a street are often uniquely identified by means of consecutive identifiers. The identifier can be a number, a letter or any combination of the two.'))

CTD_ANON_3._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'PostalCode'), CTD_ANON_4, scope=CTD_ANON_3, documentation=u'PostalCode is the container element for either simple or complex (extended) postal codes. Type: Area Code, Postcode, etc.'))

CTD_ANON_3._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Firm'), FirmType, scope=CTD_ANON_3, documentation=u'Specification of a firm, company, organization, etc. It can be specified as part of an address that contains a street or a postbox. It is therefore different from a large mail user address, which contains no street.'))

CTD_ANON_3._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'MailStop'), MailStopType, scope=CTD_ANON_3, documentation=u'A MailStop is where the the mail is delivered to within a premise/subpremise/firm or a facility.'))

CTD_ANON_3._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'AddressLine'), CTD_ANON, scope=CTD_ANON_3, documentation=u'Free format address representation. An address can have more than one line. The order of the AddressLine elements must be preserved.'))

CTD_ANON_3._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'PremiseNumberSuffix'), CTD_ANON_34, scope=CTD_ANON_3, documentation=u'A in 12A'))

CTD_ANON_3._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'SubPremise'), SubPremiseType, scope=CTD_ANON_3, documentation=u'Specification of a single sub-premise. Examples of sub-premises are apartments and suites. Each sub-premise should be uniquely identifiable.'))

CTD_ANON_3._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'PremiseLocation'), CTD_ANON_63, scope=CTD_ANON_3, documentation=u'LOBBY, BASEMENT, GROUND FLOOR, etc...'))

CTD_ANON_3._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'BuildingName'), BuildingNameType, scope=CTD_ANON_3, documentation=u'Specification of the name of a building.'))

CTD_ANON_3._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'PremiseNumberRange'), CTD_ANON_21, scope=CTD_ANON_3, documentation=u'Specification for defining the premise number range. Some premises have number as Building C1-C7'))

CTD_ANON_3._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Premise'), CTD_ANON_3, scope=CTD_ANON_3, documentation=u'Specification of a single premise, for example a house or a building. The premise as a whole has a unique premise (house) number or a premise name.  There could be more than \none premise in a street referenced in an address. For example a building address near a major shopping centre or raiwlay station'))

CTD_ANON_3._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'PremiseName'), CTD_ANON_12, scope=CTD_ANON_3, documentation=u'Specification of the name of the premise (house, building, park, farm, etc). A premise name is specified when the premise cannot be addressed using a street name plus premise (house) number.'))

CTD_ANON_3._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'PremiseNumberPrefix'), CTD_ANON_32, scope=CTD_ANON_3, documentation=u'A in A12'))
CTD_ANON_3._GroupModel_2 = pyxb.binding.content.GroupChoice(
    pyxb.binding.content.ParticleModel(CTD_ANON_3._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'PremiseNumber')), min_occurs=1, max_occurs=None),
    pyxb.binding.content.ParticleModel(CTD_ANON_3._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'PremiseNumberRange')), min_occurs=1, max_occurs=1)
    )
CTD_ANON_3._GroupModel_ = pyxb.binding.content.GroupChoice(
    pyxb.binding.content.ParticleModel(CTD_ANON_3._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'PremiseLocation')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(CTD_ANON_3._GroupModel_2, min_occurs=1, max_occurs=1)
    )
CTD_ANON_3._GroupModel_3 = pyxb.binding.content.GroupChoice(
    pyxb.binding.content.ParticleModel(CTD_ANON_3._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'SubPremise')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(CTD_ANON_3._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Firm')), min_occurs=0L, max_occurs=1)
    )
CTD_ANON_3._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(CTD_ANON_3._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'AddressLine')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(CTD_ANON_3._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'PremiseName')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(CTD_ANON_3._GroupModel_, min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(CTD_ANON_3._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'PremiseNumberPrefix')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(CTD_ANON_3._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'PremiseNumberSuffix')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(CTD_ANON_3._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'BuildingName')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(CTD_ANON_3._GroupModel_3, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(CTD_ANON_3._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'MailStop')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(CTD_ANON_3._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'PostalCode')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(CTD_ANON_3._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Premise')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_strict, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'urn:oasis:names:tc:ciq:xsdschema:xAL:2.0')), min_occurs=0L, max_occurs=None)
    )
CTD_ANON_3._ContentModel = pyxb.binding.content.ParticleModel(CTD_ANON_3._GroupModel, min_occurs=1, max_occurs=1)



CTD_ANON_4._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'AddressLine'), CTD_ANON, scope=CTD_ANON_4, documentation=u'Free format address representation. An address can have more than one line. The order of the AddressLine elements must be preserved.'))

CTD_ANON_4._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'PostalCodeNumberExtension'), CTD_ANON_19, scope=CTD_ANON_4, documentation=u'Examples are: 1234 (USA), 1G (UK), etc.'))

CTD_ANON_4._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'PostTown'), CTD_ANON_23, scope=CTD_ANON_4, documentation=u'A post town is not the same as a locality. A post town can encompass a collection of (small) localities. It can also be a subpart of a locality. An actual post town in Norway is "Bergen".'))

CTD_ANON_4._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'PostalCodeNumber'), CTD_ANON_40, scope=CTD_ANON_4, documentation=u'Specification of a postcode. The postcode is formatted according to country-specific rules. Example: SW3 0A8-1A, 600074, 2067'))
CTD_ANON_4._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(CTD_ANON_4._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'AddressLine')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(CTD_ANON_4._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'PostalCodeNumber')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(CTD_ANON_4._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'PostalCodeNumberExtension')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(CTD_ANON_4._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'PostTown')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_strict, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'urn:oasis:names:tc:ciq:xsdschema:xAL:2.0')), min_occurs=0L, max_occurs=None)
    )
CTD_ANON_4._ContentModel = pyxb.binding.content.ParticleModel(CTD_ANON_4._GroupModel, min_occurs=1, max_occurs=1)


CTD_ANON_5._GroupModel = pyxb.binding.content.GroupSequence(
    
    )
CTD_ANON_5._ContentModel = pyxb.binding.content.ParticleModel(CTD_ANON_5._GroupModel, min_occurs=0L, max_occurs=1)


CTD_ANON_6._GroupModel = pyxb.binding.content.GroupSequence(
    
    )
CTD_ANON_6._ContentModel = pyxb.binding.content.ParticleModel(CTD_ANON_6._GroupModel, min_occurs=1, max_occurs=1)


CTD_ANON_7._GroupModel = pyxb.binding.content.GroupSequence(
    
    )
CTD_ANON_7._ContentModel = pyxb.binding.content.ParticleModel(CTD_ANON_7._GroupModel, min_occurs=1, max_occurs=1)


ThoroughfareNameType._GroupModel = pyxb.binding.content.GroupSequence(
    
    )
ThoroughfareNameType._ContentModel = pyxb.binding.content.ParticleModel(ThoroughfareNameType._GroupModel, min_occurs=1, max_occurs=1)



CTD_ANON_8._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'PostalRoute'), PostalRouteType, scope=CTD_ANON_8, documentation=u'A Postal van is specific for a route as in Is`rael, Rural route'))

CTD_ANON_8._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'PostOfficeNumber'), CTD_ANON_10, scope=CTD_ANON_8, documentation=u'Specification of the number of the postoffice. Common in rural postoffices'))

CTD_ANON_8._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'PostBox'), CTD_ANON_11, scope=CTD_ANON_8, documentation=u'Specification of a postbox like mail delivery point. Only a single postbox number can be specified. Examples of postboxes are POBox, free mail numbers, etc.'))

CTD_ANON_8._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'PostOfficeName'), CTD_ANON_52, scope=CTD_ANON_8, documentation=u'Specification of the name of the post office. This can be a rural postoffice where post is delivered or a post office containing post office boxes.'))

CTD_ANON_8._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'PostalCode'), CTD_ANON_4, scope=CTD_ANON_8, documentation=u'PostalCode is the container element for either simple or complex (extended) postal codes. Type: Area Code, Postcode, etc.'))

CTD_ANON_8._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'AddressLine'), CTD_ANON, scope=CTD_ANON_8, documentation=u'Free format address representation. An address can have more than one line. The order of the AddressLine elements must be preserved.'))
CTD_ANON_8._GroupModel_ = pyxb.binding.content.GroupChoice(
    pyxb.binding.content.ParticleModel(CTD_ANON_8._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'PostOfficeName')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(CTD_ANON_8._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'PostOfficeNumber')), min_occurs=0L, max_occurs=1)
    )
CTD_ANON_8._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(CTD_ANON_8._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'AddressLine')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(CTD_ANON_8._GroupModel_, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(CTD_ANON_8._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'PostalRoute')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(CTD_ANON_8._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'PostBox')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(CTD_ANON_8._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'PostalCode')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_strict, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'urn:oasis:names:tc:ciq:xsdschema:xAL:2.0')), min_occurs=0L, max_occurs=None)
    )
CTD_ANON_8._ContentModel = pyxb.binding.content.ParticleModel(CTD_ANON_8._GroupModel, min_occurs=1, max_occurs=1)



CTD_ANON_9._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'PostOffice'), CTD_ANON_8, scope=CTD_ANON_9, documentation=u'Specification of a post office. Examples are a rural post office where post is delivered and a post office containing post office boxes.'))

CTD_ANON_9._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'PostalCode'), CTD_ANON_4, scope=CTD_ANON_9, documentation=u'PostalCode is the container element for either simple or complex (extended) postal codes. Type: Area Code, Postcode, etc.'))

CTD_ANON_9._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'AdministrativeAreaName'), CTD_ANON_53, scope=CTD_ANON_9, documentation=u' Name of the administrative area. eg. MI in USA, NSW in Australia'))

CTD_ANON_9._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'AddressLine'), CTD_ANON, scope=CTD_ANON_9, documentation=u'Free format address representation. An address can have more than one line. The order of the AddressLine elements must be preserved.'))

CTD_ANON_9._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Locality'), CTD_ANON_45, scope=CTD_ANON_9, documentation=u'Locality is one level lower than adminisstrative area. Eg.: cities, reservations and any other built-up areas.'))

CTD_ANON_9._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'SubAdministrativeArea'), CTD_ANON_60, scope=CTD_ANON_9, documentation=u' Specification of a sub-administrative area. An example of a sub-administrative areas is a county. There are two places where the name of an administrative \narea can be specified and in this case, one becomes sub-administrative area.'))
CTD_ANON_9._GroupModel_ = pyxb.binding.content.GroupChoice(
    pyxb.binding.content.ParticleModel(CTD_ANON_9._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Locality')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(CTD_ANON_9._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'PostOffice')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(CTD_ANON_9._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'PostalCode')), min_occurs=1, max_occurs=1)
    )
CTD_ANON_9._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(CTD_ANON_9._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'AddressLine')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(CTD_ANON_9._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'AdministrativeAreaName')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(CTD_ANON_9._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'SubAdministrativeArea')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(CTD_ANON_9._GroupModel_, min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_strict, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'urn:oasis:names:tc:ciq:xsdschema:xAL:2.0')), min_occurs=0L, max_occurs=None)
    )
CTD_ANON_9._ContentModel = pyxb.binding.content.ParticleModel(CTD_ANON_9._GroupModel, min_occurs=1, max_occurs=1)


CTD_ANON_10._GroupModel = pyxb.binding.content.GroupSequence(
    
    )
CTD_ANON_10._ContentModel = pyxb.binding.content.ParticleModel(CTD_ANON_10._GroupModel, min_occurs=0L, max_occurs=1)



CTD_ANON_11._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'PostalCode'), CTD_ANON_4, scope=CTD_ANON_11, documentation=u'PostalCode is the container element for either simple or complex (extended) postal codes. Type: Area Code, Postcode, etc.'))

CTD_ANON_11._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'PostBoxNumberPrefix'), CTD_ANON_13, scope=CTD_ANON_11, documentation=u'Specification of the prefix of the post box number. eg. A in POBox:A-123'))

CTD_ANON_11._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'AddressLine'), CTD_ANON, scope=CTD_ANON_11, documentation=u'Free format address representation. An address can have more than one line. The order of the AddressLine elements must be preserved.'))

CTD_ANON_11._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'PostBoxNumber'), CTD_ANON_6, scope=CTD_ANON_11, documentation=u'Specification of the number of a postbox'))

CTD_ANON_11._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'PostBoxNumberExtension'), CTD_ANON_35, scope=CTD_ANON_11, documentation=u'Some countries like USA have POBox as 12345-123'))

CTD_ANON_11._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Firm'), FirmType, scope=CTD_ANON_11, documentation=u'Specification of a firm, company, organization, etc. It can be specified as part of an address that contains a street or a postbox. It is therefore different from \na large mail user address, which contains no street.'))

CTD_ANON_11._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'PostBoxNumberSuffix'), CTD_ANON_69, scope=CTD_ANON_11, documentation=u'Specification of the suffix of the post box number. eg. A in POBox:123A'))
CTD_ANON_11._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(CTD_ANON_11._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'AddressLine')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(CTD_ANON_11._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'PostBoxNumber')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(CTD_ANON_11._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'PostBoxNumberPrefix')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(CTD_ANON_11._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'PostBoxNumberSuffix')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(CTD_ANON_11._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'PostBoxNumberExtension')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(CTD_ANON_11._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Firm')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(CTD_ANON_11._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'PostalCode')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_strict, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'urn:oasis:names:tc:ciq:xsdschema:xAL:2.0')), min_occurs=0L, max_occurs=None)
    )
CTD_ANON_11._ContentModel = pyxb.binding.content.ParticleModel(CTD_ANON_11._GroupModel, min_occurs=1, max_occurs=1)


CTD_ANON_12._GroupModel = pyxb.binding.content.GroupSequence(
    
    )
CTD_ANON_12._ContentModel = pyxb.binding.content.ParticleModel(CTD_ANON_12._GroupModel, min_occurs=0L, max_occurs=None)


CTD_ANON_13._GroupModel = pyxb.binding.content.GroupSequence(
    
    )
CTD_ANON_13._ContentModel = pyxb.binding.content.ParticleModel(CTD_ANON_13._GroupModel, min_occurs=0L, max_occurs=1)


CTD_ANON_14._GroupModel = pyxb.binding.content.GroupSequence(
    
    )
CTD_ANON_14._ContentModel = pyxb.binding.content.ParticleModel(CTD_ANON_14._GroupModel, min_occurs=0L, max_occurs=None)



CTD_ANON_15._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'DependentLocality'), DependentLocalityType, scope=CTD_ANON_15, documentation=u'Dependent localities are Districts within cities/towns, locality divisions, postal \ndivisions of cities, suburbs, etc. DependentLocality is a recursive element, but no nesting deeper than two exists (Locality-DependentLocality-DependentLocality).'))

CTD_ANON_15._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'ThoroughfareNumberRange'), CTD_ANON_62, scope=CTD_ANON_15, documentation=u'A container to represent a range of numbers (from x thru y)for a thoroughfare. eg. 1-2 Albert Av'))

CTD_ANON_15._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'PostalCode'), CTD_ANON_4, scope=CTD_ANON_15, documentation=u'PostalCode is the container element for either simple or complex (extended) postal codes. Type: Area Code, Postcode, etc.'))

CTD_ANON_15._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'DependentThoroughfare'), CTD_ANON_65, scope=CTD_ANON_15, documentation=u'DependentThroughfare is related to a street; occurs in GB, IE, ES, PT'))

CTD_ANON_15._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'ThoroughfareName'), ThoroughfareNameType, scope=CTD_ANON_15, documentation=u'Specification of the name of a Thoroughfare (also dependant street name): street name, canal name, etc.'))

CTD_ANON_15._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'ThoroughfarePreDirection'), ThoroughfarePreDirectionType, scope=CTD_ANON_15, documentation=u'North Baker Street, where North is the pre-direction. The direction appears before the name.'))

CTD_ANON_15._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'ThoroughfareNumber'), CTD_ANON_20, scope=CTD_ANON_15, documentation=u'Eg.: 23 Archer street or 25/15 Zero Avenue, etc'))

CTD_ANON_15._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Firm'), FirmType, scope=CTD_ANON_15, documentation=u'Specification of a firm, company, organization, etc. It can be specified as part of an address that contains a street or a postbox. It is therefore different from \na large mail user address, which contains no street.'))

CTD_ANON_15._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'ThoroughfareTrailingType'), ThoroughfareTrailingTypeType, scope=CTD_ANON_15, documentation=u'Appears after the thoroughfare name. Ed. British: Baker Lane, where Lane is the trailing type.'))

CTD_ANON_15._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'AddressLine'), CTD_ANON, scope=CTD_ANON_15, documentation=u'Free format address representation. An address can have more than one line. The order of the AddressLine elements must be preserved.'))

CTD_ANON_15._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'ThoroughfareLeadingType'), ThoroughfareLeadingTypeType, scope=CTD_ANON_15, documentation=u'Appears before the thoroughfare name. Ed. Spanish: Avenida Aurora, where Avenida is the leading type / French: Rue Moliere, where Rue is the leading type.'))

CTD_ANON_15._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'ThoroughfareNumberSuffix'), CTD_ANON_37, scope=CTD_ANON_15, documentation=u'Suffix after the number. A in 12A Archer Street'))

CTD_ANON_15._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Premise'), CTD_ANON_3, scope=CTD_ANON_15, documentation=u'Specification of a single premise, for example a house or a building. The premise as a whole has a unique premise (house) number or a premise name.  There could be more than \none premise in a street referenced in an address. For example a building address near a major shopping centre or raiwlay station'))

CTD_ANON_15._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'ThoroughfarePostDirection'), ThoroughfarePostDirectionType, scope=CTD_ANON_15, documentation=u'221-bis Baker Street North, where North is the post-direction. The post-direction appears after the name.'))

CTD_ANON_15._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'ThoroughfareNumberPrefix'), CTD_ANON_7, scope=CTD_ANON_15, documentation=u'Prefix before the number. A in A12 Archer Street'))
CTD_ANON_15._GroupModel_ = pyxb.binding.content.GroupChoice(
    pyxb.binding.content.ParticleModel(CTD_ANON_15._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'ThoroughfareNumber')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(CTD_ANON_15._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'ThoroughfareNumberRange')), min_occurs=1, max_occurs=1)
    )
CTD_ANON_15._GroupModel_2 = pyxb.binding.content.GroupChoice(
    pyxb.binding.content.ParticleModel(CTD_ANON_15._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'DependentLocality')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(CTD_ANON_15._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Premise')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(CTD_ANON_15._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Firm')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(CTD_ANON_15._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'PostalCode')), min_occurs=1, max_occurs=1)
    )
CTD_ANON_15._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(CTD_ANON_15._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'AddressLine')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(CTD_ANON_15._GroupModel_, min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(CTD_ANON_15._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'ThoroughfareNumberPrefix')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(CTD_ANON_15._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'ThoroughfareNumberSuffix')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(CTD_ANON_15._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'ThoroughfarePreDirection')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(CTD_ANON_15._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'ThoroughfareLeadingType')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(CTD_ANON_15._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'ThoroughfareName')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(CTD_ANON_15._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'ThoroughfareTrailingType')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(CTD_ANON_15._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'ThoroughfarePostDirection')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(CTD_ANON_15._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'DependentThoroughfare')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(CTD_ANON_15._GroupModel_2, min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_strict, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'urn:oasis:names:tc:ciq:xsdschema:xAL:2.0')), min_occurs=0L, max_occurs=None)
    )
CTD_ANON_15._ContentModel = pyxb.binding.content.ParticleModel(CTD_ANON_15._GroupModel, min_occurs=1, max_occurs=1)


CTD_ANON_16._GroupModel = pyxb.binding.content.GroupSequence(
    
    )
CTD_ANON_16._ContentModel = pyxb.binding.content.ParticleModel(CTD_ANON_16._GroupModel, min_occurs=0L, max_occurs=None)



CTD_ANON_17._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'DepartmentName'), CTD_ANON_36, scope=CTD_ANON_17, documentation=u'Specification of the name of a department.'))

CTD_ANON_17._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'PostalCode'), CTD_ANON_4, scope=CTD_ANON_17, documentation=u'PostalCode is the container element for either simple or complex (extended) postal codes. Type: Area Code, Postcode, etc.'))

CTD_ANON_17._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'AddressLine'), CTD_ANON, scope=CTD_ANON_17, documentation=u'Free format address representation. An address can have more than one line. The order of the AddressLine elements must be preserved.'))

CTD_ANON_17._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'MailStop'), MailStopType, scope=CTD_ANON_17, documentation=u'A MailStop is where the the mail is delivered to within a premise/subpremise/firm or a facility.'))
CTD_ANON_17._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(CTD_ANON_17._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'AddressLine')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(CTD_ANON_17._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'DepartmentName')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(CTD_ANON_17._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'MailStop')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(CTD_ANON_17._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'PostalCode')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_strict, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'urn:oasis:names:tc:ciq:xsdschema:xAL:2.0')), min_occurs=0L, max_occurs=None)
    )
CTD_ANON_17._ContentModel = pyxb.binding.content.ParticleModel(CTD_ANON_17._GroupModel, min_occurs=1, max_occurs=1)



FirmType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'AddressLine'), CTD_ANON, scope=FirmType, documentation=u'Free format address representation. An address can have more than one line. The order of the AddressLine elements must be preserved.'))

FirmType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'FirmName'), CTD_ANON_49, scope=FirmType, documentation=u'Name of the firm'))

FirmType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'MailStop'), MailStopType, scope=FirmType, documentation=u'A MailStop is where the the mail is delivered to within a premise/subpremise/firm or a facility.'))

FirmType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Department'), CTD_ANON_17, scope=FirmType, documentation=u'Subdivision in the firm: School of Physics at Victoria University (School of Physics is the department)'))

FirmType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'PostalCode'), CTD_ANON_4, scope=FirmType, documentation=u'PostalCode is the container element for either simple or complex (extended) postal codes. Type: Area Code, Postcode, etc.'))
FirmType._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(FirmType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'AddressLine')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(FirmType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'FirmName')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(FirmType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Department')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(FirmType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'MailStop')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(FirmType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'PostalCode')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_strict, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'urn:oasis:names:tc:ciq:xsdschema:xAL:2.0')), min_occurs=0L, max_occurs=None)
    )
FirmType._ContentModel = pyxb.binding.content.ParticleModel(FirmType._GroupModel, min_occurs=1, max_occurs=1)


CTD_ANON_18._GroupModel = pyxb.binding.content.GroupSequence(
    
    )
CTD_ANON_18._ContentModel = pyxb.binding.content.ParticleModel(CTD_ANON_18._GroupModel, min_occurs=0L, max_occurs=None)


CTD_ANON_19._GroupModel = pyxb.binding.content.GroupSequence(
    
    )
CTD_ANON_19._ContentModel = pyxb.binding.content.ParticleModel(CTD_ANON_19._GroupModel, min_occurs=0L, max_occurs=None)


CTD_ANON_20._GroupModel = pyxb.binding.content.GroupSequence(
    
    )
CTD_ANON_20._ContentModel = pyxb.binding.content.ParticleModel(CTD_ANON_20._GroupModel, min_occurs=1, max_occurs=1)



CTD_ANON_21._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'PremiseNumberRangeFrom'), CTD_ANON_44, scope=CTD_ANON_21, documentation=u'Start number details of the premise number range'))

CTD_ANON_21._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'PremiseNumberRangeTo'), CTD_ANON_48, scope=CTD_ANON_21, documentation=u'End number details of the premise number range'))
CTD_ANON_21._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(CTD_ANON_21._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'PremiseNumberRangeFrom')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(CTD_ANON_21._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'PremiseNumberRangeTo')), min_occurs=1, max_occurs=1)
    )
CTD_ANON_21._ContentModel = pyxb.binding.content.ParticleModel(CTD_ANON_21._GroupModel, min_occurs=1, max_occurs=1)



MailStopType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'MailStopName'), CTD_ANON_39, scope=MailStopType, documentation=u'Name of the the Mail Stop. eg. MSP, MS, etc'))

MailStopType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'AddressLine'), CTD_ANON, scope=MailStopType, documentation=u'Free format address representation. An address can have more than one line. The order of the AddressLine elements must be preserved.'))

MailStopType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'MailStopNumber'), CTD_ANON_59, scope=MailStopType, documentation=u'Number of the Mail stop. eg. 123 in MS 123'))
MailStopType._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(MailStopType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'AddressLine')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(MailStopType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'MailStopName')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(MailStopType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'MailStopNumber')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_strict, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'urn:oasis:names:tc:ciq:xsdschema:xAL:2.0')), min_occurs=0L, max_occurs=None)
    )
MailStopType._ContentModel = pyxb.binding.content.ParticleModel(MailStopType._GroupModel, min_occurs=1, max_occurs=1)


CTD_ANON_22._GroupModel = pyxb.binding.content.GroupSequence(
    
    )
CTD_ANON_22._ContentModel = pyxb.binding.content.ParticleModel(CTD_ANON_22._GroupModel, min_occurs=0L, max_occurs=1)



CTD_ANON_23._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'PostTownSuffix'), CTD_ANON_33, scope=CTD_ANON_23, documentation=u'GENERAL PO in MIAMI GENERAL PO'))

CTD_ANON_23._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'AddressLine'), CTD_ANON, scope=CTD_ANON_23, documentation=u'Free format address representation. An address can have more than one line. The order of the AddressLine elements must be preserved.'))

CTD_ANON_23._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'PostTownName'), CTD_ANON_28, scope=CTD_ANON_23, documentation=u'Name of the post town'))
CTD_ANON_23._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(CTD_ANON_23._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'AddressLine')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(CTD_ANON_23._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'PostTownName')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(CTD_ANON_23._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'PostTownSuffix')), min_occurs=0L, max_occurs=1)
    )
CTD_ANON_23._ContentModel = pyxb.binding.content.ParticleModel(CTD_ANON_23._GroupModel, min_occurs=1, max_occurs=1)



CTD_ANON_24._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'AddressDetails'), AddressDetails_, scope=CTD_ANON_24, documentation=u'This container defines the details of the address. Can define multiple addresses including tracking address history'))
CTD_ANON_24._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(CTD_ANON_24._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'AddressDetails')), min_occurs=1, max_occurs=None),
    pyxb.binding.content.ParticleModel(pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_strict, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'urn:oasis:names:tc:ciq:xsdschema:xAL:2.0')), min_occurs=0L, max_occurs=None)
    )
CTD_ANON_24._ContentModel = pyxb.binding.content.ParticleModel(CTD_ANON_24._GroupModel, min_occurs=1, max_occurs=1)


CTD_ANON_25._GroupModel = pyxb.binding.content.GroupSequence(
    
    )
CTD_ANON_25._ContentModel = pyxb.binding.content.ParticleModel(CTD_ANON_25._GroupModel, min_occurs=0L, max_occurs=None)


CTD_ANON_26._GroupModel = pyxb.binding.content.GroupSequence(
    
    )
CTD_ANON_26._ContentModel = pyxb.binding.content.ParticleModel(CTD_ANON_26._GroupModel, min_occurs=0L, max_occurs=None)


CTD_ANON_27._GroupModel = pyxb.binding.content.GroupSequence(
    
    )
CTD_ANON_27._ContentModel = pyxb.binding.content.ParticleModel(CTD_ANON_27._GroupModel, min_occurs=1, max_occurs=1)


CTD_ANON_28._GroupModel = pyxb.binding.content.GroupSequence(
    
    )
CTD_ANON_28._ContentModel = pyxb.binding.content.ParticleModel(CTD_ANON_28._GroupModel, min_occurs=0L, max_occurs=None)



CTD_ANON_29._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'AddressLongitude'), CTD_ANON_64, scope=CTD_ANON_29, documentation=u'Longtitude of delivery address'))

CTD_ANON_29._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'AddressLongitudeDirection'), CTD_ANON_41, scope=CTD_ANON_29, documentation=u'Longtitude direction of delivery address;N=North and S=South'))

CTD_ANON_29._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'SupplementaryPostalServiceData'), CTD_ANON_14, scope=CTD_ANON_29, documentation=u'any postal service elements not covered by the container can be represented using this element'))

CTD_ANON_29._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'SortingCode'), CTD_ANON_38, scope=CTD_ANON_29, documentation=u'Used for sorting addresses. Values may for example be CEDEX 16 (France)'))

CTD_ANON_29._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'EndorsementLineCode'), CTD_ANON_43, scope=CTD_ANON_29, documentation=u'Directly affects postal service distribution'))

CTD_ANON_29._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'KeyLineCode'), CTD_ANON_47, scope=CTD_ANON_29, documentation=u'Required for some postal services'))

CTD_ANON_29._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'AddressLatitude'), CTD_ANON_56, scope=CTD_ANON_29, documentation=u'Latitude of delivery address'))

CTD_ANON_29._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Barcode'), CTD_ANON_5, scope=CTD_ANON_29, documentation=u'Required for some postal services'))

CTD_ANON_29._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'AddressIdentifier'), CTD_ANON_67, scope=CTD_ANON_29, documentation=u'A unique identifier of an address assigned by postal authorities. Example: DPID in Australia'))

CTD_ANON_29._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'AddressLatitudeDirection'), CTD_ANON_22, scope=CTD_ANON_29, documentation=u'Latitude direction of delivery address;N = North and S = South'))
CTD_ANON_29._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(CTD_ANON_29._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'AddressIdentifier')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(CTD_ANON_29._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'EndorsementLineCode')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(CTD_ANON_29._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'KeyLineCode')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(CTD_ANON_29._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Barcode')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(CTD_ANON_29._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'SortingCode')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(CTD_ANON_29._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'AddressLatitude')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(CTD_ANON_29._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'AddressLatitudeDirection')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(CTD_ANON_29._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'AddressLongitude')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(CTD_ANON_29._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'AddressLongitudeDirection')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(CTD_ANON_29._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'SupplementaryPostalServiceData')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_strict, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'urn:oasis:names:tc:ciq:xsdschema:xAL:2.0')), min_occurs=0L, max_occurs=None)
    )
CTD_ANON_29._ContentModel = pyxb.binding.content.ParticleModel(CTD_ANON_29._GroupModel, min_occurs=1, max_occurs=1)


CTD_ANON_30._GroupModel = pyxb.binding.content.GroupSequence(
    
    )
CTD_ANON_30._ContentModel = pyxb.binding.content.ParticleModel(CTD_ANON_30._GroupModel, min_occurs=1, max_occurs=1)


CTD_ANON_31._GroupModel = pyxb.binding.content.GroupSequence(
    
    )
CTD_ANON_31._ContentModel = pyxb.binding.content.ParticleModel(CTD_ANON_31._GroupModel, min_occurs=0L, max_occurs=None)


CTD_ANON_33._GroupModel = pyxb.binding.content.GroupSequence(
    
    )
CTD_ANON_33._ContentModel = pyxb.binding.content.ParticleModel(CTD_ANON_33._GroupModel, min_occurs=0L, max_occurs=1)


CTD_ANON_34._GroupModel = pyxb.binding.content.GroupSequence(
    
    )
CTD_ANON_34._ContentModel = pyxb.binding.content.ParticleModel(CTD_ANON_34._GroupModel, min_occurs=1, max_occurs=1)


CTD_ANON_35._GroupModel = pyxb.binding.content.GroupSequence(
    
    )
CTD_ANON_35._ContentModel = pyxb.binding.content.ParticleModel(CTD_ANON_35._GroupModel, min_occurs=0L, max_occurs=1)


CTD_ANON_36._GroupModel = pyxb.binding.content.GroupSequence(
    
    )
CTD_ANON_36._ContentModel = pyxb.binding.content.ParticleModel(CTD_ANON_36._GroupModel, min_occurs=0L, max_occurs=None)



LargeMailUserType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Thoroughfare'), CTD_ANON_15, scope=LargeMailUserType, documentation=u'Specification of a thoroughfare. A thoroughfare could be a rd, street, canal, river, etc.  Note dependentlocality in a street. For example, in some countries, a large street will \nhave many subdivisions with numbers. Normally the subdivision name is the same as the road name, but with a number to identifiy it. Eg. SOI SUKUMVIT 3, SUKUMVIT RD, BANGKOK'))

LargeMailUserType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'BuildingName'), BuildingNameType, scope=LargeMailUserType, documentation=u'Name of the building'))

LargeMailUserType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'LargeMailUserName'), CTD_ANON_25, scope=LargeMailUserType, documentation=u'Name of the large mail user. eg. Smith Ford International airport'))

LargeMailUserType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Department'), CTD_ANON_17, scope=LargeMailUserType, documentation=u'Subdivision in the firm: School of Physics at Victoria University (School of Physics is the department)'))

LargeMailUserType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'PostalCode'), CTD_ANON_4, scope=LargeMailUserType, documentation=u'PostalCode is the container element for either simple or complex (extended) postal codes. Type: Area Code, Postcode, etc.'))

LargeMailUserType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'AddressLine'), CTD_ANON, scope=LargeMailUserType, documentation=u'Free format address representation. An address can have more than one line. The order of the AddressLine elements must be preserved.'))

LargeMailUserType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'PostBox'), CTD_ANON_11, scope=LargeMailUserType, documentation=u'Specification of a postbox like mail delivery point. Only a single postbox number can be specified. Examples of postboxes are POBox, free mail numbers, etc.'))

LargeMailUserType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'LargeMailUserIdentifier'), CTD_ANON_55, scope=LargeMailUserType, documentation=u'Specification of the identification number of a large mail user. An example are the Cedex codes in France.'))
LargeMailUserType._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(LargeMailUserType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'AddressLine')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(LargeMailUserType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'LargeMailUserName')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(LargeMailUserType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'LargeMailUserIdentifier')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(LargeMailUserType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'BuildingName')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(LargeMailUserType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Department')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(LargeMailUserType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'PostBox')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(LargeMailUserType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Thoroughfare')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(LargeMailUserType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'PostalCode')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_strict, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'urn:oasis:names:tc:ciq:xsdschema:xAL:2.0')), min_occurs=0L, max_occurs=None)
    )
LargeMailUserType._ContentModel = pyxb.binding.content.ParticleModel(LargeMailUserType._GroupModel, min_occurs=1, max_occurs=1)



AddressDetails_._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Address'), CTD_ANON_51, scope=AddressDetails_, documentation=u'Address as one line of free text'))

AddressDetails_._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'AddressLines'), AddressLinesType, scope=AddressDetails_, documentation=u'Container for Address lines'))

AddressDetails_._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'AdministrativeArea'), CTD_ANON_9, scope=AddressDetails_, documentation=u'Examples of administrative areas are provinces counties, special regions (such as "Rijnmond"), etc.'))

AddressDetails_._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Locality'), CTD_ANON_45, scope=AddressDetails_, documentation=u'Locality is one level lower than adminisstrative area. Eg.: cities, reservations and any other built-up areas.'))

AddressDetails_._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'PostalServiceElements'), CTD_ANON_29, scope=AddressDetails_, documentation=u'Postal authorities use specific postal service data to expedient delivery of mail'))

AddressDetails_._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Country'), CTD_ANON_66, scope=AddressDetails_, documentation=u'Specification of a country'))

AddressDetails_._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Thoroughfare'), CTD_ANON_15, scope=AddressDetails_, documentation=u'Specification of a thoroughfare. A thoroughfare could be a rd, street, canal, river, etc.  Note dependentlocality in a street. For example, in some countries, a large street will \nhave many subdivisions with numbers. Normally the subdivision name is the same as the road name, but with a number to identifiy it. Eg. SOI SUKUMVIT 3, SUKUMVIT RD, BANGKOK'))
AddressDetails_._GroupModel_ = pyxb.binding.content.GroupChoice(
    pyxb.binding.content.ParticleModel(AddressDetails_._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Address')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(AddressDetails_._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'AddressLines')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(AddressDetails_._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Country')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(AddressDetails_._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'AdministrativeArea')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(AddressDetails_._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Locality')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(AddressDetails_._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Thoroughfare')), min_occurs=1, max_occurs=1)
    )
AddressDetails_._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(AddressDetails_._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'PostalServiceElements')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(AddressDetails_._GroupModel_, min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_strict, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'urn:oasis:names:tc:ciq:xsdschema:xAL:2.0')), min_occurs=0L, max_occurs=None)
    )
AddressDetails_._ContentModel = pyxb.binding.content.ParticleModel(AddressDetails_._GroupModel, min_occurs=1, max_occurs=1)


BuildingNameType._GroupModel = pyxb.binding.content.GroupSequence(
    
    )
BuildingNameType._ContentModel = pyxb.binding.content.ParticleModel(BuildingNameType._GroupModel, min_occurs=1, max_occurs=1)


CTD_ANON_37._GroupModel = pyxb.binding.content.GroupSequence(
    
    )
CTD_ANON_37._ContentModel = pyxb.binding.content.ParticleModel(CTD_ANON_37._GroupModel, min_occurs=1, max_occurs=1)


CTD_ANON_39._GroupModel = pyxb.binding.content.GroupSequence(
    
    )
CTD_ANON_39._ContentModel = pyxb.binding.content.ParticleModel(CTD_ANON_39._GroupModel, min_occurs=0L, max_occurs=1)


ThoroughfareTrailingTypeType._GroupModel = pyxb.binding.content.GroupSequence(
    
    )
ThoroughfareTrailingTypeType._ContentModel = pyxb.binding.content.ParticleModel(ThoroughfareTrailingTypeType._GroupModel, min_occurs=1, max_occurs=1)


CTD_ANON_40._GroupModel = pyxb.binding.content.GroupSequence(
    
    )
CTD_ANON_40._ContentModel = pyxb.binding.content.ParticleModel(CTD_ANON_40._GroupModel, min_occurs=0L, max_occurs=None)


CTD_ANON_41._GroupModel = pyxb.binding.content.GroupSequence(
    
    )
CTD_ANON_41._ContentModel = pyxb.binding.content.ParticleModel(CTD_ANON_41._GroupModel, min_occurs=0L, max_occurs=1)


CTD_ANON_42._GroupModel = pyxb.binding.content.GroupSequence(
    
    )
CTD_ANON_42._ContentModel = pyxb.binding.content.ParticleModel(CTD_ANON_42._GroupModel, min_occurs=1, max_occurs=1)


CTD_ANON_43._GroupModel = pyxb.binding.content.GroupSequence(
    
    )
CTD_ANON_43._ContentModel = pyxb.binding.content.ParticleModel(CTD_ANON_43._GroupModel, min_occurs=0L, max_occurs=1)


ThoroughfarePostDirectionType._GroupModel = pyxb.binding.content.GroupSequence(
    
    )
ThoroughfarePostDirectionType._ContentModel = pyxb.binding.content.ParticleModel(ThoroughfarePostDirectionType._GroupModel, min_occurs=1, max_occurs=1)



AddressLinesType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'AddressLine'), CTD_ANON, scope=AddressLinesType, documentation=u'Free format address representation. An address can have more than one line. The order of the AddressLine elements must be preserved.'))
AddressLinesType._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(AddressLinesType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'AddressLine')), min_occurs=1, max_occurs=None),
    pyxb.binding.content.ParticleModel(pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_strict, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'urn:oasis:names:tc:ciq:xsdschema:xAL:2.0')), min_occurs=0L, max_occurs=None)
    )
AddressLinesType._ContentModel = pyxb.binding.content.ParticleModel(AddressLinesType._GroupModel, min_occurs=1, max_occurs=1)



CTD_ANON_44._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'AddressLine'), CTD_ANON, scope=CTD_ANON_44, documentation=u'Free format address representation. An address can have more than one line. The order of the AddressLine elements must be preserved.'))

CTD_ANON_44._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'PremiseNumberPrefix'), CTD_ANON_32, scope=CTD_ANON_44, documentation=u'A in A12'))

CTD_ANON_44._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'PremiseNumber'), CTD_ANON_27, scope=CTD_ANON_44, documentation=u'Specification of the identifier of the premise (house, building, etc). Premises in a street are often uniquely identified by means of consecutive identifiers. The identifier can be a number, a letter or any combination of the two.'))

CTD_ANON_44._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'PremiseNumberSuffix'), CTD_ANON_34, scope=CTD_ANON_44, documentation=u'A in 12A'))
CTD_ANON_44._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(CTD_ANON_44._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'AddressLine')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(CTD_ANON_44._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'PremiseNumberPrefix')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(CTD_ANON_44._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'PremiseNumber')), min_occurs=1, max_occurs=None),
    pyxb.binding.content.ParticleModel(CTD_ANON_44._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'PremiseNumberSuffix')), min_occurs=0L, max_occurs=None)
    )
CTD_ANON_44._ContentModel = pyxb.binding.content.ParticleModel(CTD_ANON_44._GroupModel, min_occurs=1, max_occurs=1)



CTD_ANON_45._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'PostalRoute'), PostalRouteType, scope=CTD_ANON_45, documentation=u'A Postal van is specific for a route as in Is`rael, Rural route'))

CTD_ANON_45._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'AddressLine'), CTD_ANON, scope=CTD_ANON_45, documentation=u'Free format address representation. An address can have more than one line. The order of the AddressLine elements must be preserved.'))

CTD_ANON_45._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'PostalCode'), CTD_ANON_4, scope=CTD_ANON_45, documentation=u'PostalCode is the container element for either simple or complex (extended) postal codes. Type: Area Code, Postcode, etc.'))

CTD_ANON_45._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'DependentLocality'), DependentLocalityType, scope=CTD_ANON_45, documentation=u'Dependent localities are Districts within cities/towns, locality divisions, postal \ndivisions of cities, suburbs, etc. DependentLocality is a recursive element, but no nesting deeper than two exists (Locality-DependentLocality-DependentLocality).'))

CTD_ANON_45._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Premise'), CTD_ANON_3, scope=CTD_ANON_45, documentation=u'Specification of a single premise, for example a house or a building. The premise as a whole has a unique premise (house) number or a premise name.  There could be more than \none premise in a street referenced in an address. For example a building address near a major shopping centre or raiwlay station'))

CTD_ANON_45._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Thoroughfare'), CTD_ANON_15, scope=CTD_ANON_45, documentation=u'Specification of a thoroughfare. A thoroughfare could be a rd, street, canal, river, etc.  Note dependentlocality in a street. For example, in some countries, a large street will \nhave many subdivisions with numbers. Normally the subdivision name is the same as the road name, but with a number to identifiy it. Eg. SOI SUKUMVIT 3, SUKUMVIT RD, BANGKOK'))

CTD_ANON_45._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'LargeMailUser'), LargeMailUserType, scope=CTD_ANON_45, documentation=u'Specification of a large mail user address. Examples of large mail users are postal companies, companies in France with a cedex number, hospitals and airports with their own post code. Large mail user addresses do not have a street name with premise name or premise number in countries like Netherlands. But they have a POBox and street also in countries like France'))

CTD_ANON_45._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'PostOffice'), CTD_ANON_8, scope=CTD_ANON_45, documentation=u'Specification of a post office. Examples are a rural post office where post is delivered and a post office containing post office boxes.'))

CTD_ANON_45._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'PostBox'), CTD_ANON_11, scope=CTD_ANON_45, documentation=u'Specification of a postbox like mail delivery point. Only a single postbox number can be specified. Examples of postboxes are POBox, free mail numbers, etc.'))

CTD_ANON_45._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'LocalityName'), CTD_ANON_61, scope=CTD_ANON_45, documentation=u'Name of the locality'))
CTD_ANON_45._GroupModel_ = pyxb.binding.content.GroupChoice(
    pyxb.binding.content.ParticleModel(CTD_ANON_45._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'PostBox')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(CTD_ANON_45._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'LargeMailUser')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(CTD_ANON_45._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'PostOffice')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(CTD_ANON_45._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'PostalRoute')), min_occurs=1, max_occurs=1)
    )
CTD_ANON_45._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(CTD_ANON_45._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'AddressLine')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(CTD_ANON_45._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'LocalityName')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(CTD_ANON_45._GroupModel_, min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(CTD_ANON_45._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Thoroughfare')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(CTD_ANON_45._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Premise')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(CTD_ANON_45._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'DependentLocality')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(CTD_ANON_45._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'PostalCode')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_strict, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'urn:oasis:names:tc:ciq:xsdschema:xAL:2.0')), min_occurs=0L, max_occurs=None)
    )
CTD_ANON_45._ContentModel = pyxb.binding.content.ParticleModel(CTD_ANON_45._GroupModel, min_occurs=1, max_occurs=1)



SubPremiseType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'SubPremise'), SubPremiseType, scope=SubPremiseType, documentation=u'Specification of a single sub-premise. Examples of sub-premises are apartments and suites. \nEach sub-premise should be uniquely identifiable. SubPremiseType: Specification of the name of a sub-premise type. Possible values not limited to: Suite, Appartment, Floor, Unknown\nMultiple levels within a premise by recursively calling SubPremise Eg. Level 4, Suite 2, Block C'))

SubPremiseType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Firm'), FirmType, scope=SubPremiseType, documentation=u'Specification of a firm, company, organization, etc. It can be specified as part of an address that contains a street or a postbox. It is therefore different from a large mail user address, which contains no street.'))

SubPremiseType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'MailStop'), MailStopType, scope=SubPremiseType, documentation=u'A MailStop is where the the mail is delivered to within a premise/subpremise/firm or a facility.'))

SubPremiseType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'SubPremiseNumberSuffix'), CTD_ANON_31, scope=SubPremiseType, documentation=u' Suffix of the sub premise number. eg. A in 12A'))

SubPremiseType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'SubPremiseLocation'), CTD_ANON_42, scope=SubPremiseType, documentation=u' Name of the SubPremise Location. eg. LOBBY, BASEMENT, GROUND FLOOR, etc...'))

SubPremiseType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'AddressLine'), CTD_ANON, scope=SubPremiseType, documentation=u'Free format address representation. An address can have more than one line. The order of the AddressLine elements must be preserved.'))

SubPremiseType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'SubPremiseName'), CTD_ANON_58, scope=SubPremiseType, documentation=u' Name of the SubPremise'))

SubPremiseType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'BuildingName'), BuildingNameType, scope=SubPremiseType, documentation=u'Name of the building'))

SubPremiseType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'SubPremiseNumberPrefix'), CTD_ANON_26, scope=SubPremiseType, documentation=u' Prefix of the sub premise number. eg. A in A-12'))

SubPremiseType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'SubPremiseNumber'), CTD_ANON_18, scope=SubPremiseType, documentation=u' Specification of the identifier of a sub-premise. Examples of sub-premises are apartments and suites. sub-premises in a building are often uniquely identified by means of consecutive\nidentifiers. The identifier can be a number, a letter or any combination of the two. In the latter case, the identifier includes exactly one variable (range) part, which is either a \nnumber or a single letter that is surrounded by fixed parts at the left (prefix) or the right (postfix).'))

SubPremiseType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'PostalCode'), CTD_ANON_4, scope=SubPremiseType, documentation=u'PostalCode is the container element for either simple or complex (extended) postal codes. Type: Area Code, Postcode, etc.'))
SubPremiseType._GroupModel_ = pyxb.binding.content.GroupChoice(
    pyxb.binding.content.ParticleModel(SubPremiseType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'SubPremiseLocation')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(SubPremiseType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'SubPremiseNumber')), min_occurs=0L, max_occurs=None)
    )
SubPremiseType._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(SubPremiseType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'AddressLine')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(SubPremiseType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'SubPremiseName')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(SubPremiseType._GroupModel_, min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(SubPremiseType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'SubPremiseNumberPrefix')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(SubPremiseType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'SubPremiseNumberSuffix')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(SubPremiseType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'BuildingName')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(SubPremiseType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Firm')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(SubPremiseType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'MailStop')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(SubPremiseType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'PostalCode')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(SubPremiseType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'SubPremise')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_strict, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'urn:oasis:names:tc:ciq:xsdschema:xAL:2.0')), min_occurs=0L, max_occurs=None)
    )
SubPremiseType._ContentModel = pyxb.binding.content.ParticleModel(SubPremiseType._GroupModel, min_occurs=1, max_occurs=1)



CTD_ANON_46._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'AddressLine'), CTD_ANON, scope=CTD_ANON_46, documentation=u'Free format address representation. An address can have more than one line. The order of the AddressLine elements must be preserved.'))

CTD_ANON_46._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'ThoroughfareNumber'), CTD_ANON_20, scope=CTD_ANON_46, documentation=u'Eg.: 23 Archer street or 25/15 Zero Avenue, etc'))

CTD_ANON_46._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'ThoroughfareNumberPrefix'), CTD_ANON_7, scope=CTD_ANON_46, documentation=u'Prefix before the number. A in A12 Archer Street'))

CTD_ANON_46._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'ThoroughfareNumberSuffix'), CTD_ANON_37, scope=CTD_ANON_46, documentation=u'Suffix after the number. A in 12A Archer Street'))
CTD_ANON_46._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(CTD_ANON_46._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'AddressLine')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(CTD_ANON_46._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'ThoroughfareNumberPrefix')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(CTD_ANON_46._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'ThoroughfareNumber')), min_occurs=1, max_occurs=None),
    pyxb.binding.content.ParticleModel(CTD_ANON_46._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'ThoroughfareNumberSuffix')), min_occurs=0L, max_occurs=None)
    )
CTD_ANON_46._ContentModel = pyxb.binding.content.ParticleModel(CTD_ANON_46._GroupModel, min_occurs=1, max_occurs=1)


CTD_ANON_47._GroupModel = pyxb.binding.content.GroupSequence(
    
    )
CTD_ANON_47._ContentModel = pyxb.binding.content.ParticleModel(CTD_ANON_47._GroupModel, min_occurs=0L, max_occurs=1)



CTD_ANON_48._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'PremiseNumberPrefix'), CTD_ANON_32, scope=CTD_ANON_48, documentation=u'A in A12'))

CTD_ANON_48._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'PremiseNumberSuffix'), CTD_ANON_34, scope=CTD_ANON_48, documentation=u'A in 12A'))

CTD_ANON_48._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'AddressLine'), CTD_ANON, scope=CTD_ANON_48, documentation=u'Free format address representation. An address can have more than one line. The order of the AddressLine elements must be preserved.'))

CTD_ANON_48._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'PremiseNumber'), CTD_ANON_27, scope=CTD_ANON_48, documentation=u'Specification of the identifier of the premise (house, building, etc). Premises in a street are often uniquely identified by means of consecutive identifiers. The identifier can be a number, a letter or any combination of the two.'))
CTD_ANON_48._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(CTD_ANON_48._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'AddressLine')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(CTD_ANON_48._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'PremiseNumberPrefix')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(CTD_ANON_48._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'PremiseNumber')), min_occurs=1, max_occurs=None),
    pyxb.binding.content.ParticleModel(CTD_ANON_48._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'PremiseNumberSuffix')), min_occurs=0L, max_occurs=None)
    )
CTD_ANON_48._ContentModel = pyxb.binding.content.ParticleModel(CTD_ANON_48._GroupModel, min_occurs=1, max_occurs=1)


CTD_ANON_49._GroupModel = pyxb.binding.content.GroupSequence(
    
    )
CTD_ANON_49._ContentModel = pyxb.binding.content.ParticleModel(CTD_ANON_49._GroupModel, min_occurs=0L, max_occurs=None)



CTD_ANON_50._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'ThoroughfareNumberPrefix'), CTD_ANON_7, scope=CTD_ANON_50, documentation=u'Prefix before the number. A in A12 Archer Street'))

CTD_ANON_50._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'AddressLine'), CTD_ANON, scope=CTD_ANON_50, documentation=u'Free format address representation. An address can have more than one line. The order of the AddressLine elements must be preserved.'))

CTD_ANON_50._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'ThoroughfareNumber'), CTD_ANON_20, scope=CTD_ANON_50, documentation=u'Eg.: 23 Archer street or 25/15 Zero Avenue, etc'))

CTD_ANON_50._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'ThoroughfareNumberSuffix'), CTD_ANON_37, scope=CTD_ANON_50, documentation=u'Suffix after the number. A in 12A Archer Street'))
CTD_ANON_50._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(CTD_ANON_50._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'AddressLine')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(CTD_ANON_50._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'ThoroughfareNumberPrefix')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(CTD_ANON_50._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'ThoroughfareNumber')), min_occurs=1, max_occurs=None),
    pyxb.binding.content.ParticleModel(CTD_ANON_50._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'ThoroughfareNumberSuffix')), min_occurs=0L, max_occurs=None)
    )
CTD_ANON_50._ContentModel = pyxb.binding.content.ParticleModel(CTD_ANON_50._GroupModel, min_occurs=1, max_occurs=1)


CTD_ANON_51._GroupModel = pyxb.binding.content.GroupSequence(
    
    )
CTD_ANON_51._ContentModel = pyxb.binding.content.ParticleModel(CTD_ANON_51._GroupModel, min_occurs=1, max_occurs=1)


CTD_ANON_52._GroupModel = pyxb.binding.content.GroupSequence(
    
    )
CTD_ANON_52._ContentModel = pyxb.binding.content.ParticleModel(CTD_ANON_52._GroupModel, min_occurs=0L, max_occurs=None)


CTD_ANON_53._GroupModel = pyxb.binding.content.GroupSequence(
    
    )
CTD_ANON_53._ContentModel = pyxb.binding.content.ParticleModel(CTD_ANON_53._GroupModel, min_occurs=0L, max_occurs=None)


ThoroughfarePreDirectionType._GroupModel = pyxb.binding.content.GroupSequence(
    
    )
ThoroughfarePreDirectionType._ContentModel = pyxb.binding.content.ParticleModel(ThoroughfarePreDirectionType._GroupModel, min_occurs=1, max_occurs=1)


CTD_ANON_54._GroupModel = pyxb.binding.content.GroupSequence(
    
    )
CTD_ANON_54._ContentModel = pyxb.binding.content.ParticleModel(CTD_ANON_54._GroupModel, min_occurs=1, max_occurs=None)


CTD_ANON_55._GroupModel = pyxb.binding.content.GroupSequence(
    
    )
CTD_ANON_55._ContentModel = pyxb.binding.content.ParticleModel(CTD_ANON_55._GroupModel, min_occurs=0L, max_occurs=1)


ThoroughfareLeadingTypeType._GroupModel = pyxb.binding.content.GroupSequence(
    
    )
ThoroughfareLeadingTypeType._ContentModel = pyxb.binding.content.ParticleModel(ThoroughfareLeadingTypeType._GroupModel, min_occurs=1, max_occurs=1)


CTD_ANON_56._GroupModel = pyxb.binding.content.GroupSequence(
    
    )
CTD_ANON_56._ContentModel = pyxb.binding.content.ParticleModel(CTD_ANON_56._GroupModel, min_occurs=0L, max_occurs=1)


CTD_ANON_57._GroupModel = pyxb.binding.content.GroupSequence(
    
    )
CTD_ANON_57._ContentModel = pyxb.binding.content.ParticleModel(CTD_ANON_57._GroupModel, min_occurs=0L, max_occurs=None)


CTD_ANON_58._GroupModel = pyxb.binding.content.GroupSequence(
    
    )
CTD_ANON_58._ContentModel = pyxb.binding.content.ParticleModel(CTD_ANON_58._GroupModel, min_occurs=0L, max_occurs=None)


CTD_ANON_59._GroupModel = pyxb.binding.content.GroupSequence(
    
    )
CTD_ANON_59._ContentModel = pyxb.binding.content.ParticleModel(CTD_ANON_59._GroupModel, min_occurs=0L, max_occurs=1)



CTD_ANON_60._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'PostOffice'), CTD_ANON_8, scope=CTD_ANON_60, documentation=u'Specification of a post office. Examples are a rural post office where post is delivered and a post office containing post office boxes.'))

CTD_ANON_60._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'AddressLine'), CTD_ANON, scope=CTD_ANON_60, documentation=u'Free format address representation. An address can have more than one line. The order of the AddressLine elements must be preserved.'))

CTD_ANON_60._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'SubAdministrativeAreaName'), CTD_ANON_68, scope=CTD_ANON_60, documentation=u' Name of the sub-administrative area'))

CTD_ANON_60._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'PostalCode'), CTD_ANON_4, scope=CTD_ANON_60, documentation=u'PostalCode is the container element for either simple or complex (extended) postal codes. Type: Area Code, Postcode, etc.'))

CTD_ANON_60._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Locality'), CTD_ANON_45, scope=CTD_ANON_60, documentation=u'Locality is one level lower than adminisstrative area. Eg.: cities, reservations and any other built-up areas.'))
CTD_ANON_60._GroupModel_ = pyxb.binding.content.GroupChoice(
    pyxb.binding.content.ParticleModel(CTD_ANON_60._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Locality')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(CTD_ANON_60._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'PostOffice')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(CTD_ANON_60._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'PostalCode')), min_occurs=1, max_occurs=1)
    )
CTD_ANON_60._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(CTD_ANON_60._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'AddressLine')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(CTD_ANON_60._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'SubAdministrativeAreaName')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(CTD_ANON_60._GroupModel_, min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_strict, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'urn:oasis:names:tc:ciq:xsdschema:xAL:2.0')), min_occurs=0L, max_occurs=None)
    )
CTD_ANON_60._ContentModel = pyxb.binding.content.ParticleModel(CTD_ANON_60._GroupModel, min_occurs=1, max_occurs=1)


CTD_ANON_61._GroupModel = pyxb.binding.content.GroupSequence(
    
    )
CTD_ANON_61._ContentModel = pyxb.binding.content.ParticleModel(CTD_ANON_61._GroupModel, min_occurs=0L, max_occurs=None)



CTD_ANON_62._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'ThoroughfareNumberTo'), CTD_ANON_50, scope=CTD_ANON_62, documentation=u'Ending number in the range'))

CTD_ANON_62._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'AddressLine'), CTD_ANON, scope=CTD_ANON_62, documentation=u'Free format address representation. An address can have more than one line. The order of the AddressLine elements must be preserved.'))

CTD_ANON_62._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'ThoroughfareNumberFrom'), CTD_ANON_46, scope=CTD_ANON_62, documentation=u'Starting number in the range'))
CTD_ANON_62._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(CTD_ANON_62._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'AddressLine')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(CTD_ANON_62._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'ThoroughfareNumberFrom')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(CTD_ANON_62._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'ThoroughfareNumberTo')), min_occurs=1, max_occurs=1)
    )
CTD_ANON_62._ContentModel = pyxb.binding.content.ParticleModel(CTD_ANON_62._GroupModel, min_occurs=1, max_occurs=1)


CTD_ANON_63._GroupModel = pyxb.binding.content.GroupSequence(
    
    )
CTD_ANON_63._ContentModel = pyxb.binding.content.ParticleModel(CTD_ANON_63._GroupModel, min_occurs=1, max_occurs=1)


CTD_ANON_64._GroupModel = pyxb.binding.content.GroupSequence(
    
    )
CTD_ANON_64._ContentModel = pyxb.binding.content.ParticleModel(CTD_ANON_64._GroupModel, min_occurs=0L, max_occurs=1)



CTD_ANON_65._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'ThoroughfareName'), ThoroughfareNameType, scope=CTD_ANON_65, documentation=u'Specification of the name of a Thoroughfare (also dependant street name): street name, canal name, etc.'))

CTD_ANON_65._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'ThoroughfarePreDirection'), ThoroughfarePreDirectionType, scope=CTD_ANON_65, documentation=u'North Baker Street, where North is the pre-direction. The direction appears before the name.'))

CTD_ANON_65._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'ThoroughfarePostDirection'), ThoroughfarePostDirectionType, scope=CTD_ANON_65, documentation=u'221-bis Baker Street North, where North is the post-direction. The post-direction appears after the name.'))

CTD_ANON_65._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'ThoroughfareTrailingType'), ThoroughfareTrailingTypeType, scope=CTD_ANON_65, documentation=u'Appears after the thoroughfare name. Ed. British: Baker Lane, where Lane is the trailing type.'))

CTD_ANON_65._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'ThoroughfareLeadingType'), ThoroughfareLeadingTypeType, scope=CTD_ANON_65, documentation=u'Appears before the thoroughfare name. Ed. Spanish: Avenida Aurora, where Avenida is the leading type / French: Rue Moliere, where Rue is the leading type.'))

CTD_ANON_65._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'AddressLine'), CTD_ANON, scope=CTD_ANON_65, documentation=u'Free format address representation. An address can have more than one line. The order of the AddressLine elements must be preserved.'))
CTD_ANON_65._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(CTD_ANON_65._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'AddressLine')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(CTD_ANON_65._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'ThoroughfarePreDirection')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(CTD_ANON_65._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'ThoroughfareLeadingType')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(CTD_ANON_65._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'ThoroughfareName')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(CTD_ANON_65._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'ThoroughfareTrailingType')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(CTD_ANON_65._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'ThoroughfarePostDirection')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_strict, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'urn:oasis:names:tc:ciq:xsdschema:xAL:2.0')), min_occurs=0L, max_occurs=None)
    )
CTD_ANON_65._ContentModel = pyxb.binding.content.ParticleModel(CTD_ANON_65._GroupModel, min_occurs=1, max_occurs=1)



CTD_ANON_66._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'AddressLine'), CTD_ANON, scope=CTD_ANON_66, documentation=u'Free format address representation. An address can have more than one line. The order of the AddressLine elements must be preserved.'))

CTD_ANON_66._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'AdministrativeArea'), CTD_ANON_9, scope=CTD_ANON_66, documentation=u'Examples of administrative areas are provinces counties, special regions (such as "Rijnmond"), etc.'))

CTD_ANON_66._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'CountryName'), CTD_ANON_, scope=CTD_ANON_66, documentation=u'Specification of the name of a country.'))

CTD_ANON_66._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'CountryNameCode'), CTD_ANON_57, scope=CTD_ANON_66, documentation=u'A country code according to the specified scheme'))

CTD_ANON_66._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Locality'), CTD_ANON_45, scope=CTD_ANON_66, documentation=u'Locality is one level lower than adminisstrative area. Eg.: cities, reservations and any other built-up areas.'))

CTD_ANON_66._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Thoroughfare'), CTD_ANON_15, scope=CTD_ANON_66, documentation=u'Specification of a thoroughfare. A thoroughfare could be a rd, street, canal, river, etc.  Note dependentlocality in a street. For example, in some countries, a large street will \nhave many subdivisions with numbers. Normally the subdivision name is the same as the road name, but with a number to identifiy it. Eg. SOI SUKUMVIT 3, SUKUMVIT RD, BANGKOK'))
CTD_ANON_66._GroupModel_ = pyxb.binding.content.GroupChoice(
    pyxb.binding.content.ParticleModel(CTD_ANON_66._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'AdministrativeArea')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(CTD_ANON_66._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Locality')), min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(CTD_ANON_66._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Thoroughfare')), min_occurs=1, max_occurs=1)
    )
CTD_ANON_66._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(CTD_ANON_66._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'AddressLine')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(CTD_ANON_66._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'CountryNameCode')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(CTD_ANON_66._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'CountryName')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(CTD_ANON_66._GroupModel_, min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_strict, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'urn:oasis:names:tc:ciq:xsdschema:xAL:2.0')), min_occurs=0L, max_occurs=None)
    )
CTD_ANON_66._ContentModel = pyxb.binding.content.ParticleModel(CTD_ANON_66._GroupModel, min_occurs=1, max_occurs=1)


CTD_ANON_67._GroupModel = pyxb.binding.content.GroupSequence(
    
    )
CTD_ANON_67._ContentModel = pyxb.binding.content.ParticleModel(CTD_ANON_67._GroupModel, min_occurs=0L, max_occurs=None)


CTD_ANON_68._GroupModel = pyxb.binding.content.GroupSequence(
    
    )
CTD_ANON_68._ContentModel = pyxb.binding.content.ParticleModel(CTD_ANON_68._GroupModel, min_occurs=0L, max_occurs=None)


CTD_ANON_69._GroupModel = pyxb.binding.content.GroupSequence(
    
    )
CTD_ANON_69._ContentModel = pyxb.binding.content.ParticleModel(CTD_ANON_69._GroupModel, min_occurs=0L, max_occurs=1)
