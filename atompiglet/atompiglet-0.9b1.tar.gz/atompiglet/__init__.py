#!/usr/bin/env python
# encoding: utf-8
"""
__init__.py

Created by Keith Fahlgren on Sat Jan 17 14:14:36 PST 2009
Copyright (c) 2009 O'Reilly Media. All rights reserved.
"""

import urlparse

ATOM_ENTRY_CONTENT_TYPE='application/atom+xml;type=entry'
NAMESPACES = {
    'atom':  'http://www.w3.org/2005/Atom',
    'app':   'http://www.w3.org/2007/app',
    'dc':    'http://purl.org/dc/terms/',
    'rdf':   'http://www.w3.org/1999/02/22-rdf-syntax-ns#',
    'xhtml': 'http://www.w3.org/1999/xhtml',
}

def get_absolute_url(base, uri):
    if base:
        absolute_uri = urlparse.urljoin(base, uri)
        return absolute_uri
    else:
        return uri
