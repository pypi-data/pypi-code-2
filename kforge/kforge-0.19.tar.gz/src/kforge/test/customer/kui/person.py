from kforge.test.customer.kui.base import KuiTestCase
import unittest

def suite():
    suites = [
        unittest.makeSuite(TestPersonRegister),
        unittest.makeSuite(TestPersonEntity),
    ]
    return unittest.TestSuite(suites)


class TestPersonRegister(KuiTestCase):

    kuiPersonName = 'admin'
   
    def testRegister(self):
        # Index page.
        content = 'There are %s registered people' % self.registry.persons.count()
        self.getAssertContent(self.urlPersons, content)

        # Search page.
        params = {'userQuery': 'z'}
        url = self.urlPersonSearch
        self.postAssertNotContent(url, params, self.kuiPersonName)
        params = {'userQuery': 'a'}
        self.postAssertContent(url, params, self.kuiPersonName)
    
        # Find page.
        url = self.url_for('person', action='find', id='z')
        self.getAssertNotContent(url, self.kuiPersonName)
        url = self.url_for('person', action='find', id='a')
        self.getAssertContent(url, self.kuiPersonName)


class TestPersonEntity(KuiTestCase):

    def testEntity(self):
        # Create.
        content = 'Please enter desired user details below'
        page = self.getAssertContent(self.urlPersonCreate, content)
        self.registerPerson()

        # Read.
        content = 'profile page for'
        self.getAssertContent(self.urlPersonRead, content)
        content = self.kuiPersonFullname
        self.getAssertContent(self.urlPersonRead, content)

        self.loginPerson()
        self.urlSiteHome = self.url_for('home')
        self.getAssertContent(self.urlSiteHome, 'Logged in as')
        self.getAssertContent(self.urlPersonHome, self.kuiPersonEmail)
        
        # Update.
        self.getAssertContent(self.urlPersonUpdate, 'Edit your profile')
        self.getAssertContent(self.urlPersonUpdate, self.kuiPersonName)
        self.getAssertContent(self.urlPersonUpdate, self.kuiPersonFullname)
        params = {}
        params['submission'] = '1'
        params['password'] = ''
        params['passwordconfirmation'] = ''
        kuiFullnameCorrection = 'newCorrectFullname'
        params['fullname'] = kuiFullnameCorrection
        params['email'] = self.kuiPersonEmail
        self.postAssertCode(self.urlPersonUpdate, params)

        self.getAssertContent(self.urlPersonRead, self.kuiPersonName)
        self.getAssertContent(self.urlPersonRead, kuiFullnameCorrection)
        
        # Delete.
        page = self.getAssertCode(self.urlPersonRead, code=200)
        self.deletePerson()
        page = self.getAssertCode(self.urlPersonRead, code=404)

        self.getAssertNotContent(self.urlSiteHome, 'Logged in')
        self.getAssertContent(self.urlSiteHome, 'Register')

