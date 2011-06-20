import unittest
from kforge.testunit import TestCase
import os
import shutil
import kforge.plugin.moin
import kforge.filesystem
from kforge.ioc import *

def suite():
    suites = [
        unittest.makeSuite(MoinUtilsTest),
        unittest.makeSuite(PluginTest),
    ]
    return unittest.TestSuite(suites)

fsPaths = kforge.filesystem.FileSystemPathBuilder()

class PluginTest(TestCase):
    
    def setUp(self):
        super(PluginTest, self).setUp()
        if not self.registry.plugins.has_key('moin'):
            self.registry.plugins.create('moin')
        self.plugin = self.registry.plugins['moin']
        self.project = self.registry.projects['annakarenina']
        services = self.plugin.services[self.project]
        try:
            self.service = services.create('moin')
        except:
            service = services['moin']
            service.delete()
            service.purge()
            raise
    
    def tearDown(self):
        super(PluginTest, self).tearDown()
        self.service.delete()
        self.service.purge()
        
    def testServicesPaths(self):
        self.failUnless(self.service.hasDir(), self.service.getDirPath())
    
    def testGetApacheConfig(self):
        self.plugin.getSystem().getApacheConfig(self.service)
    
    def testBackup(self):
        # TODO
        pass

class MoinUtilsTest(unittest.TestCase):
    
    dictionary = RequiredFeature('SystemDictionary')
    
    def setUp(self):
        import tempfile
        self.tempdir = tempfile.mkdtemp()  
        self.moinUtils = kforge.plugin.moin.MoinUtils(self.tempdir)  
        self.moinUtils = kforge.plugin.moin.MoinUtils(
            self.dictionary['moin.system_path'], self.tempdir
        )
        self.wikiName = 'test-create-new-wiki'  
        self.moinUtils.createWiki(self.wikiName)
    
    def tearDown(self):
        shutil.rmtree(self.tempdir)
    
    def testCreateWiki(self):
        self.failUnless(self.moinUtils.wikiExists(self.wikiName))
    
    def testDeleteWiki(self):
        self.moinUtils.deleteWiki(self.wikiName)
        self.failIf(self.moinUtils.wikiExists(self.wikiName))
    
    def testBackupWiki(self):
        destPath = os.path.join(self.tempdir, 'backup')
        outPath = destPath + '.tgz'
        self.moinUtils.backupWiki(self.wikiName, destPath)
        self.failUnless(os.path.exists(outPath))
