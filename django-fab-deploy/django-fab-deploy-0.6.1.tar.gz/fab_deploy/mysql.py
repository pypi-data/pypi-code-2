from __future__ import with_statement
from datetime import datetime
from fabric.api import *
from fab_deploy import utils
from fab_deploy import system


__all__ = ['mysql_execute', 'mysql_install', 'mysql_create_db', 'mysqldump']


@utils.run_as('root')
def mysql_install():
    """ Installs mysql. """
    if _mysql_is_installed():
        puts('Mysql is already installed.')
        return

    # this way mysql won't ask for a password on installation
    # see http://serverfault.com/questions/19367/scripted-install-of-mysql-on-ubuntu
    os = utils.detect_os()
    system.aptitude_install('debconf-utils')
    passwd=env.conf['DB_PASSWORD']

    mysql_versions = {'lenny': '5.0', 'squeeze': '5.1', 'maverick': '5.1'}
    version = mysql_versions[os]

    debconf_defaults = [
        "mysql-server-%s mysql-server/root_password_again password %s" % (version, passwd),
        "mysql-server-%s mysql-server/root_password password %s" % (version, passwd),
    ]

    run("echo '%s' | debconf-set-selections" % "\n".join(debconf_defaults))

    warn('\n=========\nThe password for mysql "root" user will be set to "%s"\n=========\n' % passwd)
    system.aptitude_install('mysql-server')

def _mysql_is_installed():
    with settings(warn_only=True):
        output = run('mysql --version')
    return output.succeeded

@utils.inside_project
def mysqldump(dir=None):
    """ Runs mysqldump. Result is stored at <env>/var/backups/ """
    if dir is None:
        dir = env.conf['ENV_DIR'] + '/var/backups'
        run('mkdir -p ' + dir)
    now = datetime.now().strftime("%Y.%m.%d-%H.%M")
    db = env.conf['DB_NAME']
    password = env.conf['DB_PASSWORD']
    run('mysqldump -uroot -p%s %s > %s/%s%s.sql' % (password, db, dir, db, now))

def mysql_execute(sql, user=None, password=None):
    """ Executes passed sql command using mysql shell. """
    user = user or env.conf['DB_USER']
    password = env.conf['DB_PASSWORD'] if password is None else password
    return run("echo '%s' | mysql -u%s -p%s" % (sql, user , password))

def mysql_create_db():
    """ Creates an empty mysql database. """
    db_name = env.conf['DB_NAME']
    if env.conf['DB_USER'] != 'root':
        password = prompt('Please enter mysql root password:')
    else:
        password = env.conf['DB_PASSWORD']
    params = 'DEFAULT CHARACTER SET utf8 DEFAULT COLLATE utf8_general_ci'
    mysql_execute('CREATE DATABASE %s %s;' % (db_name, params), 'root', password)
