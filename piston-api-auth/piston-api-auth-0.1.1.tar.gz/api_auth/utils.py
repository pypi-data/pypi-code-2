from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.contrib.contenttypes.models import ContentType

class KeyNotFound(Exception): pass
class _RequiredConfig(object): pass
class Override(object):
    data = None
    def __call__(self, data):
        self.data = data


config_map = {
    'app': ('API_AUTH_APP', _RequiredConfig),
    'model': ('API_AUTH_MODEL', 'consumer'),
    'fields': ('API_AUTH_FIELDS', {'consumer_key': 'key',
                                   'consumer_secret': 'secret'}),
    'parameters': ('API_AUTH_PARAMETERS', {'timestamp': 'timestamp',
                                           'consumer_key': 'consumer_key',
                                           'signature': 'signature',
                                           'nonce': 'nonce'}),
    'prefix': ('API_AUTH_PREFIX', 'X-APIAuth-'),
    'nonce': ('API_AUTH_NONCE', True),
    'timeout': ('API_AUTH_TIMEOUT', 15),
}

def config(key):
    name, default = config_map[key]
    config_value = getattr(settings, name, default)
    if config_value is _RequiredConfig:
        error_msg = '%s setting is required by api_auth app.' % name
        raise ImproperlyConfigured(error_msg)
    return config_value

def consumer_model():
    """
    Get the model referred by API_AUTH_APP and API_AUTH_MODEL using
    the ContentType framework.
    """
    app_label = config('app')
    model = config('model')
    consumer_type = ContentType.objects.get(app_label=app_label, model=model)
    return consumer_type.model_class()

def header_name(header_name):
    """
    Transforms the header_name parameter into a valid Django
    META key name. All Django META keys start with HTTP_, have
    all '-' replaced by '_' and all letters are uppercase.
    """
    header = config('prefix') + config('parameters')[header_name]
    return 'HTTP_%s' % header.upper().replace('-','_')

def parameter_name(parameter_name):
    """
    Force query parameters to be lowercase.
    """
    parameter = config('parameters')[parameter_name]
    return parameter.lower()

def search_key(meta, get, key):
    """
    Searches trough headers and GET arguments for the specified
    key preferring the headers.
    If the key is not found a KeyNotFound exception is raised.
    """
    key_name = config('parameters')[key]
    header = header_name(key_name)
    if header in meta:
        return meta[header]
    parameter = parameter_name(key_name)
    if parameter in get:
        return get[parameter]
    raise KeyNotFound("%s was not found." % key_name)
