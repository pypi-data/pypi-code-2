import unittest
from dm.testunit import TestCase
import dm.plugin.factory
from dm.exceptions import *

def suite():
    suites = [
            unittest.makeSuite(TestPluginFactory),
        ]
    return unittest.TestSuite(suites)


class TestPluginFactory(TestCase):
    "TestCase for the PluginFactory class."

    def setUp(self):
        super(TestPluginFactory, self).setUp()
        self.factory = dm.plugin.factory.PluginFactory()

    def pluginName(self):
        return "example"

    def pluginDomainObject(self):
        name = self.pluginName()
        return self.registry.plugins[name]

    def testExists(self):
        self.failUnless(self.factory, "No factory was created.")

    def testGetPlugin(self):
        plugin = self.factory.getPlugin(self.pluginDomainObject())
        self.failUnless(plugin, "No plugin produced by factory.")
        self.failUnlessEqual(plugin.domainObject, self.pluginDomainObject())

    def testOnRun(self):
        plugin = self.factory.getPlugin(self.pluginDomainObject())
        countBefore = plugin.counts['onRun']
        val = plugin.onRun(None)
        countAfter = plugin.counts['onRun']
        self.failUnless(countBefore + 1 == countAfter)

    def testOnProjectCreate(self):
        plugin = self.factory.getPlugin(self.pluginDomainObject())
        countBefore = plugin.counts['onProjectCreate']
        val = plugin.onProjectCreate(None)
        countAfter = plugin.counts['onProjectCreate']
        self.failUnless(countBefore + 1 == countAfter)

    def testOnProjectApprove(self):
        plugin = self.factory.getPlugin(self.pluginDomainObject())
        countBefore = plugin.counts['onProjectApprove']
        val = plugin.onProjectApprove(None)
        countAfter = plugin.counts['onProjectApprove']
        self.failUnless(countBefore + 1 == countAfter)

    def testOnProjectDelete(self):
        plugin = self.factory.getPlugin(self.pluginDomainObject())
        countBefore = plugin.counts['onProjectDelete']
        val = plugin.onProjectDelete(None)
        countAfter = plugin.counts['onProjectDelete']
        self.failUnless(countBefore + 1 == countAfter)

