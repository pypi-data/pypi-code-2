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
from zope.app.apidoc.presentation import getViewInfoDictionary
from zope.interface import Interface, implements, providedBy
from zope.publisher.browser import TestRequest, applySkin
from zope.component import adapts
from zope.publisher.interfaces.browser import IBrowserRequest
from zope.securitypolicy.interfaces import Allow, Unset, Deny

from z3c.securitytool.globalfunctions import *
from z3c.securitytool import interfaces
from z3c.securitytool.matrixdetails import MatrixDetails


class PermissionDetails(MatrixDetails):
    """Get permission details for a given principal and view.
    Includes the permissions set by the groups the principal belongs to.
    """

    implements(interfaces.IPermissionDetails)
    adapts(Interface)

    def __call__(self,principal_id,view_name, skin=IBrowserRequest):
        self.read_perm = 'zope.Public'
        self.view_name = view_name
        self.skin = skin

        request = TestRequest()
        applySkin(request, skin)
        pMatrix = {'permissions': [],
                   'permissionTree': [],
                   'roles': {},
                   'roleTree': [],
                   'groups': {}}

        ifaces = tuple(providedBy(self.context))

        for iface in ifaces:
            for view_reg in getViews(iface, skin):
                if  view_reg.name == view_name:

                    view = getView(self.context, view_reg, skin)
                    all_settings = [{name:val} for name,val in
                                     settingsForObject(view) ]

                    self.read_perm = \
                             getViewInfoDictionary(view_reg)['read_perm']\
                                or 'zope.Public'

                    self.roleSettings, junk = getSettingsForMatrix(view)
                    
                    self.rolePermMap = self.roleSettings.get(
                                              'rolePermissions', ())

                    self.updatePrincipalMatrix(pMatrix,
                                               principal_id,
                                               all_settings)
                    break

        principals = zapi.principals()
        principal = principals.getPrincipal(principal_id)

        if principal.groups:
            for group_id in principal.groups:
                gMatrix = {group_id: self(group_id,view_name,skin)}
                pMatrix['groups'].update(gMatrix)

            # The following section updates the principalPermissions with
            # the permissions found in the groups assigned. if the permisssion
            # already exists for the principal then we ignore it.
            permList = [x.items()[1][1] for x in pMatrix['permissions']]

            for matrix in gMatrix.values():
                for tmp in matrix['permissions']:
                    gPerm = tmp['permission']
                    if gPerm not in permList:
                        pMatrix['permissions'].append(tmp)

        self.orderRoleTree(pMatrix)
        return pMatrix

    def updateMatrixRoles(self, pMatrix, principal_id, name, item):
        """
        Updates the roles for the PermissionDetails class
        """
        for curRole in item.get('principalRoles', ()):
            if curRole['principal'] != principal_id:
                continue

            role = curRole['role']

            perm = roleProvidesPermission(self.rolePermMap,
                                          role,
                                          self.read_perm )

            if perm != 'Allow' and perm != 'Deny':
                continue

            parentList = item.get('parentList',None)

            if parentList:
                # If we have a parent list we want to populate the tree
                self.updateRoleTree(pMatrix, item,parentList,curRole)

            if curRole['setting'] == Deny:
                try:
                    # Here we see if we have added a security setting with
                    # this role before, if it is now denied we remove it.
                    del pMatrix['roles'][role]
                except:
                    #Cannot delete something that is not there
                    pass
            else:
                self.updateRoles(pMatrix, item,role,curRole)
