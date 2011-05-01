import sys
import time
import traceback
import cStringIO
import datetime
from django.contrib.contenttypes.models import ContentType

from models import *

import dse
dse.patch_models()

def singleton(cls, context_text):
    instances = {}

    def getinstance():
        if cls not in instances:
            instances[cls] = cls(context_text)
        return instances[cls]
    return getinstance


class DelayedLoggingContext(object):

    def __init__(self, context_text):
        self.context_text = context_text
        self.items = []

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.flush()

    def flush(self):
        with LogEntry.dse as d:
            for item in self.items:
                d.add(item)

    def log(self, loglevel, text, user=None, instance=None):
        item = dict(loglevel=loglevel, text=text, date_added=datetime.datetime.today(), user=user)
        if instance:
            item['content_type_id'] = ContentType.objects.get_for_model(instance.__class__).pk
            item['object_id'] = instance.pk

        if len(self.items) > 1000:            
            self.flush()

        self.items.append(item)

    def debug(self, text, user=None, instance=None):
        self.log('debug', text, user=user, instance=instance)

    def info(self, text, user=None, instance=None):
        self.log('info', text, user=user, instance=instance)

    def warning(self, text, user=None, instance=None):
        self.log('warning', text, user=user, instance=instance)

    def critical(self, text, user=None, instance=None):
        self.log('critical', text, user=user, instance=instance)

    def error(self, text, user=None, instance=None):
        self.log('error', text, user=user, instance=instance)

    def exception(self, text, user=None, instance=None):
        try:
            exception_data = exc_plus() 
        except:
            exception_data = ''
        self.log('exception', '%s\n\n%s' % (text, exception_data), user=user, instance=instance)


def get_context(context_text):
    return DelayedLoggingContext(context_text)


def get_singleton_context(context_text):
    if not hasattr(DelayedLoggingContext, 'singleton'):
        setattr(DelayedLoggingContext, 'singleton', singleton(DelayedLoggingContext, context_text)())
    return DelayedLoggingContext.singleton


def exc_plus():
    "Based on the recipie in Python Cookbook, #14.4"
    tb = sys.exc_info()[2]
    while 1:
        if not tb.tb_next:
            break
        tb = tb.tb_next
    stack = []
    f = tb.tb_frame
    while f:
        stack.append(f)
        f = f.f_back
    stack.reverse()
    traceback.print_exc()
    result = []
    for frame in stack:
        result.append('Frame %s in %s at line %s' % (
            frame.f_code.co_name,
            frame.f_code.co_filename,
            frame.f_lineno)
                      )
        for key, value in frame.f_locals.items():
            try:
                result.append('%s = %s' % (key, value))
            except:
                pass
    return '\n'.join(result)
