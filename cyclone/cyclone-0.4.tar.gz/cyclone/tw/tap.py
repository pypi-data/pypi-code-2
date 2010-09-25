# Copyright (c) 2001-2010 Twisted Matrix Laboratories.
# See LICENSE for details.

"""
Support for creating a service which runs a web server.
"""

import os

# Twisted Imports
from cyclone.tw import server, static, twcgi, script, demo, distrib, wsgi
from twisted.internet import interfaces, reactor
from twisted.python import usage, reflect, threadpool
from twisted.spread import pb
from twisted.application import internet, service, strports


class Options(usage.Options):
    """
    Define the options accepted by the I{twistd web} plugin.
    """
    synopsis = "[web options]"

    optParameters = [["port", "p", None, "strports description of the port to "
                      "start the server on."],
                     ["logfile", "l", None, "Path to web CLF (Combined Log Format) log file."],
                     ["https", None, None, "Port to listen on for Secure HTTP."],
                     ["certificate", "c", "server.pem", "SSL certificate to use for HTTPS. "],
                     ["privkey", "k", "server.pem", "SSL certificate to use for HTTPS."],
                     ]

    optFlags = [["personal", "",
                 "Instead of generating a webserver, generate a "
                 "ResourcePublisher which listens on  the port given by "
                 "--port, or ~/%s " % (distrib.UserDirectory.userSocketName,) +
                 "if --port is not specified."],
                ["notracebacks", "n", "Do not display tracebacks in broken web pages. " +
                 "Displaying tracebacks to users may be security risk!"],
                ]

    zsh_actions = {"logfile" : "_files -g '*.log'", "certificate" : "_files -g '*.pem'",
                   "privkey" : "_files -g '*.pem'"}


    longdesc = """\
This starts a webserver.  If you specify no arguments, it will be a
demo webserver that has the Test class from cyclone.tw.demo in it."""

    def __init__(self):
        usage.Options.__init__(self)
        self['indexes'] = []
        self['root'] = None


    def opt_index(self, indexName):
        """
        Add the name of a file used to check for directory indexes.
        [default: index, index.html]
        """
        self['indexes'].append(indexName)

    opt_i = opt_index


    def opt_user(self):
        """
        Makes a server with ~/public_html and ~/.twistd-web-pb support for
        users.
        """
        self['root'] = distrib.UserDirectory()

    opt_u = opt_user


    def opt_path(self, path):
        """
        <path> is either a specific file or a directory to be set as the root
        of the web server. Use this if you have a directory full of HTML, cgi,
        php3, epy, or rpy files or any other files that you want to be served
        up raw.
        """
        def trp(*args, **kwargs):
            # Help avoid actually importing cyclone.tw.trp until it is really
            # needed.  This avoids getting a deprecation warning if you're not
            # using deprecated functionality.
            from cyclone.tw import trp
            return trp.ResourceUnpickler(*args, **kwargs)

        def php3(*args, **kwargs):
            # Help avoid actually importing cyclone.tw.twcgi.PHP3Script until
            # it is really needed. This avoids getting a deprecation warning if
            # you're not using deprecated functionality.
            from cyclone.tw.twcgi import PHP3Script
            return PHP3Script(*args, **kwargs)

        def php(*args, **kwargs):
            # Help avoid actually importing cyclone.tw.twcgi.PHPScript until it
            # is really needed. This avoids getting a deprecation warning if
            # you're not using deprecated functionality.
            from cyclone.tw.twcgi import PHPScript
            return PHPScript(*args, **kwargs)

        self['root'] = static.File(os.path.abspath(path))
        self['root'].processors = {
            '.cgi': twcgi.CGIScript,
            '.php3': php3,
            '.php': php,
            '.epy': script.PythonScript,
            '.rpy': script.ResourceScript,
            '.trp': trp,
            }


    def opt_processor(self, proc):
        """
        `ext=class' where `class' is added as a Processor for files ending
        with `ext'.
        """
        if not isinstance(self['root'], static.File):
            raise usage.UsageError("You can only use --processor after --path.")
        ext, klass = proc.split('=', 1)
        self['root'].processors[ext] = reflect.namedClass(klass)


    def opt_class(self, className):
        """
        Create a Resource subclass with a zero-argument constructor.
        """
        classObj = reflect.namedClass(className)
        self['root'] = classObj()


    def opt_resource_script(self, name):
        """
        An .rpy file to be used as the root resource of the webserver.
        """
        self['root'] = script.ResourceScriptWrapper(name)


    def opt_wsgi(self, name):
        """
        The FQPN of a WSGI application object to serve as the root resource of
        the webserver.
        """
        pool = threadpool.ThreadPool()
        reactor.callWhenRunning(pool.start)
        reactor.addSystemEventTrigger('after', 'shutdown', pool.stop)
        try:
            application = reflect.namedAny(name)
        except (AttributeError, ValueError):
            raise usage.UsageError("No such WSGI application: %r" % (name,))
        self['root'] = wsgi.WSGIResource(reactor, pool, application)


    def opt_mime_type(self, defaultType):
        """
        Specify the default mime-type for static files.
        """
        if not isinstance(self['root'], static.File):
            raise usage.UsageError("You can only use --mime_type after --path.")
        self['root'].defaultType = defaultType
    opt_m = opt_mime_type


    def opt_allow_ignore_ext(self):
        """
        Specify whether or not a request for 'foo' should return 'foo.ext'
        """
        if not isinstance(self['root'], static.File):
            raise usage.UsageError("You can only use --allow_ignore_ext "
                                   "after --path.")
        self['root'].ignoreExt('*')


    def opt_ignore_ext(self, ext):
        """
        Specify an extension to ignore.  These will be processed in order.
        """
        if not isinstance(self['root'], static.File):
            raise usage.UsageError("You can only use --ignore_ext "
                                   "after --path.")
        self['root'].ignoreExt(ext)


    def postOptions(self):
        """
        Set up conditional defaults and check for dependencies.

        If SSL is not available but an HTTPS server was configured, raise a
        L{UsageError} indicating that this is not possible.

        If no server port was supplied, select a default appropriate for the
        other options supplied.
        """
        if self['https']:
            try:
                from twisted.internet.ssl import DefaultOpenSSLContextFactory
            except ImportError:
                raise usage.UsageError("SSL support not installed")
        if self['port'] is None:
            if self['personal']:
                path = os.path.expanduser(
                    os.path.join('~', distrib.UserDirectory.userSocketName))
                self['port'] = 'unix:' + path
            else:
                self['port'] = 'tcp:8080'



def makePersonalServerFactory(site):
    """
    Create and return a factory which will respond to I{distrib} requests
    against the given site.

    @type site: L{cyclone.tw.server.Site}
    @rtype: L{twisted.internet.protocol.Factory}
    """
    return pb.PBServerFactory(distrib.ResourcePublisher(site))



def makeService(config):
    s = service.MultiService()
    if config['root']:
        root = config['root']
        if config['indexes']:
            config['root'].indexNames = config['indexes']
    else:
        # This really ought to be web.Admin or something
        root = demo.Test()

    if isinstance(root, static.File):
        root.registry.setComponent(interfaces.IServiceCollection, s)

    if config['logfile']:
        site = server.Site(root, logPath=config['logfile'])
    else:
        site = server.Site(root)

    site.displayTracebacks = not config["notracebacks"]

    if config['personal']:
        personal = strports.service(
            config['port'], makePersonalServerFactory(site))
        personal.setServiceParent(s)
    else:
        if config['https']:
            from twisted.internet.ssl import DefaultOpenSSLContextFactory
            i = internet.SSLServer(int(config['https']), site,
                          DefaultOpenSSLContextFactory(config['privkey'],
                                                       config['certificate']))
            i.setServiceParent(s)
        strports.service(config['port'], site).setServiceParent(s)

    return s
