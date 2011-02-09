from dm.dom.stateful import *
from quant.dom.results import *

class DerivativesContract(DatedStatefulObject):

    title = String()
    deliveryPeriod = HasA('DeliveryPeriod', isRequired=True)
    isPut = Boolean(default=False)
    strikePrice = Float(isRequired=True)
    volume = Float(isRequired=True)
    expiryTime = Date(isRequired=True)
    book = HasA("Book", isRequired=False)

    pricerClass = None

    def getLabelValue(self):
        return self.title or self.id

    def calcResults(self, image):
        contractResults = ContractResults()
        contractValue = self.volume * self.estimateUnitValue(image=image)
        contractDelta = 1.0
        contractGamma = 1.0
        contractVega = 1.0
        self.addResultsLine(contractResults, ContractResults.PRESENT_VALUE_METRIC, contractValue)
        self.addResultsLine(contractResults, ContractResults.DELTA_METRIC, contractDelta)
        self.addResultsLine(contractResults, ContractResults.GAMMA_METRIC, contractGamma)
        self.addResultsLine(contractResults, ContractResults.VEGA_METRIC, contractVega)
        return contractResults

    def addResultsLine(self, results, metricName, metricValue):
        results.addResultsLine(
            contract=self,
            deliveryPeriod = self.deliveryPeriod,
            pricerType = self.getPricerClass().__name__,
            metricName = metricName,
            metricValue = metricValue
        )

    def estimateUnitValue(self, image):
        currentPrice = image.getMetricValue('current-price', self.deliveryPeriod)
        annualisedVolatility = image.getMetricValue('annualised-volatility', self.deliveryPeriod)
        nowTime = image.observationTime
        pricer = self.pricerClass(
            isPut=self.isPut,
            strikePrice=self.strikePrice,
            currentPrice=currentPrice,
            annualisedVolatility=annualisedVolatility,
            nowTime=nowTime,
            expiryTime=self.expiryTime,
        )
        return pricer.calcPrice()

    def getPricerClass(self):
        return self.pricerClass


class AbstractResults(object):

    PRESENT_VALUE_METRIC = 'value'
    DELTA_METRIC = 'delta'
    GAMMA_METRIC = 'gama'
    VEGA_METRIC = 'vega'


class ContractResults(AbstractResults):

    def __init__(self):
        self.resultLines = []

    def addResultsLine(self, contract, deliveryPeriod, pricerType, metricName, metricValue):
        self.resultLines.append({
            'contract': contract,
            'deliveryPeriod': deliveryPeriod,
            'pricerType': pricerType,
            'metricName': metricName,
            'metricValue': metricValue,
        })




# todo: Rename PersonExtn as Person
# todo: Rename Person as User
class PersonExtn(DatedStatefulObject):

    realname = String()
    email = String('')
    user = HasA('Person', isRequired=False, default=None)

    searchAttributeNames = ['realname']
    startsWithAttributeName = 'realname'

    def getLabelValue(self):
        return self.realname or self.id


