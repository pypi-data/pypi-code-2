from quant.stats import NormalDistribution
import scipy
import math

class Pricer(object):

    def __init__(self):
        pass

    def calcPrice(self):
        raise Exception, "Method not implemented."


class DerivativePricer(Pricer):

    daysPerYear = 365  # Assumes "Actual/365 Fixed" day-count convention.

    def __init__(self, strikePrice, lastPrice, actualHistoricalVolatility, nowTime, expiration, isPut=False, annualRiskFreeRate=0.0, tolerance=1e-9):
        self.strikePrice = strikePrice
        self.lastPrice = lastPrice
        self.actualHistoricalVolatility = actualHistoricalVolatility
        self.nowTime = nowTime
        self.expiration = expiration
        self.isPut = isPut
        self.annualRiskFreeRate = annualRiskFreeRate
        self.tolerance = tolerance

    def getOptionDurationYears(self):
        optionDurationDays = self.getOptionDuration().days
        return float(optionDurationDays) / self.daysPerYear

    def getOptionDuration(self):
        return self.expiration - self.nowTime

    def getNormalDistribution(self):
        if not hasattr(self, 'normalDistribution'):
            self.normalDistribution = NormalDistribution()
        return self.normalDistribution


class EuropeanBlackScholes(DerivativePricer):

    def calcPrice(self):
        S = float(self.lastPrice)
        K = float(self.strikePrice)
        r = float(self.annualRiskFreeRate) / 100.0
        t = float(self.getOptionDurationYears())
        sigma = float(self.actualHistoricalVolatility) / 100.0
        sigma_squared_t = sigma**2 * t
        try:
            sigma_root_t = sigma * math.sqrt(t)
        except Exception, inst:
            msg = "Couldn't sqrt: %s: %s" % (t, inst)
            raise Exception, msg
        d1 = (math.log(S / K) + t * r + 0.5 * sigma_squared_t) / sigma_root_t
        d2 = d1 - sigma_root_t
        Nd1 = self.N(d1)
        Nd2 = self.N(d2)
        e_to_minus_rt = math.exp(-1.0 * r * t)
        if self.isPut:
            # Put option.
            optionValue = (1-Nd2)*K*e_to_minus_rt - (1-Nd1)*S
        else:
            # Call option.
            optionValue = Nd1*S - Nd2*K*e_to_minus_rt
        return optionValue

    def N(self, d):
        return self.getNormalDistribution().cdf(d)


class BinomialTree(DerivativePricer):

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
        sigma = float(self.actualHistoricalVolatility) / 100
        t = self.stepDurationYears
        return scipy.exp(sigma * scipy.sqrt(t))

    def calcUpProbability(self):
        u = self.stepUpFactor
        return (u - 1)/(u**2 - 1)

    def calcStepDiscountFactor(self):
        r = float(self.annualRiskFreeRate) / 100
        t = self.stepDurationYears
        return scipy.exp(r * t)

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
        S = self.lastPrice
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


class AmericanBinomialTree(BinomialTree):

    def isExercisableAt(self, stepIndex):
        return True


class EuropeanBinomialTree(BinomialTree):

    def isExercisableAt(self, stepIndex):
        return stepIndex == self.stepCount


class MonteCarlo(DerivativePricer):

    pathCount = 500000

    def calcPrice(self):
        draws = self.calcDraws()
        underlyings = self.calcUnderlyings(draws)
        payoffs = self.calcPayoffs(underlyings)
        return payoffs.mean()
        
    def calcDraws(self):
        return scipy.random.standard_normal(self.pathCount)

    def calcUnderlyings(self, draws):
        T = self.getOptionDurationYears()
        sigma = float(self.actualHistoricalVolatility) / 100
        sigma_root_T = sigma * scipy.sqrt(T)
        sigma_squared_T = sigma**2 * T
        return self.lastPrice * scipy.exp(sigma_root_T * draws - 0.5 * sigma_squared_T)

    def calcPayoffs(self, underlyings):
        if self.isPut:
            differences = self.strikePrice - underlyings
        else:
            differences = underlyings - self.strikePrice
        return (differences > 0) * differences


class EuropeanMonteCarlo(MonteCarlo):

    pass


class AmericanMonteCarlo(MonteCarlo):

    # Todo: Needs L-S routine.
    pass

