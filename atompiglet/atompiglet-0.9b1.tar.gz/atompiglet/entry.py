#!/usr/bin/env python
# encoding: utf-8
"""
entry.py

Created by Keith Fahlgren on Mon Jan 19 05:29:03 PST 2009
Copyright (c) 2009 O'Reilly Media. All rights reserved.
"""

import tempfile

import datetime

from lxml import etree

import friendly_curl
import httplib2

from atompiglet import ATOM_ENTRY_CONTENT_TYPE, NAMESPACES, get_absolute_url
from atompiglet.xmlutil import XPathProperty, XPathValueProperty, XPathAttributeProperty
from atompiglet.errors import AtomPigletError, ServerError, NotFoundError, EntryError, EntryEditError

import logging

log = logging.getLogger(__name__)


class Entry(object):
    """A class that encapsulates the behavior of an AtomPub entry"""
    def __init__(self, source, tree, auth=None, etag=None, server=None):
        """Create a new Entry object from the given location and an
        ElementTree node."""
        self.etree = tree
        self.etag = etag
        tagname = tree.getroot().tag 
        if tagname != '{%s}entry' % NAMESPACES['atom']:
            raise EntryError, "Supplied XML for atom:entry is actually a %s!" % tagname
        self._auth = auth
        self.init_location = source
    
    def __str__(self):
        return "Atom Entry @ %s" % self.init_location
    
    def __repr__(self):
        return "<%s.%s instance with location: %r>" % (self.__class__.__module__, self.__class__.__name__, self.location)
    
    def dump_content_to_file(self, dumpfilename):
        """Dump the simple content of this entry into a single file at the filename provided."""
        f = open(dumpfilename, 'wb')
        bytes = self.content
        if hasattr(bytes, 'getroot'):
            bytes.write(f)
        else:
            # TODO: Consider body_buffer kwarg to FCurl get_url
            f.write(bytes.read())
        f.close()
    
    def update_content_from_file(self, readable_or_filename, content_length=None):
        """Given a file, update the content of this Entry with its contents."""
        headers = self._auth.headers() if self._auth else {}
        if self.etag:
            headers['If-Match'] = self.etag
        media_link = self.etree.xpath('/atom:entry/atom:link[@rel="edit-media"]', namespaces=NAMESPACES)
        if not(hasattr(readable_or_filename, 'read')):
            readable_or_filename = open(readable_or_filename, mode='rb')
        if len(media_link) == 1:
            media_link_url = get_absolute_url(media_link[0].base, media_link[0].get('href'))
            resp, body = friendly_curl.threadCURLSingleton().put_url(str(media_link_url), 
                                                                     content_type=self.content_type,
                                                                     headers=headers,
                                                                     upload_file=readable_or_filename,
                                                                     upload_file_length=content_length,
                                                                    )
            if resp['status'] == 412:
                raise EntryEditError("Entry at %s could not be updated because of mis-matching entity tags. Please update your copy and retry (%s)!" % (self.location, resp['status']))
            elif resp['status'] == 200:
                if 'etag' in resp:
                    self.etag = resp['etag']
                self._refresh_entry_representation()
                return True
            else:
                raise EntryError("Error updating entry at %s with file %s (%s)!" % (self.location, readable_or_filename, resp['status']))
        else:
            raise NotImplemented("Editing inline content has not been implemented (yet)!")

    def commit_updates(self, debug=False):
        """Commit any in-memory changes to the XML of this entry. 
           Throws EntryError on problems with update."""
        headers = self._auth.headers() if self._auth else {}
        if self.etag:
            headers['If-Match'] = self.etag
        data = etree.tostring(self.etree)
        try:
            resp, _ = friendly_curl.threadCURLSingleton().put_url(self.location, 
                                                                  content_type=ATOM_ENTRY_CONTENT_TYPE, 
                                                                  data=data, 
                                                                  debug=debug,
                                                                  headers=headers, 
                                                                 ) 
        except friendly_curl.friendly_curl.PyCURLError, e:
            self._refresh_entry_representation()
            raise EntryError("Entry at %s could not be updated (%s)!" % (self.location, e)) 
        if resp['status'] == 412:
            self._refresh_entry_representation()
            raise EntryEditError("Entry at %s could not be updated because of mis-matching entity tags. Please update your copy and retry (%s)!" % (self.location, resp['status']))
        elif resp['status'] != 200:
            self._refresh_entry_representation()
            raise EntryError("Entry at %s could not be updated (%s)!" % (self.location, resp['status']))
        else:
            if 'etag' in resp:
                self.etag = resp['etag'] #TESTME
            self._refresh_entry_representation()
            return True
    
    def delete(self):
        """Delete this Entry entirely. No Entity Tag matching is done."""
        headers = self._auth.headers() if self._auth else {}
        resp, _ = friendly_curl.threadCURLSingleton().delete_url(self.location, headers=headers)
        if resp['status'] == 200:
            return True
        else:
            raise EntryError, "Entry at %s could not be deleted (%s)!" % (self.location, resp['status'])

    def _refresh_entry_representation(self, force=False):
        headers = self._auth.headers() if self._auth else {}
        if self.etag and not(force):
            headers['if-none-match'] = self.etag
        try:
            resp, body = friendly_curl.threadCURLSingleton().get_url(self.location, headers=headers)
            if 'etag' in resp:
                self.etag = resp['etag']
        except Exception, e:
            raise EntryError("Entry could not be retreived from server at url %s (%s)!" % (self.location, e))

        if resp['status'] == 304: # Not Modified, nothing to see or do in this branch here
            return True
        elif resp['status'] != 200:
            raise EntryError("Entry could not be retreived from server at url %s (%s)!" % (self.location, resp['status'])) #TESTME
        else:
            atom_entry = etree.parse(body, base_url=self.location)
            self.__dict__['etree'] = atom_entry
            return True

    author_name = XPathValueProperty(xpath='/atom:entry/atom:author/atom:name',
                                     namespaces=NAMESPACES, read_only=True)
    
    author_uri =  XPathValueProperty(xpath='/atom:entry/atom:author/atom:uri',
                                     namespaces=NAMESPACES, read_only=True)
    
    content_type = XPathAttributeProperty(xpath='/atom:entry/atom:content',
                                          attribute='type', namespaces=NAMESPACES,
                                          read_only=True)
    
    edit_link = XPathProperty(xpath='/atom:entry/atom:link[@rel="edit"]',
                              namespaces=NAMESPACES,)
    
    relative_edit_link = XPathAttributeProperty(
        xpath='/atom:entry/atom:link[@rel="edit"]', attribute='href',
        namespaces=NAMESPACES, read_only=True)
    
    @property
    def location(self):
        try:
            edit_link = self.edit_link
            return httplib2.iri2uri(get_absolute_url(edit_link.base, edit_link.get('href'))).encode('utf-8')
        except AttributeError:
            return None
    
    edited = XPathValueProperty(xpath='/atom:entry/app:edited', namespaces=NAMESPACES,
                                datatype='xsd:dateTime', read_only=True)
    
    atom_id = XPathValueProperty(xpath='/atom:entry/atom:id', namespaces=NAMESPACES,
                                 read_only=True)
    
    title = XPathValueProperty(xpath='/atom:entry/atom:title',
                               namespaces=NAMESPACES)
    
    _summary = XPathProperty(xpath='/atom:entry/atom:summary', namespaces=NAMESPACES)
    
    def summary():
        def fget(self):
            summary_node = self._summary
            if summary_node.attrib['type'] == 'xhtml':
                return etree.tostring(summary_node[0])
            else:
                return summary_node.text
        
        def fset(self, value):
            summary_node = self._summary
            for child in summary_node:
                summary_node.remove(child)
            summary_node.text = ''
            try:
                xhtml = etree.fromstring(value)
                if xhtml.tag != '{http://www.w3.org/1999/xhtml}div':
                    raise Exception()
            except:
                if '<' in value:
                    # HTML
                    summary_node.attrib['type'] = 'html'
                else:
                    # Text
                    summary_node.attrib['type'] = 'text'
                summary_node.text = value
            else:
                # XHTML
                summary_node.append(xhtml)
                summary_node.attrib['type'] = 'xhtml'
        
        return locals()
    
    summary = property(**summary())
    
    updated = XPathValueProperty(xpath='/atom:entry/atom:updated',
                                 namespaces=NAMESPACES, datatype='xsd:dateTime')
    
    published = XPathValueProperty(xpath='/atom:entry/atom:published',
                                   namespaces=NAMESPACES, datatype='xsd:dateTime')
    
    def __enter__(self):
        """Allow Entry to be used as a context manager for auto-transactions.
        
        Ex:
        with atom_entry:
            # Do stuff
        # Changes are committed unless an exception happened."""
        return self
    
    def __exit__(self, type, value, tb):
        """On exit from a with block, commit if no exception happened."""
        if tb is None:
            self.commit_updates()
        else:
            self._refresh_entry_representation()

    
    @property
    def content(self):
        content_tree = self.etree.xpath('/atom:entry/atom:content', namespaces=NAMESPACES)[0]
        if ('src' in content_tree.attrib):
            content_url = get_absolute_url(content_tree.base, content_tree.get('src')).encode('utf-8')
            headers = self._auth.headers() if self._auth else {}
            #body_buffer = tempfile.NamedTemporaryFile(mode='rw+b')
            try:
                resp, body = friendly_curl.threadCURLSingleton().get_url(content_url, headers=headers)#, body_buffer=body_buffer)
            except friendly_curl.friendly_curl.PyCURLError, e: #TESTME
                raise EntryError("Content could not be retreived from Entry at %s with content location %s (%s)!" % (self.location, content_url, e))
            if resp['status'] != 200:
                raise EntryError("Content could not be retreived from Entry at %s with content location %s (%s)!" % (self.location, content_url ,resp['status'])) #TESTME
            return body
        else:
            return content_tree
    
    @classmethod
    def from_url(cls, url, auth_source=None):
        """Return the Entry at the url provided."""
        auth = None
        if auth_source:
            if not hasattr(auth_source, '_auth'):
                raise AtomPigletError("No _auth found on auth_source") 
            else:
                auth = auth_source._auth
        headers = auth.headers() if auth else None
        try:
            resp, body = friendly_curl.threadCURLSingleton().get_url(url, headers=headers)
        except Exception, e:
            raise ServerError("Entry could not be retreived from server at url %s (%s)!" % (url, e))
        if resp['status'] != 200:
            raise NotFoundError("Entry could not be retreived from server at url %s (%s)!" % (url, resp['status']))
        atom_entry = etree.parse(body, base_url=url)
        etag = None
        if 'etag' in resp:
            etag = resp['etag']
        existing_entry = cls(url, atom_entry, auth=auth, etag=etag)
        return existing_entry
    
    @classmethod
    def from_feed_url(cls, url, auth_source=None):
        """Returns all Entries from the feed URL provided.
        
        Provides the Entries through a generator. This will traverse all pages
        of the feed until it reaches the end, but only on-demand."""
        auth = None
        if auth_source:
            if not hasattr(auth_source, '_auth'):
                raise AtomPigletError("No _auth found on auth_source")
            else:
                auth = auth_source._auth
        headers = auth.headers() if auth else None
        try:
            resp, body = friendly_curl.threadCURLSingleton().get_url(url, headers=headers)
            current_location = url
        except Exception, e:
            raise ServerError("Feed could not be retreived from server at url %s (%s)!" % (url, e)) #TESTME
        if resp['status'] != 200:
            raise ServerError("Feed could not be retreived from server at url %s (%s)!" % (url, resp['status'])) #TESTME
        atom_feed = etree.parse(body, base_url=current_location)
        while True:
            if len(atom_feed.xpath('/atom:feed/atom:entry', namespaces=NAMESPACES)) == 0:
                break
            for entry in atom_feed.xpath('/atom:feed/atom:entry', namespaces=NAMESPACES):
                atom_entry = etree.ElementTree(entry)
                yield cls(current_location, atom_entry, auth=auth)
            next_link = atom_feed.xpath('/atom:feed/atom:link[@rel="next"]', namespaces=NAMESPACES)
            if next_link:
                next_link = get_absolute_url(next_link[0].base, next_link[0].attrib['href'])
                log.debug("Follwing atom:link[@rel='next']: %s" % next_link)
                try:
                    resp, body = friendly_curl.threadCURLSingleton().get_url(next_link, headers=headers)
                    current_location = next_link
                except Exception, e: #TESTME
                    raise ServerError("Feed could not be retreived from server at url %s (%s)!" % (next_link, e))
        
                if resp['status'] != 200:
                    raise ServerError("Feed could not be retreived from server at url %s (%s)!" % (next_link, resp['status'])) #TESTME
                atom_feed = etree.parse(body, base_url=current_location)
            else:
                break
            
