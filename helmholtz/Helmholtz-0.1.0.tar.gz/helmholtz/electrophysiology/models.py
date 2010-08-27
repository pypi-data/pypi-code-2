#encoding:utf-8
from django.db import models
from helmholtz.electrophysiology.fields import MatrixField
from helmholtz.chemistry.models import Product, Solution
from helmholtz.units.fields import PhysicalQuantityField 
from helmholtz.equipment.models import Equipment, Material, DeviceConfiguration
from helmholtz.signals.models import RecordingMode, Signal, ChannelType, Channel

#physical electrodes

class Electrode(Equipment):
    external_diameter = PhysicalQuantityField(unit='&mu;m', null=True, blank=True)
    material = models.ForeignKey(Material, null=True, blank=True)
    
    def parameters_str(self):
        return "external diameter: %s, material: %s" % (self.external_diameter, self.material)
    
    def __unicode__(self):
        return "%s(%s)" % (self.__class__.__name__, self.parameters_str()) 

class DiscElectrode(Electrode):
    
    def parameters_str(self):
        st = super(DiscElectrode, self).parameters_str()
        return st

class SolidElectrode(Electrode):
    impedance = PhysicalQuantityField(unit='M&Omega;', null=True, blank=True)
    
    def parameters_str(self):
        st = super(SolidElectrode, self).parameters_str()
        st += ", impedance: %s" % (self.impedance)
        return st

class HollowElectrode(Electrode):
    internal_diameter = PhysicalQuantityField(unit='&mu;m', null=True, blank=True)
    
    def parameters_str(self):
        st = super(HollowElectrode, self).parameters_str()
        st += ", internal diameter: %s" % (self.internal_diameter)
        return st

class SharpElectrode(HollowElectrode):
    
    def parameters_str(self):
        st = super(SharpElectrode, self).parameters_str()
        return st

class PatchElectrode(HollowElectrode):
    
    def parameters_str(self):
        st = super(PatchElectrode, self).parameters_str()
        return st

class MultiElectrode(Equipment):
    
    def parameters_str(self):
        st = super(MultiElectrode, self).parameters_str()
        return st

#electrode configurations

class EEG(DeviceConfiguration):
    amplification = PhysicalQuantityField(unit='', null=True, blank=True)
    filtering = models.CharField(max_length=50, null=True, blank=True)
    
class EKG(DeviceConfiguration):
    amplification = PhysicalQuantityField(unit='', null=True, blank=True)
    filtering = models.CharField(max_length=50, null=True, blank=True)
      
#Maybe ElectrodeConfiguration is too specific whereas the term Electrode is very generic 
class ElectrodeConfiguration(DeviceConfiguration):
    """Base class of all kind of electrode configurations."""
    resistance = PhysicalQuantityField(unit='M&Omega;', null=True, blank=True)
    amplification = models.CharField(max_length=100, null=True, blank=True)
    filtering = models.CharField(max_length=100, null=True, blank=True)
    
    def parameters_str(self):
        return "resistance: %s, amplification: %s, filtering:%s" % (self.resistance, self.amplification, self.filtering)
    
    def __unicode__(self):
        return "%s(%s)" % (self.__class__.__name__, self.parameters_str()) 

class DiscElectrodeConfiguration(DeviceConfiguration):
    """ECG or EEG electrode configuration."""
    contact_gel = models.ForeignKey(Product, null=True, blank=True)
    
    def parameters_str(self):
        st = super(DiscElectrodeConfiguration, self).parameters_str()
        st += ", contact gel:%s" % (self.contact_gel)
        return st

class SolidElectrodeConfiguration(ElectrodeConfiguration):
    
    def parameters_str(self):
        st = super(SolidElectrodeConfiguration, self).parameters_str()
        return st

class HollowElectrodeConfiguration(ElectrodeConfiguration):
    solution = models.ForeignKey(Solution, null=True, blank=True)
    
    def parameters_str(self):
        st = super(HollowElectrodeConfiguration, self).parameters_str()
        st += ", solution:%s" % (self.solution)
        return st

class SharpElectrodeConfiguration(HollowElectrodeConfiguration):
    
    def parameters_str(self):
        st = super(SharpElectrodeConfiguration, self).parameters_str()
        return st
    
    class Meta:
        verbose_name = 'sharp'

configurations = (('CA', 'cell attached'),
                  ('WC', 'whole cell'),
                  ('PP', 'perforated patch'),
                  ('IO', 'inside out'),
                  ('OO', 'outside out'),
                  ('L', 'loose'))
class PatchElectrodeConfiguration(HollowElectrodeConfiguration):
    seal_resistance = PhysicalQuantityField(unit='M&Omega;', null=True, blank=True)
    contact_configuration = models.CharField(max_length=2, choices=configurations, null=True, blank=True)
    
    def parameters_str(self):
        st = super(PatchElectrodeConfiguration, self).parameters_str()
        st += ", seal resistance:%s" % (self.seal_resistance)
        st += ", contact configuration:%s" % (self.get_contact_configuration_display())
        return st

    method = "patch"
    class Meta:
        verbose_name = 'patch'

#channels, recording modes and signals applied to electrophysiology
class ElectricalChannelType(ChannelType):
    pass
  
class ElectricalRecordingMode(RecordingMode):
    pass

class ElectricalChannel(Channel):
    type = models.ForeignKey(ElectricalChannelType, null=True, blank=True)
    mode = models.ForeignKey(ElectricalRecordingMode, null=True, blank=True)
    units = MatrixField(native_type='varchar', dimensions=[2])
    
    def __unicode__(self):
        st = super(ElectricalChannel, self).__unicode__()
        if self.type :
            st += "(%s)" % (self.type)
        return st

class RecordingPoint(models.Model):
    label = models.CharField(max_length=10, null=True, blank=True)
    number = models.PositiveSmallIntegerField(default=1)
    intra = models.BooleanField(default=False)
    
    def __unicode__(self):
        st = "%s" % self.number
        if self.label :
            return "%s : %s" % (self.label, st)
        return st

class ElectricalSignal(Signal):
    episode = models.PositiveIntegerField(default=1)
    channel = models.ForeignKey(ElectricalChannel)
    recording_point = models.ForeignKey(RecordingPoint)

    def __unicode__(self):
        return "%s" % self.pk

    def get_x_unit(self):
        return self.channel.electricalchannel.units.data[0]
    x_unit = property(get_x_unit)
    
    def get_y_unit(self):
        return self.channel.electricalchannel.units.data[1]
    y_unit = property(get_y_unit)
    
    def duration(self): 
        return self.analyses.get(input_of__label__icontains="duration").input_of.get().outputs.get().cast().value
    
    def min(self):
        return self.analyses.get(input_of__label__icontains="min").input_of.get().outputs.get().cast().value
    
    def max(self):
        return self.analyses.get(input_of__label__icontains="max").input_of.get().outputs.get().cast().value
    
    def p2p(self):
        return self.analyses.get(input_of__label__icontains="p2p").input_of.get().outputs.get().cast().value
    
    def amplitude(self):
        return self.analyses.get(input_of__label__icontains="amplitude").input_of.get().outputs.get().cast().value
    
    def mean(self):
        return self.analyses.get(input_of__label__icontains="mean").input_of.get().outputs.get().cast().value
    
    def std(self):
        return self.analyses.get(input_of__label__icontains="std").input_of.get().outputs.get().cast().value
    
    def rms(self):
        return self.analyses.get(input_of__label__icontains="rms").input_of.get().outputs.get().cast().value
    
    def var(self):
        return self.analyses.get(input_of__label__icontains="var").input_of.get().outputs.get().cast().value
