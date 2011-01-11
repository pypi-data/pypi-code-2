import sys

from os.path import (dirname, abspath)
from unittest import TestCase
from test import support

sys.path.insert(0, dirname(dirname(dirname(abspath(__file__)))))
from tenpy.util import flatten

class UtilTest(TestCase):

    def test_flatten(self):
        self.assertListEqual(flatten([]), [])
        self.assertListEqual(flatten([1, 2, 3]), [1, 2, 3])
        self.assertListEqual(flatten([[1], [2], [3]]), [1, 2, 3])
        self.assertListEqual(flatten([[1, 2], [3, 4]]), [1, 2, 3, 4])
        self.assertListEqual(flatten([[[1, 2], [3]], [[4], [5, 6]]]),
                [1, 2, 3, 4, 5, 6])
        self.assertListEqual(flatten([[[[[[[[1]]]]]]]]), [1])


def test_main():
    support.run_unittest(UtilTest)

if __name__ == "__main__":
    test_main()
