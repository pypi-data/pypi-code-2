from fabric.api import run, env, cd
from fab_deploy.apache import touch
from fab_deploy.utils import inside_project

@inside_project
def pip(commands=''):
    """ Runs pip command """
    run('pip '+ commands)

@inside_project
def pip_install(what='active', options='', restart=True):
    """ Installs pip requirements listed in ``reqs/<file>.txt`` file. """
    run('pip install %s -r reqs/%s.txt' % (options, what))
    if restart:
        touch()

@inside_project
def pip_update(what='active', options='', restart=True):
    """ Updates pip requirements listed in ``reqs/<file>.txt`` file. """
    run('pip install %s -U -r reqs/%s.txt' % (options, what))
    if restart:
        touch()

def virtualenv_create():
    run('mkdir -p envs')
    run('mkdir -p src')
    with cd('envs'):
        run('virtualenv --no-site-packages %s' % env.conf['INSTANCE_NAME'])
