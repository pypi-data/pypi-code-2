from datetime import datetime

from django import template
from django.utils.timesince import timesince as timesince_


register = template.Library()


def timesince(dt, arg=None):
    if not dt:
        return ''
    if arg:
        reference_dt = arg
    else:
        reference_dt = datetime.now()
    if dt > reference_dt:
        return "in %s" % timesince_(reference_dt, dt)
    else:
        return "%s ago" % timesince_(dt, reference_dt)

register.filter('timesince', timesince)
