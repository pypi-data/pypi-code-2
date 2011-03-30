import unittest

from Products.CMFCore.utils import getToolByName
from Products.PloneTestCase import PloneTestCase as ptc
from Products.Five.testbrowser import Browser

from betahaus.memberprofile.tests.layer import MemberProfileLayer
from betahaus.memberprofile.interfaces import IMemberProfileSettingsAdapter


class TestBrowser(ptc.FunctionalTestCase):
    """ Browser tests. Added as Python instead of doctests.
    """
    
    layer = MemberProfileLayer

    def test_narrative(self):
        """ Full browser test with expected usage. """
        #Browser Setup
        browser = Browser()
        browser.handleErrors = False
        portal_url = self.portal.absolute_url()

        #User setup
        pm = self.portal.portal_membership

        test_username = 'user1'
        test_user_fullname = 'This other name'
        test_user_pass = 'secret'
        test_user_email = 'user1@host.com'
        
        pm.addMember(test_username,
                     test_user_pass,
                     ['Member'],
                     [],
                     {'email': test_user_email, 'fullname': test_user_fullname})


        #For this test, we're going to use the firstname_lastname
        #convention for member profiles. (See the controlpanel)
        settings = IMemberProfileSettingsAdapter(self.portal)
        settings.set('title_as','firstname_lastname')
        self.assertEqual(settings.get('title_as'),"firstname_lastname")

        #Login the user
        browser.open(portal_url+'/login_form')
        browser.getControl('Login Name').value = test_username
        browser.getControl('Password').value = test_user_pass
        browser.getControl('Log in').click()
        self.failUnless("You are now logged in" in browser.contents)

        browser.open(portal_url+'/Members/user1')
        self.failUnless(browser.url == portal_url+'/Members/user1')
    
        #Check that some content exist
        home = pm.getHomeFolder(test_username)
        self.failUnless(browser.url == portal_url+'/Members/user1')
        self.failUnless(home.getLastname() == '')
        self.failUnless(home.Title() == test_username)

        #Let's add a firstname and lastname
        browser.getLink('Edit').click()
        browser.getControl(name='firstname').value = 'Bing'
        browser.getControl(name='lastname').value = 'van Bong'
        browser.getControl('Save').click()

        self.failUnless("Bing van Bong" in browser.contents)
        self.failUnless(test_user_email in browser.contents)
        self.failUnless(home.Title() == 'Bing van Bong')
        self.failUnless(home.getFirstname() == 'Bing')
        self.failUnless(home.getLastname() == 'van Bong')
        #Fullname should also be in sync
        self.assertEqual(home.Title(),home.getFullname())

        #Let's try out the control panel.
        #We need to login as owner first.
        self.logout()
        self.assertEqual(pm.getAuthenticatedMember().getId(),None)



        #Login
        browser.open(portal_url+'/login_form')
        browser.getControl('Login Name').value = ptc.default_user
        browser.getControl('Password').value = ptc.default_password
        browser.getControl('Log in').click()
        self.failUnless("You are now logged in" in browser.contents)
        
        #This is needed to make the test understand that we're logged in as well.
        #The browser and the test are different things!
        self.login(ptc.default_user)
        self.setRoles(['Manager'], ptc.default_user)
        self.assertEqual(pm.getAuthenticatedMember().getId(), ptc.default_user)
    

        #Going to the control panel, we should be able to change the default content of Title.
        #If we change this to username, the username will be used as title value instead of firstname lastname
        browser.open(portal_url+'/memberprofile-controlpanel')

        #Let's change it back to userid instead of firstname / lastname
        browser.getControl(name='form.title_as').value = ['username']
        browser.getControl('Save').click()
        self.assertEqual(browser.getControl(name='form.title_as').value,['username'])
        self.assertEqual(home.Title(),'user1')

        #We can also talk to the registration tool to this control panel.
        #This is used to set a custom validator for member id.
        #By default it's empty, which means that the default pattern is used.

        regtool = self.portal.portal_registration
        self.assertEqual(regtool.getIDPattern(),'')

        #Now it should only allow lowercase ids
        browser.getControl(name='form.id_pattern').value = '^[a-z][a-z0-9_]*$'
        browser.getControl('Save').click()
        self.assertEqual(regtool.getIDPattern(),u'^[a-z][a-z0-9_]*$')
    
        #When we submit this form with an empty value, the custom id should go back to '',
        #which means that the Plone default will be used.
        browser.getControl(name='form.id_pattern').value = ''
        browser.getControl('Save').click()
        self.assertEqual(regtool.getIDPattern(),'')


def test_suite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)
