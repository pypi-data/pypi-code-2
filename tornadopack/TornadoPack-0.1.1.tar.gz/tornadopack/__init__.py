"""\
Serve a PipeStack application using the async Tornado server

Example:

::

    import tornado.ioloop
    import time
    from pipestack.pipe import Pipe
    class Hello(Pipe):
        def enter(self, bag):
            def called():
                bag.http.request.write('Hello world! %s'%'James')
                tornado.ioloop.IOLoop.instance().add_timeout(time.time()+2, called)
                #bag.http.request.finish()
            tornado.ioloop.IOLoop.instance().add_timeout(time.time()+2, called)
            res = bag.mongo.posts.find_one({"author": "Mike"})['author']
            bag.http_response.body = None
"""

import StringIO
import logging
from bn import AttributeDict
from httpkit.service.response import body_stream_generator, HTTPResponseMarble, encode_header_list, encode_status 
from commandtool import Cmd

log = logging.getLogger(__name__)

environ_map = {
    'wsgi.url_scheme': 'protocol',
    'REQUEST_METHOD': 'method', 
    'PATH_INFO': 'uri', 
    'REMOTE_ADDR': 'remote_ip',
    'SERVER_PROTOCOL': 'version',
}

class LoggingEnviron(dict):
    def __getitem__(self, name):
        value = dict.__getitem__(self, name)
        log.debug('Retrieving %r with value %r', name, value)
        return value

def request2environ(request):
    new_environ = {
        'SCRIPT_NAME': '',
        'SERVER_PORT': len(request.host.split(':'))>1 and request.host.split(':')[1] or (request.protocol == 'http' and '80' or '443'),
    }
    for k, v in request.headers.items():
        new_environ['HTTP_'+(k.upper().replace('-', '_'))] = v
    for k, v in environ_map.items():
        new_environ[k] = getattr(request, v)
    if new_environ.has_key('HTTP_CONTENT_LENGTH'):
        new_environ['CONTENT_LENGTH'] = new_environ['HTTP_CONTENT_LENGTH']
    if new_environ.has_key('HTTP_CONTENT_TYPE'):
        new_environ['CONTENT_TYPE'] = new_environ['HTTP_CONTENT_TYPE']
    if request.body:
        new_environ['wsgi.input'] = StringIO.StringIO(request.body)
    if '?' in new_environ['PATH_INFO']:
        parts = new_environ['PATH_INFO'].split('?')
        new_environ['PATH_INFO'] = parts[0]
        new_environ['QUERY_STRING'] = '?'.join(parts[1:])
    return new_environ

class ServeTornado(Cmd):
    arg_spec = [
    ]
    # The option_spec specifies which options are associated with 
    # each internal variable
    option_spec = {
        'help': dict(
            options = ['-h', '--help'],
            help = 'display this message'
        ),
        'port': dict(
            options = ['-p', '--port'],
            help = 'set the port, default 8000',
            metavar='PORT'
        ),
        'reload': dict(
            options = ['--reload'],
            help = 'automatically reload the server when code changes',
        ),
        'host': dict(
            options = ['-H', '--host'],
            help = 'set the host, default 127.0.0.1. Use 0.0.0.0 for production',
            metavar='HOST',
        )
    }
    help = {
        # If you leave start and end as None, values will be 
        # automatically generated
        'start': None,
        'end': None,
        'summary': 'Serve the application using the tornado non-blocking server',
        # Used in the main command help to describe this command
    }

    def on_run(self, app, args, opts):
        tornado_handler(
            app,
            app.default_pipeline,
            host = opts.get('host', '127.0.0.1'),
            port = int(opts.get('port', '8000')),
            reload = opts.reload,
            aliases = self.aliases,
        )
        return 0

def tornado_handler(app, enter_pipes=[], host='', port=8000, profile=False, reload=False, aliases=None):
    if aliases is None:
        aliases = {}
    from tornado.httpserver import HTTPServer
    from tornado import ioloop
    if reload:
        from tornado import autoreload
        autoreload.start()
    def handle_request(request):
        new_bag = AttributeDict()
        new_bag[aliases.get('environ', 'environ')] = request2environ(request)
        new_bag[aliases.get('http_response', 'http_response')] = HTTPResponseMarble(
            bag=new_bag, 
            name=aliases.get('http_response', 'http_response'), 
            config=app.config.get(aliases.get('http_response', 'http_response'), {}),
            persistent_state=None,
            flow_state=None,
            aliases=aliases
        )
        new_bag[aliases.get('host', 'host')] = host
        new_bag[aliases.get('port', 'port')] = port
        new_bag[aliases.get('request', 'request')] = request
        app.start_flow(new_bag, enter_pipes)
        headers = ''
        for name, value in [tuple([item['name'], item['value']]) for item in encode_header_list(new_bag.http_response)]:
            headers += '%s: %s\r\n'%(name, value)
        head = "HTTP/1.1 %s\r\n%s\r\n" % (
            encode_status(new_bag.http_response),
            headers,
        )
        body = new_bag.http_response.body
        request.write(head)
        if body is not None:
            for data in body_stream_generator(new_bag.http_response):
                request.write(data)
            request.finish()
        else:
            # The app is on its own for finishing the request.
            pass
    http_server = HTTPServer(handle_request, no_keep_alive=True)
    print "Serving on http://%s:%s/"%(host, port)
    http_server.listen(port, address=host)
    print "Event loop started"
    ioloop.IOLoop.instance().start()

