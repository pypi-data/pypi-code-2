import unittest
from quant.pricer.basetest import PricerTestCase
from quant.testunit import VOLATILITY_MEDIUM
from quant.testunit import VOLATILITY_LOW
from quant.testunit import VOLATILITY_HIGH
from quant.testunit import VOLATILITY_ZERO
from quant.pricer.blackscholes import BlackScholesPricer

def suite():
    suites = [
        unittest.makeSuite(TestBlackScholesCallPricer),
        unittest.makeSuite(TestBlackScholesCallOnMoney),
        unittest.makeSuite(TestBlackScholesCallInMoney),
        unittest.makeSuite(TestBlackScholesCallOutMoney),
        unittest.makeSuite(TestBlackScholesCallLowRate),
        unittest.makeSuite(TestBlackScholesCallHighRate),
        unittest.makeSuite(TestBlackScholesPutPricer),
        unittest.makeSuite(TestBlackScholesPutOnMoney),
        unittest.makeSuite(TestBlackScholesPutOutMoney),
        unittest.makeSuite(TestBlackScholesPutInMoney),
        unittest.makeSuite(TestBlackScholesPutLowRate),
        unittest.makeSuite(TestBlackScholesPutHighRate),
    ]
    return unittest.TestSuite(suites)


class BlackScholesPricerTestCase(PricerTestCase):

    pricerClass = BlackScholesPricer
    strikePrice = 9.0

class BlackScholesCallPricerTestCase(BlackScholesPricerTestCase):
    pass


class TestBlackScholesCallPricer(BlackScholesCallPricerTestCase):
    currentPrice = 10.0
    expectedValue = 2.416

class TestBlackScholesCallOnMoney(BlackScholesCallPricerTestCase):
    currentPrice = 9.0
    expectedValue = 1.7767

class TestBlackScholesCallInMoney(BlackScholesCallPricerTestCase):
    currentPrice = 20.0
    expectedValue = 11.1534

class TestBlackScholesCallOutMoney(BlackScholesCallPricerTestCase):
    currentPrice = 3.0
    expectedValue = 0.0125

class TestBlackScholesCallLowRate(BlackScholesCallPricerTestCase):
    currentPrice = 10.0
    annualRiskFreeRate = 1.0
    expectedValue = 2.4597

class TestBlackScholesCallHighRate(BlackScholesCallPricerTestCase):
    currentPrice = 10.0
    annualRiskFreeRate = 10.0
    expectedValue = 2.8644

class BlackScholesPutPricerTestCase(BlackScholesPricerTestCase):
    isPut = True

class TestBlackScholesPutPricer(BlackScholesPutPricerTestCase):
    currentPrice = 10.0
    expectedValue = 1.416

class TestBlackScholesPutOnMoney(BlackScholesPutPricerTestCase):
    currentPrice = 9.0
    expectedValue = 1.7767

class TestBlackScholesPutOutMoney(BlackScholesPutPricerTestCase):
    currentPrice = 20.0
    expectedValue = 0.1534

class TestBlackScholesPutInMoney(BlackScholesPutPricerTestCase):
    currentPrice = 3.0
    expectedValue = 6.0125

class TestBlackScholesPutLowRate(BlackScholesPutPricerTestCase):
    currentPrice = 10.0
    annualRiskFreeRate = 1.0
    expectedValue = 1.3702

class TestBlackScholesPutHighRate(BlackScholesPutPricerTestCase):
    currentPrice = 10.0
    annualRiskFreeRate = 10.0
    expectedValue = 1.0079

