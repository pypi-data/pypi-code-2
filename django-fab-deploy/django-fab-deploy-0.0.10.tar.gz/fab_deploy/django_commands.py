#coding: utf-8
from __future__ import with_statement
from fabric.api import env, cd, local, run, settings
from fab_deploy.commands import mysqldump
from fab_deploy.utils import inside_virtualenv

@inside_virtualenv
def manage(command, on_server=True):
    if on_server:
        with cd(env.conf['SRC_DIR']):
            run('python ./manage.py '+ command)
    else:
        local('./manage.py ' + command)

def migrate(params='', do_backup=True):
    if do_backup:
        mysqldump('hosting/backups/before-migrate')
    manage('migrate --noinput %s' % params)

def syncdb(params=''):
    manage('syncdb --noinput %s' % params)

def compress(params=''):
    with settings(warn_only=True):
        manage('synccompress %s' % params)

@inside_virtualenv
def test(what=''):
    with settings(warn_only=True):
        with cd(env.conf['SRC_DIR']):
            run('./runtests.sh ' + what)

def coverage():
    pass
#    with cd(env.conf['SRC_DIR']):
#        run('source %s/bin/activate; ./bin/runcoverage.sh' % env.conf['ENV_DIR'])

