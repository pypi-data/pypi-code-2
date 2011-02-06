from quant.dom.testunit import TestCase
import unittest

def suite():
    suites = [
        unittest.makeSuite(TestMarket),
    ]
    return unittest.TestSuite(suites)

class TestMarket(TestCase):

    def setUp(self):
        self.market = self.registry.markets['WTI (Mock)']

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


