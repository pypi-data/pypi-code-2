from quant.dom.base import SimpleObject
from quant.dom.base import SimpleNamedObject
from quant.dom.base import String
from quant.dom.base import Date
from quant.dom.base import AggregatesMany
from quant.dom.base import HasMany
from quant.dom.base import HasA
from quant.dom.base import Float
from quant.dom.base import DateTime
import datetime
import dateutil.parser

class Model(SimpleObject):

    title = String()
    images = HasMany('Image', key='id')
    books = HasMany('Book', key='id')

    def getLabelValue(self):
        return self.title or self.id

    def delete(self):
        for image in self.images:
            image.market = None
            image.save()
        super(Model, self).delete()


class DeliveryPeriod(SimpleObject):

    date = Date()
    sortOnName = 'date'
    symbol = HasA('Symbol', isRequired=True)
    # Todo: Make this into history of "current" prices.
    currentPrice = Float(isRequired=True)
    resultLines = HasMany('ResultLine', key='id')
    metrics = AggregatesMany('Metric', key='id')

    def getLabelValue(self):
        dateLabel = self.meta.getAttr('date').createLabelRepr(self)
        return self.symbol.getLabelValue() + ' ' + dateLabel

    def getCurrentPrice(self, observationTime):
        # Todo: Look up effective value at observation time.
        return self.currentPrice

    def getPriceHistory(self, observationTime):
        # Todo: Return times and prices.
        return [self.currentPrice]


class Image(SimpleObject):

    isUnique = False
    observationTime = DateTime()
    sortOnName = 'observationTime'
    model = HasA('Model', isRequired=True)
    results = HasMany('Result', key='id', isEditable=False)
    metrics = AggregatesMany('Metric', key='id')

    def getLabelValue(self):
        return "%s at %s" % (self.model.getLabelValue(), self.meta.attributeNames['observationTime'].createLabelRepr(self))

    def getMetricValue(self, metricName, deliveryPeriod):
        metrics = self.metrics.findDomainObjects(metricName=metricName, deliveryPeriod=deliveryPeriod)
        if len(metrics) > 1:
            raise Exception, "There are %s values for metric '%s' and deliveryPeriod '%s'." % (len(metrics), metricName, deliveryPeriod)
        elif len(metrics) == 1:
            metricValue = metrics[0].metricValue
        else:
            metricValue = self.deriveMetricValue(metricName=metricName, deliveryPeriod=deliveryPeriod)
            self.metrics.create(metricValue=metricValue, metricName=metricName, deliveryPeriod=deliveryPeriod)
        return metricValue

    def deriveMetricValue(self, metricName, deliveryPeriod):
        if metricName == 'current-price':
            value = deliveryPeriod.getCurrentPrice(observationTime=self.observationTime)
        elif metricName == 'annualised-volatility':
            priceHistory = deliveryPeriod.getPriceHistory(observationTime=self.observationTime)
            value = self.calcAnnualisedVolatility(priceHistory)
        else:  
            raise Exception, "Market metric name '%s' not supported." % (metricName)
        return value

    def calcAnnualisedVolatility(self, priceHistory):
       return 50

    def delete(self):
        for result in self.results:
            result.image = None
            result.save()
        super(Image, self).delete()


class Symbol(SimpleNamedObject):

    deliveryPeriods = AggregatesMany('DeliveryPeriod', key='id')


class Metric(SimpleObject):

    isUnique = False
    sortOnName = 'id'

    image = HasA('Image')
    deliveryPeriod = HasA('DeliveryPeriod')
    metricName = String()
    metricValue = Float()

