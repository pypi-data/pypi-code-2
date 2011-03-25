from itaps.helpers import *
from .. import testhelper as unittest
import numpy

class TestIndexedList(unittest.TestCase):
    def setUp(self):
        self.indices = reduce(lambda x, i: x+range(i, 3+i), range(4), [])

        self.list = IndexedList(
            numpy.arange(0, 13, 3),
            numpy.array(self.indices),
            numpy.arange(10, 16))

    def testBasic(self):
        self.assertEqual(len(self.list), 4)
        self.assert_((self.list[0] == range(10, 13)).all())

        self.assert_((self.list.indices.offsets == range(0, 13, 3)).all())
        self.assert_((self.list.indices.data == self.indices).all())
        self.assert_((self.list.data == range(10, 16)).all())

    def testIndex(self):
        for i, hunk in enumerate(self.list):
            self.assertEqual(len(hunk), 3)
            self.assertEqual(self.list.length(i), 3)
            self.assert_((hunk == range(i+10, i+13)).all())

            for j, val in enumerate(hunk):
                self.assertEqual(val, i+j+10)

        self.assertRaises(IndexError, lambda: self.list[4])
        self.assertRaises(IndexError, lambda: self.list[0, 3])
