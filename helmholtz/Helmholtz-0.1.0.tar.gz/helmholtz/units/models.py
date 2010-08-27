#encoding:utf-8
#usecase:
# 1 - avoiding hard coded units
# 2 - convert a value from a unit to another
  
from django.db import models
from django.core.exceptions import ValidationError
from helmholtz.core.models import HierarchicalStructure

class Meaning(models.Model):
    """Physical meaning of a Unit."""
    description = models.TextField()
    
    def __unicode__(self):
        return self.description
    
    def get_units(self):
        count = 0
        for unit in self.unit_set.all() :
            count += 1 
            count += unit.unit_set.count()
        return count
    units = property(get_units)

class Unit(HierarchicalStructure):
    """Unit corresponding to a physical value."""
    symbol = models.CharField(max_length=16, primary_key=True)
    name = models.CharField(max_length=32)
    base_unit = models.ForeignKey('self', null=True, blank=True)
    conversion_pattern = models.TextField(null=True, blank=True)
    meaning = models.ForeignKey(Meaning, null=True, blank=True)
    math_symbol = models.CharField(max_length=32, null=True, blank=True)
    
    def get_root(self):
        return self.root('base_unit')
    
    def unit_of(self):
        """Get the physical Meaning of the base Unit."""
        root = self.get_root()
        return root.meaning
    
    def clean(self):
        """Verify if data from a form are valid."""
        if (self.base_unit is None) and self.conversion_pattern :
            raise ValidationError('conversion pattern must be empty for base units')
        if self.base_unit and not self.conversion_pattern :
            raise ValidationError('conversion pattern must be specified for derived units') 
        if self.base_unit and self.base_unit.base_unit :
            raise ValidationError('parent unit must be a base unit')
    
    def convert_to_base_unit(self, value):
        """Convert a value from a Unit system to its relative base Unit."""
        pattern = self.conversion_pattern
        pattern = pattern.replace('x', str(value))
        return eval(pattern)
    
    def get_math_symbol(self):
        """Return Unit or base Unit math_symbol field."""
        if self.math_symbol :
            return self.math_symbol
        elif self.base_unit :
            root = self.get_root()
            if root.math_symbol :
                return root.math_symbol
            else :
                return None
        else :
            return None
    
    def __unicode__(self):
        return self.symbol
