from provide.testunit import TestCase
import unittest
from provide.plugin.example import Plugin as ExamplePlugin

def suite():
    suites = [
        unittest.makeSuite(TestExamplePlugin),
    ]
    return unittest.TestSuite(suites)


class TestExamplePlugin(TestCase):

    pluginName = 'example'
    provisionName = 'example'

    def setUp(self):
        super(TestExamplePlugin, self).setUp()
        self.pluginObject = self.registry.plugins.create(self.pluginName)
        self.plugin = self.pluginObject.getSystem()
        self.plugin.resetCounts()

    def tearDown(self):
        super(TestExamplePlugin, self).tearDown()
        if self.pluginName in self.registry.plugins:
            pluginObject = self.registry.plugins[self.pluginName]
            pluginObject.delete()

    def test_counter(self):
        self.failUnlessEqual(self.plugin.getCount('blah'), 0)
        self.plugin.incCount('blah')
        self.failUnlessEqual(self.plugin.getCount('blah'), 1)

    def deleteProvision(self):
        if self.provisionName in self.registry.provisions:
            provision = self.registry.provisions[self.provisionName]
            provision.delete()
            
    def test_onProvisionCreate(self):
        self.deleteProvision()
        self.failUnlessEqual(self.plugin.getCount('onProvisionCreate'), 0)
        self.registry.provisions.create(self.provisionName)
        self.failUnlessEqual(self.plugin.getCount('onProvisionCreate'), 1)
        self.deleteProvision()

    def test_onOtherProvisionCreate(self):
        self.provisionName += 'other'
        self.deleteProvision()
        self.failUnlessEqual(self.plugin.getCount('onProvisionCreate'), 0)
        self.registry.provisions.create(self.provisionName)
        self.failUnlessEqual(self.plugin.getCount('onProvisionCreate'), 0)
        self.deleteProvision()
