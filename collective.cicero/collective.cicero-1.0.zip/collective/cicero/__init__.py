import os
import pkg_resources
from zope.component import getUtility
from plone.registry.interfaces import IRegistry
from collective.cicero.config import SERVICES
from collective.cicero.interfaces import ICiceroSettings
from z3c.suds import get_suds_client


def get_settings():
    registry = getUtility(IRegistry)
    return registry.forInterface(ICiceroSettings)

def is_test_mode():
    return 'CICERO_TEST' in os.environ

def get_client(service_name):
    if is_test_mode():
        wsdl = 'file://%s' % pkg_resources.resource_filename('collective.cicero', 'tests/%s.wsdl' % service_name)
    else:
        wsdl = SERVICES[service_name]
    return get_suds_client(wsdl)

def get_auth_token():
    if is_test_mode():
        token = 'FOO'
    else:
        client = get_client('AuthenticationService')
        settings = get_settings()
        if not settings.userName or not settings.password:
            raise ValueError('You must configure your Cicero credentials.')
        token = client.service.GetToken(settings.userName, settings.password)
    return token

def call_cicero(service_name, method_name, *args, **kw):
    client = get_client(service_name)
    method = getattr(client.service, method_name)
    if is_test_mode():
        reply = pkg_resources.resource_string('collective.cicero', 'tests/%s_%s.txt' % (service_name, method_name))
        kw['__inject'] = {'reply': reply}
    token = get_auth_token()
    return method(token, *args, **kw)

__all__ = ('call_cicero', 'get_settings')
