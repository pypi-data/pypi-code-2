import unittest
import tempfile
import os
import glob
import dumbdbm

try:
    import gdbm
except ImportError:
    gdbm = None

try:
    import dbm
except ImportError:
    dbm = None

from linkexchange.tests import MultiHashDriverTestCaseMixin
from linkexchange.db_drivers import MemMultiHashDriver
from linkexchange.db_drivers import ShelveMultiHashDriver

class MemMultiHashDriverTestCase(MultiHashDriverTestCaseMixin,
        unittest.TestCase):

    def setUpClass(cls):
        cls.db = MemMultiHashDriver()
    setUpClass = classmethod(setUpClass)

    def tearDownClass(cls):
        del cls.db
    tearDownClass = classmethod(tearDownClass)

class ShelveMultiHashDriverTestCaseMixin(MultiHashDriverTestCaseMixin):
    db_module = None

    def setUpClass(cls):
        cls.tmpdir = tempfile.mkdtemp()
        cls.db = ShelveMultiHashDriver(
                os.path.join(cls.tmpdir, 'test-XXX.db'),
                db_module=cls.db_module)
    setUpClass = classmethod(setUpClass)

    def tearDownClass(cls):
        files = glob.glob(os.path.join(cls.tmpdir, '*'))
        for x in files: os.unlink(x)
        os.rmdir(cls.tmpdir)
    tearDownClass = classmethod(tearDownClass)

class ShelveMultiHashDriverGDBMTestCase(ShelveMultiHashDriverTestCaseMixin,
        unittest.TestCase):
    db_module = gdbm

class ShelveMultiHashDriverDBMTestCase(ShelveMultiHashDriverTestCaseMixin,
        unittest.TestCase):
    db_module = dbm

class ShelveMultiHashDriverDumbDBMTestCase(ShelveMultiHashDriverTestCaseMixin,
        unittest.TestCase):
    db_module = dumbdbm
