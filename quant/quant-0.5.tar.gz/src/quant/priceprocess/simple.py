import scipy
import math

class PriceProcess(object):

    pass


class SimplePriceProcess(PriceProcess):

    def calcActualHistoricalVolatility(self, priceHistory):
        raise "Method not implemented on %s." % self.__class__


class BlackScholesVolatility(SimplePriceProcess):

    def calcActualHistoricalVolatility(self, priceHistory):
        prices = scipy.array([i.lastPrice for i in priceHistory])
        dates = [i.dateCreated for i in priceHistory]
        volatility = 100 * prices.std() / prices.mean()
        duration = max(dates) - min(dates)
        years = (duration.days) / 365.0 # Assumes zero seconds.
        if years == 0:
            raise Exception, "Can't calculate volatility for price series with zero duration: %s" % (priceHistory)
        return float(volatility) / math.sqrt(years)


class LocalVolatility(SimplePriceProcess): pass

class StochasticVolatilityHeston(SimplePriceProcess): pass

class StochasticVolatilitySABR(SimplePriceProcess): pass


