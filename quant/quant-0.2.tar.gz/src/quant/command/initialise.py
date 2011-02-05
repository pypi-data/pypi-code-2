from dm.command.initialise import InitialiseDomainModel

class InitialiseDomainModel(InitialiseDomainModel):
    """
    Creates default domain model objects.
    """
    
    def __init__(self):
        super(InitialiseDomainModel, self).__init__()
 
    def execute(self):
        super(InitialiseDomainModel, self).execute()
        self.createMarkets()
        self.commitSuccess()

    def createProtectionObjects(self):
        super(InitialiseDomainModel, self).createProtectionObjects()
        self.registry.protectionObjects.create('EuropeanOption')
        self.registry.protectionObjects.create('AmericanOption')
        self.registry.protectionObjects.create('Pricer')
        self.registry.protectionObjects.create('Book')
        self.registry.protectionObjects.create('Market')

    def createMarkets(self):
        self.registry.markets.create(
            title='WTI (Mock)',
            name='wti',
            dataService='test',
        )

