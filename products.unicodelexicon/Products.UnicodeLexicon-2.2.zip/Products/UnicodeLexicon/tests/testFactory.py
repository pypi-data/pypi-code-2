#
# Test OrderedMapping and PipelineFactory
#

from unittest import TestCase, TestSuite, makeSuite
from Products.UnicodeLexicon.pipelinefactory import OrderedMapping
from Products.UnicodeLexicon.pipelinefactory import PipelineElementFactory


class TestOrderedMapping(TestCase):

    def testAdd(self):
        m = OrderedMapping()
        m['fred'] = 1
        m['barney'] = 2
        m['wilma'] = 3
        m['betty'] = 4
        self.assertEqual(m.keys(), ['fred', 'barney', 'wilma', 'betty'])

    def testSet(self):
        m = OrderedMapping()
        m['fred'] = 1
        m['barney'] = 2
        m['wilma'] = 3
        m['betty'] = 4
        m['fred'] = 5
        self.assertEqual(m.keys(), ['fred', 'barney', 'wilma', 'betty'])

    def testDel(self):
        m = OrderedMapping()
        m['fred'] = 1
        m['barney'] = 2
        m['wilma'] = 3
        m['betty'] = 4
        del m['wilma']
        self.assertEqual(m.keys(), ['fred', 'barney', 'betty'])


class TestFactory(TestCase):

    def testRegister(self):
        class Element: pass
        f = PipelineElementFactory()
        f.registerFactory('Word Splitter', 'Whitespace splitter', Element)
        f.registerFactory('Word Splitter', 'HTML aware splitter', Element)
        f.registerFactory('Case Normalizer', 'Case normalizer', Element)
        self.assertEqual(f.getFactoryGroups(), ['Word Splitter', 'Case Normalizer'])
        self.assertEqual(f.getFactoryNames('Word Splitter'), ['Whitespace splitter', 'HTML aware splitter'])
        self.assertEqual(f.getFactoryNames('Case Normalizer'), ['Case normalizer'])

    def testInstantiate(self):
        class Element: pass
        f = PipelineElementFactory()
        f.registerFactory('Word Splitter', 'Whitespace splitter', Element)
        elem = f.instantiate('Word Splitter', 'Whitespace splitter')
        self.failUnless(isinstance(elem, Element))


def test_suite():
    suite = TestSuite()
    suite.addTest(makeSuite(TestOrderedMapping))
    suite.addTest(makeSuite(TestFactory))
    return suite

