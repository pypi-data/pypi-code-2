from decimal import Decimal
from nose.tools import eq_
from nose.plugins.skip import SkipTest
from blazech.config import parse_config_files
from blazech.exceptions import ConfigError
from helpers import get_config_path, set_test_fpath_root, run_batch

#this code is from pysjobs, hasn't been converted as part of bch
raise SkipTest

def teardown_module():
    set_test_fpath_root()

def test_parse_config_files():
    config = parse_config_files(
        True,
        get_config_path('basic1.conf'),
    )
    eq_(config.batch.logfile.verbosity, 2)
    eq_(config.batch.console.verbosity, 1)

def test_parse_config_files_overwrite_correctly():
    config = parse_config_files(
        True,
        (
            get_config_path('basic1.conf'),
            get_config_path('basic2.conf'),
        )
    )
    # setting from second file overwrites first
    eq_(config.batch.logfile.verbosity, 3)
    # setting from first still comes through
    eq_(config.batch.console.verbosity, 1)
    # default settings gets overriden
    eq_(config.logging.mainlog.path, 'blazech.conf')

def test_parse_config_decimal_conversion():
    config = parse_config_files(
        True,
        get_config_path('basic1.conf'),
    )
    eq_(config.batch.decimal_test, Decimal('1.23456'))

def test_no_configs():
    try:
        parse_config_files(True, list())
        True,
        assert False, 'should have raised ConfigError'
    except ConfigError, e:
        assert 'At least one configuration file is expected' == str(e)

def test_system_default_config():
    set_test_fpath_root('systemonly')
    config = parse_config_files(True, list())
    assert config.batch.is_system == 1
    assert config.batch.from_where == 'system'

def test_user_default_config():
    set_test_fpath_root('useronly')
    config = parse_config_files(True, list())
    assert config.batch.from_where == 'user'

def test_system_and_user_default_config():
    set_test_fpath_root('both')
    config = parse_config_files(True, list())
    assert config.batch.is_system == 1
    assert config.batch.from_where == 'user'

def test_no_system_config_files():
    set_test_fpath_root('both')
    config = parse_config_files(
        False,
        get_config_path('basic1.conf'),
    )
    eq_(config.batch.logfile.verbosity, 2)
    eq_(config.batch.console.verbosity, 1)
    assert not hasattr(config.batch, 'from_where')

def test_section_includes():
    config = parse_config_files(
        False,
        get_config_path('basic1.conf'),
    )
    # section local
    eq_(config.second.s4, 4)
    # from first included section and no overwrite of/by section local
    eq_(config.second.s3, 3)
    # from second included section and no overwrite of/by section local
    eq_(config.second.s6, 6)
    # section local after include takes precedence
    eq_(config.second.s2, 'foobar')
    # section local before include gets overwritten
    eq_(config.second.s1, 1)
    # second section overwrites first
    eq_(config.second.s5, 2)
