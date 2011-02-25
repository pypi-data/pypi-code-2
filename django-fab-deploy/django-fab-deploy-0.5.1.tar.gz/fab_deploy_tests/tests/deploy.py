from __future__ import absolute_import
import os
from fab_deploy.utils import run_as
from fabric.api import *
from fabtest import fab, vbox_urlopen
from fab_deploy.deploy import deploy_project
from fab_deploy.mysql import mysql_create_db
from fab_deploy.apache import apache_make_config, apache_make_wsgi, apache_restart, apache_install
from .base import FabDeployTest
from ..test_project.fabfile import foo_site, bar_site

def get_file_content(remote_file):
    @run_as('root')
    def cat():
        with(hide('stdout')):
            return run('cat '+remote_file)
    return fab(cat)[0]

def get_ports():
    @run_as('root')
    def ports():
        return run('netstat -A inet -lnp')
    return fab(ports)[0]

def is_local_port_binded(port):
    port_string = '127.0.0.1:%s' % port
    ports = get_ports()
    return port_string in ports

class FabDeployProjectTest(FabDeployTest):
    snapshot = 'fabtest-prepared-server'

    def setup_conf(self):
        self.cwd = os.getcwd()
        os.chdir('test_project')
        fab(foo_site)

    def tearDown(self):
        os.chdir(self.cwd)
        super(FabDeployProjectTest, self).tearDown()


class ApacheSetupTest(FabDeployProjectTest):

    def assertPortBinded(self, port):
        self.assertTrue(is_local_port_binded(port))

    def assertPortNotBinded(self, port):
        self.assertFalse(is_local_port_binded(port))

    def test_apache_config(self):
        fab(apache_install)

        # first site
        fab(foo_site)
        fab(apache_make_config)

        foo_port = env.conf.APACHE_PORT
        self.assertPortNotBinded(foo_port)
        self.assertTrue(get_file_content('/etc/apache2/sites-enabled/foo'))

        fab(apache_restart)
        self.assertPortBinded(foo_port)

        # second site
        fab(bar_site)
        fab(apache_make_config)

        bar_port = env.conf.APACHE_PORT
        self.assertNotEqual(foo_port, bar_port)
        self.assertPortNotBinded(bar_port)

        fab(apache_restart)
        self.assertPortBinded(bar_port)

        # re-configuring doesn't lead to errors
        fab(apache_make_config)
        fab(apache_restart)
        self.assertPortBinded(bar_port)

    def test_apache_make_wsgi(self):
        fab(apache_make_wsgi)
        wsgi_file = get_file_content(env.conf.ENV_DIR+'/var/wsgi/foo.py')
        self.assertTrue(wsgi_file)


class DeployTest(FabDeployProjectTest):

    def assertResponse(self, url, data):
        self.assertEqual(vbox_urlopen(url).read(), data)

    def test_deploy(self):
        # deploy first site
        fab(foo_site)
        fab(mysql_create_db)
        fab(deploy_project)

        # first site works
        self.assertResponse('http://foo.example.com/instance/', 'foo')

        # deploy second site
        fab(bar_site)
        fab(mysql_create_db)
        fab(deploy_project)

        # second site works
        self.assertResponse('http://bar.example.com/instance/', 'bar')
        # first site is still available
        self.assertResponse('http://foo.example.com/instance/', 'foo')
