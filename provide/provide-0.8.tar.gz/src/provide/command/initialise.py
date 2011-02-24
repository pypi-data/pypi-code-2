from dm.command.initialise import InitialiseDomainModelBase

class InitialiseDomainModel(InitialiseDomainModelBase):
    """
    Creates default domain model objects.
    """
    
    def __init__(self):
        super(InitialiseDomainModel, self).__init__()
 
    def execute(self):
        super(InitialiseDomainModel, self).execute()
        self.commitSuccess()
        
    def purgePackage(packageName):
        pass

