from scipy.stats import norm
from scipy import integrate
from scipy import exp, log, sqrt, pi
from math import sqrt
from quant.exceptions import PricerLimitError
import dateutil.parser
from quant.stats import NormalDistribution
from quant.stats import LogNormalDistribution

class AbstractOptionPricer(object):

    daysPerYear = 365  # Assume day-count convention: Actual/365 Fixed.

    def __init__(self, strikePrice, currentPrice, annualisedVolatility, nowTime, expiryTime, isPut=False, annualRiskFreeRate=0.0, tolerance=1e-9):
        self.strikePrice = strikePrice
        self.currentPrice = currentPrice
        self.setAnnualisedVolatility(annualisedVolatility)
        self.nowTime = nowTime
        self.expiryTime = expiryTime
        self.isPut = isPut
        self.annualRiskFreeRate = annualRiskFreeRate
        self.tolerance = tolerance

    def setAnnualisedVolatility(self, annualisedVolatility):
        self.annualisedVolatility = annualisedVolatility

    def calcPrice(self):
        raise Exception, "Method not implemented."

    def scaleVolatility(self, durationYears):
        sigma = self.annualisedVolatility / 100.0
        return sigma * sqrt(durationYears)

    def getOptionDurationYears(self):
        optionDurationDays = self.getOptionDuration().days
        return float(optionDurationDays) / self.daysPerYear

    def getOptionDuration(self):
        return self.expiryTime - self.nowTime

    def getNormalDistribution(self):
        if not hasattr(self, 'normalDistribution'):
            self.normalDistribution = NormalDistribution()
        return self.normalDistribution


class AbstractIntegralLimits(object):

    def getIntegralUpperLimit(self):
        raise Exception, "Method not implemented."

    def getIntegralLowerLimit(self):
        raise Exception, "Method not implemented."


class CallIntegralLimits(AbstractIntegralLimits):

    def getIntegralLowerLimit(self):
        highPercentile = self.currentPrice + self.INTEGRAL_WIDTH * self.annualisedVolatility
        lowPercentile = self.currentPrice - self.INTEGRAL_WIDTH * self.annualisedVolatility
        if self.strikePrice < lowPercentile:
            lowerLimit = lowPercentile
        elif self.strikePrice > highPercentile:
            lowerLimit = highPercentile
        else:
            lowerLimit = self.strikePrice
        return lowerLimit

    def getIntegralUpperLimit(self):
        highPercentile = self.currentPrice + self.INTEGRAL_WIDTH * self.annualisedVolatility
        upperLimit = highPercentile
        return upperLimit


class PutIntegralLimits(AbstractIntegralLimits):

    def getIntegralLowerLimit(self):
        lowPercentile = self.currentPrice - self.INTEGRAL_WIDTH * self.annualisedVolatility
        lowerLimit = lowPercentile
        # Todo: Use a log-normal distribution rather than normal distribution to avoid negative integral limit errors.
        if lowerLimit < 0:
            msg = "Given current price (%f) the annualisedVolatility (%f) is too high to value European Put Option with price movements based on the normal distribution." % (self.currentPrice, self.annualisedVolatility)
            raise PricerLimitError, msg
        return lowerLimit

    def getIntegralUpperLimit(self):
        highPercentile = self.currentPrice + self.INTEGRAL_WIDTH * self.annualisedVolatility
        lowPercentile = self.currentPrice - self.INTEGRAL_WIDTH * self.annualisedVolatility
        if self.strikePrice < lowPercentile:
            upperLimit = lowPercentile
        elif self.strikePrice > highPercentile:
            upperLimit = highPercentile
        else:
            upperLimit = self.strikePrice
        return upperLimit


class WienerPricer(AbstractOptionPricer, AbstractIntegralLimits):

    VOLATILITY_LIMIT_INFINITESIMAL = 0.000000001
    INTEGRAL_WIDTH = 7

    def setAnnualisedVolatility(self, annualisedVolatility):
        value = annualisedVolatility
        limit = self.VOLATILITY_LIMIT_INFINITESIMAL
        self.annualisedVolatility = abs(value) > limit and value or limit

    def calcPrice(self):
        raise Exception, "Balh"
        integralLowerLimit = self.getIntegralLowerLimit()
        integralUpperLimit = self.getIntegralUpperLimit()
        self.optionDurationVolatility = self.getOptionDurationVolatility()
        if integralLowerLimit < 0:
            raise PricerLimitError, "Integral lower limit is negative: %s" % integralLowerLimit
        if integralUpperLimit < 0:
            raise PricerLimitError, "Integral upper limit is negative: %s" % integralUpperLimit
        integral = integrate.quadrature(
            func=self.payoffDensity,
            a=integralLowerLimit,
            b=integralUpperLimit,
            tol=self.tolerance,
            maxiter=500
        )
        estimate = integral[0]
        absError = integral[1]
        if absError > self.tolerance:
            msg = "Absolute error out of tolerance: %f" % absError
            raise Exception, msg
        return estimate

    def payoffDensity(self, x):
        raise Exception, "Method not implemented."

    def getGaussianDensity(self, x):
        from scipy.stats import norm
        return self.normPdf(x)

    def getProbabilityDensity(self, x):
        pdf = self.getProbabilityDensityFunction()
        return pdf(x)

    def getProbabilityDensityFunction(self):
        if not hasattr(self, 'probabilityDensityFunction'):
            self.probabilityDensityFunction = self.createProbabilityDensityFunction()
        return self.probabilityDensityFunction
    
    def createProbabilityDensityFunction(self):
        distribution = LogNormalDistribution(
            mean=self.currentPrice, 
            variance=self.optionDurationVolatility**2,
        )
        return distribution.pdf

    def normPdf(self, x):
        return norm.pdf(x, loc=self.currentPrice, scale=self.optionDurationVolatility)

    def getOptionDurationVolatility(self):
        optionDurationDays = self.getOptionDuration().days
        annualDurationDays = 365.0
        optionDurationYears = self.getOptionDurationYears()
        optionDurationVolatility = self.scaleVolatility(optionDurationYears)
        return optionDurationVolatility


