from Products.ResourceRegistries.tools.BaseRegistry import BaseRegistryTool
from Products.ResourceRegistries.tools.JSRegistry import JSRegistryTool
from Products.CMFPlone.utils import getToolByName
from interfaces import ICDNProvider
from zope.component import getUtility
from time import time
from plone.memoize import ram

def url_cache(fun, self, *args, **kw):
    path = '/'.join(self.getPhysicalPath())
    key = "%s-%s" % (path, time() // (60 * 5))
    return key

def absolute_url(self, relative=0):
    ''' Returns the patched absolute_url for the registry
    '''
    url = super(BaseRegistryTool, self).absolute_url(relative=relative)
    if not relative:
        url = self.cdnUrl(url)
    return url

@ram.cache(url_cache)
def cdnUrl(self,url):
    ''' Returns a props dict
    '''
    portal_properties = getToolByName(self, 'portal_properties')
    cdn_props = getattr(portal_properties,'cdn_properties',None)
    enabled = False
    if not (cdn_props and cdn_props.getProperty('enable_cdn',False)):
        return url
    
    provider_name = cdn_props.getProperty('cdn_provider','CoralCDN')
    p_hostname = cdn_props.getProperty('cdn_hostname','')
    p_port = cdn_props.getProperty('cdn_port',80)
    p_path = cdn_props.getProperty('cdn_path','')
    provider = getUtility(ICDNProvider,provider_name)(hostname=p_hostname,
                                                      port=p_port,
                                                      path=p_path)
    return provider.process_url(url)

@ram.cache(url_cache)
def cdnUrlJS(self,url):
    ''' Returns a props dict
    '''
    portal_properties = getToolByName(self, 'portal_properties')
    cdn_props = getattr(portal_properties,'cdn_properties',None)
    enabled = False
    if not (cdn_props and cdn_props.getProperty('enable_cdn',False) 
            and cdn_props.getProperty('enable_cdn_js',False)):
        return url
    
    return super(JSRegistryTool, self).cdnUrl(url)
    
def run():
    # Patch BaseRegistryTool.absolute_url
    setattr(BaseRegistryTool,'absolute_url_old', BaseRegistryTool.absolute_url)
    setattr(BaseRegistryTool,'cdnUrl',cdnUrl)
    setattr(JSRegistryTool,'cdnUrl',cdnUrlJS)
    setattr(BaseRegistryTool,'absolute_url', absolute_url)