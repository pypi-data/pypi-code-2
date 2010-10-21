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

from zope.interface import Interface

class ISecurityChecker(Interface):

    def getPermissionSettingsForAllViews(self,interfaces,skin,selectedPermission=None):
        """ gets the permission settings for all views"""
    def aggregateMatrices(self):
        """ aggregates the two matricies together """
        
    def getReadPerm(self,view_reg):
        """ gets the read permission for the view """
        
    def populateMatrix(self,viewInstance,view_reg):
        """ workhorse of the SecurityChecker class """
        
    def updateRolePermissionSetting(self,permSetting,principal,role,name):
        """ updates the permission settings """
        
    def populatePermissionMatrix(self,read_perm,principalPermissions):
        """ populates the permission matrix """

class IPrincipalDetails(Interface):
    def updateMatrixPermissions( item):
        """ method to update the permissions """

    def updateMatrixRoles( name, item):
        """ method to up date the matrix roles """

    
class IPermissionDetails(Interface):
    def updateMatrixPermissions( item):
        """ method to update the permissions """

    def updateMatrixRoles( name, item):
        """ method to up date the matrix roles """

class IMatrixDetails(Interface):
    def principalPermissions(principal_id, skin):
        """ main workhorse of the class """
    def orderRoleTree(self):
        """ This is an ordering method for the roleTree """
        
    def updatePrincipalMatrix( settings):
        """ this is called to update the roles and permissions"""
        
    def updateRoles(item,role,curRole):
        """ method to update the roles """

    def updateRoleTree(item,parentList,curRole):
        """ method to update the matrix roletree """
        
    def updatePermissionTree(item,prinPerms):
        """ method to update the permission tree """

