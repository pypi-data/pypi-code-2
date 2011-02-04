from quant.dom.base import DerivativesContract, HasA
from quant.pricer.blackscholes import BlackScholesPricer

class EuropeanOption(DerivativesContract):

    pricerClass = BlackScholesPricer
