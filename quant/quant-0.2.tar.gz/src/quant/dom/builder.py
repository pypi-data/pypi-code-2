import dm.dom.builder
from dm.dom.stateful import *

from quant.dom.base import DerivativesContract
from quant.dom.forwardcontract import ForwardContract
from quant.dom.binaryoption import BinaryOption
from quant.dom.europeanoption import EuropeanOption
from quant.dom.americanoption import AmericanOption
from quant.dom.pricer import Pricer
from quant.dom.book import Book
from quant.dom.market import Market

class ModelBuilder(dm.dom.builder.ModelBuilder):

    def construct(self):
        super(ModelBuilder, self).construct()
        # Purpose of the model is to value derivativesContracts based
        # on market observables and trading assumptions.

        # The core highlighted model consists of:
        #  - ForwardContract (model object)
        #  - BinaryOption (model object)
        #  - EuropeanOption (model object)
        #  - AmericanOption (model object)
        #  - Price (model object)
        #  - Pricer (cohesive mechanism)
        #  - pricer parameters (calibration)
        #  - Market (data service)

        self.registry.registerDomainClass(ForwardContract)
        self.registry.registerDomainClass(BinaryOption)
        self.registry.registerDomainClass(EuropeanOption)
        self.registry.registerDomainClass(AmericanOption)
        self.registry.registerDomainClass(Pricer)
        self.registry.registerDomainClass(Book)
        self.registry.registerDomainClass(Market)
        self.registry.forwardContracts = ForwardContract.createRegister()
        self.registry.binaryOptions = BinaryOption.createRegister()
        self.registry.europeanOptions = EuropeanOption.createRegister()
        self.registry.americanOptions = AmericanOption.createRegister()
        self.registry.pricers = Pricer.createRegister()
        self.registry.books = Book.createRegister()
        self.registry.markets = Market.createRegister()


