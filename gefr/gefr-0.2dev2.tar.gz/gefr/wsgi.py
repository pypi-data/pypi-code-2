##
## utility methods for wsgi 
##
##

from StringIO import StringIO

from gefr import gefr_version

def get_default_environ(is_ssl=False):
    environ = {}
    environ['wsgi.version'] = (1,0)
    environ['wsgi.url_scheme'] = 'https' if is_ssl else 'http'
    environ['wsgi.multithread'] = True
    environ['wsgi.multiprocess'] = False
    environ['wsgi.run_once'] = False
    environ['wsgi.errors'] = StringIO()
    return environ

def header_dict_to_environ(headers, environ={}):
    for key,val in headers.items():
        environ['HTTP_'+key.replace('-','_')] = val
    
def get_response(start_response, body, environ):
    status = start_response.status
    message = start_response.message

    output = ''.join(body) if int(status) < 500 else environ['wsgi.errors'].getvalue()
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

