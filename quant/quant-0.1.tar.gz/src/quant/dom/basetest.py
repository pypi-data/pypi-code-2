import unittest
from quant.dom.testunit import TestCase
from quant.testunit import VOLATILITY_MEDIUM
from quant.testunit import VOLATILITY_LOW
from quant.testunit import VOLATILITY_HIGH
from quant.testunit import VOLATILITY_ZERO

def suite():
    suites = [
    ]
    return unittest.TestSuite(suites)

class DerivativesContractTestCase(TestCase):

    contractVolume = 10
    contractStrikePrice = 10
    contractExpiryTime = '2011-01-06'
    contractDeliveryPeriod = '2011-01-06'
    contractIsPut = False

    marketDataService = 'test'
    marketName = 'wti' # Oil market. 

    expectedMarketCurrentPrice = 10
    expectedMarketVolatility = 50
    expectedContractValue = None

    def setUp(self):
        super(DerivativesContractTestCase, self).setUp()
        self.contract = self.createContract()

    def tearDown(self):
        if self.contract:
            self.contract.delete()
        super(DerivativesContractTestCase, self).tearDown()

    def createContract(self, **kwds):
        return self.getContractsRegister().create(
            volume=self.contractVolume,
            strikePrice=self.contractStrikePrice,
            expiryTime=self.contractExpiryTime,
            deliveryPeriod=self.contractDeliveryPeriod,
            isPut=self.contractIsPut,
            marketDataService=self.marketDataService,
            marketName=self.marketName,
            **kwds
        )

    def getContractsRegister(self):
        raise Exception("Method not implemented.")

    def test_evaluate(self):
        self.failUnlessEqual(self.contract.market.getCurrentPrice(deliveryPeriod=self.contractExpiryTime), self.expectedMarketCurrentPrice)
        self.failUnlessEqual(self.contract.market.getAnnualisedVolatility(deliveryPeriod=self.contractExpiryTime), self.expectedMarketVolatility)
        self.contract.evaluate()
        contractValue = round(self.contract.value, 4)
        msg = self.getEvaluateErrorMsg(contractValue)
        self.failUnlessEqual(contractValue, self.expectedContractValue, msg)

    def getEvaluateErrorMsg(self, contractValue):
        msg = "Value: %s  Expected: %s  Volume: %s  Strike: %s  Current: %s  Volatility: %s" % (contractValue, self.expectedContractValue, self.contract.volume, self.contract.strikePrice, self.contract.market.getCurrentPrice(deliveryPeriod=self.contractExpiryTime), self.contract.market.getAnnualisedVolatility(deliveryPeriod=self.contractExpiryTime))
        return msg

