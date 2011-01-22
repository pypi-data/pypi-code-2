import unittest
from pkg_resources import resource_listdir

from zope.testing import doctestunit, doctest
from zope.component import testing

import Products.Five
from Products.Five import zcml

import five.grok
from five.grok.tests.doctest import doctestToPython
import os

from Testing.ZopeTestCase.layer import ZopeLite as ZopeLiteLayer

def setUp(test=None):
    testing.setUp(test)
    zcml.load_config('meta.zcml', package=Products.Five)
    zcml.load_config('configure.zcml', package=Products.Five)
    zcml.load_config('meta.zcml', package=five.grok)
    zcml.load_config('configure.zcml', package=five.grok)
    zcml.load_config('configure.zcml', package=five.grok.tests)

from five.grok.testing import grok
from zope import component


def setUpWithGrokDoctest(test=None):
    testing.setUp(test)
    testFile = test.globs.get('__file__')
    testFileDirName, testFullFileName = os.path.split(testFile)
    testFileName, testFileExt = os.path.splitext(testFullFileName)
    pythonTestFile = os.path.join(testFileDirName, testFileName + '.py')
    doctestToPython(testFile, pythonTestFile)
    component.eventtesting.setUp()
    #XXX this should be done by the GrokDocFileSuite
    grok('five.grok.README')
    from zope.traversing.adapters import DefaultTraversable
    component.provideAdapter(DefaultTraversable, [None])


def tearDownWithGrokDoctest(test=None):
    testing.tearDown(test)
    testFile = test.globs.get('__file__')
    testFileDirName, testFullFileName = os.path.split(testFile)
    testFileName, testFileExt = os.path.splitext(testFullFileName)
    pythonTestFile = os.path.join(testFileDirName, testFileName + '.py')
    os.remove(pythonTestFile)
    pythonPycTestFile = os.path.join(testFileDirName, testFileName + '.pyc')
    if os.path.exists(pythonPycTestFile):
        os.remove(pythonPycTestFile)


def suiteFromPackage(name):
    files = resource_listdir(__name__, name)
    suite = unittest.TestSuite()
    for filename in files:
        if not filename.endswith('.py'):
            continue
        if filename.endswith('_fixture.py'):
            continue
        if filename == '__init__.py':
            continue

        dottedname = 'five.grok.tests.%s.%s' % (name, filename[:-3])
        test = doctest.DocTestSuite(dottedname,
                                    setUp=setUp,
                                    tearDown=testing.tearDown,
                                    optionflags=doctest.ELLIPSIS+
                                                doctest.NORMALIZE_WHITESPACE)

        suite.addTest(test)
    return suite


def test_suite():
    
    readmeSuite = doctestunit.DocFileSuite(
            'README.txt', package='five.grok',
            setUp=setUpWithGrokDoctest, tearDown=tearDownWithGrokDoctest,
            optionflags=doctest.ELLIPSIS+
                        doctest.NORMALIZE_WHITESPACE)
    readmeSuite.layer = ZopeLiteLayer
    
    return unittest.TestSuite([

        # Unit tests for your API
        readmeSuite,

        doctestunit.DocTestSuite(
            module='five.grok.tests.adapters',
            setUp=setUp, tearDown=testing.tearDown),

        doctestunit.DocTestSuite(
            module='five.grok.tests.annotation',
            setUp=setUp, tearDown=testing.tearDown),

        doctestunit.DocTestSuite(
            module='five.grok.tests.multiadapter',
            setUp=setUp, tearDown=testing.tearDown),

        doctestunit.DocTestSuite(
            module='five.grok.tests.utilities',
            setUp=setUp, tearDown=testing.tearDown),

        doctestunit.DocTestSuite(
            module='five.grok.tests.subscribers',
            setUp=setUp, tearDown=testing.tearDown),

        doctestunit.DocTestSuite(
            module='five.grok.tests.resource',
            setUp=setUp, tearDown=testing.tearDown),
        ])


if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
