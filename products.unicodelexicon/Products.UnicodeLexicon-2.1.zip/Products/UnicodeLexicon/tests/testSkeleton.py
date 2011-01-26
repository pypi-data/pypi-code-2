#
# Skeleton UnicodeLexiconTestCase
#

from Products.UnicodeLexicon.tests import UnicodeLexiconTestCase


class TestSomeProduct(UnicodeLexiconTestCase.UnicodeLexiconTestCase):

    def afterSetUp(self):
        pass

    def testSomething(self):
        # Test something
        self.assertEqual(1+1, 2)


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestSomeProduct))
    return suite

