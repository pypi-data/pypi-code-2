import logging
from pipestack.pipe import MarblePipe, Marble

log = logging.getLogger(__name__)

class HeaderList(list):
    pass

class HTTPResponseMarble(Marble):
    def __init__(self, *k, **p):
        self.__dict__['status'] = u'200 OK'
        self.__dict__['status_format'] = u'unicode'
        self.__dict__['header_list'] = HeaderList([dict(name=u'Content-Type', value=u'text/html; charset=utf8')])
        self.__dict__['header_list_format'] = u'unicode'
        self.__dict__['body'] = []
        self.__dict__['body_format'] = u'unicode'
        Marble.__init__(self, *k, **p)

    def __setattr__(self, name, value):
        if name not in self.__dict__:
            raise AttributeError('No such attribute %s'%name)
        Marble.__setattr__(self, name, value)

class HTTPResponsePipe(MarblePipe):
    marble_class = HTTPResponseMarble

def encode_status(response):
    "Return the status as a bytes object"
    if response.status_format == u'unicode':
        return response.status.encode('ascii')
    else:
        return response.status

def encode_header_list(response):
    "Return the result of calling ``as_list()`` on the object specified in ``header_list``"
    if response.header_list_format != u'unicode':
        return list(response.header_list)
    else:
        header_list = list(response.header_list)
        final = []
        for header_record in header_list:
            final.append(dict(name=header_record['name'].encode('ascii'), value=header_record['value'].encode('ascii')))
        return final

def body_stream_generator(response):
    "Iterate over the object stored in ``body``, encoding results as necessary based on the format in ``body_format``."
    if response.body_format == u'unicode':
        encoding = None
        found = False
        for header_record in response.header_list:
            if header_record['name'].lower() == 'content-type':
                parts = header_record['value'].split(';')
                if len(parts) == 2:
                    charset = parts[1].strip().lower().split('charset')
                    if len(charset) == 2:
                        if found:
                            raise Exception("More than one HTTP header specifies the charset")
                        else:
                            encoding = charset[1].strip().strip('=').split(' ')[0]
                            found = False
        if encoding is None:
            log.info("No `Content-Type' header found with a `charset' specified, using UTF8")
            encoding = 'utf8'
        for data in response.body:
            yield data.encode(encoding)
    else:
        for data in response.body:
            yield data
     

