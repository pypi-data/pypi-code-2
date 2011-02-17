#/bin/env python
# 
# __main__.py
#
# (c) alain.spineux@gmail.com
#
# TCPProxyReflector client, server and console program
# 
import sys, os, time
import logging, ConfigParser, optparse
import threading

import socket, asyncore, asynchat

import tcpr as tcprlib
import srplib

logging.basicConfig(format='%(asctime)s %(levelname)-3.3s %(name)s %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    level=logging.INFO)

log=logging.getLogger('tcpr')

__version__=tcprlib.__version__

class OptionError(ConfigParser.Error):
    """An option has invalid value."""
    
    def __init__(self, section, option, message=None):
        self.option = option
        self.section = section
        self.message = message
        if message!=None:
            message=': %s' % (message, )
        ConfigParser.Error.__init__(self, "bad option %s in section %s%s" % (option, section, message))

def start_web_server(config, reflector_server):
    
    try:
        addr, port=config.get('server', 'listen_http').split(':')
        port=int(port)
    except ValueError:
        raise OptionError('listen_http', 'server')

    server=tcprlib.HTTPServer((addr, port), tcprlib.HTTPHandler)
    server.reflector_server=reflector_server
    server.log=logging.getLogger('http')

    http_thread=threading.Thread(target=server.serve_forever)
    http_thread.daemon=True
    http_thread.start()
    server.log.info('start listening on %s:%d', addr, port)

def start_client_cfg(config):
    log=logging.getLogger('client')

    classname=config.get('client', 'classname')
    try:
        hostname=config.get('client', 'hostname')
    except ConfigParser.NoOptionError:
        import socket 
        hostname=socket.gethostname()

    try:
        node_id=config.get('client', 'node_id')
    except ConfigParser.NoOptionError:
        try:
            import uuid
        except ImportError:
            raise OptionError('client', 'node_id', 'when using python 2.4, you must initialize node_id')
        else:
            node_id='%012X' % (uuid.getnode(),)
        
    try:
        clientname=config.get('client', 'clientname')
        password=config.get('client', 'password')
    except ConfigParser.NoOptionError:
        log.info('authentication disable')
        srp_client=None
        clientname=None
    else:
        srp_client=srplib.SRPClient('client.'+clientname, password)
        
    forwards=[]
    for forward in config.get('client', 'forwards').split(','):
        forward=forward.strip()
        try:
            protocol, name, host, port=forward.split(':')
            port=int(port)
        except ValueError:
            raise OptionError('client', 'forwards')
        
        forwards.append(tcprlib.Forward(protocol, name, host, port))

    server=config.get('client', 'server')
    try:
        host, port=server.split(':')
    except ValueError:
        try:
            import dns
            import dns.resolver
            # import required by py2exe because of a bug
            import dns.rdtypes.IN.SRV 
            
        except ImportError:
            log.error('module dnspython no found, cannot resolve SRV pointer for %r, user host:port instead',  server)
            raise OptionError('client', 'server')
        else:
            try:
                answers=dns.resolver.query(server, 'SRV')
                for rdata in answers:
                    print "ASX RDATA", answers, type(rdata)
                    print rdata
                    print rdata.target
                    print str(rdata.target)

                    _host=str(rdata.target)[:-1]
                    _port=int(rdata.port)
                print 'ASX DONE'
            except dns.exception.DNSException:
                log.error('cannot resolve SRV pointer for %s',  server)
                raise OptionError('client', 'server')
    else:
        try:
            port=int(port)
        except ValueError:
            raise OptionError('client', 'server')
        else:
            server=(host, port)
            
    alive_interval=int(config.get('client', 'alive_interval'))
    alive_timeout=int(config.get('client', 'alive_timeout'))

    tcprlib.start_client(log, classname, hostname, node_id, clientname, srp_client, forwards, server, alive_interval, alive_timeout, lambda:True)


def reset_manager_password(config, password):
    try:
        user_db_filename=config.get('server', 'user_db')
    except ConfigParser.NoOptionError:
        print 'Authentication is disabled ! Configure option "user_db" in section "server"'
    else:
        # open or create the DB
        user_db=srplib.PickleDB(user_db_filename)
        # create 'user.manager' if not existing 
        user_db.set('user.manager', password)


def start_server_cfg(config):
    log=logging.getLogger('server')
    
    srp_server=None
    try:
        user_db_filename=config.get('server', 'user_db')
    except ConfigParser.NoOptionError:
        log.info('authentication disabled')
    else:
        log.info('authentication enable')
        # open or create the DB
        user_db=srplib.PickleDB(user_db_filename)
        # create 'user.manager' if not existing 
        try:
            user_db.get('user.manager')
        except srplib.NoSuchUser:
            log.info('user manager as been created with password "manager"')
            user_db.set('user.manager', 'manager')
        srp_server=srplib.SRPServer(user_db)
        
    try:
        addr, port=config.get('server', 'listen').split(':')
        port=int(port)
    except ValueError:
        raise OptionError('server', 'listen')
    
    try:
        reflector_addr, ports=config.get('server', 'reflector').split(':')
        try:
            start, static, end=ports.split('-')
        except ValueError:
            # no static part
            start, static=ports.split('-')
            end=int(static)-1
        port_range=(int(start), int(static), int(end))
    except ValueError:
        raise OptionError('server', 'reflector')
    
    reflector_server=tcprlib.ReflectorServer(addr, port, reflector_addr, port_range, srp_server)
    log.info('start TCP Proxy Reflector server %s, listening on %s:%d', __version__, addr, port)

    try:
        addr, port=config.get('server', 'listen_cmd').split(':')
        port=int(port)
    except ValueError:
        raise OptionError('server', 'listen_cmd')
    
    tcprlib.CommandServer(addr, port, reflector_server, srp_server)
    log.info('start TCP Proxy Reflector command channel %s, listening on %s:%d', __version__, addr, port)
    
    if config.get('server', 'listen_http'):
        start_web_server(config, reflector_server)
    else:
        log.info('web interface disable.')

    alive_interval=int(config.get('server', 'alive_interval'))
    alive_timeout=int(config.get('server', 'alive_timeout'))

    interval=alive_interval
    if interval==0:
        interval=30
    
    next=time.time()+alive_interval
    while asyncore.socket_map:
        asyncore.loop(timeout=alive_interval, count=1)
        if time.time()>next:
            reflector_server.close_dead_reflectors(alive_timeout, alive_interval)
            reflector_server.close_expired_forward_servers()
            next=time.time()+alive_interval

def start_console(options, args):
    
    addr, port=args
    port=int(port)
        
    user=options_args.user
    password=options_args.password
    if user and not password:
        import getpass
        password=getpass.getpass('Enter password for %s: ' % user)
   
    tcprlib.start_console(addr, port, user=user, password=password)
    


# =====================================================================
#
# Echo server for testing
# 
# =====================================================================

class EchoHandler(asynchat.async_chat):

    def __init__(self, sock):
        asynchat.async_chat.__init__(self, sock)
        self.ibuffer=''
        self.set_terminator('\r\n')
        self.log=logging.getLogger('echo')
        self.log.info('open from %r', sock.getpeername())
       
    def collect_incoming_data(self, data):
        """Buffer the data"""
        self.ibuffer+=data

    def found_terminator(self):
        if self.ibuffer in ('exit', 'quit'):
            self.push('bye\r\n')
            self.close_when_done()
        else:
            self.push('%s\r\n' % (self.ibuffer, ))
        self.ibuffer=''

    def handle_close(self):
        self.log.info('close %r', self.getpeername())
        asynchat.async_chat.handle_close(self)


class EchoServer(asyncore.dispatcher):

    port=34567
    
    def __init__(self, host, port):
        asyncore.dispatcher.__init__(self)
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.set_reuse_addr()
        try:
            self.bind((host, port))
        except socket.error:
            self.close()
            raise
        self.listen(5)
        logging.getLogger('echo').info('server started on %s:%d', host, port)

    def handle_accept(self):
        pair=self.accept()
        sock, addr=pair
        handler=EchoHandler(sock)


def start_echo_server():
    
    port=EchoServer.port

    server=None
    while not server:
        try:
            server=EchoServer('127.0.0.1', port)
        except socket.error:
            port+=1

    return port

# generic parser

parser=optparse.OptionParser()
parser.set_usage(
"""usage: %prog -s [ config_file ] # start in server mode"
       %prog -c [ config_file ] # start in client mode
       %prog -t [ config_file ] # testing client client (include a echo server) 
       %prog -m [ config_file ] # reset manager password
       %prog [-o] [-u user] [-p password] host port # start in console mode
       
       default config_file is "tcpr.ini"
""")


pgeneric=optparse.OptionGroup(parser, "select mode", "These options are mutually exclusive")
pgeneric.add_option('-s', '--server', dest='server', action='store_true', default=False, help='start in server mode')
pgeneric.add_option('-m', '--manager-passwd', dest='manager_password', help='reset the manager password without starting the server', metavar='password')
pgeneric.add_option('-c', '--client', dest='client', action='store_true', default=False, help='start in client mode')
pgeneric.add_option('-t', '--testing', dest='testing', action='store_true', default=False, help='start in testing mode')
pgeneric.add_option('-o', '--console', dest='console', action='store_true', default=False, help='start in console mode (default)')
parser.add_option_group(pgeneric)

# console
pconsole=optparse.OptionGroup(parser, "console options", "Use theses options only in console mode")
pconsole.add_option('-u', '--user', dest='user', default=None, help='user name', metavar='user')
pconsole.add_option('-p', '--password', dest='password', default=None, help='secret password', metavar='password')
parser.add_option_group(pconsole)


(options_args, args) = parser.parse_args()

def load_config(filename):
    config_default=dict(user_db=None)
    config=ConfigParser.RawConfigParser(config_default)
    try:
        config.readfp(open(filename, 'r'))
    except Exception, e:
        log.error('error reading configuration file %s: %s', filename, e)
        sys.exit(1)
        
    if config.has_section('loggers') and config.has_section('handlers') and config.has_section('formatters'):
        import logging.config
        logging.config.fileConfig(filename)
 
    return config

if options_args.server or options_args.client or options_args.testing or options_args.manager_password:
    try:
        config_filename=args[0]
    except IndexError:
        config_filename='tcpr.ini'
    config=load_config(config_filename)

if options_args.server:
    start_server_cfg(config)
elif options_args.manager_password:
    reset_manager_password(config, options_args.manager_password)  
elif options_args.client or options_args.testing:
    if options_args.testing:
        start_echo_server()
    start_client_cfg(config)
else:
    # console
    if len(args)!=2:
        parser.error('console mode require 2 arguments')
        
    start_console(options_args, args)
