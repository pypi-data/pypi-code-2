"""
This is a vastly improved test runner over django's in-built runner.

It provides the following advantages:
  - Is not tied to application paths - you can choose to
    run tests found in any module path.
  - Prints exceptions as they occur, without waiting for
    the entire test suite to complete as unittest does.
  - assertEqual prints prettified output, so observing 
    discrepancies should be easier.  This can be further
    improved.

We also have integrated selenium support.

Usage:
  - Make your test classes derive from django_test.TestCase
  - Set your settings.TEST_RUNNER to django_test.run_tests
  - Run python manage.py test as normal:

    eg:
      python manage.py test module1.module2.module3
      python manage.py test module1.module2.Class
      python manage.py test module1.module2.Class.method

  - Settings in settings.TEST_SETTINGS dictionary will override normal settings
  - To run Selenium tests, set RUN_SELENIUM_TESTS to True

Limitations:
  - Currently, only classes ending with "Test" and methods
    starting with "test_" are found when looking for tests.
  - We don't have the full set of assert* functions.
  - We don't trap stdout output, so print statements in the
    tests will get in the way of the test results.  Would
    be better to save this somewhere and control when 
    we output it.
"""

import sys
import shutil
import itertools
import pprint
import inspect
import traceback, re, os, pdb      
from django import db
from django.core import mail
from django.conf import settings
from django.db import connection, transaction
from django.test.testcases import disable_transaction_methods, restore_transaction_methods
from django.core.urlresolvers import clear_url_caches
from django_test.xmlreport import XmlTestSuite
from django.contrib.sites.models import Site
from django.db.models.query import QuerySet
from django.db import connections, DEFAULT_DB_ALIAS
from django.core.management import call_command
from django.test.utils import setup_test_environment, teardown_test_environment
from optparse import OptionParser

from django_test.utils import import_object, import_module, restore_database
from django_test.variations import MyVariationRunner


class OptionDescriptor(object):
  def __init__(self, *args, **kwargs):
    self.args = args
    self.kwargs = kwargs

COMMAND_LINE_OPTIONS = (
  OptionDescriptor("-g", "--grep", dest = "grep", action = "append"),
  OptionDescriptor("-f", "--failed", dest = "failed", action = "store"),
  OptionDescriptor("-t", "--tag", dest = "tag", action = "store"),
  OptionDescriptor("-m", "--max_tries", dest = "max_tries", action = "store", 
                         type = "int", default = 1),
  #TODO:
  #make_option('--numworkers', '-n', dest='num_workers',
  #    help='The number of workers.'),
  #make_option('--workernum', '-w', dest='worker_num',
  #    help='The number of this worker [0..numworkers-1].'),
)


class TestDriver(object):
  def __init__(self, 
               test_paths = None, 
               num_workers = None, 
               worker_num = None,
               max_tries = 1):
    self.test_paths = test_paths
    self.num_workers = num_workers \
                       if num_workers != None \
                       else getattr(settings, "NUM_WORKERS", 1)
    self.worker_num = worker_num \
                      if worker_num != None \
                      else getattr(settings, "WORKER_NUM", 0)
    self.verbosity = 1
    self.max_tries = max_tries

    self.passed = 0
    self.errors = 0
    self.tests_seen = 0
    self.tests_run = 0

    #TODO: factor this
    self.suite = XmlTestSuite(self.worker_num)    
    self.modules = []
    self.classes = []
    self.methods = []
    self.filters = []


  def add_path(self, path):
    obj = import_object(path.replace(":", "."))

    if inspect.ismodule(obj):
      self.add_module(obj)
    elif inspect.isclass(obj):
      self.add_class(obj)
    elif inspect.ismethod(obj):
      self.add_method(obj.im_class, obj.__name__)
    else:
      raise Exception("%s should be a module, class or method." % self.test_path)


  def add_all_tests(self):
    modules = []
    for a in settings.INSTALLED_APPS:
      try:
        module = import_module(a + ".tests")
        if module not in modules:
          modules.append(module)
      except ImportError:
        print "Could not import %s" % (a + ".tests")

    for m in modules:
      self.add_module(m)


  def run(self):
    #TODO: factor this
    from playfi.util.debug import listen_for_sigquit
    listen_for_sigquit()

    setup_test_environment()
    settings.DEBUG = False
    old_name = settings.DATABASES["default"]["NAME"]
    
    if hasattr(settings, "TEST_SETTINGS"):
      for k, v in settings.TEST_SETTINGS.iteritems():
        setattr(settings, k, v)

    connection.creation.create_test_db(self.verbosity, 
                                       autoclobber = True)

    db.connections["default"].close()
    db_name = settings.DATABASES["default"]["TEST_NAME"]
    shutil.copyfile(db_name, db_name + ".bak")
    
    self.run_tests()

    connection.creation.destroy_test_db(old_name, self.verbosity)
    teardown_test_environment()

    print "%s passed, %s failed" % (self.passed, self.errors)


  def add_module(self, module):
    self.modules.append(module)

  def add_class(self, klass):
    self.classes.append(klass)

  def add_method(self, klass, method_name):
    self.methods.append((klass, method_name))

  def add_filter(self, predicate):
    self.filters.append(predicate)

  def test_method(self, class_or_object, method_name):
    if inspect.isclass(class_or_object):
      klass = class_or_object
      ob = class_or_object()
    else:
      klass = class_or_object.__class__
      ob = class_or_object

    method = ob.__getattribute__(method_name)
    method_path = "%s:%s.%s" % (klass.__module__, klass.__name__, method_name)

    self.tests_seen += 1

    if self.tests_seen % self.num_workers != self.worker_num:
      return

    if self.filters and not any([p(klass, method, method_path) for p in self.filters]):
      return

    if getattr(method, "long_test", False) and not getattr(settings, "RUN_LONG_TESTS", "True"):
      print "Skipping test %s as it's long and we're not running long tests."
      return

    result = self.suite.test(klass.__module__, klass.__name__, method_name)

    print >>sys.stderr, "-" * 50
    print >>sys.stderr, "%s (Worker %s/%s)" % \
                        (method_path, self.worker_num, self.num_workers)
    print >>sys.stderr, "-" * 50

    try_num = 1
    finished = False
    torn_down = False
    result.start()

    while not finished and try_num <= self.max_tries:
      try:
        # Actually run the test
        if getattr(method, "has_variations", False):
          self.coverage.start()
          MyVariationRunner().run_test(method)
          self.coverage.stop()
          torn_down = True
        else:
          ob._test_setup()
          ob.setUp()
          self.coverage.start()
          method()
          self.coverage.stop()

        if hasattr(ob, "post_test_checks"):
          ob.post_test_checks(method)

        result.success()
        finished = True

        print "PASSED"
        self.passed += 1
        self.tests_run += 1
      except Exception, e:
        if try_num == self.max_tries:
          print "FAILED: ", e
          etype, value, tb = sys.exc_info()
          
          st = traceback.format_tb(tb)
          ex = traceback.format_exception_only(etype, value)
          
          result.failure(''.join(ex), ''.join(st))      
          
          for line in itertools.chain(st, ex):
            print re.sub('(' + os.getcwd() + ')(.*)", (line \\d+)', 
                         '\\1\033[1;31m\\2\033[0;0;0m", \033[1;32m\\3\033[0;0;0m', 
                         line)

          if not (getattr(self, 'never_debug', False) or 
                  getattr(settings, "NEVER_DEBUG", False)):
            print "Would you like to debug? [y/N/neVer]"
            c = raw_input()
            if c.lower() == "y":
              pdb.post_mortem(sys.exc_info()[2])
            if c.lower() == "v":
              self.never_debug = True

          self.errors += 1
          self.tests_run += 1
        else:
          print "Failed.. retrying"

        try_num += 1
      finally:
        if not torn_down:
          ob.tearDown()
          ob._test_teardown()


  def test_class(self, klass):
    """
    We only create one instance of the test class, so consumers can
    put test-case-level initialisation in the class's __init__ method.
    """

    instance = klass()  

    for class_member_name in klass.__dict__:
      class_member = getattr(klass, class_member_name)
      if inspect.ismethod(class_member) and class_member_name.startswith("test_"):
        self.test_method(instance, class_member_name)

    if getattr(instance, "post_last_teardown", None):
      instance.post_last_teardown()


  def test_module(self, module):
    for module_object_name in dir(module):
      module_object = getattr(module, module_object_name)
      if inspect.isclass(module_object):
        if issubclass(module_object, TestCase):
          #TODO: factor this
          from django_test.selenium import SeleniumTestCase
          if not issubclass(module_object, SeleniumTestCase) or self.run_selenium_tests:
            self.test_class(module_object)


  def run_tests(self):
    #TODO: factor this
    from coverage import coverage
    self.coverage = coverage()

    self.run_selenium_tests = getattr(settings, "RUN_SELENIUM_TESTS", False)
    
    for m in self.modules:
      self.test_module(m)

    for c in self.classes:
      self.test_class(c)

    for c, m in self.methods:
      instance = c()
      self.test_method(instance, m)
      if getattr(instance, "post_last_teardown", None):
        instance.post_last_teardown()

    #TODO: factor this
    if hasattr(settings, "XML_REPORT_DIR"):
      self.suite.generate_xml(settings.XML_REPORT_DIR)

    #TODO: factor this
    self.coverage.html_report(directory = 'covhtml')



class CustomTestRunner(object):
  def run_tests(self, *test_paths, **options):
    driver = TestDriver(max_tries = options['max_tries'])

    if test_paths:
      for p in test_paths:
        driver.add_path(p)
    elif options['grep']:
      driver.add_all_tests()
      for p in options['grep']:
        driver.add_filter(lambda _1, _2, method_path: p in method_path)
    elif options['failed']:
      #TODO: factor this
      from playfi.util.hudson import get_failed_test_names
      for p in get_failed_test_names(int(['options'].failed)):
        driver.add_path(p)
    elif options['tag']:
      driver.add_all_tests()
      driver.add_filter(lambda _1, method, _: options['tag'] in getattr(method, 'tags', []))
    else:
      driver.add_all_tests()
      
    driver.run()



class TestCase(object):
  def __init__(self):
    pass

  def setUp(self):
    pass

  def tearDown(self):
    pass

  def assertEqual(self, o1, o2, message = ""):
    if isinstance(o1, QuerySet) or isinstance(o2, QuerySet):
      # Allow comparing of two `QuerySet`s, or a `QuerySet` and a `list`,
      # by converting `QuerySet`s to `list`s.
      return self.assertEqual(list(o1) if isinstance(o1, QuerySet) else o1,
                              list(o2) if isinstance(o2, QuerySet) else o2,
                              message)

    if o1 != o2:
      raise Exception("Not equal: \n%s\nand\n%s" % (pprint.pformat(o1)[0:10000],
                                                    pprint.pformat(o2)[0:10000])
                      + message)

  def assertContains(self, o1, o2, message = ""):
    if o2 not in o1:
      raise Exception("Not contained: \n%s\nand\n%s" % (pprint.pformat(o1)[0:10000],
                                                        pprint.pformat(o2)[0:10000])
                      + message)

  def assertTrue(self, o1):
    if not o1:
      raise Exception("Not true")

  def assertFalse(self, o1):
    if o1:
      raise Exception("Not false")

  def assertRaises(self, exc_type, func):
    try:
      func()
    except exc_type as ex:
      pass
    except Exception as ex:
      raise Exception("%s exception raised - we expected %s" % (ex, exc_type))
    else:
      raise Exception("No exception raised - we expected %s" % exc_type)

  def assertColumnsEqual(self, *args):
    for left, right in args:
      self.assertEqual(left, right)

  def _setup_urlconf(self):
    if hasattr(self, 'urls'):
      self._old_root_urlconf = settings.ROOT_URLCONF
      settings.ROOT_URLCONF = self.urls
      clear_url_caches()

  def _teardown_urlconf(self):
    if hasattr(self, '_old_root_urlconf'):
      settings.ROOT_URLCONF = self._old_root_urlconf
      clear_url_caches()

  def _flush_databases(self):
    # If the test case has a multi_db=True flag, flush all databases.
    # Otherwise, just flush default.
    if getattr(self, 'multi_db', False):
      databases = connections
    else:
      databases = [DEFAULT_DB_ALIAS]

    for db in databases:
      call_command('flush', verbosity=0, interactive=False, database=db)


  def setup_database(self, transactions = True):
    if not transactions:
      transaction.enter_transaction_management()
      transaction.managed(True)
      disable_transaction_methods()
    else:
      restore_database()

    Site.objects.clear_cache()

    if hasattr(self, 'fixtures'):
      call_command('loaddata', *self.fixtures, **{
                                                   'verbosity': 0,
                                                   'commit': False
                                                 })

  def teardown_database(self, transactions = True):
    if not transactions:
      restore_transaction_methods()
      transaction.rollback()
      transaction.leave_transaction_management()


  def _test_setup(self):
    """
    From django.test.testcases.TestCase._fixture_setup
    """

    self._setup_urlconf()
    self.setup_database(transactions = False)

  def _test_teardown(self):
    """
    From django.test.testcases.TestCase._fixture_teardown
    """
    mail.outbox = []
    self.teardown_database(transactions = False)
    self._teardown_urlconf()


  def post_test_checks(self, method):
    if not getattr(method, "allow_server_errors", False):
      #TODO: factor this
      from playfi.exception_middleware.models import ErrorReport
      # Do an actual list comparison so that if it fails, assertEqual
      # will print out the exception messages.
      self.assertEqual(list(ErrorReport.objects.all()), [])






