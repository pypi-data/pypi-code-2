import logging

log = logging.getLogger(__name__)

def wsgi_response_iterator(written, body):
    for data in written:
        yield data
    for data in body:
        yield data

class WSGIObject(object):
    def __init__(self, flow):
        self._flow = flow
        self._exc_info = None
        # start_response objects
        self._start_response_called = False
        self._data_written = False
        self._written = []

    def __setattr__(self, name, value):
        if name in ['headers', 'status', 'exc_info', 'response']:
            raise Exception('No such attribute %r'%name)
        elif name == 'result':
            self._flow.http.response.body = wsgi_response_iterator(
                self._written, 
                value
            )
        else:
            return object.__setattr__(self, name, value)

    def __getattr__(self, name):
        if name in ['headers', 'status', 'exc_info', 'response']:
            raise Exception('No such attribute %r'%name)
        elif name == 'result':
            return self._flow.http.response.body
        elif name == 'environ':
            environ = self._flow.http.environ
            if not environ.has_key('flows.flow'):
                environ['flows.flow'] = self._flow
            return environ
        else:
            return object.__getattr__(self, name)

    def write(self, data):
        if not self._data_written:
            self._data_written = True
        if not self._start_response_called:
            raise Exception(
                'You cannot write() until start_response() has been called'
            )
        if self._flow.http.response._result_returned:
            raise Exception(
                'The result has already been returned, you cannot write '
                'more data'
            )
        self._written.append(data)

    def start_response(self, status, headers, exc_info=None):
        if self._start_response_called and exc_info is None:
            raise Exception(
                'start_response() has already been called and no exc_info '
                'is present'
            )
        self._start_response_called = True
        if self._flow.http.response._result_returned:
            raise Exception('The result has already been returned')
        self._flow.http.response.status = status
        self._flow.http.response.headers = headers
        log.debug(
            'start_response() status: %r, headers: %r, exc_info: %r',
            status,
            headers,
            exc_info,
        )
        self._exc_info = exc_info
        return self.write


