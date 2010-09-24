# -*- coding: utf-8 -*-
import base64
import datetime
from django import forms
from django.conf import settings
from django.db.models.signals import post_save
from django.db.models.fields.related import OneToOneField
from django.db import models
from django.utils.text import compress_string
from django.utils.translation import ugettext_lazy as _
from south.modelsinspector import add_introspection_rules

import cPickle as pickle

def uncompress_string(s):
    """Helper function to reverse django.utils.text.compress_string."""
    import cStringIO, gzip
    try:
        zbuf = cStringIO.StringIO(s)
        zfile = gzip.GzipFile(fileobj=zbuf)
        ret = zfile.read()
        zfile.close()
    except:
        ret = s
    return ret


class IntegerTupleField(models.CharField):
    """
    A field type for holding a tuple of integers. Stores as a string
    with the integers delimited by colons.
    """
    __metaclass__ = models.SubfieldBase

    def formfield(self, **kwargs):
        defaults = {
            'form_class': forms.RegexField,
            # We include the final comma so as to not penalize Python
            # programmers for their inside knowledge
            'regex': r'^\((\s*[+-]?\d+\s*(,\s*[+-]?\d+)*)\s*,?\s*\)$',
            'max_length': self.max_length,
            'error_messages': {
                'invalid': _('Enter 0 or more comma-separated integers '
                    'in parentheses.'),
                'required': _('You must enter at least a pair of '
                    'parentheses containing nothing.'),
            },
        }
        defaults.update(kwargs)
        return super(IntegerTupleField, self).formfield(**defaults)
    
    def to_python(self, value):
        if type(value) == tuple:
            return value
        if type(value) == unicode and value.startswith('(') and \
            value.endswith(')'):
            return eval(value)
        if value == '':
            return ()
        if value is None:
            return None
        return tuple(int(x) for x in value.split(u':'))
        
    def get_db_prep_value(self, value):
        if value is None:
            return None
        return u':'.join(unicode(x) for x in value)
        
    def get_db_prep_lookup(self, lookup_type, value):
        if lookup_type == 'exact':
            return [self.get_db_prep_value(value)]
        else:
            raise TypeError('Lookup type %r not supported' %
                lookup_type)
    
    def value_to_string(self, obj):
        return self.get_db_prep_value(obj)


class CompressedTextField(models.TextField):
    """
    Transparently compress data before hitting the db and uncompress after
    fetching.
    """
    __metaclass__ = models.SubfieldBase

    def get_db_prep_value(self, value):
        if value is not None:
            value = base64.encodestring(compress_string(pickle.dumps(value)))
        return value

    def to_python(self, value):
        if value is None: return
        if isinstance(value, str): return value
        try:
            value = pickle.loads(uncompress_string(base64.decodestring(value)))
        except:
            # if we can't unpickle it it's not pickled. probably we got a
            # normal string. pass
            pass
        return value

    def post_init(self, instance=None, **kwargs):
        value = self._get_val_from_obj(instance)
        if value:
            setattr(instance, self.attname, value)

    def contribute_to_class(self, cls, name):
        super(CompressedTextField, self).contribute_to_class(cls, name)
        models.signals.post_init.connect(self.post_init, sender=cls)

 
    def value_to_string(self, obj):
        value = self._get_val_from_obj(obj)
        return value

    def get_internal_type(self):
        return "TextField"

    def db_type(self):
        db_types = {'mysql':'longblob',
                    'sqlite3':'blob',
                    'postgres':'text',
                    'postgresql_psycopg2':'text'}
        try:
            return db_types[settings.DATABASE_ENGINE]
        except KeyError:
            raise Exception, '%s currently works only with: %s' % (
                self.__class__.__name__,','.join(db_types.keys()))


"""
South Introspection Extending for Custom fields
Reference: http://south.aeracode.org/docs/customfields.html#extending-introspection
"""

rules = {}
rules['IntegerTupleField'] = [
    (
        [IntegerTupleField],
        [],
        {
            "blank": ["blank", {"default": True}],
            "null": ["null", {"default": True}],
            "max_length": ["max_length", {"default": 64}],
        },
    ),
]

rules['CompressedTextField'] = [
    (
        [CompressedTextField],
        [],
        {
            "blank": ["blank", {"default": True}],
            "null": ["null", {"default": True}],
        },
    ),
]

for f in rules.keys():
    add_introspection_rules(rules[f], ["^txcommon\.db\.models\.%s" % f,])
