from django.db import models
from ipyfield import IP


class IPyField(models.Field):
    """
    Handles conversion between int db column and IP instance.
    """
    
    __metaclass__ = models.SubfieldBase

    def to_python(self, value):
        if not value: 
            return None
        elif isinstance(value, IP):
            return value
        else:
            return IP(value)

    def get_prep_value(self, value):
        value = self.to_python(value)
        if not value:
            return None
        return value.int()

    def to_string(self, obj):
        value = self._get_val_from_obj(obj)
        return str(self.get_db_prep_value(value))

    def get_prep_lookup(self, lookup_type, value):
        if lookup_type == 'in':
            if isinstance(value, str):
                value = IP(value)
            return [self.get_prep_value(v) for v in value]
        elif lookup_type == 'exact':
            return self.get_prep_value(value)
        else:
            raise TypeError('Lookup type %r not supported.' % lookup_type)

    def get_internal_type(self):
        return 'BigIntegerField'

