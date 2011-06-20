import unittest
from webunit import webunittest

import kforge.soleInstance
import kforge.url

def suite():
    suites = [
        unittest.makeSuite(ModPythonAuthenTest),
        unittest.makeSuite(ModPythonAuthenTest2),
    ]
    return unittest.TestSuite(suites)

class ModPythonAuthenTest(webunittest.WebTestCase):
    """
    Test for project on which guest is excluded
    """
    app = kforge.soleInstance.application
    urlBuilder = kforge.url.UrlBuilderProject()
    
    def setUp(self):
        self.setServer(self.urlBuilder.getFqdn(), '80')
        self.projectName = 'annakarenina'
        self.projectMember = 'levin'
        self.nonMember = 'natasha'
        self.reg = self.app.registry
        project = self.reg.projects[self.projectName]
        self.service = project.services['example']
        self.servicePath = \
            self.urlBuilder.getServicePath(self.service)
    
    def _assertCode(self, url, code):
        page = self.get(url, code)
        if page.code != code:
            msg = 'Expected code: %s, but got %s. Page body: %s' % (code,
                    page.code, page.body)
            self.fail(msg)

    def testNeedAuth(self):
        self.setBasicAuth('anything', 'nothing')
        self._assertCode(self.servicePath, 401)
    
    def testAllowedIn(self):
        self.setBasicAuth('levin', 'levin')
        self._assertCode(self.servicePath, 404)
        self._assertCode(self.servicePath + '/', 404)
        self._assertCode(self.servicePath + '/index.html', 404)
    
    def testCannotAccessWithWrongUser(self):
        self.setBasicAuth('natasha', 'natasha')
        self._assertCode(self.servicePath, 401)

class ModPythonAuthenTest2(webunittest.WebTestCase):
    """
    Test for project on which guest is allowed in
    """
    app = kforge.soleInstance.application
    urlBuilder = kforge.url.UrlBuilderProject()
    
    def setUp(self):
        self.setServer(self.urlBuilder.getFqdn(), '80')
        self.projectName = 'warandpeace'
        self.projectMember = 'natasha'
        self.nonMember = 'levin'
        self.reg = self.app.registry
        project = self.reg.projects[self.projectName]
        self.service = project.services['example']
        self.servicePath = \
            self.urlBuilder.getServicePath(self.service)
    
    def _assertCode(self, url, code):
        page = self.get(url, code)
        if page.code != code:
            msg = 'Expected code: %s, but got %s. Page body: %s' % (code,
                    page.code, page.body)
            self.fail(msg)

    def testDoNotNeedAuth(self):
        self._assertCode(self.servicePath, 404)
    
    def testAllowedIn(self):
        self.setBasicAuth(self.projectMember, self.projectMember)
        self._assertCode(self.servicePath, 404)
        self._assertCode(self.servicePath + '/', 404)
        self._assertCode(self.servicePath + '/index.html', 404)
    
    def testCanAccessWithWrongUser(self):
        self.setBasicAuth(self.nonMember, self.nonMember)
        self._assertCode(self.servicePath, 404)
    
    """
    Not yet working ...
    def testCannotPostAsNonMember(self):
        postdata = {}
        self.post(self.servicePath, postdata, [401])
    """

