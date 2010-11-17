import unittest
from Products.OrderableReferenceField.tests.base import TestCase


class OrderableReferenceFieldTest(TestCase):

    def afterSetUp(self):
        from Products.OrderableReferenceField import OrderableReferenceField
        self.field = OrderableReferenceField('aField', relationship='aField')
        self.folder.validate_field = lambda *args, **kw: None

        self.folder.invokeFactory('Document', 'd1')
        self.folder.invokeFactory('Document', 'd2')

    def test_defaults(self):
        self.assertEquals(self.field.get(self.folder), [])

    def test_getRaw(self):
        self.assertEquals(self.field.getRaw(self.folder), [])
        self.field.set(self.folder, [self.folder.d1.UID()])
        self.assertEquals(self.field.getRaw(self.folder),
                          [self.folder.d1.UID()])

    def test_set(self):
        self.assertEquals(self.field.get(self.folder), [])
        self.field.set(self.folder, [self.folder.d2, self.folder.d1])
        self.assertEquals(self.field.get(self.folder),
                          [self.folder.d2, self.folder.d1])


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(OrderableReferenceFieldTest))
    return suite
