from logging import getLogger

from zope.interface import implements

from Products.PluggableAuthService.PluggableAuthService import _SWALLOWABLE_PLUGIN_EXCEPTIONS, DumbHTTPExtractor
from Products.PluggableAuthService.interfaces.plugins import IExtractionPlugin

from collective.gsa.interfaces import ICredentialsExtractor

logger = getLogger('collective.gsa.extractor')

class CredentialsExtractor(object):
    
    implements(ICredentialsExtractor)
    
    def __init__(self, context, request = None):
        self.context = context
        self.request = request

    def extractCredentials(self):
        plugins = self.context.plugins
        
        try:
            extractors = plugins.listPlugins( IExtractionPlugin )
        except _SWALLOWABLE_PLUGIN_EXCEPTIONS:
            logger.debug('Extractor plugin listing error', exc_info=True)
            extractors = ()

        if not extractors:
            extractors = ( ( 'default', DumbHTTPExtractor() ), )
        
        for extractor_id, extractor in extractors:

            try:
                credentials = extractor.extractCredentials( self.request )
            except _SWALLOWABLE_PLUGIN_EXCEPTIONS:
                logger.debug( 'ExtractionPlugin %s error' % extractor_id
                            , exc_info=True
                            )
                continue
            logger.debug(credentials)
            if credentials and credentials.get('password'):
                return credentials
