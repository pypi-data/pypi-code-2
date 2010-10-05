# -*- coding: utf-8 -*-
import sys
import datetime
import traceback

import pysi


WEEKDAYS = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
MONTHS = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 
    'Sep', 'Oct', 'Nov', 'Dec']

def obj_from_str(str_or_obj):
    '''
    Если передана строка, пытается проимпортировать модуль и вернуть объект.
    '''
    if isinstance(str_or_obj, basestring):
        mod_name, obj_name = str_or_obj.rsplit('.', 1)
        try:
            __import__(mod_name)
        except ImportError:
            return None
        mod = sys.modules[mod_name]
        return getattr(mod, obj_name, None)
    else:
        return str_or_obj

def list_obj_from_str(lst):
    for i in xrange(len(lst)):
        obj = obj_from_str(lst[i])
        if not obj:
            assert 0, 'object not found: %s' % item
        lst[i] = obj

class cache_property(object):
    def __init__(self, f):
        self.f = f

    def __get__(self, instance, owner):
        value = self.f(instance)
        setattr(instance, self.f.__name__, value)
        return value

def make_traceback(host):
    head = '%s | %s' % (host, datetime.datetime.now())
    line = '-' * len(head)
    return '\n%s\n%s\n%s\n%s' % (line, head, line,
        ''.join(traceback.format_exception(*sys.exc_info())[1:]))
            
def anticache_headers():
    expires = http_date(datetime.datetime.utcnow())
    return {
        'Expires' : expires,
        'Last-Modified' : expires,
        'Pragma' : 'no-cache',
        'Cache-Control' : 'private, no-cache, no-store, must-revalidate, max-age=0, pre-check=0, post-check=0',
    }

def http_date(dt):
    '''
    Дата обновления документа в http формате
    '''
    week = WEEKDAYS[dt.weekday()]
    month = MONTHS[dt.month - 1]
    return "%s, %02d %s %04d %02d:%02d:%02d GMT" % (week, dt.day, month,
        dt.year, dt.hour, dt.minute, dt.second)