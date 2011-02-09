#!/usr/bin/env python
#  -*- mode: python; indent-tabs-mode: nil; -*- coding: iso-8859-1 -*-

"""

EpubMaker.py

Copyright 2009-2011 by Marcello Perathoner

Distributable under the GNU General Public License Version 3 or newer.

Stand-alone application to build epub out of html or rst.

"""

from __future__ import with_statement

import sys
import os.path
import re
import optparse
import hashlib
import mimetypes

from epubmaker.lib.GutenbergGlobals import Struct, DCIMT, SkipOutputFormat
import epubmaker.lib.GutenbergGlobals as gg
from epubmaker.lib.Logger import debug, exception
from epubmaker.lib import Logger, DublinCore

from epubmaker import Spider
from epubmaker import ParserFactory
from epubmaker import WriterFactory
from epubmaker.packagers import PackagerFactory
from epubmaker import CommonOptions
from epubmaker import Version

def null_translation (s):
    """ Translate into same language. :-) """
    return s

TXT_FORMATS    = 'txt.utf-8 txt.iso-8859-1 txt.us-ascii'.split ()
EPUB_FORMATS   = 'epub.noimages epub.images'.split ()
OUTPUT_FORMATS = 'html pdf rst'.split () + EPUB_FORMATS + TXT_FORMATS

def main ():
    """ Main program. """

    op = optparse.OptionParser (usage = "usage: %prog [options] url", 
                                version = "EpubMaker version %s" % Version.VERSION)

    CommonOptions.add_common_options (op)

    op.add_option (
        "--make",
        dest    = "types",
        choices = 'all epub txt'.split () + OUTPUT_FORMATS,
        default = [],
        action  = 'append',
        help    = ("output type [all | epub | txt | %s] (default: all)"
                   % ' | '.join (OUTPUT_FORMATS)))

    op.add_option (
        "--max-depth",
        metavar = "LEVELS",
        dest    = "max_depth",
        type    = "int",
        default = 1,
        help    = "go how many levels deep while recursively retrieving pages. (0 == infinite)")

    op.add_option (
        "--include",
        metavar = "GLOB",
        dest    = "include", 
        default = [],
        action  = "append",
        help    = "include this url (use globs, repeat for more urls)")

    op.add_option (
        "--exclude",
        metavar = "GLOB",
        dest    = "exclude", 
        default = [],
        action  = "append",
        help    = "exclude this url (use globs, repeat for more urls)")

    op.add_option (
        "--include-mediatype",
        metavar = "GLOB/GLOB",
        dest    = "include_mediatypes_argument", 
        default = ['text/*', 'application/xhtml+xml'],
        action  = "append",
        help    = "include this mediatype (use globs, repeat for more mediatypes, eg. 'image/*')")

    op.add_option (
        "--exclude-mediatype",
        metavar = "GLOB/GLOB",
        dest    = "exclude_mediatypes", 
        default = [],
        action  = "append",
        help    = "exclude this mediatype (use globs, repeat for more mediatypes)")

    op.add_option (
        "--rewrite",
        metavar = "from>to",
        dest    = "rewrite", 
        default = [],
        action  = "append",
        help    = "rewrite url eg. 'http://www.example.org/>http://www.example.org/index.html'")

    op.add_option (
        "--title",
        dest    = "title", 
        default = None,
        help    = "ebook title (default: from meta)")

    op.add_option (
        "--author",
        dest    = "author", 
        default = None,
        help    = "author (default: from meta)")

    op.add_option (
        "--ebook",
        dest    = "ebook", 
        type    = "int",
        default = 0,
        help    = "ebook no. (default: from meta)")

    op.add_option (
        "--input-encoding",
        dest    = "inputencoding", 
        default = None,
        help    = "input encoding (default: from meta)")

    op.add_option (
        "--output-dir",
        dest    = "outputdir", 
        default = "./",
        help    = "output directory (default: ./)")

    op.add_option (
        "--output-file",
        dest    = "outputfile", 
        default = None,
        help    = "output file (default: <title>.epub)")

    op.add_option (
        "--packager",
        dest    = "packager",
        choices = ['none', 'ww'],
        default = "none",
        help    = "packager type [none | ww] (default: none)")

    options, args = CommonOptions.parse_args (op, {}, {
        'proxies': None,
        'bibrec': 'http://www.gutenberg.org/ebooks/',
        'xelatex': 'xelatex',
        'groff': 'groff',
        } )

    if not args:
        op.error ("please specify which file to convert")

    import __builtin__
    __builtin__.options = options
    __builtin__._ = null_translation

    Logger.set_log_level (options.verbose)        

    if not options.types:
        options.types = ['all']

    if 'txt' in options.types:
        options.types.remove ('txt')
        options.types += TXT_FORMATS
        
    if 'epub' in options.types:
        options.types.remove ('epub')
        options.types += EPUB_FORMATS
        
    if 'all' in options.types:
        options.types = OUTPUT_FORMATS

    options.include_mediatypes = options.include_mediatypes_argument[:]

    ParserFactory.load_parsers ()
    WriterFactory.load_writers ()

    packager_factory = None
    if options.packager != 'none':
        packager_factory = PackagerFactory (options.packager)
        packager_factory.load ()

    for arg in args:
        url = re.sub ('file:/?/?', '', arg)

        if not options.include:
            options.include.append (os.path.dirname (url) + '/*')
            
        # try to get metadata

        options.candidate = Struct ()
        options.candidate.filename = url
        options.candidate.mediatype = str (DCIMT (
            mimetypes.types_map[os.path.splitext (url)[1]], options.inputencoding))
        options.coverpage_url = None

        spider = Spider.Spider ()

        spider.parse (options.candidate.filename, 
                      options.candidate.mediatype,
                      options)
        # debug (options.candidate.mediatype)

        dc = None

        try:
            dc = DublinCore.GutenbergDublinCore ()

            # try for rst header
            dc.load_from_rstheader (spider.parsers[0].unicode_content ())

            if dc.project_gutenberg_id == 0:
                # try for Project Gutenberg header
                dc.load_from_parser (spider.parsers[0])

        except (ValueError, TypeError):
            # use standard HTML header
            dc = DublinCore.DublinCore ()
            dc.load_from_parser (spider.parsers[0])
            dc.source = url

        dc.source = url

        if options.title:
            dc.title = options.title
        if not dc.title:
            dc.title = 'NA'

        if options.author:
            dc.add_author (options.author, 'cre')
        if not dc.authors:
            dc.add_author ('NA', 'cre')

        if options.ebook:
            dc.project_gutenberg_id = options.ebook

        if dc.project_gutenberg_id:
            dc.opf_identifier = ('http://www.gutenberg.org/ebooks/%d' % dc.project_gutenberg_id)
        else:
            dc.opf_identifier = ('urn:mybooks:%s' %
                                 hashlib.md5 (url.encode ('utf-8')).hexdigest ())

        if not dc.languages:
            # we need a language for a valid epub, so make one up
            dc.add_lang_id ('en')

        aux_file_list = []
        
        for type_ in options.types:
            debug ('Building %s' % type_)
            maintype, subtype = os.path.splitext (type_)

            try:
                writer = WriterFactory.create (maintype)
                writer.setup (options)
                options.type = type_
                options.subtype = subtype

                options.include_mediatypes = options.include_mediatypes_argument[:]
                if maintype in ('html', 'pdf') or subtype == '.images':
                    # need list of images
                    options.include_mediatypes.append ('image/*')

                writer.parse (options)

                if maintype in ('html', ):
                    # need list of images for packaging
                    aux_file_list[:] = writer.get_aux_file_list ()

                if dc.project_gutenberg_id:
                    # file naming convention for PG ebooks
                    infix = '-' + maintype
                    if maintype == 'txt':
                        infix = { '.utf-8': '-0', '.iso-8859-1': '-8' }.get (subtype, '')
                    if maintype == 'html':
                        infix = '-h'
                    if maintype == 'epub':
                        infix = '-images-epub' if subtype == '.images' else '-epub'

                    filename = '%d%s.%s' % (dc.project_gutenberg_id, infix, maintype)
                else:
                    # not a PG ebook
                    filename = gg.string_to_filename (dc.title)[:75] + subtype + '.' + maintype

                options.outputfile = filename
                options.dc = dc
                writer.build ()

                if options.validate:
                    writer.validate ()

                if packager_factory:
                    try:
                        packager = packager_factory.create (type_)
                        packager.setup (options)
                        packager.package (aux_file_list)
                    except KeyError:
                        # no such packager
                        pass

                options.outputfile = None

            except SkipOutputFormat:
                continue
            
            except StandardError, what:
                exception ("%s" % what)

        if options.packager == 'ww':
            try:
                packager = packager_factory.create ('push')
                options.outputfile = '%d-final.zip' % (dc.project_gutenberg_id)
                packager.setup (options)
                packager.package (aux_file_list)
            except KeyError:
                # no such packager
                pass

    sys.exit (0)

if __name__ == "__main__":
    main ()



