from bn import AttributeDict
from httpkit.service.response import body_stream_generator, HTTPResponseMarble, encode_header_list, encode_status 
from commandtool import Cmd

def wsgi_app_handler(app, enter_pipes, profile=False, aliases=None):
    """Start a server with the ``app``, ``host`` and ``port`` specified."""
    if aliases is None:
        aliases = dict()
    def wsgi_app(environ, start_response):
        new_bag = AttributeDict()
        new_bag[aliases.get('environ', 'environ')] = environ
        new_bag[aliases.get('http_response', 'http_response')] = HTTPResponseMarble(
            bag=new_bag, 
            name=aliases.get('http_response', 'http_response'), 
            config=app.config.get(aliases.get('http_response', 'http_response'), {}),
            persistent_state=None,
            flow_state=None,
            aliases=aliases
        )
        app.start_flow(new_bag, enter_pipes)
        start_response(
            encode_status(new_bag.http_response),
            [tuple([item['name'], item['value']]) for item in encode_header_list(new_bag.http_response)],
        )
        return body_stream_generator(new_bag.http_response)
    if profile:
        # pstats problems:
        # sudo apt-get install python-profiler
        #  ~/env/bin/easy_install repoze.profile
        from repoze.profile.profiler import AccumulatingProfileMiddleware
        wsgi_app = AccumulatingProfileMiddleware(
            wsgi_app,
            log_filename='profile.log',
            cachegrind_filename='profile.cachegrind',
            discard_first_request=True,
            flush_at_shutdown=True,
            path='/__profile__'
        )
    return wsgi_app

class ServeWSGI(Cmd):
    arg_spec = [
      # ('IP_AND_PORT', 'The IP and port to serve on, eg `127.0.0.1:8000\'')#('architecture', "can be `wsgi' or `tornado'"),
    ]
    # The option_spec specifies which options are associated with 
    # each internal variable
    option_spec = {
        'help': dict(
            options = ['-h', '--help'],
            help = 'display this message'
        ),
        'profile': dict(
            options = ['--profile'],
            help = 'enable profiling'
        ),
        'port': dict(
            options = ['-p', '--port'],
            help = 'set the port, default 8000',
            metavar='PORT'
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
        # Used in the main command help to describe this command
        'help_summary': 'Serve the application',
    }

    def on_run(self, app, args, opts):
        host = opts.get('host', '127.0.0.1')
        port = int(opts.get('port', '8000'))
        wsgi_app = wsgi_app_handler(app, app.default_pipeline, opts.profile)
        try:
            from paste.httpserver import serve
        except:
            from wsgiref.simple_server import make_server
            httpd = make_server(host, port, wsgi_app)
            print "Serving HTTP with wsgiref on http://%s:%s/"%(host, port)
            httpd.serve_forever()
        else:
            print "Serving HTTP with Paste"
            serve(wsgi_app, host, port)
        return 1

