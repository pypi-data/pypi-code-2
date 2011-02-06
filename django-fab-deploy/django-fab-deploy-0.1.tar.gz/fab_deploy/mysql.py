from datetime import datetime
from fabric.api import *
from fab_deploy.utils import run_as, inside_project
from fab_deploy.system import aptitude_install

@run_as('root')
def mysql_install():
    if _mysql_is_installed():
        puts('Mysql is already installed.')
        return

    # this way mysql won't ask for a password on installation
    # see http://serverfault.com/questions/19367/scripted-install-of-mysql-on-ubuntu
    aptitude_install('debconf-utils')
    passwd=env.conf['DB_PASSWORD']
    defaults = """mysql-server-5.0\tmysql-server/root_password_again\tpassword\t%s
mysql-server-5.0\tmysql-server/root_password\tpassword\t%s""" % (passwd, passwd,)
    run("echo '%s' | debconf-set-selections" % defaults)
    warn('\n=========\nThe password for mysql "root" user will be set to "%s"\n=========\n' % passwd)

    aptitude_install('mysql-server')

def _mysql_is_installed():
    with settings(warn_only=True):
        output = run('mysql --version')
    return output.succeeded

@inside_project
def mysqldump(dir=None):
    if dir is None:
        dir = env.conf['ENV_DIR'] + '/var/backups'
        run('mkdir -p ' + dir)
    now = datetime.now().strftime("%Y.%m.%d-%H.%M")
    db = env.conf['DB_NAME']
    password = env.conf['DB_PASSWORD']
    run('mysqldump -uroot -p%s %s > %s/%s%s.sql' % (password, db, dir, db, now))

def mysql_execute(sql, user=None, password=None):
    user = user or env.conf['DB_USER']
    password = env.conf['DB_PASSWORD'] if password is None else password
    run ("echo '%s' | mysql -u%s -p%s" % (sql, user , password))

def mysql_create_db():
    db_name = env.conf['DB_NAME']
    if env.conf['DB_USER'] != 'root':
        password = prompt('Please enter mysql root password:')
    else:
        password = env.conf['DB_PASSWORD']
    params = 'DEFAULT CHARACTER SET utf8 DEFAULT COLLATE utf8_general_ci'
    mysql_execute('CREATE DATABASE %s %s;' % (db_name, params), 'root', password)
