from quant.dom.base import SimpleObject, String

class Pricer(SimpleObject):

    pricerModuleName = String()
    pricerClassName = String()

    title = String()

    def getLabelValue(self):
        return self.title or self.id

