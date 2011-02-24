import os
import commands

import dm.util.db
import dm.ioc

class Database(dm.util.db.Database):

    features = dm.ioc.features
        
    def _getSystemDictionary(self):
        import provide.dictionary 
        systemDictionary = provide.dictionary.SystemDictionary()
        return systemDictionary
            
    def init(self):
        """
        Initialise service database by creating initial domain object records.
        """
        import provide.soleInstance
        commandSet = provide.soleInstance.application.commands
        commandClass = commandSet['InitialiseDomainModel']
        initDomainModel = commandClass()
        initDomainModel.execute()

