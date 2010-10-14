from unittest import defaultTestLoader
from Products.RichImage.tests.base import RichImageTestCase
from Products.RichImage.tests.base import HAS_LINGUA

from Products.CMFCore.utils import getToolByName


class LinguaPloneTests(RichImageTestCase):

    def afterSetUp(self):
        self.setRoles(('Manager',))
        ltool = getToolByName(self.portal, 'portal_languages')
        ltool.manage_setLanguageSettings(defaultLanguage='en',
            supportedLanguages=('en', 'de'))

        self.loginAsPortalOwner()
        self.folder.invokeFactory('RichImage', 'rich-image')
        self.ri = getattr(self.folder, 'rich-image')

    if HAS_LINGUA:
        def testCopyCropToTranslations(self):
            self.ri.setImage(self.test_image)
            self.ri.addTranslation('de')
            self.ride = getattr(self.folder, 'rich-image-de')

            # Make sure there are no person crops
            self.failIf(getattr(self.ri, 'image-person', None))
            self.failIf(getattr(self.ride, 'image-person', None))

            field = self.ri.getField('image')
            x1, y1, x2, y2 = field.crops['person']
            field._createCrop(self.ri, 'person', x1, y1, x2, y2)

            # Make sure the new crop exists
            self.failUnless(field.getCrop(self.ri, 'person'))
            # And is the same on the translation
            self.failUnlessEqual(field.getCrop(self.ri, 'person'), field.getCrop(self.ride, 'person'))

def test_suite():
    return defaultTestLoader.loadTestsFromName(__name__)
