#!/usr/bin/env python
# encoding: utf-8
"""
test_etags.py

Created by Keith Fahlgren on Mon Oct  5 11:01:17 PDT 2009
Copyright (c) 2009 O'Reilly Media. All rights reserved.
"""

from __future__ import with_statement


import datetime
import logging
import os
import urlparse
import uuid

import pytz
from lxml import etree
from nose.tools import *

import mock_http

import atompiglet.rdf as rdf
from atompiglet import NAMESPACES, get_absolute_url
from atompiglet.auth import BasicAuth 
from atompiglet.entry import Entry
from atompiglet.server import Server
from atompiglet.errors import AtomPigletError, ServerError, NotFoundError, EntryError, EntryEditError 
from atompiglet.collection import Collection

import helpers

log = logging.getLogger(__name__)


class TestEtags:
    def setup(self):
        testfiles_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'files'))
        self.test_pdf = os.path.join(testfiles_dir, 'a_test.pdf')
        self.kurt_auth = BasicAuth('orm','123456789')
        self.mock_port = 45994
        mock_hostname = 'localhost'
        self.mock_url = 'http://%s:%s' % (mock_hostname, self.mock_port)

        self.server = helpers.fake_server(self.mock_port, self.mock_url, self.kurt_auth)
        self.new_entry = helpers.fake_new_pdf_entry(mock_hostname, self.mock_port, self.mock_url, self.server, self.test_pdf)

    def test_etag_wrong(self):
        '''An Entry should not be able to be updated if the server supports entity tags and the Entry has been externally modified.'''
        original_title = self.new_entry.title
        new_title = str(uuid.uuid4())

        mock = mock_http.MockHTTP(self.mock_port)
        path = urlparse.urlparse(self.new_entry.relative_edit_link).path
        mock.expects('PUT', path, times=mock_http.once).will(http_code=412)
        mock.expects('GET', path, times=mock_http.once).will(http_code=200, body=etree.tostring(self.new_entry.etree)) # It'll refresh after blowing up

        self.new_entry.title = new_title
        assert_raises(EntryEditError, self.new_entry.commit_updates)
        assert_equal(self.new_entry.title, original_title)
        mock.verify()

    def test_etag_wrong_for_content(self):
        '''An Entry should not be able to have its media updated if the server supports entity tags and the media has been externally modified.'''
        mock = mock_http.MockHTTP(self.mock_port)
        edit_path = urlparse.urlparse(self.new_entry.relative_edit_link).path
        media_link = self.new_entry.etree.xpath('/atom:entry/atom:link[@rel="edit-media"]', namespaces=NAMESPACES)
        edit_media_path = urlparse.urlparse(get_absolute_url(media_link[0].base, media_link[0].get('href'))).path
        mock.expects('PUT', edit_media_path, times=mock_http.once).will(http_code=412)
        assert_raises(EntryEditError, self.new_entry.update_content_from_file, self.test_pdf)
        mock.verify()

    def test_etag_for_content(self):
        '''An Entry should only be updated if the client sends the server the entity tag headers (If-Match).'''
        mock = mock_http.MockHTTP(self.mock_port)
        edit_path = urlparse.urlparse(self.new_entry.relative_edit_link).path
        media_link = self.new_entry.etree.xpath('/atom:entry/atom:link[@rel="edit-media"]', namespaces=NAMESPACES)
        edit_media_path = urlparse.urlparse(get_absolute_url(media_link[0].base, media_link[0].get('href'))).path
        new_etag = str(uuid.uuid4())
        new_body = 'PDF Updated'
        mock.expects('PUT', edit_media_path, times=mock_http.once, headers={'If-Match': self.new_entry.etag}).will(http_code=200, headers={'ETag': new_etag})
        mock.expects('GET', edit_path, times=mock_http.once).will(http_code=200, body=etree.tostring(self.new_entry.etree), headers={'ETag': new_etag})
        self.new_entry.update_content_from_file(self.test_pdf)
        assert_equal(new_etag, self.new_entry.etag)
        mock.verify()

    def test_etag_for_entry_changes(self):
        '''An Entry should capture changes in the entity tag headers sent from the server.'''
        mock = mock_http.MockHTTP(self.mock_port)
        path = urlparse.urlparse(self.new_entry.relative_edit_link).path
        new_etag = str(uuid.uuid4())
        new_title = str(uuid.uuid4())
        new_entry_with_new_title_body = helpers.fake_entry(title=new_title)
        mock.expects('PUT', path, times=mock_http.once, headers={'If-Match': self.new_entry.etag}).will(http_code=200, headers={'ETag': new_etag})
        mock.expects('GET', path, times=mock_http.once, headers={'If-None-Match': new_etag}      ).will(http_code=304)
        with self.new_entry:
            self.new_entry.title = new_title
        assert_equal(new_title, self.new_entry.title)
        assert_equal(new_etag, self.new_entry.etag)
        mock.verify()

    def test_etag_header(self):
        '''An Entry should only be updated if the client sends the server the entity tag headers (If-Match).'''
        original_title = self.new_entry.title
        new_title = str(uuid.uuid4())

        mock = mock_http.MockHTTP(self.mock_port)
        path = urlparse.urlparse(self.new_entry.relative_edit_link).path
        mock.expects('PUT', path, times=mock_http.once, headers={'If-Match': self.new_entry.etag}).will(http_code=200)
        new_entry_body = helpers.fake_entry(title=new_title)
        mock.expects('GET', path, times=mock_http.once).will(http_code=200, body=new_entry_body)
        self.new_entry.title = new_title
        self.new_entry.commit_updates()
        assert_equal(new_title, self.new_entry.title)
        mock.verify()

    # 304 on refresh
    # Server no Etag

