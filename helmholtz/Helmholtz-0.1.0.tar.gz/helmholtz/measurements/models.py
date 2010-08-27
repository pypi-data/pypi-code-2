#encoding:utf-8
import re
from django.core.exceptions import ValidationError
from django.db.models.base import ModelBase
from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from helmholtz.core.models import Cast
from helmholtz.units.models import Unit

def verify_pattern(pattern):
    regexp = "^(((\[|\])\-{0,1}\d+(\.\d+){0,1}:\-{0,1}\d+(\.\d+){0,1}:\-{0,1}\d+(\.\d+){0,1}(\[|\]))|\w+|\w+(\.\w+)|(\-{0,1}\d+(\.\d+)))((\|(((\[|\])\-{0,1}\d+(\.\d+){0,1}:\-{0,1}\d+(\.\d+){0,1}:\-{0,1}\d+(\.\d+){0,1}(\[|\]))|\w+|(\-{0,1}\d+(\.\d+))))*)$"
    match = re.match(regexp, pattern, re.UNICODE)
    if not match :
        raise ValidationError("bad pattern format")    
                    
choices = (('I', 'Integer'), ('F', 'Float'), ('S', 'String'), ('B', 'Boolean'), ('M', 'ModelBase'))
class Parameter(models.Model):
    """Extend base properties of a class."""
    label = models.CharField(max_length=16)
    verbose_name = models.TextField(null=True, blank=True)
    pattern = models.TextField(null=True, blank=True, validators=[verify_pattern], help_text="pattern is defined like this : [min1:step1:max1]|[min2:step2:max2] or text1|text2|text3")
    type = models.CharField(max_length=1, choices=choices)
    notes = models.TextField(null=True, blank=True)
    unit = models.ForeignKey(Unit, null=True, blank=True)
    content_type = models.ForeignKey(ContentType)
    
    def get_type(self):
        dct = {'I':int, 'F':float, 'S':unicode, 'B':bool, 'M':ModelBase}
        return dct[self.type]
    
    def is_range(self, value):
        regexp = "^(\[|\])\-{0,1}\d+(\.\d+){0,1}:\-{0,1}\d+(\.\d+){0,1}:\-{0,1}\d+(\.\d+){0,1}(\]|\[)$"
        match = re.match(regexp, value, re.UNICODE)
        if match :
            return True
        else :
            return False

    def get_range_values(self, range, verify=False):
        values = list()
        tmp_str = range[1:-1]
        interval = tmp_str.split(':')
        start = float(eval(interval[0]))
        end = float(eval(interval[2]))
        step = float(eval(interval[1]))
        tp = self.get_type()
        if verify and (((step >= 0) and (start > end)) or ((step < 0) and (end > start))) :
            raise ValidationError("bad range format")    

        if range.startswith('[') :
            values.append(tp(start))

        if step :
            val = start
            while ((step > 0) and (val < (end - step))) or ((step < 0) and (val > (end - step))) :
                val += step
                values.append(tp(val))
        
        if range.endswith(']') :
            values.append(tp(end))
        return values

    def clean(self):
        
        if self.pattern :
            tp = self.get_type()
            if not (tp == ModelBase) :
                values = self.pattern.split('|')
                last_type = None
                for value in values :
                    #force value type
                    try :
                        new_value = tp(eval(value))
                        new_type = tp
                    except :
                        new_value = eval("u'%s'" % value)
                        new_type = type(new_value)
                    if (new_type == unicode) :
                        if self.is_range(new_value) :
                            new_type = 'range'
                            values = self.get_range_values(new_value, verify=True) 
                            if not (last_type is None) and (new_type != last_type) :
                                raise ValidationError("pattern values must be of the same type")    
                               
                    last_type = new_type
            else :
                try :
                    split = self.pattern.split('.')
                    content_type = ContentType.objects.get(app_label__iexact=split[0], model__iexact=split[1])
                except :
                    raise ValidationError("model %s not in database model." % self.pattern)
        else :
            tp = self.get_type()
            if (tp == ModelBase) :
                raise ValidationError("pattern cannot be null if type is ModelBase")
            
                    
    def get_values(self):
        if self.pattern and (self.get_type() != ModelBase) :
            str_values = self.pattern.split('|') 
            try :
                evals = [eval(k) for k in str_values] 
            except : 
                evals = [eval("'%s'" % k) for k in str_values]
            values = list()
            for value in evals :
                if self.is_range(value) :
                    values.extend(self.get_range_values(value))
                else :
                    values.append(value)
                return values
        elif (self.get_type() == ModelBase) :
            split = self.pattern.split('.')
            content_type = ContentType.objects.get(app_label__iexact=split[0], model__iexact=split[1])
            values = content_type.model_class().objects.all()
            return values
        else :
            return None
    
    def __unicode__(self):
        return self.label

class GenericMeasurement(Cast):
    """Base class of all kind of measurements. Subclasses set the value and unit 
    of additional parameters defined into the Parameter class."""
    parameter = models.ForeignKey(Parameter)
    unit = models.ForeignKey(Unit, null=True, blank=True)
    timestamp = models.DateTimeField(null=True, blank=True)
    content_type = models.ForeignKey(ContentType, null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    object = generic.GenericForeignKey('content_type', 'object_id')
    
    def get_unit(self):
        return self.unit if self.unit else (self.parameter.unit if self.parameter.unit else None)
    
    def get_symbol(self):
        return self.get_unit().symbol if self.unit else None
    symbol = property(get_symbol)        
    
    def __unicode__(self):
        measurement = self.cast()
        if hasattr(measurement,'value') :
            return "%s:%s %s at %s on object %s" % (self.parameter.label, measurement.value,self.unit,self.timestamp,self.object)
        else :
            return "%s in %s at %s on object %s" % (self.parameter.label, self.unit, self.timestamp, self.object)

class BoolMeasurement(GenericMeasurement):
    value = models.BooleanField()

class IntegerMeasurement(GenericMeasurement):
    value = models.IntegerField()

class FloatMeasurement(GenericMeasurement):
    value = models.FloatField()

class StringMeasurement(GenericMeasurement):
    value = models.TextField()

class ModelMeasurement_Integer(GenericMeasurement):
    value = generic.GenericForeignKey('c_type', 'o_id')
    c_type = models.ForeignKey(ContentType, null=True, blank=True)
    o_id = models.PositiveIntegerField(null=True, blank=True)
    
class ModelMeasurement_String(GenericMeasurement):
    value = generic.GenericForeignKey('c_type', 'o_id')
    c_type = models.ForeignKey(ContentType, null=True, blank=True)
    o_id = models.TextField(null=True, blank=True)
