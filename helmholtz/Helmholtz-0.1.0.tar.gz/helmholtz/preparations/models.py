#encoding:utf-8

#############################################################################################
#Classes useful for tracking subjects living in a laboratory and used for experimentation   #
#############################################################################################
import datetime
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from helmholtz.core.models import Cast
from helmholtz.core.shortcuts import cast_object_to_leaf_class
from helmholtz.species.models import Strain
from helmholtz.people.models import Supplier
from helmholtz.equipment.models import Equipment
from helmholtz.measurements.models import GenericMeasurement, Parameter
from helmholtz.units.fields import PhysicalQuantityField
from helmholtz.chemistry.models import Solution

class Animal(models.Model):
    """Animal that is the subject of an Experiment."""
    strain = models.ForeignKey(Strain)
    identifier = models.CharField(max_length=15, null=True, blank=True)
    sex = models.CharField(max_length=1, choices=(('M', 'male'), ('F', 'female')), null=True, blank=True)
    birth = models.DateField(help_text="(approximate)", null=True, blank=True)
    sacrifice = models.DateField(null=True, blank=True)
    supplier = models.ForeignKey(Supplier, null=True, blank=True) 
    
    def get_birth(self, age):
        """Gets the date of birth from the age in days and sacrifice date."""
        assert self.sacrifice, 'sacrifice property unknown'
        delta = datetime.timedelta(age)
        return self.sacrifice - delta
    
    def set_birth(self, age, sacrifice):
        """docstring needed"""
        delta = datetime.timedelta(age)
        self.birth = sacrifice - delta
        self.save()
    
    def get_sacrifice(self, age): 
        """Gets the date of sacrifice from the age and birth date."""
        assert self.birth, 'birth property unknown'
        delta = datetime.timedelta(age)
        return self.birth + delta    
    
    def set_sacrifice(self, age, birth):
        """docstring needed"""
        delta = datetime.timedelta(age)
        self.sacrifice = birth + delta
        self.save()
    
    def _age(self):
        """Age in weeks."""
        if self.sacrifice and self.birth:
            return round((self.sacrifice - self.birth).days / 7.0, 1)
        else:
            return None
    age = property(_age)
    
    def __unicode__(self):
        st = ''
        if self.identifier :
            st += self.identifier
        if self.strain :
            if self.identifier :
                st += ', '
            st += "%s(%s)" % (self.strain.species.english_name, self.strain.name)
        if self.sex :
            st += ', ' + self.get_sex_display() 
        age = self._age()
        if age :
            st += ', %s weeks' % age
        return st 
        
    class Meta:
        ordering = ['-sacrifice']

class Preparation(Cast):
    """docstring needed"""
    animal = models.ForeignKey(Animal)
    protocol = models.TextField(null=True, blank=True)   
    observations = generic.GenericRelation(GenericMeasurement, verbose_name="observations", content_type_field='content_type', object_id_field='object_id')
    
    def __unicode__(self):
        cast = cast_object_to_leaf_class(self)
        return u"%s, %s" % (cast._meta.verbose_name, self.animal)
    
    def subclass(self):
        cast = cast_object_to_leaf_class(self)
        return cast.__class__._meta.verbose_name
    
    def get_weights(self):
        """docstring needed"""
        preparation_type = ContentType.objects.get_for_model(self)
        return GenericMeasurement.objects.filter(parameter__label='weight',
                                                 content_type=preparation_type,
                                                 object_id=self.id)
    
    def get_weight_at_sacrifice(self):
        """docstring needed"""
        one_hour = datetime.timedelta(0, 3600)
        weights = self.get_weights().filter(timestamp__gte=self.animal.sacrifice - one_hour)
        if weights.count() > 0:
            return weights[weights.count() - 1]
        else:
            return None

    def add_field(self, name, unit):
        """
        Add a metadata field taking a float value to the preparation.
        """
        param, created = Parameter.objects.get_or_create(
                            label=name,
                            content_type = ContentType.objects.get_for_model(self),
                            type="F",
                            unit=unit)
        return param
        
        

class InVivo(Preparation): # class name would be better as "InVivoPreparation"
    """docstring needed"""

    class Meta:
        verbose_name = "in vivo"


class InVitroCulture(Preparation):
    """docstring needed"""
    
    class Meta:
        verbose_name = "in vitro"

class InSilico(Preparation):
    """docstring needed"""
    
    class Meta:
        verbose_name = "in silico"
          
class InVitroSlice(Preparation):
    """docstring needed"""
    thickness = PhysicalQuantityField(unit='&mu;m', null=True)
    cut_orientation = models.CharField(max_length=50, null=True, blank=True)
    cutting_solution = models.ForeignKey(Solution, related_name="is_cutting_solution_of", null=True, blank=True)
    bath_solution = models.ForeignKey(Solution, related_name="is_bath_solution_of", null=True, blank=True)
    equipment = models.ForeignKey(Equipment, null=True, blank=True)
    
    class Meta:
        verbose_name = "in vitro slice"
    
class PreparationInformation(Cast):
    preparation = models.ForeignKey(Preparation)

# the following classes do not belong here, but in a "vision" component

class AreaCentralis(PreparationInformation):
    """docstring needed"""
    left_x = PhysicalQuantityField(unit='mm', null=True, blank=True)
    left_y = PhysicalQuantityField(unit='mm', null=True, blank=True)
    right_x = PhysicalQuantityField(unit='mm', null=True, blank=True)
    right_y = PhysicalQuantityField(unit='mm', null=True, blank=True)
          
    class Meta:
        verbose_name_plural = 'area centralis'
    
    def __unicode__(self):
        return "lx:%s,ly:%s,rx:%s,ry:%s" % (self.left_x, self.left_y, self.right_x, self.right_y)
    
class EyeCorrection(PreparationInformation):
    """docstring needed"""
    left = PhysicalQuantityField(unit='&delta;', null=True, blank=True)
    right = PhysicalQuantityField(unit='&delta;', null=True, blank=True)
        
    class Meta:
        verbose_name_plural = 'eye correction'
    
    def __unicode__(self):
        return "left:%s,right:%s" % (self.left, self.right)
