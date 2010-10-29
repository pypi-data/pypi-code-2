# -*- coding: iso-8859-15 -*-
# Copyright (c) 2003-2006 Ingeniweb SAS

# This software is subject to the provisions of the GNU General Public
# License, Version 2.0 (GPL).  A copy of the GPL should accompany this
# distribution.  THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL
# EXPRESS OR IMPLIED WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF TITLE, MERCHANTABILITY,
# AGAINST INFRINGEMENT, AND FITNESS FOR A PARTICULAR PURPOSE

# More details in the ``LICENSE`` file included in this package.

"""
PloneFilesZip tests

$Id: PloneFilesZipTestCase.py 225402 2010-10-27 16:03:38Z glenfant $
"""
__author__ = 'Gilles Lenfant <gilles.lenfant@ingeniweb.com>'
__docformat__ = 'restructuredtext'

# Python imports
import time
import os
import Globals

# Zope imports
from Testing import ZopeTestCase
from AccessControl.SecurityManagement import newSecurityManager
from AccessControl.SecurityManagement import noSecurityManager
from Acquisition import aq_base
from OFS.Image import File, Image

# CMF imports
from Products.CMFCore import CMFCorePermissions
from Products.CMFCore.utils import getToolByName

# Plone imports
from Products.CMFPlone.tests import PloneTestCase

# Products imports
from Products.PloneFilesZip.config import TOOL_ID
try:
    from Products.ATContentTypes.Extensions.toolbox import isSwitchedToATCT
except:
    isSwitchedToATCT = None

portal_name = PloneTestCase.portal_name
portal_owner = PloneTestCase.portal_owner
portal_member1 = 'portal_member1'
portal_member2 = 'portal_member2'

# Path where are stored sample.jpg and sample.doc
DATA_PATH = os.path.join(Globals.INSTANCE_HOME, 'Products', 'PloneFilesZip', 'tests', )

class PloneFilesZipTestCase(PloneTestCase.PloneTestCase):
    """ PloneExFile test case based on a plone site"""

    def afterSetUp(self):
        # Tools shortcuts
        self.portal_catalog = getToolByName(self.portal, 'portal_catalog')
        self.portal_types = getToolByName(self.portal, 'portal_types')
        self.portal_workflow = getToolByName(self.portal, 'portal_workflow')
        self.portal_properties = getToolByName(self.portal, 'portal_properties')
        self.portal_membership = getToolByName(self.portal, 'portal_membership')
        self.portal_fileszip = getToolByName(self.portal, TOOL_ID)
        self.portal_fileszip.zippablePortalTypes = self.portal_fileszip.potentialZippablePortalTypes()
        self.member_folder1 = self.portal_membership.getHomeFolder(portal_member1)
        return

    def createEmptyExFile(self, container, content_id = 'EmptyExFile', **kwargs):
        # return empty file
        container.invokeFactory(type_name='PloneExFile', id=content_id, **kwargs)
        exfile = getattr(container, content_id)
        return exfile

    def createFullExFile(self, container, content_id = 'FullExFile'):
        # create full file
        file_path = os.path.join(DATA_PATH, 'sample.doc')
        upload_file = self.createFileObject('sample.doc', file_path)
        return self.createEmptyExFile(container, content_id, file=upload_file)

    def createEmptyATFile(self, container, content_id = 'EmptyATFile', **kwargs):
        # return empty file
        container.invokeFactory(type_name='File', id=content_id, **kwargs)
        atfile = getattr(container, content_id)
        return atfile

    def createFullATFile(self, container, content_id = 'FullATFile'):
        # create full file
        file_path = os.path.join(DATA_PATH, 'sample.doc')
        upload_file = self.createFileObject('sample.doc', file_path)
        return self.createEmptyATFile(container, content_id, file=upload_file)

    def createEmptyATImage(self, container, content_id = 'EmptyATImage', **kwargs):
        # return empty image
        container.invokeFactory(type_name='Image', id=content_id, **kwargs)
        atimage = getattr(container, content_id)
        return atimage

    def createFullATImage(self, container, content_id = 'FullATImage'):
        # create full image
        file_path = os.path.join(DATA_PATH, 'sample.jpg')
        upload_file = self.createImageObject('sample.jpg', file_path)
        return self.createEmptyATImage(container, content_id, file=upload_file)

    def createFileObject(self, file_id, file_path):
        f = open(file_path, 'rb')
        file_obj = File(file_id, file_id, f)
        setattr(file_obj, 'filename', file_id)
        f.close()
        return file_obj

    def createImageObject(self, file_id, file_path):
        f = open(file_path, 'rb')
        file_obj = Image(file_id, file_id, f)
        setattr(file_obj, 'filename', file_id)
        f.close()
        return file_obj

    def beforeTearDown(self):
        # logout
        noSecurityManager()

    def loginAsPortalMember1(self):
        """Use if you need to manipulate an exfile as member."""
        uf = self.portal.acl_users
        user = uf.getUserById(portal_member1).__of__(uf)
        newSecurityManager(None, user)

    def loginAsPortalMember2(self):
        """Use if you need to manipulate an exfile as member."""
        uf = self.portal.acl_users
        user = uf.getUserById(portal_member2).__of__(uf)
        newSecurityManager(None, user)

    def loginAsPortalOwner(self):
        """Use if you need to manipulate an exfile as member."""
        uf = self.app.acl_users
        user = uf.getUserById(portal_owner).__of__(uf)
        newSecurityManager(None, user)

def setupPloneFilesZip(app, quiet=0):
    get_transaction().begin()
    _start = time.time()
    portal = app.portal

    if not quiet: ZopeTestCase._print('Installing PloneExFile ... ')

    # login as manager
    user = app.acl_users.getUserById(portal_owner).__of__(app.acl_users)
    newSecurityManager(None, user)


    # Install PloneFilesZip in portal
    portal_qi = getToolByName(portal, 'portal_quickinstaller')
    for product_name in ('ATContentTypes', 'AttachmentField', 'PloneExFile', 'PloneFilesZip'):
        if not portal_qi.isProductInstalled(product_name):
            ZopeTestCase._print('Install %s...' % product_name)
            portal_qi.installProduct(product_name)
            get_transaction().commit(1)
        else:
            ZopeTestCase._print('%s already installed...' % product_name)

    # Switch to ATCT
    if isSwitchedToATCT is not None and not isSwitchedToATCT(portal):
        # Switch to ATCT
        ZopeTestCase._print('switching to ATCT mode ... ')
        portal.switchCMF2ATCT()
        get_transaction().commit(1)
    else:
        ZopeTestCase._print('%s already switched...' % product_name)

    # Create 2 portal members with their member area
    members = []
    members.append((portal_member1, ('Member',),))
    members.append((portal_member2, ('Member', 'Owner',),))

    for member_id, member_roles in members:
        portal.portal_registration.addMember(member_id, 'azerty', member_roles)
        member_home = portal.portal_membership.getHomeFolder(member_id)
        if member_home is None:
            portal.portal_membership.createMemberArea(member_id=member_id)

    # Log out
    noSecurityManager()
    get_transaction().commit()
    if not quiet: ZopeTestCase._print('done (%.3fs)\n' % (time.time()-_start,))

app = ZopeTestCase.app()
setupPloneFilesZip(app)
ZopeTestCase.close(app)
