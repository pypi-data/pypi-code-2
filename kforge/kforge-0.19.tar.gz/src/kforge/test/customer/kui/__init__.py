from webunit import webunittest
import unittest
from kforge.test.customer.kui.base import KuiTestCase

def suite():
    import kforge.test.customer.kui.admin
    import kforge.test.customer.kui.person
    import kforge.test.customer.kui.project
    import kforge.test.customer.kui.member
    import kforge.test.customer.kui.service
    suites = [
        unittest.makeSuite(TestVisitServer),
        kforge.test.customer.kui.admin.suite(),
        kforge.test.customer.kui.person.suite(),
        kforge.test.customer.kui.project.suite(),
        kforge.test.customer.kui.member.suite(),
        kforge.test.customer.kui.service.suite(),
    ]
    return unittest.TestSuite(suites)


class TestVisitServer(KuiTestCase):
   
    def testHome(self):
        url = self.url_for('home')
        self.getAssertContent(url, 'Welcome to')
    
    def testUserLogin(self):
        url = self.url_for('login')
        self.getAssertContent(url, 'Log in')

