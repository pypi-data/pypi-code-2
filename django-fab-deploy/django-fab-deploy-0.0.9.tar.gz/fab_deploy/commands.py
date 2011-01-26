#coding: utf-8
from datetime import datetime
from fabric.api import run, env, local, cd
from fab_deploy.utils import run_as

@run_as('root')
def restart_apache():
    run('/etc/init.d/apache2 restart')

def touch():
    """ Reloads source code by touching the wsgi file """
    run('touch %s/hosting/generated/django.wsgi' % env.conf['SRC_DIR'])

def pip_install(what='active', options=''):
    """ Installs pip requirements listed in reqs/<file>.txt file. """
    run('pip install %s -E %s -r %s/reqs/%s.txt' % (options, env.conf['ENV_DIR'], env.conf['SRC_DIR'], what))
    touch()

def pip_update(what='active', options='', restart=True):
    """ Updates pip requirements listed in reqs/<file>.txt file. """
    run('pip install %s -U -E %s -r %s/reqs/%s.txt' % (options, env.conf['ENV_DIR'], env.conf['SRC_DIR'], what))
    if restart:
        touch()

def mysqldump(dir='hosting/backups'):
    now = datetime.now().strftime("%Y.%m.%d-%H.%M")
    db = env.conf['DB_NAME']
    password = env.conf['DB_PASSWORD']
    with cd(env.conf['SRC_DIR']):
        run('mysqldump -uroot -p%s %s > %s/%s%s.sql' % (password, db, dir, db, now))

def delete_pyc():
    """ Deletes *.pyc files from project source dir """
    with cd(env.conf['SRC_DIR']):
        run("find . -name '*.pyc' -delete")
