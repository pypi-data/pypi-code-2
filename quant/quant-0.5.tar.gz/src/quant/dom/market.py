from quant.dom.base import StandardObject
from quant.dom.base import SimpleObject
from quant.dom.base import SimpleNamedObject
from quant.dom.base import DatedStatefulObject
from quant.dom.base import String
from quant.dom.base import Text 
from quant.dom.base import Date
from quant.dom.base import AggregatesMany
from quant.dom.base import HasMany
from quant.dom.base import HasA
from quant.dom.base import Float
from quant.dom.base import DateTime
from quant.dom.base import Boolean
import datetime
import dateutil.parser
import scipy
import math

class Exchange(SimpleNamedObject):

    symbols = AggregatesMany('Symbol', key='name', ownerName='exchange')
    holidays = Text()


class Symbol(SimpleNamedObject):

    markets = AggregatesMany('Market', key='id')
    exchange = HasA('Exchange', isRequired=True, isSimpleOption=True)


class Market(SimpleObject):

    monthLetters = ['F', 'G', 'H', 'J', 'K', 'M', 'N', 'Q', 'U', 'V', 'X', 'Z']

    isTemporal = True

    firstDeliveryDate = Date()
    expiration = Date()
    sortOnName = 'firstDeliveryDate'
    symbol = HasA('Symbol', isRequired=True)
    lastPrice = Float(isTemporal=True, isRequired=True)
    metrics = AggregatesMany('Metric', key='id')

    def getLabelValue(self):
        monthIndex = self.firstDeliveryDate.month - 1
        monthLetter = self.monthLetters[monthIndex]
        yearAbbr = str(self.firstDeliveryDate.year)[2:]
        return self.symbol.getLabelValue() + '.' + monthLetter + yearAbbr

    def getLastPrice(self, observationTime):
        # Todo: Look up effective value at observation time.
        return self.lastPrice

    def getPriceHistory(self, observationTime):
        # Todo: Return history only until observation time.
        return ([i for i in self.temporalHistory])


class PriceProcess(DatedStatefulObject):

    package = String()
    name = String()
    

class Image(SimpleObject):

    isUnique = False
    sortOnName = 'id'
    sortAscending = False
    observationTime = DateTime()
    priceProcess = HasA('PriceProcess', isRequired=True)
    results = AggregatesMany('Result', key='id')
    metrics = AggregatesMany('Metric', key='id')

    def getLabelValue(self):
        return "#%s: %s at %s" % (self.id, self.priceProcess.codeClassName, self.meta.attributeNames['observationTime'].createLabelRepr(self))

    def getMetricValue(self, metricName, market):
        metrics = self.metrics.findDomainObjects(metricName=metricName, market=market)
        if len(metrics) > 1:
            raise Exception, "There are %s values for metric '%s' and market '%s'." % (len(metrics), metricName, market)
        elif len(metrics) == 1:
            metricValue = metrics[0].metricValue
        else:
            metricValue = self.deriveMetricValue(metricName=metricName, market=market)
            self.metrics.create(metricValue=metricValue, metricName=metricName, market=market)
        return metricValue

    def deriveMetricValue(self, metricName, market):
        if metricName == 'last-price':
            value = market.getLastPrice(observationTime=self.observationTime)
        elif metricName == 'actual-historical-volatility':
            priceHistory = market.getPriceHistory(observationTime=self.observationTime)
            value = self.priceProcess.calcActualHistoricalVolatility(priceHistory)
        else:  
            raise Exception, "Market metric name '%s' not supported." % (metricName)
        return value


class Metric(SimpleObject):

    isUnique = False
    sortOnName = 'id'

    image = HasA('Image')
    market = HasA('Market')
    metricName = String()
    metricValue = Float()

