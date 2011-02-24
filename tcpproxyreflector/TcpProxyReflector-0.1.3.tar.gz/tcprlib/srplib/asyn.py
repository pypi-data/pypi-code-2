#/bin/env python
"""
asynchat SRP authenticated sockets.
(c) alain.spineux@gmail.com
"""

import socket, base64
import asynchat, asyncore

import srplib


class SRPAsyncData:
    def __init__(self, handler, srp):
        """handler is an asynchat.async_chat and srp can be a SRPClient or SRPServer"""
        self.ibuffer=''
        self.state='start'
        self.save_collect_incoming_data=handler.collect_incoming_data
        self.save_found_terminator=handler.found_terminator
        try:
            self.save_terminator=handler.get_terminator()
        except AttributeError:
            pass
        self.srp=srp

        self.s=self.B=self.u=None # client side        
        self.username=self.A=None # server side

class _SRPHandler(asynchat.async_chat):

    def _srp_handle_authentication(self, srp):
        # print 'handle_authentication'
        self._srp_data=SRPAsyncData(self, srp)
        self.collect_incoming_data=self._srp_collect_incoming_data
        self.found_terminator=self._srp_found_terminator
        self.set_terminator('\n')

    def _srp_switch_back(self):
        self.collect_incoming_data=self._srp_data.save_collect_incoming_data
        self.found_terminator=self._srp_data.save_found_terminator
        if hasattr(self._srp_data, 'save_terminator'):
            self.set_terminator(self._srp_data.save_terminator)
        del self._srp_data

    def _srp_collect_incoming_data(self, data):
        raise NotImplementedError

    def _srp_found_terminator(self):
        raise NotImplementedError


class SRPServerHandler(_SRPHandler):

    def validate_username(self, username, user_data):
        """useful to validate on thing other than password, 
        like time, IP source, member of a group ...
        return "error message" ot None if OK""" 
        return None # always ok
            
    def handle_authentication(self, srp_session):
        # print 'handle_authentication'
        self._srp_handle_authentication(srp_session)
        
    def handle_authentication_failure(self, message, username):
        pass
    
    def handle_authentication_success(self, username, key, userdata):
        pass

    def _srp_collect_incoming_data(self, data):
        # print '_srp_collect_incoming_data', data
        self._srp_data.ibuffer+=data

    def _srp_found_terminator(self):
        # print '_srp_found_terminator %s %r + %r' % (self._srp_data.state, self._srp_data.ibuffer, self.get_terminator())
        line=self._srp_data.ibuffer
        self._srp_data.ibuffer=''
        if self._srp_data.state=='start':
            if not line:
                self.handle_authentication_failure('authentication mismatch', None)
            elif line.startswith('USER'):
                l=line.split()
                if len(l)==2:
                    self._srp_data.username=l[1]
                    self._srp_data.state='wait_for_A'
                    self.set_terminator('\n\n')
            if not self._srp_data.username:
                self.push('USER is missing.\r\n')
                self.close_when_done()
                self.handle_authentication_failure('no user', None)
                return
        elif self._srp_data.state=='wait_for_A':
            self._srp_data.A=srplib.string_to_long(base64.decodestring(line))
            try:
                self._srp_data.srp.lookup(self._srp_data.username, self._srp_data.A)
            except srplib.NoSuchUser:
                self.push('No such user "%s".\n' % self._srp_data.username)
                self.handle_authentication_failure('No such user', self._srp_data.username)
            else:
                msg=self.validate_username(self._srp_data.username, self._srp_data.srp.data)
                if msg:
                    self.push('user rejected: "%s".\n' % self._srp_data.username)
                    self.handle_authentication_failure(msg, self._srp_data.username)
                
                self.push('KEY\n')
                self.push(srplib.encode_string(self._srp_data.srp.s))
                self.push(srplib.encode_long(self._srp_data.srp.B))
                self.push(srplib.encode_long(self._srp_data.srp.u))
                self._srp_data.state='wait_for_proof'
                self.set_terminator('\n\n') # be careful this is a double \n
                
        elif self._srp_data.state=='wait_for_proof':
            m1=base64.decodestring(line)
            if m1!=self._srp_data.srp.m:
                self.push('Client authentication failed.\n')
                self.handle_authentication_failure('password mismatch', self._srp_data.srp.username)
            else:
                self.push('AOK\n')
                self.push(srplib.encode_string(self._srp_data.srp.host_authenticator()))
                self.handle_authentication_success(self._srp_data.srp.username, self._srp_data.srp.K, self._srp_data.srp.data)
                self._srp_switch_back()


class SRPClientHandler(_SRPHandler):

    def handle_authentication(self, srp_client):
        #print 'handle_authentication'
        self._srp_handle_authentication(srp_client)
        self.push('USER %s\n' % self._srp_data.srp.username)
        self.push(srplib.encode_long(self._srp_data.srp.A))

    def handle_authentication_failure(self, message):
        #print 'handle_authentication_failure', message
        self.handle_close()

    def handle_authentication_success(self, username, key):
        #print 'handle_authentication_success', username
        pass
        
    def _srp_collect_incoming_data(self, data):
        #print '_srp_collect_incoming_data', data
        self._srp_data.ibuffer+=data

    def _srp_found_terminator(self):
        #print '_srp_found_terminator %s %r + %r' % (self._srp_data.state, self._srp_data.ibuffer, self.get_terminator())
        line=self._srp_data.ibuffer
        self._srp_data.ibuffer=''
        if self._srp_data.state=='start':
            if line[0:3]!='KEY':
                self.handle_authentication_failure(line)
            self._srp_data.state='wait_for_s'
            self.set_terminator('\n\n')

        elif self._srp_data.state=='wait_for_s':
            self._srp_data.s=base64.decodestring(line)
            self._srp_data.state='wait_for_B'

        elif self._srp_data.state=='wait_for_B':
            self._srp_data.B=srplib.string_to_long(base64.decodestring(line))
            self._srp_data.state='wait_for_u'
            
        elif self._srp_data.state=='wait_for_u':
            self._srp_data.u=srplib.string_to_long(base64.decodestring(line))
            self._srp_data.srp.client_key(self._srp_data.s, self._srp_data.B, self._srp_data.u)
            self.push(srplib.encode_string(self._srp_data.srp.m))
            self._srp_data.state='wait_for_AOK'
            self.set_terminator('\n')
            
        elif self._srp_data.state=='wait_for_AOK':
            if  line[0:3]!='AOK':
                self.handle_authentication_failure(line)
            self._srp_data.state='wait_for_m'
            self.set_terminator('\n\n')
            
        elif self._srp_data.state=='wait_for_m':
            m=base64.decodestring(line)
            m1=self._srp_data.srp.host_authenticator()
            if m!=m1:
                self.handle_authentication_failure("Host authentication failed")
            else:
                self.handle_authentication_success(self._srp_data.srp.username, self._srp_data.srp.K)
                self._srp_switch_back()

if __name__ == "__main__":

    import optparse
    parser=optparse.OptionParser()
    parser.add_option('-s', '--server',  dest='server', action='store_true', default=False, help='start the server')
    parser.add_option('-c', '--console', dest='server', action='store_false', default=False, help='start the client')
    parser.add_option('-p', '--port',    dest='port', type='int', default='12345', help='the port', metavar='port')
    parser.add_option('-d', '--database',  dest='database', help='the user database filename', default='passwd', metavar='filename')
    parser.add_option('-u', '--user',    dest='username', help='the username', default=None, metavar='username')
    parser.add_option('-a', '--password',dest='password', help='the user password', default=None, metavar='password')

    (options_args, args) = parser.parse_args()

    class EchoHandler(SRPServerHandler):
    
        def __init__(self, sock, srp_session):
            SRPServerHandler.__init__(self, sock)
            self.ibuffer=''
            self.set_terminator('\r\n')
            self.handle_authentication(srp_session)
           
        def handle_authentication_failure(self, message, username):
            SRPServerHandler.handle_authentication_failure(self, message, username)
            if username:
                print 'authentication error: "%s" user "%s"' % (message, username)
            else:
                print 'authentication error: "%s"' % (message,)
    
        def handle_authentication_success(self, username, key, userdata):
            print 'session opened for user "%s"' % (username, )

        def collect_incoming_data(self, data):
            self.ibuffer+=data
    
        def found_terminator(self):
            print 'received : %r' % (self.ibuffer, )
            if self.ibuffer in ('exit', 'quit'):
                self.push('bye\r\n')
                self.close_when_done()
            else:
                self.push('%s\r\n' % (self.ibuffer, ))
            self.ibuffer=''
            
        def handle_error(self):
            raise
    
    
    class EchoServer(asyncore.dispatcher):
    
        def __init__(self, host, port, srp_server):
            asyncore.dispatcher.__init__(self)
            self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
            self.set_reuse_addr()
            self.bind((host, port))
            self.listen(5)
            self.srp_server=srp_server
            print 'echo server started'
            
        def handle_accept(self):
            sock, addr=self.accept()
            print 'new incoming connection from %s' % repr(addr)
            handler=EchoHandler(sock, self.srp_server.create_session())

    class EchoClient(SRPClientHandler):
    
        def __init__(self, host, port, srp_client):
            SRPClientHandler.__init__(self)
            self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
            self.connect( (host, port) )
            self.srp_client=srp_client

            self.ibuffer=''
            self.set_terminator('\r\n')
            
        def handle_connect(self):
            self.handle_authentication(self.srp_client)
          
        def handle_authentication_failure(self, message):
            SRPClientHandler.handle_authentication_failure(self, message)
            print 'authentication failure: %s' % (message, )
    
        def handle_authentication_success(self, username, key):
            print 'connected as %s' % (username, )
            self.push('hello world\r\n')

        def collect_incoming_data(self, data):
            self.ibuffer+=data
    
        def found_terminator(self):
            line=self.ibuffer
            self.ibuffer=''
            if line=='hello world':
                print line
                self.push('exit\r\n')
            elif line=='bye':
                print line
                self.close_when_done()
            else:
                print 'protocol mismatch, received %r' %(line)
                self.close_when_done()
            
        def handle_error(self):
            """to get a full stack trace"""
            raise
            
    if options_args.server:
        user_db=srplib.PickleDB('passwd')
        user_db.set('mary', 'poppins')
        srp_server=srplib.SRPServer(user_db)
        EchoServer('127.0.0.1', options_args.port, srp_server)
    else:
        if options_args.username==None:
            parser.error('username is required')
        if options_args.password==None:
            import getpass
            options_args.password=getpass.getpass('Enter password for %s: ' % options_args.username)
            
        EchoClient('', options_args.port, srplib.SRPClient(options_args.username, options_args.password))
        
    asyncore.loop()        

