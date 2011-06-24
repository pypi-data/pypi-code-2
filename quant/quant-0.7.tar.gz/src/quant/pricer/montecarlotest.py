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
        unittest.makeSuite(TestDslMarket),
        unittest.makeSuite(TestDslFixing),
        unittest.makeSuite(TestDslWait),
        unittest.makeSuite(TestDslSettlement),
        unittest.makeSuite(TestDslChoice),
        unittest.makeSuite(TestDslMax),
        unittest.makeSuite(TestDslAdd),
        unittest.makeSuite(TestDslSubtract),
        unittest.makeSuite(TestDslMultiply),
        unittest.makeSuite(TestDslDivide),
        unittest.makeSuite(TestDslIdenticalFixings),
        unittest.makeSuite(TestDslBrownianIncrements),
        unittest.makeSuite(TestDslUncorrelatedMarkets),
        unittest.makeSuite(TestDslFutures),
        unittest.makeSuite(TestDslEuropean),
        unittest.makeSuite(TestDslBermudan),
        unittest.makeSuite(TestDslSumContracts),
        unittest.makeSuite(TestDslAddition),
        unittest.makeSuite(TestDslErrorDateIsNotStatement),
        unittest.makeSuite(TestDslErrorDateIsNotExpression),
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

    toleranceValue = 0.02
    toleranceDelta = 0.1
    toleranceGamma = 0.1

    def setUp(self):
        self.pricer = self.pricerClass(
            specification=self.specification,
            image=self.registry.images.get(1)
        )

    def assertTolerance(self, estimated, expected, tolerance):
        upper = expected + tolerance
        lower = expected - tolerance
        assert lower <= estimated <= upper, "Estimated '%s' not close enough to expected '%s' (tolerance '%s')." % (estimated, expected, tolerance)

    def test_pricer(self):
        if self.expectedExceptionClass:
            self.assertRaises(self.expectedExceptionClass, self.pricer.calcValue)
            return
        # Check option value.
        estimatedValue = self.pricer.calcValue()
        self.assertTolerance(estimatedValue, self.expectedValue, self.toleranceValue)

        # Find a market.
        markets = self.pricer.getMarkets()
        if not markets:
            return
        market = list(markets)[0]
        # Check option delta.
        estimatedDelta = self.pricer.calcDelta(market)
        self.assertTolerance(estimatedDelta, self.expectedDelta, self.toleranceDelta)

        # Todo: Decide what to do with gamma (too much noise to pass tests).
        # Check option gamma.
        #estimatedGamma = self.pricer.calcGamma(market)
        #roundedGamma = round(estimatedGamma, self.DECIMALS)
        #expectedGamma = round(self.expectedGamma, self.DECIMALS)
        #msg = "Value: %s  Expected: %s" % (roundedGamma, expectedGamma)
        #self.assertEqual(roundedGamma, expectedGamma, msg)


class TestDslMarket(DslTestCase):
    specification = "Market('#1')"
    expectedValue = 10.0
    expectedDelta = 1.0
    expectedGamma = 0


class TestDslFixing(DslTestCase):
    specification = "Fixing(Date('2012-01-01'), Market('#1'))"
    expectedValue = 10.0
    expectedDelta = 1.0
    expectedGamma = 0


class TestDslWait(DslTestCase):
    specification = "Wait(Date('2012-01-01'), Market('#1'))"
    expectedValue = 9.753
    expectedDelta = 0.975
    expectedGamma = 0


class TestDslSettlement(DslTestCase):
    specification = "Settlement(Date('2012-01-01'), Market('#1'))"
    expectedValue = 9.753
    expectedDelta = 0.975
    expectedGamma = 0


class TestDslChoice(DslTestCase):
    specification = "Fixing(Date('2012-01-01'), Choice( Market('#1') - 9, 0))"
    expectedValue = 2.416
    expectedDelta = 0.677
    expectedGamma = 0.07


class TestDslMax(DslTestCase):
    specification = "Fixing(Date('2012-01-01'), Max(Market('#1'), Market('#2')))"
    expectedValue = 12.756
    expectedDelta = 0.636
    expectedGamma = 0


class TestDslAdd(DslTestCase):
    specification = "Market('#1') + Market('#2')"
    expectedValue = 20.0
    expectedDelta = 1
    expectedGamma = 0


class TestDslSubtract(DslTestCase):
    specification = "Market('#1') - 10"
    expectedValue = 0.0
    expectedDelta = 1
    expectedGamma = 0


class TestDslMultiply(DslTestCase):
    specification = "Market('#1') * Market('#2')"
    expectedValue = 100.0
    expectedDelta = 10.0
    expectedGamma = 0


class TestDslDivide(DslTestCase):
    specification = "Market('#1') / 10"
    expectedValue = 1.0
    expectedDelta = 0.1
    expectedGamma = 0


class TestDslIdenticalFixings(DslTestCase):
    specification = """
Fixing(Date('2012-01-01'), Market('#1')) - Fixing(Date('2012-01-01'), Market('#1'))
"""
    expectedValue = 0
    expectedDelta = 0
    expectedGamma = 0


class TestDslBrownianIncrements(DslTestCase):
    specification = """
Wait(
    Date('2012-03-15'),
    Max(
        Fixing(
            Market('#1'), 
            Date('2012-01-01')
        ) /
        Fixing(
            Market('#1'),
            Date('2011-01-01')
        ),
        1.0
    ) -
    Max(
        Fixing(
            Market('#1'), 
            Date('2013-01-01')
        ) /
        Fixing(
            Market('#1'),
            Date('2012-01-01')
        ),
        1.0
    )
)"""
    expectedValue = 0
    expectedDelta = 0
    expectedGamma = 0


class TestDslUncorrelatedMarkets(DslTestCase):
    specification = """
Max(
    Fixing(
        Date('2012-01-01'),
        Market('#1')
    ) *
    Fixing(
        Date('2012-01-01'),
        Market('#2')
    ) / 10,
    0.0
) - Max(
    Fixing(
        Date('2013-01-01'),
        Market('#1')
    ), 0
)"""
    expectedValue = 0
    # Todo: Figure out why the delta sometimes evaluates to 1 for a period of time and then
    # reverts back to evaluating to 0.
    expectedDelta = 0
    expectedGamma = 0

    toleranceValue = 0.04
    toleranceDelta = 0.2
    toleranceGamma = 0.2


class TestDslFutures(DslTestCase):
    specification = """
Wait( Date('2012-01-01'),
    Market('#1') - 9
) """
    expectedValue = 0.9753
    expectedDelta = 0.9753
    expectedGamma = 0.0


class TestDslEuropean(DslTestCase):
    specification = "Wait(Date('2012-01-01'), Choice(Market('#1') - 9, 0))"
    expectedValue = 2.356
    expectedDelta = 0.660
    expectedGamma = 0.068


class TestDslBermudan(DslTestCase):
    specification = """
Fixing( Date('2011-06-01'), Choice( Market('#1') - 9,
    Fixing( Date('2012-01-01'), Choice( Market('#1') - 9, 0))
))
"""
    expectedValue = 2.416
    expectedDelta = 0.677
    expectedGamma = 0.07


class TestDslSumContracts(DslTestCase):
    specification = """
Fixing(
    Date('2011-06-01'),
    Choice(
        Market('#1') - 9,
        Fixing(
            Date('2012-01-01'),
            Choice(
                Market('#1') - 9,
                0
            )
        )
    )
) + Fixing(
    Date('2011-06-01'),
    Choice(
        Market('#1') - 9,
        Fixing(
            Date('2012-01-01'),
            Choice(
                Market('#1') - 9,
                0
            )
        )
    )
)
"""
    expectedValue = 2.416 + 2.416
    expectedDelta = 0.677 + 0.677
    expectedGamma = 0.07 + 0.07

    toleranceValue = 0.04
    toleranceDelta = 0.2
    toleranceGamma = 0.2


class TestDslAddition(DslTestCase):
    specification = """
Fixing( Date('2012-01-01'),
    Max(Market('#1') - 9, 0) + Market('#1') - 9 
)
"""
    expectedValue = 3.416
    expectedDelta = 1.677
    expectedGamma = 0.07

    toleranceValue = 0.04
    toleranceDelta = 0.2
    toleranceGamma = 0.2


class TestDslErrorDateIsNotStatement(DslTestCase):
    expectedExceptionClass = DslSourceError 
    specification = "Date('2012-03-15')"


class TestDslErrorDateIsNotExpression(DslTestCase):
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

