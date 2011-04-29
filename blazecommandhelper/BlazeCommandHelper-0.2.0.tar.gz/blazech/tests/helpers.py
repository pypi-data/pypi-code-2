import os, sys
import blazech
from blazech.config import DefaultConfig
from blazech.locations import set_paths
from blazeutils.config import QuickSettings
from blazeutils.helpers import tolist

here = os.path.dirname(os.path.abspath(__file__))
base_path = os.path.join(here, 'test-scratch')

from scripttest import TestFileEnvironment

def get_tfenv(load_test_plugins, use_test_config):
    osenv = os.environ.copy()
    if not load_test_plugins:
        osenv['BCH_LOAD_TEST_PLUGINS'] = '0'
    else:
        osenv['BCH_LOAD_TEST_PLUGINS'] = '1'
    osenv['BCH_USE_TEST_CONFIG'] = use_test_config
    return TestFileEnvironment(os.path.join(here, 'test-output'), environ=osenv)

class TestConfig(DefaultConfig):
    def __init__(self):
        DefaultConfig.__init__(self)
        self.console.verbosity = 'none'

def run_bch(*args, **kw):
    load_test_plugins = kw.pop('load_test_plugins', False)
    use_test_config = kw.pop('use_test_config', 'both')
    env = get_tfenv(load_test_plugins, use_test_config)
    if args and args[0].endswith('.conf'):
        args=list(args)
        configpath = get_config_path(args.pop(0))
        args = ['bch', '-c', configpath] + args
    else:
        args = ('bch',) + args
    env.clear()
    result = env.run(*args, **kw)
    return result

def run_cmdapp(*args, **kw):
    load_test_plugins = kw.pop('load_test_plugins', False)
    use_test_config = kw.pop('use_test_config', 'both')
    env = get_tfenv(load_test_plugins, use_test_config)
    if args and args[0].endswith('.conf'):
        args=list(args)
        configpath = get_config_path(args.pop(0))
        args = ['bch-test-app', '-c', configpath] + args
    else:
        args = ('bch-test-app',) + args
    env.clear()
    result = env.run(*args, **kw)
    return result

def run_batch(config, *args):
    if not args:
        args = ('test', )
    if isinstance(config, QuickSettings):
        config.lock()
        return blazech.Batch(config, args).run()
    else:
        configpath = get_config_path(config)
        args = ['-c', configpath] + list(args)
        return blazech.run_batch(args)

# tell Nose not to test anything in here and test it
__test__ = False
def test_should_not_run():
    assert False

def get_config_path(fname):
    return os.path.join(here, 'configs', fname)

def set_test_fpath_root(name='noconfigs'):
    test_path = os.path.join(here, 'configs', name)
    set_paths(test_path)
set_test_fpath_root()
