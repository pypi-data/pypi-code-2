from quant.dom.testunit import TestCase
from quant.market import BlackScholesProcess
import unittest

def suite():
    suites = [
        unittest.makeSuite(TestMarketData),
    ]
    return unittest.TestSuite(suites)

class TestMarketData(TestCase):

    marketDataService = 'test'
    marketName = 'wti'
    marketDeliveryPeriod = '2011-01-06'

    expectedNowTime = '2010-01-06 00:00:00'
    expectedCurrentPrices = [10, 12, 9, 10]
    expectedVolatilities = [50, 50, 50, 50]
    expectedDeliveryPeriods = ['2010-10-06', '2010-11-06', '2010-12-06', '2011-01-06']
    expectedPriceProcessClass = BlackScholesProcess

    def setUp(self):
        from quant.market import MarketData
        self.market = MarketData(
            dataService=self.marketDataService,
            name=self.marketName,
        )

    def test_getCurrentPrice(self):
        for i in range(len(self.expectedDeliveryPeriods)):
            deliveryPeriod = self.expectedDeliveryPeriods[i]
            currentPrice = self.market.getCurrentPrice(deliveryPeriod=deliveryPeriod)
            self.assertEqual(currentPrice, self.expectedCurrentPrices[i])

    def test_getAnnualisedVolatility(self):
        for i in range(len(self.expectedDeliveryPeriods)):
            deliveryPeriod = self.expectedDeliveryPeriods[i]
            annualisedVolatility = self.market.getAnnualisedVolatility(deliveryPeriod=deliveryPeriod) 
            self.assertEqual(annualisedVolatility, self.expectedVolatilities[i])

    def test_getNowTime(self):
        self.assertEqual(self.market.getNowTime(), self.expectedNowTime)

    def test_getPriceProcess(self):
        self.assertEqual(type(self.market.getPriceProcess()), self.expectedPriceProcessClass)

