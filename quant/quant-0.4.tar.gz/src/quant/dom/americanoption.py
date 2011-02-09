from quant.dom.base import DerivativesContract, HasA
from quant.pricer.binomialtree import AmericanBinomialTreePricer
from quant.pricer.montecarlo import AmericanMonteCarloPricer

class American(DerivativesContract):

    pricerClass = AmericanBinomialTreePricer

