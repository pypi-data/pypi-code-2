#coding: utf-8
import iso8601
import pytz
from django.conf import settings
from django.db import models
from django import forms

def iso8601_to_local_datetime(value):
    default_tz = pytz.timezone(settings.TIME_ZONE)
    return iso8601.parse_date(value).astimezone(default_tz).replace(tzinfo=None)


class ISO8601FormField(forms.DateTimeField):
    def to_python(self, value):
        try:
            return iso8601_to_local_datetime(value)
        except iso8601.ParseError:
            return super(ISO8601FormField, self).to_python(value)


class ISO8601Field(models.DateTimeField):
    def to_python(self, value):
        if isinstance(value, basestring):
            return super(ISO8601Field, self).to_python(iso8601_to_local_datetime(value))
        return super(ISO8601Field, self).to_python(value)

    def formfield(self, **kwargs):
        defaults = {'form_class': ISO8601FormField}
        defaults.update(kwargs)
        return super(ISO8601Field, self).formfield(**defaults)

try:
    from south.modelsinspector import add_introspection_rules
    add_introspection_rules([], ['merchant_api.fields.*'])
except ImportError:
    pass
