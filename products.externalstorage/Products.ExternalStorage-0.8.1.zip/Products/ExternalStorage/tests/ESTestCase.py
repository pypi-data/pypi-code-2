#
# PloneTestCase
#

# $Id: ESTestCase.py 54417 2007-11-26 01:14:11Z deo $

from Testing import ZopeTestCase

ZopeTestCase.installProduct('PortalTransforms')
ZopeTestCase.installProduct('MimetypesRegistry')
ZopeTestCase.installProduct('Archetypes')
ZopeTestCase.installProduct('ExternalStorage')
ZopeTestCase.installProduct('ExternalExample')

ZopeTestCase.utils.setupCoreSessions()

from Products.PloneTestCase import PloneTestCase

PloneTestCase.setupPloneSite(products=['Archetypes', 'ExternalExample'])

import os
import transaction

from Products.ExternalStorage.config import ENVIRONMENT_VARIABLE

portal_name = 'portal'
portal_owner = 'portal_owner'
default_user = PloneTestCase.default_user
default_password = PloneTestCase.default_password

FILENAME_ZIP = 'sample.zip'
FILENAME_DOC = 'test.doc'
FILENAME_PNG = 'sample.png'
FILENAME_DOC_NEW = 'new.doc'
FILENAME_ZIP_CHARS = 'sample (chars).zip'
FILENAME_DOC_CHARS = 'test (chars).doc'

base = os.path.split(__file__)[0] or os.getcwd()
DATAPATH = os.path.join(base, 'data')
DATAPATH_ZIP = os.path.join(DATAPATH, FILENAME_ZIP)
DATAPATH_DOC = os.path.join(DATAPATH, FILENAME_DOC)
DATAPATH_PNG = os.path.join(DATAPATH, FILENAME_PNG)
DATAPATH_ZIP_CHARS = os.path.join(DATAPATH, FILENAME_ZIP_CHARS)
DATAPATH_DOC_CHARS = os.path.join(DATAPATH, FILENAME_DOC_CHARS)

CONTENT_TXT = """mytestfile"""
CONTENT_ZIP = open(DATAPATH_ZIP, 'r').read()
CONTENT_DOC = open(DATAPATH_DOC, 'r').read()
CONTENT_PNG = open(DATAPATH_PNG, 'rb').read()
CONTENT_ZIP_CHARS = open(DATAPATH_ZIP_CHARS, 'r').read()
CONTENT_DOC_CHARS = open(DATAPATH_DOC_CHARS, 'r').read()

STORAGE_PATH = '/tmp/es_tests'
BASE_PATH = '%s/files/Members/%s/' % (STORAGE_PATH, default_user)
BASE_PATH_MISC = '%s/misc/Members/%s/' % (STORAGE_PATH, default_user)


class ESTestCase(PloneTestCase.PloneTestCase):

    class Session(dict):
        def set(self, key, value):
            self[key] = value

    def _setup(self):
        PloneTestCase.PloneTestCase._setup(self)
        self.app.REQUEST['SESSION'] = self.Session()
        os.environ[ENVIRONMENT_VARIABLE] = STORAGE_PATH

    def beforeTearDown(self):
        """Remove all the stuff again.
        """
        base = os.environ.get(ENVIRONMENT_VARIABLE)
        for root, dirs, files in os.walk(base, topdown=None):
            for name in files:
                os.remove(os.path.join(root, name))
            for name in dirs:
                os.rmdir(os.path.join(root, name))
        if os.path.exists(base):
            os.rmdir(base)

    def _addFileByString(self, place, field, id):
        """Adds a file by string.
        """
        place.invokeFactory('ExternalArticle', id=id)
        obj = getattr(place, id)
        transaction.savepoint(optimistic=True)
        kw = {field: CONTENT_TXT}
        obj.edit(**kw)
        return obj

    def _addFileByFileUpload(self, place, field, id,
                             portal_type='ExternalArticle'):
        """Adds a file by file upload.
        """
        place.invokeFactory(portal_type, id=id)
        obj = getattr(place, id)
        transaction.savepoint(optimistic=True)
        self._updateContent(obj, field, os.path.join(DATAPATH, id))
        return obj

    def _updateContent(self, obj, field, filepath):
        """Updates a field content for a file.
        """
        from dummy import FileUpload
        file = open(filepath, 'r')
        file.seek(0)
        filename = filepath.split('/')[-1]
        fu = FileUpload(filename=filename, file=file)
        kw = {field: fu}
        obj.edit(**kw)

class FunctionalTestCase(ZopeTestCase.Functional, ESTestCase):
    pass
