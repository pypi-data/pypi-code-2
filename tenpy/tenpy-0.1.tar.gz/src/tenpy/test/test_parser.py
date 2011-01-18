import sys

from ast import PyCF_ONLY_AST
from os.path import (dirname, abspath, join)
from unittest import TestCase
from test import support

sys.path.insert(0, dirname(dirname(dirname(abspath(__file__)))))
from tenpy.parser import TenpyFile

tenpyname = support.findfile("test.tenpy")


class TenpyFileTest(TestCase):

    def setUp(self):
        self.tenpyfile = TenpyFile()

    def test_parse(self):
        # TODO: tests the css
        line = self.tenpyfile.parse(join(dirname(abspath(__file__)), tenpyname))
        self.assertTupleEqual(line.__next__(), ("eval", "default",
            'evaltest = "eval test success"\n'))
        self.assertTupleEqual(line.__next__(), ("xpath", "span[@id='text']",
            '"example1"\n'))
        self.assertTupleEqual(line.__next__(), ("xpath", '*[@id="loop"]',
            ('["loop example2" for i in range(5)]\n')))
        self.assertTupleEqual(line.__next__(), ("xpath", "body/span[@id='loop_with']",
            """[{"p[@id='p1']:xpath": "loop example3",
  "p[@id='p2']:xpath": "loop example4",
  } for i in range(5)]
"""))


def test_main():
    support.run_unittest(TenpyFileTest)

if __name__ == "__main__":
    test_main()
