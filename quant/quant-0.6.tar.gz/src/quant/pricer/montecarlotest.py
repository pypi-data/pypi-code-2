import unittest
from quant.pricer.basetest import PricerTestCase
from quant.pricer.simple import EuropeanMonteCarlo
from quant.pricer.simple import AmericanMonteCarlo
from quant.pricer.simple import DslMonteCarlo
from quant.dsl import DslSourceError
from quant.dsl import DslProgrammingError

def suite():
    suites = [
        unittest.makeSuite(TestEuropeanCall),
        unittest.makeSuite(TestEuropeanPut),
#        unittest.makeSuite(TestAmericanCall),
#        unittest.makeSuite(TestAmericanPut),
        unittest.makeSuite(TestDslEuropean),
        unittest.makeSuite(TestDslFutures),
        unittest.makeSuite(TestDslAddition),
        unittest.makeSuite(TestDslBrokenRoot),
        unittest.makeSuite(TestDslBrokenUnbalancedMax),
        unittest.makeSuite(TestDslBrokenDateIsNotValue),
    ]
    return unittest.TestSuite(suites)

# Todo: Variable pathCount (tests want low value, sites want high value).

class MonteCarloPricerTestCase(PricerTestCase):

    DECIMALS = 1


class TestEuropeanCall(MonteCarloPricerTestCase):

    pricerClass = EuropeanMonteCarlo

    strikePrice = 9
    lastPrice = 10
    actualHistoricalVolatility = 50
    expectedValue = 2.416
    expectedDelta = 0.677
    expectedGamma = 0.07


class TestEuropeanPut(MonteCarloPricerTestCase):

    pricerClass = EuropeanMonteCarlo
    isPut = True

    strikePrice = 9
    lastPrice = 10
    actualHistoricalVolatility = 50
    expectedValue = 1.416


class TestAmericanCall(MonteCarloPricerTestCase):

    pricerClass = AmericanMonteCarlo

    strikePrice = 9
    lastPrice = 10
    actualHistoricalVolatility = 50
    expectedValue = 2.416


class TestAmericanPut(MonteCarloPricerTestCase):

    pricerClass = AmericanMonteCarlo
    isPut = True

    strikePrice = 9
    lastPrice = 10
    actualHistoricalVolatility = 50
    expectedValue = 1.416


class DslTestCase(MonteCarloPricerTestCase):

    pricerClass = DslMonteCarlo
    expectedDelta = None
    expectedGamma = None
    expectedVega = None

    def setUp(self):
        self.pricer = self.pricerClass(
            specification=self.specification,
            image=self.registry.images.get(1)
        )

    def test_calcValue(self):
        if self.expectedExceptionClass:
            self.assertRaises(self.expectedExceptionClass, self.pricer.calcValue)
            return
        # Check option value.
        estimatedValue = self.pricer.calcValue()
        roundedValue = round(estimatedValue, self.DECIMALS)
        expectedValue = round(self.expectedValue, self.DECIMALS)
        msg = "Value: %s  Expected: %s" % (roundedValue, expectedValue)
        self.assertEqual(roundedValue, expectedValue, msg)

        # Find a market.
        markets = self.pricer.getMarkets()
        if not markets:
            return
        market = list(markets)[0]
        # Check option delta.
        estimatedDelta = self.pricer.calcDelta(estimatedValue, market)
        roundedDelta = round(estimatedDelta, self.DECIMALS)
        expectedDelta = round(self.expectedDelta, self.DECIMALS)
        msg = "Value: %s  Expected: %s" % (roundedDelta, expectedDelta)
        self.assertEqual(roundedDelta, expectedDelta, msg)

        # Check option gamma.
        estimatedGamma = self.pricer.calcGamma(estimatedValue, estimatedDelta, market)
        roundedGamma = round(estimatedGamma, self.DECIMALS)
        expectedGamma = round(self.expectedGamma, self.DECIMALS)
        msg = "Value: %s  Expected: %s" % (roundedGamma, expectedGamma)
        self.assertEqual(roundedGamma, expectedGamma, msg)


class TestDslEuropean(DslTestCase):
    specification = """
Settlement(
    Date('2012-03-15'),
    Max(
        Fixing(
            Market('#1'), 
            Date('2012-01-01')
        ) - 9,
        0
    ),
)
"""
    expectedValue = 2.416
    expectedDelta = 0.677
    expectedGamma = 0.07


class TestDslFutures(DslTestCase):
    specification = """
Settlement(
    Date('2012-03-15'),
    Fixing(
        Market('#1'), 
        Date('2012-01-01')
    ) - 9,
)
"""
    expectedValue = 1.0
    expectedDelta = 1.0
    expectedGamma = 0.0


class TestDslAddition(DslTestCase):
    specification = """
Settlement(
    Date('2012-03-15'),
    Fixing(
        Market('#1'), 
        Date('2012-01-01')
    ) - 9,
) + Settlement(
    Date('2012-03-15'),
    Max(
        Fixing(
            Market('#1'), 
            Date('2012-01-01')
        ) - 9,
        0
    ),
)
"""
    expectedValue = 3.416
    expectedDelta = 1.677
    expectedGamma = 0.07


class TestDslBrokenRoot(DslTestCase):
    expectedExceptionClass = DslSourceError 
    specification = """
Date('2012-03-15')
"""


class TestDslBrokenDateIsNotValue(DslTestCase):
    expectedExceptionClass = DslSourceError 
    specification = """
Settlement(
    Date('2012-03-15'),
    Max(
        Fixing(
            Market('#1'), 
            Date('2012-01-01')
        ) - 9,
        Date('2001-01-01')
    ),
)
"""

class TestDslBrokenUnbalancedMax(DslTestCase):
    expectedExceptionClass = DslProgrammingError 
    specification = """
Settlement(
    Date('2012-03-15'),
    Max(
        Fixing(
            Market('#1'), 
            Date('2012-01-01')
        ) - 9,
        Fixing(
            Market('#1'), 
            Date('2012-01-01')
        ) - 9
    ),
)
"""

