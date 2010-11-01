from zine import get_wsgi_app
import os

INSTANCE_FOLDER = 'missing'

POOL_SIZE = None
POOL_RECYCLE = None
POOL_TIMEOUT = None
BEHIND_PROXY = None

def app_factory(global_conf, **kw):
    if kw.has_key('instance_folder'):
        INSTANCE_FOLDER = kw['instance_folder']
    if not os.path.isdir(INSTANCE_FOLDER):
        raise EnvironmentError(
                u'INSTANCE_FOLDER (%s) does not exist. '
                u'Please edit "deploy.ini"' % INSTANCE_FOLDER
              )
    return get_wsgi_app(INSTANCE_FOLDER)
