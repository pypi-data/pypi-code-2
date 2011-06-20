import unittest
from kforge.test.customer.plugin.base import PluginTestCase
from kforge.dictionarywords import *

def suite():
    suites = [
        unittest.makeSuite(TestSvn),
    ]
    return unittest.TestSuite(suites)


class TestSvn(PluginTestCase):

    requiredPlugins = ['svn']

    def testHttpClient(self):
        url = self.getServicePath('svn')
        self.getAssertCode(url, 404)
        self.createService('svn', 'svn')
        content = 'svn - Revision 0: /'
        if self.dictionary[SVN_DAV_MOD_PYTHON_ACCESS_CONTROL]:
            if self.dictionary[APACHE_PYTHON_MODULE] == 'mod_wsgi':
                self.getAssertCode(url, 200) # Cookies are accepted.
            else:
                # Todo: Implement DAV svn equivalent in Python for mod_wsgi.
                self.getAssertCode(url, 401) # Cookies not accepted.
        elif self.dictionary[APACHE_PYTHON_MODULE] == 'mod_python':
            self.getAssertContent(url, content, code=200) # Cookies are accepted.
        self.logoutPerson()
        self.getAssertCode(url, 401)
        self.setBasicAuthPerson()
        self.getAssertContent(url, content)
        self.logoutPerson()
        self.getAssertCode(url, 401)
        # Check viewVC location.
        urlSplit = url.strip().split('/')
        urlSplit[2] = 'viewvc/'+urlSplit[2]+''
        url = '/'.join(urlSplit)
        self.getAssertCode(url, 401)
        self.loginPerson()
        self.getAssertContent(url, 'ViewVC Help', code=200)

    def testSubversionClient(self):
        self.createService('svn', 'svn')
        self.svnCheckoutAddCommit('svn', 'Just testing...')
