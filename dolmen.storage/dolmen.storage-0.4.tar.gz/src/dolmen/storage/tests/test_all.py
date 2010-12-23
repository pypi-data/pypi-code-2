# -*- coding: utf-8 -*-

import unittest
import pkg_resources
from dolmen.storage import tests
from zope.testing import doctest


def make_test(dottedname):
    test = doctest.DocTestSuite(
        dottedname,
        optionflags=doctest.ELLIPSIS+doctest.NORMALIZE_WHITESPACE)
    test.layer = tests.DolmenStorageLayer(tests)
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

        dottedname = 'dolmen.storage.tests.%s.%s' % (name, filename[:-3])
        suite.addTest(make_test(dottedname))
    return suite


def test_suite():
    suite = unittest.TestSuite()

    readme = doctest.DocFileSuite(
        '../README.txt',
        optionflags=(doctest.ELLIPSIS + doctest.NORMALIZE_WHITESPACE),
        )
    readme.layer = tests.DolmenStorageLayer(tests)
    suite.addTest(readme)
    
    for name in ['container', 'annotations']:
        suite.addTest(suiteFromPackage(name))
    return suite


if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
