# -*- coding: utf-8 -*-
"""
    flaskext.actions
    ~~~~~~~~~~~~~~~~~

    Description of the module goes here...

    :copyright: (c) 2010 by Young King.
    :license: BSD, see LICENSE for more details.
"""
import sys,os
from werkzeug import script
import utils

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
    def action(port=('p', 8000), reactor_type=('r', 0)):
        """run application use twisted http server
        :param reactor_type: [default 0]
                            0       default reactor
                            1       epoll   reactor
                            2       poll    reactor
                            3       kqueue  reactor
                            4       iocp    reactor
                            other   select  reactor
        """
        try:
            if reactor_type ==0:
                pass
            elif reactor_type == 1:
                from twisted.internet import epollreactor
                epollreactor.install()
            elif reactor_type == 2:
                from twisted.internet import pollreactor
                pollreactor.install()
            elif reactor_type == 3:
                from twisted.internet import kqreactor
                kqreactor.install()
            elif reactor_type == 4:
                from twisted.internet import iocpreactor
                iocpreactor.install()
            from twisted.internet import reactor
            from twisted.application import internet, service
            from twisted.web import server, wsgi
        except ImportError:
            print "You need to install twisted"
            sys.exit()
        from twisted.internet import reactor
        from twisted.application import internet, service
        from twisted.web import server, wsgi

        #application = service.Application('twisted-wsgi') # call this anything you like
        resource = wsgi.WSGIResource(reactor, reactor.getThreadPool(), app)
        factory = server.Site(resource)
        reactor.listenTCP(int(port),factory)
        reactor.run()

    return action


def bshell(app):
    def action():
        """run shell use bpython
        """
        from bpython import embed
        embed({"app": app})
    return action

def compile_pyc(app,use_verbose=True):
    def action(directory=('d','.'),verbose=use_verbose):
        """Compile all python files in the directory into bytecode files.
        """
        import py_compile 
        for root, dirs, files in os.walk(directory):
            for file in files:
                ext = os.path.splitext(file)[1]
                if ext==".py":
                    full_path = os.path.abspath(os.path.join(root, file))
                    if verbose:
                        print "%sc" % full_path
                    py_compile.compile(full_path)

    return action

def clean(app,use_pretend=True,use_verbose=True):
    def action(directory=('d','.'),extention=('e','.pyc'),pretend=use_pretend,verbose=use_verbose):
        """
        Clean the specify filename extention files from the directory.
        :param pretend: Instead  of  actually performing the clean,just print it
        """
        check = lambda s: s.endswith(extention)
        if pretend:
            print "The following files are supposed to be delete:"
        else:
            print "the following files are removed:"
        for dirpath, dirnames, filenames in os.walk(directory):
            for filename in filter(check, filenames):
                fullpath = os.path.abspath(os.path.join(dirpath, filename))
                if verbose:
                        print "%s" % fullpath
                if not pretend:
                    os.remove(fullpath)
    return action

def generate_secret_key(app):
    def action(length=('l',32)):
        """creates a new secret key"""
        print utils.generate_secret_key(length)
    return action


class Manager(object):
    def __init__(self, application):
        self.application = application
        self._actions = {
                'runfcgi'    :   runfcgi(application),
                'shell'     :   script.make_shell(lambda: {"app": application},
                                    "Interactive Flask Shell"),
                'runserver' :   script.make_runserver(lambda: application,
                                    use_reloader=True, threaded=True, hostname='0.0.0.0',
                                    port=7777, use_debugger=True),
                'bshell'    :   bshell(application),
                'compile_pyc' : compile_pyc(application),
                'clean'       : clean(application),
                'generate_secret_key':generate_secret_key(application),
                'runtwisted'  :   run_twisted_server(application),

        }

    def add_action(self, name, func):
        self._actions[name] = func(self.application)

    def run(self):
        script.run(self._actions, '')
