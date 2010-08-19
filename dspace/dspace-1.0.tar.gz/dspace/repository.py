from urlparse import urlparse

from oaipmh.client import Client
from oaipmh.metadata import MetadataRegistry
from dspace.metadata import dspace_mets_reader


class Repository(object):
    def __init__(self, url, **kwargs):
        """ The url should be the full url base for the OAI-PMH repository """
        registry = MetadataRegistry()
        registry.registerReader('mets',dspace_mets_reader)
        kwargs.setdefault('metadata_registry', registry)
        self.oai = Client(url, **kwargs)
        self.identifier_base = self._extractIdentifierBase(url)
    
    def _extractIdentifierBase(self, url):
        return urlparse(url).hostname
    
    def _extractSet(self, handle):
        if not isinstance(handle, basestring):
            raise ValueError('Collection handles must be strings')
        return 'hdl_' + handle.replace('/','_').replace(':','_')
    
    def getName(self):
        return self.oai.identify().repositoryName()
    
    def getCollections(self):
        return map(lambda c: c[0:2], self.oai.listSets())
    
    def getItemHandles(self, collection=None, **kw):
        for item in self.getItemIdentifiers(collection=collection, **kw):
            yield item.identifier().split(':',2)[2]
    
    def getItemIdentifiers(self, collection=None, **kw):
        kw.setdefault('metadataPrefix', 'mets')
        
        if collection:
            kw['set'] = self._extractSet(collection)
        
        return self.oai.listIdentifiers(**kw)
    
    def getItems(self, collection=None, **kw):
        kw.setdefault('metadataPrefix','mets')
        
        if collection:
            kw['set'] = self._extractSet(collection)
        
        return self.oai.listRecords(**kw)
    
    def getItem(self, handle=None, identifier=None, **kwargs):
        kwargs.setdefault('metadataPrefix','mets')
        
        if handle is None and identifier is None:
            raise ValueError('Either handle or identifier must be provided')
        
        if handle is not None:
            if identifier is not None:
                raise ValueError('Either a handle or identifier must be provided, not both')
            
            identifier = 'oai:%s:%s' % (self.identifier_base, handle,)
        
        return self.oai.getRecord(identifier=identifier, **kwargs)
    
        
        