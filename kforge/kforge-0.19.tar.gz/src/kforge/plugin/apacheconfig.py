import os

import kforge.plugin.base
import kforge.apache.config
import kforge.utils

class Plugin(kforge.plugin.base.NonServicePlugin):
    
    def __init__(self, domainObject):
        super(Plugin, self).__init__(domainObject)
        self.configBuilder = kforge.apache.config.ApacheConfigBuilder()
    
    def onServiceCreate(self, service):
        self.rebuildAndReload()
    
    def onServiceUpdate(self, service):
        self.rebuildAndReload()
    
    def onServiceDelete(self, service):
        self.rebuildAndReload()
    
    def rebuildAndReload(self):
        self.configBuilder.buildAll()
        self.configBuilder.reloadConfig()
        
