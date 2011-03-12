from fab_deploy import *

LAYOUT_OPTIONS = dict(
    PROJECT_PATH = 'src',
    LOCAL_CONFIG = 'local_settings.py',
    REMOTE_CONFIG_TEMPLATE = 'staging_settings.py',
    PIP_REQUIREMENTS_PATH = '',
    PIP_REQUIREMENTS = 'requirements.txt',
    PIP_REQUIREMENTS_ACTIVE = 'requirements.txt',
    CONFIG_TEMPLATES_PATHS = ['hosting/staging', 'hosting'],
)

def foo_site():
    env.hosts = ['foo@127.0.0.1:2222']
    env.conf = dict(
        DB_PASSWORD = '123',
        VCS = 'git',
        SERVER_NAME = 'foo.example.com',
    )
    env.conf.update(LAYOUT_OPTIONS)
    update_env()
