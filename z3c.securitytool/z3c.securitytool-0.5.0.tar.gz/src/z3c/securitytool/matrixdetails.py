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

from zope.app import zapi
from zope.securitypolicy.interfaces import Allow, Unset, Deny

class MatrixDetails(object):
    """
    This is the super class of PrincipalDetails and PermissionDetails
    """

    def __init__(self,context):
        """
        init method for the super class
        """
        self.context = context
    
    def updatePrincipalMatrix(self, pMatrix, principal_id, settings):
        """ this method recursively populates the principal permissions
            dict  (MatrixDetails)
        """

        principals = zapi.principals()
        principal = principals.getPrincipal(principal_id)

        for setting in settings:
            for name, item in setting.items():
                self.updateMatrixRoles(pMatrix, principal_id, name,item)
                self.updateMatrixPermissions(pMatrix, principal_id, item)

    def updateMatrixPermissions(self, pMatrix, principal_id, item):
        """ Here we get all the permissions for the given principal
            on the item passed.
        """
            
        for prinPerms in item.get('principalPermissions', ()):
            if principal_id != prinPerms['principal']:
                continue

            # If this method is being used by permissionDetails then
            # we will have a read_perm in the self namespace. If it is
            # the same as curPerm we can continue
            curPerm = prinPerms['permission']
            if getattr(self,'read_perm',curPerm) != curPerm:
                continue
                
            if item.get('parentList',None):
                self.updatePermissionTree(pMatrix, item,prinPerms)

            mapping = {'permission': prinPerms['permission'],
                       'setting'   : prinPerms['setting'],}

            dup = [perm for perm in pMatrix['permissions'] \
                   if perm['permission'] == mapping['permission']]

            if dup:
                # This means we already have a record with this permission
                # and the next record would be less specific so we continue
                continue

            pMatrix['permissions'].append(mapping)

    def orderRoleTree(self,pMatrix):
        # This is silly I know but I want global settings at the end
        try:
            roleTree = pMatrix['roleTree']
            
            globalSettings = roleTree.pop(0)
            roleTree.append(globalSettings)
        except IndexError:
            # Attempting to pop empty list
            pass

    def updateRoleTree(self,pMatrix,item,parentList,curRole):
        """
        This method is responsible for poplating the roletree.
        """
        roleTree = pMatrix['roleTree']

        key = item.get('uid')
        keys =  [x.keys()[0] for x in roleTree]

        # Each key is unique so we just get the list index to edit
        if key in keys:
            listIdx = keys.index(key)
        else:
            roleTree.append({key:{}})
            listIdx = -1

        roleTree[listIdx][key]['parentList'] =  parentList
        roleTree[listIdx][key]['name'] = item.get('name')
        roleTree[listIdx][key].setdefault('roles',[])

        # We make sure we only add the roles we do not yet have.
        if curRole not in roleTree[listIdx][key]['roles']:
            roleTree[listIdx][key]['roles'].append(curRole)

    def updateRoles(self,pMatrix, item,role,curRole):
        if curRole['setting'] == Allow:
            # We only want to append the role if it is Allowed
            roles = pMatrix['roles']
            rolePerms = self.roleSettings['rolePermissions']

            if not roles.has_key(role):
                roles[role] = []

            # Here we get the permissions provided by each role
            for rolePerm in rolePerms:
                if rolePerm['role'] == role:
                    mapping = {'permission': rolePerm['permission'],
                               'setting'   : rolePerm['setting'].getName()
                              }

                    if mapping not in roles[role]:
                        roles[role].append(mapping)

    def updatePermissionTree(self,pMatrix, item,prinPerms):
        """ method responsible for creating permission tree """

        permissionTree = pMatrix['permissionTree']

        key = item.get('uid')
        keys =  [x.keys()[0] for x in permissionTree]

        # Each key is unique so we just get the list index to edit
        if key in keys:
            listIdx = keys.index(key)
        else:
            permissionTree.append({key:{}})
            listIdx = -1

        permissionTree[listIdx][key]['parentList'] = item.get('parentList')
        permissionTree[listIdx][key]['name'] = item.get('name')
        permissionTree[listIdx][key].setdefault('permissions',[])

        if prinPerms not in permissionTree[listIdx][key]['permissions']:
              permissionTree[listIdx][key]['permissions'].append(prinPerms)

