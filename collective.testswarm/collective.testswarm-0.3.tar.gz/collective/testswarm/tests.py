""" A sample test, this uses a layer which uses TESTSWARM_LAYER as its
base.
"""
import unittest2 as unittest

from layers import TESTTESTSWARM_LAYER


class TestSwarmTestCase(unittest.TestCase):
    """ The layer registers the resources required to run the test and
    adds a job with a list of suites to the TestSwarm instance."""
    layer = TESTTESTSWARM_LAYER

    def test_collective_testswarm(self):
        """Just need one test for the testrunner to sniff out.

        NOTE: Since the layer has a timeout in its testSetUp method
        nothing in this test would be called until that timeout was
        over."""
