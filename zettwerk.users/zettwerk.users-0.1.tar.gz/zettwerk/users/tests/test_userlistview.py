from base import TestCase
from zope.component import getMultiAdapter
from zope.component import getSiteManager
from zope.publisher.browser import TestRequest
from Products.MailHost.interfaces import IMailHost
from collective.MockMailHost.MockMailHost import MockMailHost

from DateTime import DateTime

from Products.CMFCore.utils import getToolByName


# monkey patch MockMailHosts send method.
# the original one just takes msg an no keywords.
def send_patch(self, messageText,
    mto=None,
    mfrom=None,
    subject=None,
    encode=None,
    immediate=False,
    charset=None,
    msg_type=None,):
    self.messages.append(messageText)
MockMailHost.send = send_patch
# /monkey patch


class TestUserListView(TestCase):

    def afterSetUp(self):
        self.setRoles(('Manager',))
        self.rtool = getToolByName(self.portal, 'portal_registration')
        self.gtool = getToolByName(self.portal, 'portal_groups')
        self.mtool = getToolByName(self.portal, 'portal_membership')

        # override the Mailhost. I need a collevtive.MockMailHost here!!
        sm = getSiteManager()
        sm.registerUtility(self.portal.MailHost, IMailHost)

        self.gtool.addGroup('group1')
        gr1 = self.gtool.getGroupById('group1')
        self.gtool.addGroup('group2')
        gr2 = self.gtool.getGroupById('group2')

        self.rtool.addMember('Member1', '12345',
            roles=('Member',),
            properties={'fullname': 'John Doe 1',
                'username': 'Member1',
                'email': 'test1@example.com'})
        gr1.addMember('Member1')

        self.rtool.addMember('Member2', '12345',
            roles=('Member',),
            properties={'fullname': 'Jane Doe 1',
                'username': 'Member2',
                'email': 'test2@example.com'})
        gr1.addMember('Member2')

        self.rtool.addMember('Member3', '12345',
            roles=('Member',),
            properties={'fullname': 'John Doe 2',
                'username': 'Member3',
                'email': 'test3@example.com'})
        gr2.addMember('Member3')

        self.rtool.addMember('Member4', '12345',
            roles=('Member',),
            properties={'fullname': 'Jane Doe 2',
                'username': 'Member4',
                'email': 'test4@example.com'})

    def test__getMembers(self):
        request = TestRequest()
        view = getMultiAdapter((self.portal, request), name='userlist_view')

        ret = view._getMembers()
        self.assertEquals(len(ret), 5)

    def test__getMembersByGroup(self):
        request = TestRequest()
        view = getMultiAdapter((self.portal, request), name='userlist_view')

        ret = view._getMembersByGroup('group2')
        self.assertEquals(len(ret), 1)
        self.assertEquals(ret[0].getId(), 'Member3')

        ret = view._getMembersByGroup('xxx')
        self.assertEquals(len(ret), 0)

    def test__getMemberInfo(self):
        request = TestRequest()
        view = getMultiAdapter((self.portal, request), name='userlist_view')
        member = self.mtool.getMemberById('Member4')

        ret = view._getMemberInfo(member)
        self.assertEquals(ret, {'fullname': 'Jane Doe 2',
            'username': 'Member4',
            'email': 'test4@example.com',
            'url': 'http://nohost/plone/author/Member4',
            'last_login_time': DateTime('2000/01/01'),
            'initial_login': False,
            'checked': False})

    def test__getMemberInfo_logged_in(self):
        request = TestRequest()
        view = getMultiAdapter((self.portal, request), name='userlist_view')
        member = self.mtool.getMemberById('Member4')
        member.setMemberProperties(
            {'login_time': DateTime('2011/02/25 11:15:19.034939 GMT+1'),
            'last_login_time': DateTime('2011/02/25 09:15:10.034213 GMT+1')})

        ret = view._getMemberInfo(member)
        self.assertEquals(ret, {'fullname': 'Jane Doe 2',
            'username': 'Member4',
            'email': 'test4@example.com',
            'url': 'http://nohost/plone/author/Member4',
            'last_login_time': DateTime('2011/02/25 09:15:10.034213 GMT+1'),
            'initial_login': True,
            'checked': False})

    def test_getUsers_all(self):
        request = TestRequest()
        view = getMultiAdapter((self.portal, request), name='userlist_view')

        ret = view.getUsers()
        self.assertEquals(len(ret), 5)

    def test_getUsers_batching(self):
        request = TestRequest()
        view = getMultiAdapter((self.portal, request), name='userlist_view')
        view.pagesize = 2

        ret = view.getUsers()
        self.assertEquals(len(ret), 2)

    def test_getUsers_batching_show_all(self):
        request = TestRequest(show_all='True')
        view = getMultiAdapter((self.portal, request), name='userlist_view')
        view.pagesize = 2

        ret = view.getUsers()
        self.assertEquals(len(ret), 5)

    def test_getUsers_by_group(self):
        request = TestRequest(group_id='group1')
        view = getMultiAdapter((self.portal, request), name='userlist_view')

        ret = view.getUsers()
        self.assertEquals(len(ret), 2)

    def test_getUsers_batch_select_batch(self):
        request = TestRequest(select='batch')
        view = getMultiAdapter((self.portal, request), name='userlist_view')
        view.pagesize = 2

        ret = view.getUsers()
        self.assertEquals(len(ret), 2)
        self.assertEquals(ret[0]['checked'], True)
        self.assertEquals(ret[1]['checked'], True)

    def test_getUsers_batch_selected_users(self):
        request = TestRequest(users=['Member1'])
        view = getMultiAdapter((self.portal, request), name='userlist_view')
        view.pagesize = 2

        ret = view.getUsers()
        self.assertEquals(len(ret), 2)
        self.assertEquals(ret[0]['checked'], True)
        self.assertEquals(ret[1]['checked'], False)

    def test_getUsers_batch_selected_users_string_type(self):
        request = TestRequest(users='Member1')
        view = getMultiAdapter((self.portal, request), name='userlist_view')
        view.pagesize = 2

        ret = view.getUsers()
        self.assertEquals(len(ret), 2)
        self.assertEquals(ret[0]['checked'], True)
        self.assertEquals(ret[1]['checked'], False)

    def test_getUsers_batch_selected_users_wrong_type(self):
        request = TestRequest(users=1)
        view = getMultiAdapter((self.portal, request), name='userlist_view')
        view.pagesize = 2

        self.assertRaises(TypeError, view.getUsers)

    def test_getUsers_all_select_orphan(self):
        request = TestRequest(select='orphan')
        view = getMultiAdapter((self.portal, request), name='userlist_view')
        view.pagesize = 2
        member = self.mtool.getMemberById('Member2')
        member.setMemberProperties(
            {'login_time': DateTime('2011/02/25 11:15:19.034939 GMT+1'),
            'last_login_time': DateTime('2011/02/25 09:15:10.034213 GMT+1')})

        ret = view.getUsers()
        self.assertEquals(len(ret), 2)
        self.assertEquals(ret[0]['checked'], True)
        self.assertEquals(ret[1]['checked'], False)
        self.assertEquals(ret.orphans, 4)

    def test__setChecked(self):
        request = TestRequest()
        view = getMultiAdapter((self.portal, request), name='userlist_view')
        view.selectedusers = ['Member2']
        member1 = {'username': 'Member1'}
        member2 = {'username': 'Member2'}

        ret = view._setChecked(member1)
        self.assertEquals(ret, {'username': 'Member1',
            'checked': False})

        ret = view._setChecked(member2)
        self.assertEquals(ret, {'username': 'Member2',
            'checked': True})

    def test__setChecked_select_batch(self):
        request = TestRequest()
        view = getMultiAdapter((self.portal, request), name='userlist_view')
        view.selectcurrentbatch = True
        member1 = {'username': 'Member1'}
        member2 = {'username': 'Member2'}

        ret = view._setChecked(member1)
        self.assertEquals(ret, {'username': 'Member1',
            'checked': True})

        ret = view._setChecked(member2)
        self.assertEquals(ret, {'username': 'Member2',
            'checked': True})

    def test__setChecked_user_checked(self):
        request = TestRequest()
        view = getMultiAdapter((self.portal, request), name='userlist_view')
        view.selectcurrentbatch = False
        view.selectedusers = ['Member1']
        member1 = {'username': 'Member1'}
        member2 = {'username': 'Member2'}

        ret = view._setChecked(member1)
        self.assertEquals(ret, {'username': 'Member1',
            'checked': True})

        ret = view._setChecked(member2)
        self.assertEquals(ret, {'username': 'Member2',
            'checked': False})

    def test__setChecked_select_orphan(self):
        request = TestRequest()
        view = getMultiAdapter((self.portal, request), name='userlist_view')
        view.selectcurrentbatch = False
        view.selectorphan = True
        member1 = {'username': 'Member1', 'initial_login': True}
        member2 = {'username': 'Member2', 'initial_login': False}

        ret = view._setChecked(member1)
        self.assertEquals(ret, {'username': 'Member1',
            'checked': False, 'initial_login': True})

        ret = view._setChecked(member2)
        self.assertEquals(ret, {'username': 'Member2',
            'checked': True, 'initial_login': False})

    def test__resetPasswords_all(self):
        request = TestRequest(select='all')
        view = getMultiAdapter((self.portal, request), name='userlist_view')

        ret = view._resetPasswords()
        # 4 because there is a default test_user_1_ without configured
        # mail address
        self.assertEquals(ret, 4)
        self.assertEquals(len(self.portal.MailHost.messages), 4)

    def test__resetPasswords_users(self):
        request = TestRequest(users=['Member1', 'Member2'])
        from zope.annotation.interfaces import IAttributeAnnotatable
        from zope.interface import alsoProvides
        alsoProvides(request, IAttributeAnnotatable)
        view = getMultiAdapter((self.portal, request), name='userlist_view')

        ret = view._resetPasswords()
        self.assertEquals(ret, 2)
        self.assertEquals(len(self.portal.MailHost.messages), 2)

    def test__resetPasswords_all_filtered_by_group(self):
        request = TestRequest(select='all', group_id='group1')
        view = getMultiAdapter((self.portal, request), name='userlist_view')

        ret = view._resetPasswords()
        self.assertEquals(ret, 2)
        self.assertEquals(len(self.portal.MailHost.messages), 2)

    def test__resetPasswords_all_not_yet_logged_in(self):
        request = TestRequest(select='orphan')
        view = getMultiAdapter((self.portal, request), name='userlist_view')
        member = self.mtool.getMemberById('Member4')
        member.setMemberProperties(
            {'login_time': DateTime('2011/02/25 11:15:19.034939 GMT+1'),
            'last_login_time': DateTime('2011/02/25 09:15:10.034213 GMT+1')})

        ret = view._resetPasswords()
        self.assertEquals(ret, 3)
        self.assertEquals(len(self.portal.MailHost.messages), 3)

    def test__countOrphan(self):
        request = TestRequest()
        view = getMultiAdapter((self.portal, request), name='userlist_view')
        view.selectcurrentbatch = False
        view.selectedusers = ['Member1']
        member1 = {'username': 'Member1', 'initial_login': True}
        member2 = {'username': 'Member2', 'initial_login': False}
        member3 = {'username': 'Member3'}

        members = [member1, member2, member3]

        ret = view._countOrphan(members)
        self.assertEquals(ret, 2)
