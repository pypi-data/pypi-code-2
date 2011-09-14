# ./pyxb/bundles/opengis/raw/_nsgroup_2.py
# PyXB bindings for NGM:74d7865bc281d02523b2e79f08defec82904da9c
# Generated 2011-09-09 14:19:15.801685 by PyXB version 1.1.3
# Group contents:
# Namespace http://www.opengis.net/cat/csw/2.0.2
# Namespace http://purl.org/dc/terms/ [xmlns:dct]


import pyxb
import pyxb.binding
import pyxb.utils.utility

# Unique identifier for bindings created at the same time
_GenerationUID = pyxb.utils.utility.UniqueIdentifier('urn:uuid:9b8fedac-db18-11e0-abb2-001fbc013adc')

# Import bindings for schemas in group
import pyxb.binding.datatypes
import pyxb.bundles.opengis._dc
import pyxb.bundles.opengis.ows

_Namespace = pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/cat/csw/2.0.2', create_if_missing=True)
_Namespace.configureCategories(['typeBinding', 'elementBinding'])
_Namespace_ows = pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/ows', create_if_missing=True)
_Namespace_ows.configureCategories(['typeBinding', 'elementBinding'])
_Namespace_dct = pyxb.namespace.NamespaceForURI(u'http://purl.org/dc/terms/', create_if_missing=True)
_Namespace_dct.configureCategories(['typeBinding', 'elementBinding'])

# Complex type AbstractRecordType with content type EMPTY
class AbstractRecordType (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_EMPTY
    _Abstract = True
    _ExpandedName = pyxb.namespace.ExpandedName(_Namespace, u'AbstractRecordType')
    # Base type is pyxb.binding.datatypes.anyType

    _ElementMap = {
        
    }
    _AttributeMap = {
        
    }
_Namespace.addCategoryObject('typeBinding', u'AbstractRecordType', AbstractRecordType)


# Complex type DCMIRecordType with content type ELEMENT_ONLY
class DCMIRecordType (AbstractRecordType):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(_Namespace, u'DCMIRecordType')
    # Base type is AbstractRecordType
    
    # Element {http://purl.org/dc/elements/1.1/}DC-element uses Python identifier DC_element
    __DC_element = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(pyxb.bundles.opengis._dc.Namespace, u'DC-element'), 'DC_element', '__httpwww_opengis_netcatcsw2_0_2_DCMIRecordType_httppurl_orgdcelements1_1DC_element', True)

    
    DC_element = property(__DC_element.value, __DC_element.set, None, None)


    _ElementMap = AbstractRecordType._ElementMap.copy()
    _ElementMap.update({
        __DC_element.name() : __DC_element
    })
    _AttributeMap = AbstractRecordType._AttributeMap.copy()
    _AttributeMap.update({
        
    })
_Namespace.addCategoryObject('typeBinding', u'DCMIRecordType', DCMIRecordType)


# Complex type RecordType with content type ELEMENT_ONLY
class RecordType (DCMIRecordType):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(_Namespace, u'RecordType')
    # Base type is DCMIRecordType
    
    # Element {http://www.opengis.net/ows}BoundingBox uses Python identifier BoundingBox
    __BoundingBox = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(_Namespace_ows, u'BoundingBox'), 'BoundingBox', '__httpwww_opengis_netcatcsw2_0_2_RecordType_httpwww_opengis_netowsBoundingBox', True)

    
    BoundingBox = property(__BoundingBox.value, __BoundingBox.set, None, None)

    
    # Element {http://www.opengis.net/cat/csw/2.0.2}AnyText uses Python identifier AnyText
    __AnyText = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(_Namespace, u'AnyText'), 'AnyText', '__httpwww_opengis_netcatcsw2_0_2_RecordType_httpwww_opengis_netcatcsw2_0_2AnyText', True)

    
    AnyText = property(__AnyText.value, __AnyText.set, None, None)

    
    # Element DC_element ({http://purl.org/dc/elements/1.1/}DC-element) inherited from {http://www.opengis.net/cat/csw/2.0.2}DCMIRecordType

    _ElementMap = DCMIRecordType._ElementMap.copy()
    _ElementMap.update({
        __BoundingBox.name() : __BoundingBox,
        __AnyText.name() : __AnyText
    })
    _AttributeMap = DCMIRecordType._AttributeMap.copy()
    _AttributeMap.update({
        
    })
_Namespace.addCategoryObject('typeBinding', u'RecordType', RecordType)


# Complex type SummaryRecordType with content type ELEMENT_ONLY
class SummaryRecordType (AbstractRecordType):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(_Namespace, u'SummaryRecordType')
    # Base type is AbstractRecordType
    
    # Element {http://purl.org/dc/terms/}modified uses Python identifier modified
    __modified = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(_Namespace_dct, u'modified'), 'modified', '__httpwww_opengis_netcatcsw2_0_2_SummaryRecordType_httppurl_orgdctermsmodified', True)

    
    modified = property(__modified.value, __modified.set, None, None)

    
    # Element {http://www.opengis.net/ows}BoundingBox uses Python identifier BoundingBox
    __BoundingBox = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(_Namespace_ows, u'BoundingBox'), 'BoundingBox', '__httpwww_opengis_netcatcsw2_0_2_SummaryRecordType_httpwww_opengis_netowsBoundingBox', True)

    
    BoundingBox = property(__BoundingBox.value, __BoundingBox.set, None, None)

    
    # Element {http://purl.org/dc/terms/}abstract uses Python identifier abstract
    __abstract = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(_Namespace_dct, u'abstract'), 'abstract', '__httpwww_opengis_netcatcsw2_0_2_SummaryRecordType_httppurl_orgdctermsabstract', True)

    
    abstract = property(__abstract.value, __abstract.set, None, None)

    
    # Element {http://purl.org/dc/elements/1.1/}subject uses Python identifier subject
    __subject = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(pyxb.bundles.opengis._dc.Namespace, u'subject'), 'subject', '__httpwww_opengis_netcatcsw2_0_2_SummaryRecordType_httppurl_orgdcelements1_1subject', True)

    
    subject = property(__subject.value, __subject.set, None, u'A topic of the content of the resource. Typically, Subject will be \n      expressed as keywords, key phrases, or classification codes that \n      describe a topic of the resource. Recommended best practice is to \n      select a value from a controlled vocabulary or formal classification \n      scheme.')

    
    # Element {http://purl.org/dc/elements/1.1/}title uses Python identifier title
    __title = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(pyxb.bundles.opengis._dc.Namespace, u'title'), 'title', '__httpwww_opengis_netcatcsw2_0_2_SummaryRecordType_httppurl_orgdcelements1_1title', True)

    
    title = property(__title.value, __title.set, None, u'A name given to the resource. Typically, Title will be a name by \n      which the resource is formally known.')

    
    # Element {http://purl.org/dc/elements/1.1/}relation uses Python identifier relation
    __relation = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(pyxb.bundles.opengis._dc.Namespace, u'relation'), 'relation', '__httpwww_opengis_netcatcsw2_0_2_SummaryRecordType_httppurl_orgdcelements1_1relation', True)

    
    relation = property(__relation.value, __relation.set, None, u'A reference to a related resource. Recommended best practice is to \n      identify the referenced resource by means of a string or number \n      conforming to a formal identification system.')

    
    # Element {http://purl.org/dc/terms/}spatial uses Python identifier spatial
    __spatial = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(_Namespace_dct, u'spatial'), 'spatial', '__httpwww_opengis_netcatcsw2_0_2_SummaryRecordType_httppurl_orgdctermsspatial', True)

    
    spatial = property(__spatial.value, __spatial.set, None, None)

    
    # Element {http://purl.org/dc/elements/1.1/}identifier uses Python identifier identifier
    __identifier = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(pyxb.bundles.opengis._dc.Namespace, u'identifier'), 'identifier', '__httpwww_opengis_netcatcsw2_0_2_SummaryRecordType_httppurl_orgdcelements1_1identifier', True)

    
    identifier = property(__identifier.value, __identifier.set, None, u'An unambiguous reference to the resource within a given context. \n      Recommended best practice is to identify the resource by means of a \n      string or number conforming to a formal identification system. Formal \n      identification systems include but are not limited to the Uniform \n      Resource Identifier (URI) (including the Uniform Resource Locator \n      (URL)), the Digital Object Identifier (DOI), and the International \n      Standard Book Number (ISBN).')

    
    # Element {http://purl.org/dc/elements/1.1/}type uses Python identifier type
    __type = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(pyxb.bundles.opengis._dc.Namespace, u'type'), 'type', '__httpwww_opengis_netcatcsw2_0_2_SummaryRecordType_httppurl_orgdcelements1_1type', False)

    
    type = property(__type.value, __type.set, None, u'The nature or genre of the content of the resource. Type includes \n      terms describing general categories, functions, genres, or aggregation \n      levels for content. Recommended best practice is to select a value \n      from a controlled vocabulary (for example, the DCMI Type Vocabulary). \n      To describe the physical or digital manifestation of the resource, \n      use the Format element.')

    
    # Element {http://purl.org/dc/elements/1.1/}format uses Python identifier format
    __format = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(pyxb.bundles.opengis._dc.Namespace, u'format'), 'format', '__httpwww_opengis_netcatcsw2_0_2_SummaryRecordType_httppurl_orgdcelements1_1format', True)

    
    format = property(__format.value, __format.set, None, u'The physical or digital manifestation of the resource. Typically, \n      Format will include the media-type or dimensions of the resource. \n      Format may be used to identify the software, hardware, or other \n      equipment needed to display or operate the resource. Examples of \n      dimensions include size and duration. Recommended best practice is to \n      select a value from a controlled vocabulary (for example, the list \n      of Internet Media Types defining computer media formats).')


    _ElementMap = AbstractRecordType._ElementMap.copy()
    _ElementMap.update({
        __modified.name() : __modified,
        __BoundingBox.name() : __BoundingBox,
        __abstract.name() : __abstract,
        __subject.name() : __subject,
        __title.name() : __title,
        __relation.name() : __relation,
        __spatial.name() : __spatial,
        __identifier.name() : __identifier,
        __type.name() : __type,
        __format.name() : __format
    })
    _AttributeMap = AbstractRecordType._AttributeMap.copy()
    _AttributeMap.update({
        
    })
_Namespace.addCategoryObject('typeBinding', u'SummaryRecordType', SummaryRecordType)


# Complex type EmptyType with content type EMPTY
class EmptyType (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_EMPTY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(_Namespace, u'EmptyType')
    # Base type is pyxb.binding.datatypes.anyType

    _ElementMap = {
        
    }
    _AttributeMap = {
        
    }
_Namespace.addCategoryObject('typeBinding', u'EmptyType', EmptyType)


# Complex type BriefRecordType with content type ELEMENT_ONLY
class BriefRecordType (AbstractRecordType):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(_Namespace, u'BriefRecordType')
    # Base type is AbstractRecordType
    
    # Element {http://purl.org/dc/elements/1.1/}identifier uses Python identifier identifier
    __identifier = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(pyxb.bundles.opengis._dc.Namespace, u'identifier'), 'identifier', '__httpwww_opengis_netcatcsw2_0_2_BriefRecordType_httppurl_orgdcelements1_1identifier', True)

    
    identifier = property(__identifier.value, __identifier.set, None, u'An unambiguous reference to the resource within a given context. \n      Recommended best practice is to identify the resource by means of a \n      string or number conforming to a formal identification system. Formal \n      identification systems include but are not limited to the Uniform \n      Resource Identifier (URI) (including the Uniform Resource Locator \n      (URL)), the Digital Object Identifier (DOI), and the International \n      Standard Book Number (ISBN).')

    
    # Element {http://www.opengis.net/ows}BoundingBox uses Python identifier BoundingBox
    __BoundingBox = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(_Namespace_ows, u'BoundingBox'), 'BoundingBox', '__httpwww_opengis_netcatcsw2_0_2_BriefRecordType_httpwww_opengis_netowsBoundingBox', True)

    
    BoundingBox = property(__BoundingBox.value, __BoundingBox.set, None, None)

    
    # Element {http://purl.org/dc/elements/1.1/}type uses Python identifier type
    __type = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(pyxb.bundles.opengis._dc.Namespace, u'type'), 'type', '__httpwww_opengis_netcatcsw2_0_2_BriefRecordType_httppurl_orgdcelements1_1type', False)

    
    type = property(__type.value, __type.set, None, u'The nature or genre of the content of the resource. Type includes \n      terms describing general categories, functions, genres, or aggregation \n      levels for content. Recommended best practice is to select a value \n      from a controlled vocabulary (for example, the DCMI Type Vocabulary). \n      To describe the physical or digital manifestation of the resource, \n      use the Format element.')

    
    # Element {http://purl.org/dc/elements/1.1/}title uses Python identifier title
    __title = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(pyxb.bundles.opengis._dc.Namespace, u'title'), 'title', '__httpwww_opengis_netcatcsw2_0_2_BriefRecordType_httppurl_orgdcelements1_1title', True)

    
    title = property(__title.value, __title.set, None, u'A name given to the resource. Typically, Title will be a name by \n      which the resource is formally known.')


    _ElementMap = AbstractRecordType._ElementMap.copy()
    _ElementMap.update({
        __identifier.name() : __identifier,
        __BoundingBox.name() : __BoundingBox,
        __type.name() : __type,
        __title.name() : __title
    })
    _AttributeMap = AbstractRecordType._AttributeMap.copy()
    _AttributeMap.update({
        
    })
_Namespace.addCategoryObject('typeBinding', u'BriefRecordType', BriefRecordType)


conformsTo = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(_Namespace_dct, u'conformsTo'), pyxb.bundles.opengis._dc.SimpleLiteral)
_Namespace_dct.addCategoryObject('elementBinding', conformsTo.name().localName(), conformsTo)

mediator = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(_Namespace_dct, u'mediator'), pyxb.bundles.opengis._dc.SimpleLiteral)
_Namespace_dct.addCategoryObject('elementBinding', mediator.name().localName(), mediator)

modified = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(_Namespace_dct, u'modified'), pyxb.bundles.opengis._dc.SimpleLiteral)
_Namespace_dct.addCategoryObject('elementBinding', modified.name().localName(), modified)

Record = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(_Namespace, u'Record'), RecordType)
_Namespace.addCategoryObject('elementBinding', Record.name().localName(), Record)

accessRights = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(_Namespace_dct, u'accessRights'), pyxb.bundles.opengis._dc.SimpleLiteral)
_Namespace_dct.addCategoryObject('elementBinding', accessRights.name().localName(), accessRights)

provenance = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(_Namespace_dct, u'provenance'), pyxb.bundles.opengis._dc.SimpleLiteral)
_Namespace_dct.addCategoryObject('elementBinding', provenance.name().localName(), provenance)

references = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(_Namespace_dct, u'references'), pyxb.bundles.opengis._dc.SimpleLiteral)
_Namespace_dct.addCategoryObject('elementBinding', references.name().localName(), references)

isVersionOf = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(_Namespace_dct, u'isVersionOf'), pyxb.bundles.opengis._dc.SimpleLiteral)
_Namespace_dct.addCategoryObject('elementBinding', isVersionOf.name().localName(), isVersionOf)

requires = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(_Namespace_dct, u'requires'), pyxb.bundles.opengis._dc.SimpleLiteral)
_Namespace_dct.addCategoryObject('elementBinding', requires.name().localName(), requires)

rightsHolder = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(_Namespace_dct, u'rightsHolder'), pyxb.bundles.opengis._dc.SimpleLiteral)
_Namespace_dct.addCategoryObject('elementBinding', rightsHolder.name().localName(), rightsHolder)

spatial = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(_Namespace_dct, u'spatial'), pyxb.bundles.opengis._dc.SimpleLiteral)
_Namespace_dct.addCategoryObject('elementBinding', spatial.name().localName(), spatial)

SummaryRecord = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(_Namespace, u'SummaryRecord'), SummaryRecordType)
_Namespace.addCategoryObject('elementBinding', SummaryRecord.name().localName(), SummaryRecord)

tableOfContents = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(_Namespace_dct, u'tableOfContents'), pyxb.bundles.opengis._dc.SimpleLiteral)
_Namespace_dct.addCategoryObject('elementBinding', tableOfContents.name().localName(), tableOfContents)

license = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(_Namespace_dct, u'license'), pyxb.bundles.opengis._dc.SimpleLiteral)
_Namespace_dct.addCategoryObject('elementBinding', license.name().localName(), license)

temporal = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(_Namespace_dct, u'temporal'), pyxb.bundles.opengis._dc.SimpleLiteral)
_Namespace_dct.addCategoryObject('elementBinding', temporal.name().localName(), temporal)

valid = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(_Namespace_dct, u'valid'), pyxb.bundles.opengis._dc.SimpleLiteral)
_Namespace_dct.addCategoryObject('elementBinding', valid.name().localName(), valid)

isPartOf = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(_Namespace_dct, u'isPartOf'), pyxb.bundles.opengis._dc.SimpleLiteral)
_Namespace_dct.addCategoryObject('elementBinding', isPartOf.name().localName(), isPartOf)

bibliographicCitation = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(_Namespace_dct, u'bibliographicCitation'), pyxb.bundles.opengis._dc.SimpleLiteral)
_Namespace_dct.addCategoryObject('elementBinding', bibliographicCitation.name().localName(), bibliographicCitation)

audience = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(_Namespace_dct, u'audience'), pyxb.bundles.opengis._dc.SimpleLiteral)
_Namespace_dct.addCategoryObject('elementBinding', audience.name().localName(), audience)

available = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(_Namespace_dct, u'available'), pyxb.bundles.opengis._dc.SimpleLiteral)
_Namespace_dct.addCategoryObject('elementBinding', available.name().localName(), available)

created = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(_Namespace_dct, u'created'), pyxb.bundles.opengis._dc.SimpleLiteral)
_Namespace_dct.addCategoryObject('elementBinding', created.name().localName(), created)

replaces = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(_Namespace_dct, u'replaces'), pyxb.bundles.opengis._dc.SimpleLiteral)
_Namespace_dct.addCategoryObject('elementBinding', replaces.name().localName(), replaces)

dateAccepted = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(_Namespace_dct, u'dateAccepted'), pyxb.bundles.opengis._dc.SimpleLiteral)
_Namespace_dct.addCategoryObject('elementBinding', dateAccepted.name().localName(), dateAccepted)

dateCopyrighted = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(_Namespace_dct, u'dateCopyrighted'), pyxb.bundles.opengis._dc.SimpleLiteral)
_Namespace_dct.addCategoryObject('elementBinding', dateCopyrighted.name().localName(), dateCopyrighted)

alternative = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(_Namespace_dct, u'alternative'), pyxb.bundles.opengis._dc.SimpleLiteral)
_Namespace_dct.addCategoryObject('elementBinding', alternative.name().localName(), alternative)

hasPart = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(_Namespace_dct, u'hasPart'), pyxb.bundles.opengis._dc.SimpleLiteral)
_Namespace_dct.addCategoryObject('elementBinding', hasPart.name().localName(), hasPart)

AbstractRecord = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(_Namespace, u'AbstractRecord'), AbstractRecordType, abstract=pyxb.binding.datatypes.boolean(1))
_Namespace.addCategoryObject('elementBinding', AbstractRecord.name().localName(), AbstractRecord)

dateSubmitted = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(_Namespace_dct, u'dateSubmitted'), pyxb.bundles.opengis._dc.SimpleLiteral)
_Namespace_dct.addCategoryObject('elementBinding', dateSubmitted.name().localName(), dateSubmitted)

hasFormat = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(_Namespace_dct, u'hasFormat'), pyxb.bundles.opengis._dc.SimpleLiteral)
_Namespace_dct.addCategoryObject('elementBinding', hasFormat.name().localName(), hasFormat)

abstract = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(_Namespace_dct, u'abstract'), pyxb.bundles.opengis._dc.SimpleLiteral)
_Namespace_dct.addCategoryObject('elementBinding', abstract.name().localName(), abstract)

DCMIRecord = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(_Namespace, u'DCMIRecord'), DCMIRecordType)
_Namespace.addCategoryObject('elementBinding', DCMIRecord.name().localName(), DCMIRecord)

extent = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(_Namespace_dct, u'extent'), pyxb.bundles.opengis._dc.SimpleLiteral)
_Namespace_dct.addCategoryObject('elementBinding', extent.name().localName(), extent)

hasVersion = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(_Namespace_dct, u'hasVersion'), pyxb.bundles.opengis._dc.SimpleLiteral)
_Namespace_dct.addCategoryObject('elementBinding', hasVersion.name().localName(), hasVersion)

medium = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(_Namespace_dct, u'medium'), pyxb.bundles.opengis._dc.SimpleLiteral)
_Namespace_dct.addCategoryObject('elementBinding', medium.name().localName(), medium)

isFormatOf = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(_Namespace_dct, u'isFormatOf'), pyxb.bundles.opengis._dc.SimpleLiteral)
_Namespace_dct.addCategoryObject('elementBinding', isFormatOf.name().localName(), isFormatOf)

isReferencedBy = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(_Namespace_dct, u'isReferencedBy'), pyxb.bundles.opengis._dc.SimpleLiteral)
_Namespace_dct.addCategoryObject('elementBinding', isReferencedBy.name().localName(), isReferencedBy)

isRequiredBy = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(_Namespace_dct, u'isRequiredBy'), pyxb.bundles.opengis._dc.SimpleLiteral)
_Namespace_dct.addCategoryObject('elementBinding', isRequiredBy.name().localName(), isRequiredBy)

isReplacedBy = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(_Namespace_dct, u'isReplacedBy'), pyxb.bundles.opengis._dc.SimpleLiteral)
_Namespace_dct.addCategoryObject('elementBinding', isReplacedBy.name().localName(), isReplacedBy)

BriefRecord = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(_Namespace, u'BriefRecord'), BriefRecordType)
_Namespace.addCategoryObject('elementBinding', BriefRecord.name().localName(), BriefRecord)

issued = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(_Namespace_dct, u'issued'), pyxb.bundles.opengis._dc.SimpleLiteral)
_Namespace_dct.addCategoryObject('elementBinding', issued.name().localName(), issued)

educationLevel = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(_Namespace_dct, u'educationLevel'), pyxb.bundles.opengis._dc.SimpleLiteral)
_Namespace_dct.addCategoryObject('elementBinding', educationLevel.name().localName(), educationLevel)



DCMIRecordType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(pyxb.bundles.opengis._dc.Namespace, u'DC-element'), pyxb.bundles.opengis._dc.SimpleLiteral, abstract=pyxb.binding.datatypes.boolean(1), scope=DCMIRecordType))
DCMIRecordType._GroupModel_2 = pyxb.binding.content.GroupChoice(
    pyxb.binding.content.ParticleModel(DCMIRecordType._UseForTag(pyxb.namespace.ExpandedName(pyxb.bundles.opengis._dc.Namespace, u'DC-element')), min_occurs=1, max_occurs=1)
    )
DCMIRecordType._GroupModel_ = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(DCMIRecordType._GroupModel_2, min_occurs=0L, max_occurs=None)
    )
DCMIRecordType._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(DCMIRecordType._GroupModel_, min_occurs=1, max_occurs=1)
    )
DCMIRecordType._ContentModel = pyxb.binding.content.ParticleModel(DCMIRecordType._GroupModel, min_occurs=1, max_occurs=1)



RecordType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(_Namespace_ows, u'BoundingBox'), pyxb.bundles.opengis.ows.BoundingBoxType, scope=RecordType))

RecordType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(_Namespace, u'AnyText'), EmptyType, scope=RecordType))
RecordType._GroupModel_3 = pyxb.binding.content.GroupChoice(
    pyxb.binding.content.ParticleModel(RecordType._UseForTag(pyxb.namespace.ExpandedName(pyxb.bundles.opengis._dc.Namespace, u'DC-element')), min_occurs=1, max_occurs=1)
    )
RecordType._GroupModel_2 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(RecordType._GroupModel_3, min_occurs=0L, max_occurs=None)
    )
RecordType._GroupModel_ = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(RecordType._GroupModel_2, min_occurs=1, max_occurs=1)
    )
RecordType._GroupModel_4 = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(RecordType._UseForTag(pyxb.namespace.ExpandedName(_Namespace, u'AnyText')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(RecordType._UseForTag(pyxb.namespace.ExpandedName(_Namespace_ows, u'BoundingBox')), min_occurs=0L, max_occurs=None)
    )
RecordType._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(RecordType._GroupModel_, min_occurs=1, max_occurs=1),
    pyxb.binding.content.ParticleModel(RecordType._GroupModel_4, min_occurs=1, max_occurs=1)
    )
RecordType._ContentModel = pyxb.binding.content.ParticleModel(RecordType._GroupModel, min_occurs=1, max_occurs=1)



SummaryRecordType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(_Namespace_dct, u'modified'), pyxb.bundles.opengis._dc.SimpleLiteral, scope=SummaryRecordType))

SummaryRecordType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(_Namespace_ows, u'BoundingBox'), pyxb.bundles.opengis.ows.BoundingBoxType, scope=SummaryRecordType))

SummaryRecordType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(_Namespace_dct, u'abstract'), pyxb.bundles.opengis._dc.SimpleLiteral, scope=SummaryRecordType))

SummaryRecordType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(pyxb.bundles.opengis._dc.Namespace, u'subject'), pyxb.bundles.opengis._dc.SimpleLiteral, scope=SummaryRecordType, documentation=u'A topic of the content of the resource. Typically, Subject will be \n      expressed as keywords, key phrases, or classification codes that \n      describe a topic of the resource. Recommended best practice is to \n      select a value from a controlled vocabulary or formal classification \n      scheme.'))

SummaryRecordType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(pyxb.bundles.opengis._dc.Namespace, u'title'), pyxb.bundles.opengis._dc.SimpleLiteral, scope=SummaryRecordType, documentation=u'A name given to the resource. Typically, Title will be a name by \n      which the resource is formally known.'))

SummaryRecordType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(pyxb.bundles.opengis._dc.Namespace, u'relation'), pyxb.bundles.opengis._dc.SimpleLiteral, scope=SummaryRecordType, documentation=u'A reference to a related resource. Recommended best practice is to \n      identify the referenced resource by means of a string or number \n      conforming to a formal identification system.'))

SummaryRecordType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(_Namespace_dct, u'spatial'), pyxb.bundles.opengis._dc.SimpleLiteral, scope=SummaryRecordType))

SummaryRecordType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(pyxb.bundles.opengis._dc.Namespace, u'identifier'), pyxb.bundles.opengis._dc.SimpleLiteral, scope=SummaryRecordType, documentation=u'An unambiguous reference to the resource within a given context. \n      Recommended best practice is to identify the resource by means of a \n      string or number conforming to a formal identification system. Formal \n      identification systems include but are not limited to the Uniform \n      Resource Identifier (URI) (including the Uniform Resource Locator \n      (URL)), the Digital Object Identifier (DOI), and the International \n      Standard Book Number (ISBN).'))

SummaryRecordType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(pyxb.bundles.opengis._dc.Namespace, u'type'), pyxb.bundles.opengis._dc.SimpleLiteral, scope=SummaryRecordType, documentation=u'The nature or genre of the content of the resource. Type includes \n      terms describing general categories, functions, genres, or aggregation \n      levels for content. Recommended best practice is to select a value \n      from a controlled vocabulary (for example, the DCMI Type Vocabulary). \n      To describe the physical or digital manifestation of the resource, \n      use the Format element.'))

SummaryRecordType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(pyxb.bundles.opengis._dc.Namespace, u'format'), pyxb.bundles.opengis._dc.SimpleLiteral, scope=SummaryRecordType, documentation=u'The physical or digital manifestation of the resource. Typically, \n      Format will include the media-type or dimensions of the resource. \n      Format may be used to identify the software, hardware, or other \n      equipment needed to display or operate the resource. Examples of \n      dimensions include size and duration. Recommended best practice is to \n      select a value from a controlled vocabulary (for example, the list \n      of Internet Media Types defining computer media formats).'))
SummaryRecordType._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(SummaryRecordType._UseForTag(pyxb.namespace.ExpandedName(pyxb.bundles.opengis._dc.Namespace, u'identifier')), min_occurs=1L, max_occurs=None),
    pyxb.binding.content.ParticleModel(SummaryRecordType._UseForTag(pyxb.namespace.ExpandedName(pyxb.bundles.opengis._dc.Namespace, u'title')), min_occurs=1L, max_occurs=None),
    pyxb.binding.content.ParticleModel(SummaryRecordType._UseForTag(pyxb.namespace.ExpandedName(pyxb.bundles.opengis._dc.Namespace, u'type')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(SummaryRecordType._UseForTag(pyxb.namespace.ExpandedName(pyxb.bundles.opengis._dc.Namespace, u'subject')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(SummaryRecordType._UseForTag(pyxb.namespace.ExpandedName(pyxb.bundles.opengis._dc.Namespace, u'format')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(SummaryRecordType._UseForTag(pyxb.namespace.ExpandedName(pyxb.bundles.opengis._dc.Namespace, u'relation')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(SummaryRecordType._UseForTag(pyxb.namespace.ExpandedName(_Namespace_dct, u'modified')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(SummaryRecordType._UseForTag(pyxb.namespace.ExpandedName(_Namespace_dct, u'abstract')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(SummaryRecordType._UseForTag(pyxb.namespace.ExpandedName(_Namespace_dct, u'spatial')), min_occurs=0L, max_occurs=None),
    pyxb.binding.content.ParticleModel(SummaryRecordType._UseForTag(pyxb.namespace.ExpandedName(_Namespace_ows, u'BoundingBox')), min_occurs=0L, max_occurs=None)
    )
SummaryRecordType._ContentModel = pyxb.binding.content.ParticleModel(SummaryRecordType._GroupModel, min_occurs=1, max_occurs=1)



BriefRecordType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(pyxb.bundles.opengis._dc.Namespace, u'identifier'), pyxb.bundles.opengis._dc.SimpleLiteral, scope=BriefRecordType, documentation=u'An unambiguous reference to the resource within a given context. \n      Recommended best practice is to identify the resource by means of a \n      string or number conforming to a formal identification system. Formal \n      identification systems include but are not limited to the Uniform \n      Resource Identifier (URI) (including the Uniform Resource Locator \n      (URL)), the Digital Object Identifier (DOI), and the International \n      Standard Book Number (ISBN).'))

BriefRecordType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(_Namespace_ows, u'BoundingBox'), pyxb.bundles.opengis.ows.BoundingBoxType, scope=BriefRecordType))

BriefRecordType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(pyxb.bundles.opengis._dc.Namespace, u'type'), pyxb.bundles.opengis._dc.SimpleLiteral, scope=BriefRecordType, documentation=u'The nature or genre of the content of the resource. Type includes \n      terms describing general categories, functions, genres, or aggregation \n      levels for content. Recommended best practice is to select a value \n      from a controlled vocabulary (for example, the DCMI Type Vocabulary). \n      To describe the physical or digital manifestation of the resource, \n      use the Format element.'))

BriefRecordType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(pyxb.bundles.opengis._dc.Namespace, u'title'), pyxb.bundles.opengis._dc.SimpleLiteral, scope=BriefRecordType, documentation=u'A name given to the resource. Typically, Title will be a name by \n      which the resource is formally known.'))
BriefRecordType._GroupModel = pyxb.binding.content.GroupSequence(
    pyxb.binding.content.ParticleModel(BriefRecordType._UseForTag(pyxb.namespace.ExpandedName(pyxb.bundles.opengis._dc.Namespace, u'identifier')), min_occurs=1L, max_occurs=None),
    pyxb.binding.content.ParticleModel(BriefRecordType._UseForTag(pyxb.namespace.ExpandedName(pyxb.bundles.opengis._dc.Namespace, u'title')), min_occurs=1L, max_occurs=None),
    pyxb.binding.content.ParticleModel(BriefRecordType._UseForTag(pyxb.namespace.ExpandedName(pyxb.bundles.opengis._dc.Namespace, u'type')), min_occurs=0L, max_occurs=1),
    pyxb.binding.content.ParticleModel(BriefRecordType._UseForTag(pyxb.namespace.ExpandedName(_Namespace_ows, u'BoundingBox')), min_occurs=0L, max_occurs=None)
    )
BriefRecordType._ContentModel = pyxb.binding.content.ParticleModel(BriefRecordType._GroupModel, min_occurs=1, max_occurs=1)

conformsTo._setSubstitutionGroup(pyxb.bundles.opengis._dc.relation)

mediator._setSubstitutionGroup(audience)

modified._setSubstitutionGroup(pyxb.bundles.opengis._dc.date)

Record._setSubstitutionGroup(AbstractRecord)

accessRights._setSubstitutionGroup(pyxb.bundles.opengis._dc.rights)

provenance._setSubstitutionGroup(pyxb.bundles.opengis._dc.DC_element)

references._setSubstitutionGroup(pyxb.bundles.opengis._dc.relation)

isVersionOf._setSubstitutionGroup(pyxb.bundles.opengis._dc.relation)

requires._setSubstitutionGroup(pyxb.bundles.opengis._dc.relation)

rightsHolder._setSubstitutionGroup(pyxb.bundles.opengis._dc.DC_element)

spatial._setSubstitutionGroup(pyxb.bundles.opengis._dc.coverage)

SummaryRecord._setSubstitutionGroup(AbstractRecord)

tableOfContents._setSubstitutionGroup(pyxb.bundles.opengis._dc.description)

license._setSubstitutionGroup(pyxb.bundles.opengis._dc.rights)

temporal._setSubstitutionGroup(pyxb.bundles.opengis._dc.coverage)

valid._setSubstitutionGroup(pyxb.bundles.opengis._dc.date)

isPartOf._setSubstitutionGroup(pyxb.bundles.opengis._dc.relation)

bibliographicCitation._setSubstitutionGroup(pyxb.bundles.opengis._dc.identifier)

audience._setSubstitutionGroup(pyxb.bundles.opengis._dc.DC_element)

available._setSubstitutionGroup(pyxb.bundles.opengis._dc.date)

created._setSubstitutionGroup(pyxb.bundles.opengis._dc.date)

replaces._setSubstitutionGroup(pyxb.bundles.opengis._dc.relation)

dateAccepted._setSubstitutionGroup(pyxb.bundles.opengis._dc.date)

dateCopyrighted._setSubstitutionGroup(pyxb.bundles.opengis._dc.date)

alternative._setSubstitutionGroup(pyxb.bundles.opengis._dc.title)

hasPart._setSubstitutionGroup(pyxb.bundles.opengis._dc.relation)

dateSubmitted._setSubstitutionGroup(pyxb.bundles.opengis._dc.date)

hasFormat._setSubstitutionGroup(pyxb.bundles.opengis._dc.relation)

abstract._setSubstitutionGroup(pyxb.bundles.opengis._dc.description)

DCMIRecord._setSubstitutionGroup(AbstractRecord)

extent._setSubstitutionGroup(pyxb.bundles.opengis._dc.format)

hasVersion._setSubstitutionGroup(pyxb.bundles.opengis._dc.relation)

medium._setSubstitutionGroup(pyxb.bundles.opengis._dc.format)

isFormatOf._setSubstitutionGroup(pyxb.bundles.opengis._dc.relation)

isReferencedBy._setSubstitutionGroup(pyxb.bundles.opengis._dc.relation)

isRequiredBy._setSubstitutionGroup(pyxb.bundles.opengis._dc.relation)

isReplacedBy._setSubstitutionGroup(pyxb.bundles.opengis._dc.relation)

BriefRecord._setSubstitutionGroup(AbstractRecord)

issued._setSubstitutionGroup(pyxb.bundles.opengis._dc.date)

educationLevel._setSubstitutionGroup(audience)
