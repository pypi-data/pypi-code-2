from dm.command.initialise import InitialiseDomainModel
import datetime
import calendar
from dm.ioc import RequiredFeature

class InitialiseDomainModel(InitialiseDomainModel):
    """
    Creates default domain model objects.
    """

    timepoint = RequiredFeature('Timepoint')
    
    def execute(self):
        super(InitialiseDomainModel, self).execute()
        # Remove various update permissions.
        self.removePermission('Update', 'Result')
        self.removePermission('Update', 'Image')
        # Create objects.
        now = datetime.datetime.now()
        self.thisYear = now.year
        self.thisMonth = now.month
        self.thisDay = now.day
        self.createSymbols()
        self.createMarkets()
        self.createPriceProcesses()
        self.createContractTypes()
        self.createPricers()
        self.createPricerPreferences()
        self.createImages()
        self.createRights()
        self.createBooks()
        self.createContracts()
        self.createResults()
        self.commitSuccess()

    def removePermission(self, actionName, domainClassName):
        action = self.registry.actions[actionName]
        protection = self.registry.protectionObjects['Result']
        protection = self.registry.protectionObjects[domainClassName]
        permission = protection.permissions[action]
        for grant in permission.grants:
            grant.delete()

    def createProtectionObjects(self):
        super(InitialiseDomainModel, self).createProtectionObjects()
        self.registry.protectionObjects.create('Symbol')
        self.registry.protectionObjects.create('PriceProcess')
        self.registry.protectionObjects.create('ContractType')
        self.registry.protectionObjects.create('Pricer')
        self.registry.protectionObjects.create('Book')
        self.registry.protectionObjects.create('Model')
        self.registry.protectionObjects.create('Image')
        self.registry.protectionObjects.create('Market')
        self.registry.protectionObjects.create('Result')
        # For the contract types....
        self.registry.protectionObjects.create('American')
        self.registry.protectionObjects.create('Binary')
        self.registry.protectionObjects.create('Dsl')
        self.registry.protectionObjects.create('European')
        self.registry.protectionObjects.create('Futures')
        # Todo: Make setting up access control for contract types easier.

    def createSymbols(self):
        self.exchange1 = self.registry.exchanges.create('NYMX')
        self.symbol1 = self.exchange1.symbols.create('CL')
        self.symbol2 = self.exchange1.symbols.create('HO')

    def createMarkets(self):
        for periodYear in range(self.thisYear, self.thisYear+2):
            for periodMonth in range(1, 13):
                if periodYear == self.thisYear:
                    if periodMonth <= self.thisMonth:
                        continue
                periodDay = calendar.monthrange(periodYear,periodMonth)[1]
                firstDeliveryDate = datetime.datetime(periodYear, periodMonth, periodDay)
                print "Delivery date: %s" % firstDeliveryDate
                # Todo: Get expiration from the market data source.
                expiration = datetime.datetime(periodYear, periodMonth, 1)
                lastPrice1 = 30
                referenceDate1 = datetime.datetime(self.thisYear-1, 1, 1)
                lastPrice2 = 10
                referenceDate2 = datetime.datetime(self.thisYear, 1, 1)
                self.timepoint.recorded = referenceDate1
                market = self.symbol1.markets.create(
                    expiration=expiration,
                    firstDeliveryDate=firstDeliveryDate,
                    lastPrice=lastPrice1
                )
                self.timepoint.reset()
                temporalHistory = market.temporalHistory
                version = market.temporalHistory.create(dateCreated=referenceDate2)
                version.lastPrice = lastPrice2
                version.save()

    def createPriceProcesses(self):
        self.priceProcessBlackScholes = self.registry.priceProcesses.create(
            codeModuleName='quant.priceprocess.simple',
            codeClassName='BlackScholesVolatility'
        )
        self.priceProcessLocalVolatility = self.registry.priceProcesses.create(
            codeModuleName='quant.priceprocess.simple',
            codeClassName='LocalVolatility'
        )
        self.priceProcessStochasticVolatilityHeston = self.registry.priceProcesses.create(
            codeModuleName='quant.priceprocess.simple',
            codeClassName='StochasticVolatilityHeston'
        )
        self.priceProcessStochasticVolatilitySABR = self.registry.priceProcesses.create(
            codeModuleName='quant.priceprocess.simple',
            codeClassName='StochasticVolatilitySABR'
        )

    def createContractTypes(self):
        self.contractTypeAmerican = self.createContractType(
            codeModuleName='quant.contracttype.simple',
            codeClassName='American'
        )
        self.contractTypeBinary = self.createContractType(
            codeModuleName='quant.contracttype.simple',
            codeClassName='Binary'
        )
        self.contractTypeDsl = self.createContractType(
            codeModuleName='quant.contracttype.simple',
            codeClassName='Dsl'
        )
        self.contractTypeEuropean = self.createContractType(
            codeModuleName='quant.contracttype.simple',
            codeClassName='European'
        )
        self.contractTypeFutures = self.createContractType(
            codeModuleName='quant.contracttype.simple',
            codeClassName='Futures'
        )

    def createContractType(self, codeModuleName, codeClassName):
        contractType = self.registry.contractTypes.create(
            codeModuleName=codeModuleName,
            codeClassName=codeClassName
        )
        contractClass = contractType.getCodeClass()
        self.registry.registerDomainClass(contractClass)
        return contractType

    def createPricers(self):
        self.pricerEuropeanBlackScholes = self.registry.pricers.create(
            codeModuleName='quant.pricer.simple',
            codeClassName='EuropeanBlackScholes'
        )
        self.pricerEuropeanBinomialTree = self.registry.pricers.create(
            codeModuleName='quant.pricer.simple',
            codeClassName='EuropeanBinomialTree'
        )
        self.pricerAmericanBinomialTree = self.registry.pricers.create(
            codeModuleName='quant.pricer.simple',
            codeClassName='AmericanBinomialTree'
        )
        self.pricerEuropeanMontecarlo = self.registry.pricers.create(
            codeModuleName='quant.pricer.simple',
            codeClassName='EuropeanMontecarlo'
        )
        self.pricerAmericanMontecarlo = self.registry.pricers.create(
            codeModuleName='quant.pricer.simple',
            codeClassName='AmericanMontecarlo'
        )

    def createPricerPreferences(self):
        self.registry.pricerPreferences.create(
            priceProcess = self.priceProcessBlackScholes,
            contractType = self.contractTypeEuropean,
            pricer = self.pricerEuropeanBlackScholes,
        )
        self.registry.pricerPreferences.create(
            priceProcess = self.priceProcessBlackScholes,
            contractType = self.contractTypeAmerican,
            pricer = self.pricerAmericanBinomialTree,
        )
        self.registry.pricerPreferences.create(
            priceProcess = self.priceProcessLocalVolatility,
            contractType = self.contractTypeEuropean,
            pricer = self.pricerEuropeanBlackScholes,
        )
        self.registry.pricerPreferences.create(
            priceProcess = self.priceProcessLocalVolatility,
            contractType = self.contractTypeAmerican,
            pricer = self.pricerAmericanBinomialTree,
        )

    def createImages(self):
        self.image1 = self.registry.images.create(observationTime=datetime.datetime(self.thisYear, self.thisMonth, self.thisDay), priceProcess=self.priceProcessBlackScholes)

    def createRights(self):
        self.call = self.registry.optionRights.create('Call')
        self.put = self.registry.optionRights.create('Put')
        self.buy = self.registry.futuresRights.create('Buy')
        self.sell = self.registry.futuresRights.create('Sell')

    def createBooks(self):
        self.book1 = self.registry.books.create(title="My Book")

    def createContracts(self):
        deliveryYear = self.thisYear + 1
        deliveryMonth = self.thisMonth
        deliveryDay = calendar.monthrange(deliveryYear, deliveryMonth)[1]
        firstDeliveryDate = datetime.datetime(deliveryYear, deliveryMonth, deliveryDay)
        underlying = self.symbol1.markets.read(firstDeliveryDate=firstDeliveryDate)
        expiration = underlying.expiration - datetime.timedelta(14)
        europeans = self.contractTypeEuropean.getCodeClass().createRegister()
        self.option1 = europeans.create(
            title="European call #1",
            right=self.call,
            volume=10,
            strikePrice=9,
            underlying=underlying,
            expiration=expiration,
            book=self.book1,
        )
        self.option2 = europeans.create(
            title="European put #2",
            right=self.put,
            volume=10,
            strikePrice=9,
            underlying=underlying,
            expiration=expiration,
            book=self.book1,
        )

    def createResults(self):
        self.registry.results.create(image=self.image1, book=self.book1)
