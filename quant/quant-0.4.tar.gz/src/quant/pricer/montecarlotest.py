import unittest
from quant.pricer.basetest import PricerTestCase
from quant.pricer.montecarlo import EuropeanMonteCarloPricer
from quant.pricer.montecarlo import AmericanMonteCarloPricer

def suite():
    suites = [
        unittest.makeSuite(TestEuropeanCall),
        unittest.makeSuite(TestEuropeanPut),
#        unittest.makeSuite(TestAmericanCall),
#        unittest.makeSuite(TestAmericanPut),
    ]
    return unittest.TestSuite(suites)


class MonteCarloPricerTestCase(PricerTestCase):

    DECIMALS = 1


class TestEuropeanCall(MonteCarloPricerTestCase):

    pricerClass = EuropeanMonteCarloPricer

    strikePrice = 9
    currentPrice = 10
    annualisedVolatility = 50
    expectedValue = 2.416


class TestEuropeanPut(MonteCarloPricerTestCase):

    pricerClass = EuropeanMonteCarloPricer
    isPut = True

    strikePrice = 9
    currentPrice = 10
    annualisedVolatility = 50
    expectedValue = 1.416


class TestAmericanCall(MonteCarloPricerTestCase):

    pricerClass = AmericanMonteCarloPricer

    strikePrice = 9
    currentPrice = 10
    annualisedVolatility = 50
    expectedValue = 2.416


class TestAmericanPut(MonteCarloPricerTestCase):

    pricerClass = AmericanMonteCarloPricer
    isPut = True

    strikePrice = 9
    currentPrice = 10
    annualisedVolatility = 50
    expectedValue = 1.416

