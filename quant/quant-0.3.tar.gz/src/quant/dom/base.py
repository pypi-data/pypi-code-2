from dm.dom.stateful import *
from quant.dom.results import *

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


class DerivativesContract(DatedStatefulObject):

    pricerClass = None

    title = String()
    isPut = Boolean(default=False)

    volume = Integer()
    strikePrice = Float(isRequired=True)
    expiryTime = String(isRequired=True)
    underlying = String()
    deliveryPeriod = String(isRequired=True)
    # Todo: paymentTime ?

    book = HasA("Book", isRequired=False)


    def getLabelValue(self):
        return self.title or self.id

    def calcResults(self, market):
        value = self.volume * self.estimateUnitValue(market=market)
        deliveryPeriodResults = DeliveryPeriodResults()
        deliveryPeriodResults.name = self.deliveryPeriod
        deliveryPeriodResults.value = value 
        underlyingResults = UnderlyingResults()
        underlyingResults.name = self.underlying
        underlyingResults.deliveryPeriods.append(deliveryPeriodResults)
        underlyingResults.value = value
        contractResults = ContractResults()
        contractResults.name = self.getLabelValue()
        contractResults.domainClassName = self.meta.name
        contractResults.id = self.id
        contractResults.value = value
        contractResults.registryAttrName = self.getRegistryAttrName()
        contractResults.pricer = self.getPricerClass().__name__
        contractResults.underlyings.append(underlyingResults)
        return contractResults

    def estimateUnitValue(self, market):
        currentPrice = market.getCurrentPrice(deliveryPeriod=self.deliveryPeriod)
        annualisedVolatility = market.getAnnualisedVolatility()
        nowTime = market.getNowTime()
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

