# -*- coding: utf-8 -*-
'''Tests for some basic/generic implementations already provided in the storer
interface.'''

## Created: 2011-01-07 guy Guy K. Kloss <Guy.Kloss@aut.ac.nz>
##
## Copyright 2011 Guy K. Kloss
## Some rights reserved.
##
## http://www.aut.ac.nz/

__author__ = 'Guy K. Kloss <Guy.Kloss@aut.ac.nz>'

import unittest

from matanui.storerinterface import filter_results

from test import testdata


class StorerInterfaceTest(unittest.TestCase):
    """Testing the storerinterface module."""


    def test_filter_results(self):
        for query in testdata.TEST_QUERIES:
            result = filter_results(query, testdata.TEST_ENTRIES)
            result.sort()
            # We need a copy to not compromise the tester's content.
            expected = testdata.TEST_QUERIES[query][:]
            expected.sort()
            self.assertEqual(result, expected)


if __name__ == "__main__":
    unittest.main()
