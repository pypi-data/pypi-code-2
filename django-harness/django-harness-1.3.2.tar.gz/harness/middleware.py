# -*- coding: utf-8 -*-
import threading
_thread_locals = threading.local()

def _get_real_ip(request):
    fwd_ips = request.META.get('HTTP_X_FORWARDED_FOR')
    if fwd_ips:
        return fwd_ips.split(",")[0].strip()
    return request.META['REMOTE_ADDR']

def get_current_ip():
    "Returns current IP address."
    return getattr(_thread_locals, 'ip', None)

def get_current_user():
    "Returns current user (authenticated or anonymous)."
    return getattr(_thread_locals, 'user', None)

class ThreadIPMiddleware(object):
    def process_request(self, request):
        _thread_locals.ip = _get_real_ip(request)
        return None

class ThreadUserMiddleware(object):
    def process_request(self, request):
        _thread_locals.user = getattr(request, 'user', None)
        return None
