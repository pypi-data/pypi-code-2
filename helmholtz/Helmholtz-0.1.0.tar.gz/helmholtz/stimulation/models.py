#encoding:utf-8
from django.db import models
from helmholtz.core.models import Cast
from helmholtz.equipment.models import Equipment

class Stimulus(Cast):
    """Stimulation presented to/performed on a subject during an Experiment.""" 
    stimulus_generator = models.ForeignKey(Equipment, null=True, blank=True)
    
    def __unicode__(self):
        return 'Stimulus:%s' % (self.pk)
    
    class Meta:
        verbose_name_plural = 'stimuli'

class NullStimulus(Stimulus):
    """A convenient class to identify spontaneous activity protocols."""
    title = models.CharField(max_length=20,default="SpontaneousActivity",null=True,blank=True)
    
    class Meta:
        verbose_name = "spontaneous activity"
