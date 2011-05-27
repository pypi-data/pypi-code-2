import urllib2
import urllib
from copy import copy
import yaml

class PyHole(object):
    def __init__(self, url, path=[], params={}, user_agent="PyHole", timeout=10, opener=None, force_slash=False):
        self.url = url
        self.params = params
        self.path = path
        self.user_agent = user_agent
        self.headers = { 'User-Agent' : self.user_agent }
        self.timeout = timeout
        self.force_slash = force_slash
        if self.force_slash:
            self.trailing_slash = '/'
        else:
            self.trailing_slash = ''
        
        if opener is None:
            self.opener = urllib2.build_opener( urllib2.HTTPCookieProcessor() )
        else:
            self.opener = opener

    def _copy(self):
        return PyHole(  url = copy(self.url), 
                        path=copy(self.path), 
                        params=copy(self.params), 
                        user_agent = copy(self.user_agent), 
                        timeout = self.timeout, 
                        opener=self.opener,
                        force_slash=self.force_slash,
                )
    # Lazy URL building
    
    def __getattr__(self, name):
        """ Build url by attribute
            proxy = PyHole(url='http://domain.ltd/')
            print proxy.some
            http://domain.ltd/some/
            
        """
        copy = self._copy()
        copy.path.append(name)
        return copy

    def __call__(self, *args, **kwargs):
        copy = self._copy()
        copy.params.update(kwargs)
        for arg in args:
            if type(arg) is dict:
                copy.params.update(arg)
            else:
                copy.path.append(arg)
        
        return copy

    def __getitem__(self, item):
        copy = self._copy()
        copy.path.append(item)
        return copy
    
    # Creating URL

    def __makeurl__ (self):
        return self.url + ('/' if self.path and self.url[-1] != '/' else '' ) + '/'.join(map(lambda x: urllib2.quote(str(x), '~'), self.path)) + ('' if not self.path and self.url[-1] == '/' else self.trailing_slash) + ('?' + urllib.urlencode(self.params.items()) if self.params else '')
        
    
    
    # Making HTTP Post or Get
    def get(self):
        return self.__connect__(urllib2.Request(self.__makeurl__(), headers=self.headers))


    def post(self, data={}):
        return self.__connect__(urllib2.Request(self.__makeurl__(), data=urllib.urlencode(data), headers=self.headers))

    def yget(self):
        """ HTTP GET and load yaml content """
        return yaml.load(self.get())

    def ypost(self, *args, **kwargs):
        """ HTTP POST and load yaml content """
        return yaml.load(self.post(*args, **kwargs))

    # Connection layer
    def __connect__(self, request):
        result = self.opener.open(request)#,  timeout=self.timeout)
        body = result.read()
        result.close()
        return body
        
    # Conversion to string
    def __str__(self):
        return self.__makeurl__().encode('ascii')

    def __unicode__(self):
        return self.__makeurl__()
