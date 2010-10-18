from Products.CMFCore.utils import getToolByName

from .base import ATRefSpeedupTestCase


class TestGetReferences(ATRefSpeedupTestCase):

    def afterSetUp(self):
        self.rc = getToolByName(self.portal, 'reference_catalog')

    def test_none(self):
        doc1 = self.portal.doc1
        doc2 = self.portal.doc2
        self.assertEquals(self.rc.getReferences(doc1), [])
        self.assertEquals(self.rc.getReferences(doc1, 'relatesTo'), [])
        self.assertEquals(self.rc.getReferences(doc1, 'relatesTo', doc2), [])

    def test_single(self):
        doc1 = self.portal.doc1
        doc2 = self.portal.doc2
        doc3 = self.portal.doc3
        doc1.setRelatedItems([doc2.UID()])
        result = self.rc.getReferences(doc1)
        self.assertEquals(result[0].getTargetObject(), doc2)
        result = self.rc.getReferences(doc1, 'relatesTo')
        self.assertEquals(result[0].getTargetObject(), doc2)
        result = self.rc.getReferences(doc1, 'relatesTo', doc2)
        self.assertEquals(result[0].getTargetObject(), doc2)
        result = self.rc.getReferences(doc1, 'relatesTo', doc3)
        self.assertEquals(result, [])

    def test_many(self):
        doc1 = self.portal.doc1
        doc2 = self.portal.doc2
        doc3 = self.portal.doc3
        uids = [doc2.UID(), doc3.UID()]
        doc1.setRelatedItems(uids)
        result = [r.getTargetObject() for r in self.rc.getReferences(doc1)]
        self.assertEquals(set(result), set([doc2, doc3]))

    def test_bidi(self):
        doc1 = self.portal.doc1
        doc2 = self.portal.doc2
        doc1.setRelatedItems([doc2.UID()])
        doc2.setRelatedItems([doc1.UID()])
        result = [r.getTargetObject() for r in self.rc.getReferences(doc1)]
        self.assertEquals(result, [doc2])
        result = [r.getTargetObject() for r in self.rc.getReferences(doc2)]
        self.assertEquals(result, [doc1])


class TestGetBackReferences(ATRefSpeedupTestCase):

    def afterSetUp(self):
        self.rc = getToolByName(self.portal, 'reference_catalog')

    def test_none(self):
        doc1 = self.portal.doc1
        doc2 = self.portal.doc2
        self.assertEquals(self.rc.getBackReferences(doc1), [])
        self.assertEquals(self.rc.getBackReferences(doc1, 'relatesTo'), [])
        self.assertEquals(self.rc.getBackReferences(doc1, 'relatesTo', doc2),
                          [])

    def test_single(self):
        doc1 = self.portal.doc1
        doc2 = self.portal.doc2
        doc3 = self.portal.doc3
        doc1.setRelatedItems([doc2.UID()])
        result = self.rc.getBackReferences(doc2)
        self.assertEquals(result[0].getSourceObject(), doc1)
        result = self.rc.getBackReferences(doc2, 'relatesTo')
        self.assertEquals(result[0].getSourceObject(), doc1)
        result = self.rc.getBackReferences(doc2, 'relatesTo', doc1)
        self.assertEquals(result[0].getSourceObject(), doc1)
        result = self.rc.getBackReferences(doc2, 'relatesTo', doc3)
        self.assertEquals(result, [])

    def test_many(self):
        doc1 = self.portal.doc1
        doc2 = self.portal.doc2
        doc3 = self.portal.doc3
        uids = [doc2.UID(), doc3.UID()]
        doc1.setRelatedItems(uids)
        result = [r.getSourceObject() for r in self.rc.getBackReferences(doc2)]
        self.assertEquals(set(result), set([doc1]))
        result = [r.getSourceObject() for r in self.rc.getBackReferences(doc3)]
        self.assertEquals(set(result), set([doc1]))

    def test_bidi(self):
        doc1 = self.portal.doc1
        doc2 = self.portal.doc2
        doc1.setRelatedItems([doc2.UID()])
        doc2.setRelatedItems([doc1.UID()])
        result = [r.getSourceObject() for r in self.rc.getBackReferences(doc1)]
        self.assertEquals(result, [doc2])
        result = [r.getSourceObject() for r in self.rc.getBackReferences(doc2)]
        self.assertEquals(result, [doc1])


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestGetReferences))
    suite.addTest(makeSuite(TestGetBackReferences))
    return suite
