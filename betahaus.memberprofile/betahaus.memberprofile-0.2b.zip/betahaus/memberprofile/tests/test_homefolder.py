"""This is an integration "unit" test. It uses PloneTestCase because I'm lazy
"""
import unittest
from Products.CMFCore.utils import getToolByName
from Products.PloneTestCase import PloneTestCase as ptc
from betahaus.memberprofile.tests import base
from betahaus.memberprofile.interfaces import IMemberProfileSettingsAdapter

ptc.setupPloneSite()

class TestHomefolder(base.TestCase):
    """
    """
    
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


def test_suite():
    """This sets up a test suite that actually runs the tests in the class
    above
    """ 
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestHomefolder))
    return suite
