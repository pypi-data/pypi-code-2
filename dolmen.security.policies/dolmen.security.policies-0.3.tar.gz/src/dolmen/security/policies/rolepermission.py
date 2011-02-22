# -*- coding: utf-8 -*-

import grokcore.component as grok

from zope.securitypolicy.interfaces import Allow, Deny
from zope.securitypolicy.interfaces import IRolePermissionManager
from zope.securitypolicy.securitymap import AnnotationSecurityMap
from zope.securitypolicy.rolepermission import (
    RolePermissionManager, AnnotationRolePermissionManager)


class ExtraRolePermissionMap(AnnotationSecurityMap):
    grok.provides(IRolePermissionManager)
    grok.implements(IRolePermissionManager)
    key = AnnotationRolePermissionManager.key

    def __init__(self, context):
        super(ExtraRolePermissionMap, self).__init__(context)
        self.context = context
        self.extra = self._compute_extra_data()

    def __nonzero__(self):
        """This is a fix, because zope.securitypolicty tests 'if adapter'
        and we have to be bool-ed to True.
        """
        return True

    def queryCell(self, rowentry, colentry, default=None):
        cell = self.extra.queryCell(rowentry, colentry, default=default)
        if cell is default:
            return AnnotationPrincipalRoleManager.queryCell(
                self, rowentry, colentry, default=default)
        return cell

    def getCol(self, colentry):
        col = self.extra._bycol.get(colentry)
        former = self._bycol.get(colentry)
        if former:
            col.update(former)
        if col:
            return col.items()
        return []

    def getRow(self, rowentry):
        row = self.extra._byrow.get(rowentry)
        if row:
            nrow = self._byrow.get(rowentry)
            if nrow:
                row.update(nrow)
        if row:
            return row.items()
        return []

    def getAllCells(self):
        res = []
        for r in self._byrow.keys():
            for c in self._byrow[r].items():
                res.append((r,) + c)
        res.extend(self.extra.getAllCells())
        return res

    getSetting = queryCell
    getPermissionForRole = getCol
    getRolesForPermission = getRow
    getRolesAndPermissions = getAllCells

    unsetPermissionFromRole = AnnotationSecurityMap.delCell

    def grantPermissionToRole(self, permission_id, role_id, check=True):
        AnnotationSecurityMap.addCell(permission_id, role_id, Allow)

    def denyPermissionToRole(self, permission_id, role_id, check=True):
        AnnotationSecurityMap.addCell(permission_id, role_id, Deny)
