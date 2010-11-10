from os.path import join, dirname
import shutil

# Backward compatible unittest
try:
    import unittest
    # skip was added in 2.7/3.1
    assert unittest.skip
except AttributeError:
    import unittest2 as unittest


class TestCase(unittest.TestCase):
    def setUp(self):
        self.here = dirname(__file__)
        self.fixtures = join(self.here, 'fixtures')
        self.working = join(self.fixtures, 'working')

        shutil.rmtree(self.working, ignore_errors=True)
