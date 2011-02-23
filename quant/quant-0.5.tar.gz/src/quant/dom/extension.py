from quant.dom.base import DatedStatefulObject
from quant.dom.base import String
from quant.dom.base import AggregatesMany
from quant.dom.base import HasA
import codecs

class Extension(DatedStatefulObject):

    codeModuleName = String()
    codeClassName = String()

    def getLabelValue(self):
        return "%s.%s" % (self.codeModuleName, self.codeClassName)

    def getCodeClass(self):
        return getattr(self.getCodeModule(), self.codeClassName)

    def canImportCode(self):
        try:
            self.getCodeClass()
        except ImportError:
            return False
        else:
            return True

    def getCodeModule(self):
        return __import__(self.codeModuleName, '', '', '*')

    def getExtensionRegistryAttrName(self):
        return self.getCodeClass().getRegistryAttrName()

    def listCode(self):
        try:
            return file(self.getCodeModule().__file__.rstrip('c')).read()
        except ImportError, inst:
            return "Error importing code: %s" % inst


class PriceProcess(Extension):

    pricerPreferences = AggregatesMany('PricerPreference', key='contractType')

    def calcActualHistoricalVolatility(self, priceHistory):
        priceProcessClass = self.getCodeClass()
        priceProcess = priceProcessClass()
        return priceProcess.calcActualHistoricalVolatility(priceHistory)


class ContractType(Extension):

    pricerPreferences = AggregatesMany('PricerPreference', key='priceProcess')


class Pricer(Extension):
    
    pricerPreferences = AggregatesMany('PricerPreference', key='id')


class PricerPreference(DatedStatefulObject):

    pricer = HasA('Pricer')
    contractType = HasA('ContractType')
    priceProcess = HasA('PriceProcess')

    def getLabelValue(self):
        return "%s for %s with %s" % (
            self.pricer.getLabelValue(),
            self.contractType.getLabelValue(),
            self.priceProcess.getLabelValue()
        )

