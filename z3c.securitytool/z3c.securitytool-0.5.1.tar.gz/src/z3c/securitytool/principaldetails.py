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
from z3c.securitytool.matrixdetails import MatrixDetails
from z3c.securitytool import interfaces

class PrincipalDetails(MatrixDetails):
    implements(interfaces.IPrincipalDetails)
    adapts(Interface)

    def __call__(self,principal_id, skin=IBrowserRequest):
        """Return all security settings (permissions, groups, roles)
           for all interfaces provided by this context for a
           `principal_id`, and of course we are only after browser views"""

        request = TestRequest()
        applySkin(request, skin)
        pMatrix = {'permissions': [],
                   'permissionTree': [],
                   'roles': {},
                   'roleTree': [],
                   'groups': {}}

        ifaces = tuple(providedBy(self.context))

        for iface in ifaces:
            for view_reg in getViews(iface, IBrowserRequest):
                view = getView(self.context, view_reg, skin)
                if not view:
                    continue
                all_settings = [{name:val} for name,val in
                                 settingsForObject(view) ]

                self.roleSettings, junk = getSettingsForMatrix(view)
                self.updatePrincipalMatrix(pMatrix, principal_id, all_settings)

        principals = zapi.principals()
        principal = principals.getPrincipal(principal_id)

        if principal.groups:
            for group_id in principal.groups:
                gMatrix = {group_id: self(group_id)}
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
        updates the MatrixRoles for the PrincipalDetails class
        """
        for curRole in item.get('principalRoles', ()):
            if curRole['principal'] != principal_id:
                continue

            role = curRole['role']
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
                self.updateRoles(pMatrix,item,role,curRole)
