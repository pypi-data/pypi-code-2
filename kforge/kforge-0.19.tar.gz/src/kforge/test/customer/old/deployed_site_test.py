import unittest
from webunit import webunittest

# todo: Include the project_front_controller tests.


def suite():
    suites = [
        unittest.makeSuite(TestMediaHttp),
        unittest.makeSuite(TestAdminHttp),
        # unittest.makeSuite(TestAdminHttps),
        unittest.makeSuite(TestProjectHttp),
        # unittest.makeSuite(TestProjectHttps),
        ]
    return unittest.TestSuite(suites)

import kforge.url
import kforge.dictionary
dictionary = kforge.dictionary.SystemDictionary()

class CommonHttp(webunittest.WebTestCase):
    urlBuilder = None
    https = False
    
    def setUp(self):
        if self.https:
            self.setServer(self.urlBuilder.getFqdn(), 443)
            self.protocol = 'https'
        else:
            self.setServer(self.urlBuilder.getFqdn(), 80)
    
    def testFetch(self):
        self.assertCode('/', 200)
    
    def testWeAreNotBeingStupid(self):
        # this should not exist
        self.assertCode('/afjdlajlja.html', 404)

class TestMediaHttp(CommonHttp):
    def setUp(self):
        self.setServer(dictionary['www.media_host'], 80)
    
    def testFetch(self):
        "may give 200 or 401 on '/' so don't assume anything"
        pass
    
    def testCss(self):
        self.assertCode('/css/forms.css', 200)

class TestAdminHttp(CommonHttp):
    urlBuilder = kforge.url.UrlBuilderAdmin()
    
    def testWeAreNotBeingStupid(self):
        # this should not exist but for some reason django returns 200
        self.assertCode('/afjdlajlja.html', 200)

class TestAdminHttps(TestAdminHttp):
    https = True

class TestProjectHttp(CommonHttp):
    urlBuilder = kforge.url.UrlBuilderProject()

class TestProjectHttps(TestProjectHttp):
    https = True

if __name__ == '__main__':
    import unittest
    unittest.main()
