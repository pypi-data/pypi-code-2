import traceback
from wsgiref.simple_server import make_server

import run_task

def simple_app(environ, start_response):

    input = environ['wsgi.input']
    content = input.read(int(environ['CONTENT_LENGTH']))
    try:
        response = run_task.dispatch(content, environ['PATH_INFO'])
        status = '200 OK'
        headers = [('Content-type', 'application/json')]
    except Exception:
        traceback.print_exc()
        status = "501 ERROR"
        headers = []
        response = ""

    start_response(status, headers)
    return [response]

httpd = make_server('', 8000, simple_app)
print "Serving on port 8000..."
httpd.serve_forever()
