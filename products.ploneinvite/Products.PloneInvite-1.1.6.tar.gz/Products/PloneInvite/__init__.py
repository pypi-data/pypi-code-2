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

from zope.i18nmessageid import MessageFactory
PloneInviteMessageFactory = MessageFactory('PloneInvite')

from Products.CMFCore import utils, DirectoryView
from config import PROJECTNAME, GLOBALS
 
# FakeMessageFactory for translating strings in scripts - Kees Hink
from AccessControl import ModuleSecurityInfo
from fakemessagefactory import FakeMessageFactory
ModuleSecurityInfo('Products.PloneInvite').declarePublic('FakeMessageFactory')

DirectoryView.registerDirectory('skins', GLOBALS)

def initialize(context):
    """Import the submodules and initialize the registered types."""

    from Products.PloneInvite import PloneInvite

    utils.ToolInit(PROJECTNAME,
                   tools = (PloneInvite.PloneInvite,),
                   icon='tool.gif',
                   ).initialize(context)
