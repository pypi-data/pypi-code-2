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


try:
  from Products.CMFCore import CMFCorePermissions
except ImportError:
  from Products.CMFCore import permissions as CMFCorePermissions

# Assign invites to others
GeneratePortalInvites = 'PloneInvite: Generate Portal Invites' 
# Invite other users
InvitePortalUsers = 'PloneInvite: Invite Portal Users' 
# Manage your own invites
ManageMemberInvites = 'PloneInvite: Manage Member Invites' 

ManagePortalInvites = CMFCorePermissions.ManagePortal
AddPortalUser = CMFCorePermissions.AddPortalMember
