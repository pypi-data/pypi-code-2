import unittest
import StringIO

from dm.config import ConfigFileReader

def suite():
    suites = [
        unittest.makeSuite(TestConfigFileReader),
    ]
    return unittest.TestSuite(suites)


class TestConfigFileReader(unittest.TestCase):
    
    def setUp(self):
        str1 = """[DEFAULT]
var_1: var1
var_2: var2/var1
# core stuff
[core]
var_2 = var2
var_3: /var3/%(var_1)s
"""
        configFile1 = StringIO.StringIO(str1)
        self.configParser = ConfigFileReader()
        self.configParser.readfp(configFile1)
        self.expectedDictionary = {
            'var_1'     : 'var1',
            'var_2'     : 'var2/var1',
            'core.var_1': 'var1',
            'core.var_2': 'var2',
            'core.var_3': '/var3/var1',
        }
    
    def test_convertKey(self):
        keyname = 'sect1.optionA'
        exp = ('sect1', 'optionA')
        out = self.configParser.convertKey(keyname)
        self.assertEqual(exp, out)

    def test___set_item__(self):
        keyname = 'newsection.abc'
        value = 'xyz'
        self.configParser[keyname] = value
        self.assertEqual(value, self.configParser[keyname])

    def test_as_dictionary(self):
        config = self.configParser
        for word in self.expectedDictionary.keys():
            configWord = config[word]
            expectedWord = self.expectedDictionary[word]
            self.assertEquals(configWord, expectedWord)

    def test_has_key(self):
        key1 = 'var_1'
        key2 = 'core.var_2'
        key3 = 'core.xyz'
        key4 = 'nonexistent.blah'
        self.failUnless(self.configParser.has_key(key1))
        self.failUnless(self.configParser.has_key(key2))
        self.failIf(self.configParser.has_key(key3))
        self.failIf(self.configParser.has_key(key4))

    def test_keys(self):
        out = self.configParser.keys()
        exp = ['var_2', 'var_1', 'core.var_3', 'core.var_2', 'core.var_1' ]
        self.assertEqual(exp, out)
        
