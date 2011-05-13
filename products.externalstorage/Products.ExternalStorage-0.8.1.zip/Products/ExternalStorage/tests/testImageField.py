#
# ImageField Tests
#

from Testing import ZopeTestCase

import os
from Products.Archetypes.Field import HAS_PIL
from Products.ExternalStorage.tests import ESTestCase


class TestImageField(ESTestCase.ESTestCase):

    # Tests the content type updating of an external article.

    def afterSetUp(self):
        self.img = self._addFileByFileUpload(self.folder, 'image',
                                             ESTestCase.FILENAME_PNG,
                                             'ExternalImage')

    def testPrimaryFieldGetContentType(self):
        self.assertEqual('image/png', self.img.getContentType())

    def testGetContentType(self):
        self.assertEqual('image/png', self.img.getContentType('image'))

    def testImageData(self):
        self.assertEqual(ESTestCase.CONTENT_PNG, self.img.getImage().data)

    def testFileSystemPresence(self):
        instance_path = os.path.join(ESTestCase.BASE_PATH,
                                     ESTestCase.FILENAME_PNG)
        image_path = os.path.join(instance_path, 'image')
        self.assertTrue(os.path.isdir(instance_path))
        self.assertTrue(os.path.isfile(image_path))

    def testFileSystemPresence(self):
        # Only run if PIL is available, then scales are created
        if HAS_PIL:
            instance_path = os.path.join(ESTestCase.BASE_PATH,
                                         ESTestCase.FILENAME_PNG)
            imagescales_path = os.path.join(instance_path, 'image_')
            scales = self.img.getPrimaryField().getAvailableSizes(self.img)
            for scale in scales:
                self.assertTrue(os.path.isfile(imagescales_path + scale))


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestImageField))
    return suite
