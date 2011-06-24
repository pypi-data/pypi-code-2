import dm.dom.builder
from dm.dom.stateful import *

from quant.dom.market import Exchange
from quant.dom.market import Symbol
from quant.dom.market import Image
from quant.dom.market import Market
from quant.dom.market import Metric
from quant.contracttype.simple import OptionRight
from quant.contracttype.simple import FuturesRight
from quant.dom.book import Book
from quant.dom.result import Result, ResultLine
from quant.dom.extension import ContractType
from quant.dom.extension import PriceProcess
from quant.dom.extension import Pricer
from quant.dom.extension import PricerPreference

class ModelBuilder(dm.dom.builder.ModelBuilder):

    def loadImage(self):
        pass

    def construct(self):
        super(ModelBuilder, self).construct()
        # Core model.
        self.registry.registerDomainClass(Exchange)
        self.registry.registerDomainClass(Symbol)
        self.registry.registerDomainClass(Market)
        self.registry.registerDomainClass(Image)
        self.registry.registerDomainClass(Metric)
        self.registry.registerDomainClass(OptionRight)
        self.registry.registerDomainClass(FuturesRight)
        self.registry.registerDomainClass(Book)
        self.registry.registerDomainClass(ResultLine)
        self.registry.registerDomainClass(Result)
        self.registry.exchanges = Exchange.createRegister()
        self.registry.symbols = Symbol.createRegister()
        self.registry.markets = Market.createRegister()
        self.registry.images = Image.createRegister()
        self.registry.optionRights = OptionRight.createRegister()
        self.registry.futuresRights = FuturesRight.createRegister()
        self.registry.books = Book.createRegister()
        self.registry.results = Result.createRegister()
        # Extensions.
        self.registry.registerDomainClass(ContractType)
        self.registry.registerDomainClass(PriceProcess)
        self.registry.registerDomainClass(Pricer)
        self.registry.registerDomainClass(PricerPreference)
        self.registry.contractTypes = ContractType.createRegister()
        self.registry.priceProcesses = PriceProcess.createRegister()
        self.registry.pricers = Pricer.createRegister()
        self.registry.pricerPreferences = PricerPreference.createRegister()
        self.registry.loadBackgroundRegister(self.registry.contractTypes)
        self.registry.loadBackgroundRegister(self.registry.priceProcesses)
        self.registry.loadBackgroundRegister(self.registry.pricers)
        self.registry.loadBackgroundRegister(self.registry.pricerPreferences)
        # Contracts from contract types.
        for contractType in self.registry.contractTypes:
            try:
                contractClass = contractType.getCodeClass()
            except ImportError, inst:
                # Todo: Write this to the logger.
                msg = "Error importing code for contract type '%s'." % contractType.getLabelValue()
                print msg
            else:
                self.registry.registerDomainClass(contractClass)
                registryAttrName = contractClass.getRegistryAttrName() 
                contractRegister = contractClass.createRegister()
                setattr(self.registry, registryAttrName, contractRegister)

