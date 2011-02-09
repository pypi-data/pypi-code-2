from scipy.stats import norm
from scipy import integrate
from scipy import exp, log, sqrt, pi
from math import sqrt
import dateutil.parser
from quant.stats import NormalDistribution
from quant.pricer.base import AbstractOptionPricer

class EuropeanBlackScholesPricer(AbstractOptionPricer):

    def calcPrice(self):
        S = float(self.currentPrice)
        K = float(self.strikePrice)
        r = float(self.annualRiskFreeRate) / 100.0
        t = float(self.getOptionDurationYears())
        sigma = float(self.annualisedVolatility) / 100.0
        sigma_squared_t = sigma**2 * t
        try:
            sigma_root_t = sigma * sqrt(t)
        except Exception, inst:
            msg = "Couldn't sqrt: %s: %s" % (t, inst)
            raise Exception, msg
        d1 = (log(S / K) + t * r + 0.5 * sigma_squared_t) / sigma_root_t
        d2 = d1 - sigma_root_t
        Nd1 = self.N(d1)
        Nd2 = self.N(d2)
        e_to_minus_rt = exp(-1.0 * r * t)
        if self.isPut:
            # Put option.
            optionValue = (1-Nd2)*K*e_to_minus_rt - (1-Nd1)*S
        else:
            # Call option.
            optionValue = Nd1*S - Nd2*K*e_to_minus_rt
        return optionValue

    def N(self, d):
        return self.getNormalDistribution().cdf(d)

