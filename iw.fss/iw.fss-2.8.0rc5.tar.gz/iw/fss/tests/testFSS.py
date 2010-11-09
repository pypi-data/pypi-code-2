## -*- coding: utf-8 -*-
## Copyright (C) 2006 Ingeniweb

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
Testing FSS features
$Id: testFSS.py 118954 2010-06-10 07:41:53Z glenfant $
"""

import transaction
import Products
from StringIO import StringIO
from zope.component import getUtility
from Products.Five import zcml
from ZPublisher.HTTPRequest import HTTPRequest
from ZPublisher.HTTPResponse import HTTPResponse
from ZPublisher.Iterators import IStreamIterator
import iw.fss
from iw.fss.interfaces import IConf
from iw.fss.migration import Migrator
from iw.fss.utils import objectImplements

from common import *

class TestFSS(FSSTestCase.FSSTestCase):

    def afterSetUp(self):
        self.loginAsPortalOwner()
        content_id = 'test_folder'
        self.portal.invokeFactory(FOLDER_TYPE, id=content_id)
        self.test_folder = getattr(self.portal, content_id)
        self.logout()
        self.portal_repository = self.portal.portal_repository
        conf_class = getUtility(IConf, "globalconf")
        self.conf = conf_class()


# #############################################################################
# ADD
# #############################################################################

    def testAddFileFromString(self):
        self.loginAsPortalOwner()
        content_id = 'test_file'
        self.file_content = self.addFileByString(self.test_folder, content_id)

        # Get file field
        file_field = self.file_content.getField('file')

        # Get file value
        file_value = file_field.get(self.file_content)

        # Test value
        self.assertEquals(str(file_value.data), 'mytestfile')

        # Test filename
        self.assertEquals(file_value.filename, '')

        # Test size
        self.assertEquals(file_value.get_size(), 10)

        # Test content type
        self.assertEquals(file_field.getContentType(self.file_content), 'text/plain')

        # Test using BaseUnit
        bu = file_field.getBaseUnit(self.file_content)
        bu_value = bu.getRaw()
        self.assertEquals(len(bu_value), 10)
        self.assertEquals(bu_value, """mytestfile""")

        # Test using manage_FTPget
        ftp_value = self.file_content.manage_FTPget()
        self.failIf(ftp_value is None)
        self.assertEquals(len(ftp_value), 10)
        # ftp_value is an PdataStreamIterator
        self.failUnless(isinstance(ftp_value,
                  Products.Archetypes.WebDAVSupport.PdataStreamIterator))

        self.assertEquals(ftp_value.next(), """mytestfile""")
        self.logout()


    def testSetByInvokeFactory(self):
        self.loginAsPortalOwner()
        self.portal.invokeFactory(type_name='FSSItem', id="dummy",
                                  title="Foo title", text="Foo text")
        self.assertEquals(self.portal['dummy'].getText(), 'Foo text')

    def testAddAnBigImage(self):
        self.loginAsPortalOwner()
        content_id = 'testbigimage'

        self.file_content = self.addBigImageByFileUpload(self.test_folder,
                                                         content_id)
        # Get file field
        file_field = self.file_content.getField('image')

        # Get file value
        file_value = file_field.get(self.file_content)

        # Test value
        self.assertEquals(len(file_value.data), 247207)

        # Test using BaseUnit
        bu = file_field.getBaseUnit(self.file_content)
        bu_value = bu.getRaw()
        self.assertEquals(len(bu_value), 1 << 16)
        self.logout()


    def _testDefaultContentFromUploadedFile(self):
        # Get file field
        file_field = self.file_content.getField('file')

        # Get file value
        file_value = file_field.get(self.file_content)

        # Test filename
        self.assertEquals(file_value.filename, 'word.doc')

        # Test size
        self.assertEquals(file_value.get_size(), 10240)

        # Test content type
        self.assertEquals(file_field.getContentType(self.file_content), 'application/msword')

        # Test using BaseUnit
        bu = file_field.getBaseUnit(self.file_content)
        bu_value = bu.getRaw()
        self.assertEquals(len(bu_value), 10240)

        # Test using manage_FTPget
        ftp_value = self.file_content.manage_FTPget()
        self.failIf(ftp_value is None)
        self.assertEquals(len(ftp_value), 10240)

    def testAddFileFromUploadedFile(self):
        self.loginAsPortalOwner()

        # Create file
        content_id = 'test_file'
        self.file_content = self.addFileByFileUpload(self.test_folder, content_id)

        self._testDefaultContentFromUploadedFile()

        self.logout()

# #############################################################################
# EDIT
# #############################################################################
    def testEditFile(self):
        self.loginAsPortalOwner()

        # Create file
        content_id = 'test_file'
        self.file_content = self.addFileByFileUpload(self.test_folder, content_id)

        self._testDefaultContentFromUploadedFile()

        # Update content
        data_path = self.getDataPath()
        self.updateContent(self.file_content, 'file', os.path.join(data_path, 'excel.xls'))

        # Get file field
        file_field = self.file_content.getField('file')

        # Get file value
        file_value = file_field.get(self.file_content)

        # Test filename
        self.assertEquals(file_value.filename, 'excel.xls')

        # Test size
        self.assertEquals(file_value.get_size(), 13824)

        # Test content type
        self.assertEquals(file_field.getContentType(self.file_content), 'application/vnd.ms-excel')

        self.logout()

# #############################################################################
# RENAME
# #############################################################################
    def testRenameContent(self):
        self.loginAsPortalOwner()

        # Create file
        content_id = 'test_file'
        self.file_content = self.addFileByFileUpload(self.test_folder, content_id)
        old_uid = self.file_content.UID()

        # Rename file
        new_content_id = 'new_test_file'
        self.test_folder.manage_renameObjects((content_id,), (new_content_id,))

        # Test file
        self.assertEquals(self.file_content.getId(), new_content_id)
        self.assertEquals(self.file_content.UID(), old_uid)
        self._testDefaultContentFromUploadedFile()
        self.logout()

# #############################################################################
# COPY
# #############################################################################
    def testCopyContent(self):
        self.loginAsPortalOwner()

        # Create file
        content_id = 'test_file'
        self.file_content = self.addFileByFileUpload(self.test_folder, content_id)

        # Copy file in another folder
        cb = self.test_folder.manage_copyObjects(ids=(content_id,))

        new_folder_id = 'new_test_folder'
        self.portal.invokeFactory(FOLDER_TYPE, id=new_folder_id)
        new_folder = getattr(self.portal, new_folder_id)

        # Paste
        new_folder.manage_pasteObjects(cb_copy_data=cb)

        # Test source file
        self._testDefaultContentFromUploadedFile()

        # Test destination file
        new_file_content = getattr(new_folder, content_id)

        # Get file field
        file_field = new_file_content.getField('file')

        # Get file value
        file_value = file_field.get(new_file_content)

        # Test filename
        self.assertEquals(file_value.filename, 'word.doc')

        # Test size
        self.assertEquals(file_value.get_size(), 10240)

        # Test content type
        self.assertEquals(file_field.getContentType(new_file_content), 'application/msword')

        # more tests here to test that the external content
        # is also copied
        old_storage = getattr(self.test_folder, content_id).getField('file').getStorage()
        new_storage = file_field.getStorage()
        old_instance = getattr(self.test_folder, content_id)

        old_fss = old_storage.getFSSInfo('file', old_instance)
        new_fss = new_storage.getFSSInfo('file', new_file_content)

        old_brains = self.conf.getStorageBrainsByUID(old_fss.getUID())
        new_brains = self.conf.getStorageBrainsByUID(new_fss.getUID())

        st_old = [x for x in old_brains if x['name'] == 'file'][0]
        st_new = [x for x in new_brains if x['name'] == 'file'][0]

        self.assertNotEqual(old_fss.getUID(), new_fss.getUID())
        self.assertNotEqual(len(st_old.keys()), 0, str(st_old))
        self.assertNotEqual(len(st_new.keys()), 0, str(st_new))
        self.assertNotEqual(st_old['fs_path'], st_new['fs_path'])
        self.assertEqual(st_old['size'], st_new['size'])
        self.assertNotEqual(st_old['path'], st_new['path'])

        self.logout()

    def testCopyFolderWithImages(self):
        if not self.use_atct:
            # Only ATFolder implements correctly copy/paste for sub objects
            return

        self.loginAsPortalOwner()

        # Create new folder and fill it with some content
        self.portal.invokeFactory(id='test_source_folder', type_name=FOLDER_TYPE)
        self.sf = getattr(self.portal, 'test_source_folder')

        # adding some images
        self.addImageByFileUpload(self.sf, 's1')
        self.addImageByFileUpload(self.sf, 's2')
        self.addImageByFileUpload(self.sf, 's3')
        self.addImageByFileUpload(self.sf, 's4')
        self.addImageByFileUpload(self.sf, 's5')
        self.addImageByFileUpload(self.sf, 's6')

        self.assertEqual(len(self.sf.objectValues()), 6)

        # creating new subfolder
        self.portal.invokeFactory(id='test_target_folder', type_name=FOLDER_TYPE)

        # make sure objects got copied
        obnum = random.choice([1,2,3,4,5,6])

        o_cobject = getattr(self.sf, 's%s' % obnum)
        o_storage = o_cobject.getField('image').getStorage()
        o_fssinfo = o_storage.getFSSInfo('image', o_cobject)
        o_brains = self.conf.getStorageBrainsByUID(o_fssinfo.getUID())

        # copying complete sf folder to test_target_folder
        cb = self.portal.manage_copyObjects(ids=(self.sf.getId(), ))

        # paste into new folder
        self.tf = getattr(self.portal, 'test_target_folder')
        self.assertEqual(len(self.tf.objectValues()), 0)
        self.tf.manage_pasteObjects(cb_copy_data=cb)
        self.assertEqual(len(self.tf.objectValues()), 1)

        # copied folder should contain six items
        self.cf = getattr(self.tf, 'test_source_folder')
        self.assertEqual(len(self.cf.objectValues()), 6)

        # make sure copied folder got new UID
        self.assertNotEqual(self.cf.getPhysicalPath(), self.sf.getPhysicalPath())
        self.assertEqual(self.cf.getId(), self.sf.getId())

        n_cobject = getattr(self.cf, 's%s' % obnum)
        n_storage = n_cobject.getField('image').getStorage()
        n_fssinfo = n_storage.getFSSInfo('image', n_cobject)
        n_brains = self.conf.getStorageBrainsByUID(n_fssinfo.getUID())

        self.assertNotEqual(o_fssinfo.getUID(), n_fssinfo.getUID())
        self.assertNotEqual(len(o_brains), 0, str(o_brains))
        self.assertNotEqual(len(n_brains), 0, str(n_brains))

        # test if scales were copied
        for name in ('image_mini', 'image_thumb'):
            fs_path = [x['fs_path'] for x in o_brains if x['name'] == name][0]
            assert os.path.exists(fs_path)

        for name in ('image_mini', 'image_thumb'):
            fs_path = [x['fs_path'] for x in n_brains if x['name'] == name][0]
            assert os.path.exists(fs_path)

        # FSS must have created new files on filesystem
        for name in ('image', 'image_mini', 'image_thumb'):
            o_brain = [x for x in o_brains if x['name'] == name][0]
            n_brain = [x for x in n_brains if x['name'] == name][0]
            self.assertNotEqual(o_brain['fs_path'], n_brain['fs_path'])
            self.assertEqual(o_brain['size'], n_brain['size'])
            self.assertNotEqual(o_brain['path'], n_brain['path'])

        # testing deletion
        old_s1_uid = self.sf.s1.UID()
        s1_brains = self.conf.getStorageBrainsByUID(old_s1_uid)
        assert len(s1_brains)>0

        self.sf.manage_delObjects(['s1', ])
        assert 's1' not in self.sf.objectIds()
        s1_brains = self.conf.getStorageBrainsByUID(old_s1_uid)
        assert len(s1_brains)==0


        self.logout()

# #############################################################################
# CUT
# #############################################################################
    def testCutContent(self):
        self.loginAsPortalOwner()

        # Create file
        content_id = 'test_file'
        self.file_content = self.addFileByFileUpload(self.test_folder, content_id)
        old_uid = self.file_content.UID()
        old_storage = getattr(self.test_folder, content_id).getField('file').getStorage()
        old_instance = getattr(self.test_folder, content_id)
        old_fss = old_storage.getFSSInfo('file', old_instance)

        # Copy file in another folder
        cb = self.test_folder.manage_cutObjects(ids=(content_id,))

        new_folder_id = 'new_test_folder'
        self.portal.invokeFactory(FOLDER_TYPE, id=new_folder_id)
        new_folder = getattr(self.portal, new_folder_id)

        # Paste
        new_folder.manage_pasteObjects(cb_copy_data=cb)

        # Test source file
        self.failIf(hasattr(self.test_folder, content_id))

        # Test destination file
        new_file_content = getattr(new_folder, content_id)

        # Get file field
        file_field = new_file_content.getField('file')

        # Get file value
        file_value = file_field.get(new_file_content)

        # Test filename
        self.assertEquals(file_value.filename, 'word.doc')

        # Test size
        self.assertEquals(file_value.get_size(), 10240)

        # Test content type
        self.assertEquals(file_field.getContentType(new_file_content), 'application/msword')

        self.assertEquals(new_file_content.UID(), old_uid)

        # more tests here to test that the external content
        # is also copied
        new_storage = file_field.getStorage()
        new_fss = new_storage.getFSSInfo('file', new_file_content)

        st_old = self.conf.getStorageBrainsByUID(old_fss.getUID())[0]
        st_new = self.conf.getStorageBrainsByUID(new_fss.getUID())[0]

        self.assertEqual(old_fss.getUID(), new_fss.getUID())
        self.assertNotEqual(len(st_old.keys()), 0, str(st_old))
        self.assertNotEqual(len(st_new.keys()), 0, str(st_new))
        self.assertEqual(st_old['fs_path'], st_new['fs_path'])
        self.assertEqual(st_old['size'], st_new['size'])

        self.logout()

    def testCutFolderWithFSSContent(self):
        self.loginAsPortalOwner()

        # Create source folder
        src_folder_id = 'src_folder'
        self.portal.invokeFactory(FOLDER_TYPE, id=src_folder_id)
        src_folder = getattr(self.portal, src_folder_id)

        # Create a file in source folder
        src_content_id = 'src_file'
        src_content = self.addFileByFileUpload(src_folder, src_content_id)

        # Keep a reference to this source content
        old_instance = src_content
        old_uid = old_instance.UID()
        old_storage = old_instance.getField('file').getStorage()
        old_fss = old_storage.getFSSInfo('file', old_instance)

        # Copy source folder to another folder
        cb = self.portal.manage_cutObjects(ids=(src_folder_id,))

        dst_folder_id = 'dst_folder'
        self.portal.invokeFactory(FOLDER_TYPE, id=dst_folder_id)
        dst_folder = getattr(self.portal, dst_folder_id)

        # Paste
        dst_folder.manage_pasteObjects(cb_copy_data=cb)

        # Test that source folder has moved
        self.failIf(hasattr(self.portal, src_folder_id))

        # Get new source folder
        new_folder = getattr(dst_folder, src_folder_id)

        # Get new source content
        new_content = getattr(new_folder, src_content_id)

        # Get file field
        file_field = new_content.getField('file')

        # Get file value and test it
        file_value = file_field.get(new_content)
        self.failUnless(isinstance(file_value, VirtualBinary), file_value.__class__)

        # Test filename
        self.assertEquals(file_value.filename, 'word.doc')

        # Test size
        self.assertEquals(file_value.get_size(), 10240)

        # Test content type
        self.assertEquals(file_field.getContentType(new_content), 'application/msword')

        self.assertEquals(new_content.UID(), old_uid)

        # more tests here to test that the external content
        # is also copied
        new_storage = file_field.getStorage()
        new_fss = new_storage.getFSSInfo('file', new_content)

        st_old = self.conf.getStorageBrainsByUID(old_fss.getUID())[0]
        st_new = self.conf.getStorageBrainsByUID(new_fss.getUID())[0]

        self.assertEqual(old_fss.getUID(), new_fss.getUID())
        self.assertNotEqual(len(st_old.keys()), 0, str(st_old))
        self.assertNotEqual(len(st_new.keys()), 0, str(st_new))
        self.assertEqual(st_old['fs_path'], st_new['fs_path'])
        self.assertEqual(st_old['size'], st_new['size'])

        self.logout()

# #############################################################################
# DELETE
# #############################################################################
    def testDeleteContent(self):
        self.loginAsPortalOwner()

        # Create file
        content_id = 'test_file'
        self.file_content = self.addFileByFileUpload(self.test_folder, content_id)

        # Delete file
        self.test_folder.manage_delObjects(ids=[content_id])

        # Test file
        self.failIf(hasattr(self.test_folder, content_id))
        self.logout()

    def testStorageWhenDeleteContent(self):
        from FSSTestCase import STORAGE_PATH

        self.loginAsPortalOwner()

        # Create file
        content_id = 'test_file'
        self.file_content = self.addFileByFileUpload(self.test_folder, content_id)

        # One item in storage path
        self.failUnlessEqual(len(os.listdir(STORAGE_PATH)), 1)

        # Delete file
        self.test_folder.manage_delObjects(ids=[content_id])

        # Zero items in storage path
        self.failUnlessEqual(len(os.listdir(STORAGE_PATH)), 0)

        self.logout()

# #############################################################################
# FIELD OPERATIONS
# #############################################################################
    def testDeleteField(self):
        self.loginAsPortalOwner()

        # Create content
        content_id = 'test_file'
        file_content = self.addFileByFileUpload(self.test_folder, content_id)

        # Get file field
        file_field = file_content.getField('file')

        # Get file value
        file_value = file_field.get(file_content)

        # Test filename
        self.assertEquals(file_value.filename, 'word.doc')

        # Test size
        self.assertEquals(file_value.get_size(), 10240)

        # Test content type
        self.assertEquals(file_field.getContentType(file_content), 'application/msword')

        # Delete file field value
        file_field.set(file_content, 'DELETE_FILE')

        # Get file value
        file_value = file_field.get(file_content)

        self.assertEquals(file_value, '')

    def testModifyField(self):
        self.loginAsPortalOwner()

        # Create content
        content_id = 'test_file'
        file_content = self.addFileByFileUpload(self.test_folder, content_id)

        # Get file field
        file_field = file_content.getField('file')

        # Get file value
        file_value = file_field.get(file_content)

        # Test filename
        self.assertEquals(file_value.filename, 'word.doc')

        # Test size
        self.assertEquals(file_value.get_size(), 10240)

        # Test content type
        self.assertEquals(file_field.getContentType(file_content), 'application/msword')

        # Delete file field value
        new_value = 'example of content'
        file_field.set(file_content, new_value)

        # Get file value
        file_value = file_field.get(file_content)

        # Test value
        self.assertEquals(str(file_value), new_value)

        # Test content type
        self.assertEquals(file_field.getContentType(file_content), 'text/plain')

# #############################################################################
# UID OPERATIONS
# #############################################################################
    def test_setUID(self):
        self.loginAsPortalOwner()

        # Create content
        content_id = 'test_file'
        file_content = self.addFileByFileUpload(self.test_folder, content_id)

        # Get file field
        file_field = file_content.getField('file')

        # Get file value
        file_value = file_field.get(file_content)

        # Test filename
        self.assertEquals(file_value.filename, 'word.doc')

        # Test size
        self.assertEquals(file_value.get_size(), 10240)

        # Test content type
        self.assertEquals(file_field.getContentType(file_content), 'application/msword')

        # Modify UID
        file_content._setUID('dummyUID')
        self.assertEquals(file_content.UID(), "dummyUID")

        # Get file field
        file_field = file_content.getField('file')

        # Get file value
        file_value = file_field.get(file_content)

        # Test filename
        self.assertEquals(file_value.filename, 'word.doc')

        # Test size
        self.assertEquals(file_value.get_size(), 10240)

        # Test content type
        self.assertEquals(file_field.getContentType(file_content), 'application/msword')



# #############################################################################
# VIRTUAL BINARY OPERATIONS
# #############################################################################
    def testVirtualBinaryAbsoluteUrl(self):

        self.loginAsPortalOwner()

        # Create content
        content_id = 'test_file'
        file_content = self.addFileByFileUpload(self.test_folder, content_id)

        # Get file field
        file_field = file_content.getField('file')

        # Get file value
        file_value = file_field.get(file_content)

        # Test absolute_url
        url = '%(instance_url)s/%(name)s' % {
            'instance_url': file_content.absolute_url(),
            'name': 'file',
            }
        self.assertEquals(file_value.absolute_url(), url)


# #############################################################################
# Test File Stream Operator
# #############################################################################

    def _testFileStreamIterator(self,start,end):
        """
        unit test about range_filestream_iterator
        """
        # Create content
        from FSSTestCase import CONTENT_PATH

        # Create range file stream iterator
        from iw.fss.FileSystemStorage import \
            range_filestream_iterator

        iterator = range_filestream_iterator(CONTENT_PATH,start,end,mode='rb')
        data=''
        for i in iterator:
            data +=i
        self.assertEqual(len(data) , end - start  ,
                         '%i != %i len is not correct' % \
                                 (len(data),  end  - start))



    def testRangeFileStreamIterator(self):
        """ test range operation of file stream operator """
        #begin of the file
        self._testFileStreamIterator(0,10)
        #middle
        self._testFileStreamIterator(30,1000)
        #end

        self._testFileStreamIterator(500,1023)
        #

    def testRangeSupport(self):
        """
        functionnal test of range support
        """

        self.loginAsPortalOwner()

        # Create content
        content_id = 'test_file'
        file_content = self.addFileByFileUpload(self.test_folder, content_id)
        # Get file field
        file_field = file_content.getField('file')
        file_content = file_field.get(file_content)
        # do an simple request
        e = {'SERVER_NAME':'foo', 'SERVER_PORT':'80', 'REQUEST_METHOD':'GET'}
        out = StringIO()
        resp = HTTPResponse(stdout=out)
        req = HTTPRequest(sys.stdin, e, resp)
        req.RESPONSE = resp
        data = file_content.index_html(req, resp)
        self.failUnless(len(data) == len(file_content) ,
                        'not good lenght data ')

        # now do an range request with one range
        e =  {'SERVER_NAME':'foo',
              'SERVER_PORT':'80',
              'REQUEST_METHOD':'GET',
              'HTTP_RANGE' : 'bytes=0-10' }
        resp = HTTPResponse(stdout=out)
        req = HTTPRequest(sys.stdin, e, resp)
        req.RESPONSE = resp
        data = file_content.index_html(req, resp)
        read_data = ''
        for d in data:
            read_data +=d

        self.failUnless(len(read_data) == 11 ,
                        'not good lenght data <%s>' % len(read_data))

        # now mulitple range
        e =  {'SERVER_NAME':'foo',
              'SERVER_PORT':'80',
              'REQUEST_METHOD':'GET',
              'HTTP_RANGE' : 'bytes=0-10, 50-80' }
        resp = HTTPResponse(stdout=out)
        req = HTTPRequest(sys.stdin, e, resp)
        req.RESPONSE = resp
        data = file_content.index_html(req, resp)

# #############################################################################
# Test donwload patches
# #############################################################################

    def testPatched(self):
        self.loginAsPortalOwner()

        # Create content
        content_id = 'test_file'
        file_content = self.addFileByFileUpload(self.test_folder, content_id)
        # Get file field
        file_field = file_content.getField('file')
        response = file_field.download(file_content, no_output = True)
        self.assertEqual(bool(objectImplements(IStreamIterator, response)), True)
        HTTP_RESPONSE = file_content.REQUEST.RESPONSE
        self.failUnless(HTTP_RESPONSE.headers.has_key('content-length'))
        ## reinit response headers
        file_content.REQUEST.RESPONSE.headers = {}
        response = file_field.download(file_content)
        self.assertEqual(bool(objectImplements(IStreamIterator, response)), True)
        self.failUnless(HTTP_RESPONSE.headers.has_key('content-length'))



# #############################################################################
# Test CMFEditions compliance
# #############################################################################

    def testCMFEditions(self):
        self.loginAsPortalOwner()
        portal_repository = self.portal_repository
        data_path = self.getDataPath()
        file1_path = os.path.join(data_path, 'word.doc')
        file1 = open(file1_path, 'rb').read()
        file2_path = os.path.join(data_path, 'excel.xls')
        file2 = open(file2_path, 'rb').read()
        image1_path = os.path.join(data_path, 'image.jpg')
        image1 = open(image1_path, 'rb').read()

        content = self.addATFileByFileUpload(self.folder, 'test_file_and_image')
        portal_repository.applyVersionControl(content, comment='save no 1')

        self.updateContent(content, 'file', file2_path)
        self.updateContent(content, 'image', image1_path)
        portal_repository.save(content, comment='save no 2')

        vdata = portal_repository.retrieve(content, 0)
        obj = vdata.object
        # Verify
        file_field = obj.getField('file')
        file_value = file_field.get(obj)
        self.assertEquals(file_value.filename, 'word.doc')
        self.assertEquals(file_value.get_size(), 10240)
        self.assertEquals(file_field.getContentType(obj), 'application/msword')

        vdata = portal_repository.retrieve(content, 1)
        obj = vdata.object
        # Verify
        file_field = obj.getField('file')
        file_value = file_field.get(obj)
        self.assertEquals(file_value.filename, 'excel.xls')
        self.assertEquals(file_value.get_size(), 13824)
        self.assertEquals(file_field.getContentType(obj), 'application/vnd.ms-excel')

        portal_repository.revert(content, 0)
        # Verify
        file_field = content.getField('file')
        file_value = file_field.get(content)
        self.assertEquals(file_value.filename, 'word.doc')
        self.assertEquals(file_value.get_size(), 10240)
        self.assertEquals(file_field.getContentType(content), 'application/msword')

        self.logout()
        return

    def test_migrations(self):
        """Testing migrations from natural ATCT storage (Annotation ?)
        """

        from iw.fss.zcml import patchedTypesRegistry

        self.loginAsPortalOwner()

        # Install content from zexp
        zexp_path = os.path.join(self.getDataPath(), 'migration-in.zexp')
        self.portal._importObjectFromFile(zexp_path)
        self._checkImportedContent()

        # We apply FSS settings to ATCT
        zcml.load_config('atct.zcml', iw.fss)

        # We process the migration
        migrator = Migrator(self.portal)
        migrator.migrateToFSS()

        # We check we have the same content (AT API pov)
        self._checkImportedContent(1)

        # Deleting imported stuff
        self.portal._delObject('migration-in')
        patchedTypesRegistry = {}
        return


    def _checkImportedContent(self, step=0):
        """Some checks on imported context before and after migration
        """
        folder = self.portal['migration-in']
        self.failUnlessEqual(folder.portal_type, 'Folder')

        expecting = [
            # item id, field name, size, mime type
            ('Lorem ipsum.pdf', 'file', 0, 'application/octet-stream'),
            ('einsteinphoto.jpg', 'image', 17794, 'image/jpeg'),
            ('news-with-image', 'image', 17794, 'image/jpeg'),
            ('news-without-image', 'image', 0, 'image/png')
            ]

        # We have all expected items
        expected_ids = [x[0] for x in expecting]
        self.failUnlessEqual(set(folder.objectIds()), set(expected_ids))

        # Inspecting each item
        for item_id, fieldname, size, mimetype in expecting:
            item = folder[item_id]
            field = item.Schema()[fieldname]

            # Checking size
            #
            self.failUnlessEqual(field.getBaseUnit(item).size, size)

            # Checking mime type
            # if item_id != 'news-without-image':
            self.failUnlessEqual(field.getBaseUnit(item).mimetype, mimetype,
                                 "Got mime type %s when expected %s for %s"
                                 % (field.getBaseUnit(item).mimetype, mimetype, item_id))
        return

###
## Real test classes
###

from iw.fss.strategy import (
    DirectoryStorageStrategy, FlatStorageStrategy,
    SiteStorageStrategy, SiteStorageStrategy2)

class TestDirectoryStorageStrategy(TestFSS):

    strategy_klass = DirectoryStorageStrategy

class TestFlatStorageStrategy(TestFSS):

    strategy_klass = FlatStorageStrategy

class TestSiteStorageStrategy(TestFSS):

    strategy_klass = SiteStorageStrategy

class TestSiteStorageStrategy2(TestFSS):

    strategy_klass = SiteStorageStrategy2

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestDirectoryStorageStrategy))
#    suite.addTest(makeSuite(TestFlatStorageStrategy))
#    suite.addTest(makeSuite(TestSiteStorageStrategy))
#    suite.addTest(makeSuite(TestSiteStorageStrategy2))
    return suite

if __name__ == '__main__':
    framework()
