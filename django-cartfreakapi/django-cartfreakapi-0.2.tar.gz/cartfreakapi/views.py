import hashlib
from django.conf import settings
from django.http import HttpResponse
from django.core.exceptions import ImproperlyConfigured
from cartfreakapi import CartFreakError


REQUIRED_VARS = ('command', 'hash')
VALID_COMMANDS = ('CREATE', 'REMOVE', 'RENEW', 'COMPLETE', 'DECLINE')
ERROR_STR = 'ERROR %s'


def handle_api(request, callback=None, key_name='CARTFREAKAPI_KEY'):
    if not hasattr(settings, key_name):
        raise ImproperlyConfigured(
            u'No CartFreak API setting configured for %s' % key_name
        )

    if request.method != 'POST':
        return HttpResponse(ERROR_STR % 'request must be sent as POST')
    
    cf_key = getattr(settings, key_name)
    for req in REQUIRED_VARS:
        if req not in request.POST:
            err_msg = 'No %s varaible was sent' % req
            return HttpResponse(ERROR_STR % err_msg)
    
    in_hash = request.POST.get('hash')
    command = request.POST.get('command')
    _hash = hashlib.sha1(cf_key + command).hexdigest()

    if command not in VALID_COMMANDS:
        return HttpResponse(ERROR_STR % 'Invalid command sent')

    if _hash != in_hash:
        return HttpResponse(ERROR_STR % 'Invalid hash sent')
    
    if callback is not None and callable(callback):
        try:
            callback(request.POST.copy())
        except CartFreakError, err:
            return HttpResponse(ERROR_STR % str(err))

    return HttpResponse('OK')
