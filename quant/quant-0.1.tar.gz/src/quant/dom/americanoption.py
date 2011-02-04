from quant.dom.base import DerivativesContract, HasA
from quant.pricer.binomialtree import AmericanBinomialTreePricer
from quant.pricer.montecarlo import AmericanMonteCarloPricer

class AmericanOption(DerivativesContract):

    pricerClass = AmericanBinomialTreePricer

