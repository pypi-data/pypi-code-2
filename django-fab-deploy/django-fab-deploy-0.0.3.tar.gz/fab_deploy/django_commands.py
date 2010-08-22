#coding: utf-8
from __future__ import with_statement
from fabric.api import env, cd, local, run
from fab_deploy.commands import mysqldump

def manage(command, on_server=True):
    if on_server:
        with cd(env.conf['SRC_DIR']):
            run ('%s/bin/python ./manage.py %s' % (env.conf['ENV_DIR'], command))
    else:
        local('./manage.py %s' % command)

def migrate(params='', do_backup=True):
    if do_backup:
        mysqldump('before-migrate/')
    manage('migrate --noinput %s' % params)

def syncdb():
    manage('syncdb --noinput')

def compress():
    manage('synccompress')

def test():
    pass
#    with cd(env.conf['SRC_DIR']):
#        run('source %s/bin/activate; ./bin/runtests.sh' % env.conf['ENV_DIR'])

def coverage():
    pass
#    with cd(env.conf['SRC_DIR']):
#        run('source %s/bin/activate; ./bin/runcoverage.sh' % env.conf['ENV_DIR'])

