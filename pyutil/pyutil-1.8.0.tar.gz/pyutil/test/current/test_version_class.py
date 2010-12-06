import re, unittest

from pyutil import version_class

class T(unittest.TestCase):
    def test_rc_regex(self):
        v = version_class.Version('9.9.9rc9')
        self.failUnlessEqual(str(v), '9.9.9c9')
