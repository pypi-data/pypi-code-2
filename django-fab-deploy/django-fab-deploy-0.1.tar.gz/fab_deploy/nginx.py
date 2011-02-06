from fabric.api import run, env, settings
from fab_deploy.utils import run_as, upload_config_template
from fab_deploy.system import aptitude_install

@run_as('root')
def nginx_install():
    aptitude_install('nginx', 'lenny-backports')
    run('rm -f /etc/nginx/sites-enabled/default')

@run_as('root')
def nginx_setup():
    name = env.conf['INSTANCE_NAME']
    upload_config_template('nginx.config', '/etc/nginx/sites-available/%s' % name)
    with settings(warn_only=True):
        run('ln -s /etc/nginx/sites-available/%s /etc/nginx/sites-enabled/%s' % (name, name))
    run('/etc/init.d/nginx restart')
