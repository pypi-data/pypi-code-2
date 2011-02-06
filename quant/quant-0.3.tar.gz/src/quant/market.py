class MarketData(object):

    def __init__(self, dataService, name):
        self.dataService = dataService
        self.name = name

    def getCurrentPrice(self, deliveryPeriod):
        return self.getDataService().getCurrentPrice(deliveryPeriod=deliveryPeriod)

    def getAnnualisedVolatility(self, deliveryPeriod=None):
        return self.getDataService().getAnnualisedVolatility(deliveryPeriod=deliveryPeriod)

    def getNowTime(self):
        return self.getDataService().getNowTime()

    def getPeriodsUntil(self, deliveryPeriod):
        return self.getDataService().getPeriodsUntil(deliveryPeriod=deliveryPeriod)

    def getDataService(self):
        if self.dataService == 'test':
            return StubMarketDataService()
        else:
            raise Exception, "Data service not supported: %s" % self.dataService

    def getPriceProcess(self):
        return self.getDataService().getPriceProcess()

class AbstractMarketDataService(object):

    def getCurrentPrice(self, deliveryPeriod):
        raise Exception, "Method not implemented."

    def getAnnualisedVolatility(self, deliveryPeriod=None):
        raise Exception, "Method not implemented."

    def getPriceProcess(self):
        raise Exception, "Method not implemented."
        return self.getDataService().getPriceProcess()

class StubMarketDataService(AbstractMarketDataService):

    data = [
        {
            'deliveryPeriod': '2010-10-06',
            'current': 10,
            'annualisedVolatility': 1,
        },
        {
            'deliveryPeriod': '2010-11-06',
            'current': 12,
            'annualisedVolatility': 1,
        },
        {
            'deliveryPeriod': '2010-12-06',
            'current': 9,
            'annualisedVolatility': 1,
        },
        {
            'deliveryPeriod': '2011-01-06',
            'current': 10,
            'annualisedVolatility': 1,
        },

    ]

    def getItem(self, deliveryPeriod):
        for item in self.data:
            if item['deliveryPeriod'] == deliveryPeriod:
                return item
        msg = "Period not found in data: %s" % deliveryPeriod
        raise Exception, msg

    def getCurrentPrice(self, deliveryPeriod):
        return self.getItem(deliveryPeriod)['current']

    def getAnnualisedVolatility(self, deliveryPeriod=None):
        return 50

    def getNowTime(self):
        return '2010-01-06 00:00:00'

    def getPriceProcess(self):
        return BlackScholesProcess()

class BlackScholesProcess(object):
    pass
