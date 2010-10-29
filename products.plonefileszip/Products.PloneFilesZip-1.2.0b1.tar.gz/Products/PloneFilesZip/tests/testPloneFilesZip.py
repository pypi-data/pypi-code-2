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
Retrievers for file like fields
$Id: testPloneFilesZip.py 225402 2010-10-27 16:03:38Z glenfant $
"""

__author__  = 'Gilles Lenfant <gilles.lenfant@ingeniweb.com>'
__docformat__ = 'restructuredtext'

import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from common import *

from Products.PloneFilesZip.registry import GlobalRegistry
from Products.PloneFilesZip.interfaces import IFieldRetriever

tests = []

class TestPloneFilesZip(PloneFilesZipTestCase):
    """Test all"""

    def test_Registry(self):
        """Testing the registry"""

        expected = ['file', 'image']
        expected.sort()
        got = GlobalRegistry.listFieldTypes()
        got.sort()
        self.failUnlessEqual(got, expected,
                             "We got %s when %s was expected" % (str(got), str(expected)))

        for ft in got:
            r = GlobalRegistry.getRetriever(ft)
            self.failUnless(IFieldRetriever.isImplementedByInstancesOf(r),
                            "IFieldRetriever interface was expected")
        return

    def test_ATFileRetriever(self):
        """The ATFile retriever"""

        self.loginAsPortalMember1()
        self.createFullATFile(self.member_folder1)
        atfile = getattr(self.member_folder1, 'FullATFile')
        retrievers = GlobalRegistry.getRetrieversFor(atfile)
        self.failUnlessEqual(len(retrievers), 1,
                             "Should find only 1 retriever for ATFile")

        # Checking the retriever type
        retriever = retrievers[0]
        self.failUnlessEqual(retriever.field_type, 'file',
                             "Should return a FileFieldRetriever")

        # Checking the file name
        filename = retriever.fileName()
        expected = 'sample.doc'
        self.failUnlessEqual(filename, expected,
                             "File name: got '%s' when expecting '%s'" % (filename, expected))

        # Checking the mime type
        mimetype = retriever.mimeType()
        expected = 'application/msword'
        self.failUnlessEqual(mimetype, expected,
                             "MIME type: got '%s' when expecting '%s'" % (mimetype, expected))

        # Checking the retriever
        body = retriever.fileBody()
        file_path = os.path.join(DATA_PATH, 'sample.doc')
        self.failUnlessEqual(body, file(file_path, 'rb').read(),
                             "Wrong AT file data")
        return

    def test_ATImageRetriever(self):
        """The ATImage retriever"""

        self.loginAsPortalMember1()
        self.createFullATImage(self.member_folder1)
        atimage = getattr(self.member_folder1, 'FullATImage')
        retrievers = GlobalRegistry.getRetrieversFor(atimage)
        self.failUnlessEqual(len(retrievers), 1,
                             "Should find only 1 retriever for ATImage")

        # Checking the retriever type
        retriever = retrievers[0]
        self.failUnlessEqual(retriever.field_type, 'image',
                             "Should return a ImageFieldRetriever")

        # Checking the file name
        filename = retriever.fileName()
        expected = 'sample.jpg'
        self.failUnlessEqual(filename, expected,
                             "File name: got '%s' when expecting '%s'" % (filename, expected))

        # Checking the mime type
        mimetype = retriever.mimeType()
        expected = 'image/jpeg'
        self.failUnlessEqual(mimetype, expected,
                             "MIME type: got '%s' when expecting '%s'" % (mimetype, expected))

        # Checking the retriever
        body = retriever.fileBody()
        file_path = os.path.join(DATA_PATH, 'sample.jpg')
        self.failUnlessEqual(body, file(file_path, 'rb').read(),
                             "Wrong AT image data")
        return

    def test_ExFileRetriever(self):
        """The ExFile retriever"""

        self.loginAsPortalMember1()
        self.createFullExFile(self.member_folder1)
        exfile = getattr(self.member_folder1, 'FullExFile')
        retrievers = GlobalRegistry.getRetrieversFor(exfile)
        self.failUnlessEqual(len(retrievers), 1,
                             "Should find only 1 retriever for ExFile")

        # Checking the retriever type
        retriever = retrievers[0]
        self.failUnlessEqual(retriever.field_type, 'file',
                             "Should return a FileFieldRetriever")

        # Checking the file name
        filename = retriever.fileName()
        expected = 'sample.doc'
        self.failUnlessEqual(filename, expected,
                             "File name: got '%s' when expecting '%s'" % (filename, expected))

        # Checking the mime type
        mimetype = retriever.mimeType()
        expected = 'application/msword'
        self.failUnlessEqual(mimetype, expected,
                             "MIME type: got '%s' when expecting '%s'" % (mimetype, expected))

        # Checking the retriever
        body = retriever.fileBody()
        file_path = os.path.join(DATA_PATH, 'sample.doc')
        self.failUnlessEqual(body, file(file_path, 'rb').read(),
                             "Wrong exFile data")
        return

    def test_PotentialZippablePortalTypes(self):
        """Finding AT allowed contents with binary fields"""

        expected = ['PloneExFile', 'File', 'Image', 'News Item']
        expected.sort()
        portal_types = self.portal_fileszip.potentialZippablePortalTypes()
        for portal_type in portal_types:
            self.failUnless(portal_type in expected, "Did not find portal types")
        return

    def test_ZipLinkVisibility(self):
        """Checks if the Download zip action shows"""

        self.loginAsPortalMember1()
        self.createEmptyExFile(self.member_folder1)
        self.failUnless(self.portal_fileszip.showZipAction(self.member_folder1),
                        "Member 1 should have the Zip action")

        f = getattr(self.member_folder1, 'EmptyExFile')
        self.portal_workflow.doActionFor(f, 'hide')
        self.logout()
        self.loginAsPortalMember2()
        self.failIf(self.portal_fileszip.showZipAction(self.member_folder1),
                    "Member 2 should not have the Zip action")
        return



tests.append(TestPloneFilesZip)

if __name__ == '__main__':
    framework()
else:
    # While framework.py provides its own test_suite()
    # method the testrunner utility does not.
    import unittest
    def test_suite():
        suite = unittest.TestSuite()
        for test in tests:
            suite.addTest(unittest.makeSuite(test))
        return suite

