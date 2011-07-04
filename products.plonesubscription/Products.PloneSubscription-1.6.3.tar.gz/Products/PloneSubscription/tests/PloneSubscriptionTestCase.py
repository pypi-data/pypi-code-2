# -*- coding: utf-8 -*-
## PloneSubscription
## A Plone tool supporting different levels of subscription and notification
## Copyright (C)2006 Ingeniweb

## This program is free software; you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation; either version 2 of the License, or
## (at your option) any later version.

## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.

## You should have received a copy of the GNU General Public License
## along with this program; see the file COPYING. If not, write to the
## Free Software Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.

"""
This module implements generic functions for subscriptions testcase
"""
__version__ = "$Revision: 25037 $"
# $Source$
# $Id: PloneSubscriptionTestCase.py 227919 2010-12-01 11:43:20Z glenfant $
__docformat__ = 'restructuredtext'

# Python imports
import os
import time
import Globals

# Zope imports
from Testing import ZopeTestCase
from AccessControl.SecurityManagement import newSecurityManager
from AccessControl.SecurityManagement import noSecurityManager
from Acquisition import aq_base
#for plone 2.5
import transaction

# CMF imports
from Products.CMFCore.utils import getToolByName

# Plone imports
from Products.PloneTestCase import PloneTestCase

# Products imports
from Products.Archetypes.tests import ArchetypesTestCase
from Products.ATContentTypes.Extensions.Install import install as installATCT
try:
    from Products.ATContentTypes.Extensions.toolbox import isSwitchedToATCT
except:
    pass

class PloneSubscriptionTestCase(PloneTestCase.PloneTestCase):

    # Globals
    portal_name = 'portal'
    portal_owner = 'portal_owner'
    user_name = PloneTestCase.default_user
    user_password = PloneTestCase.default_password

    class Session(dict):
        def set(self, key, value):
            self[key] = value

    def _setup(self):
        PloneTestCase.PloneTestCase._setup(self)
        self.app.REQUEST['SESSION'] = self.Session()

        # Configure tool
        self.stool = getToolByName(self.portal, 'portal_subscription')
        self.mtool = getToolByName(self.portal, 'portal_membership')
        self.ttool = getToolByName(self.portal, 'portal_types')

    def beforeTearDown(self):
        # logout
        noSecurityManager()
    
    def loginAsPortalMember(self):
        '''Use if you need to manipulate site as a member.'''
        self._setupUser()
        self.mtool.createMemberarea(self.user_name)
        member = self.mtool.getMemberById(self.user_name)
        member.setMemberProperties({'fullname': self.user_name.capitalize(), 'email': 'test@example.com',})
        self.login()

    def loginAsPortalOwner(self):
        '''Use if you need to manipulate site as a manager.'''
        uf = self.app.acl_users
        user = uf.getUserById(self.portal_owner).__of__(uf)
        newSecurityManager(None, user)

    def getPermissionsOfRole(self, role):
        perms = self.portal.permissionsOfRole(role)
        return [p['name'] for p in perms if p['selected']]

    def security_context_setup(self):
        "create groups and users"

        self.acl = self.portal.acl_users
        self.acl.userFolderAddGroup('g1', ())
        self.acl.userFolderAddGroup('g2', ())
        self.acl.userFolderAddUser('u1', 'secret', (), (), ('g1', ), )
        self.acl.userFolderAddUser('u2', 'secret', (), (), ('g2', ), )

    def afterSetUp(self):
        self.loginAsPortalOwner()
        #self.security_context_setup()
        self.portal.invokeFactory('Folder', 'test_folder')

        # define quick access variables
        self.sp = self.stool.getProvider()
        self.tp = self.stool.getTemplates()
        self.test_folder = self.portal.test_folder

        self.logout()

def setupPloneSubscription(app, id=ArchetypesTestCase.portal_name, quiet=0):
#     Please import the transaction module, and use transaction.get() instead of
#     get_transaction().  transaction.commit() is a shortcut spelling of
#     transaction.get().commit(), and transaction.abort() of
#     transaction.get().abort().

    transaction.begin()
    _start = time.time()
    portal = app[id]
    
    if not quiet: ZopeTestCase._print('Installing PloneSubscription Site ... ')

    # Login as manager
    user = app.acl_users.getUserById('portal_owner').__of__(app.acl_users)
    newSecurityManager(None, user)
    qi_tool = getToolByName(portal, 'portal_quickinstaller', None)
    
    # Add ATCT
    if hasattr(aq_base(portal), 'switchCMF2ATCT'):
        ZopeTestCase._print('ATCT already installed ... ')
    else:
        qi_tool.installProduct('ATContentTypes')
        get_transaction().commit(1)
    
    if hasattr(aq_base(portal), 'switchCMF2ATCT'):
        if not isSwitchedToATCT(portal):
            # Switch to ATCT
            ZopeTestCase._print('switching to ATCT mode ... ')
            portal.switchCMF2ATCT()
            get_transaction().commit(1)

    # Add PloneSubscription
    qi_tool.installProduct('PloneSubscription')
    get_transaction().commit(1)
    
    # Log out
    noSecurityManager()
    get_transaction().commit()
    if not quiet: ZopeTestCase._print('done (%.3fs)\n' % (time.time()-_start,))

# Install PloneSubscription
ZopeTestCase.installProduct('MimetypesRegistry')
ZopeTestCase.installProduct('PythonScripts')
ZopeTestCase.installProduct('PortalTransforms')
ZopeTestCase.installProduct('Archetypes')
ZopeTestCase.installProduct('ATReferenceBrowserWidget')
ZopeTestCase.installProduct('ATContentTypes')
ZopeTestCase.installProduct('ExtendedPathIndex')
ZopeTestCase.installProduct('DataGridField')
try:
    ZopeTestCase.installProduct('PloneMaintenance')
except:
    pass
ZopeTestCase.installProduct('PloneSubscription')

# Setup Plone site
try:
    PloneTestCase.setupPloneSite(products=[
    'Archetypes',
    'ATReferenceBrowserWidget',
    'DataGridField',
    'PloneMaintenance',
    ])
except:
    PloneTestCase.setupPloneSite(products=[
    'Archetypes',
    'ATReferenceBrowserWidget',
    'DataGridField',
    ])

app = ZopeTestCase.app()
setupPloneSubscription(app)
ZopeTestCase.close(app)
