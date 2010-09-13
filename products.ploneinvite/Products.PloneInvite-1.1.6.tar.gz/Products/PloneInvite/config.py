from Products.PloneInvite import PloneInviteMessageFactory as _
from Products.PloneInvite.Permissions import GeneratePortalInvites, \
    InvitePortalUsers, ManageMemberInvites, ManagePortalInvites, AddPortalUser

GLOBALS = globals()
SKINS_DIR = 'skins'

PROJECTNAME = 'PloneInvite' 
UNIQUE_ID = 'plone_invite' 
TOOLNAME = "Portal Invite Tool"

SET_PORTAL_PERMISSIONS= (
    (InvitePortalUsers, ('Authenticated',), 1),
    (ManageMemberInvites, ('Authenticated',), 1),
    # Enable self-registration 
    # (still protected by customized join_form validation)
    (AddPortalUser, ('Anonymous',),1),
    )

SET_CONTROL_PANEL = (
    ('UserInvites', _(u'Member Invitations'), 'string:${portal_url}/user_invites', 
    '', ManagePortalInvites, 'Products', 1, 'UsersGroups',
    'group.gif', ''),
    )
     
SET_SELENIUM_ACTIONS = (
    ('plone_invite','Plone_invite','string:here/get_plone_invite_ftests','',
    'View','ftests'),
    )
