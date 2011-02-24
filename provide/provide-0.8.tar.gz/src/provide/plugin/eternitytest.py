from provide.plugin.basetest import PluginTestCase
import unittest

def suite():
    suites = [
        unittest.makeSuite(TestPlugin),
    ]
    return unittest.TestSuite(suites)


class TestPlugin(PluginTestCase):

    pluginName = 'eternity'
    applicationName = '0.1'
    serviceName = '1'

