from quant.dom.base import SimpleObject, String

class Market(SimpleObject):

    title = String()
    name = String()
    dataService = String()

    def getLabelValue(self):
        return self.title or self.id

    def getCurrentPrice(self, *args, **kwds):
        return self.market.getCurrentPrice(*args, **kwds)

    def getAnnualisedVolatility(self, *args, **kwds):
        return self.market.getAnnualisedVolatility(*args, **kwds)

    def getNowTime(self):
        return self.market.getNowTime()

    def getMarket(self):
        if not hasattr(self, '_market'):
            from quant.market import MarketData
            self._market = MarketData(
                dataService=self.dataService,
                name=self.name,
            )
        return self._market

    market = property(getMarket)


