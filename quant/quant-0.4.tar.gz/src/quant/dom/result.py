from quant.dom.base import SimpleObject
from quant.dom.base import SimpleDatedObject
from quant.dom.base import String
from quant.dom.base import AggregatesMany
from quant.dom.base import HasA
from quant.dom.base import Integer
from quant.dom.base import Float
from quant.dom.base import AbstractResults
import datetime
import dateutil.parser

class Result(SimpleDatedObject, AbstractResults):

    isUnique = False

    book = HasA('Book', isEditable=True)
    image = HasA('Image', isEditable=True)
    lines = AggregatesMany('ResultLine', key='id')

    def getLabelValue(self):
        return self.book.getLabelValue() + ' with ' + self.image.getLabelValue()

    def onCreate(self):
        super(Result, self).onCreate()
        self.calcResults()

    def calcResults(self):
        bookResults = BookResults()
        bookResults.evaluationDate = self.image.observationTime
        # Calculate contract results individually.
        for contract in self.book.getContracts():
            contractResults = contract.calcResults(image=self.image)
            bookResults.addContractResults(contractResults)
        # Save the book results.
        for line in bookResults.resultLines:
            self.lines.create(
               contractId=line['contract'].id,
               contractType=line['contract'].meta.name,
               contractRegisterName=line['contract'].getRegistryAttrName(),
               contractLabel=line['contract'].getLabelValue(),
               deliveryPeriod=line['deliveryPeriod'],
               pricerType=line['pricerType'],
               metricName=line['metricName'],
               metricValue=float(line['metricValue']),
            )

    def getTotalValue(self):
        totalValue = 0
        for line in self.lines:
            if line.metricName == self.PRESENT_VALUE_METRIC:
                totalValue += line.metricValue
        return totalValue

    def getContract(self, contractType, contractId):
        contractClass = self.registry.getDomainClass(contractType)
        contractRegister = contractClass.createRegister()
        return contractRegister[contractId]

    def getValuesByContract(self):
        contracts = []
        contractValues = {}
        for line in self.lines:
            metricName = line.metricName
            if metricName == self.PRESENT_VALUE_METRIC:
                contract = self.getContract(line.contractType, line.contractId)
                if contract not in contracts:
                    contracts.append(contract)
                    contractValues[contract.id] = 0
                metricValue = line.metricValue
                contractValues[contract.id] += metricValue
        valuesByContract = [{'contract': c, 'contractValue': contractValues[c.id]} for c in contracts]
        return valuesByContract

    def getGreeksByDeliveryPeriod(self):
        deliveryPeriods = []
        deliveryPeriodDeltas = {}
        deliveryPeriodGammas = {}
        deliveryPeriodVegas = {}
        greeks = [self.DELTA_METRIC, self.GAMMA_METRIC, self.VEGA_METRIC]
        for line in self.lines:
            deliveryPeriod = line.deliveryPeriod
            if deliveryPeriod not in deliveryPeriods:
                deliveryPeriods.append(deliveryPeriod)
                deliveryPeriodDeltas[deliveryPeriod.id] = 0.0
                deliveryPeriodGammas[deliveryPeriod.id] = 0.0
                deliveryPeriodVegas[deliveryPeriod.id] = 0.0
            metricName = line.metricName
            metricValue = line.metricValue
            if metricName == self.DELTA_METRIC:
                deliveryPeriodDeltas[deliveryPeriod.id] += metricValue
            elif metricName == self.GAMMA_METRIC:
                deliveryPeriodGammas[deliveryPeriod.id] += metricValue
            elif metricName == self.VEGA_METRIC:
                deliveryPeriodVegas[deliveryPeriod.id] += metricValue
        greeksByPeriod = [{'deliveryPeriod': p, 'delta': deliveryPeriodDeltas[p.id], 'gamma': deliveryPeriodGammas[p.id], 'vega': deliveryPeriodVegas[p.id]} for p in deliveryPeriods]
        return greeksByPeriod


class ResultLine(SimpleObject):

    isUnique = False
    sortOnName = 'id'

    result = HasA('Result')
    deliveryPeriod = HasA('DeliveryPeriod')
    contractId = Integer()
    contractType = String()
    contractRegisterName = String()
    contractLabel = String()
    pricerType = String()
    metricName = String()
    metricValue = Float()

    def getContract(self):
        if not hasattr(self, '_contract'):
            self._contract = self.result.getContract(self.contractType, self.contractId)
        return self._contract


class BookResults(AbstractResults):

    def __init__(self):
        self.contractResults = []
        self.value = 0
        self.resultLines = []

    def addContractResults(self, contractResults):
        for resultLine in contractResults.resultLines:
            self.resultLines.append(resultLine)
            if resultLine['metricName'] == self.PRESENT_VALUE_METRIC:
                self.value += resultLine['metricValue']

    def getValuesByContract(self):
        contracts = []
        contractValues = {}
        for line in self.resultLines:
            metricName = line['metricName']
            if metricName == self.PRESENT_VALUE_METRIC:
                contract = line['contract']
                if contract not in contracts:
                    contracts.append(contract)
                    contractValues[contract.id] = 0
                metricValue = line['metricValue']
                contractValues[contract.id] += metricValue
        valuesByContract = [{'contract': c, 'contractValue': contractValues[c.id]} for c in contracts]
        return valuesByContract

    def getGreeksByDeliveryPeriod(self):
        deliveryPeriods = []
        deliveryPeriodDeltas = {}
        deliveryPeriodGammas = {}
        deliveryPeriodVegas = {}
        greeks = [self.DELTA_METRIC, self.GAMMA_METRIC, self.VEGA_METRIC]
        for line in self.resultLines:
            deliveryPeriod = line['deliveryPeriod']
            if deliveryPeriod not in deliveryPeriods:
                deliveryPeriods.append(deliveryPeriod)
                deliveryPeriodDeltas[deliveryPeriod.id] = 0.0
                deliveryPeriodGammas[deliveryPeriod.id] = 0.0
                deliveryPeriodVegas[deliveryPeriod.id] = 0.0
            metricName = line['metricName']
            metricValue = line['metricValue']
            if metricName == self.DELTA_METRIC:
                deliveryPeriodDeltas[deliveryPeriod.id] += metricValue
            elif metricName == self.GAMMA_METRIC:
                deliveryPeriodGammas[deliveryPeriod.id] += metricValue
            elif metricName == self.VEGA_METRIC:
                deliveryPeriodVegas[deliveryPeriod.id] += metricValue
        greeksByPeriod = [{'deliveryPeriod': p, 'delta': deliveryPeriodDeltas[p.id], 'gamma': deliveryPeriodGammas[p.id], 'vega': deliveryPeriodVegas[p.id]} for p in deliveryPeriods]
        return greeksByPeriod



