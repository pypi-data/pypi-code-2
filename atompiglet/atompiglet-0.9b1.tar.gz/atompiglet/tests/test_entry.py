#!/usr/bin/env python
# encoding: utf-8
"""
test_entry.py

Created by Keith Fahlgren on Wed Jan 21 09:33:57 PST 2009
Copyright (c) 2009 O'Reilly Media. All rights reserved.
"""

from __future__ import with_statement

import datetime
import logging
import os
import shutil
import tempfile
import urlparse
import uuid
from cStringIO import StringIO


import pytz
from lxml import etree
from nose.tools import *
from nose.plugins.skip import SkipTest

import mock_http

from atompiglet import NAMESPACES, get_absolute_url
from atompiglet.auth import BasicAuth 
from atompiglet.entry import Entry
from atompiglet.server import Server
from atompiglet.errors import AtomPigletError, ServerError, NotFoundError, EntryError, EntryEditError 
from atompiglet.collection import Collection

import helpers 

log = logging.getLogger(__name__)


class TestEntry:
    def setup(self):
        self.testfiles_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'files'))
        self.test_pdf = os.path.join(self.testfiles_dir, 'a_test.pdf')
        self.test_pdf_modified = os.path.join(self.testfiles_dir, 'a_test_modified.pdf')

        self.auth = BasicAuth('a','b')
        self.mock_port = 45994
        mock_hostname = 'localhost'
        self.mock_url = 'http://%s:%s' % (mock_hostname, self.mock_port)

        self.server = helpers.fake_server(self.mock_port, self.mock_url, self.auth)
        self.new_entry = helpers.fake_new_pdf_entry(mock_hostname, self.mock_port, self.mock_url, self.server, self.test_pdf)

        self.to_delete = []
        self.to_clean = []
        self.tempdir = tempfile.mkdtemp('dumpy')
        (_,self.dumpepubfile) = tempfile.mkstemp(suffix='.epub', dir=self.tempdir)
        (_,self.dumpxmlfile) = tempfile.mkstemp(suffix='.xml', dir=self.tempdir)
        self.to_clean.append(self.dumpepubfile)
        self.to_clean.append(self.dumpxmlfile)

    def test_entry_etree(self):
        """An Entry should have a representation in XML format for low-level XPath querying."""
        assert(self.new_entry.etree.xpath is not None)

    def test_entry_not_an_entry_fail(self):
        """An Entry should only be created if given a valid atom:entry."""
        feed = etree.ElementTree(etree.Element('{%s}feed' % NAMESPACES['atom']))
        location = 'bogus'
        assert_raises(EntryError, Entry, location, feed)

    def test_entry_etree_mucking_fail(self):
        """An Entry's etree representation should not be able to be arbitrarily mucked with."""
        subtitle = etree.Element('{%s}subtitle' % NAMESPACES['atom'])
        self.new_entry.etree.getroot().append(subtitle)
        assert_raises(EntryError, self.new_entry.commit_updates)

    def test_entry_content(self):
        """An Entry should have downloadable content."""
        mock = mock_http.MockHTTP(self.mock_port)
        #mock.server.wsgi_app.apps.values()[0].log.access_log.setLevel(logging.WARNING) # Shut up, Cherrypy

        content_tree = self.new_entry.etree.xpath('/atom:entry/atom:content', namespaces=NAMESPACES)
        url = urlparse.urlparse(get_absolute_url(content_tree[0].base, content_tree[0].get('src'))).path
        mock.expects('GET', url, times=mock_http.once).will(http_code=200, body="%PDF-1.4\n")
        assert(self.new_entry.content)
        mock.verify()

    def test_entry_content_same(self):
        """An Entry's content should be the same as what was uploaded."""
        uploaded_bytes = open(self.test_pdf).read()
        mock = mock_http.MockHTTP(self.mock_port)
        mock.server.wsgi_app.apps.values()[0].log.access_log.setLevel(logging.WARNING) # Shut up, Cherrypy
        content_tree = self.new_entry.etree.xpath('/atom:entry/atom:content', namespaces=NAMESPACES)
        content_url = urlparse.urlparse(get_absolute_url(content_tree[0].base, content_tree[0].get('src'))).path
        mock.expects('GET', content_url, times=mock_http.once).will(http_code=200, body=uploaded_bytes)
        content = self.new_entry.content
        current_bytes = content.read()
        assert_equal(uploaded_bytes, current_bytes)
        mock.verify()

    def test_entry_content_fail(self):
        """An Entry's content should not be able to be updated if it does not even vaguely resemble the Content-Type."""
        mock = mock_http.MockHTTP(self.mock_port)
        mock.server.wsgi_app.apps.values()[0].log.access_log.setLevel(logging.WARNING) # Shut up, Cherrypy
        media_link = self.new_entry.etree.xpath('/atom:entry/atom:link[@rel="edit-media"]', namespaces=NAMESPACES)
        media_link_url = urlparse.urlparse(get_absolute_url(media_link[0].base, media_link[0].get('href'))).path
        mock.expects('PUT', media_link_url, times=mock_http.once).will(http_code=415)
        test_xml = os.path.join(self.testfiles_dir, 'a_test.xml')
        assert_raises(EntryError, self.new_entry.update_content_from_file, test_xml)
        mock.verify()

    def test_entry_content_updated(self):
        """An Entry's content should be able to be updated."""
        updated_bytes = open(self.test_pdf_modified).read()
        mock = mock_http.MockHTTP(self.mock_port)
        mock.server.wsgi_app.apps.values()[0].log.access_log.setLevel(logging.WARNING) # Shut up, Cherrypy
        media_link = self.new_entry.etree.xpath('/atom:entry/atom:link[@rel="edit-media"]', namespaces=NAMESPACES)
        media_link_url = urlparse.urlparse(get_absolute_url(media_link[0].base, media_link[0].get('href'))).path
        mock.expects('PUT', media_link_url, times=mock_http.once).will(http_code=200)
        path = urlparse.urlparse(self.new_entry.relative_edit_link).path
        mock.expects('GET', path, times=mock_http.once).will(http_code=200, body=etree.tostring(self.new_entry.etree))
        self.new_entry.update_content_from_file(self.test_pdf_modified)

        content_tree = self.new_entry.etree.xpath('/atom:entry/atom:content', namespaces=NAMESPACES)
        content_url = urlparse.urlparse(get_absolute_url(content_tree[0].base, content_tree[0].get('src'))).path
        mock.expects('GET', content_url, times=mock_http.once).will(http_code=200, body=updated_bytes)
        content = self.new_entry.content
        current_bytes = content.read()
        assert_equal(updated_bytes, current_bytes)
        mock.verify()
    
    def test_entry_content_updated_from_readable(self):
        """An Entry's content should be able to be updated from any read()-able object."""
        updated_bytes = open(self.test_pdf_modified).read()
        mock = mock_http.MockHTTP(self.mock_port)
        mock.server.wsgi_app.apps.values()[0].log.access_log.setLevel(logging.WARNING) # Shut up, Cherrypy
        media_link = self.new_entry.etree.xpath('/atom:entry/atom:link[@rel="edit-media"]', namespaces=NAMESPACES)
        media_link_url = urlparse.urlparse(get_absolute_url(media_link[0].base, media_link[0].get('href'))).path
        mock.expects('PUT', media_link_url, times=mock_http.once).will(http_code=200)
        mock.expects('GET', urlparse.urlparse(self.new_entry.relative_edit_link).path, times=mock_http.once).will(http_code=200, body=etree.tostring(self.new_entry.etree))
        test_input = StringIO()
        test_input.write(updated_bytes)
        test_input.seek(0)
        self.new_entry.update_content_from_file(test_input,
                                                content_length=len(updated_bytes))
        content_tree = self.new_entry.etree.xpath('/atom:entry/atom:content', namespaces=NAMESPACES)
        content_url = urlparse.urlparse(get_absolute_url(content_tree[0].base, content_tree[0].get('src'))).path
        mock.expects('GET', content_url, times=mock_http.once).will(http_code=200, body=updated_bytes)
        content = self.new_entry.content
        current_bytes = content.read()
        assert_equal(updated_bytes, current_bytes)
        mock.verify()

    def test_entry_summary(self):
        """An Entry could have a summary."""
        assert(self.new_entry.summary)

    def test_entry_summary_contents(self):
        """An Entry should have the correct summary."""
        summary = 'SUMMARY_TEXT'
        assert_equal(summary, self.new_entry.summary)

    def test_entry_summary_modify(self):
        """An Entry should allow the summary to be modified."""
        new_summary = str(uuid.uuid4())
        self.new_entry.summary = new_summary
        mock = mock_http.MockHTTP(self.mock_port)
        mock.server.wsgi_app.apps.values()[0].log.access_log.setLevel(logging.WARNING) # Shut up, Cherrypy
        path = urlparse.urlparse(self.new_entry.relative_edit_link).path
        new_entry_body = helpers.fake_entry(summary=new_summary)
        mock.expects('PUT', path, times=mock_http.once).will(http_code=200)
        mock.expects('GET', path, times=mock_http.once).will(http_code=200, body=new_entry_body)
        self.new_entry.commit_updates()
        assert_equal(new_summary, self.new_entry.summary)
        mock.verify()

    def test_entry_atom_id(self):
        """An Entry should have an Atom ID."""
        assert(self.new_entry.atom_id)

    def test_entry_title(self):
        """An Entry should have a title."""
        assert(self.new_entry.title)

    def test_entry_title_contents(self):
        """An Entry should have the correct title."""
        generated_title = 'TITLE_TEXT'
        assert_equal(generated_title, self.new_entry.title)

    def test_entry_title_modify(self):
        """An Entry should allow the title to be modified."""
        new_title = str(uuid.uuid4())
        self.new_entry.title = new_title
        mock = mock_http.MockHTTP(self.mock_port)
        mock.server.wsgi_app.apps.values()[0].log.access_log.setLevel(logging.WARNING) # Shut up, Cherrypy
        path = urlparse.urlparse(self.new_entry.relative_edit_link).path
        new_entry_body = helpers.fake_entry(title=new_title)
        mock.expects('PUT', path, times=mock_http.once).will(http_code=200)
        mock.expects('GET', path, times=mock_http.once).will(http_code=200, body=new_entry_body)
        self.new_entry.commit_updates()
        assert_equal(new_title, self.new_entry.title)
        mock.verify()

    def test_entry_edited_datetime(self):
        """An Entry should have an edited date."""
        assert(self.new_entry.edited)

    def test_entry_edited_recency(self):
        """An Entry should have an edited date that is before now."""
        resolution = 30 # different clocks, sigh...
        fuzzy_now = datetime.datetime.now(pytz.utc) + datetime.timedelta(seconds=resolution)
        entry_edited = self.new_entry.edited
        assert(entry_edited < fuzzy_now)

    def test_entry_updated_datetime(self):
        """An Entry should have an updated date."""
        assert(self.new_entry.updated)

    def test_entry_updated_recency(self):
        """An Entry should have an updated date that is before now."""
        resolution = 30 # different clocks, sigh...
        fuzzy_now = datetime.datetime.now(pytz.utc) + datetime.timedelta(seconds=resolution)
        entry_updated = self.new_entry.updated
        assert(entry_updated < fuzzy_now)

    def test_entry_updated_modify(self):
        """An Entry should allow the updated date to be modified."""
        now = datetime.datetime.now(pytz.utc)
        self.new_entry.updated = now
        new_entry_body = helpers.fake_entry(updated=now)
        mock = mock_http.MockHTTP(self.mock_port)
        mock.server.wsgi_app.apps.values()[0].log.access_log.setLevel(logging.WARNING) # Shut up, Cherrypy
        path = urlparse.urlparse(self.new_entry.relative_edit_link).path
        mock.expects('PUT', path, times=mock_http.once).will(http_code=200)
        mock.expects('GET', path, times=mock_http.once).will(http_code=200, body=new_entry_body)
        self.new_entry.commit_updates()
        entry_updated = self.new_entry.updated
        forward_delta  = (now - entry_updated).seconds
        backward_delta = (entry_updated - now).seconds
        resolution = 2 
        assert(forward_delta < resolution or backward_delta < resolution)
        mock.verify()

    def test_entry_updated_modify_fail(self):
        """An Entry should not allow the updated date to be modified to an imprecise date."""
        now = datetime.datetime.now()
        try:
            self.new_entry.updated = now
            self.new_entry.commit_updates()
            assert(False)
        except TypeError:
            pass

    def test_entry_random_modify(self):
        """An Entry should allow arbitrary attributes to be modified because this is Python."""
        try:
            self.new_entry.subtitle = "There is no atom:subtitle!"
        except:    
            assert(False)

    def test_entry_modify_fails(self):
        """An Entry should not be able to be updated unless authentication is correct."""
        before_auth = self.new_entry.__dict__['_auth'] 
        self.new_entry.__dict__['_auth'] = None
        mock = mock_http.MockHTTP(self.mock_port)
        mock.server.wsgi_app.apps.values()[0].log.access_log.setLevel(logging.WARNING) # Shut up, Cherrypy
        path = urlparse.urlparse(self.new_entry.relative_edit_link).path
        mock.expects('PUT', path, times=mock_http.once).will(http_code=401)
        mock.expects('GET', path, times=mock_http.once).will(http_code=200, body=etree.tostring(self.new_entry.etree)) # After it blows up
        try:
            self.new_entry.title = "No title editing without auth!"
            self.new_entry.commit_updates()
            assert(False)
        except EntryError:
            self.new_entry.__dict__['_auth'] = before_auth
        mock.verify()

    ## Refactoring from Server
    
    def test_entry_lookup(self):
        """Entry should allow entries to be retrieved by URL."""
        mock = mock_http.MockHTTP(self.mock_port)
        mock.server.wsgi_app.apps.values()[0].log.access_log.setLevel(logging.WARNING) # Shut up, Cherrypy
        path = urlparse.urlparse(self.new_entry.relative_edit_link).path
        mock.expects('GET', path, times=mock_http.once).will(http_code=200, body=etree.tostring(self.new_entry.etree))
        entry = Entry.from_url(self.mock_url + path)
        assert(entry)
        mock.verify()
    
    def test_entry_lookup_with_custom_class(self):
        """Entry should allow entries to be retrieved by URL and instantiated using a custom class."""
        class CustomEntry(Entry):
            @property
            def foo(self):
                return "Bar"
        mock = mock_http.MockHTTP(self.mock_port)
        mock.server.wsgi_app.apps.values()[0].log.access_log.setLevel(logging.WARNING) # Shut up, Cherrypy
        path = urlparse.urlparse(self.new_entry.relative_edit_link).path
        mock.expects('GET', path, times=mock_http.once).will(http_code=200, body=etree.tostring(self.new_entry.etree))
        old_entry = CustomEntry.from_url(self.mock_url + path)
        assert(old_entry)
        assert(isinstance(old_entry, CustomEntry))
        assert_equal(old_entry.foo, 'Bar')
        mock.verify()
    
    def test_entry_lookup_root(self):
        """An Entry retrieved by URL should be an atom:entry at its root."""
        mock = mock_http.MockHTTP(self.mock_port)
        mock.server.wsgi_app.apps.values()[0].log.access_log.setLevel(logging.WARNING) # Shut up, Cherrypy
        path = urlparse.urlparse(self.new_entry.relative_edit_link).path
        mock.expects('GET', path, times=mock_http.once).will(http_code=200, body=etree.tostring(self.new_entry.etree))
        entry = Entry.from_url(self.mock_url + path)
        root = entry.etree.getroot()
        assert_equal('{%s}entry' % NAMESPACES['atom'], root.tag)
        mock.verify()

    def test_entry_lookup_fail(self):
        """Entry should not allow entries to be retrieved by incorrect URLs."""
        assert_raises(ServerError, Entry.from_url, 'not a known entry url')

    def test_server_entry_lookup_fail_2(self):
        """Entry should not allow entries to be retrieved by incorrect URLs."""
        mock = mock_http.MockHTTP(self.mock_port)
        mock.server.wsgi_app.apps.values()[0].log.access_log.setLevel(logging.WARNING) # Shut up, Cherrypy
        path = '/notfound'
        mock.expects('GET', path, times=mock_http.once).will(http_code=404)
        assert_raises(NotFoundError, Entry.from_url, self.mock_url + path)
        mock.verify()
    
    def test_entries_no_edit(self):
        """Entry should allow pure Atom (not Pub) feeds of entries to be retrieved by URL."""
        feed_length = 20

        mock = mock_http.MockHTTP(self.mock_port)
        mock.server.wsgi_app.apps.values()[0].log.access_log.setLevel(logging.WARNING) # Shut up, Cherrypy
        feed_url = self.mock_url + '/feed'
        feed = helpers.fake_atom_feed(feed_url, length=feed_length)
        mock.expects('GET', '/feed', times=mock_http.once).will(http_code=200, body=feed)
        entries = list(Entry.from_feed_url(feed_url))
        mock.verify()

        num_locations = len([e.location for e in entries])
        assert_equal(feed_length, num_locations)
        
    def test_entries_multipage(self):
        """Entry should allow paged feeds of entries to be retrieved by URL."""
        feed_length = 20

        mock = mock_http.MockHTTP(self.mock_port)
        mock.server.wsgi_app.apps.values()[0].log.access_log.setLevel(logging.WARNING) # Shut up, Cherrypy
        feed_first_url = self.mock_url + '/feed/1'
        feed_second_url = self.mock_url + '/feed/2'
        feed_third_url = self.mock_url + '/feed/3'
        feed_first_pg  = helpers.fake_atom_feed(feed_first_url,  length=feed_length, next=feed_second_url)
        feed_second_pg = helpers.fake_atom_feed(feed_second_url, length=feed_length, next=feed_third_url)
        feed_third_pg = helpers.fake_atom_feed(feed_third_url, length=feed_length)
        mock.expects('GET', '/feed/1', times=mock_http.once).will(http_code=200, body=feed_first_pg)
        mock.expects('GET', '/feed/2', times=mock_http.once).will(http_code=200, body=feed_second_pg)
        mock.expects('GET', '/feed/3', times=mock_http.once).will(http_code=200, body=feed_third_pg)
        entries = list(Entry.from_feed_url(feed_first_url))
        mock.verify()

        num_locations = len([e.location for e in entries])
        expected = 3 * feed_length
        assert_equal(expected, num_locations)
        
    def test_entries_lookup(self):
        """Entry should allow feeds of entries to be retrieved by URL."""
        feed_length = 20

        mock = mock_http.MockHTTP(self.mock_port)
        mock.server.wsgi_app.apps.values()[0].log.access_log.setLevel(logging.WARNING) # Shut up, Cherrypy
        feed_url = self.mock_url + '/feed'
        feed = helpers.fake_feed(feed_url, length=feed_length)
        mock.expects('GET', '/feed', times=mock_http.once).will(http_code=200, body=feed)
        entries = list(Entry.from_feed_url(feed_url))
        mock.verify()

        num_entries = len(entries)
        assert_equal(feed_length, num_entries)
        
    def test_entries_lookup_empty(self):
        """Entry should allow empty feeds of entries to be retrieved by URL."""
        mock = mock_http.MockHTTP(self.mock_port)
        mock.server.wsgi_app.apps.values()[0].log.access_log.setLevel(logging.WARNING) # Shut up, Cherrypy
        empty_feed_url = self.mock_url + '/emptyfeed'
        empty_feed = helpers.fake_feed(empty_feed_url, length=0)
        mock.expects('GET', '/emptyfeed', times=mock_http.once).will(http_code=200, body=empty_feed)
        entries = list(Entry.from_feed_url(empty_feed_url))
        mock.verify()
        expected = 0
        assert_equal(expected, len(entries))
        
    def test_entries_lookup_with_custom_class(self):
        """Entry should allow feeds of entries to be retrieved by URL and instantiated using a custom class."""
        class CustomEntry(Entry):
            pass
        mock = mock_http.MockHTTP(self.mock_port)
        mock.server.wsgi_app.apps.values()[0].log.access_log.setLevel(logging.WARNING) # Shut up, Cherrypy
        feed_url = self.mock_url + '/feed'
        empty_feed = helpers.fake_feed(feed_url)
        mock.expects('GET', '/feed', times=mock_http.once).will(http_code=200, body=empty_feed)
        entries = list(CustomEntry.from_feed_url(feed_url))
        mock.verify()
        assert(len(entries) > 0)
        assert(isinstance(entries[0], CustomEntry))

    def test_error_heirarchy_regression(self):
        """All Errors should be part of an AtomPiglet heirarchy."""
        # https://intranet.oreilly.com/jira/browse/ATOMPIG-5
        try:
            Entry.from_url('not a known entry url')
            raise AssertionError
        except AtomPigletError:
            pass


    def test_entry_delete_fails(self):
        """An Entry should not be able to be deleted unless authentication is correct."""
        before_auth = self.new_entry.__dict__['_auth'] 
        self.new_entry.__dict__['_auth'] = None
        mock = mock_http.MockHTTP(self.mock_port)
        mock.server.wsgi_app.apps.values()[0].log.access_log.setLevel(logging.WARNING) # Shut up, Cherrypy
        path = urlparse.urlparse(self.new_entry.relative_edit_link).path
        mock.expects('DELETE', urlparse.urlparse(self.new_entry.relative_edit_link).path, times=mock_http.once).will(http_code=401)
        assert_raises(EntryError, self.new_entry.delete)
        mock.verify()
    
    def test_entry_with(self):
        """An Entry should be able to be edited with a context manager to help commit updates."""
        new_title = str(uuid.uuid4())
        mock = mock_http.MockHTTP(self.mock_port)
        mock.server.wsgi_app.apps.values()[0].log.access_log.setLevel(logging.WARNING) # Shut up, Cherrypy
        path = urlparse.urlparse(self.new_entry.relative_edit_link).path
        new_entry_body = helpers.fake_entry(title=new_title)
        mock.expects('PUT', path, times=mock_http.once).will(http_code=200)
        mock.expects('GET', path, times=mock_http.once).will(http_code=200, body=new_entry_body)
        with self.new_entry:
            self.new_entry.title = new_title
        assert_equal(new_title, self.new_entry.title)
        mock.verify()

    def test_entry_edit_with_our_exception(self):
        """An Entry should be able to be edited with a context manager that prevents unwanted updates if exceptions are raised during editing."""
        original_title = self.new_entry.title
        new_title = str(uuid.uuid4())

        mock = mock_http.MockHTTP(self.mock_port)
        mock.server.wsgi_app.apps.values()[0].log.access_log.setLevel(logging.WARNING) # Shut up, Cherrypy
        path = urlparse.urlparse(self.new_entry.relative_edit_link).path
        mock.expects('GET', path, times=mock_http.once).will(http_code=200, body=etree.tostring(self.new_entry.etree))

        def with_exception():
            with self.new_entry:
                self.new_entry.title = new_title
                raise Exception()
        assert_raises(Exception, with_exception)
        assert_equal(self.new_entry.title, original_title)
        mock.verify()

    def test_entry_edit_with_server_blowup(self):
        """An Entry should be able to be edited with a context manager that prevents unwanted updates if exceptions are raised during editing (like the server blowing up)."""
        raise SkipTest # abruptly_disconnect is no longer supported in mock_http
        original_title = self.new_entry.title
        new_title = str(uuid.uuid4())

        mock = mock_http.MockHTTP(self.mock_port)
        mock.server.wsgi_app.apps.values()[0].log.access_log.setLevel(logging.WARNING) # Shut up, Cherrypy
        path = urlparse.urlparse(self.new_entry.relative_edit_link).path
        mock.expects('PUT', path, times=mock_http.once).will(abruptly_disconnect=True)
        mock.expects('GET', path, times=mock_http.once).will(http_code=200, body=etree.tostring(self.new_entry.etree))

        def with_exception():
            with self.new_entry:
                self.new_entry.title = new_title
        assert_raises(EntryError, with_exception)
        assert_equal(self.new_entry.title, original_title)
        mock.verify()

    def test_entry_edit_with_server_bogus(self):
        """An Entry should be able to be edited with a context manager that prevents unwanted updates if exceptions are raised during editing (like the server pretending something has gone away)."""
        original_title = self.new_entry.title
        new_title = str(uuid.uuid4())

        mock = mock_http.MockHTTP(self.mock_port)
        mock.server.wsgi_app.apps.values()[0].log.access_log.setLevel(logging.WARNING) # Shut up, Cherrypy
        path = urlparse.urlparse(self.new_entry.relative_edit_link).path
        mock.expects('PUT', path, times=mock_http.once).will(http_code=404)
        mock.expects('GET', path, times=mock_http.once).will(http_code=200, body=etree.tostring(self.new_entry.etree))

        def with_exception():
            with self.new_entry:
                self.new_entry.title = new_title
        assert_raises(EntryError, with_exception)
        assert_equal(self.new_entry.title, original_title)
        mock.verify()

    def test_entry_str(self):
        """An Entry should have a pretty representation for users."""
        assert('Atom' in str(self.new_entry))
        
    def test_entry_repr(self):
        """An Entry should have a representation for developers."""
        assert('http' in repr(self.new_entry))
        
    def teardown(self):
        no_clean = False
        if no_clean:
            for file in self.to_clean:
                print "Not deleting file %s" % file
            for d in self.to_delete:
                print "Not deleting entry at %s" % d.location
        else:
            for d in self.to_delete:
                try:
                    d.delete()
                except Exception, e:    
                    print "Warning: %s could not be deleted (%s)!" % (d.location, e)

            for file in self.to_clean:
                try:
                    os.remove(file)
                except Exception, e:
                    print "Couldn't remove %s during cleanup (%s)" % (file, e)

            shutil.rmtree(self.tempdir)

