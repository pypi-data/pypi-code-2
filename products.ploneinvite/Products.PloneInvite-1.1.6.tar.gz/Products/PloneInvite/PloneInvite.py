## This library is free software; you can redistribute it and/or
## modify it under the terms of the GNU  General Public
## License as published by the Free Software Foundation; either
## version 2 of the License, or any later version.

## This library is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
##  General Public License for more details.

## You should have received a copy of the GNU  General Public
## License along with this library; if not, write to the Free Software
## Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

# PortalInvite tool.

from urllib import quote_plus

from Globals import InitializeClass, HTMLFile
from Acquisition import aq_base
from OFS.SimpleItem import SimpleItem
from OFS.ObjectManager import ObjectManager
from AccessControl import ClassSecurityInfo
from OFS.PropertyManager import PropertyManager
from Products.CMFCore.ActionProviderBase import ActionProviderBase
from Products.CMFCore.ActionProviderBase import ActionInformation
from Products.CMFCore.Expression import Expression
from Products.CMFCore.utils import UniqueObject
from Products.CMFCore.utils import getToolByName
from Products.ZCatalog.ZCatalog import manage_addZCatalog
from Products.ZCatalog.CatalogPathAwareness import CatalogPathAware
from Products.BTreeFolder2.BTreeFolder2 import BTreeFolder2, manage_addBTreeFolder
from random import randint
from DateTime import DateTime 

import Permissions
from config import PROJECTNAME, UNIQUE_ID, TOOLNAME

from Products.PloneInvite import PloneInviteMessageFactory as _

class UsedInviteError(Exception):
    pass

class InviteError(Exception):
    pass

class PloneInvite(UniqueObject, ObjectManager, SimpleItem, ActionProviderBase,
        PropertyManager):
    """
    Portal Invite tool, allows users to invite other users. Keeps track
    of who invited whom. Requires support from the portal join template
    to ensure that the invite code is necessary (template is included).
    """

    meta_type = TOOLNAME
    id = UNIQUE_ID
    title = _(u'Allows users to invite new users')
    
    _actions = (
        ActionInformation(id='invite',
                          title=_(u'Invite'),
                          action=Expression( text='string:${portal_url}/invite_form'),
                          condition=Expression( text='python:member and len(portal.plone_invite.getInvitesUser(used=0, sent=0))'),
                          permissions=(Permissions.InvitePortalUsers,),
                          category='user',
                          visible=1),
        ActionInformation(id='generate_invites',
                          title=_(u'Give invitations'),
                          action=Expression( text='string:${portal_url}/user_invites'),
                          condition=Expression( text='python:member and not checkPermission("Manage portal", context)'),
                          permissions=(Permissions.GeneratePortalInvites,),
                          category='user',
                          visible=1),
        )

    manage_options = ( {'label': 'Overview', 'action': 'manage_overview'},
        ) + ActionProviderBase.manage_options \
          + ObjectManager.manage_options + SimpleItem.manage_options \
          + PropertyManager.manage_options

    security = ClassSecurityInfo()

    security.declareProtected(Permissions.ManagePortalInvites, 'manage_overview')
    manage_overview = HTMLFile('dtml/overview', globals())

    def all_meta_types(self, interfaces=None):
        return ()

    def __init__(self, id='', title=''):
        """
        Adds an invites folder to self.
        """
        self.manage_addProperty('days', '7', 'int')
        self.manage_addProperty('plone_invite_email_address', '', 'string')
        manage_addBTreeFolder(self, 'invites', 'Invites')

    security.declarePrivate('_updateCatalog')
    def _updateCatalog(self):
        """Updates the catalog to include the required fields."""
        if not hasattr(aq_base(self), 'Catalog'):
            manage_addZCatalog(self, 'Catalog', 'Invite Catalog')

        c = self.Catalog

        indexes = c.indexes()
        if 'sender' not in indexes:
            c.addIndex('sender', 'FieldIndex')
        if 'recipient' not in indexes:
            c.addIndex('recipient', 'FieldIndex')
        if 'usedstr' not in indexes:
            c.addIndex('usedstr', 'FieldIndex')
        if 'sentstr' not in indexes:
            c.addIndex('sentstr', 'FieldIndex')
        if 'enforceaddressstr' not in indexes:
            c.addIndex('enforceaddressstr', 'FieldIndex')

        columns = c.schema()
        if 'id' not in columns:
            c.addColumn('id')

    security.declarePrivate('manage_afterAdd')
    def manage_afterAdd(self, item, container):
        self._updateCatalog()
        return ObjectManager.manage_afterAdd(self, item, container)

    security.declareProtected(Permissions.GeneratePortalInvites, 'generateInvite')
    def generateInvite(self, sender=None, count=1, userenforce=False, REQUEST=None):
        """
        Creates a new invite and assigns it to a sender.
        """
        for x in range(count):
            suffix = str(randint(1, 10000000000))
            invitecode = self.invites.generateId(prefix='', suffix=suffix)
            invite = InviteToken(invitecode, sender=sender, enforce_address = userenforce)
            self.invites._setObject(invitecode, invite)

    security.declareProtected(Permissions.InvitePortalUsers, 'delInvite')
    def delInvite(self, invitecode):
        """
        Deletes an invite in case it cannot be used for any reason.
        """
        self.invites.manage_delObjects(invitecode)

    # Since the join script runs as Manager:
    security.declareProtected(Permissions.AddPortalUser, 'useInvite')
    def useInvite(self, invitecode, recipient):
        """
        Marks an invite code as used by a specific recipient. Does not
        create the user account. Raises an exception if the invite is
        unusable. Returns silently otherwise.
        """
        obj = self.invites.get(invitecode, None)
        if obj is None or obj.used:
            raise UsedInviteError(_(u'Invalid invite code.'))
        obj.use(recipient)

    security.declarePublic('getJoinFormAddress')
    def getJoinFormAddress(self, invitecode, email):
        """Returns the email address of the invite."""
        obj = self.invites.get(invitecode, None)
        if obj and obj.enforce_address:
            return obj.sent_address
        if obj and not email:
            return obj.sent_address
        return email
    
    security.declarePublic('mailInvite')
    def mailInvite(self, variables = {}):
        """
        Mails an invite. Behaves similarly to plone_utils.sendto().
        """
        urltool = getToolByName(self, 'portal_url')
        portal = urltool.getPortalObject()
        encoding = portal.getProperty('email_charset')
        # Use site e-mail as sender, to modify: Go to ZMI, modify plone_invite
        # tool's 'plone_invite_email_address' property
        if self.getProperty('plone_invite_email_address') != '':
            variables['invite_from_address'] = self.getProperty(
                'plone_invite_email_address')
        else:
            portal = getToolByName(self, 'portal_url')
            variables['invite_from_address'] = portal.getProperty(
                'email_from_address')

        mail_text = self.invite_template(self, **variables)

        # Without encoding, sending mail fails for me - Kees Hink
        #mail_text = mail_text.encode()

        host = self.MailHost
        #host.send(mail_text)
        result = host.secureSend(
            mail_text, 
            variables['invite_to_address'], 
            variables['invite_from_address'],
            #subject=variables['subject'], 
            subtype='plain', 
            charset=encoding, 
            debug=False,
            From=variables['invite_from_address'],
            )
        
    security.declareProtected(Permissions.ManageMemberInvites, 'getInvitesUser')
    def getInviteCode(self, enforce_address=False):
        """Returns an invide code for the authenticated user."""
        invites = self.getInvitesUser(sent=0, used=0)
        if enforce_address:
            # Tries to reuse enforce_address marked as True
            for invite in invites:
                if invite['enforce_address']:
                    return invite['id']
            for invite in invites:
                invitecode = invite['id']
                obj = self.invites.get(invitecode, None)
                obj.enforce()
                return invitecode
            raise InviteError, _(u"You have no invitations")

        for invite in invites:
            if not invite['enforce_address']:
                return invite['id']
        raise InviteError, _(u"You have no invitations")
        
    security.declareProtected(Permissions.ManageMemberInvites, 'getInvitesUser')
    def getInvitesUser(self, sent=None, used=None, enforce_address=None):
        """
        Returns invites for the current user matching specifications.
        """
        user = self.portal_membership.getAuthenticatedMember().getId()
        return self.getInvites(user, sent, used, enforce_address)

    security.declareProtected(Permissions.ManageMemberInvites, 'getInvites')
    def getInvites(self, user=None, sent=None, used=None, enforce_address=None):
        """
        Returns invites matching the given specifications.
        """
        def boolstring(value):
            if value:
                return 'True'
            return 'False'

        if user is None:
            qp = {}
        else:
            qp = {'sender': user}

        if sent is not None:
            qp['sentstr'] = boolstring(sent)
        if used is not None:
            qp['usedstr'] = boolstring(used)
        if enforce_address is not None:
            qp['enforceaddressstr'] = boolstring(enforce_address)

        matches = self.Catalog(**qp)
        result = []
        for item in matches:
            result.append(item.getObject()._invitedict())
        return result

InitializeClass(PloneInvite)

class InviteToken(CatalogPathAware, SimpleItem):
    """
    An invite token. This class provides no ZMI management interface.
    All handling is via the plone_invite tool.
    """
    
    meta_type = 'Invite Token'

    manage_options = (
        {'label': 'Summary', 'action': 'index_html'},
        ) + SimpleItem.manage_options

    security = ClassSecurityInfo()

    _defaults = {
        'cdate': DateTime,          # Date invite was created.
        'udate': None,              # Date invite was claimed.
        'sdate': None,              # Date invite was sent to someone.
        'xdate': None,              # Date invite expires.        
        'used': False,              # Indicates if claimed by recipient or not.
        'sent': False,              # Indicates if sent to anyone or not.
        'sender': '',               # User this invite was assigned to.
        'recipient': '',            # User who claimed it.
        'sent_address': '',         # Address the invite was sent to.
        'enforce_address': False,   # Enforce the email address of the invitation.
        }

    security.declareProtected(Permissions.ManagePortalInvites, 'index_html')
    index_html = HTMLFile('dtml/invite', globals())

    def __init__(self, id, title='', sender='', enforce_address=False):
        self.id = id
        self.sender = sender
        self.enforce_address = enforce_address
        self._setDefaults()

    def _setDefaults(self):
        for key, value in self._defaults.items():
            if not hasattr(aq_base(self), key):
                if callable(value): # For DateTime()
                    setattr(self, key, value())
                else:
                    setattr(self, key, value)

    security.declareProtected(Permissions.ManagePortalInvites, 'title')
    def title(self):
        """Title of token."""
        return "%s - %s" % (self.id, self.sender)

    security.declareProtected(Permissions.ManagePortalInvites, 'usedstr')
    def usedstr(self):
        """Returns the value of used as a string, for the catalog."""
        if self.used:
            return 'True'
        return 'False'

    security.declareProtected(Permissions.ManagePortalInvites, 'sentstr')
    def sentstr(self):
        """Returns the value of sent as a string, for the catalog."""
        if self.sent:
            return 'True'
        return 'False'

    security.declareProtected(Permissions.ManagePortalInvites, 'sentstr')
    def enforceaddressstr(self):
        """Returns the value of sent as a string, for the catalog."""
        if self.enforce_address:
            return 'True'
        return 'False'

    security.declareProtected(Permissions.ManagePortalInvites, 'use')
    def use(self, recipient):
        """
        Use an invite code. Note that a code is used only when claimed
        by a recipient. Merely sending an invite to someone does not
        use it up. The "recipient" parameter refers to the login id of
        the new user.
        """
        if self.expired():
            raise InviteError(_(u'Invite code has expired.'))
            
        if not self.used:
            self.recipient = recipient
            self.udate = DateTime()
            self.used = True
            self.reindex_object()
        else:
            raise UsedInviteError(_(u'Invite code already used by %s.') % self.recipient)
            
    security.declareProtected(Permissions.ManagePortalInvites, 'enforce')
    def expired(self):
        """Returns true if the object is expired."""
        if self.sent:
            if not self.used:
                return self.xdate < DateTime()
            return True
        return False

    security.declareProtected(Permissions.ManagePortalInvites, 'enforce')
    def enforce(self):
        """
        Marks an invite code as enforced.
        """
        self.enforce_address = True
        self.reindex_object()

    security.declareProtected(Permissions.InvitePortalUsers, 'sendTo')
    def sendTo(self, sent_address):
        """
        Mark this invite code as sent to a particular address. This is
        needed when invites are in limited supply.
        """
        itool = self.plone_invite
        days = itool.getProperty('days')
        if not self.sent:
            self.sent_address = sent_address
            self.sdate = DateTime()
            self.sent = True
            self.xdate = self.sdate + days 
            self.reindex_object()
        else:
            raise UsedInviteError(_(u'Invite code already sent to %s.') % self.sent_address)
    
    security.declarePrivate('_invitedict')
    def _invitedict(self):
        """
        Returns invite code details as a dictionary.
        """
        result = {'id': self.getId()}
        for key in self._defaults.keys():
            result[key] = getattr(self, key, None)
        return result

InitializeClass(InviteToken)
