#!/usr/bin/env python
# encoding: utf-8
"""
test_rdf_utils.py

Created by Keith Fahlgren on Thu Jan 22 19:02:44 PST 2009
Copyright (c) 2009 O'Reilly Media. All rights reserved.
"""

import os
import os.path

from lxml import etree
from nose.tools import *

import atompiglet.rdf 
from atompiglet import NAMESPACES
from atompiglet.auth import BasicAuth 
from atompiglet.server import Server 
import atompiglet.entry
import urlparse

class TestRDFUtils:
    def setup(self):
        self.testfiles_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'files'))
        self.test_pdf = os.path.join(self.testfiles_dir, 'a_test.pdf')
        self.pdf_mimetype = 'application/pdf' 

        self.to_delete = []

        username = 'orm'
        password = '123456789'
        self.server = Server(Server.TEST_KURT, auth=BasicAuth(username, password))
        self.orm_wksp = self.server.workspaces["O'Reilly Media"]
        self.webpdfs_coll = self.orm_wksp.collections["Web PDFs"]
        self.new_entry = self.webpdfs_coll.add_from_file(self.test_pdf, self.pdf_mimetype)
        self.to_delete.append(self.new_entry)

    def test_rdf_utils_set_is_format_of(self):
        """The RDF utilities should be able to add an dc:isFormatOf relationship to an entry."""
        urn = "urn:x-domain:oreilly.com:atompiglet-test-rdf-utils:1"
        atompiglet.rdf.set_is_format_of(self.new_entry, urn)
        entry_again = atompiglet.entry.Entry.from_url(self.new_entry.location)
        current_is_format_of = entry_again.etree.xpath('/atom:entry/rdf:RDF/rdf:Description/dc:isFormatOf/@rdf:resource',
                                                       namespaces=NAMESPACES)
        assert_equal(urn, current_is_format_of[0])

    def test_rdf_utils_set_is_format_of_multiple_rdf(self):
        """The RDF utilities should complain when asked to add an dc:isFormatOf relationship to an entry that has two rdf:RDF tags."""
        urn = "urn:x-domain:oreilly.com:atompiglet-test-rdf-utils:1"
        etree.SubElement(self.new_entry.etree.getroot(),
                         '{%s}RDF' % NAMESPACES['rdf'], nsmap=NAMESPACES)
        etree.SubElement(self.new_entry.etree.getroot(),
                         '{%s}RDF' % NAMESPACES['rdf'], nsmap=NAMESPACES)
        assert_raises(atompiglet.rdf.UtilsError,
                      atompiglet.rdf.set_is_format_of, self.new_entry, urn)
    
    def test_rdf_utils_set_is_format_of_multiple_descriptions(self):
        """The RDF utilities should complain when asked to add an dc:isFormatOf relationship to an entry that has two rdf:RDF tags."""
        urn = "urn:x-domain:oreilly.com:atompiglet-test-rdf-utils:1"
        rdf = etree.SubElement(self.new_entry.etree.getroot(),
                               '{%s}RDF' % NAMESPACES['rdf'], nsmap=NAMESPACES)
        etree.SubElement(rdf, '{%s}Description' % NAMESPACES['rdf'], nsmap=NAMESPACES)
        etree.SubElement(rdf, '{%s}Description' % NAMESPACES['rdf'], nsmap=NAMESPACES)
        assert_raises(atompiglet.rdf.UtilsError,
                      atompiglet.rdf.set_is_format_of, self.new_entry, urn)
    
    def test_rdf_utils_set_is_format_of_update(self):
        """The RDF utilities should be able to update an dc:isFormatOf relationship to an entry."""
        urn = "urn:x-domain:oreilly.com:atompiglet-test-rdf-utils:2"
        atompiglet.rdf.set_is_format_of(self.new_entry, urn)
        entry_two = atompiglet.entry.Entry.from_url(self.new_entry.location,
                                                    auth_source=self.new_entry)

        urn_two = "urn:x-domain:oreilly.com:atompiglet-test-rdf-utils:2"
        atompiglet.rdf.set_is_format_of(entry_two, urn_two)
        entry_three = atompiglet.entry.Entry.from_url(entry_two.location)
        current_is_format_of = entry_three.etree.xpath('/atom:entry/rdf:RDF/rdf:Description/dc:isFormatOf/@rdf:resource',
                                                       namespaces=NAMESPACES)
        assert_equal(urn_two, current_is_format_of[0])

    def test_rdf_utils_entry_from_unique_urn(self):
        """The RDF utilities should be able to get an entry (on some servers) tagged uniquely by dc:isFormatOf."""
        urn = "urn:x-domain:oreilly.com:atompiglet-test-rdf-utils:1"
        old_entry_id = self.new_entry.atom_id
        atompiglet.rdf.set_is_format_of(self.new_entry, urn)

        entry_again = atompiglet.rdf.entry_from_unique_urn(self.server, self.webpdfs_coll, urn)
        new_entry_id = entry_again.atom_id
        assert_equal(old_entry_id, new_entry_id)

    def test_rdf_utils_entry_from_unique_urn_remodify(self):
        """The RDF utilities should be able to modify and re-post an entry (on some servers) tagged uniquely by dc:isFormatOf."""
        urn = "urn:x-domain:oreilly.com:atompiglet-test-rdf-utils:1"
        old_entry_id = self.new_entry.atom_id
        atompiglet.rdf.set_is_format_of(self.new_entry, urn)

        entry_again = atompiglet.rdf.entry_from_unique_urn(self.server, self.webpdfs_coll, urn)
        new_entry_id = entry_again.atom_id
        assert_equal(old_entry_id, new_entry_id)
        descriptions = entry_again.etree.xpath('/atom:entry/rdf:RDF/rdf:Description', namespaces=NAMESPACES)
        assert_equal(len(descriptions), 1)
        title = etree.SubElement(descriptions[0], '{%s}title' % NAMESPACES['dc'])
        title.text = 'A test title.'
        entry_again.commit_updates()
        entry_again_again = atompiglet.rdf.entry_from_unique_urn(self.server, self.webpdfs_coll, urn)
        old_title = entry_again.etree.xpath('/atom:entry/rdf:RDF/rdf:Description/dc:title/text()', namespaces=NAMESPACES)
        new_title = entry_again_again.etree.xpath('/atom:entry/rdf:RDF/rdf:Description/dc:title/text()', namespaces=NAMESPACES)
        assert_equal(old_title, new_title)
        
    def test_rdf_utils_entry_from_predicate(self):
        """The RDF utilities should be able to retreive entries by searching by predicate."""
        test_urn = 'urn:x-domain:oreilly.com:product:9780596158217.EBOOK'
        entry_element = self.new_entry.etree.getroot() # atom:entry
        rdf_element = etree.SubElement(entry_element, '{%s}RDF' % NAMESPACES['rdf'])
        description_element = etree.SubElement(rdf_element, '{%s}Description' % NAMESPACES['rdf'])
        isPartOf_element = etree.SubElement(description_element,
                                            '{%s}isPartOf' % NAMESPACES['dc'],
                                            attrib={'{%s}resource' % NAMESPACES['rdf']:
                                                    test_urn})
        self.new_entry.commit_updates()
        entry_feed = list(atompiglet.rdf.entries_from_predicate(
            self.server, self.webpdfs_coll,
            urlparse.urljoin(NAMESPACES['dc'], 'isPartOf'), test_urn))
        found = False
        for entry in entry_feed:
            assert(entry.etree.xpath('/atom:entry/rdf:RDF/rdf:Description/dc:isPartOf[@rdf:resource="%s"]' % test_urn,
                                     namespaces=NAMESPACES))
            if entry.atom_id == self.new_entry.atom_id:
                found = True
        assert(found)
    
    def test_rdf_to_atom_sample_video_entry(self):
        """An Entry should be able to be transformed into RDF."""
        test_file = os.path.join(os.path.dirname(__file__), 'files/video.xml')
        entry = atompiglet.entry.Entry(test_file, etree.parse(test_file))
        rdf = atompiglet.rdf.rdf_for_entry(entry)
        assert_equal(rdf.xpath('/rdf:RDF/rdf:Description/@rdf:about',
                               namespaces=NAMESPACES)[0],
                     'http://charles.vz.west.ora.com:8082/atom/oreilly/videos/2')
        assert_equal(rdf.xpath('/rdf:RDF/rdf:Description/rdf:type/@rdf:resource',
                               namespaces=NAMESPACES)[0],
                     'http://www.w3.org/2005/Atomentry')
        assert_equal(rdf.xpath('/rdf:RDF/rdf:Description/dc:isPartOf/@rdf:resource',
                               namespaces=NAMESPACES)[0],
                     'urn:x-domain:oreilly.com:product:9780596802103.VIDEO')
        assert_equal(rdf.xpath('/rdf:RDF/rdf:Description/dc:identifier/text()',
                               namespaces=NAMESPACES)[0],
                     'tag:oreilly.com,2009-02-10:/oreilly/videos/2')
        
    def test_rdf_to_atom_gypsy_media_entry(self):
        """An Entry from Gypsy should be able to be transformed into RDF."""
        test_file = os.path.join(os.path.dirname(__file__), 'files/gypsy_media_entry.xml')
        entry = atompiglet.entry.Entry(test_file, etree.parse(test_file))
        rdf = atompiglet.rdf.rdf_for_entry(entry)
        assert_equal(rdf.xpath('/rdf:RDF/rdf:Description/@rdf:about',
                               namespaces=NAMESPACES)[0],
                     'http://mediaservice.oreilly.com/gypsy/atom/oreilly/ebooks/tag:oreilly.com,2008-12-15:8b15dfface7e48e1adb9bfe57f8241ec')
        assert_equal(rdf.xpath('/rdf:RDF/rdf:Description/rdf:type/@rdf:resource',
                               namespaces=NAMESPACES)[0],
                     'http://www.w3.org/2005/Atomentry')
        assert_equal(rdf.xpath('/rdf:RDF/rdf:Description/dc:identifier/text()',
                               namespaces=NAMESPACES)[0],
                     'tag:oreilly.com,2008-12-15:8b15dfface7e48e1adb9bfe57f8241ec')
        assert_equal(rdf.xpath('/rdf:RDF/rdf:Description/dc:isFormatOf/@rdf:resource',
                               namespaces=NAMESPACES)[0],
                     'urn:x-domain:oreilly.com:product:9780596158217.EBOOK')

    def test_rdf_to_atom_gypsy_media_entry_no_edit_link(self):
        """An Entry without an edit link should be able to be transformed into RDF."""
        test_file = os.path.join(os.path.dirname(__file__), 'files/gypsy_media_entry_no_edits.xml')
        entry = atompiglet.entry.Entry(test_file, etree.parse(test_file))
        rdf = atompiglet.rdf.rdf_for_entry(entry)
        assert_equal(rdf.xpath('/rdf:RDF/rdf:Description/@rdf:about',
                               namespaces=NAMESPACES)[0],
                     'tag:oreilly.com,2008-12-15:8b15dfface7e48e1adb9bfe57f8241ec')
        assert_equal(rdf.xpath('/rdf:RDF/rdf:Description/rdf:type/@rdf:resource',
                               namespaces=NAMESPACES)[0],
                     'http://www.w3.org/2005/Atomentry')
        assert_equal(rdf.xpath('/rdf:RDF/rdf:Description/dc:identifier/text()',
                               namespaces=NAMESPACES)[0],
                     'tag:oreilly.com,2008-12-15:8b15dfface7e48e1adb9bfe57f8241ec')
        assert_equal(rdf.xpath('/rdf:RDF/rdf:Description/dc:isFormatOf/@rdf:resource',
                               namespaces=NAMESPACES)[0],
                     'urn:x-domain:oreilly.com:product:9780596158217.EBOOK')
    
    def teardown(self):
        for d in self.to_delete:
            try:
                d.delete()
            except:    
                print "%s could not be deleted!" % (d)
