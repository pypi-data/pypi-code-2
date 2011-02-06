from fabric.api import run, env, settings
from fabric.contrib.files import append

from fab_deploy.utils import run_as, upload_config_template
from fab_deploy.system import aptitude_install

def touch(wsgi_file=None):
    """ Reloads source code by touching the wsgi file """
    if wsgi_file is None:
        wsgi_file = env.conf['ENV_DIR']+'/var/wsgi/'+env.conf['INSTANCE_NAME']+'.py'
    run('touch ' + wsgi_file)

def apache_make_wsgi():
    wsgi_dir = env.conf['ENV_DIR']+'/var/wsgi/'
    run('mkdir -p ' + wsgi_dir)
    file_name = env.conf['INSTANCE_NAME']+'.py'
    upload_config_template('django_wsgi.py', wsgi_dir+file_name)

@run_as('root')
def apache_restart():
    run('/etc/init.d/apache2 stop')
    run('/etc/init.d/apache2 start')

# ==== installation ===

@run_as('root')
def apache_install():
    aptitude_install('apache2 libapache2-mod-wsgi libapache2-mod-rpaf')
    run('rm -f /etc/apache2/sites-enabled/default')
    run('rm -f /etc/apache2/sites-enabled/000-default')
    run("echo '' > /etc/apache2/ports.conf")
    apache_setup_locale()

@run_as('root')
def apache_make_config():
    name = env.conf['INSTANCE_NAME']
    upload_config_template('apache.config', '/etc/apache2/sites-available/%s' % name)
    run('a2ensite %s' % name)

def apache_setup():
    apache_make_config()
    apache_make_wsgi()
    apache_restart()

@run_as('root')
def apache_setup_locale():
    append('/etc/apache2/envvars', ['export LANG="en_US.UTF-8"', 'export LC_ALL="en_US.UTF-8"'])

