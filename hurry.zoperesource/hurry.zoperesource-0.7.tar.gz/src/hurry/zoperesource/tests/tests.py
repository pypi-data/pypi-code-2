import os
import unittest
import doctest

from zope.app.testing.functional import FunctionalDocFileSuite
from zope.app.testing import functional

FunctionalLayer = functional.ZCMLLayer(
    os.path.join(os.path.split(__file__)[0], 'ftesting.zcml'),
    __name__, 'FunctionalLayer')


def test_suite():
    optionflags = doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS
    globs = {}

    suite = unittest.TestSuite()

    readme = FunctionalDocFileSuite(
        '../README.txt',
        optionflags=optionflags,
        globs=globs)

    readme.layer = FunctionalLayer

    suite.addTest(readme)

    return suite
