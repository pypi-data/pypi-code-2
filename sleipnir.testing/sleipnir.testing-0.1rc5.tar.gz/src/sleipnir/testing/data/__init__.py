#!/usr/bin/env python
# -*- mode:python; tab-width: 2; coding: utf-8 -*-

"""Unit Test Data files"""

from __future__ import absolute_import

__author__  = "Carlos Martin <cmartin@liberalia.net>"
__status__  = "alpha"
__version__ = "0.2"
__date__    = "25 January 2010"
__license__ = "See LICENSE file for details"

import os
import sys

__all__ = ['DATA']

#Add here local modules
from .. import constants


class DATA(object):
    """Collector to access Test files"""

    PLUGIN_DIRS = [
        os.path.join(constants.__plugin_dir__, 'eggs'),
        os.path.join(constants.__plugin_dir__, 'python')
        ]

    def __init__(self, dct=None):
        #pylint: disable-msg=E1002
        super(DATA, self).__init__()
        self.contents = dct or {}

        if not len(self.contents):
            for inst in dir(self.__class__):
                if type(getattr(self.__class__, inst)) == property:
                    self.__get_tests(inst)

    def __getitem__(self, key):
        return self.contents[key]

    def __getattr__(self, value):
        return getattr(self.contents, value)

    def __get_tests(self, ttype):
        """Retrieve test of type 'ttype'"""

        retval = self.contents.setdefault(ttype, [])
        if not retval:
            for root, _, tfile in os.walk(constants.__tsplib_dir__):
                for ffile in [x for x in tfile if x.endswith(ttype)]:
                    self.contents[ttype].append(os.path.join(root, ffile))
        return retval

    @property
    def dct(self):
        """Get tests in TSPlib Format required by doctests"""
        return self.__get_tests('dct')

    @property
    def jsn(self):
        """Get tests compatible with Python TSP Serialize format"""
        return self.__get_tests('jsn')

    @property
    def tsp(self):
        """Get tests comptible with TSPlib Format"""
        return self.__get_tests('tsp')
