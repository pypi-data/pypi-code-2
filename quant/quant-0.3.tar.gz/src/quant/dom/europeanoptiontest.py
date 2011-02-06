import unittest
from quant.dom.testunit import TestCase
from quant.dom.basetest import DerivativesContractTestCase

def suite():
    suites = [
    ]
    return unittest.TestSuite(suites)

class EuropeanOptionTestCase(DerivativesContractTestCase):

    def getContractsRegister(self):
        return self.registry.europeanOptions

