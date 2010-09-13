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

from Products.Archetypes.public import listTypes
from Products.Archetypes.Extensions.utils import installTypes, install_subskin
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.DirectoryView import addDirectoryViews

from Products.PloneInvite.config import SET_CONTROL_PANEL, PROJECTNAME, \
    GLOBALS, SET_PORTAL_PERMISSIONS


from StringIO import StringIO

def setupControlPanel(portal, SET_CONTROL_PANEL, REQUEST=None):
    """Adds control panel actions."""
    cptool = getToolByName(portal, 'portal_controlpanel')
    action_list = [action.id for action in cptool.listActions()]
    for id, name, action, condition, permission, category, \
            visible, appId, imageUrl, description in SET_CONTROL_PANEL:
        index_list = []
        if id in action_list:
            index_list.append(action_list.index(id))
            
            if index_list:
                cptool.deleteActions(index_list)
                ait = getToolByName(portal, 'portal_actionicons')
                ait.removeActionIcon(category, action_id=id)
                
        cptool.addAction(id, name, action, condition, permission, \
             category, visible, appId, imageUrl, description)


def setupPortalPermissions(portal, permissions):
    """Sets up some default Portal Permissions"""
    for permission, roles, flag in permissions:
        try:
            portal.manage_permission(permission, roles, flag)
        except ValueError:
            pass


def install(self):
    out = StringIO()
    installTypes(self, out, listTypes(PROJECTNAME), PROJECTNAME)

    #installing subskins
    skins_tool = getToolByName(self, 'portal_skins')
    addDirectoryViews(skins_tool, 'skins', GLOBALS)
    
    partecs_skins = ['ploneinvite',]

    for skin_name, skin_path in skins_tool.getSkinPaths():
        path_elems = [p.strip() for p in skin_path.split(',')]
        for skin in partecs_skins:
            if skin not in path_elems:
                path_elems.insert(1, skin)
        for notskin in ('.svn','CVS'):
            if notskin in path_elems:
                path_elems.remove(notskin)
        new_path = ', '.join(path_elems)
        skins_tool.addSkinSelection(skin_name, new_path)

    print >> out, "Installed skins for %s." % PROJECTNAME

    portal = getToolByName(self, 'portal_url').getPortalObject()

    setupControlPanel(portal, SET_CONTROL_PANEL)
    setupPortalPermissions(portal, SET_PORTAL_PERMISSIONS)

    if hasattr(self, 'plone_invite'):        
        self.plone_invite._updateCatalog()
        for invite in self.plone_invite.invites.objectValues():
            invite._setDefaults() # Upgrade properties
        print >> out, "plone_invite tool already exists. \
            Updated catalog and invite codes."
    else:
        self.manage_addProduct['PloneInvite'].manage_addTool(
            type = 'Portal Invite Tool')
        print >> out, "Added plone_invite tool."

        
    self.portal_actions.addActionProvider('plone_invite')
    print >> out, "Added plone_invite to action providers."

    print >> out, "Successfully installed %s." % PROJECTNAME
    return out.getvalue()

def uninstall(self):
    out=StringIO()
    
    portal = getToolByName(self, 'portal_url').getPortalObject()
    cptool = getToolByName(portal, 'portal_controlpanel')
    action_list = [action.id for action in cptool.listActions()]
    for id, name, action, condition, permission, category, \
            visible, appId, imageUrl, description in SET_CONTROL_PANEL:
        index_list = []
        if id in action_list:
            index_list.append(action_list.index(id))
            
            if index_list:
                cptool.deleteActions(index_list)
                ait = getToolByName(portal, 'portal_actionicons')
                ait.removeActionIcon('controlpanel', action_id=id)


    out.write('manual uninstall completed.\n')
    return out.getvalue()

