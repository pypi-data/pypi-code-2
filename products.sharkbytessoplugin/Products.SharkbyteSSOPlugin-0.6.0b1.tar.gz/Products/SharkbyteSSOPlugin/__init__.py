""" SharkbyteSSOPlugin
Copyright(C), 2006, Sharkbyte Studios Ltd

This program is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License
as published by the Free Software Foundation; either version 2
of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
"""

from AccessControl.Permissions import add_user_folders
from Products.PluggableAuthService.PluggableAuthService import registerMultiPlugin
from SharkbyteSSOPlugin import SharkbyteSSOPlugin, manage_addSharkbyteSSOPlugin

def initialize(context):
    """ Initialize the SharkbyteSSOPlugin """
    registerMultiPlugin(SharkbyteSSOPlugin.meta_type)

    context.registerClass( SharkbyteSSOPlugin
                             , permission=add_user_folders
                             , constructors=( manage_addSharkbyteSSOPlugin
                                            , manage_addSharkbyteSSOPlugin
                                            )
                             , icon='zmi/sso.png'
                             , visibility=None
                             )
