from zope.interface import Interface

class ICDNProvider(Interface):
    '''Base for CDN Provider
    '''
    
    def process_url(url):
        '''
        '''