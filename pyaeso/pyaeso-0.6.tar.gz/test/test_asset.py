########################################################################
## Standard library imports
#~ from datetime import datetime
#~ from datetime import date
#~ from datetime import timedelta
import unittest
import doctest
import sys
import os
import bz2
from cStringIO import StringIO


########################################################################
## Import 3rd party modules
#~ import pytz


########################################################################
## AESO Modules
from aeso import asset
import libtest


class TestAssetList(unittest.TestCase):
    def test_parse_asset_list_file(self):
        test_series_file = os.path.join(os.path.dirname(__file__), 'res', 'asset_list.csv.bz2')

        f = bz2.BZ2File(test_series_file)
        assets = list(asset.parse_asset_list_file(f))
        self.assertEquals(len(assets), 1862)
        for a in assets:
            for char in '<>':
                # ETS embeds HTML anchors in the asset name.  Test to
                # make sure they have been properly stripped out.
                self.assertTrue(char not in a.asset_name)
        f.close()


class TestAssetRemote(unittest.TestCase):
    def test_asset_list_connection(self):
        '''ETS-Coupled Test.'''
        f = StringIO()
        asset.dump_asset_list(f)
        assets = list(asset.parse_asset_list_file(f))
        f.close()


loader = unittest.TestLoader()
remote_suites = [
    loader.loadTestsFromTestCase(TestAssetRemote),
    doctest.DocTestSuite(asset),
]

local_suites = [
    loader.loadTestsFromTestCase(TestAssetList),
]


if __name__ == '__main__':
    sys.exit(libtest.main(sys.argv[1:], local_suites, remote_suites))
