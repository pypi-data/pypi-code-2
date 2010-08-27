#encoding:utf-8
from django.db import models

class Quality(object):
    def __init__(self, value, max):
        assert value <= max, "value must be <= max"
        self.max = max
        self.value = value
         
    def __str__(self):
        return '%s/%s' % (self.value, self.max)
    
    def __unicode__(self):
        return u'%s/%s' % (self.value, self.max)
    
    def __repr__(self):
        return "Quality(%s,%s)" % (self.value, self.max) 
    
    def db_repr(self):
        return """%s/%s""" % (self.value, self.max)
        
class QualityField(models.PositiveSmallIntegerField):
    __metaclass__ = models.SubfieldBase
    
    def __init__(self, max=5, *args, **kwargs):
        self.max = max
        help_text = "Specify a value from 0 to %s." % max
        super(QualityField, self).__init__(help_text=help_text, *args, **kwargs)
    
    def to_python(self, value):
        if isinstance(value, Quality) :
            return value
        return Quality(value, self.max) if value else None
    
    def db_prep_value(self, value):
        return value.db_repr()
