from django.db import models
from django.utils.simplejson import loads, dumps
from django.utils.datastructures import MultiValueDict



class MultiValueDictField(models.Field):
    description = u'Multi-value dictionary Field'
    __metaclass__ = models.SubfieldBase
    
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('editable', False)
        super(MultiValueDictField,self).__init__(*args, **kwargs)

    def to_python(self, value):
        if isinstance(value, basestring):
            if value:
                return MultiValueDict(loads(value))
            else:
                return MultiValueDict()
        if isinstance(value, dict):
            return MultiValueDict(value)
        if isinstance(value,MultiValueDict):
            return value
        
        if not value:
            return MultiValueDict()
        
        raise ValueError('Unexpected value encountered when converting data to python')

    def get_prep_value(self, value):
        if not value:
            return 
        if isinstance(value,MultiValueDict):
            return dumps(dict(value.iterlists()))
        if isinstance(value, dict):
            return dumps(value)
        if isinstance(value, basestring):
            return value
        
        raise ValueError('Unexpected value encountered when preparing for database')

    def get_internal_type(self):
        return 'TextField'

try:
    from south.modelsinspector import add_introspection_rules
    add_introspection_rules([],['^bookreader\.fields\.MultiValueDictField'])
except ImportError, e:
    print str(e)
    pass