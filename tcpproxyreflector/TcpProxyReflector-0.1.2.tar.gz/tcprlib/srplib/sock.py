#/bin/env python
"""
SRP authenticated sockets.
(c) alain.spineux@gmail.com
"""

import socket, base64, SocketServer, time

import srplib

def SRPSocket(host, port, username, passphrase = None):
    """Create a connection to the given host and port, which must be
    running the SRPServer.  Perform authentication and return the socket
    and session key if successful, or raise an exception if not."""

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((host, port))
    key = SRPAuth(sock, username, passphrase)
    return (sock, key)

def SRPAuth(sock, username, passphrase = None):
    """Perform an SRP authentication on a socket.  Return the session key
    if authentication was successful, or raise an exception if it was not.
    The other end of the socket must be ready to receive the SRP
    commands."""

    if not passphrase:
        passphrase = getpass.getpass('Enter passphrase for %s: ' % username)
 
    srp=srplib.SRPClient(username, passphrase)   
    # Send the USER command.
    
    sock.send('USER %s\n' % username)
    
    # Get the client-side keys and send the public one.
    
    sock.send(srplib.encode_long(srp.A))
    
    # Read the response.
    
    line=readline(sock)
    if line[0:3]!='KEY':
        raise srplib.NoSuchUser, line
    s = base64.decodestring(read_chunk(sock))
    B = srplib.string_to_long(base64.decodestring(read_chunk(sock)))
    u = srplib.string_to_long(base64.decodestring(read_chunk(sock)))
    
    # Now calculate the session key and send the proof.
    srp.client_key(s, B, u)
    
    sock.send(srplib.encode_string(srp.m))
    
    line = readline(sock)
    if line[0:3] != 'AOK':
        raise srplib.AuthFailure, line
    
    # Authenticate the host.
    m=base64.decodestring(read_chunk(sock))
    m1=srp.host_authenticator()   
    if m!=m1:
        raise srplib.AuthFailure, "Host authentication failed."
    
    # All done, return the session key.
    
    return srp.K

class SRPRequestHandler(SocketServer.StreamRequestHandler):

    def handle_authentication_failure(self, message, username=None):
        pass

    def handle_authentication_success(self, username, key):
        pass
    
    def validate_username(username, data):
        """useful to validate on thing other than password, 
        like time, IP source, member of a group ...
        return "error message" ot None if OK""" 
        return None # always ok
    
    def setup(self):
        SocketServer.StreamRequestHandler.setup(self)
        self.srp=self.server.srp_server.create_session()

        line=self.rfile.readline()
        
        if not line:
            self.handle_authentication_failure('authentication mismatch', None)
            return
        elif line.startswith('USER'):
            l=line.split()
            if len(l)==2:
                username=l[1]
        if not username:
            self.wfile.write('USER is missing.\r\n')
            self.handle_authentication_failure('no user', None)
            return

        A=srplib.string_to_long(base64.decodestring(read_long(self.rfile)))
        try:
            self.srp.lookup(username, A)
        except srplib.NoSuchUser:
            self.wfile.write('No such user "%s".\n' % username)
            self.handle_authentication_failure('No such user', username)
            return

        msg=self.validate_username(username)
        if msg:
            self.wfile.write('user rejected: "%s".\n' % username)
            self.handle_authentication_failure(msg, username)
        
        self.wfile.write('KEY\n')
        self.wfile.write(srplib.encode_string(self.srp.s))
        self.wfile.write(srplib.encode_long(self.srp.B))
        self.wfile.write(srplib.encode_long(self.srp.u))

        line=self.rfile.readline()
        _empty_line=self.rfile.readline()
        m1=base64.decodestring(line)
        if m1!=self.srp.m:
            self.wfile.write('Client authentication failed.\n')
            self.handle_authentication_failure('password mismatch', username)
            return

        self.wfile.write('AOK\n')
        self.wfile.write(srplib.encode_string(self.srp.host_authenticator()))
        self.handle_authentication_success(username, self.srp.K, self.srp.data)


def readline(sock):
    buf=''
    ch='NOT EOF'
    while ch and ch!='\n':
        ch=sock.recv(1)
        buf+=ch
    return buf

def read_chunk(sock):
    ll=[]
    while 1:
        line=readline(sock)
        if not line:
            raise EOFError
        l=line.strip()
        if not l:
            break
        ll.append(l)
    
    return ''.join(ll)


def readline2(rfile):
    buf=''
    ch='NOT EOF'
    while ch and ch!='\n':
        ch=rfile.read(1)
        buf+=ch
    return buf

def read_long(rfile):
    ll=[]
    while 1:
        line=readline2(rfile)
        if not line:
            raise EOFError
        l=line.strip()
        if not l:
            break
        ll.append(l)
    
    return ''.join(ll)


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

    class EchoHandler(SRPRequestHandler):

        srp_server=srplib.PickleDB('passwd')
            
        def handle_authentication_failure(self, message, username=None):
            if username:
                print 'authentication error: "%s" user "%s"' % (message, username)
            else:
                print 'authentication error: "%s"' % (message,)
    
        def handle_authentication_success(self, username, key, user_data):
            print 'session opened for user "%s"' % (username, )
        
        def validate_username(username, user_data):
            return None

        def handle(self):
            line='continue'
            while line and line not in ('quit\r\n', 'exit\r\n'):
                line=self.rfile.readline()
                print 'received : %r' % (line, )
                if line:
                    self.wfile.write(line)
            if line in ('quit\r\n', 'exit\r\n'):
                self.wfile.write('bye\r\n')

        def handle_authentication_failure(self, message, username):
            if username:
                print 'authentication error: "%s" user "%s"' % (message, username)
            else:
                print 'authentication error: "%s"' % (message,)
    
        
    class MyForkingTCPServer(SocketServer.ForkingTCPServer):
        allow_reuse_address=True
            
    if options_args.server:
        user_db=srplib.PickleDB('passwd')
        user_db.set('mary', 'poppins')
        srp_server=srplib.SRPServer(user_db)
        s=MyForkingTCPServer(('127.0.0.1', options_args.port), EchoHandler)
        s.srp_server=srp_server
        print 'echo server started'
        s.serve_forever()

    else:
        if options_args.username==None:
            parser.error('username is required')
        if options_args.password==None:
            import getpass
            options_args.password=getpass.getpass('Enter password for %s: ' % options_args.username)
            
        try:
            sock, _key=SRPSocket('127.0.0.1', options_args.port, options_args.username, options_args.password)
        except srplib.NoSuchUser, e:
            print 'user not found', e
        except srplib.AuthFailure, e:
            print 'authentication failure', e
        else:
            print 'Logged in'
            sock.send('hello world\r\n')
            time.sleep(0.1) # should use file.readline() instead
            received=sock.recv(1024)
            print received,
            sock.send('exit\r\n')
            time.sleep(0.1) # should use file.readline() instead
            received=sock.recv(1024)
            print received,
            sock.close()
