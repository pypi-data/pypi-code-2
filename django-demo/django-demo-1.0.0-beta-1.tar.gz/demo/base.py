from copy import copy
from demo.exceptions import UnsupportedBackend
from demo import settings
from django.core.management import call_command
from django.db import connections
from django.utils.importlib import import_module

class Backend(object):
    def __init__(self):
        self._module = None
        
    @property
    def module(self):
        if not self._module:
            if settings.BACKEND:
                package, name = settings.BACKEND.rsplit('.', 1)
            else:
                name = 'backend'
                package = 'demo.backends.%s' % connections.databases['default']['ENGINE'].split('.')[-1]
            try:
                self._module = import_module('.%s' % name, package)
            except ImportError:
                raise UnsupportedBackend(connections.databases['default']['ENGINE'])
        return self._module
    
    def __getattr__(self, attr):
        return getattr(self.module, attr)
    
backend = Backend()

def install_database(name):
    config = copy(connections.databases['default'])
    config['NAME'] = name
    connections.databases[name] = config

def create_database(name):
    config = copy(connections.databases['default'])
    config['NAME'] = name
    backend.create(name)
    connections.databases[name] = config
    call_command('syncdb', database=name, interactive=False, verbosity=0)
    if settings.FIXTURES:
        call_command('loaddata', database=name, verbosity=0, *settings.FIXTURES)

def drop_database(name):
    backend.drop(name)
    del connections._connections[name]