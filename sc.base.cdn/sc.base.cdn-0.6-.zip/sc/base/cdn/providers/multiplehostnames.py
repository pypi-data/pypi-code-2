from zope.interface import implements
from random import choice
from sc.base.cdn.interfaces import ICDNProvider


class cdn(object):
    
    implements(ICDNProvider)
    
    
    def __init__(self,hostname=[],port=80,path='', per_registry=False):
        ''' Initialize
        '''
        self.hostname = hostname
        self.port = port
        self.path = path
        self.per_registry = per_registry
        
    def process_url(self,url):
        '''Given a base url we return an url pointing to 
           the hostname and path informed
           >>> obj = cdn()
           >>> obj.hostname = ['foo','bar',]
           >>> obj.port = 80
           >>> obj.path = ''
           >>> url = obj.process_url('http://nohost/plone/')
           >>> assert (url in ['http://foo/plone/', 'http://bar/plone/',])
           >>> url = obj.process_url('http://nohost:80/plone/')
           >>> assert (url in ['http://foo/plone/','http://bar/plone/'])
           >>> url = obj.process_url('http://nohost:8080/plone/')
           >>> assert (url in ['http://foo/plone/','http://bar/plone/'])
           >>> obj = cdn()
           >>> obj.hostname = ['bar',]
           >>> obj.port = 80
           >>> obj.path = 'somelongpath'
           >>> assert obj.process_url('http://nohost/plone/') == 'http://bar/somelongpath/plone/'
           >>> assert obj.process_url('http://nohost:80/plone/') == 'http://bar/somelongpath/plone/'
           >>> assert obj.process_url('http://nohost/plone/') == 'http://bar/somelongpath/plone/'
           >>> obj = cdn()
           >>> obj.hostname = ['foobar','barfoo',]
           >>> obj.port = 8080
           >>> obj.path = 'shrtpth'
           >>> url = obj.process_url('http://nohost/plone/')
           >>> assert (url in ['http://foobar:8080/shrtpth/plone/','http://barfoo:8080/shrtpth/plone/',])
           >>> url = obj.process_url('http://nohost:80/plone/')
           >>> assert (url in ['http://foobar:8080/shrtpth/plone/','http://barfoo:8080/shrtpth/plone/',])
           >>> url = obj.process_url('http://nohost/plone/')
           >>> assert (url in ['http://foobar:8080/shrtpth/plone/','http://barfoo:8080/shrtpth/plone/',])
        '''
        # splits url parts
        protocol,path = url.split('://')
        path = path.split('/')
        hostname = self.hostname
        if not isinstance(hostname,(list,tuple)):
            hostname = [hostname,]
        hostname = choice(hostname)
        if not self.port in [80,]:
            hostname = '%s:%s' % (hostname, self.port)
        
        path[0] = hostname
        # add path, if supplied
        if self.path:
            path.insert(1,self.path)
        
        # join everything
        path = '/'.join(path)
        url = '%s://%s' % (protocol, path)
        return url