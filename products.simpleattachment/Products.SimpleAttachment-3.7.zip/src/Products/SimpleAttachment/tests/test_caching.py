from Products.CMFPlone.utils import _createObjectByType as create
from Products.SimpleAttachment.tests.base import IntegrationTestCase
from Products.SimpleAttachment.tests.utils import getData


class CachingTests(IntegrationTestCase):

    def afterSetUp(self):
        self.setRoles(('Manager',))

    def makeOne(self, filename):
        return create('FileAttachment', self.folder, 'foo',
            title='Foo Bar', file=getData(filename))

    def testSearchableTextReturnsText(self):
        attachment = self.makeOne('plone3.pdf')
        self.failUnless('Plone 3' in attachment.SearchableText())

    def testSearchableTextCachesTransformedFile(self):
        attachment = self.makeOne('plone3.pdf')
        original = attachment.SearchableText()
        # after the first call the transformed output should be cached
        # so let's sneak in a different value and check again...
        storage = attachment.getField('file').getStorage()
        storage.set('file', attachment, 'hurz!')
        self.assertEqual(attachment.getFile().data, 'hurz!')
        self.assertEqual(attachment.SearchableText(), original)

    def testMutatorInvalidatesCache(self):
        attachment = self.makeOne('plone3.pdf')
        self.failUnless('Plone 3' in attachment.SearchableText())
        attachment.setFile(getData('plone4.pdf'))
        self.failUnless('Plone 4' in attachment.SearchableText())

    def testFieldSetInvalidatesCache(self):
        attachment = self.makeOne('plone3.pdf')
        self.failUnless('Plone 3' in attachment.SearchableText())
        attachment.getField('file').set(attachment, getData('plone4.pdf'))
        self.failUnless('Plone 4' in attachment.SearchableText())

    def testUpdateInvalidatesCache(self):
        attachment = self.makeOne('plone3.pdf')
        self.failUnless('Plone 3' in attachment.SearchableText())
        attachment.update(file=getData('plone4.pdf'))
        self.failUnless('Plone 4' in attachment.SearchableText())


def test_suite():
    from unittest import defaultTestLoader
    return defaultTestLoader.loadTestsFromName(__name__)
