from quant.pricer.base import AbstractOptionPricer
import scipy
from scipy import exp, sqrt

class AbstractMonteCarloPricer(AbstractOptionPricer):

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
        sigma_root_T = sigma * sqrt(T)
        sigma_squared_T = sigma**2 * T
        return self.lastPrice * exp(sigma_root_T * draws - 0.5 * sigma_squared_T)

    def calcPayoffs(self, underlyings):
        if self.isPut:
            differences = self.strikePrice - underlyings
        else:
            differences = underlyings - self.strikePrice
        return (differences > 0) * differences


class AmericanMonteCarloPricer(AbstractMonteCarloPricer):
    pass

class EuropeanMonteCarloPricer(AbstractMonteCarloPricer):
    pass

