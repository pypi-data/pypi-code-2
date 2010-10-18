from .base import ATRefSpeedupTestCase


class TestReferenceable(ATRefSpeedupTestCase):

    def test_no_references(self):
        doc1 = self.portal.doc1
        self.assertEquals(doc1.getRelatedItems(), [])
        self.assertEquals(doc1.getRawRelatedItems(), [])
        self.assertEquals(doc1.getReferences(), [])
        self.assertEquals(doc1.getRelationships(), [])

    def test_single_reference(self):
        doc1 = self.portal.doc1
        doc2 = self.portal.doc2
        doc1.setRelatedItems([doc2.UID()])
        self.assertEquals(doc1.getRelatedItems(), [doc2])
        self.assertEquals(doc1.getRawRelatedItems(), [doc2.UID()])
        self.assertEquals(doc1.getReferences(), [doc2])
        self.assertEquals(doc1.getRelationships(), ['relatesTo'])

    def test_many_references(self):
        doc1 = self.portal.doc1
        doc2 = self.portal.doc2
        doc3 = self.portal.doc3
        uids = [doc2.UID(), doc3.UID()]
        doc1.setRelatedItems(uids)
        self.assertEquals(set(doc1.getRelatedItems()), set([doc2, doc3]))
        self.assertEquals(set(doc1.getRawRelatedItems()), set(uids))
        self.assertEquals(set(doc1.getReferences()), set([doc2, doc3]))
        self.assertEquals(doc1.getRelationships(), ['relatesTo'])

    def test_bidi_references(self):
        doc1 = self.portal.doc1
        doc2 = self.portal.doc2
        doc1.setRelatedItems([doc2.UID()])
        doc2.setRelatedItems([doc1.UID()])
        self.assertEquals(doc1.getRelatedItems(), [doc2])
        self.assertEquals(doc1.getRawRelatedItems(), [doc2.UID()])
        self.assertEquals(doc1.getReferences(), [doc2])
        self.assertEquals(doc1.getRelationships(), ['relatesTo'])
        self.assertEquals(doc2.getRelatedItems(), [doc1])
        self.assertEquals(doc2.getRawRelatedItems(), [doc1.UID()])
        self.assertEquals(doc2.getReferences(), [doc1])
        self.assertEquals(doc2.getRelationships(), ['relatesTo'])


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestReferenceable))
    return suite
