import unittest
from zope.component import getUtility
from Products.CMFCore.interfaces import IPropertiesTool
from Products.RichImage.tests.base import RichImageTestCase
from Products.RichImage.content.richimage import RichImageSchema
try:
    from Products.CacheSetup.interfaces import IPurgeUrls
    from Products.RichImage.cache import RichImagePurge
    HAVE_CACHESETUP=True
except ImportError:
    HAVE_CACHESETUP=False

test_sizes = {'size1': (100, 200),
              'size2': (200, 300),
             }
test_crops = {'crop1': (0, 0, 50, 100),
              'crop2': (0, 0, 100,  50),
              'crop3': (20, 10, 100,  50),
             }

class TestContent(RichImageTestCase):

    def afterSetUp(self):
        self.loginAsPortalOwner()
        self.folder.invokeFactory('RichImage', 'rich-image')
        self.ri = getattr(self.folder, 'rich-image')

        # Store default schema settings
        self.default_sizes = RichImageSchema['image'].sizes
        self.default_crops = RichImageSchema['image'].crops
        self.default_create = RichImageSchema['image'].createCropsOnSet
        self.default_ui_crop_scale = RichImageSchema['image'].ui_crop_scale

        # custom schema setup
        RichImageSchema['image'].sizes = test_sizes
        RichImageSchema['image'].crops = test_crops
        RichImageSchema['image'].createCropsOnSet = True
        RichImageSchema['image'].ui_crop_scale = 'size1'

        # also set up scale sizes for `plone.app.imaging`
        sizes = test_sizes.items()
        sizes = [ '%s %d:%d' % ((key,) + value) for key, value in sizes ]
        iprops = getUtility(IPropertiesTool).imaging_properties
        iprops.manage_changeProperties(allowed_sizes=sizes)

    def beforeTearDown(self):
        # Restore default schema settings
        RichImageSchema['image'].sizes = self.default_sizes
        RichImageSchema['image'].crops = self.default_crops
        RichImageSchema['image'].createCropsOnSet = self.default_create
        RichImageSchema['image'].ui_crop_scale = self.default_ui_crop_scale

    def testTraversing(self):
        self.ri.setImage(self.test_image)
        traverse = self.portal.REQUEST.traverseName

        for size_id in test_sizes.keys():
            obj = traverse(self.ri, 'image_%s' %size_id)
            self.failUnless(obj != None)

        for crop_id in test_crops.keys():
            obj = traverse(self.ri, 'image_%s' %crop_id)
            self.failUnless(obj != None)

    def testCropsOnSet(self):
        self.ri.schema['image'].createCropsOnSet = False
        self.ri.setImage(self.test_image)

        for crop_id in test_crops.keys():
            crop = self.ri.schema['image'].getCrop(self.ri, crop=crop_id)
            self.failIf(crop)

    def testCropsOnTraverse(self):
        self.ri.schema['image'].createCropsOnSet = False
        self.ri.setImage(self.test_image)

        for crop_id in test_crops.keys():
            crop = self.ri.restrictedTraverse('image_%s' % crop_id)
            self.failUnless(crop)

    def testCropsCreation(self):
        self.ri.schema['image'].createCropsOnSet = False
        self.ri.setImage(self.test_image)
        ri_field = self.ri.getField('image')

        for crop_id in test_crops.keys():
            # automatic crop creation on tag method call
            ri_field.tag(self.ri, scale = crop_id)
            obj = self.ri.restrictedTraverse('image_%s' %crop_id)
            self.failUnless(obj != None)

    def testSelectedCropsSizes(self):
        self.ri.schema['image'].createCropsOnSet = ('crop2',)
        self.ri.setImage(self.test_image)

        missing_crops = ('crop1', 'crop3')
        for crop_id in missing_crops:
            crop = self.ri.schema['image'].getCrop(self.ri, crop=crop_id)
            self.failIf(crop)

        existing_crops = ('crop2',)
        for crop_id in existing_crops:
            crop = self.ri.schema['image'].getCrop(self.ri, crop=crop_id)
            self.failUnless(crop)


    def testCropsSizes(self):
        self.ri.schema['image'].createCropsOnSet = True
        self.ri.setImage(self.test_image)

        for crop_id, crop_values in test_crops.items():
            obj = self.ri.restrictedTraverse('image_%s' %crop_id)
            x1, y1, x2, y2 = crop_values
            width = x2 - x1
            height = y2 - y1
            self.failUnless(obj.width == width)
            self.failUnless(obj.height == height)

    def testCropsSizesWithResize(self):
        self.ri.schema['image'].createCropsOnSet = True
        # using a very small image
        self.ri.setImage(self.test_image_small)

        for crop_id, crop_values in test_crops.items():
            obj = self.ri.restrictedTraverse('image_%s' %crop_id)
            x1, y1, x2, y2 = crop_values
            width = x2 - x1
            height = y2 - y1
            self.failUnless(obj.width == width)
            self.failUnless(obj.height == height)

    def testCropEdit(self):
        self.ri.schema['image'].createCropsOnSet = True
        self.ri.setImage(self.test_image)

        ri_field = self.ri.getField('image')
        ri_field.editCrop(self.ri, 'crop1', 0, 0, 10, 20)
        obj = self.ri.restrictedTraverse('image_crop1')
        self.failUnless(obj.width == 10)
        self.failUnless(obj.height == 20)

        # with resize
        ri_field = self.ri.getField('image')
        ri_field.editCrop(self.ri, 'crop1', 0, 0, 10, 20, scale = 5)
        obj = self.ri.restrictedTraverse('image_crop1')
        self.failUnless(obj.width == 50)
        self.failUnless(obj.height == 100)


    def testFullSizeImage(self):
        self.ri.setImage(self.test_image)

        # This should be the standard AT behaviour...
        ri_field = self.ri.getField('image')
        tag = ri_field.tag(self.ri)
        self.failUnless('height="200" width="500"' in tag)
        src = "http://nohost/plone/Members/test_user_1_/rich-image/image"
        self.failUnless(src in tag)

        # except that with the traversal adapter from `plone.app.imaging`
        # it's not possible anymore to use `restrictedTraverse`.  instead
        # we need proper url traversal employing the publisher...
        traverse = self.portal.REQUEST.traverseName
        obj = traverse(self.ri, 'image')

        self.assertEqual(obj.width, 500)
        self.assertEqual(obj.height, 200)

    def testGetSize(self):
        ri_field = self.ri.getField('image')

        self.ri.setImage(self.test_image)
        self.assertEqual(ri_field.getSize(self.ri), (500, 200))

        self.ri.setImage(self.test_image_small)
        self.assertEqual(ri_field.getSize(self.ri), (25, 10))

        self.ri.setImage(self.test_image_jpg)
        self.assertEqual(ri_field.getSize(self.ri), (500, 200))

    def testCropPreservesFormat(self):
        ri_field = self.ri.getField('image')
        self.ri.schema['image'].createCropsOnSet = True

        self.ri.setImage(self.test_image)
        crop = ri_field.getCrop(self.ri, crop='crop1')
        self.failUnless(crop.getContentType() == 'image/png')

        self.ri.setImage(self.test_image_small)
        crop = ri_field.getCrop(self.ri, crop='crop1')
        self.failUnless(crop.getContentType() == 'image/png')

        self.ri.setImage(self.test_image_jpg)
        crop = ri_field.getCrop(self.ri, crop='crop1')
        self.failUnless(crop.getContentType() == 'image/jpeg')

    def testCropTag(self):
        # used to get the crop tag avoiding the creation
        self.ri.schema['image'].createCropsOnSet = False
        self.ri.setImage(self.test_image)
        ri_field = self.ri.getField('image')

        for crop_id, crop_values in test_crops.items():
            self.failUnless(ri_field.crop_tag(self.ri, crop_id) == None)

            # let's create the crop now
            ri_field.tag(self.ri, scale=crop_id)
            crop_tag = ri_field.crop_tag(self.ri, crop_id)
            src = 'http://nohost/plone/Members/test_user_1_/rich-image/image_' + crop_id
            self.failUnless(src in crop_tag, crop_tag)
            x1, y1, x2, y2 = crop_values
            width = x2 - x1
            height = y2 - y1
            self.failUnless('height="%s"' % height in crop_tag, crop_tag)
            self.failUnless('width="%s"' % width in crop_tag, crop_tag)

    def testCropEditRatio(self):
        # Used by crop_edit template in order to make a selection on a scaled image
        # but the real crop is done on the full size image
        self.ri.setImage(self.test_image)
        ri_field = self.ri.getField('image')
        self.assertEqual(ri_field.cropEditRatio(self.ri), (5.0, 5.0))

        RichImageSchema['image'].ui_crop_scale = 'size2'
        self.assertEqual(ri_field.cropEditRatio(self.ri), (2.5, 2.5))

    def testAvailableCrops(self):
        self.ri.schema['image'].createCropsOnSet = False
        self.ri.setImage(self.test_image)

        self.failUnlessEqual(self.ri.available_crops(), [])

        # Traverse will create
        traverse = self.portal.REQUEST.traverseName

        for crop_id in test_crops.keys():
            obj = traverse(self.ri, 'image_%s' %crop_id)
            self.failUnless(crop_id in self.ri.available_crops())

        self.failUnlessEqual(self.ri.available_crops(), ['crop3', 'crop2', 'crop1'])

    def testCropBlob(self):
        self.ri.schema['image'].createCropsOnSet = False
        self.ri.setImage(self.test_image)

        ri_field = self.ri.getField('image')
        ri_field.getAvailableCrops(self.ri)
        # getRaw returns a BlobWrapper which _crop has to know how to handle
        thumbnail_file, format = ri_field._crop(ri_field.getRaw(self.ri), 0, 0, 10, 20)
        self.failUnless(thumbnail_file)
        self.failUnlessEqual(format, 'png')

    if HAVE_CACHESETUP:
        def testCachePurgeRelativeUrls(self):
            a=IPurgeUrls(self.ri, None)
            self.failUnless(isinstance(a, RichImagePurge))
            self.assertEqual(set(a.getRelativeUrls()),
                             set(['Members/test_user_1_/rich-image/crop1',
                                  'Members/test_user_1_/rich-image/crop2',
                                  'Members/test_user_1_/rich-image/crop3']))


        def testCacheNoAbsoluteUrls(self):
            a=IPurgeUrls(self.ri, None)
            self.assertEqual(a.getAbsoluteUrls(None), [])


def test_suite():
    return unittest.TestSuite([
        unittest.makeSuite(TestContent),
        ])


if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')

