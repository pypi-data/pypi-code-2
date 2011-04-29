from nose.plugins.skip import SkipTest
from .helpers import run_cmdapp

def test_no_commands_given_is_error():
    result = run_cmdapp(expect_error=True)
    assert 'bch-test-app: error: too few arguments' in result.stderr, str(result)

def test_help():
    result = run_cmdapp('--help')
    assert 'usage: bch-test-app [-h] [-v] [-q] {cahw,cahwu,foo}' in result.stdout, str(result)

def test_invalid_command():
    result = run_cmdapp('notthere', expect_error=True)
    assert "argument subparser: invalid choice: 'notthere' (choose from 'cahw', 'cahwu', 'foo')" in result.stderr, str(result)

def test_verbosity_too_high():
    result = run_cmdapp('-vvvv', 'cahw', expect_error=True)
    assert 'verbosity too high, max is -vvv' in result.stderr, str(result)

def test_system_command():
    result = run_cmdapp('cahw')
    assert 'hello world from system command' in result.stdout, str(result)

def test_user_command():
    result = run_cmdapp('cahwu')
    assert 'hello world from user command' in result.stdout, str(result)

def test_plugin_command():
    result = run_cmdapp('foo', load_test_plugins = True)
    assert 'entry-point foo' in result.stdout, str(result)
