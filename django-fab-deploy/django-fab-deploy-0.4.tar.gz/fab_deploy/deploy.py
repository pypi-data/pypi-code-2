#coding: utf-8
from __future__ import with_statement
from fabric.api import *
from fabric.contrib.console import confirm
from fabric.contrib.files import upload_template

from fab_deploy.utils import upload_config_template, delete_pyc, run_as
from fab_deploy.virtualenv import pip_install, pip_update
from fab_deploy.django_commands import compress, migrate, syncdb, test
from fab_deploy.system import prepare_server
from fab_deploy.apache import apache_setup, apache_install, touch
from fab_deploy.nginx import nginx_setup, nginx_install
from fab_deploy.virtualenv import virtualenv_create
from fab_deploy import vcs

def full_deploy():
    """ Prepares server and deploys the project. """
    prepare_server()
    deploy_project()

def deploy_project():
    """ Deploys project on prepared server. """
    virtualenv_create()
    make_clone()

    pip_install('all', restart=False)

    setup_web_server()
    update_django_config()

    syncdb()
    migrate()

def make_clone():
    """ Creates repository clone on remote server. """
    with cd('src'):
        with settings(warn_only=True):
            run('mkdir %s' % env.conf['INSTANCE_NAME'])
            with cd(env.conf['INSTANCE_NAME']):
                vcs.init()
    vcs.push()
    with cd('src'):
        with cd(env.conf['INSTANCE_NAME']):
            vcs.up()
    update_django_config(restart=False)
    vcs.configure()

def update_django_config(restart=True):
    """ Updates :file:`config.py` on server (using :file:`config.server.py`) """
    upload_template('config.server.py', '%s/config.py' % env.conf['SRC_DIR'], env.conf, True)
    if restart:
        touch()

def up(branch=None):
    """ Runs vcs ``up`` or ``checkout`` command on server and reloads
    mod_wsgi process. """
    delete_pyc()
    with cd('src/'+ env.conf['INSTANCE_NAME']):
        vcs.up(branch)
    compress()
    touch()

def setup_web_server():
    """ Sets up a web server (apache + nginx). """
    apache_install()
    nginx_install()

    apache_setup()
    nginx_setup()

def push(*args):
    ''' Run it instead of your VCS push command.

    Arguments:

    * notest - don't run tests
    * syncdb - run syncdb before code reloading
    * migrate - run migrate before code reloading
    * pip_update - run pip_update before code reloading
    * norestart - do not reload source code
    '''
    allowed_args = set(['force', 'notest', 'syncdb', 'migrate', 'pip_update', 'norestart'])
    for arg in args:
        if arg not in allowed_args:
            print 'Invalid argument: %s' % arg
            print 'Valid arguments are: %s' % allowed_args
            return

    vcs.push()
    delete_pyc()
    with cd('src/'+env.conf['INSTANCE_NAME']):
        vcs.up()

    if 'pip_update' in args:
        pip_update(restart=False)
    if 'syncdb' in args:
        syncdb()
    if 'migrate' in args:
        migrate()
    compress()
    if 'norestart' not in args:
        touch()
    if 'notest' not in args:
        test()

def undeploy():
    """ Shuts site down. This command doesn't clean everything, e.g.
    user data (database, backups) is preserved. """

    if not confirm("Do you wish to undeploy host %s?" % env.hosts[0], default=False):
        abort("Aborting.")

    @run_as('root')
    def wipe_web():
        run('rm -f /etc/nginx/sites-enabled/'+env.conf['INSTANCE_NAME'])
        run('a2dissite ' + env.conf['INSTANCE_NAME'])
        run('invoke-rc.d nginx reload')
        run('invoke-rc.d apache2 reload')

    wipe_web()
    run('rm -rf %s' % env.conf['SRC_DIR'])
    for folder in ['bin', 'include', 'lib', 'src']:
        run('rm -rf %s' % env.conf['ENV_DIR'] + '/' + folder)
