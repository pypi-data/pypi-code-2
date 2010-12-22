# Standard library imports
import unittest
import sys
from StringIO import StringIO
import os
import tempfile
import shutil

# 3rd party imports
import numpy

# Custom library imports
import marketgraphs
import simple
import list_participants
import marginal_prices


class ScriptSandbox(unittest.TestCase):
    def setUp(self):
        self._old_stdout = sys.stdout
        self._old_stderr = sys.stderr
        self._old_cwd = os.getcwd()

        self._tempdir = tempfile.mkdtemp()
        os.chdir(self._tempdir)
        sys.stdout = StringIO()
        sys.stderr = StringIO()

    def tearDown(self):
        def errorhander(function, path, execinfo):
            raise OSError('Cannot delete tempfile at ' + path)

        stdout = sys.stdout
        stderr = sys.stderr

        sys.stdout = self._old_stdout
        sys.stderr = self._old_stderr
        os.chdir(self._old_cwd)

        # Delete temp directory
        shutil.rmtree(self._tempdir, onerror = errorhander)


class TestMarketGraphs(ScriptSandbox):
    def assertArraysEqual(self, a1, a2):
        self.assertEquals(len(a1), len(a2), str(a1) + ' != ' + str(a2) + '; array lengths not equal.')

        for i in xrange(len(a1)):
            self.assertEquals(a1[i], a2[i], 'Array values at index ' + str(i) + ' not equal (' + str(a1) + ' != ' + str(a2) + ')')


    def test_block_avg_filter(self):
        sample = numpy.array([1., 2., 3., 4., 5., 6.])
        expected = [1.5, 3.5, 5.5]
        actual = marketgraphs.block_avg_filter(sample, 2)
        self.assertArraysEqual(expected, actual)

        sample = numpy.array([1., 2., 3., 4., 5., 6., 7.])
        expected = [3., 6.]
        actual = marketgraphs.block_avg_filter(sample, 3)
        self.assertArraysEqual(expected, actual)


    def test_block_max_filter(self):
        sample = [1, 4, 2, 5, 3, 6]
        expected = [4, 5, 6]
        actual = marketgraphs.block_max_filter(sample, size = 2)
        self.assertArraysEqual(expected, actual)

        sample = [1, 4, 2, 5, 3, 6, 7]
        expected = [5, 7]
        actual = marketgraphs.block_max_filter(sample, size = 3)
        self.assertArraysEqual(expected, actual)


    def test_block_min_filter(self):
        sample = [0, 1, 4, 2, 5, 3, 6]
        expected = [1, 2, 3]
        actual = marketgraphs.block_min_filter(sample, size = 2)

        self.assertArraysEqual(expected, actual)


    def test_main(self):
        self.assertEquals(marketgraphs.main(), 0)

        expected_files = [
            'market-demand.png',
            'market-price.png',
            'market-equilibrium.png',
        ]

        for fn in expected_files:
            self.assertTrue(os.path.isfile(fn))
            self.assertTrue(os.path.getsize(fn) > 10)


class TestSimple(ScriptSandbox):
    def test_main(self):
        self.assertEquals(simple.main(), 0)

        self.assertTrue(len(sys.stdout.getvalue()) > 50)


class TestListParticipants(ScriptSandbox):
    def test_main(self):
        self.assertEquals(list_participants.main(), 0)

        self.assertTrue(len(sys.stdout.getvalue()) > 50)


class TestMarginalPrices(ScriptSandbox):
    def test_main(self):
        self.assertEquals(marginal_prices.main(), 0)

        self.assertTrue(len(sys.stdout.getvalue()) > 100)


if __name__ == '__main__':
    unittest.main()

