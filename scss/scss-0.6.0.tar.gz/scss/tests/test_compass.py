import os.path
import unittest

from scss import parser


class TestSCSS( unittest.TestCase ):

    def test_load(self):
        path = os.path.join(os.path.dirname(__file__), 'compass.scss')
        src = open(path).read()
        test = parser.parse(src)
        out = parser.load(open(path), precache=True)
        self.assertEqual(test, out)
