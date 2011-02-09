import dm.dom.builder
from dm.dom.stateful import *

from quant.dom.base import DerivativesContract
from quant.dom.market import Model
from quant.dom.market import Metric
from quant.dom.market import DeliveryPeriod
from quant.dom.market import Image
from quant.dom.market import Symbol
from quant.dom.forwardcontract import ForwardContract
from quant.dom.binaryoption import BinaryOption
from quant.dom.europeanoption import European
from quant.dom.americanoption import American
from quant.dom.pricer import Pricer
from quant.dom.book import Book
from quant.dom.result import Result, ResultLine

class ModelBuilder(dm.dom.builder.ModelBuilder):

    def construct(self):
        super(ModelBuilder, self).construct()
        # Purpose of the model is to value derivativesContracts based
        # on market observables and trading assumptions.

        # The core highlighted model consists of:
        #  - ForwardContract (model object)
        #  - BinaryOption (model object)
        #  - European (model object)
        #  - American (model object)
        #  - Price (model object)
        #  - Pricer (cohesive mechanism)
        #  - pricer parameters (calibration)
        #  - Market (data service)

        self.registry.registerDomainClass(ForwardContract)
        self.registry.registerDomainClass(BinaryOption)
        self.registry.registerDomainClass(European)
        self.registry.registerDomainClass(American)
        self.registry.registerDomainClass(Pricer)
        self.registry.registerDomainClass(Book)
        self.registry.registerDomainClass(Model)
        self.registry.registerDomainClass(Image)
        self.registry.registerDomainClass(DeliveryPeriod)
        self.registry.registerDomainClass(Result)
        self.registry.registerDomainClass(ResultLine)
        self.registry.registerDomainClass(Symbol)
        self.registry.registerDomainClass(Metric)
        self.registry.forwardContracts = ForwardContract.createRegister()
        self.registry.binaryOptions = BinaryOption.createRegister()
        self.registry.europeans = European.createRegister()
        self.registry.americans = American.createRegister()
        self.registry.pricers = Pricer.createRegister()
        self.registry.books = Book.createRegister()
        self.registry.models = Model.createRegister()
        self.registry.images = Image.createRegister()
        self.registry.symbols = Symbol.createRegister()
        self.registry.deliveryPeriods = DeliveryPeriod.createRegister()
        self.registry.results = Result.createRegister()

    def loadImage(self):
        pass
