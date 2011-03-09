#!python
"""
Entrypoint for starting the VMController Guest.
"""

try:
    import os
    import sys
    import logging
    import tempfile
    import inject

    from pkg_resources import resource_stream
    from ConfigParser import SafeConfigParser
    from optparse import OptionParser
    from twisted.internet import reactor, protocol
    from twisted.application import internet, service

    from vmcontroller.common import support, exceptions
    from vmcontroller.common import StompProtocolFactory, StompProtocol
    from vmcontroller.guest.config import init_config, init_config_file, debug_config
    from vmcontroller.guest.services import VMStompEngine, VMWords
    from vmcontroller.guest.services.FileServer import FileServerFactory
except ImportError, e:
    print "Import error in %s : %s" % (__name__, e)
    import sys
    sys.exit()

logger = logging.getLogger(__name__)

def init_logging(logfile=None, loglevel=logging.INFO):
    """
    Sets logging configuration.
    @param logfile: File to log messages. Default is None.
    @param loglevel: Log level. Default is logging.INFO.
    """
    format = '%(asctime)s - [%(threadName)s] %(filename)s:%(lineno)s - (%(levelname)s) %(message)s'
    if logfile:
        logging.basicConfig(filename=logfile, level=loglevel, format=format)
    else:
        logging.basicConfig(level=loglevel, format=format)

def init():
    """
    """

    parser = OptionParser()
    parser.add_option("-c", "--config", dest="configfile",
                      help="Read configuration from FILE. (Overrides default config file.)", metavar="FILE")
    parser.add_option("-a", "--host", dest="broker_host",
                      help="Listen on specified address for broker.", metavar="ADDR")
    parser.add_option("-p", "--port", dest="broker_port",
                      help="Listen on specified port for broker.", type="int", metavar="PORT")
    parser.add_option("-l", "--logfile", dest="logfile",
                      help="Log to specified file.", metavar="FILE")
    parser.add_option("--debug", action="store_true", dest="debug", default=False, 
                      help="Sets logging to debug (unless logging configured in config file).")

    (options, args) = parser.parse_args()

    config = init_config()
    injector = inject.Injector()
    inject.register(injector)

    injector.bind('config', to=config)
    injector.bind('words', to=VMWords.getWords, scope=inject.appscope)
    injector.bind('stompProtocol', to=StompProtocol, scope=inject.appscope) 
    injector.bind('stompEngine', to=VMStompEngine, scope=inject.appscope) 
    injector.bind('subject', to=VMStompEngine, scope=inject.appscope) 

    if options.broker_host is not None:
        config.set('broker', 'host', options.broker_host)
        
    if options.broker_port is not None:
        config.set('broker', 'port', str(options.broker_port))

    level = logging.DEBUG if options.debug else logging.INFO
    init_logging(logfile=options.logfile, loglevel=level)
    debug_config(config)

@inject.param('config')
def start(config):
    """Start twisted event loop and the fun should begin..."""

    host = config.get('broker', 'host') 
    port = int(config.get('broker', 'port'))

    username = config.get('broker', 'username')
    password = config.get('broker', 'password')

    fileServerPort      = int(config.get('fileserver', 'port'))
    fileServerDirectory = config.get('fileserver', 'directory')

    # Start File Server
    try:
      	reactor.listenTCP(fileServerPort, FileServerFactory(fileServerDirectory))
        logger.info('Listening on port %d, serving files from directory: %s' % (fileServerPort, fileServerDirectory))
    except:
        logger.fatal("Unable to start file server at port: %d, please check." % fileServerPort)

    stompProtocolFactory = StompProtocolFactory()

    reactor.connectTCP(host, port, stompProtocolFactory)
    reactor.run()
    return internet.TCPClient(host, port, stompProtocolFactory)

def main():
    init()
    logger.info("Starting VMController in guest.")

    application = service.Application("vmcontroller.guest")

    guest_service = start()
    guest_service.setServiceParent(application)

if __name__ == '__main__':
    try:
        main()
    except (KeyboardInterrupt, SystemExit):
        pass
    except Exception, e:
        logger().error("Server terminated due to error: %s" % e)
        logger().exception(e)

#TODO: Implement using twisted.conch, file transfer
