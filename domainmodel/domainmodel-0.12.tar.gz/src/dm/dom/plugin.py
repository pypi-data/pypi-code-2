from dm.dom.stateful import *
from dm.ioc import *

def getProjects():
    domainRegistry = RequiredFeature('DomainRegistry')
    return domainRegistry.projects

class Plugin(StandardObject):
    "Registered plugin."

    systemFactory = RequiredFeature('PluginFactory')
   
    def __init__(self, **kwds):
        super(Plugin, self).__init__(**kwds)
        self.__system = None
    
    def initialise(self, register):
        "Initialises the plugin system."
        # Todo: Document what 'register' is.
        pluginSystem = self.getSystem()
        if pluginSystem:
            pluginSystem.initialise(register)

    def getSystem(self):
        "Returns plugin system modelled by domain object."
        if not self.__system:
            self.__system = self.systemFactory.getPlugin(self)
        return self.__system

    def getMaxServicesPerProject(self):
        "Returns the maximum service instances for any project."
        pluginSystem = self.getSystem()
        if pluginSystem:
            return pluginSystem.getMaxServicesPerProject()
        else:
            return None

    def extendsDomainModel(self):
        "Whether or not the plugin system has it's own domain objects."
        return self.getSystem().extendsDomainModel

    def getExtnRegister(self):
        "Returns the plugin system's domain object register."
        return self.getSystem().getRegister()

    def getExtnObject(self, service):
        "Returns one of the plugin system's domain objects."
        extnRegister = self.getSystem().getRegister()
        if service in extnRegister:
            return extnRegister[service]
        else:
            return None

