import os.path
import unittest
import kforge.plugin.apacheconfig

def suite():
    suites = [
        unittest.makeSuite(PluginTest),
        ]
    return unittest.TestSuite(suites)

class PluginTest(unittest.TestCase):
    
    def test1(self):
        # [[TODO: test that stuff is actually being rewritten]]
        pass
