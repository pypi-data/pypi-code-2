from quant.dom.base import DerivativesContract

class ForwardContract(DerivativesContract):

    def estimateUnitValue(self):
        return self.market.getCurrentPrice(self.expiryTime)


