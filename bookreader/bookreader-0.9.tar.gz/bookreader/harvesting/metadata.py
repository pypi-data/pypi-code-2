from oaipmh.metadata import MetadataRegistry
from dspace.metadata import NestedMetadataReader

namespaces = {
    'atom': "http://www.w3.org/2005/Atom",
    'ore': "http://www.openarchives.org/ore/terms/",
    'oreatom': "http://www.openarchives.org/ore/atom/",
    'dcterms': "http://purl.org/dc/terms/",
    'oai': 'http://www.openarchives.org/OAI/2.0/',
    'mets': 'http://www.loc.gov/METS/',
    'mods': 'http://www.loc.gov/mods/v3',
    'xlink': 'http://www.w3.org/1999/xlink',
    'dim': 'http://www.dspace.org/xmlns/dspace/dim',
    'rdf': 'http://www.w3.org/1999/02/22-rdf-syntax-ns#',
}

ore_bitstream_reader = NestedMetadataReader(
    fields = {
        'url': ('firstText', '@href'),
        'title': ('firstText', '@title'),
        'mimetype': ('firstText', '@type'),
        'size': ('firstText', '@length'),
        'bundle': ('firstText', '../oreatom:triples/rdf:Description[@rdf:about=./@href]/dcterms:description/text()'),
    },
    namespaces = namespaces)

ore_description_reader = NestedMetadataReader(
    fields = {
        'about': ('firstText', '@rdf:about'),
        'bundle': ('firstText','dcterms:description/text()')
    },
    namespaces = namespaces)

ore_reader = NestedMetadataReader(
    fields = {
        'bitstreams': (ore_bitstream_reader, 'atom:entry/atom:link[@rel="http://www.openarchives.org/ore/terms/aggregates"]'),
        'triples': (ore_description_reader, 'atom:entry/oreatom:triples/rdf:Description[rdf:type/@rdf:resource="http://www.dspace.org/objectModel/DSpaceBitstream"]'),
    },
    namespaces = namespaces)

dim_reader = NestedMetadataReader(
    fields = {
        'creator': ('textList', 'dim:dim/dim:field[@element="creator" and @mdschema="dc"]/text()'),
        'issued': ('firstText', 'dim:dim/dim:field[@element="date" and @mdschema="dc" and @qualifier="issued"]/text()'),
        'created': ('firstText', 'dim:dim/dim:field[@element="date" and @mdschema="dc" and @qualifier="created"]/text()'),
        'title': ('firstText','dim:dim/dim:field[@element="title" and @mdschema="dc" and not(@qualifier)]/text()'),
        'title.alternative': ('textList','dim:dim/dim:field[@element="title" and @mdschema="dc" and @qualifier="alternative"]/text()'),
        'description': ('textList','dim:dim/dim:field[@element="description" and @mdschema="dc" and not(@qualifier="provenance")]/text()'),
        'contributor': ('textList','dim:dim/dim:field[@element="contributor" and @mdschema="dc"]/text()'),
        'subject': ('textList','dim:dim/dim:field[@element="subject" and @mdschema="dc" and not(@qualifier)]/text()'),
        'subject.other': ('textList','dim:dim/dim:field[@element="subject" and @mdschema="dc" and @qualifier="other"]/text()'),
        'publisher': ('textList','dim:dim/dim:field[@element="publisher" and @mdschema="dc"]/text()'),
        'offset': ('firstText', 'dim:dim/dim:field[@element="offset" and @mdschema="local"]/text()'),
        'thumbnail': ('firstText', 'dim:dim/dim:field[@element="thumbnail" and @mdschema="local"]/text()')
    },
    namespaces = namespaces)

metadata_registry = MetadataRegistry()
metadata_registry.registerReader('dim', dim_reader)
metadata_registry.registerReader('ore', ore_reader)

__all__ = ['metadata_registry']
