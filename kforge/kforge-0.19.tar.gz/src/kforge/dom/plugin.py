from dm.dom.plugin import Plugin
from dm.dom.stateful import HasManyPages 
from dm.ioc import RequiredFeature
from kforge.exceptions import MissingPluginSystem

def getProjects():
    domainRegistry = RequiredFeature('DomainRegistry')
    return domainRegistry.projects

class Plugin(Plugin):
    "Registered Plugin."

    services = HasManyPages('Service', 'name', 'project', pageKeys=getProjects)

    def getMaxServicesPerProject(self):
        "Returns the maximum service instances for any project."
        if self.hasSystem():
            return self.getSystem().getMaxServicesPerProject()
        else:
            return None

    def getApacheConfigCommon(self):
        self.assertHasSystem()
        return self.getSystem().getApacheConfigCommon()

    def buildWsgiFile(self):
        self.assertHasSystem()
        return self.getSystem().buildWsgiFile()

    def buildCgiFile(self):
        self.assertHasSystem()
        return self.getSystem().buildCgiFile()

    def assertHasSystem(self):
        if not self.hasSystem():
            msg = "Plugin object '%s' has no system object." % self.name
            self.log.error(msg)
            raise MissingPluginSystem(msg)

    def hasSystem(self):
        return bool(self.getSystem())

