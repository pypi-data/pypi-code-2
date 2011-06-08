import os
import tempfile
import shutil
from nose.tools import ok_, eq_

class env(object):
    pass

class DummyArgs(dict):
    def __getattr__(self, key):
        return self[key]

def setup():
    env.basedir = tempfile.mkdtemp()

def teardown():
    if hasattr(env, 'basedir'):
        shutil.rmtree(env.basedir)

def test_env():
    assert hasattr(env, 'basedir')

def test_list_empty():
    from aodag.scaffold.commands import cmd_list
    args = DummyArgs(base_dir=env.basedir)
    cmd_list(args)

def test_list_one():
    os.makedirs(os.path.join(env.basedir, 'test_list_one', 'a', 'b', 'c'))
    from aodag.scaffold.commands import cmd_list
    args = DummyArgs(base_dir=env.basedir)
    cmd_list(args)

def test_install():

    from aodag.scaffold.commands import cmd_install
    args = DummyArgs(base_dir=env.basedir, scaffold="test_install.scaffold", 
            scaffold_file=os.path.join(os.getcwd(), "sample", "sample.scaffold.zip"))
    cmd_install(args)
    ok_(os.path.exists(os.path.join(env.basedir, "test_install.scaffold")))

