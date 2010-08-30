from __future__ import with_statement

import os
import simplejson as ConfigModule
import sys
import unittest
import user

import pomsets_app.controller.automaton as AutomatonModule
import pomsets_app.utils as AppUtilsModule

class TestParse(unittest.TestCase):

    def testParseCloudCredentials(self):

	with open('test/config1') as f:

	    cfg = ConfigModule.load(f)

	    credentials = [x for x in cfg['cloud controller credentials']]
	    self.assertTrue(len(credentials) is 1)
	    
	    credential = credentials[0]
	    
	    expected = 'Eucalyptus'
	    actual = credential['service name']
	    self.assertEquals(expected, actual)
	    
	    expected = 'euca2ools'
	    actual = credential['service API']
	    self.assertEquals(expected, actual)
	    
	    values = credential['values']

	    expected = '00:00:00:00:00:00:00:00:00:00:00:00:00:00:00:00:00:00:00:00'
	    actual = values['user key pair']
	    self.assertEquals(expected, actual)

	    expected = 'pathToIdentityFile'
	    actual = values['identity file']
	    self.assertEquals(expected, actual)
	    
	    expected ='image-id'
	    actual = values['default image']
	    self.assertEquals(expected, actual)
	    
	    pass

	return
    
    
    def testParseRemoteExecuteCredentials(self):
	
	with open('test/config1') as f:

	    cfg = ConfigModule.load(f)

	    credentials = [x for x in cfg['remote execute credentials']]
	    self.assertTrue(len(credentials) is 1)
	    
	    credential = credentials[0]
	    
	    expected = 'remotehost'
	    actual = credential['hostname']
	    self.assertEquals(expected, actual)
	    
	    expected = 'myself'
	    actual = credential['user']
	    self.assertEquals(expected, actual)
	    
	    expected = 'ssh/key/file'
	    actual = credential['keyfile']
	    self.assertEquals(expected, actual)
	    
	    pass
	
	return
    
    
    def testParseHadoopConfigurations(self):
	with open('test/config1') as f:

	    cfg = ConfigModule.load(f)

	    configurations = [x for x in cfg['hadoop configurations']]
	    self.assertTrue(len(configurations) is 1)
	    
	    configuration = configurations[0]
	    
	    expected = 'localhost'
	    actual = configuration['hostname']
	    self.assertEquals(expected, actual)
	    
	    expected = '/hadoop/core'
	    actual = configuration['home']
	    self.assertEquals(expected, actual)
	    
	    pass
	
	return


    def testParseDotCommandPath(self):
	with open('test/config1') as f:
	    cfg = ConfigModule.load(f)

	    configurations = [x for x in cfg['graphviz configurations']]
	    self.assertTrue(len(configurations) is 1)

            configuration = configurations[0]
            expected = 'localhost'
            actual = configuration['hostname']

            expected = '/path/to/dot'
            actual = configuration['dot command path']
            pass

        return

    """
    def testParseLibraryDefinition(self):
	with open('%s/app/src/test/config1' % APP_ROOT) as f:

	    cfg = ConfigModule.load(f)

	    libraryLocations = [x for x in cfg['library definitions']]
	    self.assertTrue(len(libraryLocations) is 1)

	    expected = ['/Users/myself/.pomsets/library']
	    actual = libraryLocations
	    self.assertEquals(expected, actual)
	    pass
	    
	return
    """
    
    # END class TestParse
    pass


class TestSave(unittest.TestCase):

    PATH_ORIGINAL = 'test/config1' 
    PATH_SAVE = '/tmp/foo'
    
    def setUp(self):
        config = AppUtilsModule.loadConfig(configPath=TestSave.PATH_ORIGINAL)

	automaton = AutomatonModule.Automaton()
	automaton.loadConfig(config)
	
	self.automaton = automaton
	return
    
    def tearDown(self):
	if os.path.exists(TestSave.PATH_SAVE):
	    os.unlink(TestSave.PATH_SAVE)
	    
	return
    
    def testSaveConfig1(self):
	"""
	need to ensure that no values get corrupted
	just save out, with no modifications
	"""
	
        # save out to file
        configData = AppUtilsModule.createNewConfigDataObject()
        self.automaton.addConfigToSave(configData)
        AppUtilsModule.saveConfig(configData, configPath=TestSave.PATH_SAVE)


	originalCfg = None
	with open(TestSave.PATH_ORIGINAL) as f:
	    originalCfg = ConfigModule.load(f)
	
	savedCfg = None
	with open(TestSave.PATH_SAVE) as f:
	    savedCfg = ConfigModule.load(f)
	    
	self.assertTrue(originalCfg is not None)
	self.assertTrue(savedCfg is not None)
	
	self.assertEquals(set(originalCfg.keys()), set(savedCfg.keys()))

        for key in originalCfg.keys():
            self.assertEquals(originalCfg[key], savedCfg[key])
	
	
	return
    
    def testSaveConfig2(self):
	"""
	need to ensure that changes get saved out properly
	change some values
	assert that the values got changed
	"""
	
	return
    
    # END class TestSave
    pass




def main():

    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestParse, 'test'))
    suite.addTest(unittest.makeSuite(TestSave, 'test'))
    suite.addTest(unittest.makeSuite(TestAutomaton, 'test'))

    runner = unittest.TextTestRunner()
    runner.run(suite)
    return

if __name__=="__main__":
    main()

