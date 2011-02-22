import httplib2
import urlparse
import logging
try:
    import json
except ImportError:
    import simplejson as json

class SyncError(Exception):
    """Sync error
    
    """

class BadJSONResponse(SyncError):
    """The response is not JSON
    
    """

class SyncAPI(object):
    
    def __init__(self, url, username=None, password=None, logger=None):
        self.logger = logger
        if self.logger is None:
            self.logger = logging.getLogger(__name__)
        self.url = url
        self.http = httplib2.Http()
        if username:
            self.http.add_credentials(username, password)
        
    def _request(self, path, method, headers=None, body=None):
        """Send a request
        
        """
        url = urlparse.urljoin(self.url, path)
        self.logger.debug('Sending a request to %s, method=%s, headers=%s ...', 
                          url, method, headers)
        resp, content = self.http.request(url, method=method, body=body, 
                                          headers=headers)
        self.logger.debug('Response: %r', resp)
        self.logger.debug('Content: %r', content)
        if resp.status != 200:
            raise SyncError(resp.status, resp.reason)
        try:
            result = json.loads(content)
        except ValueError:
            raise BadJSONResponse('Bad JSON response')
        return result
    
    def signature(self, path):
        """Get signature of a remote file
        
        """
        self.logger.debug('Getting signature of %s ...', path)
        try:
            result = self._request('signature/'+path, 'GET')
        except SyncError, e:
            if e.args[0] == 404:
                return None
            raise
        sig = result['data']
        self.logger.info('Got signature %s of %s ', sig, path)
        return sig
        
    def put(self, content, path):
        """Put a local file to remote server
        
        """
        self.logger.debug('Putting %d bytes %s ...', len(content), path)
        result = self._request('put/'+path, 'POST', body=content)
        self.logger.info('Put file to %s', path)
        return result
    
    def delete(self, path):
        """Delete a remote file
        
        """
        self.logger.debug('Deleting file %s ...', path)
        result = self._request('delete/'+path, 'POST')
        self.logger.info('%s was deleted', path)
        return result
    
    def files(self):
        """Get file map
        
        """
        self.logger.debug('Getting file map ...')
        result = self._request('files', 'GET')
        files = result['data']
        self.logger.info('Got file map %s ', files)
        return files
        
if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    api = SyncAPI('http://127.0.0.1:5000/api/')
    api.sync(999, 'test', 'a/b/c.txt')
