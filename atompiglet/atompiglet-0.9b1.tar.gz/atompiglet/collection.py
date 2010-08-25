#!/usr/bin/env python
# encoding: utf-8
"""
collection.py

Created by Keith Fahlgren on Sun Jan 18 06:51:25 PST 2009
Copyright (c) 2009 O'Reilly Media. All rights reserved.
"""

import os
import logging
from cStringIO import StringIO

from lxml import etree

import friendly_curl

from atompiglet import NAMESPACES, get_absolute_url
from atompiglet.errors import AtomPigletError
from atompiglet.entry import Entry



log = logging.getLogger(__name__)

def atom_tag(name, parent=None, body_text=None, attrib={}):
    if parent is not None:
        elem = etree.SubElement(parent, '{http://www.w3.org/2005/Atom}%s' % name,
                                attrib=attrib,
                                nsmap={None: 'http://www.w3.org/2005/Atom'})
    else:
        elem = etree.Element('{http://www.w3.org/2005/Atom}%s' % name,
                             attrib=attrib,
                             nsmap={None: 'http://www.w3.org/2005/Atom'})
    if body_text:
        elem.text = body_text
    return elem

class CollectionAdditionError(AtomPigletError):
    """Errors raised while trying to add an entry to an app:collection."""
    pass

class Collection:
    """Encapsulates the behavior of an AtomPub collection."""
    
    def __init__(self, title, node, auth=None, server=None):
        self.title = title
        self._node = node
        self._auth = auth
        self._server = server

        self.etree = self._node
        self.location = self._resolve_location()
        
    def __repr__(self):
        return "<%s.%s instance with location: %r>" % (self.__class__.__module__, self.__class__.__name__, self.location)

    def add_from_file(self, readable_or_filename, content_type,
                      content_length=None, slug=None, debug=False):
        """Add a Media Resource to the Collection from the provided file.
        
        :param readable_or_filename: A ``read()``-able object or a filename that\
        can be ``open()``'d, to use as the content of the entry.
        :param content_type: The IANA media type of the content from\
        ``readable_or_filename``.
        :param content_length: The length of the content from
        ``readable_or_filename``. Required if that parameter is not something
        that can be ``fstat()``'d.
        :param slug: The Slug to use when POST-ing the entry.
        :param debug: Use FriendlyCURL in debug mode.
        :returns: The :class:`atompiglet.entry.Entry` created.
        :raises CollectionAdditionError: if something goes wrong
        """
        if not(hasattr(readable_or_filename, 'read')):
            readable_or_filename = open(readable_or_filename, 'rb')
        headers = self._auth.headers() if self._auth else {}
        if slug is not None:
            headers['Slug'] = slug
        log.debug("POSTing to %s" % self.location)
        resp, body = friendly_curl.threadCURLSingleton().post_url(
            str(self.location), headers=headers, upload_file=readable_or_filename,
            upload_file_length=content_length, content_type=content_type,
            debug=debug)
        if resp['status'] != 201:
            err = CollectionAdditionError("Error uploading file %s to app:collection at %s (%s)!" % (readable_or_filename, self.location, resp['status']))
            err.body = body
            err.resp = resp
            raise err

        location = resp['location'] # MUST have a Location header
        content_location = resp['content-location'] if 'content-location' in resp else None # MAY have a Content-Location header
        etag = resp['etag'] if 'etag' in resp else None
        if location == content_location:
            # The body return is a real representation of the entry if the two headers match
            atom_entry = etree.parse(body, base_url=location)
            new_entry = Entry(location, atom_entry, auth=self._auth, etag=etag, server=self._server)
            return new_entry
        else:    
            # Just do it the hard way
            new_entry = Entry.from_url(location, auth_source=self)
            return new_entry
    
    def add_entry(self, content, title, content_type='text', slug=None, debug=False):
        """Add an Entry Resource to the Collection.
        
        :param content: The content of the atom:entry. May be a string or, if\
        `content_type` is xhtml, an etree.
        :param title: The title of the atom entry.
        :param content_type: text, html, or xhtml - the type of content in the\
        entry.
        :param slug: The Slug to use when creating the entry.
        :returns: The :class:`atompiglet.entry.Entry` created.
        :raises CollectionAdditionError: if something goes wrong
        """
        entry = atom_tag('entry')
        et = etree.ElementTree(entry)
        atom_tag(parent=entry, name='title', body_text=title, attrib={'type': 'text'})
        if content_type == 'text' or content_type == 'html':
            atom_tag(parent=entry, name='content', body_text=content, attrib={'type': content_type})
        elif content_type == 'xhtml':
            content_element = atom_tag(parent=entry, name='content',
                                       attrib={'type': content_type})
            content_element.append(content.getroot())
        entry_buffer = StringIO()
        et.write(entry_buffer)
        entry_buffer.seek(0)
        headers = self._auth.headers() if self._auth else {}
        if slug is not None:
            headers['Slug'] = slug
        resp, body = friendly_curl.threadCURLSingleton().post_url(
            str(self.location), headers=headers, upload_file=entry_buffer,
            upload_file_length=len(entry_buffer.getvalue()),
            content_type='application/atom+xml; type=entry', debug=debug)
        if resp['status'] != 201:
            raise CollectionAdditionError(
                "Error uploading content %s to app:collection at %s (%s)!" %\
                (content, self.location, resp['status']))

        location = resp['location'] # MUST have a Location header
        content_location = resp['content-location'] if 'content-location' in resp else None # MAY have a Content-Location header
        etag = resp['etag'] if 'etag' in resp else None
        if location == content_location:
            # The body return is a real representation of the entry if the two headers match
            atom_entry = etree.parse(body, base_url=location)
            new_entry = Entry(location, atom_entry, auth=self._auth, etag=etag, server=self._server)
            return new_entry
        else:    
            # Just do it the hard way
            new_entry = Entry.from_url(location, auth_source=self)
            return new_entry
    
    def entries(self, entry_cls=Entry):
        """Fetch the entries in this collection.
        
        :returns: A generator of entries in this collection.
        :rtype: :class:`atompiglet.entry.Entry`
        """
        return entry_cls.from_feed_url(self.location, auth_source=self)
    
    def _resolve_location(self):
        href = self._node.get('href')
        return get_absolute_url(self._node.base, href)
