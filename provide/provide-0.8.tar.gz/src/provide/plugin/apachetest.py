from provide.plugin.basetest import PluginTestCase
import unittest

def suite():
    suites = [
        unittest.makeSuite(TestPlugin),
    ]
    return unittest.TestSuite(suites)


class TestPlugin(PluginTestCase):

    pluginName = 'apache'
    provisionLocation = 'http://mirrors.enquira.co.uk/apache/httpd/'
    applicationName = '2.2.11'
    serviceName = 'productiontest'
    applicationDependencies = {
        'mod_python': 'http://mirror.lividpenguin.com/pub/apache/httpd/modpython/mod_python-3.3.1.tgz',
        'subversion': 'http://subversion.tigris.org/downloads/subversion-1.5.6.tar.gz',
        'mod_fastcgi': 'http://www.fastcgi.com/dist/mod_fastcgi-2.4.6.tar.gz',
        'serf': 'http://serf.googlecode.com/files/serf-0.3.0.tar.bz2',
    }


