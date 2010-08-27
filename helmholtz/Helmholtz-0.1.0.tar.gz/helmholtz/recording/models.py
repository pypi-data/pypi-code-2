#encoding:utf-8
from django.db import models
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from helmholtz.core.shortcuts import cast_object_to_leaf_class, get_class
from helmholtz.core.schema import cast_queryset
from helmholtz.annotation.models import IntegerAnnotation, IntegerObjectIsAnnotated
from helmholtz.measurements.models import GenericMeasurement
from helmholtz.equipment.models import Device, DeviceConfiguration
from helmholtz.experiment.models import Experiment
from helmholtz.location.models import Position
from helmholtz.stimulation.models import Stimulus

class RecordingBlock(models.Model):
    """Split an experiment into several sequences of recording."""
    experiment = models.ForeignKey(Experiment)
    label = models.CharField(max_length=10, null=True, blank=True)
    start = models.DateTimeField(null=True, blank=True)
    end = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(null=True, blank=True)
    
    def __unicode__(self):
        st = "Recording block "
        st = "%s%s" % (st, self.label) if self.label else "%s%s" % (st, self.id)
        return st
    
    def get_files(self):
        """docstring needed"""
        cls = get_class('storage', 'File')
        files = cls.objects.filter(signal__protocol__block=self).distinct()
        return files
    files = property(get_files)    
    
    def get_signals(self):
        """docstring needed"""
        cls = get_class('signals', 'Signal')
        signals = cls.objects.filter(protocol__block=self).distinct()
        return signals
    signals = property(get_signals)    
    
    def get_files_and_status_by_protocol_types(self, user):
        """Store files relative to the block by protocol type."""
        files = dict()
        for file in self.files :
            protocol = file.protocol.type 
            if not (protocol in files) :
                files[protocol] = []
            signals = dict()
            for signal in cast_queryset(file.signal_set.all(), 'ElectricalSignal') :
                if not signal.episode in signals :
                    signals[signal.episode] = list()
                signals[signal.episode].append(signal)
            files[protocol].append({'object':file, 'status':file.download_status_key(user), 'signals':signals})
        for protocol in files :
            files[protocol].sort(key=lambda x:x['object'].protocol.pk)
        return files
    
    def get_protocols_by_type(self):
        """Store protocols relative to the block by protocol type."""
        protocols = {}
        for protocol in self.protocolrecording_set.all() :
            exp_protocol = protocol.type 
            if not (exp_protocol in protocols) :
                protocols[exp_protocol] = []
            protocols[exp_protocol].append(protocol)
        #transform each list of protocol into a QuerySet
        for protocol in protocols :
            protocols[protocol] = self.protocolrecording_set.model.objects.filter(pk__in=[k.pk for k in protocols[protocol]])
        return protocols
    
    def get_protocols(self):
        """Get all protocol types."""
        protocols = self.get_protocols_by_type().keys()
        return protocols
    distinct_protocols = property(get_protocols)
    
    def _protocols(self):
        """docstring needed"""
        protocols = [k.label for k in self.get_protocols()]
        return ','.join(protocols) if protocols else None
    protocol_names = property(_protocols)
    
    def get_method_set(self):
        return set([cast_object_to_leaf_class(k.configuration).__class__._meta.verbose_name for k in self.recordingconfiguration_set.all()])    

    def get_methods(self):
        """Get method relative to the block."""
        all_methods = self.get_method_set()
        methods = list(all_methods)
        methods.sort()
        return methods
    methods = property(get_methods)
    
    def _methods(self):
        methods = self.get_methods()
        return ', '.join(methods) if methods else None        
    method_names = property(_methods)
    
    def get_configurations_by_method_types(self):
        """Store recording configurations relative to the block by method type."""
        configurations = {}
        for configuration in self.recordingconfiguration_set.all() :
            name = cast_object_to_leaf_class(configuration).__class__._meta.verbose_name
            if not (name in configurations) :
                configurations[name] = []
            configurations[name].append(configuration)
        for configuration in configurations :
            configurations[configuration] = self.recordingconfiguration_set.filter(pk__in=[k.pk for k in configurations[configuration]])
        return configurations
    configurations = property(get_configurations_by_method_types)
    
    @property
    def duration(self):
        return self.end - self.start
    
    class Meta:
        ordering = ['experiment__label', 'label']

class RecordingConfiguration(models.Model):
    """Configuration of each device used to acquire data."""
    label = models.CharField(max_length=30, null=True, blank=True)
    block = models.ForeignKey(RecordingBlock)
    device = models.ForeignKey(Device)
    configuration = models.ForeignKey(DeviceConfiguration, null=True, blank=True, verbose_name="device configuration")
    position = models.ForeignKey(Position, null=True, blank=True, verbose_name="absolute position")
    measurements = generic.GenericRelation(GenericMeasurement, content_type_field='content_type', object_id_field='object_id')
    
    def __unicode__(self):
        return unicode(self.pk)
    
    @property
    def type(self):
        return self.get_subclass()._meta.verbose_name 

class ProtocolRecording(models.Model):
    """Split a recording block into several stimulation protocols."""
    block = models.ForeignKey(RecordingBlock)
    label = models.CharField(max_length=20)
    stimulus = models.ForeignKey(Stimulus, null=True, blank=True)
    notes = models.TextField(null=True, blank=True)
    measurements = generic.GenericRelation(GenericMeasurement, content_type_field='content_type', object_id_field='object_id')
    
    def get_type(self):
        return self.stimulus.cast().__class__._meta.verbose_name if self.stimulus else 'spontaneous activity'# self.protocol.entity.model_class()
    type = property(get_type)
    
    def get_methods(self):
        """docstring needed"""
        all_methods = set() 
        for signal in self.signal_set.all() :
            methods = signal.configuration.block.get_method_set()
            all_methods.update(methods)
        return list(all_methods)
    methods = property(get_methods)
    
    def get_method_names(self):
        """docstring needed"""
        return ', '.join(self.methods) if self.methods else None  
    method_names = property(get_method_names)
    
    def get_file(self):
        """docstring needed"""
        cls = get_class('storage', 'File')
        files = cls.objects.filter(signal__protocol__pk=self.pk).distinct()
        if files.count() :
            return files[0]
        else :
            return None
    file = property(get_file)   
    
    def get_files(self):
        """docstring needed"""
        cls = get_class('storage', 'File')
        return cls.objects.filter(signal__channel__protocol=self)   
    
    def __unicode__(self):
        return "ProcotolRecording (block %s, stimulus %s)" % (self.block.label, self.stimulus)
