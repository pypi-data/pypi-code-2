import unittest
from kforge.test.customer.plugin.base import PluginTestCase
import os

def suite():
    suites = [
        unittest.makeSuite(TestTrac),
    ]
    return unittest.TestSuite(suites)


class TestTrac(PluginTestCase):

    requiredPlugins = ['svn', 'trac']

    def testHttpClient(self):
        self.createService('svn', 'svn') # Tested by TestSvn.
        urlService = self.getServicePath('trac')
        urlProjectService = self.getProjectServicePath('trac')
        urlProjectServiceEdit = self.getProjectServiceEditPath('trac')
        self.getAssertCode(urlProjectService, 404)
        self.getAssertCode(urlService, 404)
        self.createService('trac', 'trac', wait=False)
        serviceId = self.registry.projects[self.kuiProjectName].services['svn'].id
        params = {'svn': '%s' % serviceId, 'name': 'trac'}
        self.postAssertCode(urlProjectServiceEdit, params) 
        self.waitRunningService('trac')
        self.getAssertContent(urlService, 'Welcome to Trac')
        self.logoutPerson()
        self.getAssertCode(urlService, 401)
        self.setBasicAuthPerson()
        self.getAssertContent(urlService, 'Welcome to Trac')
        self.clearBasicAuth()
        commitMsg = 'Testing subversion with Trac timeline'
        self.svnCheckoutAddCommit('svn', commitMsg)
        self.loginPerson()
        self.getAssertContent(urlService, 'Welcome to Trac')
        # Trac prefers URLs without trailing slashes.
        urlTimeline = urlService + 'timeline/'
        self.getAssertCode(urlTimeline, 301)
        urlTimeline = urlService + 'timeline'
        self.getAssertCode(urlTimeline, 200)
        self.getAssertContent(urlTimeline, commitMsg)

