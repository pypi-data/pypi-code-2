#!/usr/bin/env python
# encoding: utf-8
"""
test_citeulike.citeulike2bib.py

Created by dan mackinlay on 2010-12-09.
Copyright (c) 2010 __MyCompanyName__. All rights reserved.
"""

import nose
from nose.tools import *
from output.bibtex import tex_diacriticize
import codecs

if __name__ == '__main__':
    nose.main()

def test_bib_tex_diacritics():
    source_dest = (
      # (u"field with {", "field with \{", "brace escaping"),
      (u"Swedenbørg", u"Swedenb\o{}rg"), 
      (u"jalapeño", u"jalape\~no"),
      (u"garçon",u"gar\c{c}on"),
      (u"Århus", u"\AA{}rhus"),
      (u"L'Hôpital", u"L'H\^opital"),
    )
    for src, dest in source_dest:
        yield assert_equals, dest, tex_diacriticize(src)