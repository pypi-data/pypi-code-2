import unittest
from quant.dom.basetest import DerivativesContractTestCase

def suite():
    suites = [
    ]
    return unittest.TestSuite(suites)

class ForwardContractTestCase(DerivativesContractTestCase):

    def getContractsRegister(self):
        return self.registry.forwardContracts

