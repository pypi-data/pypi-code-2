import dm.dom.builder
from dm.dom.stateful import *

class ModelBuilder(dm.dom.builder.ModelBuilder):

    def construct(self):
        super(ModelBuilder, self).construct()

        self.registry.registerDomainClass(Provision)
        self.registry.provisions = Provision.createRegister()

        self.registry.registerDomainClass(Application)
        self.registry.applications = Application.createRegister()

        self.registry.registerDomainClass(Link)
        self.registry.links = Link.createRegister()

        self.registry.registerDomainClass(Dependency)
        self.registry.dependencies = Dependency.createRegister()

        self.registry.registerDomainClass(Service)
        self.registry.services = Service.createRegister()

        self.registry.registerDomainClass(Purpose)
        self.registry.purposes = Purpose.createRegister()

        self.registry.registerDomainClass(DataDump)
        self.registry.dataDumps = DataDump.createRegister()

        self.registry.registerDomainClass(MigrationPlan)
        self.registry.migrationPlans = MigrationPlan.createRegister()


class Provision(StandardObject):

    location = String()
    applications = AggregatesMany('Application', 'name')
    purposes = AggregatesMany('Purpose', 'name')
    migrationPlans = AggregatesMany('MigrationPlan', 'name')

    def getPluginSystem(self):
        pluginDomainObject = self.registry.plugins[self.name]
        return pluginDomainObject.getSystem()


# Todo: Rename to Version (or Release, or Distribution).
class Application(StandardObject):
    
    location = String()
    provision = HasA('Provision')
    services = AggregatesMany('Service', 'name')
    dependencies = AggregatesMany('Dependency', 'name')
    links = AggregatesMany('Link', 'service')


class Link(SimpleObject):

    application = HasA('Application')
    service = HasA('Service')


class Dependency(StandardObject):

    location = String()
    application = HasA('Application')


class Purpose(StandardObject):

    provision = HasA('Provision')
    service = HasA('Service', isRequired=False)


class Service(StandardObject):

    application = HasA('Application')
    dataDumps = AggregatesMany('DataDump', 'name')
    links = AggregatesMany('Link', 'application')
    isDbCreated = Boolean(default=False, isRequired=False)
    isFsCreated = Boolean(default=False, isRequired=False)

    def commission(self):
        self.raiseCommission()

    def editConfig(self):
        self.raiseEditConfig()

    def unitTest(self):
        self.raiseUnitTest()

    def raiseCommission(self):
        self.onCommission()

    def raiseEditConfig(self):
        self.onEditConfig()

    def raiseUnitTest(self):
        self.onUnitTest()

    def onCommission(self):
        self.notifyPlugins(self.__class__.__name__ + 'Commission', self)

    def onEditConfig(self):
        self.notifyPlugins(self.__class__.__name__ + 'EditConfig', self)
    
    def onUnitTest(self):
        self.notifyPlugins(self.__class__.__name__ + 'UnitTest', self)


class DataDump(StandardObject):

    service = HasA('Service')
    sourceDump = HasA('DataDump', isRequired=False)
    migrationPlan = HasA('MigrationPlan', isRequired=False)
    location = String(isRequired=False)

    def commissionService(self):
        self.raiseCommissionService()

    def raiseCommissionService(self):
        self.onCommissionService()

    def onCommissionService(self):
        self.notifyPlugins(self.__class__.__name__ + 'CommissionService', self)


class MigrationPlan(StandardObject):

    location = String()
    provision = HasA('Provision')

