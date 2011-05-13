#
# Tests the Archive
#

from Testing import ZopeTestCase

from Products.ExternalStorage.tests import ESTestCase


class TestArchive(ESTestCase.ESTestCase):
    """Tests the archive of an external article.
    """

    def _testArchiveContent(self):
        # XXX: Test archive!
        self.fail()


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestArchive))
    return suite
