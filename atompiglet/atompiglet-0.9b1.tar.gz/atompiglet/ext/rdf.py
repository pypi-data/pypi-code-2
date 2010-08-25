#!/usr/bin/env python
# encoding: utf-8
"""
rdf.py

Created by Keith Fahlgren on Thu Jan 22 19:04:41 PST 2009
Copyright (c) 2009 O'Reilly Media. All rights reserved.
"""
import urllib
import os.path
import logging

from lxml import etree

from atompiglet import NAMESPACES
from atompiglet.entry import Entry
import atompiglet.xslt

log = logging.getLogger(__name__)

class UtilsError(Exception):
    """Errors thrown by interacting with RDF features."""
    
def entry_from_unique_urn(server, collection, urn):
    """Given a Server, Collection, and URN, find the unique Entry in the Collection that asserts a relationship with that URN.
    Throws EntryError or ServerError if a unique entry cannot be found."""
    base_url = collection.location
    query_param = 'q'
    query = {query_param : str(urn)}
    full_url = base_url + '?' + urllib.urlencode(query)
    return Entry.from_url(str(full_url), auth_source=collection)
    
def entries_from_predicate(server, collection, predicate, obj):
    """Given a Server and a Collection, finds the Entries in the Collection
    that have a predicate with value object in their RDF."""
    base_url = collection.location
    query = {'predicate': predicate, 'object': obj}
    full_url = base_url + '?' + urllib.urlencode(query)
    return Entry.from_feed_url(str(full_url), auth_source=server)
    
def rdf_for_entry(entry):
    """Takes an atom:entry and returns an RDF representation of it as an etree."""
    return atompiglet.xslt.atom_to_rdf(entry.etree)

def legacy_rdf_for_entry(entry):
    """Takes an atom:entry and returns an RDF representation of it as an etree."""
    return atompiglet.xslt.atom_to_legacy_rdf(entry.etree)

def set_is_format_of(entry, uri):
    """Add or update a dc:isFormatOf relationship to the provided URI in the RDF of the given Entry."""
    is_format_ofs = entry.etree.xpath('/atom:entry/rdf:RDF/rdf:Description/dc:isFormatOf', namespaces=NAMESPACES)
    descriptions  = entry.etree.xpath('/atom:entry/rdf:RDF/rdf:Description', namespaces=NAMESPACES)
    rdfs          = entry.etree.xpath('/atom:entry/rdf:RDF', namespaces=NAMESPACES)
    if len(is_format_ofs) > 1:
        raise UtilsError("Entry at %s has %s dc:isFormat statements! That doesn't make sense to this library author!" % (entry.location, len(is_format_ofs))) #TESTME?
    if len(descriptions) > 1:
        raise UtilsError("Entry at %s has %s rdf:Description statements! That doesn't make sense to this library author!" % (entry.location, len(descriptions)))
    if len(rdfs) > 1:
        raise UtilsError("Entry at %s has %s rdf:RDF statements! That doesn't make sense to this library author!" % (entry.location, len(rdfs)))
    if len(rdfs) == 1:
        rdf = rdfs[0]
    else:
        rdf = etree.SubElement(
            entry.etree.getroot(), '{%s}RDF' % NAMESPACES['rdf'],
            nsmap=NAMESPACES)
    if len(descriptions) == 1:
        description = descriptions[0]
    else:
        description = etree.SubElement(
            rdf, '{%s}Description' % NAMESPACES['rdf'], nsmap=NAMESPACES)
    if len(is_format_ofs) == 1:
        # We just need to update it
        is_format_ofs[0].set('{%s}resource' % NAMESPACES['rdf'], uri) 
    else:
        is_format_of = etree.SubElement(
            description, '{%s}isFormatOf' % NAMESPACES['dc'],
            attrib={'{%s}resource' % NAMESPACES['rdf']: uri},
            nsmap=NAMESPACES)
    entry.commit_updates()
