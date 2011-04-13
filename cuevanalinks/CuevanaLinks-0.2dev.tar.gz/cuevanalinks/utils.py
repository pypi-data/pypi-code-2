#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
from unicodedata import normalize
from urlparse import urlparse

_punct_re = re.compile(r'[\t !"#$%&\'()*\-/<=>?@\[\\\]^_`{|},.]+')

def slugify(text, delim=u'-'):
    """Generates an slightly worse ASCII-only slug."""
    result = []
    for word in _punct_re.split(unicode(text).lower()):
        word = normalize('NFKD', word).encode('ascii', 'ignore')
        if word:
            result.append(word)
    return unicode(delim.join(result))


def urlparams(url):
    """
    Get an URL an return a dictionary of its query params
    """
    import pdb; pdb.set_trace()
    url = urlparse(url)
    return dict([part.split('=') for part in url[4].split('&')])
    
    


def get_numbers(s):
    """Extracts all integers from a string an return them in a list"""

    return map(int, re.findall(r'[0-9]+', unicode(s)))
