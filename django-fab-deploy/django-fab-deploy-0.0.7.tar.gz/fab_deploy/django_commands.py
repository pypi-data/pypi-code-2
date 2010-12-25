#coding: utf-8
from __future__ import with_statement
from fabric.api import env, cd, local, run, settings
from fab_deploy.commands import mysqldump

def manage(command, on_server=True):
    if on_server:
        with cd(env.conf['SRC_DIR']):
            run ('%s/bin/python ./manage.py %s' % (env.conf['ENV_DIR'], command))
    else:
        local('./manage.py %s' % command)

def migrate(params='', do_backup=True):
    if do_backup:
        mysqldump('hosting/backups/before-migrate')
    manage('migrate --noinput %s' % params)

def syncdb(params=''):
    manage('syncdb --noinput %s' % params)

def compress(params=''):
    with settings(warn_only=True):
        manage('synccompress %s' % params)

def test(what=''):
    with settings(warn_only=True):
        with cd(env.conf['SRC_DIR']):
            run('source %s/bin/activate; ./runtests.sh %s' % (env.conf['ENV_DIR'], what))

def coverage():
    pass
#    with cd(env.conf['SRC_DIR']):
#        run('source %s/bin/activate; ./bin/runcoverage.sh' % env.conf['ENV_DIR'])

