#encoding:utf-8
from django.db import models
from django.contrib.contenttypes import generic
from helmholtz.core.models import Cast
from helmholtz.core.shortcuts import cast_object_to_leaf_class
from helmholtz.core.fields import QualityField
from helmholtz.recording.models import ProtocolRecording, RecordingConfiguration
from helmholtz.storage.models import File
##from helmholtz.analysis.models import Potential_DatabaseObject_Id

class ChannelType(Cast):
    """docstring needed."""
    name = models.CharField(max_length=32)
    symbol = models.CharField(max_length=8, null=True, blank=True)
    
    def __unicode__(self):
        return self.symbol if self.symbol else self.name

class RecordingMode(Cast):
    """docstring needed."""
    name = models.CharField(max_length=16)
    
    def __unicode__(self):
        return self.name

class Channel(Cast):
    """docstring needed."""
    label = models.CharField(max_length=10, null=True, blank=True)
    number = models.PositiveSmallIntegerField(default=1)
    
    def __unicode__(self):
        st = "%s" % self.number
        if self.label :
            return "%s : %s" % (self.label, st)
        return st

class Signal(Cast):
    """Raw data acquired during an Experiment."""
    label = models.CharField(max_length=16)
    file = models.ForeignKey(File)
    protocol = models.ForeignKey(ProtocolRecording, null=True, blank=True)
    configuration = models.ForeignKey(RecordingConfiguration, null=True, blank=True)
    quality = QualityField(max=5, null=True, blank=True)
    ##analyses = generic.GenericRelation(Potential_DatabaseObject_Id, content_type_field='content_type', object_id_field='object_id')
    
    def __unicode__(self):
        return "%s" % self.label
    
    def get_method_type(self):
        return cast_object_to_leaf_class(self.configuration.configuration).__class__._meta.verbose_name.lower()
    method = property(get_method_type)
    
    def get_protocol_type(self):
        return self.protocol.type if self.protocol else None
    protocol_type = property(get_protocol_type)
