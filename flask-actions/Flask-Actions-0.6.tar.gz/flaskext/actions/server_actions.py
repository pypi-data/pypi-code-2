# -*- coding: utf-8 -*-
"""
    flaskext.actions.server_actions
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""
import sys,os
from werkzeug import script

def runfcgi(application, before_daemon=None):
    def action( hostname            =   ('h', ''),
                port                =   ('p', 3001),
                protocol            =   'scgi',
                method              =   'threaded',
                children            =   20,
                daemonize           =   False,
                pidfile             =   '/var/run/flask.pid',
                workdir             =   '.',
                outlog              =   '/dev/null',
                errlog              =   '/dev/null',
                umask               =   022,
        ):
        """run application use flup
        you can choose these arguments:
        protocol :   scgi, fcgi or ajp
        method   :   threaded or fork
        children :   number of threads or processes"""
        if protocol not in ('scgi', 'fcgi', 'ajp'):
            sys.exit('invalid protocol: %s'%protocol)
        flup_module = 'server.%s'%protocol

        kw = {'maxSpare': children, 'minSpare': children}

        if protocol == 'scgi':
            kw['scriptName'] = '/'

        if method == 'threaded':
            kw['maxThreads'] = children
        elif method == 'fork':
            flup_module += '_fork'
            kw['maxChildren'] = children
        else:
            sys.exit('invalid method: %s'%method)

        try:
            WSGIServer = getattr(__import__('flup.' + flup_module, '', '', flup_module), 'WSGIServer')
        except ImportError:
            print "You need to install flup"
            sys.exit()

        if os.name!='posix' and outlog=='/dev/null':
            outlog = None
        if os.name!='posix' and errlog=='/dev/null':
            errlog = None

        if daemonize:
            from .daemonize import become_daemon
            become_daemon(workdir, outlog, errlog, umask)

        if daemonize and pidfile and os.name=='posix':
            try:
                fp = open(pidfile, 'w')
                fp.write("%d\n" % os.getpid())
                fp.close()
            except:
                pass

        if before_daemon is not None:
            before_daemon()

        WSGIServer(application, bindAddress=(hostname, port), **kw).run()

    return action

def run_twisted_server(app):
    def action(host=('h','127.0.0.1'),port=('p', 8000)):
        """run application use twisted http server
        """
        from twisted.web import server, wsgi
        from twisted.python.threadpool import ThreadPool
        from twisted.internet import reactor
        thread_pool = ThreadPool()
        thread_pool.start()
        reactor.addSystemEventTrigger('after', 'shutdown', thread_pool.stop)
        factory = server.Site(wsgi.WSGIResource(reactor, thread_pool, app))
        reactor.listenTCP(int(port), factory, interface=self.host)
        reactor.run()

    return action

def run_appengine_server(app):
    def action(host=('h','127.0.0.1'),port=('p', 8000)):
        """run application use appengine http server
        """
        from google.appengine.ext.webapp import util
        util.run_wsgi_app(app)
    return action

def run_gunicorn_server(app):
    def action(host=('h','127.0.0.1'),port=('p', 8000),workers=('w',4)):
        """run application use gunicorn http server
        """
        from gunicorn.arbiter import Arbiter
        from gunicorn.config import Config
        app.cfg = Config({'bind': "%s:%d" % (host, port), 'workers': workers})
        arbiter = Arbiter(app)
        arbiter.run()
    return action

def run_tornado_server(app):
    """run application use tornado http server
    """
    def action(port=('p', 8000)):
        import tornado.wsgi
        import tornado.httpserver
        import tornado.ioloop
        container = tornado.wsgi.WSGIContainer(app)
        server = tornado.httpserver.HTTPServer(container)
        server.listen(port=port)
        tornado.ioloop.IOLoop.instance().start()
    return action

def run_fapws_server(app):
    def action(host=('h','127.0.0.1'),port=('p', '8000')):
        """run application use fapws http server
        """
        import fapws._evwsgi as evwsgi
        from fapws import base
        evwsgi.start(host, port)
        evwsgi.set_base_module(base)
        evwsgi.wsgi_cb(('', app))
        evwsgi.run()
    return action

def run_meinheld_server(app):
    def action(host=('h','127.0.0.1'),port=('p', 8000)):
        """run application use Meinheld http server
        """
        from meinheld import server
        server.listen((host, port))
        server.run(app)
    return action

def run_cherrypy_server(app):
    def action(host=('h','127.0.0.1'),port=('p', 8000)):
        """run application use CherryPy http server
        """
        from cherrypy import wsgiserver
        server = wsgiserver.CherryPyWSGIServer((host, port), app)
        server.start()
    return action

def run_paste_server(app):
    def action(host=('h','127.0.0.1'),port=('p', '8000')):
        """run application use Paste http server
        """
        from paste import httpserver
        httpserver.serve(app, host=host, port=port)
    return action

def run_diesel_server(app):
    def action(host=('h','127.0.0.1'),port=('p', 8000)):
        """run application use diesel http server
        """
        from diesel.protocols.wsgi import WSGIApplication
        application = WSGIApplication(app, port=self.port)
        application.run()
    return action

def run_gevent_server(app):
    def action(host=('h','127.0.0.1'),port=('p', 8000)):
        """run application use gevent http server
        """
        from gevent import wsgi
        wsgi.WSGIServer((host, port), app).serve_forever()
    return action

def run_eventlet_server(app):
    def action(host=('h','127.0.0.1'),port=('p', 8000)):
        """run application use eventlet http server
        """
        from eventlet import wsgi, listen
        wsgi.server(listen((host, port)), app)
    return action

def run_eurasia_server(app):
    def action(hostname=('h', '0.0.0.0'), port=('p', 8000)):
        """run application use eurasia http server"""
        try:
            from eurasia import WSGIServer
        except ImportError:
            print "You need to install eurasia"
            sys.exit()
        server = WSGIServer(app, bindAddress=(hostname, port))
        server.run()
    return action

def run_rocket_server(app):
    def action(host=('h','127.0.0.1'),port=('p', 8000)):
        """run application use rocket http server
        """
        from rocket import Rocket
        server = Rocket((host, port), 'wsgi', { 'wsgi_app' : app })
        server.start()
    return action


server_actionnames = {
        'runfcgi':runfcgi,
        'runtwisted':run_twisted_server,
        'run_appengine':run_appengine_server,
        'run_gevent':run_gevent_server,
        'run_eventlet':run_eventlet_server,
        'run_gunicorn':run_gunicorn_server,
        'run_rocket':run_rocket_server,
        'run_eurasia':run_eurasia_server,
        'run_tornado':run_tornado_server,
        'run_fapws':run_fapws_server,
        'run_meinheld':run_meinheld_server,
        'run_cherrypy':run_cherrypy_server,
        'run_paste_server':run_paste_server,
        'run_diesel':run_diesel_server,
        }


