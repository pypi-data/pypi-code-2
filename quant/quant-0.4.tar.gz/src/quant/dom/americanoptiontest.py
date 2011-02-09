import unittest
from quant.dom.testunit import TestCase
from quant.dom.basetest import DerivativesContractTestCase

def suite():
    suites = [
    ]
    return unittest.TestSuite(suites)


class AmericanTestCase(DerivativesContractTestCase):

    def getContractsRegister(self):
        return self.registry.americans

