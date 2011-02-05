"""Tests for pyverify.verify.
"""
import os
import unittest

from pyverify.verify import verify_installed_files
from pyverify.verify import verify_dists
from distutils2._backport.pkgutil import Distribution

CWD = os.path.abspath(os.path.dirname(__file__))
DISTINFO = os.path.join(CWD, 'site-packages/dummy-0.1.dist-info')
DISTINFO_PATH = os.path.dirname(DISTINFO)


class VerifyTestCase(unittest.TestCase):

    def test_verify_installed_files_missing(self):
        """Test verifing installed files that are all missing.
        """
        expected = [
            ('dummy.py', '', '', 2), ('dummy.pyc', '', '', 0),
            ('METADATA', '', '', 2), ('INSTALLER', '', '', 2),
            ('REQUESTED', '', '', 2), ('RECORD', '', '', 0)]
        path = DISTINFO
        dist = Distribution(path=path)
        installed_files = dist.get_installed_files()
        verified_files = [f for f in verify_installed_files(installed_files)]
        self.assertEqual(expected, verified_files)

    def test_verify_dists(self):
        """Test verifing distros and all installed files that
        are all missing.
        """
        expected = [('dummy', {'status': 4, 'verified_files': [
            ('dummy.py', '', '', 2), ('dummy.pyc', '', '', 0),
            ('METADATA', '', '', 2), ('INSTALLER', '', '', 2),
            ('REQUESTED', '', '', 2), ('RECORD', '', '', 0)]})]
        dists = ['dummy']
        paths = [DISTINFO_PATH]
        verified_dists = [d for d in verify_dists(dists, paths=paths)]
        self.assertEqual(expected, verified_dists)


def test_suite():
    return unittest.makeSuite(VerifyTestCase)

if __name__ == "__main__":
    unittest.main(defaultTest="test_suite")
