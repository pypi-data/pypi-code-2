import unittest
from quant.testunit import TestCase
from quant.leastsquares import LeastSquares
import scipy

def suite():
    suites = [
        unittest.makeSuite(TestLeastSquares),
        unittest.makeSuite(TestLeastSquares2),
    ]
    return unittest.TestSuite(suites)


class LeastSquaresTestCase(TestCase):

    fixtureX = None
    fixtureY = None
    expected = None
    DECIMALS = 12
 
    def setUp(self):
        assert self.fixtureX != None
        assert self.fixtureY != None
        self.fixture = LeastSquares(self.fixtureX, self.fixtureY)

    def testFit(self):
        assert self.expected != None
        fitData = self.fixture.fit()
        for i, expectedValue in enumerate(self.expected):
            fitValue = round(fitData[i], self.DECIMALS)
            msg = "expected value: %s, fit value: %s, expected data: %s, fit data: %s" % (
                expectedValue, fitValue, self.expected, fitData)
            self.assertEqual(expectedValue, fitValue, msg)

class TestLeastSquares(LeastSquaresTestCase):

    fixtureX = [scipy.array([0, 1, 2]), scipy.array([3, 4, 5])]
    fixtureY = scipy.array([1, 1, 1])
    expected = scipy.array([1, 1, 1])


class TestLeastSquares2(LeastSquaresTestCase):

    fixtureX = [scipy.array([0, 1, 2]), scipy.array([3, 4, 5])]
    fixtureY = scipy.array([0, 1, 2])
    expected = scipy.array([0, 1, 2])

