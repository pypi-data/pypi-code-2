#
# Testing PortalInvite
#

from Products.PloneInvite.tests.PartecsTesting import PartecsTestCase
from DateTime import DateTime

class TestPloneInviteToolInit(PartecsTestCase):
    """Testing the portal invite class."""
    
    def testUniqueObject(self):
        """Checks the existence of the plone_invite object."""
        self.assert_(hasattr(self.app.plone, 'plone_invite'),
                          'Portal invite missing')
        
                          
class TestPloneInviteInit(PartecsTestCase):
    """Testing the attributes on the portal invite class."""

    def afterSetUp(self):
        super(TestPloneInviteInit, self).afterSetUp()
        self.pi = self.app.plone.plone_invite
    
    def testInvitesFolder(self):
        """Checks the existence of the invites folder."""
        self.assert_(hasattr(self.pi, 'invites'),
                     'Invites folder missing.')
        self.assert_(self.pi.invites.meta_type == "BTreeFolder2",
                     "Error in invites.meta_type")

    def testCatalog(self):
        """Tests Catalog object for Invites folder."""
        self.assert_(hasattr(self.pi, 'Catalog'),
                     'Catalog missing.')
        self.assert_(self.pi.Catalog.meta_type == "ZCatalog",
                     "Error in Catalog.meta_type")
        
        indexes = self.pi.Catalog.indexes()
        for index in ['recipient', 'enforceaddressstr', 'sentstr', 'sender',
                      'usedstr']:
            self.assert_(index in indexes,
                         "Index : %s missing"%index)
            
        columns = self.pi.Catalog.schema()
        self.assert_('id' in columns,
                     "Column : id missing")        
            
    def testProperties(self):
        """Tests Portal invite properties."""
        self.assert_(self.pi.hasProperty('days'),
                     'days property missing.')

    
class TestPloneInvite(PartecsTestCase):
    """Testing the portal invite class."""
    
    def afterSetUp(self):
        super(TestPloneInvite, self).afterSetUp()
        self.switchUser('test_manager')        
        self.pi = self.app.plone.plone_invite

    def testGenerateInvite(self):
        """Tests the generate invites method."""
        numinvites = len(self.pi.invites.objectValues())
        self.pi.generateInvite(sender="test_member", count=4, userenforce=True)
        self.assert_(len(self.pi.invites.objectValues())==4+numinvites,
                     'Invite codes not created.')
        
        self.assert_(len(self.pi.getInvites('test_member'))==4,
                    'getInvites fail.')

        self.assertRaises(Exception, self.pi.getInviteCode)
        
        self.pi.generateInvite(sender="test_manager", count=4, userenforce=True)
        self.assert_(len(self.pi.invites.objectValues())==8+numinvites,
                    'Invite codes not created for test_manager.')
        
        self.assert_(len(self.pi.getInvites('test_member'))==4,
                    'getInvites fail.')
        
        invitecode =self.pi.getInviteCode(True)
        self.pi.delInvite(invitecode)
        
        self.assert_(len(self.pi.getInvites('test_manager'))==3,
                    'getInvites fail.')

class TestInviteToken(PartecsTestCase):
    """Testing the invite token class."""
    
    def afterSetUp(self):
        super(TestInviteToken, self).afterSetUp()
        self.pi = self.app.plone.plone_invite
        self.switchUser('test_manager')        
        self.pi.generateInvite(sender="test_member", count=4, userenforce=True)
        self.switchUser('test_member')        
        invitecode = self.pi.getInviteCode(True)
        self.token = self.pi.invites.get(invitecode)

    def testGenerateInvite(self):
        """Tests invite token attributes."""
        attrs = ['cdate', 'udate', 'sdate','xdate', 'used', 'sent', 'sender',                 
                 'recipient', 'sent_address', 'enforce_address']
        for attr in attrs:
            self.assert_(hasattr(self.token, attr),
                         "Attribute %s missing"%attr)

    def testQuery(self):
        """Tests a token query."""
        result = self.pi.getInvitesUser()
        token = result[0]
        keys = ['cdate', 'udate', 'sdate','xdate', 'used', 'sent', 'sender',                 
                'recipient', 'sent_address', 'enforce_address']
        for key in keys:
            self.assert_(token.has_key(key),
                         "Key %s missing."%key)
        
    
def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestPloneInviteToolInit))    
    suite.addTest(makeSuite(TestPloneInviteInit))
    suite.addTest(makeSuite(TestPloneInvite))
    suite.addTest(makeSuite(TestInviteToken))        
    return suite
