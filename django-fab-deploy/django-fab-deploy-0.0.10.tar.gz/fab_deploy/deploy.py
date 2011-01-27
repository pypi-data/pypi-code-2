#coding: utf-8
from __future__ import with_statement
from fabric.api import env, run, local, settings, cd
from fabric.contrib.files import upload_template

from fab_deploy.utils import run_as, upload_hosting_template
from fab_deploy.commands import touch, pip_install, pip_update, delete_pyc
from fab_deploy.django_commands import compress, migrate, syncdb, test
from fab_deploy.system import install_system_packages, setup_backports, setup_locale, install_vcs

def full_deploy():
    install_system_packages()
    setup_backports()
    install_vcs()

    make_virtualenv()
    make_clone()
    make_hgrc()
    make_wsgi()

    pip_install('all')

    setup_web_server()
    update_config()


def make_virtualenv():
    run('mkdir -p %s' % env.conf['ENV_BASE'])
    run('mkdir -p %s' % env.conf['SRC_BASE'])
    with cd(env.conf['ENV_BASE']):
        run('virtualenv --no-site-packages %s' % env.conf['INSTANCE_NAME'])


def push(*args):
    ''' Run it instead of hg push.
    Arguments:
      * force - run all actions even if nothing changes
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

    repo = 'ssh://%s@%s/%s/%s/' % (env.conf['USER'], env.conf['HOST'], env.conf['SRC_BASE'], env.conf['INSTANCE_NAME'])
    local('hg push %s' % repo)
    delete_pyc()
    with cd(env.conf['SRC_BASE']):
        with cd(env.conf['INSTANCE_NAME']):
            output = run('hg up')
            updated = '0 files updated, 0 files merged, 0 files removed, 0 files unresolved' not in output
    if updated or 'force' in args:
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


def update_config(only_upload=False):
    upload_template('config.server.py', '%s/config.py' % env.conf['SRC_DIR'], env.conf, True)
    if not only_upload:
        touch()


def up(branch=None):
    delete_pyc()
    branch = branch or env.conf['HG_BRANCH']
    with cd(env.conf['SRC_BASE']):
        with cd(env.conf['INSTANCE_NAME']):
            run('hg up -C %s' % branch)
    compress()
    touch()


def make_clone():
    with cd(env.conf['SRC_BASE']):
        with settings(warn_only=True):
            run('mkdir %s' % env.conf['INSTANCE_NAME'])
            with cd(env.conf['INSTANCE_NAME']):
                run('hg init')
    local('hg push ssh://%s@%s/%s/%s/' % (env.conf['USER'], env.conf['HOST'], env.conf['SRC_BASE'], env.conf['INSTANCE_NAME']))
    with cd(env.conf['SRC_BASE']):
        with cd(env.conf['INSTANCE_NAME']):
            run('hg up -C %s' % env.conf['HG_BRANCH'])
    update_config(only_upload=True)


def make_hgrc():
    upload_hosting_template('hgrc', '%s/.hg/hgrc' % env.conf['SRC_DIR'])

def make_wsgi():
    upload_hosting_template('django.wsgi', '%s/hosting/generated/django.wsgi' % env.conf['SRC_DIR'])


@run_as('root')
def setup_web_server():
    name = env.conf['INSTANCE_NAME']

    upload_hosting_template('apache.config', '/etc/apache2/sites-available/%s' % name)
    upload_hosting_template('nginx.config', '/etc/nginx/sites-available/%s' % name)

    with settings(warn_only=True):
        run('ln -s /etc/nginx/sites-available/%s /etc/nginx/sites-enabled/%s' % (name, name))
        run('rm /etc/nginx/sites-enabled/default')
        run('rm /etc/apache2/sites-enabled/default')
    run('a2ensite %s' % name)
    setup_locale()
    run('/etc/init.d/nginx restart')
