import os
import unittest


class TestCase(unittest.TestCase):

    def setUp(self):
        os.environ['CICERO_TEST'] = '1'

    def test_call_cicero(self):
        # smoke test for suds integration -- doesn't actually do a live lookup
        from collective.cicero import call_cicero
        res = call_cicero('ElectedOfficialQueryService', 'GetOfficialsByAddress')
        self.assertEqual('ArrayOfElectedOfficialInfo', res.__class__.__name__)
        self.assertEqual(2, len(res[0]))


def test_suite():
    import unittest
    return unittest.defaultTestLoader.loadTestsFromName(__name__)
