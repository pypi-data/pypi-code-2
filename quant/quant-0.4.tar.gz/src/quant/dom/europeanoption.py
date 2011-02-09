from quant.dom.base import DerivativesContract, HasA
from quant.pricer.blackscholes import EuropeanBlackScholesPricer

class European(DerivativesContract):

    pricerClass = EuropeanBlackScholesPricer
