"""Tests for the `demain` package."""

import demain
__main__ = demain.fix()

import os
import sys
import unittest
from subprocess import check_call

thisdir = os.path.dirname(__file__)
def tfile(*names):
    return os.path.join(thisdir, 'test_situations', *names)

def env(*other_paths):
    paths = [ os.path.dirname(thisdir) ]  # so `demain` will be in path
    paths.extend(other_paths)
    return {'PYTHONPATH': ':'.join(paths)}

class BasicTests(unittest.TestCase):

    def test_situation1_invoked_as_script(self):
        check_call([sys.executable, tfile('situation1', 'foo.py')], env=env())

    def test_situation1_invoked_with_dash_m(self):
        check_call([sys.executable, '-m', 'foo'],
                   env=env(tfile('situation1')))

    def test_situation2(self):
        check_call([sys.executable, '-m', 'bigpackage.foo'],
                   env=env(tfile('situation2')))

    def test_situation3(self):
        check_call([sys.executable, '-m', 'bigpackage.foo'],
                   env=env(tfile('situation3')))

    def test_chrism(self):
        check_call([sys.executable, tfile('chrism', 'app.py')], env=env())

if __main__:
    unittest.main()
