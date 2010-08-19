from lxml import etree

from oaipmh.metadata import MetadataReader
from oaipmh.common import Metadata



__all__ = ['dspace_mets_namespaces',
           'dspace_mets_reader']

class NestedMetadataReader(MetadataReader):
    def __call__(self, element):
        map = {}
        # create XPathEvaluator for this element
        xpath_evaluator = etree.XPathEvaluator(element, 
                                               namespaces=self._namespaces)
        
        e = xpath_evaluator.evaluate
        # now extra field info according to xpath expr
        for field_name, (field_type, expr) in self._fields.items():
            if field_type == 'bytes':
                value = str(e(expr))
            elif field_type == 'bytesList':
                value = [str(item) for item in e(expr)]
            elif field_type == 'text':
                # make sure we get back unicode strings instead
                # of lxml.etree._ElementUnicodeResult objects.
                value = unicode(e(expr))
            elif field_type == 'textList':
                # make sure we get back unicode strings instead
                # of lxml.etree._ElementUnicodeResult objects.
                value = [unicode(v) for v in e(expr)]
            elif field_type == 'firstText':
                value = e(expr)
                if isinstance(value, list):
                    if len(value) > 0:
                        value = unicode(value[0])
                    else:
                        value = None
                else:
                    value = unicode(value)
            elif isinstance(field_type, MetadataReader):
                value = e(expr)
                if isinstance(value, list):
                    value = [field_type(v) for v in value]
                else:
                    value = field_type(value)
            else:
                raise Error, "Unknown field type: %s" % field_type
            map[field_name] = value
        return Metadata(map)

dspace_mets_namespaces = {
    'oai': 'http://www.openarchives.org/OAI/2.0/',
    'mets': 'http://www.loc.gov/METS/',
    'mods': 'http://www.loc.gov/mods/v3',
    'xlink': 'http://www.w3.org/1999/xlink',
    'dim': 'http://www.dspace.org/xmlns/dspace/dim'}

dspace_mets_bitstream_reader = NestedMetadataReader(
    fields = {
        'identifier': ('firstText','@ID'),
        'mimetype': ('firstText','@MIMETYPE'),
        'size': ('firstText','@SIZE'),
        'checksum': ('firstText','@CHECKSUM'),
        'checksum_type': ('firstText','@CHECKSUMTYPE'),
        'url': ('firstText','mets:FLocat[@LOCTYPE="URL" and @xlink:type="simple"]/@xlink:href'),
    },
    namespaces = dspace_mets_namespaces)

dspace_mets_bundle_reader = NestedMetadataReader(
    fields = {
        'name': ('firstText','@USE'),
        'bitstreams': (dspace_mets_bitstream_reader,'mets:file'),},
    namespaces = dspace_mets_namespaces)

dspace_mets_reader = NestedMetadataReader(
    fields = {
        'creator': ('textList', 'mets:mets/mets:dmdSec/mets:mdWrap[@MDTYPE="MODS"]/mets:xmlData/mods:name/mods:namePart/text()'),
        'issued': ('textList', 'mets:mets/mets:dmdSec/mets:mdWrap[@MDTYPE="MODS"]/mets:xmlData/mods:originInfo/mods:dateIssued/text()'),
        'description': ('textList', 'mets:mets/mets:dmdSec/mets:mdWrap[@MDTYPE="MODS"]/mets:xmlData/mods:note[not(@type)]/text()'),
        'subject': ('textList','mets:mets/mets:dmdSec/mets:mdWrap[@MDTYPE="MODS"]/mets:xmlData/mods:subject/mods:topic/text()'),
        'title': ('textList','mets:mets/mets:dmdSec/mets:mdWrap[@MDTYPE="MODS"]/mets:xmlData/mods:titleInfo/text()'),
        'bundles': (dspace_mets_bundle_reader, 'mets:mets/mets:fileSec/mets:fileGrp'),},
    namespaces = dspace_mets_namespaces)
