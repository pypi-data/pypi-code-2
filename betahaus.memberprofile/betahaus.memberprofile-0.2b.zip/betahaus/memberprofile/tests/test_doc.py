"""
    Functional tests - collects all *.txt files
"""

import os
import glob
from zope.testing import doctest
import unittest
from Globals import package_home
from Testing.ZopeTestCase import FunctionalDocFileSuite as Suite
from base import FunctionalTestCase

GLOBALS = globals()

UNITTESTS = []

OPTIONFLAGS = (doctest.ELLIPSIS |
               doctest.NORMALIZE_WHITESPACE |
               doctest.REPORT_ONLY_FIRST_FAILURE)

def list_doctests():
    home = package_home(GLOBALS)
    return [filename for filename in
            glob.glob(os.path.sep.join([home, '*.txt']))
            if os.path.basename(filename) not in UNITTESTS]

def test_suite():
    filenames = list_doctests()

    suites = [Suite(os.path.basename(filename),
               optionflags=OPTIONFLAGS,
               package='betahaus.memberprofile.tests',
               test_class=FunctionalTestCase)
              for filename in filenames]

    return unittest.TestSuite(suites)
