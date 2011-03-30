"""This is an integration "unit" test. It uses PloneTestCase because I'm lazy
"""
import unittest

from Products.CMFCore.utils import getToolByName
from Products.PloneTestCase import PloneTestCase as ptc
from Products.validation import validation

from betahaus.memberprofile.interfaces import IMemberProfileSettingsAdapter
from betahaus.memberprofile.tests.layer import MemberProfileLayer


class TestHomefolder(ptc.PloneTestCase):
    """
    """
    
    layer = MemberProfileLayer

    def afterSetUp(self):
        """This method is called before each single test. It can be used to
        set up common state. Setup that is specific to a particular test 
        should be done in that test method.
        """
        pm = self.portal.portal_membership
        pm.addMember('member', 'secret', ['Member'], [])

        test_username = 'user1'
        test_user_fullname = 'users fullname'
        test_user_pass = 'secret'
        test_user_email = 'user1@host.com'
        
        pm.addMember(test_username,
                     test_user_pass,
                     ['Member'],
                     [],
                     {'email': test_user_email, 'fullname': test_user_fullname})


    def beforeTearDown(self):
        """This method is called after each single test. It can be used for
        cleanup, if you need it. Note that the test framework will roll back
        the Zope transaction at the end of each test, so tests are generally
        independent of one another. However, if you are modifying external
        resources (say a database) or globals (such as registering a new
        adapter in the Component Architecture during a test), you may want to
        tear things down here.
        """

    def testHomefolderType(self):
        pt = self.portal.portal_types
        memprofile = pt.getTypeInfo('MemberProfile')
        self.failUnless(memprofile)
        #FIXME: Check addable, views etc

    def testLoggedInCreatesMemberArea(self):
        pm = self.portal.portal_membership
        self.login('user1')
        self.assertEqual(pm.getHomeFolder(), None) 
        self.portal.logged_in()
        self.failIfEqual(pm.getHomeFolder(), None)

    def testMemberprofileFirstLastname(self):
        """ We can set firstname / lastname as title too. """
        settings = IMemberProfileSettingsAdapter(self.portal)
        settings.set('title_as','firstname_lastname')
        self.assertEqual(settings.get('title_as'), 'firstname_lastname')
        
        self.login('user1')
        self.portal.logged_in()
        pm = self.portal.portal_membership
        home = pm.getHomeFolder()
        #We need to set firstname and lastname to check this
        home.setFirstname('Mr')
        home.setLastname('Testing')
        self.assertEqual(home.Title(),'Mr Testing')
        self.assertEqual(home.getFirstname(),'Mr')
        self.assertEqual(home.getLastname(),'Testing')

    def testUniqueEmailValidationExists(self):
        v = validation.validatorFor('isUniqueEmail')
        from betahaus.memberprofile.validators import IsUniqueEmail
        self.failUnless(isinstance(v, IsUniqueEmail))

    def testUniqueEmailValidatioOnContent(self):
        """ It shouldn't be possible to change your email address to something
            that already exists.
        """
        pm = self.portal.portal_membership
        pm.addMember('new',
                     'new',
                     ['Member'],
                     [],
                     {'email': 'unique@email.com', 'fullname': 'New user'})

        self.login('new')
        self.portal.logged_in()
        home = pm.getHomeFolder()

        #Validators returns None if they don't have any objections, otherwise string
        field = home.getField('email')
        #This is not an email address
        self.assertEqual(field.validate('hello', home), u"Validation failed(isEmail): 'hello' is not a valid email address.")
        #This already exists
        self.assertEqual(field.validate('user1@host.com', home), u"The email address you entered wasn't unique in this site.")
        #This should work as expected - I.e. return None
        self.assertEqual(field.validate('iam@unique.se', home), None)

    def testUserisInAppRootEmailValidation(self):
        """ Check that users in the zope root are picked up in validation too. """
        #We have to create a profile for a zope user first. The portal owner in tests is a zope user.
        pm = self.portal.portal_membership
        self.loginAsPortalOwner()
        self.portal.logged_in()
        zhome = pm.getHomeFolder()
        zhome.setEmail('super@zope.org')
        
        #Login as other user
        self.login('user1')
        self.portal.logged_in()
        home = pm.getHomeFolder()
        field = home.getField('email')
        self.assertEqual(field.validate('super@zope.org', home), u"The email address you entered wasn't unique in this site.")
        self.assertEqual(field.validate('iam@unique.se', home), None)


def test_suite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)
