#!/usr/bin/env python
# encoding: utf-8
"""
test_misc.py

Created by Keith Fahlgren on Mon Oct  5 17:02:45 PDT 2009
Copyright (c) 2009 O'Reilly Media. All rights reserved.
"""

from nose.tools import *

from atompiglet import get_absolute_url
from atompiglet.server import Server

class TestMisc:
    def test_absolute_url(self):
        """The get_absolute_url should make a URL absolute."""
        absoluted = get_absolute_url('http://www.cwi.nl', 'FAQ.html')
        expected = 'http://www.cwi.nl/FAQ.html'
        assert_equal(expected, absoluted)

    def test_absolute_url_no_base(self):
        """The get_absolute_url should make a URL absolute even if it already is."""
        absoluted = get_absolute_url(None, 'http://www.cwi.nl/%7Eguido/FAQ.html')
        expected = 'http://www.cwi.nl/%7Eguido/FAQ.html'
        assert_equal(expected, absoluted)

