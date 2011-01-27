from datetime import datetime
from fabric.api import run, env
from fab_deploy.utils import run_as, inside_project

@run_as('root')
def restart_apache():
    run('/etc/init.d/apache2 restart')

@inside_project
def touch():
    """ Reloads source code by touching the wsgi file """
    run('touch hosting/generated/django.wsgi')

@inside_project
def pip_install(what='active', options=''):
    """ Installs pip requirements listed in reqs/<file>.txt file. """
    run('pip install %s -r reqs/%s.txt' % (options, what))
    touch()

@inside_project
def pip_update(what='active', options='', restart=True):
    """ Updates pip requirements listed in reqs/<file>.txt file. """
    run('pip install %s -U -r reqs/%s.txt' % (options, what))
    if restart:
        touch()

@inside_project
def mysqldump(dir='hosting/backups'):
    now = datetime.now().strftime("%Y.%m.%d-%H.%M")
    db = env.conf['DB_NAME']
    password = env.conf['DB_PASSWORD']
    run('mysqldump -uroot -p%s %s > %s/%s%s.sql' % (password, db, dir, db, now))

@inside_project
def delete_pyc():
    """ Deletes *.pyc files from project source dir """
    run("find . -name '*.pyc' -delete")
