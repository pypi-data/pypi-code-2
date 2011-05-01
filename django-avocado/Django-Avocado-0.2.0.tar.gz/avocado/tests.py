from django.utils import unittest
from django.test.utils import setup_test_environment, teardown_test_environment
from django.contrib.auth.models import User

from avocado.context import *
from avocado.models import *


class BasicTestCase(unittest.TestCase):

    def setUp(self):
        self.u = User.objects.create(username='test', first_name='t', last_name='t', email='t@t.com', password='t')

    def tearDown(self):
        User.objects.all().delete()
        LogEntry.objects.all().delete()

    def test_basic(self):
        with get_context("my context") as log:
            log.debug("debug", instance=self.u)
        self.assertTrue(LogEntry.objects.all().count() == 1)

    def test_basic_many(self):
        with get_context("my context") as log:
            for i in range(0, 100):
                log.debug("debug %s" % i, instance=self.u)
            self.assertTrue(LogEntry.objects.all().count() == 0)
        self.assertTrue(LogEntry.objects.all().count() == 100)

    def test_get_context_debug(self):
        with get_context("my context") as log:
            log.debug("debug")
        self.assertTrue(LogEntry.objects.all().count() == 1)

    def test_get_context_info(self):
        with get_context("my context") as log:
            log.info("info")
        self.assertTrue(LogEntry.objects.all().count() == 1)

    def test_get_context_critical(self):
        with get_context("my context") as log:
            log.critical("critical")
        self.assertTrue(LogEntry.objects.all().count() == 1)

    def test_get_context_warning(self):
        with get_context("my context") as log:
            log.warning("warning")
        self.assertTrue(LogEntry.objects.all().count() == 1)

    def test_get_context_error(self):
        with get_context("my context") as log:
            log.error("error")
        self.assertTrue(LogEntry.objects.all().count() == 1)

    def test_get_context_exception(self):
        with get_context("my context") as log:
            log.exception("exception", str(Exception()), instance=self.u)
        self.assertTrue(LogEntry.objects.all().count() == 1)

    def test_get_singleton_context(self):
        ctx1 = get_singleton_context("my context")
        ctx2 = get_singleton_context("my context")
        self.assertIs(ctx1,ctx2)

    def test_get_singleton_context_debug(self):
        ctx1 = get_singleton_context("my context1")
        ctx2 = get_singleton_context("my context2")
        ctx1.debug("debug1")
        ctx2.debug("debug2")
        self.assertEqual(LogEntry.objects.all().count(), 0)
        ctx1.flush()
        self.assertEqual(LogEntry.objects.all().count(), 2)

    def test_exc_plus(self):
        with get_context("my context") as log:
            try:
               a = 1
               b = 2
               c = a +b
               raise Exception("fdsfd")
            except Exception, e:
                log.exception("exception", "Caught exception doing some math. Not uncommon.")
        self.assertTrue(LogEntry.objects.all().count() == 1)
