try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

from django.http import HttpResponse, QueryDict
from django.utils.datastructures import MultiValueDict

from fromagerie.parser import DistutilsMultiPartParser

def parse_post_and_files(request):
    """
    Parse broken distutils multipart/form-data POST content.
    """
    POST, FILES =  QueryDict(''), MultiValueDict()
    if request.META.get('CONTENT_TYPE', '').startswith('multipart'):

        # This is ugly, but it seems to be the only way to avoid reading
        # the request body into memory
        if hasattr(request, '_req'):
            request_body = request._req
        elif hasattr(request, 'environ') and 'wsgi.input' in request.environ:
            request_body = request.environ['wsgi.input']
        else:
            request_body = StringIO(request.raw_post_data)
            
        try:
            parser = DistutilsMultiPartParser(request.META,
                                              request_body,
                                              request.upload_handlers,
                                              request._encoding)
            POST, FILES = parser.parse()
        except:
            pass
    return POST, FILES



class HttpResponseUnauthorized(HttpResponse):
    status_code = 401

    def __init__(self, content="Authorization Required", *args, **kwargs):
        super(HttpResponseUnauthorized, self).__init__(content, *args, **kwargs)

class HttpResponseNotImplemented(HttpResponse):
    status_code = 501
