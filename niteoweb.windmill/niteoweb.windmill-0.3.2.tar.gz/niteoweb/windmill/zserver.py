import time
import random

from urllib import urlopen
from StringIO import StringIO

from Testing.ZopeTestCase.threadutils import setNumberOfThreads, QuietThread

from ZServer import asyncore, logger, zhttp_server, zhttp_handler

class ZServerLayer(object):
    """Layer mixin for starting and stopping a ZServer HTTP server on a random
    port. The various class variables may be set prior to setUp() in order to
    influence how the server is run. On tearDown(), the socket will be closed,
    and the server stopped.
    
    Like all of Zope's servers, this relies on an asyncore loop, which will
    be started in a separate thread. As such, running this in parallel in
    multiple threads is likely to be a very bad idea.
    
    In particular, this probably means that this layer cannot be run reliably
    after Testing.ZopeTestCase.utils.startZServer() has been called.
    """
    
    host = '127.0.0.1'
    port = random.choice(range(55000, 55500))
    log = StringIO()
    _threads = 1
    
    @classmethod
    def setUp(cls):
        cls._shutdown = False
        setNumberOfThreads(cls._threads)
        t = QuietThread(target=cls._runner, args=())
        t.setDaemon(1)
        t.start()
        for ignore in range(1000):
            time.sleep(0.1)
            try:
                urlopen("http://%s:%i" % (cls.host, cls.port))
                break;
            except IOError:
                pass

    @classmethod
    def tearDown(cls):
        cls._shutdown = True
    
    @classmethod
    def _runner(cls):
        """Start a server using asyncore - this runs in a separate thread!
        """
        log = logger.file_logger(cls.log)
        
        # Create ZServer
        server = zhttp_server(ip=cls.host, port=cls.port, logger_object=log)
        handler = zhttp_handler(module='Zope2', uri_base='')
        server.install_handler(handler)
        
        # Poll
        timeout = 30.0
        socket_map = asyncore.socket_map
        while socket_map and not cls._shutdown:
            asyncore.poll(timeout, socket_map)
        
        # Close socket
        server.close()
