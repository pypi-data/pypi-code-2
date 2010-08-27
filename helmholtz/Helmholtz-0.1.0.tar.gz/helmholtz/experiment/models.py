#encoding:utf-8
from django.db import models
from django.contrib.contenttypes import generic
from helmholtz.core.shortcuts import get_class
from helmholtz.core.schema import create_subclass_lookup
from helmholtz.access_control.models import Permission
from helmholtz.people.models import Researcher
from helmholtz.equipment.models import Setup
from helmholtz.preparations.models import Preparation

class Experiment(models.Model):
    """Experiment done on a preparation."""
    label = models.CharField(max_length=32)
    start = models.DateTimeField(null=True, blank=True)
    end = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(null=True, blank=True)
    setup = models.ForeignKey(Setup)
    researchers = models.ManyToManyField(Researcher)
    preparation = models.ForeignKey(Preparation, null=True, blank=True)
    #permissions = generic.GenericRelation(Permission, content_type_field='content_type', object_id_field='object_id')
    
    def __unicode__(self):
        return self.label if self.label else self.pk
     
    def get_files(self):
        """A shortcut to access all File objects relative to an Experiment."""
        cls = get_class('storage', 'File')
        files = cls.objects.filter(signal__protocol__block__experiment=self).distinct()
        return files
    files = property(get_files)
    
    def get_signals(self):
        """A shortcut to access all Signal objects relative to an Experiment."""
        cls = get_class('signals', 'Signal')
        signals = cls.objects.filter(protocol__block__experiment=self).distinct()
        return signals
    signals = property(get_signals)   
    
    def get_protocols(self):
        """A shortcut to access all ProtocolRecording objects relative to an Experiment."""
        cls = get_class('recording', 'ProtocolRecording')
        protocols = cls.objects.filter(block__experiment=self).distinct()
        return protocols
    protocols = property(get_protocols)
    
    def count_methods_of_type(self, method_cls):
        """Return the number of method used in the Experiment."""
        lookup = create_subclass_lookup(method_cls)
        prefix = 'recordingconfiguration__configuration'
        suffix = 'isnull'
        st = "%s__%s__%s" % (prefix, lookup, suffix)
        count = self.recordingblock_set.filter(**{st:False}).distinct().count()
        return count
      
    def get_methods(self):
        """Return the list of recording methods used during an Experiment."""
        methods = set()
        for block in self.recordingblock_set.all() :
            methods.update(set(block.methods))
        return list(methods)
    methods = property(get_methods)
    
    def get_protocols_by_type(self):
        """Return a dictionary containing all protocols relative to the experiment arranged by protocol type."""
        protocols = {}
        for block in self.recordingblock_set.all() :
            for protocol in block.protocolrecording_set.all() :
                exp_protocol = protocol.type
                if not (exp_protocol in protocols) :
                    protocols[exp_protocol] = []
                protocols[exp_protocol].append(protocol)
        #transform each list of protocol into a QuerySet
        for protocol in protocols :
            pks = [k.pk for k in protocols[protocol]]
            cls = self.recordingblock_set.model.protocolrecording_set.related.model
            protocols[protocol] = cls.objects.filter(pk__in=pks)
        return protocols
    
    def get_distinct_protocols(self):
        """Get all protocol types."""
        protocols = self.get_protocols_by_type().keys()
        return protocols
    distinct_protocols = property(get_protocols)
    
    def _protocols(self):
        """docstring needed"""
        protocols = [k.label for k in self.get_distinct_protocols()]
        return ','.join(protocols) if protocols else None
    protocol_names = property(_protocols)
    
    class Meta:
        ordering = ['-start', 'label']
