from base64 import b64encode
from hashlib import md5
import httplib
from logging import getLogger
from urlparse import urlparse

from lxml import etree



log = getLogger('dspace.sword.service')

class SwordService(object):
    """ SwordService provides basic interaction with the DSPace implementation 
    of the SWORD protocol v. 1.3 """
    
    def __init__(self, base_url, service_path='sword/servicedocument',
                 deposit_path='sword/deposit', user=None, password=None,
                 on_behalf_of=None):
        
        self.service_path = service_path
        self.deposit_path = deposit_path
        self.on_behalf_of = on_behalf_of
        self._connection = None
        self._base = urlparse(base_url)
        
        assert self._base[0] in ('http', 'https', )
        
        if self._base.username is not None and user is None:
            user = self._base.username
        if self._base.password is not None and password is None:
            password = self._base.password
        
        if user is not None and password is not None:
            log.debug('Authentication information provided to SwordService: '
                      'user=%s, password=%s' % (user, '*' * len(password),))
            self.auth = b64encode('%s:%s' % (user, password,))
    
    def __del__(self):
        if self._connection is not None:
            try:
                self._connection.close()
            except:
                pass
    
    @property
    def _service_url(self):
        """ Get the service document url """
        return '/'.join((self._base[2].rstrip('/'),
                         self.service_path.lstrip('/'),))
    
    def _deposit_url(self, handle):
        """ Get the deposit url for a handle """
        return '/'.join((self._base[2].rstrip('/'),
                         self.deposit_path.lstrip('/'),
                         str(handle).strip('/'),))
    
    @property
    def connection(self):
        if self._connection is None:
            args = {'host': self._base.hostname}
            if self._base.port is not None:
                args['port'] = self._base.port
            
            if self._base[0] == 'http':
                self._connection = httplib.HTTPConnection(**args)
            else:
                self._connection = httplib.HTTPSConnection(**args)
        
        return self._connection
    
    def _headers(self, **kwargs):
        headers = {}
        
        if 'on_behalf_of' in kwargs:
            if kwargs['on_behalf_of'] is not None:
                headers['X-On-Behalf-Of'] = kwargs['on_behalf_of']
        elif self.on_behalf_of:
            headers['X-On-Behalf-Of'] = self.on_behalf_of
        
        if 'no_op' in kwargs and kwargs['no_op'] is not None:
            headers['X-No-Op'] = str(kwargs['no_op']).lower()
        
        if 'verbose' in kwargs:
            headers['X-Verbose'] = str(kwargs['verbose']).lower()
        
        if self.auth: 
            headers['Authorization'] = 'Basic %s' % (self.auth,)
        
        headers['User-Agent'] = 'PythonDSpace/2.0'
        
        return headers
    
    def get_service_document(self, **kwargs):
        """ blah """
        self.connection.request('GET', self._service_url,
                                headers=self._headers(**kwargs))
        resp = self.connection.getresponse()
        
        print resp.status
        
        if resp.status != 200:
            raise Exception('Unable to retrieve the service document: %s' % (resp.reason,))
        
        return resp.read()
    
    def deposit(self, handle, data,
                packaging='http://purl.org/net/sword-types/METSDSpaceSIP',
                content_type='application/zip', **kwargs):
        headers = self._headers(**kwargs)
        headers['X-Packaging'] = packaging
        headers['Content-Type'] = content_type
        try:
            data_hash = md5()
            if hasattr(data,'seek'):
                data.seek(0)
                while True:
                    chunk = data.read(4096)
                    if len(chunk) == 0:
                        break
                    data_hash.update(chunk)
                data.seek(0)
            else:
                data_hash.update(data)
            headers['Content-MD5'] = data_hash.hexdigest()
        except Exception:
            log.warning('Unable to calculate the MD5 hash of upload data')
        
        self.connection.request('POST', self._deposit_url(handle), data,
                                headers)
        
        resp = self.connection.getresponse()
        
        if resp.status != 201:
            log.error('Unexpected response when depositing: %d %s\n%s' % 
                      (resp.status, resp.reason, resp.read()))
            raise Exception('Unable to deposit the data: %s' % (resp.reason,))
        
        try:
            parsed = etree.parse(resp)
        except Exception:
            log.exception('Error parsing the deposit response')
            return None
        
        handle = parsed.find('{http://www.w3.org/2005/Atom}id')
        if handle is None:
            log.error('Unable to find an atom:id in the resposne for a deposit')
            return None
        
        return urlparse(handle.text)[2].lstrip('/')
