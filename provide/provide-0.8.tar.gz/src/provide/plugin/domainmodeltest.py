from provide.plugin.basetest import PluginTestCase
import unittest

def suite():
    suites = [
        unittest.makeSuite(TestPlugin),
    ]
    return unittest.TestSuite(suites)


class TestPlugin(PluginTestCase):

    pluginName = 'domainmodel'
    applicationName = '0.3'
    serviceName = '1'
    applicationLocation = '/home/john/desire-dev/svn/trunk/dist/desire-0.3.tar.gz'

