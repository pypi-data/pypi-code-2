#!/usr/bin/env python
# encoding: utf-8
"""
kurt.py

Created by Keith Fahlgren on Fri Jan 30 19:34:49 PST 2009
Copyright (c) 2009 O'Reilly Media. All rights reserved.
"""
import logging
import os
import re
import tempfile
import urllib

from lxml import etree

from atompiglet import NAMESPACES
from atompiglet.server import Server
from atompiglet.entry import Entry

log = logging.getLogger(__name__)

NAMESPACES.update(
    { 'kurt':  'http://atom.oreilly.com/kurt/1', }
)

KURT  = 'http://atom.oreilly.com/atom'
TEST_KURT  = 'http://dcwtest.west.ora.com/atom'
META  = 'http://meta.oreilly.com/atom'
TEST_META  = 'http://dmwtest.west.ora.com/atom'
GYPSY = 'http://mediaservice.oreilly.com/gypsy/atom/service'
TEST_GYPSY = 'http://mediaman.vz.west.ora.com/gypsy/atom/service'


class Book:
    """Tools for transforming, dumping, and regularizing Kurt's Book entries."""

    WEB_IMAGE_CONTENT_TYPES = [
        'image/bmp',
        'image/gif',
        'image/jpeg',
        'image/png',
        'image/tiff',
    ]

    PRINT_IMAGE_CONTENT_TYPES = [
        'application/pdf',
        'application/postscript',
        'image/gif',
    ]

    BOOKFILENAME = "book.xml"
    REMOVE_KURT_IDS = """
<xsl:stylesheet version="1.0" 
                xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
                xmlns:kurt="%s">
  <xsl:template match="@*|node()">
    <xsl:copy>
      <xsl:apply-templates select="@*|node()"/>
    </xsl:copy>
  </xsl:template>
  <xsl:template match="@kurt:id">
    <!-- Drop it -->
  </xsl:template>
</xsl:stylesheet>""" % NAMESPACES['kurt']
    def __init__(self, entry, server):
        self.entry = entry
        self.server = server
        self.docbook = DocBook(self.entry.content)

    def dump_book(self, dumpdir=None, figs_subdir=None, allowed_image_content_types=[]):
        """Dump the DocBook content and all referenced images to the filesystem. Scrub all the Kurt-specific decorations
        in the process."""
        if not(dumpdir):
            dumpdir = tempfile.mkdtemp('kurt_books_dumping_tmp') #FIXME
        if figs_subdir:
            sd = os.path.join(dumpdir, figs_subdir)
            os.mkdir(sd)

        self.remove_kurt_ids()
        image_map = self._dump_images(dumpdir, allowed_image_content_types, figs_subdir=figs_subdir)
        self._rewrite_filerefs(image_map)

        bookfile = os.path.join(dumpdir, self.BOOKFILENAME)
        log.debug("Dumping DocBook file from %s as %s" % (self.entry.atom_id, bookfile))
        f = open(bookfile, "w")
        self.docbook.etree.write(f)
        f.close()
        return (bookfile, dumpdir)

    def remove_kurt_ids(self):
        """Remove all kurt:ids from the associated DocBook from Kurt. Returns False if the transformation fails. """
        xslt_transformer = etree.XSLT(etree.fromstring(self.REMOVE_KURT_IDS))
        try:
            result = xslt_transformer(self.docbook.etree)
            self.docbook.etree = result
            return True
        except etree.XSLTError: #FIXME
            return False

    def _rewrite_filerefs(self, image_map):
        for atom_id, filename in image_map.iteritems():
            basename = os.path.basename(filename)
            referencing_elements = self.docbook.etree.xpath('//*[@fileref="%s"]' % atom_id)
            for element in referencing_elements:
                element.set('fileref', basename)

    def _dump_images(self, dumpdir, allowed_image_content_types, figs_subdir=None):
        image_stub_map = self._map_image_atom_ids_to_filestubs()
        image_filename_map = {}
        for atom_id, filestub in image_stub_map.iteritems():
            image_entry = Utils.entry_from_atom_id(self.server, atom_id)
            content_type = image_entry.content_type
            if allowed_image_content_types and content_type not in allowed_image_content_types:
                log.debug("Skipping image file %s with content-type %s" % (atom_id, content_type))
                continue
            filename = self._choose_filename(content_type, filestub, dumpdir, figs_subdir)
            image_filename_map[atom_id] = filename
            log.debug("Dumping image file from %s to %s" % (atom_id, filename))
            image_entry.dump_content_to_file(filename)
        return image_filename_map

    def _choose_filename(self, content_type, filestub, dir, figs_subdir):
        filename = None
        if content_type == 'image/png':
            filename = filestub + '.png'
        elif content_type == 'image/jpeg':
            filename = filestub + '.jpg'
        elif content_type == 'application/postscript':
            filename = filestub + '.ps' #TESTME
        elif content_type == 'image/bmp':
            filename = filestub + '.bmp'
        elif content_type == 'image/gif':
            filename = filestub + '.gif'
        elif content_type == 'image/tiff':
            filename = filestub + '.tiff'
        elif content_type == 'application/pdf':
            filename = filestub + '.pdf'
        elif content_type == 'application/xml': #TESTME
            filename = filestub + '.xml'
        else:
            raise NotImplementedError("File extention not known for content/@type %s!" % content_type) #TESTME

        if figs_subdir:
            return os.path.join(dir, figs_subdir, filename)
        else:
            return os.path.join(dir, filename)

    def _map_image_atom_ids_to_filestubs(self):
        non_words = re.compile('\W')
        fileref_atom_ids = self.docbook.filerefs
        map = dict([(atom_id, non_words.sub('', atom_id)) for atom_id in fileref_atom_ids])
        return map


# =============================================================================

class DocBook:
    """Tools for interacting with DocBook content."""
    def __init__(self, file_or_tree):
        try:
            if file_or_tree.getroot:
                # It's a tree, how nice
                self.__dict__['etree'] = file_or_tree
        except AttributeError:
            parser = etree.XMLParser(dtd_validation=True)
            try:
                self.__dict__['etree'] = etree.parse(file_or_tree, parser)
            except etree.XMLSyntaxError, e:
                # No DOCTYPE, bummer! Rewind, hoping it is a file and not just a
                # string and retry
                try:
                    file_or_tree.seek(0)
                except AttributeError:
                    pass
                self.__dict__['etree'] = etree.parse(file_or_tree)

    def __getattr__(self, attr):
        if attr == 'filerefs':
            return self._get_filerefs()
        else:    
            raise AttributeError, attr

    def _get_filerefs(self):
        filerefs = self.etree.xpath("//@fileref")
        return filerefs 

# =============================================================================

class Utils:
    """Utilities provided to interface with server-specific functionality and features that exist on
    the AtomPub server 'Kurt'."""

    @staticmethod
    def entry_from_atom_id(server, atom_id):
        """Given an Kurt Server object and a Atom ID, return the matching entry. Throws a ServerError if the entry cannot be found."""
        base_url = server.endpoint_url
        query_param = 'q'
        query = {query_param : str(atom_id)}
        full_url = base_url + '?' + urllib.urlencode(query)
        return Entry.from_url(str(full_url))
