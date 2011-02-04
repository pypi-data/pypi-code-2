from quant.dom.testunit import TestCase

class PricerTestCase(TestCase):

    DECIMALS = 4

    pricerClass = None
    isPut = False

    strikePrice = 10
    currentPrice = 10
    annualisedVolatility = 50
    annualRiskFreeRate = 0
    tolerance = 1e-8
    nowTime = '2010-01-06'
    expiryTime = '2011-01-06'

    expectedExceptionClass = None

    def setUp(self):
        self.assertTrue(self.pricerClass, "Pricer class missing on %s." % self.__class__.__name__)
            
        self.calc = self.pricerClass(
            strikePrice=self.strikePrice,
            currentPrice=self.currentPrice,
            annualisedVolatility=self.annualisedVolatility,
            nowTime=self.nowTime,
            expiryTime=self.expiryTime,
            annualRiskFreeRate=self.annualRiskFreeRate,
            isPut=self.isPut,
        )

    def test_calcPrice(self):
        if self.expectedExceptionClass:
            self.assertRaises(self.expectedExceptionClass, self.calc.run)
        else:
            estimatedValue = self.calc.calcPrice()
            estimatedValue = round(estimatedValue, self.DECIMALS)
            expectedValue = round(self.expectedValue, self.DECIMALS)
            msg = "Value: %s  Expected: %s  Strike: %s  Current: %s  Volatility: %s  Rate: %s" % (estimatedValue, expectedValue, self.strikePrice, self.currentPrice, self.annualisedVolatility, self.annualRiskFreeRate)
            self.assertEqual(estimatedValue, expectedValue, msg)


