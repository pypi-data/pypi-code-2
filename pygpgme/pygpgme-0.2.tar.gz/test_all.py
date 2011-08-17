import sys
import unittest

import gpgme.tests

def test_suite():
    return gpgme.tests.test_suite()

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
