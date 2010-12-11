from os import path as op

from svarga import env
from svarga.utils.imports import import_module
from svarga.db.sqla.process import TABLE_PREFIX_ATTRIBUTE

from svargaext.sqlamigrate import files

APP_MIGRATE_NAME = 'migrate'
APP_MIGRATE_DIR = 'migratedb'

class AppSettings(object):
    def __init__(self, app):
        self.app = app
        self.path = app.module.__path__[0]
        self.models = set()

    def add_model(self, model):
        self.models.add(model)

    def get_repository_path(self):
        return op.join(self.path, APP_MIGRATE_DIR)

def _load_app(name, config):
    mod_name = '%s.%s' % (name, APP_MIGRATE_NAME)
    try:
        mod = import_module(mod_name)
    except ImportError:
        # TODO: Check if it was compilation error or file not present
        return None

    init = getattr(mod, 'init', None)

    if init is not None:
        settings = AppSettings(config)
        init(settings)

        return settings

    return None

def get_apps():
    result = dict()

    for app, config in env.apps.iteritems():
        settings = _load_app(app, config)

        if settings:
            result[app] = settings

    return result

def get_app(name):
    config = env.apps.get(name, None)

    if config is None:
        return None

    return _load_app(name, config)

def instrument(name):
    config = env.apps.get(name, None)

    if config is None:
        return None

    path = config.module.__path__[0]
    migrate_path = op.join(path, '%s.py' % APP_MIGRATE_NAME)

    if op.exists(migrate_path):
        return None

    # Try to import list of models
    models_name = '%s.models' % name
    try:
        models = import_module(models_name)
    except ImportError:
        return None

    # Find at least one model which belongs to this module
    model = None

    for v in models.__dict__.itervalues():
        if hasattr(v, TABLE_PREFIX_ATTRIBUTE) and v.__module__ == models_name:
            model = v
            break

    if model is None:
        # TODO: Error logging
        return None

    # Now, try to find base class
    base = None

    for n,v in models.__dict__.iteritems():
        if model is not v and isinstance(v, type) and issubclass(model, v):
            base = n
            break

    content = files.read_template('migrate.py_tmpl')

    f = file(op.join(path, 'migrate.py'), 'w')
    f.write(content % dict(app_name=name, model_base=base))
    f.close()

    return _load_app(name, config)
