from urlparse import urlparse
from warnings import warn

from oaipmh.client import Client
from oaipmh.metadata import MetadataRegistry

from dspace.metadata import dspace_mets_reader
from dspace.sword.service import SwordService


class Repository(object):
    """ Repository handles interaction with the various interfaces provided by 
    the dspace repository. """
    
    def __init__(self, url=None, **kwargs):
        self.base_url = kwargs.pop('base_url', None)
        self.oai_path = kwargs.pop('oai_path', None)
        
        self.oai_enabled = bool(kwargs.pop('oai_enabled', True))
        self.sword_enabled = bool(kwargs.pop('sword_enabled', False))
        
        if url is not None:
            warn('The url paramater will not be supported in version 3, '
                 'use base_url and oai_path instead', DeprecationWarning)
            
            if (self.base_url and url.startswith(self.base_url) and 
                self.oai_path is None):
                self.oai_path = url.replace(self.base_url, '', 1).lstrip('/')
            elif not self.base_url:
                if self.oai_path is None:
                    self.oai_path = 'dspace-oai/request'
                if url.endswith(self.oai_path):
                    self.base_url = url[:-(len(self.oai_path) + 1)]
        
        if self.base_url is None:
            raise ValueError('base_url argument must be specified')
        
        if not 'metadata_registry' in kwargs:
            kwargs['metadata_registry'] = MetadataRegistry()
            kwargs['metadata_registry'].registerReader('mets',
                                                       dspace_mets_reader)
        
        if self.sword_enabled:
            skwargs = {'base_url': self.base_url}
            
            for key in kwargs.keys():
                if key.startswith('sword_'):
                    skwargs[key[6:]] = kwargs.pop(key)
            
            self.sword = SwordService(**skwargs)
        
        if self.oai_enabled:
            self.oai = Client('/'.join((self.base_url, self.oai_path,)),
                              **kwargs)
        
        self.identifier_base = self._extractIdentifierBase(self.base_url)
    
    def _extractIdentifierBase(self, url):
        """ From a given URL, extract the OAI identifier base (hostname) """
        return urlparse(url).hostname
    
    def _extractSet(self, handle):
        """ Determine the OAI set from a collection handle """
        if not isinstance(handle, basestring):
            raise ValueError('Collection handles must be strings')
        return 'hdl_' + handle.replace('/','_').replace(':','_')
    
    def getName(self):
        """ Get the configured name of the repository """
        assert self.oai_enabled, 'Requires OAI-PMH to be enabled'
        return self.oai.identify().repositoryName()
    
    def getCollections(self):
        """ Get a list of the collections in the repository """
        assert self.oai_enabled, 'Requires OAI-PMH to be enabled'
        return map(lambda c: c[0:2], self.oai.listSets())
    
    def getItemHandles(self, collection=None, **kw):
        """ Get item handles from the OAI-PMH interface """
        assert self.oai_enabled, 'Requires OAI-PMH to be enabled'
        for item in self.getItemIdentifiers(collection=collection, **kw):
            yield item.identifier().split(':', 2)[2]
    
    def getItemIdentifiers(self, collection=None, **kw):
        """ Get item identifiers from the OAI-PMH interface """
        assert self.oai_enabled, 'Requires OAI-PMH to be enabled'
        kw.setdefault('metadataPrefix', 'mets')
        
        if collection:
            kw['set'] = self._extractSet(collection)
        
        return self.oai.listIdentifiers(**kw)
    
    def getItems(self, collection=None, **kw):
        """ Get full items from the OAI-PMH interface """
        assert self.oai_enabled, 'Requires OAI-PMH to be enabled'
        kw.setdefault('metadataPrefix','mets')
        
        if collection:
            kw['set'] = self._extractSet(collection)
        
        return self.oai.listRecords(**kw)
    
    def getItem(self, handle=None, identifier=None, **kwargs):
        """ Get a single item from the OAI-PMH interface either by handle or 
        identifier """
        assert self.oai_enabled, 'Requires OAI-PMH to be enabled'
        kwargs.setdefault('metadataPrefix','mets')
        
        if handle is None and identifier is None:
            raise ValueError('Either handle or identifier must be provided')
        
        if handle is not None:
            if identifier is not None:
                raise ValueError('Either a handle or identifier must be '
                                 'provided, not both')
            
            identifier = 'oai:%s:%s' % (self.identifier_base, handle,)
        
        return self.oai.getRecord(identifier=identifier, **kwargs)
    
    def getOAIItemIdentifier(self, handle):
        return 'oai:%s:%s' % (self._extractIdentifierBase(self.base_url),
                              handle)
    
    def getSwordCollections(self):
        pass
        
    def getSwordCollection(self, args):
        pass
    