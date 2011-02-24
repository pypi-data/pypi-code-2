from provide.plugin.basetest import PluginTestCase
import unittest

def suite():
    suites = [
        unittest.makeSuite(TestPlugin),
    ]
    return unittest.TestSuite(suites)


class TestPlugin(PluginTestCase):

    pluginName = 'desire'
    applicationName = '0.1'
    serviceName = '1'
    applicationLocation = '/home/john/desire-dev/svn/trunk/dist/desire-0.1.tar.gz'

