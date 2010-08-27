#encoding:utf-8
from django.db import models
from helmholtz.units.fields import PhysicalQuantityField
from helmholtz.neuralstructures.models import Atlas, BrainRegion
from helmholtz.equipment.models import StereotaxicType

ap_choices = (('A', 'anterior'), ('M', 'medial'), ('P', 'posterior'))
lt_choices = (('L', 'left'), ('R', 'right'))
dv_choices = (('D', 'dorsal'), ('M', 'medial'), ('V', 'ventral'))
class Position(models.Model):
    """Defines a coordinate position relative to an Atlas and an apparatus."""
    label = models.CharField(max_length=20, null=True, blank=True)
    brain_region = models.ForeignKey(BrainRegion, null=True, blank=True)
    apparatus = models.ForeignKey(StereotaxicType, null=True, blank=True)
    atlas = models.ForeignKey(Atlas, null=True, blank=True)
    ap_axis = models.CharField(max_length=1, choices=ap_choices, null=True, blank=True)
    ap_value = PhysicalQuantityField(unit='mm', null=True, blank=True)
    dv_axis = models.CharField(max_length=1, choices=dv_choices, null=True, blank=True)
    dv_value = PhysicalQuantityField(unit='mm', null=True, blank=True)
    lt_axis = models.CharField(max_length=1, choices=lt_choices, null=True, blank=True)
    lt_value = PhysicalQuantityField(unit='mm', null=True, blank=True)
    depth = PhysicalQuantityField(unit='&micro;m', null=True, blank=True, verbose_name='distance from the surface')
    
    def _ap(self):
        st = ''
        if self.ap_axis :
            st += self.get_ap_axis_display()
            if self.ap_value :
                st += '(%s)' % self.ap_value
        return st if st else None
    _ap_axis = property(_ap)
    
    def _dv(self):
        st = ''
        if self.dv_axis :
            st += self.get_dv_axis_display()
            if self.dv_value :
                st += '(%s)' % self.dv_value
        return st if st else None
    _dv_axis = property(_dv)
    
    def _lt(self):
        st = ''
        if self.lt_axis :
            st += self.get_lt_axis_display()
            if self.lt_value :
                st += '(%s)' % self.lt_value
        return st if st else None
    _lt_axis = property(_lt)
    
    def __unicode__(self):
        return "%s-%s-%s in %s at %s depth" % (self._ap_axis,
                                   self._dv_axis,
                                   self._lt_axis,
                                   self.brain_region,
                                   self.depth)

class SpatialConfiguration(models.Model):
    """Defines position of Electrodes, Cameras and Cells 
    relatively to a stereotaxic point defined in Position."""
    label = models.CharField(max_length=20, null=True, blank=True)
    distance_from_surface = PhysicalQuantityField(unit='&micro;m', null=True, blank=True, verbose_name='distance')
    ap_angle = PhysicalQuantityField(unit='rad', null=True, blank=True, verbose_name='anterior-posterior angle')
    lt_angle = PhysicalQuantityField(unit='rad', null=True, blank=True, verbose_name='lateral angle')
    dv_angle = PhysicalQuantityField(unit='rad', null=True, blank=True, verbose_name='dorsal-ventral angle')

    def __unicode__(self):
        return "[%s,%s,%s,%s]" % (self.distance_from_surface, self.ap_angle, self.lt_angle, self.dv_angle) 
