import unittest
import os.path
from fabric.api import *
from fab_deploy import create_linux_account, prepare_server
from fab_deploy.utils import run_as, update_env

from fab_deploy_tests.utils import fab, VirtualBox
from fabric.state import _AttributeDict

path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

class VirtualBoxTest(unittest.TestCase):
    def setUp(self):
        self.box = VirtualBox(env._VM_NAME)
        self.activate_snapshot('initial')

    def tearDown(self):
        self.box.stop()

    def activate_snapshot(self, name):
        self.box.stop()
        self.box.snapshot('restore', name)
        self.box.start()


class FabricTest(VirtualBoxTest):
    host = 'root@127.0.0.1:2222'
    password = '123'
    key_filename = None

    def setUp(self):
        super(FabricTest, self).setUp()
        self._default_env = _AttributeDict(env)
        self.setup_env()

    def tearDown(self):
        env.update(self._default_env)
        super(FabricTest, self).tearDown()

    def setup_env(self):
        env.hosts = [self.host]
        env.password = self.password
        env.key_filename = self.key_filename
        env.disable_known_hosts = True

    def assertUserIs(self, user):
        # use it inside fab commands
        assert run('whoami') == user

class FabDeployTest(FabricTest):
    host = 'foo@127.0.0.1:2222'
    key_filename = [os.path.join(path, "keys/id_rsa")]

    def setup_env(self):
        super(FabDeployTest, self).setup_env()
        self.setup_conf()
        update_env()

    def setup_conf(self):
        env.conf = getattr(env, 'conf', {})
        env.conf['OS'] = env._OS

    def create_linux_account(self):
        fab(create_linux_account, os.path.join(path, "keys/id_rsa.pub"))

    def get_package_state(self, name):
        """ Returns package state as in aptitude output: i, v, etc. """
        state = {}
        @run_as('root')
        def command():
            regexp = "^%s$" % name
            output = run('aptitude -q -F "%%c" search %s' % regexp)
            state[name] = output.splitlines()[-1]
        fab(command)
        return state[name]

    def assertPackageInstalled(self, name):
        state = self.get_package_state(name)
        self.assertEqual(state, 'i')

    def assertPackageNotInstalled(self, name):
        state = self.get_package_state(name)
        self.assertNotEqual(state, 'i')

class BasicTest(FabDeployTest):
    def test_run_as(self):
        @run_as('root')
        def command():
            self.assertUserIs('root')
        fab(command)

class SystemTest(FabDeployTest):

    def test_create_linux_account(self):
        self.create_linux_account()
        def command():
            self.assertUserIs('foo')
        fab(command)

    def test_prepare_server_ok(self):
        fab(prepare_server)
        self.assertPackageInstalled('memcached')
        self.assertPackageInstalled('python')

