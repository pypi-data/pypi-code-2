from unittest import defaultTestLoader
from Products.RichImage.tests.base import RichImageTestCase

from Products.CMFCore.utils import getToolByName


class BlobTests(RichImageTestCase):

    def afterSetUp(self):
        self.setRoles(('Manager',))
        ltool = getToolByName(self.portal, 'portal_languages')
        ltool.manage_setLanguageSettings(defaultLanguage='en',
            supportedLanguages=('en', 'de'))

    def testCreateRichImage(self):
        data = self.test_image
        img = self.folder[self.folder.invokeFactory('RichImage', 'richie')]
        img.update(title='A very rich image.', image=data, language='en')
        self.assertEqual(img.Title(), 'A very rich image.')
        self.assertEqual(img.Language(), 'en')
        self.assertEqual(img.getPortalTypeName(), 'RichImage')
        self.assertEqual(img.getContentType(), 'image/png')
        self.assertEqual(str(img.getImage()), data)
        self.assertEqual(img.getSize(), (500, 200))
        self.failUnless('/richie/image"' in img.tag())
        request = img.REQUEST
        response = request.RESPONSE
        self.assertEqual(img.index_html(request, response).read(), data)
        headers = response.headers
        self.assertEqual(response.headers['status'], '200 OK')
        self.assertEqual(response.headers['content-length'], str(len(data)))
        self.assertEqual(response.headers['content-type'], 'image/png')


def test_suite():
    return defaultTestLoader.loadTestsFromName(__name__)

