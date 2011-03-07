from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.utils.importlib import import_module


def get_backend():
    """ Returns crawler backend """
    backend_mod_name = settings.CRAWLER_BACKEND
    try:
        backend = import_module(backend_mod_name)
    except ImportError, e:
        raise ImproperlyConfigured(('Error importing crawler backend module %s: "%s"'
                                    % (backend_mod_name, e)))
    return backend
