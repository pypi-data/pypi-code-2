# -*- coding: utf-8 -*-

import grokcore.component as grok
from zope.securitypolicy.interfaces import Allow, Deny
from zope.securitypolicy.securitymap import AnnotationSecurityMap
from zope.securitypolicy.principalrole import AnnotationPrincipalRoleManager
from zope.securitypolicy.interfaces import (
    IPrincipalRoleManager, IPrincipalRoleMap)


class ExtraRoleMap(AnnotationSecurityMap):
    grok.provides(IPrincipalRoleManager)
    grok.implements(IPrincipalRoleManager, IPrincipalRoleMap)
    key = AnnotationPrincipalRoleManager.key
    
    def __init__(self, context):
        super(ExtraRoleMap, self).__init__(context)
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
        row.extend(self._byrow.get(rowentry))
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

    getPrincipalsAndRoles = getAllCells
    getPrincipalsForRole = getRow
    getRolesForPrincipal = getCol
    getSetting = queryCell

    # Add / Del operations
    unsetRoleForPrincipal = AnnotationSecurityMap.delCell
    
    def assignRoleToPrincipal(self, role_id, principal_id):
        AnnotationSecurityMap.addCell(self, role_id, principal_id, Allow)

    def removeRoleFromPrincipal(self, role_id, principal_id):
        AnnotationSecurityMap.addCell(self, role_id, principal_id, Deny)
