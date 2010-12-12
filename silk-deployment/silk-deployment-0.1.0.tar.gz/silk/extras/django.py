from silk.fabfile import push as real_push
from silk.utils import run_til_you_die as _run_til_you_die
from signal import SIGINT
import silk
import os
#SIGH

#time to rewrite code that I wrote last night but is trapped on my laptop because I didn't do an hg addremove
#SIGH
#I think the only new file was django.py.
#which includes collectstatic, and an overwritten push

def _get_proj_dir(root):
    """Ugly magic function to loop through subdirectories and return the first
    one that looks like a Django project (has a settings.py)"""
    #get list of current folder contents
    paths = [os.path.join(root, folder) for folder in os.listdir(root) if os.path.isdir(os.path.join(os.path.join(root, folder)))]
    for path in paths:
        if os.path.isfile(os.path.join(path, 'settings.py')):
            return path

def collectstatic():
    """Runs ./manage.py collectstatic, setting current Silk role 
    as env var so it can be picked up in local_settings"""
    args = ['./manage.py', 'collectstatic', '--settings=local_settings']
    proj_dir = _get_proj_dir(silk.lib.get_site_root(os.getcwd()))
    env_vars = {'SILK_ROLE': silk.lib.get_role()}
    _run_til_you_die(args, SIGINT, proj_dir, env=env_vars)

def push():
    collectstatic()
    real_push()
