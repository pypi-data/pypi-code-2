## -*- coding: utf-8 -*-
## Copyright (C) 2006-2007 Ingeniweb

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
Base test case
$Id: FSSTestCase.py 115319 2010-04-14 14:48:26Z yboussard $
"""

# Python imports
import os
import Globals

# Zope imports
import transaction
from Testing import ZopeTestCase
from AccessControl.SecurityManagement import newSecurityManager
from zope.component import getUtility

# CMF imports
from Products.CMFCore.utils import getToolByName

# Plone imports
from Products.PloneTestCase import PloneTestCase

# Globals
portal_name = 'portal'
portal_owner = 'portal_owner'
default_user = PloneTestCase.default_user
default_password = PloneTestCase.default_password

STORAGE_PATH = os.path.join(Globals.INSTANCE_HOME, 'var', 'unittests_storage')
BACKUP_PATH = os.path.join(Globals.INSTANCE_HOME, 'var', 'unittests_backup')

DATA_PATH = os.path.join(os.path.dirname(__file__), 'data')
CONTENT_PATH = os.path.join(DATA_PATH, 'word.doc')
IMAGE_PATH = os.path.join(DATA_PATH, 'image.jpg')
BIG_IMAGE_PATH = os.path.join(DATA_PATH, 'bigimage.png')
CONTENT_TXT = """mytestfile"""


from Products.PloneTestCase.layer import onsetup
from Products.Five import fiveconfigure
from Products.Five import zcml
from Testing import ZopeTestCase as ztc

@onsetup
def setup_fss():

    fiveconfigure.debug_mode = True
    import iw.fss
    zcml.load_config('meta.zcml', iw.fss)
    zcml.load_config('configure.zcml', iw.fss)
    fiveconfigure.debug_mode = False
    ztc.installPackage('iw.fss')

setup_fss()

class FSSTestCase(PloneTestCase.PloneTestCase):

    class Session(dict):
        def set(self, key, value):
            self[key] = value

    def _setup(self):
        from iw.fss.customconfig import INSTALL_EXAMPLE_TYPES_ENVIRONMENT_VARIABLE
        from iw.fss.interfaces import IConf
        os.environ[INSTALL_EXAMPLE_TYPES_ENVIRONMENT_VARIABLE] = 'True'

        PloneTestCase.PloneTestCase._setup(self)
        self.app.REQUEST['SESSION'] = self.Session()

        # Create temporary dirs to run test cases
        for base_path in (STORAGE_PATH, BACKUP_PATH):
            if not os.path.exists(base_path):
                os.mkdir(base_path)
        conf= getUtility(IConf, "globalconf")
        self.conf = conf()

        # Patch getStorageStragegy to test all strategies
        strategy_klass = self.strategy_klass
        def getStorageStrategy(self):
            return strategy_klass(STORAGE_PATH, BACKUP_PATH)

        from iw.fss.conffile import ConfFile
        ConfFile.getStorageStrategy = getStorageStrategy

        # Check if fss is switched
        self.use_atct = False
        ttool = getToolByName(self.portal, 'portal_types')
        info = ttool.getTypeInfo('Folder')
        if info.getProperty('meta_type') == 'ATFolder':
            self.use_atct = True

    def beforeTearDown(self):
        """Remove all the stuff again.
        """

        import shutil
        shutil.rmtree(STORAGE_PATH)
        shutil.rmtree(BACKUP_PATH)
        return

    def getDataPath(self):
        """Returns data path used for test cases"""

        return DATA_PATH

    def loginAsPortalOwner(self):
        '''Use if you need to manipulate an article as member.'''
        uf = self.app.acl_users
        user = uf.getUserById(portal_owner).__of__(uf)
        newSecurityManager(None, user)

    def addFileByString(self, folder, content_id):
        """Adds a file by string.
        """
        folder.invokeFactory('FSSItem', id=content_id)
        content = getattr(folder, content_id)
        transaction.savepoint(optimistic=True)
        kw = {'file' : CONTENT_TXT}
        content.edit(**kw)
        return content

    def addFileByFileUpload(self, folder, content_id):
        """Adds a file by file upload.
        """

        folder.invokeFactory('FSSItem', id=content_id)
        content = getattr(folder, content_id)
        transaction.savepoint(optimistic=True)
        self.updateContent(content, 'file', CONTENT_PATH)
        return content

    def addImageByFileUpload(self, folder, content_id):
        """
        Adding image
        """
        folder.invokeFactory('FSSItem', id=content_id)
        content = getattr(folder, content_id)
        transaction.savepoint(optimistic=True)
        self.updateContent(content, 'image', IMAGE_PATH)
        return content

    def addBigImageByFileUpload(self, folder, content_id):
        """
        Adding image
        """
        folder.invokeFactory('FSSItem', id=content_id)
        content = getattr(folder, content_id)
        transaction.savepoint(optimistic=True)
        self.updateContent(content, 'image', BIG_IMAGE_PATH)
        return content



    ## ATContentTypes based testcases

    def addATFileByString(self, folder, content_id):
        """Adds a file by string.
        """

        folder.invokeFactory('ATFSSItem', id=content_id)
        content = getattr(folder, content_id)
        transaction.savepoint(optimistic=True)
        kw = {'file' : CONTENT_TXT}
        content.edit(**kw)
        return content

    def addATFileByFileUpload(self, folder, content_id):
        """Adds a file by file upload.
        """

        folder.invokeFactory('ATFSSItem', id=content_id)
        content = getattr(folder, content_id)
        transaction.savepoint(optimistic=True)
        self.updateContent(content, 'file', CONTENT_PATH)
        return content

    def addATImageByFileUpload(self, folder, content_id):
        """
        Adding image
        """
        folder.invokeFactory('ATFSSItem', id=content_id)
        content = getattr(folder, content_id)
        transaction.savepoint(optimistic=True)
        self.updateContent(content, 'image', IMAGE_PATH)
        return content

    # Update content for any type

    def updateContent(self, content, field, filepath):
        """Updates a field content for a file.
        """

        from dummy import FileUpload
        file = open(filepath, 'rb')
        file.seek(0)
        filename = filepath.split('/')[-1]
        fu = FileUpload(filename=filename, file=file)
        kw = {field: fu}
        content.edit(**kw)

DEFAULT_PRODUCTS = ['kupu', 'iw.fss']

HAS_ATCT = True
ZopeTestCase.installProduct('ATContentTypes')

# Setup Plone site
PloneTestCase.setupPloneSite(products=DEFAULT_PRODUCTS, extension_profiles=['iw.fss:testfixtures'])

