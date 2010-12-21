# -*- coding: iso-8859-15 -*-
# (c) Mikael Högqvist

import httplib2, simplejson, os, socket
from urlparse import urljoin, urlunparse, urlparse

class NotFound(Exception): pass
class Unauthorized(Exception): pass
class BadRequest(Exception): pass
class MethodNotAllowed(Exception): pass
class Conflict(Exception): pass
class InternalServerError(Exception): pass

exception_map = {
'400': BadRequest,
'401': Unauthorized,
'404': NotFound,
'405': MethodNotAllowed,
'409': Conflict,
'500': InternalServerError
}

# TODO: implement support for different authentication, authorization-schemes
# TODO: add support for caching with etags from httplib2
class Client(object):
    def __init__(self, service_url, base_path=None, user=None, password=None, key=None, cert=None):
        self.service_url = service_url
        self.__base_path = base_path

        self.__cache_path = ''
        self.__cookie_path = ''
        self.__cached_cookie = None

        self.__user = user
        self.__password = password

        # must be absolute paths
        self.__key = key
        self.__cert = cert
        
        # Indicates if we store cookies/cache on disk between instances
        self.__persistence = False

        if self.__base_path:
            if not os.path.exists(self.__base_path):
                os.mkdir(self.__base_path)
            
            cache_path = os.path.join(self.__base_path, 'cache')
            
            if not os.path.exists(cache_path):
                os.mkdir(cache_path)
            
            self.__cache_path = cache_path
            
            self.__cookie_path = os.path.join(self.__base_path, 'cookie.txt')
            self._read_cookie()
            self.__persistence = True

    def _read_cookie(self):
        if self.__cached_cookie:
            return self.__cached_cookie
        
        if self.__persistence and os.path.exists(self.__cookie_path):
            f = file(self.__cookie_path)
            self.__cached_cookie = self._file_like_to_string(f)
            f.close()    
            return self.__cached_cookie
        
        # cookie is empty
        return ''
        
    def _write_cookie(self, cookie):
        if self.__persistence:
            f = file(self.__cookie_path, 'w')
            f.write(cookie)
            f.close()
        
        self.__cached_cookie = cookie

    def _file_like_to_string(self, f):
        return ''.join(l for l in f)

    def _request_url(self, resource):
        url = urlparse(resource)
        # if the resource has a net location already, it overrides
        # the internal service url
        if not url.netloc == '':
            return resource
        
        # otherwise we assume that the resource is relative to the
        # service url. Note that it can contain a path part.
        service_url = urlparse(self.service_url)
        
        res_path = url.path
        if url.path.startswith('/'):
            res_path = url.path[1:]
        
        return urlunparse((service_url.scheme, service_url.netloc,
                           urljoin(service_url.path, res_path),
                           url.params, url.query, url.fragment))
        
        
        
    def request(self, resource, body=None, method='GET', headers={}):
        h = httplib2.Http(self.__cache_path)
        # dont follow redirects, this is done by the implementor
        h.follow_redirects = False
        
        cookie = self._read_cookie()
        if cookie:
            headers['cookie'] = cookie
        
        if self.__user and self.__password:
            h.add_credentials(self.__user, self.__password)

        if self.__key and self.__cert:
            h.add_certificate(self.__key, self.__cert, "")

        #headers['Cookie'] = self._read_cookie()
        
        # this is probably a file-like object and no string
        # since httplib2 does not yet support streaming, read this into a string
        if body and hasattr(body, 'read'):
            body = self._file_like_to_string(body)
        
        # if the given resource is relative, use the known
        # service url to construct the full resource.
        resource = self._request_url(resource)
        
        try:
            stat, resp = h.request(resource, method, body=body, headers=headers)

            if stat['status'][0] == '4':
                raise exception_map[stat['status']](resp)
            
            try:
                cookie = stat['set-cookie']
                self._write_cookie(cookie)
            # just ignore if no cookie is given    
            except KeyError, e:
                pass
                
            return stat, resp
        except socket.error, e:
            raise
        except Exception, e:
            # TODO: handle this appropriately
            print "exception: ", str(e)
            raise
            
    def get(self, resource, headers={}):
        return self.request(resource)
    
    def post(self, resource, data, headers={}):
        return self.request(resource, body=data, method='POST', headers=headers) 
    
    # TODO: use the 'lost update' implementation from httplib2
    def put(self, resource, data, headers={}):
        return self.request(resource, body=data, method='PUT', headers=headers)
    
    def delete(self, resource, headers={}):
        return self.request(resource, method='DELETE', headers=headers)

class CollectionClient(object):
    """
    The client counterpart to the WSGI-collection. Implements the basic 
    collection methods such as retrieve, list, create, update and delete.
    The methods take care of error handling, but leaves handling of 
    content to the class inheriting the ``CollectionClient`.
    """

    def __init__(self, client, prefix='/'):
        """
        Creates a new CollectionClient

        ``client`` - A ``benri.client.Client`` that will be used to access the
                     collection
        ``prefix`` - indicates the path to the collection which the client will
                     operate on. Ex: http://example.org:10101/entries/
        """
        self._client = client
        self._prefix = prefix
        self._resource_url = urljoin(self._client.service_url, self._prefix)
        
    def _resource(self, path='', noun='', query_string=''):
        if path and path[0] == '/':
            path = path[1:]
        
        r = urljoin(self._resource_url, path)
        return r + urlunparse(('','','',noun,query_string,''))

    def members(self, accepts='text/plain'):
        """
        Retrieves a list of all members in the collection.
        
        ``accepts`` - the string passed as part of the accept header to be used
                       for content negotiation.
        """
        headers = {'Accept': accepts}
        return self._client.get(self._resource(), headers=headers)
        
    def create(self, data, name='', query_string='', mimetype='text/plain'):
        """
        Creates a new entry in the collection.
        
        ``data`` - A file-like object with the data to pass to the server.
        ``name`` - Indicates the name of the entry in the collection. With an 
                   empty name, the server will generate a name.
        ``query_string`` - applied as '?<query_string>' to the request.                   
        ``mimetype`` - the content-type of the data, defaults to 'text/plain'.

        Returns full URL to the new entry on success. 
        """

        headers = {'Slug': name}
        headers['Content-Type'] = mimetype
        return self._client.post(self._resource(query_string=query_string), data, headers=headers)
        
    def retrieve(self, name, noun='', query_string='', accepts='text/plain'):
        """
        Retrives the content related to name. Raises ``NotFound`` with the
        returned content as body if the entry is not found. The return value
        is a string.
        
        ``name`` - The name of the entry in the collection.
        ``noun`` - modifier applied as ';<noun>' to the request. 
        ``query_string`` - applied as '?<query_string>' to the request.
        ``accepts`` - the string passed as part of the accept header to be used
                      for content negotiation.
        """
        return self._client.get(self._resource(path=name, noun=noun, query_string=query_string))

    def update(self, name, data, noun='', query_string='', mimetype='text/plain'):
        """
        Updates the entry with the given name and the data. Default is to 
        replace the entry with the data. Using noun it is possible to indicate
        different behaviour of the update.
        
        ``name`` - The name of the entry in the collection.
        ``data`` - A file-like object containing the data for the update.        
        ``noun`` - Can be used to indicate special behaviour of the update.
        ``query_string`` - applied as '?<query_string>' to the request.        
        ``mimetype`` - the content-type of the data, defaults to 'text/plain'.        
        """
        
        headers = {'Content-Type': mimetype}
        return self._client.put(self._resource(path=name, noun=noun, query_string=query_string), data, headers=headers)
        
    def delete(self, name):
        """
        Removes the named entry.
        
        ``name`` - The id of the entry to remove.
        
        Does not return anything on success. Raises either NotFound,
        or NotAuthorized on failure.
        """

        # use the request directly since otherwise this will call itself
        return self._client.request(self._resource(path=name), method='DELETE', headers={})

