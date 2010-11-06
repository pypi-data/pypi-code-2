# -*- coding: utf-8 -*-

import unittest
import doctest
import pkg_resources
from dolmen.content import tests


def make_test(dottedname):
    test = doctest.DocTestSuite(
        dottedname, setUp=tests.siteSetUp, tearDown=tests.siteTearDown,
        optionflags=doctest.ELLIPSIS + doctest.NORMALIZE_WHITESPACE)
    test.layer = tests.DolmenContentLayer(tests)
    return test


def suiteFromPackage(name):
    files = pkg_resources.resource_listdir(__name__, name)
    suite = unittest.TestSuite()
    for filename in files:
        if not filename.endswith('.py'):
            continue
        if filename.endswith('_fixture.py'):
            continue
        if filename == '__init__.py':
            continue

        dottedname = 'dolmen.content.tests.%s.%s' % (name, filename[:-3])
        suite.addTest(make_test(dottedname))
    return suite


def test_suite():
    suite = unittest.TestSuite()
    readme = doctest.DocFileSuite(
        '../README.txt', globs={'__name__': 'dolmen.content'},
        optionflags=(doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS))
    readme.layer = tests.DolmenContentLayer(tests)
    suite.addTest(readme)
    for name in ['overview', 'schema', 'factory']:
        suite.addTest(suiteFromPackage(name))
    return suite
