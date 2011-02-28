from Acquisition import aq_inner
from zope.interface import implements, Interface


from Products.Five import BrowserView
from Products.CMFCore.utils import getToolByName
from Products.statusmessages.interfaces import IStatusMessage

from Products.CMFPlone.PloneBatch import Batch

from zettwerk.users import usersMessageFactory as _


class IUserListView(Interface):
    """
    UserList view interface
    """


class UserListView(BrowserView):
    """
    UserList browser view
    """
    implements(IUserListView)

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.pagesize = 20
        self.selectcurrentbatch = False
        self.selectedusers = []
        self.selectorphan = False

    @property
    def portal_catalog(self):
        return getToolByName(self.context, 'portal_catalog')

    @property
    def portal(self):
        return getToolByName(self.context, 'portal_url').getPortalObject()

    @property
    def portal_membership(self):
        return getToolByName(self.context, 'portal_membership')

    @property
    def portal_groups(self):
        return getToolByName(self.context, 'portal_groups')

    @property
    def plone_url(self):
        return self.portal.absolute_url()

    @property
    def show_select_all_items(self):
        return not self.request.get('select', '').lower() in ('all',
            'batch')

    @property
    def show_select_orphan_items(self):
        return not self.request.get('select', '').lower() in ('orphan',)

    def _getMembers(self):
        """ Returns a list of members """
        return self.portal_membership.listMembers()

    def _getMembersByGroup(self, group_id):
        """ Returns a list of members of a group """
        group = self.portal_groups.getGroupById(group_id)
        if group:
            return group.getGroupMembers()
        return []

    def _getMemberInfo(self, member):
        """ Returns necessary infos of member """
        login_time = member.getProperty('login_time')
        initial_login = str(login_time) != '2000/01/01'
        return {'fullname': member.getProperty('fullname'),
            'username': member.getId(),
            'email': member.getProperty('email'),
            'url': self.plone_url + '/author/' + member.getId(),
            'last_login_time': member.getProperty('last_login_time'),
            'initial_login': initial_login,
            'checked': False}

    def _setChecked(self, member_info, checked=[]):
        """ Updates member_info, sets 'checked': True or False """
        member_info['checked'] = self.selectcurrentbatch\
            or member_info['username'] in self.selectedusers
        if self.selectorphan and not member_info.get('initial_login', True):
            member_info['checked'] = True
        return member_info

    def _getContents(self, group_id):
        """ returns a list of contents """
        if group_id:
            contents = self._getMembersByGroup(group_id)
        else:
            contents = self._getMembers()
        return contents

    def _resetPasswords(self):
        """ Reset password of requested users.
        Returns number of reset password requests  """
        selected_all = not self.show_select_all_items
        selected_orphan = not self.show_select_orphan_items
        ptool = getToolByName(self.context, 'portal_registration')
        group_id = self.request.get('group_id', None)
        if selected_all:
            members = [m.getId() for m in self._getContents(group_id)]
        elif selected_orphan:
            contents = map(self._getMemberInfo, self._getContents(group_id))
            members = [m['username'] for m in contents
                if not m.get('initial_login', False)]
        else:
            members = self.request.get('users')
        if not isinstance(members, (list, tuple)):
            raise(TypeError('members must be list or tuple'))
        ret = 0
        for member in members:
            try:
                ptool.mailPassword(member, self.request)
                ret += 1
            except ValueError:
                # XXX: Logging? but should not happen in reality?
                pass
        return ret

    def _countOrphan(self, members):
        """ Return number of orphan members """
        return sum([int(not m.get('initial_login', False)) for m in members])

    def getUsers(self):
        """ Returns list of users  """
        b_start = self.request.get('b_start', 0)
        show_all = self.request.get('show_all', '').lower() == 'true'
        group_id = self.request.get('group_id', None)
        checked = self.request.get('users', [])
        self.selectcurrentbatch = not self.show_select_all_items
        self.selectorphan = not self.show_select_orphan_items
        if isinstance(checked, basestring):
            checked = [checked]
        if not isinstance(checked, (list, tuple)):
            raise(TypeError('checked must be list or tuple'))
        self.selectedusers = checked

        contents = map(self._getMemberInfo, self._getContents(group_id))

        if show_all:
            pagesize = len(contents)
        else:
            pagesize = self.pagesize
        batch = Batch(contents, pagesize, b_start, orphan=1)
        map(self._setChecked, batch)
        batch.orphans = self._countOrphan(contents)
        return batch

    def __call__(self):
        """ Reset passwords if necessary. Call supers __call__ """
        reset_passwords = self.request.form.get('reset_passwords', None)
        if reset_passwords:
            ret = self._resetPasswords()
            msgid = _(u"userlist_reset_passwords",
                default=u"Passwords of ${count} users resetted",
                mapping={u"count": ret})

            # Use inherited translate() function to get the final text string
            translated = self.context.translate(msgid)

            # Show the final result count to the user as a status message
            messages = IStatusMessage(self.request)
            messages.addStatusMessage(translated, type="info")

            # Redirect to this view, but forget selected items and so on...
            self.request.RESPONSE.redirect(
                self.context.absolute_url() + '/@@userlist_view')
            return None
        return super(UserListView, self).__call__()
