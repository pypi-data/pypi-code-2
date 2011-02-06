#coding: utf-8
from __future__ import with_statement
from fabric.api import run, settings, env
from fab_deploy.mysql import mysqldump
from fab_deploy.utils import inside_project

@inside_project
def manage(command):
    run('python ./manage.py '+ command)

def migrate(params='', do_backup=True):
    if do_backup:
        backup_dir = env.conf['ENV_DIR']+'/var/backups/before-migrate'
        run('mkdir -p '+ backup_dir)
        mysqldump(backup_dir)
    manage('migrate --noinput %s' % params)

def syncdb(params=''):
    manage('syncdb --noinput %s' % params)

def compress(params=''):
    with settings(warn_only=True):
        manage('synccompress %s' % params)

@inside_project
def test(what=''):
    with settings(warn_only=True):
        run('./runtests.sh ' + what)

def coverage():
    pass
#    with cd(env.conf['SRC_DIR']):
#        run('source %s/bin/activate; ./bin/runcoverage.sh' % env.conf['ENV_DIR'])

