from dm.command.initialise import InitialiseDomainModel
import datetime

class InitialiseDomainModel(InitialiseDomainModel):
    """
    Creates default domain model objects.
    """
    
    def __init__(self):
        super(InitialiseDomainModel, self).__init__()
 
    def execute(self):
        super(InitialiseDomainModel, self).execute()
        self.createSymbols()
        self.createModels()
        self.createBooks()
        self.createContracts()
        # Remove permission to update results.
        action = self.registry.actions['Update']
        protection = self.registry.protectionObjects['Result']
        permission = protection.permissions[action]
        for grant in permission.grants:
            grant.delete()
        # Remove permission to update images.
        protection = self.registry.protectionObjects['Image']
        permission = protection.permissions[action]
        for grant in permission.grants:
            grant.delete()
        self.commitSuccess()

    def createProtectionObjects(self):
        super(InitialiseDomainModel, self).createProtectionObjects()
        self.registry.protectionObjects.create('European')
        self.registry.protectionObjects.create('American')
        self.registry.protectionObjects.create('Symbol')
        self.registry.protectionObjects.create('Pricer')
        self.registry.protectionObjects.create('Book')
        self.registry.protectionObjects.create('Model')
        self.registry.protectionObjects.create('Image')
        self.registry.protectionObjects.create('DeliveryPeriod')
        self.registry.protectionObjects.create('Result')

    def createSymbols(self):
        self.symbol1 = self.registry.symbols.create('WTI')
        self.symbol2 = self.registry.symbols.create('ICE')

    def createModels(self):
        self.model1 = self.registry.models.create(
            title='WTI (Mock)',
        )
        for year in range(2010, 2013):
            for month in range(1, 13):
                for day in range(1, 2):
                    date = datetime.datetime(year, month, day)
                    currentPrice = 10
                    self.symbol1.deliveryPeriods.create(
                        date=date,
                        currentPrice=currentPrice,
                    )
        self.model1.images.create(observationTime=datetime.datetime(2010, 1, 1))

    def createBooks(self):
        self.book1 = self.registry.books.create(title="My Book", model=self.model1)

    def createContracts(self):
        deliveryPeriod = self.symbol1.deliveryPeriods.read(date=datetime.datetime(2011, 1, 1))
        expiryTime = datetime.datetime(2011, 1, 1)
        self.option1 = self.book1.europeans.create(
            title="European call #1",
            isPut=False,
            volume=10,
            strikePrice=9,
            expiryTime=expiryTime,
            deliveryPeriod=deliveryPeriod
        )
        self.option2 = self.book1.europeans.create(
            title="European put #2",
            isPut=True,
            volume=10,
            strikePrice=9,
            expiryTime=expiryTime,
            deliveryPeriod=deliveryPeriod
        )

