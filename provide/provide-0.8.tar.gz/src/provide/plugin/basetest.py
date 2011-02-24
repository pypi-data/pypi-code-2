from provide.testunit import TestCase
import unittest
from provide.plugin.base import ProvisionPlugin
from provide.plugin.base import DomainModelApplicationPlugin

def suite():
    suites = [
        unittest.makeSuite(TestProvisionPlugin),
        unittest.makeSuite(TestDomainModelApplicationPlugin),
    ]
    return unittest.TestSuite(suites)


class PluginTestCase(TestCase):

    applicationLocation = ''
    provisionLocation = ''
    applicationDependencies = []

    def setUp(self):
        super(PluginTestCase, self).setUp()
        self.deleteProvision()
        self.deletePlugin()
        self.pluginObject = self.createPlugin()
        self.plugin = self.pluginObject.getSystem()
        self.failIf(self.pluginName in self.registry.provisions)
        self.failUnless(self.pluginName in self.registry.plugins)
    
    def tearDown(self):
        super(PluginTestCase, self).tearDown()
        self.deleteProvision()
        self.deletePlugin()
        self.failIf(self.pluginName in self.registry.provisions)
        self.failIf(self.pluginName in self.registry.plugins)
 
    def createPlugin(self):
        return self.registry.plugins.create(self.pluginName)

    def createProvision(self):
        provision = self.registry.provisions.create(self.pluginName,
            location=self.provisionLocation)
        return provision

    def createApplication(self):
        provision = self.createProvision()
        application = provision.applications.create(self.applicationName)
        for dependencyName, dependencyLocation in self.applicationDependencies.items():
            application.dependencies.create(dependencyName,
                location=dependencyLocation)
        return application

    def createService(self):
        application = self.createApplication()
        return application.services.create(self.serviceName)

    def deletePlugin(self):
        if self.pluginName in self.registry.plugins:
            pluginObject = self.registry.plugins[self.pluginName]
            pluginObject.delete()

    def deleteProvision(self):
        if self.pluginName in self.registry.provisions:
            provision = self.registry.provisions[self.pluginName]
            provision.delete()

    def test_createProvision(self):
        provision = self.createProvision()
        self.failUnless(self.plugin.hasProvision(provision))

    def test_createApplication(self):
        application = self.createApplication()
        self.failUnless(self.plugin.hasApplication(application))

    def test_createService(self):
        service = self.createService()
        self.failUnless(self.plugin.hasService(service))


class StubDomainObject(object):

    name = ''


class TestProvisionPlugin(TestCase):

    def setUp(self):
        super(TestProvisionPlugin, self).setUp()
        self.plugin = ProvisionPlugin(StubDomainObject())

    def tearDown(self):
        super(TestProvisionPlugin, self).tearDown()
        self.plugin = None

    def test_createProvision(self):
        self.failUnlessRaises(Exception, self.plugin.createProvision, None)
    
    def test_createApplication(self):
        self.failUnlessRaises(Exception, self.plugin.createApplication, None)

    def test_isNativeProvision(self):
        self.failUnlessRaises(Exception, self.plugin.isNativeProvision, None)


class TestDomainModelApplicationPlugin(TestCase):

    def setUp(self):
        super(TestDomainModelApplicationPlugin, self).setUp()
        self.plugin = DomainModelApplicationPlugin(StubDomainObject())

    def tearDown(self):
        super(TestDomainModelApplicationPlugin, self).tearDown()
        self.plugin = None


