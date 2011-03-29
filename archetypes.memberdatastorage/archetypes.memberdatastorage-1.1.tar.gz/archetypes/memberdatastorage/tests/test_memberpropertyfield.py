"""This is an integration "unit" test. It uses PloneTestCase because I'm lazy
"""


import unittest

from Products.CMFCore.utils import getToolByName

from Products.PloneTestCase import PloneTestCase as ptc

ptc.setupPloneSite()


class TestMemberPropertyField(ptc.PloneTestCase):

    """Test usage of the member property field.
    """

    def afterSetUp(self):

        """This method is called before each single test. It can be used to
        set up common state. Setup that is specific to a particular test 
        should be done in that test method.
        """

        self.membership = getToolByName(self.portal, 'portal_membership')

        # create our own member to mess with
        self.membership.addMember('user1', 'u1', ['Member'], [],
                                  {'email': 'user1@host.com',
                                   'fullname': 'User 1'})

        self.folder.invokeFactory('Document', 'my-doc')
        self.folder.invokeFactory('Document', 'user1')

        from archetypes.memberdatastorage.memberpropertyfield \
            import MemberPropertyField
        
        self.field_id = 'fullname'
        self.initial_value = 'Monty Python'

        for id in ['my-doc', 'user1']:
            page = self.folder[id]
            page.schema.addField(MemberPropertyField(self.field_id))
            page.schema[self.field_id].set(page,self.initial_value)


    def beforeTearDown(self):

        """This method is called after each single test. It can be used for
        cleanup, if you need it. Note that the test framework will roll back
        the Zope transaction at the end of each test, so tests are generally
        independent of one another. However, if you are modifying external
        resources (say a database) or globals (such as registering a new
        adapter in the Component Architecture during a test), you may want to
        tear things down here.
        """

    def _setup_memberarea(self, type='Document'):
        self.membership.memberarea_type = type
        self.membership.memberareaCreationFlag = 1

    def _make_email_field(self, context):
        from archetypes.memberdatastorage.memberpropertyfield \
            import MemberPropertyField
        context.schema.addField(MemberPropertyField('email',default='me@nohost.not'))
        context.schema.initializeLayers(context)

    def test_fallback_use_of_memberpropertyfield(self):

        page = self.folder['my-doc']
        value = page.schema[self.field_id].get(page)
        self.assertEquals(self.initial_value, value)


    def test_default_use_of_memberpropertyfield(self):

        member = self.membership.getMemberById('user1')
        member_value = member.getProperty(self.field_id)

        self.assertEquals(self.initial_value, member_value)

        # and now the other way around
        new_name = 'Buster Keaton'
        member.setMemberProperties({'fullname':new_name})
        page = self.folder['user1']
        content_value = page.schema[self.field_id].get(page)
        
        self.assertEquals(content_value, new_name)


    def test_memberproperty_creation(self):
        
        new_field_id = 'age'
        member = self.membership.getMemberById('user1')
        
        # Assert user doesn't have the property yet
        self.failIf(member.hasProperty('age'))      

        page = self.folder['user1']

        from archetypes.memberdatastorage.memberpropertyfield \
            import MemberPropertyField
        
        page.schema.addField(MemberPropertyField('age',default='youngster'))
        page.schema.initializeLayers(page)  # to trigger the field's initializeLayer
        
        # re-get the member to pick up the update
        member = self.membership.getMemberById('user1')
        
        # Assert member does have the property now
        self.failUnless(member.hasProperty('age')) 
        
        property_value = member.getProperty('age')
        content_value  = page.schema['age'].get(page)
        
        self.assertEquals(property_value, content_value)
        

    def test_memberarea_creation(self):
        #Create a member area
        self._setup_memberarea()
        self.login('user1')
        self.portal.logged_in()
        
        #Add email field and assign value
        home = self.membership.getHomeFolder()
        self._make_email_field(home)
        home.schema['email'].set(home, 'hello@welt.de')
        
        content_email = home.schema['email'].get(home)
        #Just to make sure...
        self.assertEqual('hello@welt.de', content_email)
        
        #It should exist as a property - (If we use getAuthenticatedMember() it won't work)
        member = self.membership.getMemberById('user1')
        property_email = member.getProperty('email')
        
        self.assertEqual(content_email, property_email)

    def test_memberarea_with_escaped_login_name(self):
        self._setup_memberarea()
        userid = email = 'will-be@escaped.now'
        self.membership.addMember(userid, 'u1', ['Member'], [],
                                  {'email': email,
                                   'fullname': 'Escaped User'})

        self.login(userid)
        self.portal.logged_in()
        
        #Add email field and assign value
        home = self.membership.getHomeFolder()
        self._make_email_field(home)
        home.schema['email'].set(home, 'hello@welt.de')
        
        content_email = home.schema['email'].get(home)
        #Just to make sure...
        self.assertEqual('hello@welt.de', content_email)
        
        #It should exist as a property - (If we use getAuthenticatedMember() it won't work)
        member = self.membership.getMemberById(userid)
        property_email = member.getProperty('email')
        
        self.assertEqual(content_email, property_email)


    ## TODO: the fallback could be tested more rigorously; 
    ## test properties other than string type

def test_suite():
    """This sets up a test suite that actually runs the tests in the class
    above
    """
    return unittest.defaultTestLoader.loadTestsFromName(__name__)
