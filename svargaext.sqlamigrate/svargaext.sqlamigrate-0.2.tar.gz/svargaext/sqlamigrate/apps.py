from os import path as op

from amalgam.backends.sqla.base import Base
from svarga import env
from svarga.utils.imports import import_module

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

    # Try to import module with models
    try:
        module = import_module(name + '.models')
    except ImportError:
        return None

    # Find at least one model which belongs to this module
    model = None

    for n in dir(module):
        obj = getattr(module, n)
        try:
            if obj.__module__ == module.__name__ and issubclass(obj, Base):
                model = obj
                break
        except TypeError:
            pass

    if model is None:
        # TODO: Error logging
        return None

    # Now, try to find base class
    base = None

    for n in dir(module):
        obj = getattr(module, n)
        if model is not obj and isinstance(obj, type) and issubclass(model, obj):
            base = n
            break

    content = files.read_template('migrate.py_tmpl')

    f = file(op.join(path, 'migrate.py'), 'w')
    f.write(content % dict(app_name=name, model_base=base))
    f.close()

    return _load_app(name, config)
