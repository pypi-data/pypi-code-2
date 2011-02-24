from provide.plugin.basetest import PluginTestCase
import unittest

def suite():
    suites = [
        unittest.makeSuite(TestPlugin),
    ]
    return unittest.TestSuite(suites)


class TestPlugin(PluginTestCase):

    pluginName = 'kforge'
    applicationName = '0.2'
    serviceName = '1'

