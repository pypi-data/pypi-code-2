import unittest
from quant.pricer.basetest import PricerTestCase
from quant.pricer.binomialtree import EuropeanBinomialTreePricer
from quant.pricer.binomialtree import AmericanBinomialTreePricer

def suite():
    suites = [
        unittest.makeSuite(TestEuropeanCall),
        unittest.makeSuite(TestEuropeanPut),
        unittest.makeSuite(TestAmericanCall),
        unittest.makeSuite(TestAmericanPut),
    ]
    return unittest.TestSuite(suites)


class BinomialTreePricerTestCase(PricerTestCase):

    DECIMALS = 3


class TestEuropeanCall(BinomialTreePricerTestCase):

    pricerClass = EuropeanBinomialTreePricer

    strikePrice = 9
    lastPrice = 10
    actualHistoricalVolatility = 50
    expectedValue = 2.416


class TestEuropeanPut(BinomialTreePricerTestCase):

    pricerClass = EuropeanBinomialTreePricer
    isPut = True

    strikePrice = 9
    lastPrice = 10
    actualHistoricalVolatility = 50
    expectedValue = 1.416


class TestAmericanCall(BinomialTreePricerTestCase):

    pricerClass = AmericanBinomialTreePricer

    strikePrice = 9
    lastPrice = 10
    actualHistoricalVolatility = 50
    expectedValue = 2.416


class TestAmericanPut(BinomialTreePricerTestCase):

    pricerClass = AmericanBinomialTreePricer
    isPut = True

    strikePrice = 9
    lastPrice = 10
    actualHistoricalVolatility = 50
    expectedValue = 1.416

