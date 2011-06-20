import unittest
import tempfile
from kforge.testunit import TestCase

def suite():
    "Return a TestSuite of kforge.command TestCases."
    suites = [
            unittest.makeSuite(TestUtils),
            unittest.makeSuite(TestPassword),
        ]
    return unittest.TestSuite(suites)

class TestUtils(TestCase):

    def test_import(self):
        if self.dictionary['captcha.enable']:
            # check module imports
            import kforge.utils.captcha  

import kforge.utils.password
class TestPassword(TestCase):

    def test_generate(self):
        out = kforge.utils.password.generate()
        self.failUnless(len(out) == 8)

    def test_generate_2(self):
        size = 10
        out = kforge.utils.password.generate(size)
        self.failUnless(len(out) == size)

