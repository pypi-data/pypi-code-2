##
## utility methods for wsgi 
##
##

import sys

from org.python.core.util import FileUtil
from StringIO import StringIO

from gefr import gefr_version

def get_default_environ(is_ssl=False):
    environ = {}
    environ['wsgi.version'] = (1,0)
    environ['wsgi.url_scheme'] = 'https' if is_ssl else 'http'
    environ['wsgi.multithread'] = True
    environ['wsgi.multiprocess'] = False
    environ['wsgi.run_once'] = False
    environ['wsgi.errors'] = sys.stderr
    return environ
    
def get_environ_from_servlet_request(request):
    environ = get_default_environ()
        
    environ['REQUEST_METHOD'] = request.getMethod()
    environ['SCRIPT_NAME'] = ''
    environ['PATH_INFO'] = request.getRequestURI()
    environ['QUERY_STRING'] = request.getQueryString() or ''
    environ['CONTENT_TYPE'] = request.getHeader('Content-Type')
    environ['CONTENT_LENGTH'] = int(request.getHeader('Content-Length') or 0)
    environ['SERVER_NAME'] = request.getLocalName()
    environ['SERVER_PORT'] = str(request.getLocalPort())
    environ['REMOTE_ADDR'] = request.getRemoteHost()
    environ['SERVER_PROTOCOL'] = 'http'
    environ['wsgi.input'] = FileUtil.wrap(request.getInputStream())

    for header in request.getHeaderNames():
        environ['HTTP_'+header.replace('-','_')] = request.getHeader(header)

    return environ

def header_dict_to_environ(headers, environ={}):
    for key,val in headers.items():
        environ['HTTP_'+key.replace('-','_')] = val

def get_response(start_response, body, environ):
    status = start_response.status
    message = start_response.message

    output = ''.join(body)
    output = unicode(output, encoding='utf8')

    first_line = " ".join(["HTTP/1.1", status, message])

    headers = start_response.headers
    headers['Server'] = "gefr-%s/%s" % (environ['gefr.backend'], gefr_version)

    if "HTTP_Connection" in environ:
        headers['Connection'] = environ['HTTP_Connection']

    content_length = len(output)
    headers["Content-Length"] = str(content_length)
    header_lines = "\r\n".join([''.join([k,": ",headers[k]]) for k in headers.keys()])
    results = "\r\n".join([first_line, header_lines, '', output])
    return results

