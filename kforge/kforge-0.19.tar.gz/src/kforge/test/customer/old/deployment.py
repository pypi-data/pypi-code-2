import unittest

from dm.ioc import *
import kforge.apache.config

# deployment tests
import kforge.apachetest
import kforge.test.deployed_site_test
import kforge.test.customer.kui
import kforge.plugin.davtest
import kforge.plugin.wwwtest

registry = RequiredFeature('DomainRegistry')
if not registry.plugins.has_key('www'):
    newPlugin = registry.plugins.create('www')
if not registry.plugins.has_key('dav'):
    newPlugin = registry.plugins.create('dav')

kforge.apache.config.ApacheConfigBuilder().buildConfigFile()
# reloading of web server will be done in kforge.apache.configtest

def suite():
    suites = [
            kforge.apachetest.suite(),
            kforge.test.deployed_site_test.suite(),
            # kforge.test.customer.kui.suite(),
            # [[TODO: temporarily commented out as broken due to removal of domain_setup]]
            unittest.makeSuite(kforge.plugin.wwwtest.DeploymentTest),
            unittest.makeSuite(kforge.plugin.davtest.DeploymentTest),
        ]
    return unittest.TestSuite(suites)
