#/bin/env python
# 
# proxyreflector.py
#
# (c) alain.spineux@gmail.com
#
# TCPProxyReflector client, server and console program
# 

import sys, os, logging, re, time, random 
import struct, socket, asyncore, asynchat
import telnetlib

import srplib
import srplib.sock


  
from srplib.asyn import SRPClientHandler, SRPServerHandler
# from asynchat import async_chat as SRPClientHandler
# from asynchat import async_chat as SRPServerHandler

__all__=[
    '__version__', 'TPRException',
    'ClientHandler', 'Forward',
    'ReflectorServer', 'CommandServer',
    'HTTPServer', 'HTTPHandler',
    'TelnetSRP', 
    'start_console', 'start_client',
]

__version__='0.1.2'

DEBUG=True

log=logging.getLogger('proxyreflector')

class TPRException(Exception):
    pass


class multiplex_ascii:
    """This is how TCPR multiplex packets, this one use human readable
    format, easyer to debug"""
    
    header_size=13
    header_re=re.compile('=(?P<type>.)-(?P<tunnel>[0-9A-Fa-f]{4})-(?P<arg>[0-9A-Fa-f]{4})-')

    # type action
    #  T   allocate new tunnel, arg=channel number
    #  D   data
    #  C   close tunnel
    #  S   shutdown reflector
        
    @staticmethod
    def pack_cmd(cmd, tunnel, arg):
        return '=%c-%04X-%04X-' % (cmd, tunnel, arg)

    @staticmethod
    def pack_data(tunnel, data):
        # type tunnel, size, data
        buf='=%c-%04X-%04X-' % ('D', tunnel, len(data))
        return buf+data
    
    @staticmethod
    def unpack(buf):
        assert len(buf)==multiplex_ascii.header_size, 'buffer has a wrong size: %d %r' % (len(buf), buf[:2*multiplex_ascii.header_size])
        match=multiplex_ascii.header_re.match(buf)
        assert match, 'buffer %r dont match header format' % (buf[:multiplex_ascii.header_size], )
        return match.group('type'), int(match.group('tunnel'), 16), int(match.group('arg'), 16)


class multiplex_bin:
    """This is how TCPR multiplex packets, this one use optimized binary format""" 
    
    header_size=6

    # type action
    #  T   allocate new tunnel, arg=channel number
    #  D   data
    #  C   close tunnel
    #  S   shutdown reflector
        
    magic=123 # first byte of each packet 
    
    @staticmethod
    def pack_cmd(cmd, tunnel, arg):
        return struct.pack('!BcHH', multiplex_bin.magic, cmd, tunnel, arg)

    @staticmethod
    def pack_data(tunnel, data):
        # type tunnel, size, data
        return struct.pack('!BcHH', multiplex_bin.magic, 'D', tunnel, len(data))+data
    
    @staticmethod
    def unpack(buf):
        assert len(buf)==multiplex_bin.header_size, 'buffer has a wrong size: %d %r' % (len(buf), buf[:2*multiplex_bin.header_size])
        magic, type, tunnel, arg=struct.unpack('!BcHH', buf)
        assert magic==multiplex_bin.magic, 'buffer %r dont match header format' % (buf[:multiplex_bin.header_size], )
        return type, tunnel, arg


multiplex=multiplex_bin



# =====================================================================
#
# dispatcher_with_send
# 
# =====================================================================

class tcpr_dispatcher_with_send(asyncore.dispatcher_with_send):
    """add close_when_done()"""
    def __init__(self, sock=None):
        asyncore.dispatcher_with_send.__init__(self, sock)
        self.closing=False
        
    def close_when_done(self):
        """wait for the out_buffer to be empty before to close"""
        self.closing=True
        if not self.out_buffer:
            self.close()
        
    def initiate_send(self):
        asyncore.dispatcher_with_send.initiate_send(self)
        if not self.out_buffer and self.closing:
            self.close()

# =====================================================================
#
# Client
# 
# =====================================================================

class TunnelHandler(tcpr_dispatcher_with_send):

    def __init__(self, client_handler, id, channel_n):
        tcpr_dispatcher_with_send.__init__(self, None)
        self.id=None # will be set at the end
        self.client_handler=client_handler
        self.channel_n=channel_n
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        forward=self.client_handler.forwards[channel_n]
        self.connect((forward.addr, forward.port))
        self.last_use=time.time()
        # register tunnel
        self.client_handler.tunnels[id]=self
        self.id=id
        
    def handle_read(self):
        self.last_use=time.time()
        data = self.recv(8192)
        if data:
            self.client_handler.send_tunnel(self, data)
        else:
            """don't send an empty packet, handle_close will be called next"""

    def handle_close(self):
        self.client_handler.log.info('close tunnel %%%d (request by application)', self.id)
        self.client_handler.push(multiplex.pack_cmd('C', self.id, self.channel_n))
        tcpr_dispatcher_with_send.handle_close(self)

    def close(self):
        # unregister tunnel
        del self.client_handler.tunnels[self.id]
        tcpr_dispatcher_with_send.close(self)

    def write_through(self, data):
        self.last_use=time.time()
        self.send(data)

    def handle_connect(self):
        """avoid message with python 2.4"""

    def handle_error(self):
        t, v=sys.exc_info()[:2]
        if t==socket.error and v.errno==111:
            self.client_handler.log.info('error tunnel %%%d $%d: %s)', self.id, self.channel_n, v)
            self.handle_close()
        else:
            tcpr_dispatcher_with_send.handle_error(self)


class Forward:
    """forward as seen by the client side"""
    def __init__(self, prot_name, forward_name, addr, port):
        self.prot_name=prot_name
        self.forward_name=forward_name
        self.addr=addr
        self.port=port

class ClientHandler(SRPClientHandler):

    def __init__(self, class_name, hostname, node_id, host, port, forwards, srp_client=None):
        # using socket instead of asynchat will raise an exception right now
        # with the right error. asyncore use non blocking socket that are badly 
        # handled by the library  http://bugs.python.org/issue6550
        sock=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect( (host, port) )
        SRPClientHandler.__init__(self, sock)

        self.log=logging.getLogger('client')
        self.class_name=class_name
        self.hostname=hostname
        self.node_id=node_id
        self.forwards=forwards
        self.srp_client=srp_client
        self.username=None
        self.ibuffer=''
        
        self.tunnels=dict()
        self.current_tunnel=None
        self.last_use=time.time()
        
        self.state='wait_connection_status'
        self.set_terminator('\r\n')

        if self.srp_client:
            self.handle_authentication(self.srp_client)
        else:
            self.handle_authentication_success(None, None)

    def handle_authentication_failure(self, message):
        self.log.error('authentication failure: %s', message)
        SRPClientHandler.handle_authentication_failure(self, message)

    def handle_authentication_success(self, username, key):
        if self.srp_client:
            self.log.info('logged in as %s', username)
        else:
            self.log.info('connected')

        self.username=username            
        # identify the client
        self.push('%s %s %s\r\n' % (self.class_name, self.node_id, self.hostname))

    def collect_incoming_data(self, data):
        """Buffer the data"""
        self.ibuffer+=data

    #  T   allocate new tunnel, size is channel number
    #  D   data
    #  C   close tunnel
    #  S   shutdown reflector
    #  P   ping

    def found_terminator(self):
        data=self.ibuffer
        self.ibuffer=''
        self.last_use=time.time()
        if self.state=='wait_for_packet_data':
            # self.log.debug('received data %d: %d', self.current_tunnel, len(data))
            self.tunnels[self.current_tunnel].write_through(data)
            self.state='wait_for_packet'
            self.set_terminator(multiplex.header_size)
            
        elif self.state=='wait_for_packet':
            packet_type, packet_tunnel, packet_arg=multiplex.unpack(data)
            # self.log.debug('received <%c %d %d>', packet_type, packet_tunnel, packet_arg)
            
            if packet_type=='D':
                # data
                self.state='wait_for_packet_data'
                self.current_tunnel=packet_tunnel
                self.set_terminator(packet_arg)
            elif packet_type=='T':
                # open new tunnel
                forward=self.forwards[packet_arg]

                try:
                    tunnel=TunnelHandler(self, packet_tunnel, packet_arg)
                except socket.error, e:
                    # send error
                    self.log.error('cannot open tunnel %%%d to %s:%d ($%d:%s:%s) (%s)', packet_tunnel, forward.addr, forward.port, packet_arg, forward.prot_name, forward.forward_name, e)
                    self.push(multiplex.pack_cmd('T', packet_tunnel, 1))
                else:
                    # send confirmation
                    self.log.info('open tunnel %%%d to %s:%d ($%d:%s:%s)', packet_tunnel, forward.addr, forward.port, packet_arg, forward.prot_name, forward.forward_name)
                    self.push(multiplex.pack_cmd('T', packet_tunnel, 0)) # OK

                self.set_terminator(multiplex.header_size)

            elif packet_type=='C':
                # close tunnel
                try:
                    tunnel=self.tunnels[packet_tunnel]
                except KeyError:
                    """tunnel already closed"""
                else:
                    self.log.info('close tunnel %%%d (request by other side)', packet_tunnel)
                    tunnel.close_when_done()
                # the confirmation should come from TunnelHandler.handle_close via self.close_tunnel
                self.set_terminator(multiplex.header_size)

            elif packet_type=='P':
                # ping
                # self.log.debug('ping %X %X', packet_tunnel, packet_arg)
                if packet_arg>0:
                    self.push(multiplex.pack_cmd('P', packet_tunnel, packet_arg-1))  
                self.set_terminator(multiplex.header_size)

        elif self.state=='wait_connection_status':
            if not data.startswith('4'):
                self.log.error('connection failure: %s', data)
                self.close()
                return
            self.log.info('connected (%s)', data)
            
            # send forwards
            for i, forward in enumerate(self.forwards):
                self.push('%s %s\r\n' % (forward.prot_name, forward.forward_name))
                self.log.info('$%d prot=%s name=%s to=%s:%d', i, forward.prot_name, forward.forward_name, forward.addr, forward.port)
            # end forward list by an empty line 
            self.push('\r\n')
            self.state='wait_for_packet'
            self.set_terminator(multiplex.header_size)

    def close(self):
        self.log.info('bye')
        SRPClientHandler.close(self)
        # required if pyhton before 2.6
        self.connected=False
        self.accepting=False

    def send_tunnel(self, tunnel, data):
        self.last_use=time.time()
        buf=multiplex.pack_data(tunnel.id, data)
        # self.log.debug('send_tunnel %d + %d', multiplex.header_size, len(buf)-multiplex.header_size)
        self.push(buf)  
        
    def check_for_dead(self, alive_timeout, alive_interval):
        status='running'
        now=time.time()
        if alive_timeout and self.last_use+alive_timeout<now:
            delay=int(now-self.last_use)
            self.log.error('no packets received for %0d:%02d:%02d', delay/3600, delay/60%60, delay%60)
            status='dead'
        elif alive_interval and self.last_use+alive_interval<now:
            # send a ping
            self.push(multiplex.pack_cmd('P', random.randint(0, 65535), 1))  
            self.set_terminator(multiplex.header_size)
            # the reply will update self.last_use
        else:
            # used a short time ago
            pass
        return status

# =====================================================================
#
# ForwarderHandler
# 
# =====================================================================


class ForwarderHandler(tcpr_dispatcher_with_send):

    def __init__(self, forward_server, sock):
        tcpr_dispatcher_with_send.__init__(self, sock)
        self.forward_server=forward_server
        # self.forward_server.log.debug('open %s:%d', self.getpeername()[0], self.getpeername()[1])
        self.id=None
        self.state='new'
        self.last_use=time.time()
        self.forward_server.reflector_handler.register_tunnel(self)
        self.ingoing=0
        self.outgoing=0
        
    def handle_read(self):
        self.last_use=self.forward_server.last_use=time.time()
        data = self.recv(8192)
        self.ingoing+=len(data)
        if data:
            self.forward_server.reflector_handler.send_tunnel(self, data)

    def write_through(self, data):
        self.last_use=self.forward_server.last_use=time.time()
        if self.state!='open':
            raise TPRException, 'ForwarderHandler not open on both side'
        self.send(data)
        self.outgoing+=len(data)

    def handle_close(self):
        self.forward_server.log.info('close tunnel %%%d (request by application)', self.id)
        self.forward_server.reflector_handler.close_tunnel_otherside(self)
        tcpr_dispatcher_with_send.handle_close(self)

    def close(self):
        if self.out_buffer:
            self.forward_server.log.error('CLOSING WHEN BUFFER NOT EMPTY: %d bytes left', len(self.out_buffer))

        self.forward_server.reflector_handler.unregister_tunnel(self)
#        if self.connected:
        self.forward_server.log.info('tunnel %%%d with %s:%d closed recv=%dk sent=%dk', self.id, self.getpeername()[0], self.getpeername()[1], self.ingoing/1024, self.outgoing/1024)
        tcpr_dispatcher_with_send.close(self)

class ForwardServer(asyncore.dispatcher):

    def __init__(self, reflector_handler, num, prot_name, forward_name):
        asyncore.dispatcher.__init__(self)
        self.reflector_handler=reflector_handler
        self.num=num                    # the order of the forward, this is the id with the client 
        self.prot_name=prot_name        # name of the protocol (ssh, http, rdp, vnc, ...)
        self.forward_name=forward_name  # a name choosed by the user
        self.id=None                    # this is the id given by the ReflectorServer, the reference used with the CommandHandler
        
        self.time_expiration=0
        self.allowed_targets=set()
        
        self.reflector_handler.manager.register_forward_server(self)
        self.log=logging.getLogger('%s#%d' % (self.reflector_handler.name, self.id, ))

        self.connected = False
        self.accepting = False
        
    def __del__(self):
        self.reflector_handler.manager.unregister_forward_server(self)
        self.__del__(self)

    def reopen(self, addr):
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.set_reuse_addr()
        
        try:
            self.bind(addr)
        except socket.error:
            self.close()
            raise
        
        self.listen(5)
        self.log.info('listening on %s:%d', addr[0], addr[1])
        self.last_use=time.time()

    def start(self, target, fixed_port, expiration_delay):
        """activate or modify the configuration of the server"""
        if self.accepting:
            raise TPRException('already started')
        
        addr=self.reflector_handler.manager.allocate_addr(fixed_port)
        if expiration_delay:
            self.time_expiration=time.time()+expiration_delay
        else:
            self.time_expiration=0
        self.allowed_targets=set([target, ])
        self.log.info('start target=%s delay=%ds port=%s', target, self.time_expiration and self.time_expiration-time.time(), fixed_port)
        self.reopen(addr)
        
    def modify(self, target, fixed_port, expiration_delay):
            
        if expiration_delay!=None:
            if expiration_delay==0:
                self.time_expiration=0
            else:
                self.time_expiration=time.time()+expiration_delay
        
        if target:
            if target.startswith('-'):
                self.allowed_targets.discard(target[1:])
            else:
                self.allowed_targets.add(target)

        self.log.info('modify target=%s delay=%ss port=%s', target, self.time_expiration and self.time_expiration-time.time(), fixed_port)

        if fixed_port and fixed_port!=self.getsockname()[1]:
            # need to reopen the server on the fixed port
            addr=self.reflector_handler.manager.allocate_addr(fixed_port)
            # ok I have an address, then close and reopen
            self.log.info('close to reopen on a different port')
            self.close()
            self.reopen(addr)
                      
    def handle_accept(self):
        self.last_use=time.time()
        pair = self.accept()
        if pair is None:
            pass
        else:
            sock, addr = pair
            
            if self.check_time_limit():
                sock.close()
            elif addr[0] in self.allowed_targets or '0.0.0.0' in self.allowed_targets:
                # self.log.debug('Incoming connection from %s', repr(addr))
                handler = ForwarderHandler(self, sock)
            else:
                self.log.info('Denied connection from %s', repr(addr))

    def check_time_limit(self):
        if (self.accepting and self.time_expiration!=0 and self.time_expiration<time.time()):
            self.reflector_handler.manager.log.info('#%d forward server expired, close', self.id)
            self.close()
            return True
        return False

    def close(self):
        self.log.info('close')
        self.reflector_handler.manager.free_addr(self.getsockname())
        asyncore.dispatcher.close(self)
        
# =====================================================================
#
# ReflectorHandler
# 
# =====================================================================
        
class ReflectorHandler(SRPServerHandler):
    
    def __init__(self, manager, sock, srp_session=None):
        SRPServerHandler.__init__(self, sock)
        self.manager=manager
        self.ibuffer=''
        self.set_terminator('\r\n')
        self.state='reading_header'
        
        self.class_name='unknown'
        self.hostname='new'
        self.node_id='000000000000'
        self.name='%s:%d' % self.getpeername()
        self.log=logging.getLogger(self.name)
        self.ingoing=0
        self.outgoing=0

        self.key=None
        
        self.forward_servers=[] # list of forwards sent by the client, the order is important  
        
        self.tunnel_unique_id=0
        self.tunnels=dict()
        
        self.current_tunnel=None
        self.last_use=time.time()
        
        self.srp_session=srp_session
        self.clientname=None
        self.clientgroups=set()
        self.fqclientgroups=set()
        
        if self.srp_session:
            self.handle_authentication(srp_session)

    def validate_username(self, username, data):
        if not username.startswith('client.'):
            return 'credential must be a "client" credential'
        return None
            
    def handle_authentication_failure(self, message, username):
        SRPServerHandler.handle_authentication_failure(self, message, username)
        self.clientname=username
        if self.clientname:
            self.log.error('authentication error user "%s" : %s', username, message)
        else:
            self.log.error('authentication error: %s', message)

    def handle_authentication_success(self, username, key, userdata):
        # username must start with 'client.' , if not will close the connection later
        self.clientname=username
        self.clientgroups=set(userdata)

    def collect_incoming_data(self, data):
        """Buffer the data"""
        self.ibuffer+=data
        self.ingoing+=len(data)

    def push(self, data):
        SRPServerHandler.push(self, data)
        self.outgoing+=len(data)

    def found_terminator(self):
        data=self.ibuffer
        self.ibuffer=''
        self.last_use=time.time()
        if self.state=='wait_for_packet_data':
            # self.log.debug('received data %d: %d', self.current_tunnel, len(data))
            try:
                self.tunnels[self.current_tunnel].write_through(data)
            except KeyError:
                self.log.error('tunnel not found #%d len=%d', self.current_tunnel, len(data))
            self.state='wait_for_packet'
            self.set_terminator(multiplex.header_size)
            
        elif self.state=='wait_for_packet':

            packet_type, packet_tunnel, packet_arg=multiplex.unpack(data)
            # self.log.debug('received <%c %d %d>', packet_type, packet_tunnel, packet_arg)
            
            if packet_type=='D':
                # data
                self.state='wait_for_packet_data'
                self.current_tunnel=packet_tunnel
                self.set_terminator(packet_arg)
            elif packet_type=='C':
                # close tunnel
                try:
                    tunnel=self.tunnels[packet_tunnel]
                except KeyError:
                    """tunnel already closed"""
                else:
                    tunnel.forward_server.log.info('close tunnel %%%d (request by other side)', packet_tunnel)
                    tunnel.close_when_done()
                self.set_terminator(multiplex.header_size)
            elif packet_type=='T':
                # ack for open tunnel
                if packet_arg==0:
                    # success
                    self.tunnels[packet_tunnel].state='open'
                    self.tunnels[packet_tunnel].forward_server.log.info('ACK, tunnel %%%d open', packet_tunnel)
                else:
                    # failure
                    self.tunnels[packet_tunnel].forward_server.log.info('NACK, tunnel %%%d not open', packet_tunnel)
                    self.tunnels[packet_tunnel].close()
                self.set_terminator(multiplex.header_size)
                
            elif packet_type=='P':
                # ping
                # self.log.debug('ping %X %X', packet_tunnel, packet_arg)
                if packet_arg>0:
                    self.push(multiplex.pack_cmd('P', packet_tunnel, packet_arg-1))
                self.set_terminator(multiplex.header_size)
        
        elif self.state=='reading_header':
            # self.log.info('ASX buffer=%r', data)
            try:
                self.class_name, self.node_id, self.hostname=data.split(None, 2)
            except ValueError:
                self.log.info('bad header %r', data)
                self.push('513 bad header, bye\r\n')
                self.close_when_done()
                return
            
            # peername=self.socket.getpeername()
            # sockname=self.socket.getsockname()
            self.log.info('open reflector class=%s hostname=%s node_id=%s', self.class_name, self.hostname, self.node_id)
            self.fqclientgroups=set(map(lambda x:'%s:%s' % (x, self.node_id), self.clientgroups))
            self.log.info('fqclientgroups: %s', ', '.join(self.fqclientgroups))
            # search for a matching reflector
            for reflector in self.manager.reflectors.itervalues():
                if reflector.class_name==self.class_name and reflector.node_id==self.node_id and reflector.hostname==self.hostname: 
                    # could compare user login also (clientname)
                    self.log.info('client already connected, connection closed')
                    self.push('500 already connected\r\n')
                    self.close_when_done()
                    return

            self.push('400 waiting forwards\r\n')
            self.key=self.getpeername()
            self.manager.reflectors[self.key]=self
            self.state='reading_forwards'
        elif self.state=='reading_forwards':
            if data:
                prot_name, forward_name=data.split(None, 1)
                forward_server=ForwardServer(self, len(self.forward_servers), prot_name, forward_name)
                self.forward_servers.append(forward_server)
                self.log.info('#%d num=%d prot=%s name=%s', forward_server.id, forward_server.num, forward_server.prot_name, forward_server.forward_name)
            else:
                # end of the forward list  
                self.state='wait_for_packet'
                self.set_terminator(multiplex.header_size)
                
    def handle_close(self):
        asynchat.async_chat.handle_close(self)

    def close(self):
        for forward_server in self.forward_servers:
            self.manager.unregister_forward_server(forward_server)
            forwarder2close=[]
            for tunnel_id, forwarder in self.tunnels.iteritems():
                if forwarder.forward_server==forward_server:
                    forwarder2close.append(forwarder)

            for forwarder in forwarder2close:
                forwarder.close() 
                
            if forward_server.accepting:
                forward_server.close()

        if self.key:
            del self.manager.reflectors[self.key]
        self.log.info('close %s %s %s %s %d', self.name, self.class_name, self.hostname, self.node_id, len(self.forward_servers))
        asynchat.async_chat.close(self)
        
    def stop_forward(self, forward_server, terminate=False):
        # terminate will close all underneath tunnel too
        
        forward_server.allowed_targets=[]
        forward_server.limit=time.time()
        
        if forward_server.accepting:
            forward_server.close() # not handle_close
        
        if terminate:
            forwarder2close=[]
            for tunnel_id, forwarder in self.tunnels.iteritems():
                if forwarder.forward_server==forward_server:
                    forwarder2close.append(forwarder)

            for forwarder in forwarder2close:
                forwarder.close()
            # The ForwardServer will be closed by self.unregister_tunnel()
            # when closing all the tunnel 
        
    def register_tunnel(self, forwarder):
        self.last_use=time.time()
        forwarder.id=self.tunnel_unique_id
        forwarder.forward_server.log.info('register tunnel %%%d connection from %s:%d', forwarder.id, forwarder.getpeername()[0], forwarder.getpeername()[1])
        self.tunnel_unique_id+=1
        self.tunnels[forwarder.id]=forwarder
        self.push(multiplex.pack_cmd('T', forwarder.id, forwarder.forward_server.num))  

    def close_tunnel_otherside(self, forwarder):
        self.push(multiplex.pack_cmd('C', forwarder.id, forwarder.forward_server.num))

    def unregister_tunnel(self, forwarder):
        forwarder.forward_server.log.info('unregister tunnel %%%d', forwarder.id)
        del self.tunnels[forwarder.id]

    def send_tunnel(self, forwarder, data):
        self.last_use=time.time()
        buf=multiplex.pack_data(forwarder.id, data)        
        # self.log.debug('send_tunnel %d + %d', multiplex.header_size, len(buf)-multiplex.header_size)
        self.push(buf)
        
    def check_for_dead(self, alive_timeout, alive_interval):
        status='running'
        now=time.time()
        if alive_timeout and self.last_use+alive_timeout<now:
            delay=int(now-self.last_use)
            self.log.error('not used for %0d:%02d:%02d', delay/3600, delay/60%60, delay%60)
            status='dead'
        elif alive_interval and self.last_use+alive_interval<now:
            # send a ping
            self.push(multiplex.pack_cmd('P', random.randint(0, 65535), 1))  
            self.set_terminator(multiplex.header_size)
            # the reply will update self.last_use
        else:
            # used a short time ago
            pass
        
        return status
        
    def get_user_friendly_status(self):
        clientname=''
        if self.clientname:
            clientname=self.clientname[7:]+'@' # drop 'client.' and add a '@'
            
        status='reflector<%s%s(%s,%s,%s)>\n' % (clientname, self.name, self.class_name, self.hostname, self.node_id) 
        for forward_server in self.forward_servers:
            fw_status=''
            if forward_server.accepting:
                fw_status=' listening on %s:%d' % (forward_server.addr[0], forward_server.addr[1] )
                if forward_server.time_expiration:
                    delay=forward_server.time_expiration-time.time()
                    if delay>0:
                        fw_status+=' for %dH%02dm%02ds\n' % (delay/3600,delay/60%60, delay%60)
                    else:
                        fw_status+=' closing\n'
                else:
                    fw_status+=' no time limit\n' 
                fw_status+='      ... accepting '+', '.join(forward_server.allowed_targets)
            status+='   #%d <$%d %s,%s>%s\n' %(forward_server.id, forward_server.num, forward_server.prot_name, forward_server.forward_name, fw_status)
            for tunnel_id, forwarder in self.tunnels.iteritems():
                if forwarder.forward_server==forward_server:
                    addr, port=forwarder.getpeername()
                    status+='      >tunnel %%%d connection from %s:%d recv=%dK send=%dK\n' % (tunnel_id, addr, port, forwarder.ingoing/1024, forwarder.outgoing/1024)

        for tunnel_id, forwarder in self.tunnels.iteritems():
            addr, port=forwarder.getpeername()
            reflector=forwarder.forward_server.reflector_handler
            status+='tunnel %%%d connection from %s:%d to reflector %s\n' % (tunnel_id, addr, port, reflector.name)
        return status

    def handle_error(self):
        if DEBUG:
            raise
        else:
           asyncore.dispatcher.handle_error(self) 
       
class ReflectorServer(asyncore.dispatcher):
    def __init__(self, addr, port, reflector_addr, port_range, srp_server):
        asyncore.dispatcher.__init__(self)
        self.reflectors=dict() # active reflectors 
        self.log=logging.getLogger('reflector')
        self.srp_server=srp_server
        self.reflector_addr=reflector_addr
        self.port_range=port_range
        self.current_port=self.port_range[0]
        self.used_ports=set()
        self.unique_forward_server_id=0
        self.all_forward_servers=dict() # list of all forwards mixed together
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.set_reuse_addr()
        self.bind((addr, port))
        self.listen(5)
        self.log.info('server started on %s:%d', addr, port)

    def handle_accept(self):
        pair = self.accept()
        if pair is None:
            pass
        else:
            sock, addr = pair
            self.log.info('new incoming connection from %s:%d', addr[0], addr[1])

            srp=None
            if self.srp_server:
                srp=self.srp_server.create_session()
            handler = ReflectorHandler(self, sock, srp)

    def allocate_addr(self, fixed_port=None):
        if fixed_port:
            if self.port_range[1]<fixed_port<=self.port_range[2] and fixed_port not in self.used_ports:
                self.used_ports.add(fixed_port)
                return (self.reflector_addr, fixed_port)
            else:
                raise TPRException, 'fixed port already in use or out of range'
        else:
            port=None
            i=self.port_range[1]-self.port_range[0]+1
            while i>0:
                port=self.current_port
                self.current_port+=1
                if port not in self.used_ports:
                    self.used_ports.add(port)
                    break   
                if self.current_port>self.port_range[1]:
                    self.current_port=self.port_range[0]
                i-=1
    
            if port==None:
                raise TPRException, 'all ports are in use'
        
        return (self.reflector_addr, port)

    def free_addr(self, addr):
        self.used_ports.remove(addr[1])   

    def register_forward_server(self, forward_server):
        forward_server.id=self.unique_forward_server_id
        self.all_forward_servers[forward_server.id]=forward_server
        self.unique_forward_server_id+=1
    
    def unregister_forward_server(self, forward_server):
        del self.all_forward_servers[forward_server.id]
        
    def get_user_friendly_status(self, groups, rfilter):
        status=''
        orphan_forward_server=set(self.all_forward_servers.keys())
        for reflector_id, reflector in self.reflectors.iteritems():
            for fs in reflector.forward_servers:
                orphan_forward_server.remove(fs.id)
                
            if groups!=None and groups.isdisjoint(reflector.clientgroups) and groups.isdisjoint(reflector.fqclientgroups):
                continue
            if rfilter and reflector.class_name.find(rfilter)==-1 and reflector.hostname.find(rfilter)==-1 and reflector.node_id.find(rfilter)==-1 and reflector.name.find(rfilter)==-1:
                continue
            
            status+=reflector.get_user_friendly_status()
            
        if orphan_forward_server:
            status+='orphan_forward_server: %d\n' % (len(orphan_forward_server),)
            
        status+='used port:'
        for i, used_port in enumerate(self.used_ports):
            if i!=0:
                status+=','
            status+=' %d' % (used_port, )
        status+='\n'
        
        return status

    def close_dead_reflectors(self, alive_timeout, alive_interval):
        deads=[]
        for reflector_id, reflector in self.reflectors.iteritems():
            if reflector.check_for_dead(alive_timeout, alive_interval)=='dead':
                deads.append(reflector)
                
        for dead in deads:
            dead.handle_close()
            # handle_close removes the reflector from self.reflectors

    def close_expired_forward_servers(self):
        for forward_server in self.all_forward_servers.itervalues():
            forward_server.check_time_limit()

    def handle_error(self):
        if DEBUG:
            raise
        else:
           asyncore.dispatcher.handle_error(self) 


# =====================================================================
#
# Command
# 
# =====================================================================


class CommandHandler(SRPServerHandler):
    
    help="""
help to get this help

list [filter]
    list all forwards available to the logged user, 
    filter match any string in reflector definition or in the forwards
    
    > list                 # list all connected clients and available forwards  
    > list ssh             # list, using "ssh" to filter the entries 
    > list 192.168.111.23  # or using "192.168.111.23"

status
    detailed list of all forwards available to the logged user,
    including the open tunnels
    
    > status
     
start  <forward_id> [!|*|<ip>|<host>] [p=port] [t=time(s|m|h|d)]
modify <forward_id> [[-|+]!|*|<ip_address>] [p=port] [t=time(s|m|h|d)]

    start or modify a forward
    
       !: is for "self", meaning the IP address of the host running this console  
       *: is for "any", meaning any host
       ip: is one single IP address
       host: is a hostname
       port: is a tcp port
       time: time can in (s)econds, (m)inutes, (h)ours or (d)ays

    The "modify" command can be used multiple time to reconfigure a forward, 
    without closing any already open connections
    
    > start  0 # activate forward 0, allowing the console host to access the forward  
    > modify 0 *  # give access to any host to the running forward 0 
    > modify 0 t=5m # will stop the forward in 5 minutes 
    > modify 0 +91.87.56.178 # add one IP to the list of allowed host
    > modify 0 p=3456 # reopen the forward on a fixed port  
    > modify 0 +91.87.56.178 t=5m p=3456 # change multiples options at once  
    > start 0 91.87.56.178 p=3456 t=5m # start one forward with multiple options
    
stop <forward_id>
    stop an active forward, without closing  already open connections
    
    > stop 0
    
terminate <forward_id>
    stop an active forward closing all related connections
    
    > terminate 0
    
# account management is restricted to user "manager".
"""
    
    help_account="""
user|client  list
    list all existing user or client, showing the groups they are in
     
user|client  add    <name> <password> <space_separated_group_list>
    create a new user or client account 
    
user|client  del    <name>
    remove an existing client or user account
    
user|client  passwd <name> <password>
    change the password of a user or client account
    
user|client  groups <name> <space_separated_group_list>
    change the groups of a user or client.
    You must specify all the groups 
      
group list
    a list of all existing groups and members
    group management is automatic, to create a new group, 
    just add its name in the list of groups of a user or client.   
"""

    re_list=re.compile('list(?:\s+(?P<filter>.*))?$')
    re_status=re.compile('status(?:\s+(?P<filter>.*))?$')
    re_start=re.compile('(?P<what>start|modify)\s+(?P<id>\d+)(\s+(?P<sign>[-+])?(?:(?P<shortcut>[*!])|(?P<hostname>[0-9a-zA-Z][.-0-9a-zA-Z]*)|(?P<ip>(?:(?:25[0-5]|2[0-4]\d|[01]?\d\d?)\.){3}(?:25[0-5]|2[0-4]\d|[01]?\d\d?))))?(?:\s+[pP]=(?P<port>\d+))?(?:\s+[tT]=(?P<delay>\d+[smhd]?))?$')
    re_stop=re.compile('(?P<what>stop|terminate)\s+(?P<id>\d+)$')
    re_group_list=re.compile('group\s+list$')
    re_id_list=re.compile('(?P<what>user|client)\s+list$')
    re_id_del=re.compile('(?P<what>user|client)\s+del\s+(?P<id>[a-zA-Z][\w\.@]*)$')
    re_id_add_passwd=re.compile('(?P<what>(?P<user>user)|client)\s+(?P<cmd>add|passwd)\s+(?P<id>[a-zA-Z][\w\.@]*)\s+(?P<passwd>\S+)(?P<groups>(\s+[a-zA-Z][\w\.@]*(?(user)(:[\w\.@]*)?))*)$')
    # this regex parse client and user differently user allow fully qualified group aka group_name:host_id 
    re_id_groups=re.compile('(?P<what>(?P<user>user)|client)\s+groups\s+(?P<id>[a-zA-Z][\w\.@]*)(?P<groups>(\s+[a-zA-Z][\w\.@]*(?(user)(:[\w\.@]*)?))*)$')
    
    def __init__(self, manager, sock, srp_session):
        SRPServerHandler.__init__(self, sock)
        self.manager=manager
        self.log=logging.getLogger('cmd')
        self.ibuffer=''
        self.set_terminator('\r\n')

        self.srp_session=srp_session
        self.username=None
        self.usergroups=set()
        
        if self.srp_session:
            self.user_db=self.srp_session.server.user_db
            self.handle_authentication(self.srp_session)
        else:
            self.username='user.manager'
            self.welcome()

    def welcome(self):
        self.push('\r\nWelcome')
        if self.srp_session:
            self.push(' %s' % (self.username, ))
        ports=''
        if  self.manager.port_range[1]-self.manager.port_range[0]>0:
            ports+='Dynamic ports (%d-%d)' % self.manager.port_range[:2]
        else:
            ports+='Dynamic ports (disable)'
            
        if self.manager.port_range[2]-self.manager.port_range[1]>1:
            ports+=' fixed ports (%d-%d)' % (self.manager.port_range[1]+1, self.manager.port_range[2])
        else:
            ports+=' fixed port (disable)'
        self.push('\r\ntype help for help. %s.\r\n\r\n' % (ports, ))

        
    def validate_username(self, username, data):
        if not username.startswith('user.'):
            return 'credential must be a "user" credential'
        return None
            
    def handle_authentication_failure(self, message, username):
        SRPServerHandler.handle_authentication_failure(self, message, username)
        self.username=username
        if self.username:
            self.log.error('authentication error user "%s" : %s', username, message)
        else:
            self.log.error('authentication error: %s', message)

    def handle_authentication_success(self, username, key, userdata):
        self.log.info('user login=%s groups=%r', username, userdata)
        self.username=username
        if isinstance(userdata, list):
            self.usergroups=set(userdata)
        self.welcome()

    def collect_incoming_data(self, data):
        self.ibuffer+=data

    def found_terminator(self):
        line=self.ibuffer
        self.ibuffer=''

        self.log.info('received command=%r', line)
        line=line.strip()
        # show user db
        if line=='show':
            for id, (data, _salt, _verifier, _pfid) in self.user_db.passwd.iteritems():
                self.push('%s %r\r\n' % (id, data))
            self.push('\r\n')
            return
        # group list
        match=self.re_group_list.match(line)
        if match:
            groups=dict()
            for id, (data, _salt, _verifier, _pfid) in self.user_db.passwd.iteritems():
                if data:
                    for group in data:
                        groups.setdefault(group, []).append(id)
            group_keys=groups.keys()
            group_keys.sort()
            for group in group_keys:
                self.push('%s %s\r\n' % (group, ' '.join(groups[group])))
            self.push('\r\n')
            return
        # user list
        match=self.re_id_list.match(line)
        if match:
            start=match.group('what')+'.'
            l=len(start)
            ids=filter(lambda x: x.startswith(start), self.user_db.passwd.keys())
            ids.sort()
            for id in ids:
                (data, _salt, _verifier, _pfid)=self.user_db.passwd[id]
                if data:
                    self.push('%s: %s\r\n' % (id[l:], ' '.join(data)))
                else:
                    self.push('%s:\r\n' % (id[l:], ))
            self.push('\r\n')
            return
        # user del
        match=self.re_id_del.match(line)
        if match:
            what, id=match.group('what', 'id')
            fqid='%s.%s' % (what, id)
            try:
                self.user_db.remove(fqid)
            except srplib.NoSuchUser:
                self.push('%s not found: %s\r\n' % (what, id))
            else:
                self.push('%s removed\r\n' % (what, ))
            self.push('\r\n')
            return
        # user add|passwd
        match=self.re_id_add_passwd.match(line)
        if match:
            what, id, cmd, passwd, groups=match.group('what', 'id', 'cmd', 'passwd', 'groups')
            fqid='%s.%s' % (what, id)
            if cmd=='passwd':
                try:
                    self.user_db.get(fqid)
                except srplib.NoSuchUser:
                    self.push('%s not found: %s\r\n' % (what, id))
                    self.push('\r\n')
                    return

            groups=groups.split()
            
            if cmd=='passwd':
                if groups:
                    self.user_db.set(fqid, passwd, groups)
                else:
                    self.user_db.set(fqid, passwd)
                self.push('%s password changed\r\n' % (what, ))
            else:
                self.user_db.set(fqid, passwd, groups)
                self.push('%s %s added\r\n' % (what, id))
            self.push('\r\n')
            return
        # user groups
        match=self.re_id_groups.match(line)
        if match:
            what, id, groups=match.group('what', 'id', 'groups')
            fqid='%s.%s' % (what, id)
            try:
                self.user_db.get(fqid)
            except srplib.NoSuchUser:
                self.push('%s not found: %s\r\n' % (what, id))
                self.push('\r\n')
                return
            
            groups=groups.split()

            self.user_db.set(fqid, None, groups)
            
            self.push('%s groups updated\r\n' % (what, ))
            self.push('\r\n')
            return

        # list [filter]
        match=self.re_list.match(line)
        if match:
            rfilter=match.group('filter')
            count=0
            for reflector in self.manager.reflectors.itervalues():
                # look if user can access this reflector 
                if self.username!='user.manager' and self.usergroups.isdisjoint(reflector.clientgroups) and self.usergroups.isdisjoint(reflector.fqclientgroups):
                    continue
                # check if filter matches
                if rfilter and reflector.class_name.find(rfilter)==-1 and reflector.hostname.find(rfilter)==-1 and reflector.node_id.find(rfilter)==-1 and reflector.name.find(rfilter)==-1:
                    # then search inside the provided forwards
                    found=False
                    for forward_server in reflector.forward_servers:
                        found=forward_server.prot_name.find(rfilter)!=-1 or forward_server.forward_name.find(rfilter)!=-1
                        if found:
                            break
                    if not found:
                        continue

                count+=1
                self.push('%s %s %s %s\r\n' % (reflector.class_name, reflector.hostname,  reflector.node_id, reflector.name))
                for forward_server in reflector.forward_servers:
                    if forward_server.accepting:
                        status=' listening on port %d' % (forward_server.addr[1], )
                    else:
                        status=''
                    self.push('   #%d %s %s%s\r\n' % (forward_server.id, forward_server.prot_name, forward_server.forward_name, status))
            if count==0:
                self.push('251 no match\r\n')
            else:
                self.push('250 OK\r\n')
            self.push('\r\n')
            return
        
        # start
        match=self.re_start.match(line)
        if match:
            what=match.group('what')
            forward_id=match.group('id')
            try:
                forward_id=int(forward_id)
                forward=self.manager.all_forward_servers[forward_id]
                if self.username!='user.manager' and self.usergroups.isdisjoint(forward.reflector_handler.clientgroups) and self.usergroups.isdisjoint(forward.reflector_handler.fqclientgroups):
                    raise KeyError, str(forward_id)
            except (KeyError, ValueError):
                self.push('553 unknown or unavailable forward id: %s\r\n\r\n' % (forward_id, ))
                return
            else:
                if what=='start' and forward.accepting:
                    self.push('553 forward already started, use modify instead\r\n\r\n')
                    return
                elif what=='modify' and not forward.accepting:
                    self.push('553 forward stopped use "start" first\r\n\r\n')
                    return
                    
                if what=='start' or match.group('shortcut')=='!':
                    target=self.getpeername()[0]
                else:
                    target=None
                    
                if match.group('shortcut')=='*':
                    target='0.0.0.0'
                elif match.group('hostname'):
                    hostname=match.group('hostname')
                    try:
                        target=socket.gethostbyname(hostname)
                    except socket.gaierror, e:
                        self.push('512 %s: %s\r\n\r\n' % (hostname, e))
                        return
                elif match.group('ip'):
                    target=match.group('ip')
                    
                if match.group('sign')=='-':
                    if what=='start':
                        self.push('500 cannot remove a host when starting a forward\r\n\r\n')
                        return
                    if target:
                        target='-'+target
                    
                static_port=match.group('port')
                if static_port:
                    static_port=int(static_port)

                delay=match.group('delay')
                if delay!=None:
                    try:
                        delay=int(delay)
                    except ValueError:
                        units=dict(s=1, m=60, h=3600, d=86400)
                        delay=int(delay[:-1])*units[delay[-1]]

                try:
                    if what=='start':
                        forward.start(target, static_port, delay)
                    else:
                        forward.modify(target, static_port, delay)
                except TPRException, e:
                    self.push('530 %s\r\n\r\n' % (str(e), ))
                else:
                    self.push('250 forwarder listening on %s:%d\r\n\r\n' % (forward.getsockname()[0], forward.getsockname()[1], ))
            return
        # stop or terminate
        match=self.re_stop.match(line)
        if match:
            what=match.group('what')
            forward_id=match.group('id')
            try:
                forward_id=int(forward_id)
                forward=self.manager.all_forward_servers[forward_id]
                if self.username!='user.manager' and self.usergroups.isdisjoint(forward.reflector_handler.clientgroups) and self.usergroups.isdisjoint(forward.reflector_handler.fqclientgroups):
                    raise KeyError, str(forward_id)
            except (KeyError, ValueError):
                self.push('553 unknown or unavailable forward id: %s\r\n\r\n' % (forward_id, ))
                return
            else:
                try:    
                    forward.reflector_handler.stop_forward(forward, what=='terminate')    
                except TPRException, e:
                    self.push('530 %s\r\n\r\n' % (str(e), ))
                else:
                    self.push('250 forwarder %sed\r\n\r\n' % (what, ))
            return

        match=self.re_status.match(line)
        if match:
            rfilter=match.group('filter')
            rfilter=match.group('filter')
            groups=self.usergroups
            if self.username=='user.manager':
                groups=None
            status=self.manager.get_user_friendly_status(groups, rfilter)
            status=status.replace('\n', '\r\n')
            self.push(status)
            self.push('\r\n')
            return

        if line=='help':
            help=self.help.replace('\n\n','\n \n').replace('\n', '\r\n')
            self.push(help[2:])
            if self.username=='user.manager':
                help=self.help_account.replace('\n\n','\n \n').replace('\n', '\r\n')
                self.push(help[2:])
            self.push('\r\n')
        elif line in ('exit', 'quit'):
            self.push('bye\r\n\r\n')
            self.close_when_done()
        elif line=='':
            self.push('\r\n')
        else:
            self.push('command unknown\r\n\r\n')

    def handle_close(self):
        self.log.info('bye')
        asynchat.async_chat.handle_close(self)

    def handle_error(self):
        if DEBUG:
            raise
        else:
           asyncore.dispatcher.handle_error(self) 
     
class CommandServer(asyncore.dispatcher):

    def __init__(self, addr, port, reflector_server, srp_server):
        asyncore.dispatcher.__init__(self)
        self.log=logging.getLogger('cmd')
        self.manager=reflector_server
        self.srp_server=srp_server
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.set_reuse_addr()
        self.bind((addr, port))
        self.listen(5)
        self.log.info('server started on %s:%d', addr, port)
        
    def handle_accept(self):
        pair = self.accept()
        if pair is None:
            pass
        else:
            sock, addr = pair
            self.log.info('new incoming connection from %s' % repr(addr))
            srp=None
            if self.srp_server:
                srp=self.srp_server.create_session()
            handler = CommandHandler(self.manager, sock, srp)

# =====================================================================
#
# HTTPServer
# 
# =====================================================================


import string,cgi,time
from os import curdir, sep
import threading
import BaseHTTPServer, urlparse

class HTTPHandler(BaseHTTPServer.BaseHTTPRequestHandler):
    server_version= "TcpProxyReflector/1.1"

    def handle_error(self, request, client_address):
        raise
    
    def log_message(self, format, *args):
        self.server.log.info("[%s] %s", self.client_address[0], format%args)
  
    def do_GET(self, message=None, bg=None):
        self.send_response(200)
        self.send_header('Content-type',    'text/html')
        self.end_headers()

        self.wfile.write(
"""<html><head><title>TCP Proxy Reflector console admin</title>        
<style type="text/css">
table.reflector_list {
    border: 1px #aaaaaa solid;
    border-spacing: 0;
    border-collapse: collapse;
}
table.reflector_list th, table.reflector_list td {
    border: 1px #aaaaaa solid;
    padding: 1px 4px;
}
.left  { text-align:left;  }
.right { text-align:right; }
</style></head>""")

        try:
            body=self._do_GET(message, bg)
        except Exception, e:
            body='<body><p style="background: #FFCCCC;">Unexpexted error: %s</p>\n' % (e, )
            body+='<a href="/">refresh</a>\n</body>\n'
        
        self.wfile.write(body)
        self.wfile.write('</html>\n')
            
    def _do_GET(self, message, bg):

        parse=urlparse.urlparse(self.path)
        path=parse.path

        body=''
        if message==None:
            bg, message='#D8E4F1', 'Tcp Proxy Reflector console admin'

        cmd='<em>unknwon</em>'
        try:
            params=urlparse.parse_qs(parse.query)
            cmd=params.get('cmd', [None])[0]
            if cmd!=None:
                id=int(params.get('id')[0])
                forward_server=self.server.reflector_server.all_forward_servers[id]
                if cmd=='remove':
                    ip=params.get('ip')[0]
                    forward_server.modify('-'+ip, None, None)
                elif cmd=='stop':
                    forward_server.reflector_handler.stop_forward(forward_server, False)
                elif cmd=='terminate':
                    forward_server.reflector_handler.stop_forward(forward_server, True)
        except Exception:
            bg, message='#FFCCCC', 'Unexpected error handling command %r' % (cmd, ) 
                
        
            
        body+='<body><strong>Be careful their is no security using this interface: no authentication, no encryption at all!</strong>'
        if message:
            body+='<p style="background: %s;">%s</p>\n' % (bg, message)
        else:
            body+='<p>&nbsp</p>\n'

        body+='<a href="%s">refresh</a>\n' % (path, )
        if path!='/':
            body+='&nbsp;&nbsp;&nbsp;&nbsp;<a href="/">list all reflectors</a>\n'
        if path!='/accounts':
            body+='&nbsp;&nbsp;&nbsp;&nbsp;<a href="/accounts">accounts</a>\n'
        
        if path=='/accounts':
            body+='<p>Users</p>\n<table class="reflector_list"><tr><th>User</th><th>groups</th></tr>\n'
            
            groups=dict()
            clients=''
            for id, (data, _salt, _verifier, _pfid) in self.server.reflector_server.srp_server.user_db.passwd.iteritems():
                if data==None:
                    data=[]
                for group in data:
                    groups.setdefault(group, []).append(id)
                if id.startswith('user.'):
                    body+='<tr><td>%s</td><td>%s</td></tr>' % (id[5:], ', '.join(data))
                elif id.startswith('client.'):
                    clients+='<tr><td>%s</td><td>%s</td></tr>' % (id[7:], ', '.join(data))
                    
            body+='</table>\n<p>Clients</p>\n<table class="reflector_list"><tr><th>Client</th><th>groups</th></tr>\n'
            body+='%s</table>\n<p>Groups</p>\n<table class="reflector_list"><tr><th>Groups</th><th>members</th></tr>' % (clients, )
                
            group_keys=groups.keys()
            group_keys.sort()
            for group in group_keys:
                body+='<tr><td>%s</td><td>%s</td></tr>' % (group, ' '.join(groups[group]))
    
            body+='</table>\n'
            
            
        else:
            body+='<table class="reflector_list">\n'
    
            status=''
            if not self.server.reflector_server.reflectors:
                status+='no clients.&nbsp;&nbsp;&nbsp;'
            
            status+='port range:'
            if  self.server.reflector_server.port_range[1]-self.server.reflector_server.port_range[0]>0:
                status+=' dynamic (%d-%d)' % self.server.reflector_server.port_range[:2]
            else:
                status+=' dynamic (disable)'
                
            if self.server.reflector_server.port_range[2]-self.server.reflector_server.port_range[1]>1:
                status+=' fixed (%d-%d)' % (self.server.reflector_server.port_range[1]+1, self.server.reflector_server.port_range[2])
            else:
                status+=' fixed (disable)'
            
            body+="""<thead>
    <tr style="background:#F8E0B0;"><th>Class name</th><th colspan="3">username @ ip:port</th><th colspan="2">hostname</th><th>node id</th><th rowspan="3"> in </th><th rowspan="3"> out </th></tr>
    <tr style="background:#D8E4F1;"><th></th><th>Id</th><th>protocol</th><th>forward name</th><th colspan="3">listening on port, accept connection from</th></tr>
    <tr style="background:#FFFFCE;"><th colspan="4"></th><th>tunnel Id</th><th colspan="2">client addr:port</th></tr>
    <tr><td colspan="9">%s</td></tr>
    </thead>\n
     """ % (status, )                         
            
            for reflector_id, reflector in self.server.reflector_server.reflectors.iteritems():
                path_name='/%s.%d' % reflector.getpeername()
                if path!='/' and path!=path_name and path!='/'+reflector.class_name:
                    continue 
    
                body+='<tr style="background:#F8E0B0;">\n'
                clientname=''        
                if reflector.clientname:
                    clientname=reflector.clientname[7:]+' @ '
                body+='<th colspan="1" class="left"><a href="/%s">%s</a></th>\n' % (reflector.class_name, reflector.class_name,)
                body+='<th colspan="3" class="left">%s<a href="%s">%s</a></th>\n' % (clientname, path_name, reflector.name)
                body+='<th colspan="2" class="left">%s</th>\n' % (reflector.hostname, )
                body+='<th colspan="1" class="left">%s</th>\n' % (reflector.node_id, )
                body+='<th>%dk</th><th>%dk</th></tr>\n' % (reflector.ingoing/1024, reflector.outgoing/1024)
    
                for forward_server in reflector.forward_servers:
                    listening, color='<td colspan="3">not activated</td>', ' style="background:#D8E4F1;"'
                    start, stop, terminate='Start', '', ''
                    time_limit, host='', self.client_address[0]
                    if forward_server.accepting:
                        allowed_targets=','.join(map(lambda x:'<a href="%s?id=%d&cmd=remove&ip=%s" title="remove">%s</a>' % (path, forward_server.id, x, x), forward_server.allowed_targets))
                        listening='<td colspan="3">port:%d accept:%s</td>' % (forward_server.getsockname()[1], allowed_targets)
                        color=' style="background:#D8F1E4;"'
                        start='Modify'
                        stop='<a href="%s?id=%d&cmd=stop">Stop</a>' % (path, forward_server.id,)
                        host=''
                        if forward_server.time_expiration:
                            delay=forward_server.time_expiration-time.time()
                            if delay>0:
                                time_limit='%dH%02dm%02ds' % (delay/3600,delay/60%60, delay%60)
                            else:
                                time_limit='closing'
                        else:
                            time_limit='no time limit'
                    
                    post_body=''
                    for tunnel_id, forwarder in reflector.tunnels.iteritems():
                        if forwarder.forward_server==forward_server:
                            post_body+='<tr style="background: #FFFFCE;"><td colspan="4" style="background:#FFF;"></td>'
                            addr, port=forwarder.getpeername()
                            post_body+='<td class="left">tunnel %d</td><td colspan="2" class="right">%s:%d</td>\n' % (tunnel_id, addr, port)
                            post_body+='<td class="right">%dk</td><td class="right">%dk</td></tr>\n' % (forwarder.outgoing/1024, forwarder.ingoing/1024)
                            
                    if post_body:
                        terminate='<a href="%s?id=%d&cmd=terminate">Terminate</a>' % (path, forward_server.id, )
    
                    body+='<tr%s><td style="background:#FFF;"></td><td>#%d</td><td>%s</td><td>%s</td>%s<td colspan="2">%s</td></tr>\n' %(color, forward_server.id, forward_server.prot_name, forward_server.forward_name, listening, time_limit)
                    body+='<tr><td colspan="2"></td><td colspan="5"><form style="margin:0;" method="post" action="%s"> %s %s <input type="hidden" value="start" name="cmd"/><input type="hidden" value="%d" name="id"/><input type="submit" size="12" value="%s"/> host:<input type="text" value="%s" name="host" size="25"/> port:<input type="text" name="port" size="5" /> time:<input type="text" name="time" size="3" /></form></td><td colspan="2"></td></tr>\n' % (path, stop, terminate, forward_server.id, start, host)
                    body+=post_body
                        
                            
            body+='</table>\n'
            body+='</body>'
        return body

    def do_POST(self):
        try:
            ctype, pdict = cgi.parse_header(self.headers.getheader('content-type'))
            form=cgi.FieldStorage(fp=self.rfile,
                        headers=self.headers, environ = {'REQUEST_METHOD':'POST'},
                        keep_blank_values = 1, strict_parsing = 1)
            host=form['host'].value
            if host=='*':
                host='0.0.0.0'
            elif host=='!':
                host=self.client_address[0]
            else:
                host=socket.gethostbyname(host)
    
            forward=self.server.reflector_server.all_forward_servers[int(form['id'].value)]
            
            port=form['port'].value
            if port=='':
                port=None
            else:
                try:
                    port=int(port)
                except ValueError:
                    self.do_GET("Invalid port: %r" % (port, ), '#FFCCCC')
                    return
                
            delay=form['time'].value
            if delay=='':
                delay=None
            else:
                try:
                    delay=int(delay)
                except ValueError:
                    units=dict(s=1, m=60, h=3600, d=86400)
                    try:
                        delay=int(delay[:-1])*units[delay[-1]]
                    except ValueError, IndexError:
                        self.do_GET("Invalid time: %r" % (delay, ), '#FFCCCC')
                        return
                    
            if forward.accepting:
                forward.modify(host, port, delay)
            else:
                forward.start(host, port, delay)
#        except TPRException, e:
        except Exception, e:
            self.server.log.exception('handling post request')
            self.do_GET("Error: %s" % (str(e), ), '#FFCCCC')
        else:
            self.do_GET('Success: new forwarder listening on %s:%d' % (forward.getsockname()[0], forward.getsockname()[1]), '#D8F1E4')


class HTTPServer(BaseHTTPServer.HTTPServer):
    allow_reuse_address=True
    log='overwritten after __init__'
    
    def handle_error(self, request, client_address):
        raise
   

# =====================================================================
#
# Console with authentication
# 
# =====================================================================

class TelnetSRP(telnetlib.Telnet):
    """add SRP authentication"""       
    def open(self, host, port, user=None, password=None):
        
        try:
            import readline
        except ImportError:
            pass
        self.eof = 0
        if not port:
            port = TELNET_PORT
        self.host = host
        self.port = port
        if user and password:
            self.sock, _key = srplib.sock.SRPSocket(host, port, user, password)
        else:
            self.sock = socket.create_connection((host, port))
        

def start_console(addr, port, user=None, password=None):

    srp_license=srplib.srp_license            

    console=TelnetSRP()
    auto_reconnect=True
    input, eof='', False
    if user:
        user='user.'+user
    while not eof and auto_reconnect:
        try:
            console.open(addr, port, user=user, password=password)
        except srplib.NoSuchUser:
            print 'unknown user %s' % (user, )
            return
        except srplib.AuthFailure:
            print 'authentication failure'
            return
        else:
            if srp_license:
                print srp_license
                srp_license=None
            # display welcome message
            line=console.read_until('\r\n\r\n')
            line=line[:-2]
            print line
                
        auto_reconnect=False
        try:
            eof=False
            while not eof:
                if not input:
                    input=raw_input('>')
                auto_reconnect=True
                console.write('%s\r\n' % (input, ))
                line='continue'
                while line:
                    last_line=line
                    line=console.read_until('\r\n')
                    line=line[:-2]
                    if line:
                        print line
                input=''
                eof=(last_line=='bye')
                
        except EOFError:
            pass


def start_client(log, classname, hostname, node_id, clientname, srp_client, forwards, server, alive_interval, alive_timeout, forever):
    """forever can be a callable or True or False"""
    def factory():
        if isinstance(server, tuple):
           host, port=server
        else:
            try:
                import dns.resolver
                answers=dns.resolver.query(server, 'SRV')
                for rdata in answers:
                    host=str(rdata.target)[:-1]
                    port=int(rdata.port)
            except dns.exception.DNSException:
                log.error('cannot resolve SRV pointer for %s',  server)
            else:
                log.info('use SRV pointer for %s: %s:%d',  server, host, port)

        try:
            client=ClientHandler(classname, hostname, node_id,
                                   host, port,
                                   forwards,
                                   srp_client)
        except socket.error, e:
            log.error('connecting to %s:%d (%s)', host, port, e)
            return None
        else:
            return client

    if isinstance(server, tuple):
        server_display='%s:%d' % server
    else:
        server_display=server

    log.info('start TCP Proxy Reflector client, connect to server is %s', server)
    client=None

    next=time.time()+alive_interval
    while forever==True or (callable(forever) and forever()): # or asyncore.socket_map:
        try:
            if not client:
                client=factory()
                next=time.time()+alive_interval
            asyncore.loop(timeout=1, count=1)
            if client and client.connected:
                if time.time()>next:
                    if client.check_for_dead(alive_timeout, alive_interval)=='dead':
                        client.close()
                        client=None
                    else:
                        next=time.time()+alive_interval
            else:
                time.sleep(alive_interval)
                client=None
                
        except Exception, e:
            log.exception('Unexpected exception')
            time.sleep(alive_interval)
            next=time.time()+alive_timeout
