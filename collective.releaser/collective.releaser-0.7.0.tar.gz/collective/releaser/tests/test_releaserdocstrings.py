# -*- coding: utf-8 -*-
"""
Generic Test case for collective.releaser doc strings
"""
__docformat__ = 'restructuredtext'

import unittest
import doctest
import sys
import os

from collective.releaser import testing
from zope.testing import doctest

current_dir = os.path.abspath(os.path.dirname(__file__))

def doc_suite(test_dir, globs=None):
    """Returns a test suite, based on doc tests strings found in /*.py"""
    suite = []
    if globs is None:
        globs = globals()

    flags = (doctest.ELLIPSIS | doctest.NORMALIZE_WHITESPACE |
             doctest.REPORT_ONLY_FIRST_FAILURE)

    package_dir = os.path.split(test_dir)[0]
    if package_dir not in sys.path:
        sys.path.append(package_dir)

    # filtering files on extension
    docs = [doc for doc in
            os.listdir(package_dir) if doc.endswith('.py')]
    docs = [doc for doc in docs if not doc.startswith('__')]
    docs = [doc for doc in docs if doc not in ['config.py']]

    for test in docs:
        fd = open(os.path.join(package_dir, test))
        content = fd.read()
        fd.close()
        if '>>> ' not in content:
            continue
        test = test.replace('.py', '')
        suite.append(doctest.DocTestSuite('collective.releaser.%s' % test,
                                            optionflags=flags,
                                            globs=globs,
                                            setUp=testing.releaserSetUp,
                                            tearDown=testing.releaserTearDown))

    return unittest.TestSuite(suite)

def test_suite():
    """returns the test suite"""
    return doc_suite(current_dir)

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')

