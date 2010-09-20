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

def bshell(app):
    def action():
        """run shell use bpython
        """
        from bpython import embed
        embed({"app": app})
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
        }

    def add_action(self, name, action):
        self._actions[name] = action

    def run(self):
        script.run(self._actions, '')
