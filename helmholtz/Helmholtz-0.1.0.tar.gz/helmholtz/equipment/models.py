#encoding:utf-8

##############################################################################
#Classes useful to reconstruct setups used for experimentations              #
##############################################################################

##############################################################################
#Here's some usecases :                                                      #                                                              #
# 1 - define setups used to realize home made experimental protocols         #
# 2 - store set of devices useful to deploy a setup                          #
##############################################################################

from django.db import models
from django.contrib.contenttypes import generic
from helmholtz.core.models import Cast
from helmholtz.annotation.models import IntegerAnnotation
from helmholtz.people.models import Supplier, ScientificStructure

class Material(models.Model):
    name = models.CharField(max_length=256)
    composition = models.CharField(max_length=32, null=True, blank=True)
    supplier = models.ForeignKey(Supplier, null=True, blank=True)
    
    def __unicode__(self):
        return self.name
    shortname = property(__unicode__)
    
    class Meta:
        ordering = ['name', 'supplier']
        unique_together = (('name', 'supplier'),)

class Equipment(Cast):
    """Equipment that could be deployed in a Setup."""
    manufacturer = models.ForeignKey(Supplier, null=True, blank=True)
    model = models.CharField(max_length=20)
    annotations = generic.GenericRelation(IntegerAnnotation, content_type_field='content_type', object_id_field='object_id')
    
    def __unicode__(self):
        return u"%s (%s,%s)" % (self.type, self.manufacturer, self.model)
    
    class Meta :
        verbose_name_plural = 'equipment'

class EquipmentType(Cast):
    """Type of Equipment."""
    name = models.CharField(primary_key=True, max_length=20)
    
    def __unicode__(self):
        return self.name
    
    class Meta :
        ordering = ['name']

class StereotaxicType(EquipmentType):
    """Subclass of EquipmentType to make distinction between stereotaxic apparatus and common equipment types."""
    
    def __unicode__(self):
        return self.name

class GenericEquipment(Equipment):
    """Subclass of Equipment used when it is not necessary to describe an Equipment with metadata."""
    type = models.ForeignKey(EquipmentType)

class Device(Cast):
    """Realization of an Equipment."""
    equipment = models.ForeignKey(Equipment)
    label = models.CharField(max_length=20)
    serial_or_id = models.CharField(max_length=50, null=True, blank=True)
    notes = models.TextField(null=True, blank=True)
    
    def __unicode__(self):
        return self.label

class DeviceConfiguration(Cast):
    """Base class of all kind of configurations."""
    label = models.CharField(max_length=50, null=True, blank=True)
    notes = models.TextField(null=True, blank=True)

    def __unicode__(self):
        return unicode(self.pk)

class SubSystem(models.Model):
    """Structure Equipment used in a Setup in a hierarchical manner."""
    parent = models.ForeignKey('self', null=True, blank=True)
    label = models.CharField(max_length=256)
    devices = models.ManyToManyField(Device, blank=True)
    annotations = generic.GenericRelation(IntegerAnnotation, content_type_field='content_type', object_id_field='object_id')
    
    def __unicode__(self):
        return self.label
    
    def get_components(self):
        """docstring needed"""
        result = list()
        subsystems = self.subsystem_set.all()
        for subsystem in subsystems :
            result.append(subsystem)
            result.extend(subsystem.get_components())
        return result
    
    def get_equipment(self):
        """docstring needed"""
        equipment = list(self.equipment.all())
        subsystems = self.subsystem_set.all()
        for subsystem in subsystems :
            equipment.extend(subsystem.get_equipment())
        return equipment   
    
    class Meta :
        ordering = ['label']
    
class Setup(models.Model):
    """Setup used to launch protocols during Experiments."""
    label = models.CharField(max_length=30, null=True, blank=True)
    place = models.ForeignKey(ScientificStructure, related_name='is_location_of')
    room = models.CharField(max_length=16)
    subsystems = models.ManyToManyField(SubSystem)
    annotations = generic.GenericRelation(IntegerAnnotation, content_type_field='content_type', object_id_field='object_id')
    
    def __unicode__(self):
        return u"%s \u2192 %s" % (self.place, self.room)
    
    def get_components(self):
        """docstring needed"""
        result = list()
        subsystems = self.subsystems.all()
        for subsystem in subsystems :
            result.append(subsystem)
            result.extend(subsystem.get_components())
        return result
    
    def get_equipment(self):
        """docstring needed"""
        equipment = list()
        subsystems = self.subsystems.all()
        for subsystem in subsystems :
            equipment.extend(subsystem.get_equipment())
        return equipment   
