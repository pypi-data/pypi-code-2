#!/usr/bin/env python
#  -*- mode: python; indent-tabs-mode: nil; -*- coding: utf-8 -*-

"""

RSTParser.py

Copyright 2010 by Marcello Perathoner

Distributable under the GNU General Public License Version 3 or newer.

"""

import datetime
import re
import collections
import urlparse

import lxml.html
from lxml import etree
import docutils.core

from pkg_resources import resource_string # pylint: disable=E0611

from epubmaker.lib.GutenbergGlobals import NS, xpath
from epubmaker.lib.Logger import info, debug, warn, error
from epubmaker.lib.MediaTypes import mediatypes as mt
from epubmaker.lib.DublinCore import DublinCore

from epubmaker.parsers import HTMLParser

from epubmaker.mydocutils.parsers import GutenbergRSTParser
from epubmaker.mydocutils.writers import GutenbergNroffWriter, GutenbergHTMLWriter, XetexWriter

mediatypes = (mt.rst, )

RE_EMACS_CHARSET = re.compile (r'-\*-.*coding:\s*(\S+)',  re.I)

class Meta (collections.defaultdict):
    """ Parse RST meta section. """
    
    # .. meta::
    #    :PG.id: 181
    re_meta_section_start = re.compile (r'^\.\.\s+meta::')
    re_meta_entry = re.compile (r'^\s+:([^:]+):\s*(.*)$')

    def __init__ (self, rst):
        """ Get meta section of rst. """

        # pylint: disable=E1002
        super (Meta, self).__init__ (list)
        in_meta = False
        for line in rst.splitlines ():
            if self.re_meta_section_start.match (line):
                in_meta = True
                continue
            if in_meta:
                m = self.re_meta_entry.match (line)
                if not m:
                    break
                super (Meta, self).__getitem__ (m.group (1)).append (m.group (2))

    def getone (self, what, default = None):
        """ Get non-repeatable field value. """
        if what in self:
            return self[what][0]
        return default

    def strunk (self, what):
        """ Get concatenated repeatable field value. """
        return DublinCore.strunk (self[what])


class Parser (HTMLParser.Parser):
    """ Parse a ReStructured Text 

    and convert it to xhtml suitable for ePub packaging.

    """

    def preprocess (self, charset):
        """ Insert pg header and footer. """
        
        rst = self.unicode_content ()

        meta = Meta (rst)
        
        # see if this is a PG text
        pgid = meta.getone ('PG.Id', 0)
        if pgid:
            # insert pg header below book title
            header, footer = self.get_pg_headers (meta, charset)
            rst = self.re_header_insert_point.sub (header, rst)
            # insert pg footer at end of text
            rst = self.re_footer_insert_point.sub (footer, rst)

        return rst

        
    def rst2nroff (self, charset = 'utf-8'):
        """ Convert RST to nroff. """

        rst = self.preprocess (charset)
        
        overrides = {
            'doctitle_xform': 1,
            'sectsubtitle_xform': 1,
            'footnote_references': 'superscript',
            'compact_lists': 1,
            'compact_simple': 1,
            'page_numbers': 1,
            'encoding': charset,
            }
   
        parts = docutils.core.publish_parts (
            source = rst,
            source_path = self.options.candidate.filename,
            parser = GutenbergRSTParser.Parser (),
            writer = GutenbergNroffWriter.Writer (),
            settings_overrides = overrides)

        return parts['whole']


    def rst2xetex (self):
        """ Convert RST to xetex. """

        rst = self.preprocess ('utf-8')
        
        overrides = {
            'doctitle_xform': 1,
            'sectsubtitle_xform': 1,
            'footnote_references': 'superscript',
            'compact_lists': 1,
            'compact_simple': 1,
            'page_numbers': 1,
            'encoding': 'utf-8',
            }
   
        parts = docutils.core.publish_parts (
            source = rst,
            source_path = self.options.candidate.filename,
            parser = GutenbergRSTParser.Parser (),
            writer = XetexWriter.Writer (),
            settings_overrides = overrides)

        return parts['whole']


    def rst2html (self):
        """ Convert RST input to HTML output. """
        
        rst = self.preprocess ('utf-8')
        
        overrides = {
            'stylesheet': None,
            'stylesheet_path': None,
            'doctitle_xform': 1,
            'initial_header_level': 2,
            'sectsubtitle_xform': 1,
            'footnote_references': 'superscript',
            'page_numbers': 1,
            'encoding': 'utf-8',
            }

        parts = docutils.core.publish_parts (
            source = rst,
            source_path = self.options.candidate.filename,
            parser = GutenbergRSTParser.Parser (),
            writer = GutenbergHTMLWriter.Writer (),
            settings_overrides = overrides)

        html = parts['whole']
        html = html.replace ('&nbsp;', u' ')
        html = html.replace ('&mdash;', u'—')
        return html


    def get_charset_from_rstheader (self):
        """ Parse text for hints about charset. """
        # .. -*- coding: utf-8 -*-
        
        charset = None
        rst = self.bytes_content ()
        
        match = RE_EMACS_CHARSET.search (rst)
        if (match):
            charset = match.group (1)
            info ('Got charset %s from emacs comment' % charset)

        return charset


    def fix_coverpage (self):
        """ Move <meta name='coverpage'> to <link rel='coverpage'>

        <meta> is much easier to set in RST, but <link> is the correct semantic.

        """
        
        for head in xpath (self.xhtml, "/xhtml:html/xhtml:head"):
            for meta in xpath (head, "xhtml:meta[@name = 'coverpage']"):
                url = meta.get ('content')
                meta.drop_tag ()
                link = etree.Element (NS.xhtml.link, rel = 'coverpage', href = url)
                link.tail = '\n'
                head.append (link)
            

    re_whole_header = re.compile (r'<header>\s*(.*)</header>', re.DOTALL)
    re_whole_footer = re.compile (r'<footer>\s*(.*)</footer>', re.DOTALL)
    re_copyrighted  = re.compile (r'<copyrighted>\s*(.*?)</copyrighted>', re.DOTALL)
    re_header_insert_point = re.compile (r'^..\s+pgheader::\s*$', re.MULTILINE | re.DOTALL)
    re_footer_insert_point = re.compile (r'^..\s+pgfooter::\s*$', re.MULTILINE | re.DOTALL)

 
    def get_pg_headers (self, meta, encoding):
        """ Parse PG header and footer out of the license file. """
        
        lic = resource_string ('epubmaker.parsers', 'pg-license.rst')
        lic = lic.decode ('utf-8')
        
        title = meta.getone ('PG.Title') or meta.getone ('DC.Title')
        title = title.partition ('\n')[0] 

        release_date = datetime.datetime.strptime (
            meta.getone ('PG.Released'), '%Y-%m-%d').date ()

        language = meta.get ('DC.Language', ['en'])
        language = map (lambda x: DublinCore.language_map.get (
            x, 'Unknown').title (), language)
        language = DublinCore.strunk (language)

        producers = meta.get ('PG.Producer', '')
        if producers:
            producers = 'Produced by %s.' % DublinCore.strunk (producers)

        credits_ = meta.getone ('PG.Credits', '')

        lic = lic.replace ('<bibrec>', urlparse.urljoin (
            options.config.BIBREC, meta.getone ('PG.Id', 0)))

        lic = lic.replace ('<pg-top-line>',
                           'The Project Gutenberg EBook of %s' % title)
        lic = lic.replace ('<pg-produced-by>', producers)
        lic = lic.replace ('<pg-credits>', credits_)
        lic = lic.replace (
            '<pg-start-line>',
            '\*\*\* START OF THIS PROJECT GUTENBERG EBOOK %s \*\*\*' % title.upper ())
        lic = lic.replace (
            '<pg-end-line>',
            '\*\*\* END OF THIS PROJECT GUTENBERG EBOOK %s \*\*\*' % title.upper ())

        # keep those 6 leading spaces !!!
        lic = lic.replace ('<pg-machine-header>', u"""Title: {title}
      
      Author: {authors}
      
      Release Date: {date} [EBook #{pgid}]
      
      Language: {language}
      
      Character set encoding: {encoding}""".format (
                        title    = meta.getone ('DC.Title'),
                        authors  = DublinCore.strunk (meta['DC.Creator']),
                        date     = datetime.datetime.strftime (release_date, '%B %d, %Y'),
                        pgid     = meta.getone ('PG.Id'),
                        language = language,
                        encoding = encoding.upper ()))

        if meta.getone ('PG.Rights').lower () == 'copyrighted':
            lic = self.re_copyrighted.sub ('\1', lic)
        else:
            lic = self.re_copyrighted.sub ('', lic)

        f = self.re_whole_footer.search (lic)
        h = self.re_whole_header.search (lic)

        return h and h.group (1) or '', f and f.group (1) or ''
            

    def parse (self):
        """ Parse a RST file to xhtml. """

        # cache
        if self.xhtml is not None:
            return

        html = self.rst2html ()

        # remove doctype, we will add the correct one before serializing
        html = re.compile ('^.*<html ', re.I | re.S).sub ('<html ', html) 

        try:
            self.xhtml = etree.fromstring (
                html, 
                lxml.html.XHTMLParser (), # encoding = 'unicode'), # FIXME: ???
                base_url = self.url)                                           
        except etree.ParseError, what:
            error ("etree.fromstring says %s" % what)
            raise
        
        self._fix_anchors ()  # needs relative paths
        self.fix_coverpage () # must run before make_links_absolute

        self.xhtml.make_links_absolute (base_url = self.url)

        self._to_xhtml11 ()

        debug ("Done parsing %s" % self.url)
