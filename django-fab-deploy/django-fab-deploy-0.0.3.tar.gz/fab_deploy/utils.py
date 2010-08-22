from functools import wraps
from fabric.contrib.files import upload_template
from fabric.api import env

def run_as(user):
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

def upload_hosting_template(name, to):
    upload_template('./hosting/templates/'+name, to, env.conf, True)

def update_env():
    HOME_DIR = '/home/%s' % env.user
    ENV_BASE, SRC_BASE = 'envs', 'src'

    env.conf.update({
       'HOME_DIR': HOME_DIR,
       'ENV_BASE': ENV_BASE,
       'SRC_BASE': SRC_BASE,
       'ENV_DIR': HOME_DIR + '/' + ENV_BASE + '/' + env.conf['INSTANCE_NAME'],
       'SRC_DIR': HOME_DIR + '/' + SRC_BASE + '/' + env.conf['INSTANCE_NAME'],
    })
