from bn import AttributeDict
from httpkit.helper.http import HTTPResponse
from basecmd import BaseServeCmd

def wsgi_handler(service, name=None, start_services=[], host='', port=8000, profile=False):
    app = wsgi_app_handler(service, start_services, profile)
    try:
        from paste.httpserver import serve
    except:
        from wsgiref.simple_server import make_server
        httpd = make_server(host, port, app)
        print "Serving HTTP with wsgiref on http://%s:%s/"%(host, port)
        httpd.serve_forever()
    else:
        print "Serving HTTP with Paste"
        serve(app, host, port)

def wsgi_app_handler(site, start_services, profile=False):
    """Start a server with the ``app``, ``host`` and ``port`` specified."""
    def app(environ, start_response):
        new_service = AttributeDict()
        new_service['http'] = AttributeDict(response=HTTPResponse(),environ= environ)
        site.start_flow(new_service, start_services)
        start_response(
            new_service.http.response.status,
            new_service.http.response.headers
        )
        return new_service.http.response.get_result()
    if profile:
        # pstats problems:
        # sudo apt-get install python-profiler
        #  ~/env/bin/easy_install repoze.profile
        from repoze.profile.profiler import AccumulatingProfileMiddleware
        app = AccumulatingProfileMiddleware(
            app,
            log_filename='profile.log',
            cachegrind_filename='profile.cachegrind',
            discard_first_request=True,
            flush_at_shutdown=True,
            path='/__profile__'
        )
    return app

def serveWsgi():
    return BaseServeCmd(
        wsgi_handler, 
        'Serve the application using a threaded WSGI server (paste.httpserver if possible, otherwise wsgiref)'
    )

# New naming
def ServeCmd():
    return serveWsgi()
ServeWsgi = ServeWSGI = ServeCmd
