#encoding:utf-8
from django.db import models
from django.contrib.contenttypes import generic
from helmholtz.core.shortcuts import find_file
from helmholtz.access_control.conditions import is_downloadable_by
from helmholtz.access_control.models import IntegerPermission
##from helmholtz.access_request.models import AccessRequest

class CommunicationProtocol(models.Model):
    """Existing communication protocols."""
    name = models.TextField(primary_key=True)
    initials = models.CharField(max_length=10)
    
    def __unicode__(self):
        return self.initials

class MimeType(models.Model):
    """Existing type of File."""
    extension = models.CharField(primary_key=True, max_length=8)
    name = models.CharField(max_length=32)
    
    def __unicode__(self):
        return self.name
    shortname = property(__unicode__)

class FileServer(models.Model):
    """Physical storage where a File could be stored."""
    label = models.CharField(max_length=16)
    protocol = models.ForeignKey(CommunicationProtocol, null=True, blank=True)
    ip_address = models.IPAddressField(default="127.0.0.1")
    port = models.PositiveIntegerField(null=True, blank=True)
    
    def get_url(self):
        """docstring needed"""
        url = ''
        if self.protocol and self.ip_address :
            url += "%s://%s%s/" % (self.protocol, self.ip_address, '' if not self.port else ":%s" % self.port)
        return url
    url = property(get_url) 
    
    def __unicode__(self):
        return self.url
    
    class Meta:
        ordering = ['protocol', 'ip_address', 'port']
        
class FileLocation(models.Model):
    """Path on a FileServer where a File is located."""
    server = models.ForeignKey(FileServer)
    root = models.TextField(null=True, blank=True)
    path = models.TextField()
    
    def get_path(self):
        """docstring needed"""
        st = ''
        if self.root :
            st += self.root + "/"
        st += self.path
        return st
    hdd_path = property(get_path)
    
    def get_url(self):
        """docstring needed"""
        url = self.server.url + self.hdd_path
        return url
    url = property(get_url) 
    
    def __unicode__(self):
        return self.url
    
    class Meta:
        ordering = ['server', 'root', 'path']

class File(models.Model) :
    """File containing data."""
    name = models.TextField()
    location = models.ForeignKey(FileLocation, null=True) 
    mimetype = models.ForeignKey(MimeType, null=True)
    original = models.NullBooleanField(null=True, blank=True)
    notes = models.TextField(null=True, blank=True)
    permissions = generic.GenericRelation(IntegerPermission, content_type_field='content_type', object_id_field='object_id')
    ##requests = generic.GenericRelation(AccessRequest, content_type_field='content_type', object_id_field='object_id')

    def get_filename(self):
        """docstring needed"""
        st = self.name
        if self.mimetype :
            st += '.' + self.mimetype.extension
        return st
    filename = property(get_filename)
    
    def get_protocol(self):
        """docstring needed"""
        signals = self.signal_set.filter(protocol__isnull=False).distinct()
        if signals.count() :
            return signals[0].protocol
        else :
            return None
    protocol = property(get_protocol)
    
    def is_on_hdd(self):
        """docstring needed"""
        results = find_file(self.location.hdd_path, self.filename)
        return (len(results) == 1)
    
    def download_status_key(self, user):
        """docstring needed"""
        if self.is_on_hdd() :
            if is_downloadable_by(self, user) :
                return "all_formats"
            else :
                try :
                    request = self.requests.get(user=user)
                    status = request.get_state_display()
                    return  status if not status == 'accepted' else 'requested'
                except :
                    return None
        else :
            return "not_available"
    
    def get_all_file_formats(self):
        """docstring needed"""
        pattern = "%s.*" % self.name
        results = find_file(self.location.hdd_path, pattern)   
        if not results :
            return None
        else :
            formats = [k.split('.')[-1] for k in results]  
            return formats
    formats = property(get_all_file_formats)
    
    def get_protocols(self):
        """docstring needed"""
        protocols = self.signal_set.filter(channel__protocol__isnull=False).distinct()
        return protocols
    protocols = property(get_protocols)
    
    def get_protocols_by_type(self):
        """Store protocols relative to the block by protocol type."""
        protocols = {}
        for protocol in self.get_protocols() :
            name = protocol.protocol_type.label
            if not (name in protocols) :
                protocols[name] = []
            protocols[name].append(protocol)
        #transform each list of protocol into a QuerySet
        for protocol in protocols :
            protocols[protocol] = self.protocolrecording_set.model.objects.filter(pk__in=[k.pk for k in protocols[protocol]])
        return protocols
    
    def get_protocol_types(self):
        """Get all protocol types."""
        protocols = self.get_protocols_by_type().keys()
        return protocols
    distinct_protocols = property(get_protocols)
    
    def _protocols(self):
        """docstring needed"""
        protocols = self.get_protocols()
        return ','.join(protocols) if protocols else None
    protocol_names = property(_protocols)
    
    def get_path(self, format=None):
        """docstring needed"""
        if not format :
            extension = self.mimetype.extension
        else :
            extension = format
        return "%s/%s.%s" % (self.location.hdd_path, self.name, extension)
    hdd_path = property(get_path)
    
    def is_available_as(self, format):
        """docstring needed"""
        formats = self.formats
        return format.lower() in formats
    
    def __unicode__(self):
        return self.filename
    
    class Meta:
        ordering = ['name', 'mimetype']
