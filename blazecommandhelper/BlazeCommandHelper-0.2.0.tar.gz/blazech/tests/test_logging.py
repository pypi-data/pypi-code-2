from nose.tools import eq_, raises
from nose.plugins.skip import SkipTest
from blazech.config import DefaultConfig
from blazech.exceptions import ConfigError
import blazech.log
from blazeutils.testing import logging_handler, clear_test_handlers, ListIO
from helpers import run_batch, TestConfig, get_config_path, run_bch

#this code is from pysjobs, hasn't been converted as part of bch
raise SkipTest

@raises(ConfigError)
def test_value_error_with_bad_logging_config():
    settings = TestConfig()
    settings.logging.mainlog.verbosity = 'foobar'
    try:
        run_batch(settings)
    except ConfigError, e:
        if 'unrecognized value for logging.mainlog.verbosity: foobar' in str(e):
            raise

class TestBatchLogs(object):

    @classmethod
    def teardown_class(cls):
        clear_test_handlers()

    def test_succesful_job_at_batch_level(self):
        settings = TestConfig()
        settings.job.test._action_ = 'test_use_only'
        lh = logging_handler('blazech.Batch')
        result = run_batch(settings)
        assert 'batch started' in lh.current, lh.current
        assert 'test_use_only which maps to TestUseOnly' in lh.next, lh.current
        assert 'running job test' in lh.next, lh.current
        assert 'batch completed' in lh.next, lh.current

    def test_action_class_that_doesnt_exist(self):
        settings = TestConfig()
        settings.job.test._action_ = 'not_really_there'
        lh = logging_handler('blazech.Batch', 10)
        result = run_batch(settings)
        assert 'action class NotReallyThere can not be imported' in lh.next, lh.current

    def test_job_causes_exception(self):
        settings = TestConfig()
        settings.job.test._action_ = 'raise_exception'
        lh = logging_handler('blazech.Batch', 10)
        result = run_batch(settings)
        lh.next
        assert 'job test raised an exception' in lh.next, lh.current

    def test_no_jobs(self):
        settings = TestConfig()
        lh = logging_handler('blazech.Batch', 10)
        result = run_batch(settings)
        assert 'job test could not be run: no jobs have been configured' in lh.next, lh.current

    def test_no_job_settings(self):
        settings = TestConfig()
        settings.job.otherjob._action_ = 'raise_exception'
        lh = logging_handler('blazech.Batch', 10)
        result = run_batch(settings)
        assert 'job test could not be run: its settings were not found' in lh.next, lh.current

    def test_no_action_settings(self):
        settings = TestConfig()
        settings.job.test.foo = 'bar'
        lh = logging_handler('blazech.Batch', 10)
        result = run_batch(settings)
        assert 'job test could not be run: it did not have an _action_ setting' in lh.next, lh.current

class TestStdoutLogging(object):

    @classmethod
    def setup_class(cls):
        cls.cstream = ListIO()
        blazech.log.CONSOLE_STREAM = cls.cstream

    @classmethod
    def teardown_class(cls):
        blazech.log.CONSOLE_STREAM = None

    def tearDown(self):
        self.cstream.reset()

    def test_default_stdout_logging(self):
        settings = DefaultConfig()
        run_batch(settings)
        assert 'batch started' in self.cstream.current, self.cstream.current
        assert 'no jobs have been configured' in self.cstream.next, self.cstream.current
        assert 'batch completed' in self.cstream.next, self.cstream.current

    def test_console_logging_off(self):
        settings = TestConfig()
        run_batch(settings)
        assert len(self.cstream.contents) == 0

    def test_inc_errors_is_false(self):
        settings = DefaultConfig()
        settings.job.test._action_ = 'raise_exception'
        run_batch(settings)
        assert len(self.cstream.contents) == 4
        assert self.cstream.contents[2].strip().endswith('job test raised an exception')

    def test_inc_errors_is_true(self):
        settings = DefaultConfig()
        settings.console.inc_errors = True
        settings.job.test._action_ = 'raise_exception'
        run_batch(settings)
        assert len(self.cstream.contents) == 5, self.cstream.contents
        assert 'Traceback' in self.cstream.contents[2].strip()

    def test_quiet_flag(self):
        res = run_bch('info_console_output.conf', '-q', 'test')
        eq_(res.stdout.count('\n'), 0)

    def test_cmd_line_verbosity_takes_precedence_over_config_file(self):
        res = run_bch('info_console_output.conf', '-vvv', 'test')
        assert 'which maps to TestUseOnly' in res.stdout

    def test_cmd_line_vv_includes_stack_trace(self):
        res = run_bch('info_console_output.conf', '-v', 'error')
        assert 'Traceback' not in res.stdout

        res = run_bch('info_console_output.conf', '-vv', 'error')
        assert 'Traceback' in res.stdout

class TestFileLogging(object):

    def test_default_logging_is_not_setup(self):
        res = run_bch('default_file_logging.conf', 'test')
        assert len(res.files_created) == 0

    def test_minimal(self):
        res = run_bch('minimal_file_logging.conf', 'test')
        assert len(res.files_created) == 1
        lfile = res.files_created['blazech.log']
        assert 'batch started' in lfile
        assert 'no jobs have been configured' in lfile
        assert 'batch completed' in lfile
        as_list = open(lfile.full).read().strip().split('\n')
        assert len(as_list) == 3, as_list

    def test_error_file(self):
        res = run_bch('error_file_logging.conf', 'test')
        assert len(res.files_created) == 2
        lfile = res.files_created['blazech.log']
        as_list = open(lfile.full).read().strip().split('\n')
        assert len(as_list) == 4, as_list
        lfile = res.files_created['blazech_error.log']
        assert 'job test raised an exception' in lfile
        assert 'Traceback' in lfile
