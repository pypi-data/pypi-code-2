#encoding:utf-8
from django.db import models
from helmholtz.core.models import Cast
from helmholtz.chemistry.models import Solution
from helmholtz.experiment.models import Experiment
from helmholtz.units.fields import PhysicalQuantityField

class DrugApplication(Cast):
    """Store drug application that could be done on a Preparation during an Experiment."""
    experiment = models.ForeignKey(Experiment)
    solution = models.ForeignKey(Solution)
    notes = models.TextField(null=True, blank=True)
    
    def __unicode__(self):
        return self._meta.verbose_name + ' ' + str(self.id)
    
class Perfusion(DrugApplication):
    """Store drug perfusion that could be done on a Preparation during an Experiment."""
    start = models.DateTimeField(null=True, blank=True) 
    end = models.DateTimeField(null=True, blank=True) 
    rate = PhysicalQuantityField(unit='mL/h', null=True, blank=True) 
     
    def get_duration(self) :
        if self.start and self.end:
            return self.end - self.start
        else:
            return None
    
    class Meta :
        ordering = ['-start']

class Injection(DrugApplication):
    """Store drug injection that could be done on a Preparation during an Experiment."""
    volume = PhysicalQuantityField(unit='ml', null=True, blank=True)
    time = models.DateTimeField(null=True, blank=True)
    
    class Meta :
        ordering = ['-time']
