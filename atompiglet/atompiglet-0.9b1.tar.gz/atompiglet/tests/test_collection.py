#!/usr/bin/env python
# encoding: utf-8
"""
test_collection.py

Created by Keith Fahlgren on Sun Jan 18 06:59:53 PST 2009
Copyright (c) 2009 O'Reilly Media. All rights reserved.
"""

import os
import tempfile
import urlparse
import uuid
from cStringIO import StringIO

from lxml import etree

from nose.tools import *

import mock_http

from atompiglet import NAMESPACES
from atompiglet.auth import BasicAuth 
from atompiglet.server import Server 
from atompiglet.collection import Collection, CollectionAdditionError

import helpers

class TestCollection:
    def setup(self):
        self.testfiles_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'files'))
        self.test_pdf = os.path.join(self.testfiles_dir, 'a_test.pdf')
        self.pdf_mimetype = 'application/pdf' 

        self.to_delete = []

        username = 'orm'
        password = '123456789'
        self.kurt_auth = BasicAuth(username, password)
        self.server = Server(Server.TEST_KURT, auth=self.kurt_auth)
        self.orm_wksp = self.server.workspaces["O'Reilly Media"]
        self.webpdfs_coll = self.orm_wksp.collections["Web PDFs"]
        self.meta_server = Server(Server.TEST_META, auth=self.kurt_auth)
        self.entry_wksp = self.meta_server.workspaces['Automation Results']
        self.entry_coll = self.entry_wksp.collections['Results']

        self.mock_port = 45994
        mock_hostname = 'localhost'
        self.mock_url = 'http://%s:%s' % (mock_hostname, self.mock_port)
        self.fake_server = helpers.fake_server(self.mock_port, self.mock_url, self.kurt_auth)
        self.fake_orm_wksp = self.fake_server.workspaces["O'Reilly Media"]
        self.fake_webpdfs_coll = self.fake_orm_wksp.collections["Web PDFs"]

        self.default_text = str(uuid.uuid4())
        self.default_title = str(uuid.uuid4())

    def test_collection_title(self):
        """Every Collection should have a title."""
        for coll in self.orm_wksp.collections.values():
            assert(coll.title)

    def test_collection_location(self):
        """Every Collection should have a location."""
        for coll in self.orm_wksp.collections.values():
            assert(coll.location)

    def test_collection_location_structure(self):
        """Every Collection's location should be absolute an HTTP URL."""
        for coll in self.orm_wksp.collections.values():
            first_four = coll.location[0:4]
            assert_equal('http', first_four)

    def test_collection_etree(self):
        """Every Collection should have a representation in XML format for low-level XPath querying."""
        for coll in self.orm_wksp.collections.values():
            assert(coll.etree.xpath is not None)

    def test_collection_oreilly_books(self):
        """The "O'Reilly Media" workspace on the test server should have a "Books" app:collection"""
        assert("Books" in self.orm_wksp.collections)

    def test_collection_oreilly_webpdfs(self):
        """The "O'Reilly Media" workspace on the test server should have a "Web PDFs" app:collection"""
        assert("Web PDFs" in self.orm_wksp.collections)

    def test_collection_oreilly_webpdfs_add(self):
        """The "Web PDFs" app:collection should allow new PDFs to be added to it."""
        new_entry = self.webpdfs_coll.add_from_file(self.test_pdf, self.pdf_mimetype)
        self.to_delete.append(new_entry)
        assert(new_entry)
    
    def test_collection_oreilly_webpdfs_add_by_fileobject(self):
        """The "Web PDFs" app:collection should allow new PDFs to be added to it from read-able objects."""
        test_input = StringIO()
        test_file = open(self.test_pdf, mode='rb')
        test_input.write(test_file.read())
        test_input.seek(0)
        test_length = len(test_input.getvalue())
        new_entry = self.webpdfs_coll.add_from_file(test_input, self.pdf_mimetype,
                                                    content_length=test_length)
        self.to_delete.append(new_entry)
        assert(new_entry)

    def test_collection_oreilly_webpdfs_add_fails(self):
        """The "Web PDFs" app:collection should not allow non-PDFs to be added to it."""

        tf = tempfile.NamedTemporaryFile(mode='w')
        tf.write('Not a PDF')
        assert_raises(CollectionAdditionError, self.webpdfs_coll.add_from_file, tf.name, self.pdf_mimetype)

    def test_collection_new_entry_location(self):
        """New Entries should have an absolute location."""
        new_entry = self.webpdfs_coll.add_from_file(self.test_pdf, self.pdf_mimetype)
        self.to_delete.append(new_entry)
        first_four = new_entry.location[0:4]
        assert_equal('http', first_four)

    def test_collection_oreilly_webpdfs_delete(self):
        """New Entries added from a file should be able to be deleted."""
        new_entry = self.webpdfs_coll.add_from_file(self.test_pdf, self.pdf_mimetype)
        was_deleted = new_entry.delete()
        assert(was_deleted)
        
    
    def test_collection_add_entry_text(self):
        """New Entries should be able to have text as their content."""
        new_entry = self.entry_coll.add_entry(self.default_text, self.default_title)
        self.to_delete.append(new_entry)
        assert_equal(self.default_text,  new_entry.content.text)
        assert_equal(self.default_title, new_entry.title)

    def test_collection_add_entry_content_location(self):
        """New Entries should be returned with a minimum of HTTP requests if the server sends the proper headers."""
        path = urlparse.urlparse(self.fake_webpdfs_coll.location).path
        mock = mock_http.MockHTTP(self.mock_port)
        entry_body = helpers.fake_entry()
        mock.expects('POST', path, times=mock_http.once).will(http_code=201, 
                                                              body=entry_body,
                                                              headers={'Location': path + '/1',
                                                                       'Content-Location': path + '/1'},
                                                             )           
        new_entry = self.fake_webpdfs_coll.add_entry(self.default_text, self.default_title)
        # Explicitly _no_ GET here
        assert(new_entry)
        mock.verify()
    
    def test_collection_add_entry_fails(self):
        """New Entries should raise Exceptions when they are not allowed by the server."""
        path = urlparse.urlparse(self.fake_webpdfs_coll.location).path
        mock = mock_http.MockHTTP(self.mock_port)
        mock.expects('POST', '/' + helpers.PDF_COLLECTION_URL, times=mock_http.once).will(http_code=500)
        assert_raises(CollectionAdditionError, self.fake_webpdfs_coll.add_entry, self.default_text, self.default_title)
        mock.verify()
    
    def test_collection_add_entry_xhtml(self):
        """New Entries should be able to have xhtml as their content."""
        content = 'Test XHTML Content'
        test_xhtml_str = '<div xmlns="%s">%s</div>' % (NAMESPACES['xhtml'], content)
        title = 'XHTML Content'
        xhtml = etree.ElementTree(etree.fromstring(test_xhtml_str))
        new_entry = self.entry_coll.add_entry(xhtml, title, content_type='xhtml')
        self.to_delete.append(new_entry)
        assert_equal(len(new_entry.content), 1)
        assert_equal(new_entry.content[0].tag, '{%s}div' % NAMESPACES['xhtml'])
        assert_equal(new_entry.content[0].text, content)

    def test_collection_add_entry_slug(self):
        """New Entries should be able to have a Slug header set to specify the requested atom:id."""
        text = 'Some text'
        title = 'Slug Specified'
        slug = 'entry_resource_slug_id'
        new_entry = self.entry_coll.add_entry(text, title, slug=slug)
        self.to_delete.append(new_entry)
        assert_equal(slug, new_entry.atom_id)

    def test_collection_oreilly_webpdfs_entries(self):
        """The "Web PDFs" app:collection should have entries in it"""
        new_entry = self.webpdfs_coll.add_from_file(self.test_pdf, self.pdf_mimetype)
        self.to_delete.append(new_entry)
        new_entry_two = self.webpdfs_coll.add_from_file(self.test_pdf, self.pdf_mimetype)
        self.to_delete.append(new_entry_two)
        entry = self.webpdfs_coll.entries().next()
        assert(entry)
        
    def test_slug(self):
        """The "Web PDFs" app:collection should allow PDFs to be added to it with custom atom:ids specified through the Slug header."""
        slug = 'media_resource_slug_id'
        new_entry = self.webpdfs_coll.add_from_file(self.test_pdf, self.pdf_mimetype, slug=slug)
        self.to_delete.append(new_entry)
        assert_equal(slug, new_entry.atom_id)

    def test_collection_display(self):
        """A Collection should have a developer-oriented string representation."""
        self.server = Server(Server.TEST_KURT)
        self.orm_wksp = self.server.workspaces["O'Reilly Media"]
        self.webpdfs_coll = self.orm_wksp.collections["Web PDFs"]
        r = repr(self.webpdfs_coll)
        assert(r)
    
    def teardown(self):
        for d in self.to_delete:
            try:
                d.delete()
            except:    
                print "%s could not be deleted!" % (d)
