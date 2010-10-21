##############################################################################
#
# Copyright (c) 2008 Zope Foundation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################

import transaction
from zope.app.folder import Folder
from zope.app import zapi
from zope.app.appsetup.bootstrap import getInformationFromEvent
from zope.securitypolicy.interfaces import IPrincipalPermissionManager
from zope.securitypolicy.interfaces import IPrincipalRoleManager


class Participation:
    interaction = None
    
class CreateStructure(object):
    def __init__(self,event):
        """ This method gets called on IDatabaseOpenedEvent when running the
            Demo we add some seemingly random security permissions to the
            folder tree created below so users of the demo can see what
            security tool can display
        """
        db, connection, root, root_folder = getInformationFromEvent(event)
        # Lets get the root folder so we can assign some permissions to
        # specific contexts
        root=zapi.getRoot(root_folder)

        # If the following folders do not exist... lets create them
        if 'Folder1' not in root:
            root['Folder1'] = Folder()

        if 'Folder2' not in root['Folder1']:
            root['Folder1']['Folder2'] = Folder()
            
        if 'Folder3' not in root['Folder1']['Folder2']:
            root['Folder1']['Folder2']['Folder3'] = Folder()

        # Lets get the list of all principals on the system.
        sysPrincipals = zapi.principals()
        principals = [x.id for x in sysPrincipals.getPrincipals('')
                    if x.id not in ['zope.group1','zope.group2','zope.randy']]

# Here is where we begin to set the permissions for the root context level
        roleManager = IPrincipalRoleManager(root)
        permManager = IPrincipalPermissionManager(root)
        roleManager.assignRoleToPrincipal('zope.Editor', 'zope.group1')

        # Here we assign the group group1 to zope.daniel and zope.randy

        group1  = sysPrincipals.getPrincipal('zope.group1')
        group2  = sysPrincipals.getPrincipal('zope.group2')
        
        daniel  = sysPrincipals.getPrincipal('zope.daniel')
        randy  = sysPrincipals.getPrincipal('zope.randy')

        # We add group1 and group2 to Randy to make sure that the
        # allow permission overrides the Deny permission at the
        # same level.
        randy.groups.append('zope.group1')
        randy.groups.append('zope.group2')


        # We add randy as a group to daniel with a subgroup
        # of group1 and and group2
        daniel.groups.append('zope.randy')

        
        roleManager.assignRoleToPrincipal('zope.Writer', 'zope.daniel')
        roleManager.assignRoleToPrincipal('zope.Writer', 'zope.stephan')

        for principal in principals:
            permManager.grantPermissionToPrincipal('concord.ReadIssue',
                                              principal)
            permManager.denyPermissionToPrincipal('concord.DeleteArticle',
                                              principal)
            permManager.denyPermissionToPrincipal('concord.CreateArticle',
                                              principal)


# Now at the root level we will deny all the permissions to group2 and
# Allow all the permissions to group 1
        for perm in ['concord.DeleteIssue', 'concord.CreateIssue',
                     'concord.ReadIssue', 'concord.CreateArticle',
                     'concord.DeleteArticle', 'concord.PublishIssue']:
                     
            permManager.denyPermissionToPrincipal(perm, group1.id)
            permManager.grantPermissionToPrincipal(perm,group2.id)



# Here is where we begin to set the permissions for the context level of
# Folder1.
        roleManager = IPrincipalRoleManager(root['Folder1'])
        permManager = IPrincipalPermissionManager(root['Folder1'])

        roleManager.assignRoleToPrincipal('zope.Janitor', 'zope.markus')
        roleManager.assignRoleToPrincipal('zope.Writer', 'zope.daniel')

        for principal in principals:
            permManager.denyPermissionToPrincipal('concord.ReadIssue',
                                              principal)
            permManager.grantPermissionToPrincipal('concord.DeleteIssue',
                                              principal)
            permManager.grantPermissionToPrincipal('concord.CreateArticle',
                                              principal)


# Here is where we begin to set the permissions for the context level of
# /root/Folder1/Folder2.
        roleManager = IPrincipalRoleManager(root['Folder1']['Folder2'])
        permManager = IPrincipalPermissionManager(root['Folder1']['Folder2'])

        roleManager.assignRoleToPrincipal('zope.Janitor', 'zope.markus')
        roleManager.assignRoleToPrincipal('zope.Writer', 'zope.daniel')

        permManager.denyPermissionToPrincipal('concord.CreateArticle',
                                              'zope.daniel')
        permManager.denyPermissionToPrincipal('concord.CreateIssue',
                                              'zope.daniel')
        permManager.denyPermissionToPrincipal('concord.CreateIssue',
                                              'zope.stephan')
        permManager.denyPermissionToPrincipal('concord.CreateIssue',
                                              'zope.markus')
        permManager.denyPermissionToPrincipal('concord.CreateIssue',
                                              'zope.anybody')

# Here is where we begin to set the permissions for the context level of
# /root/Folder1/Folder2/Folder3.
        roleManager = IPrincipalRoleManager(root['Folder1']\
                                                ['Folder2']\
                                                ['Folder3'])
        permManager = IPrincipalPermissionManager(root['Folder1']\
                                                      ['Folder2']\
                                                      ['Folder3'])

        
        roleManager.removeRoleFromPrincipal('zope.Writer','zope.daniel')
        roleManager.removeRoleFromPrincipal('zope.Janitor', 'zope.markus')

        transaction.commit()
