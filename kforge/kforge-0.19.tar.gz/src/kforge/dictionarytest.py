import unittest
import os
import kforge.dictionary

def suite():
    "Return a TestSuite of kforge.dom TestCases."
    suites = [
        unittest.makeSuite(SystemDictionaryTest),
    ]
    return unittest.TestSuite(suites)


class SystemDictionaryTest(unittest.TestCase):
    "TestCase for the SystemDictionary class."
    
    def setUp(self):
        self.dictionary = kforge.dictionary.SystemDictionary()
    
    def testInit(self):
        self.failUnless(self.dictionary)
    
    def testGetValues(self):
        self.failUnless(self.dictionary.has_key('project_data_dir'))

