from nose.plugins.skip import SkipTest
from .helpers import run_bch

def test_no_commands_found_error():
    result = run_bch(use_test_config='none', expect_error=True)
    assert 'Error: no commands found or registered' in result.stderr, str(result)

def test_no_commands_given_is_error():
    result = run_bch(expect_error=True)
    assert 'bch: error: too few arguments' in result.stderr, str(result)

def test_help():
    result = run_bch('--help')
    assert 'usage: bch [-h] [-v] [-q] {hwu,hw}' in result.stdout, str(result)

def test_invalid_command():
    result = run_bch('notthere', expect_error=True)
    assert "argument subparser: invalid choice: 'notthere' (choose from 'hwu', 'hw')" in result.stderr, str(result)

def test_verbosity_too_high():
    result = run_bch('-vvvv', 'hw', expect_error=True)
    assert 'verbosity too high, max is -vvv' in result.stderr, str(result)

def test_system_command():
    result = run_bch('hw')
    assert 'hello world from system command' in result.stdout, str(result)

def test_user_command():
    result = run_bch('hwu')
    assert 'hello world from user command' in result.stdout, str(result)
