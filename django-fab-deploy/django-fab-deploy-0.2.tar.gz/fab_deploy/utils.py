import os
from functools import wraps
from fabric.context_managers import prefix, cd
from fabric.contrib.files import upload_template
from fabric.api import env, run
from fabric.state import _AttributeDict

def run_as(user):
    """
    Decorator. Runs fabric command as specified user. It is most useful to
    run commands that require root access to server::

        from fabric.api import run
        from fab_deploy.utils import run_as

        @run_as('root')
        def aptitude_update():
            run('aptitude update')

    """
    def decorator(func):
        @wraps(func)
        def inner(*args, **kwargs):
            old_user = env.user
            env.user = user
            result = func(*args, **kwargs)
            env.user = old_user
            return result
        return inner
    return decorator

def upload_config_template(name, to=None):
    if to is None:
        base_dir = env.conf['ENV_DIR'] + "/etc/"
        run('mkdir -p ' + base_dir)
        to = base_dir + name
    upload_template('./config_templates/' + name, to, env.conf, True)

def update_env():
    """
    Updates :attr:`env.conf` configuration with some defaults and converts
    it to _AttributeDict (that's a dictionary subclass enabling attribute
    lookup/assignment of keys/values).

    Call :func:`update_env` at the end of each server-configuring function.

    ::

        from fab_deploy import *

        def my_site():
            env.hosts = ['example.com']
            env.user = 'example'
            env.conf = dict(
                DB_PASSWORD = 'password',
            )
            update_env()
    """

    HOME_DIR = '/home/%s' % env.user
    if 'INSTANCE_NAME' not in env.conf:
        env.conf['INSTANCE_NAME'] = env.user

    defaults = _AttributeDict(
        HG_BRANCH = 'default',
        DB_NAME = env.conf['INSTANCE_NAME'],
        DB_USER = 'root',
        PROCESSES = 1,
        THREADS = 15,
        HOME_DIR = HOME_DIR,
        ENV_DIR = HOME_DIR + '/envs/' + env.conf['INSTANCE_NAME'],
        SRC_DIR = HOME_DIR + '/src/' + env.conf['INSTANCE_NAME'],
        USER = env.user,
        HOST = env.hosts[0],
        SERVER_NAME = env.hosts[0],
        SERVER_ADMIN = 'example@example.com',
    )
    defaults.update(env.conf)
    env.conf = defaults

def virtualenv():
    """
    Context manager. Use it for perform actions inside virtualenv::

        with virtualenv():
            # virtualenv is active here

    """
    return prefix('source '+env.conf['ENV_DIR']+'/bin/activate')

def inside_virtualenv(func):
    """
    Decorator. Use it for perform actions inside virtualenv::

        @inside_virtualenv
        def my_command():
            # virtualenv is active here

    """
    @wraps(func)
    def inner(*args, **kwargs):
        with virtualenv():
            return func(*args, **kwargs)
    return inner

def inside_project(func):
    """
    Decorator. Use it to perform actions inside project dir with
    virtualenv activated::

        from fabric.api import *
        from fab_deploy.utils import inside_project

        @inside_project
        def cleanup():
            # the current dir is a project source dir and
            # virtualenv is activated
            run('python manage.py cleanup')

    """
    @wraps(func)
    def inner(*args, **kwargs):
        with cd(env.conf['SRC_DIR']):
            with virtualenv():
                return func(*args, **kwargs)
    return inner

@inside_project
def delete_pyc():
    """ Deletes *.pyc files from project source dir """
    run("find . -name '*.pyc' -delete")

def _data_path(fname):
    """Return the path to a data file of ours."""
    return os.path.join(os.path.split(__file__)[0], fname)
