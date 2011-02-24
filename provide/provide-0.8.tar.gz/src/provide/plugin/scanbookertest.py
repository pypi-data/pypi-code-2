from provide.plugin.basetest import PluginTestCase
import unittest

def suite():
    suites = [
        unittest.makeSuite(TestPlugin),
    ]
    return unittest.TestSuite(suites)


class TestPlugin(PluginTestCase):

    pluginName = 'scanbooker'
    applicationName = '0.1'
    serviceName = '1'
    applicationLocation = '/home/john/scanbooker-dev/svn/trunk/dist/scanbooker-0.11a.tar.gz'

