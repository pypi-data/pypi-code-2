from quant.dom.base import DerivativesContract
#from quant.pricer.binaryoption import BinaryOptionCallPricer

class BinaryOption(DerivativesContract):

    def getPricerClass(self):
        return BinaryOptionCallPricer

