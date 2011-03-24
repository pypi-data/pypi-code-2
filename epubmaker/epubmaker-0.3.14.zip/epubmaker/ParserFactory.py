#!/usr/bin/env python
#  -*- mode: python; indent-tabs-mode: nil; -*- coding: iso-8859-1 -*-

"""

ParserFactory.py

Copyright 2009-10 by Marcello Perathoner

Distributable under the GNU General Public License Version 3 or newer.

"""

from __future__ import with_statement

import os.path
import urllib

from pkg_resources import resource_listdir # pylint: disable=E0611

from epubmaker.lib.Logger import debug, error

parser_modules = {}

def load_parsers ():
    """ See what types we can parse. """

    for fn in resource_listdir ('epubmaker.parsers', ''):
        modulename, ext = os.path.splitext (fn)
        if ext == '.py':
            if (modulename.endswith ('Parser')):
                module = __import__ ('epubmaker.parsers.' + modulename, fromlist = [modulename])
                debug ("Loading parser from module: %s for mediatypes: %s" % (
                    modulename, ', '.join (module.mediatypes)))
                for mediatype in module.mediatypes:
                    parser_modules[mediatype] = module

    return parser_modules.keys ()


def unload_parsers ():
    """ Unload parser modules. """
    for k in parser_modules.keys ():
        del parser_modules[k]
    

class ParserFactory (object):
    """ A factory and a cache for parsers.

    So we don't reparse the same file twice.

    """

    parsers = {} # cache: parsers[url] = parser
    
    @staticmethod
    def get (mediatype):
        """ Get the right kind of parser. """
        try:
            return parser_modules[mediatype].Parser ()
        except KeyError:
            return parser_modules['*/*'].Parser ()
            

    @classmethod
    def create (cls, url, attribs):
        """ Create an appropriate parser. """

        debug ("Need parser for %s" % url)

        if url in cls.parsers:
            debug ("... reusing parser for %s" % url)
            # reuse same parser, maybe already filled with data
            return cls.parsers[url]

        orig_url = url
        fp = urllib.urlopen (orig_url, proxies = options.config.PROXIES)
        url = fp.geturl ()

        if url != orig_url:
            debug ("... redirected to %s" % url)
            if url in cls.parsers:
                debug ("... reusing parser for %s" % url)
                # reuse same parser, maybe already filled with data
                return cls.parsers[url]

        # ok. so we have to create a new parser
        debug ("... creating new parser for %s" % url)

        msg = fp.info ()
        mediatype = msg.get ('Content-Type')
        if mediatype:
            mediatype = mediatype.partition (';')[0]
            debug ("... got mediatype %s from server" % mediatype)
        else:
            mediatype = 'application/octet-stream'
            error ("... cannot determine mediatype for %s" % url)

        # get the right kind of parser
        try:
            parser = parser_modules[mediatype].Parser ()
        except KeyError:
            parser = parser_modules['*/*'].Parser ()

        parser.setup (orig_url, mediatype, attribs, fp)

        cls.parsers[parser.url] = parser
        cls.parsers[orig_url] = parser

        return parser
    

    @classmethod
    def clear (cls):
        """ Clear parser cache to free memory. """

        # debug: kill refs
        for dummy_url, parser in cls.parsers.items ():
            del parser
            
        cls.parsers = {}

