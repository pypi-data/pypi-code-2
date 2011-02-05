from quant.pricer.base import AbstractOptionPricer
from scipy import exp, sqrt

class AbstractBinomialTreePricer(AbstractOptionPricer):

    # Todo: Fix american (it's the same as european at the moment).
    # Todo: Encapsulate and test the time divisions.
    # Todo: Encapsulate and test the payoff functions.

    stepCount = 300

    def calcPrice(self):
        self.stepDurationYears = self.calcStepDurationYears()
        self.stepUpFactor = self.calcStepUpFactor()
        self.stepUpProbability = self.calcUpProbability()
        self.stepDiscountFactor = self.calcStepDiscountFactor()
        return self.calcOptionValue()

    def calcStepDurationYears(self):
        T = self.getOptionDurationYears()
        return T / self.stepCount

    def calcStepUpFactor(self):
        sigma = float(self.annualisedVolatility) / 100
        t = self.stepDurationYears
        return exp(sigma * sqrt(t))

    def calcUpProbability(self):
        u = self.stepUpFactor
        return (u - 1)/(u**2 - 1)

    def calcStepDiscountFactor(self):
        r = float(self.annualRiskFreeRate) / 100
        t = self.stepDurationYears
        return exp(r * t)

    def calcOptionValue(self):
        laterNodes = None
        for stepIndex in range(self.stepCount, -1, -1):
            nodeCount = stepIndex + 1
            earlierNodes = [None] * (nodeCount)
            for nodeIndex in range(0, nodeCount):
                netUps = 2 * nodeIndex - stepIndex
                if laterNodes == None:
                    # Option value is exercise value.
                    optionValue = self.calcExerciseValue(netUps)
                else:
                    # Option value is max of exercise value and binomial value.
                    continuationValue = self.calcContinuationValue(laterNodes, nodeIndex)
                    if not self.isExercisableAt(stepIndex):
                        optionValue = continuationValue
                    else:
                        exerciseValue = self.calcExerciseValue(netUps)
                        optionValue = max(continuationValue, exerciseValue)
                earlierNodes[nodeIndex] = optionValue
            laterNodes = earlierNodes
        return laterNodes[0]

    def calcContinuationValue(self, laterNodes, nodeIndex):
        upValue = laterNodes[nodeIndex+1]
        downValue = laterNodes[nodeIndex]
        expectedValue = self.stepUpProbability * upValue
        expectedValue += (1 - self.stepUpProbability) * downValue
        return self.stepDiscountFactor * expectedValue

    def calcExerciseValue(self, netUps):
        underlyingValue = self.calcUnderlyingValue(netUps)
        return self.calcPayoff(underlyingValue, self.strikePrice)

    def calcUnderlyingValue(self, netUps):
        u = self.stepUpFactor
        x = netUps
        S = self.currentPrice
        return u**x * S

    def calcPayoff(self, underlyingValue, strikePrice):
        S = underlyingValue
        K = strikePrice
        if not self.isPut:
            return max(S - K, 0)
        else:
            return max(K - S, 0)

    def isExercisableAt(self, stepIndex):
        raise Exception, "Method not implemented on %s" % self.__class__.__name__


class AmericanBinomialTreePricer(AbstractBinomialTreePricer):

    def isExercisableAt(self, stepIndex):
        return stepIndex == self.stepCount


class EuropeanBinomialTreePricer(AbstractBinomialTreePricer):

    def isExercisableAt(self, stepIndex):
        return stepIndex == self.stepCount

