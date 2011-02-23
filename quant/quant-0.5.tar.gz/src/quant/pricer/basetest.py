from quant.dom.testunit import TestCase
import datetime

class PricerTestCase(TestCase):

    DECIMALS = 4

    pricerClass = None
    isPut = False

    strikePrice = 10
    lastPrice = 10
    actualHistoricalVolatility = 50
    annualRiskFreeRate = 0
    tolerance = 1e-8
    nowTime = datetime.datetime(2010, 1, 1)
    expiration = datetime.datetime(2011, 1, 1)

    expectedExceptionClass = None

    def setUp(self):
        self.assertTrue(self.pricerClass, "Pricer class missing on %s." % self.__class__.__name__)
            
        self.calc = self.pricerClass(
            strikePrice=self.strikePrice,
            lastPrice=self.lastPrice,
            actualHistoricalVolatility=self.actualHistoricalVolatility,
            nowTime=self.nowTime,
            expiration=self.expiration,
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
            msg = "Value: %s  Expected: %s  Strike: %s  Current: %s  Volatility: %s  Rate: %s" % (estimatedValue, expectedValue, self.strikePrice, self.lastPrice, self.actualHistoricalVolatility, self.annualRiskFreeRate)
            self.assertEqual(estimatedValue, expectedValue, msg)


