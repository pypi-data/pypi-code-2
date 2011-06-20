import unittest

from kforge.testunit import TestCase
import kforge.filesystem

def suite():
    suites = [
        unittest.makeSuite(PluginTest),
    ]
    return unittest.TestSuite(suites)

class PluginTest(TestCase):
    
    def setUp(self):
        super(PluginTest, self).setUp()
        if not self.registry.plugins.has_key('www'):
            self.registry.plugins.create('www')
        self.plugin = self.registry.plugins['www']
        self.project = self.registry.projects['annakarenina']
        if 'www' in self.project.services:
            service = self.project.services['www']
            service.delete()
            service.purge()
        self.project.services.create('www', plugin=self.plugin)
        self.service = self.project.services['www']
        self.fsPathBuilder = kforge.filesystem.FileSystemPathBuilder()
    
    def tearDown(self):
        self.service.delete()
        self.service.purge()
    
    def testService(self):
        # Check the filesystem has been setup.
        fsPath = self.fsPathBuilder.getServicePath(self.service)
        self.failUnless(fsPath)
        # Check the Apache configuration looks okay.
        apacheConfig = self.plugin.getSystem().getApacheConfig(self.service)
        expect = 'Alias %(urlPath)s ' + fsPath + '\n'
        self.assertEquals(apacheConfig, expect)

