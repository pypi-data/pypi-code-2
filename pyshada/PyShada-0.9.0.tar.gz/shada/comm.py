## \brief Communication Protocol from Shell to Python namespace.
#
# \section scenario Scenario
#
# User will interleave shell command and Python code.  They want to
# run Python code for some points when they run a shell command.  The
# invokation may pass some information generated dynamic by shell
# command to Python code.  We need a mechanisim for passing
# information from shell to Python.  These information include
# environment variables, stdin, stdout, and arguments.
#
# This module provide a protocol running a server and several clients.
# Python code that call shell would host a server for accepting
# requests from client, while clients are an agent program called by
# shell command to passing requested command and informations to
# Python code.  When a server receives a request, it extracts
# informations from the request and calling a callable specified by
# the requested command.
#
# The server and clients are connected through a unix domain socket.
# The server pass the listened address to clients through environment
# variable, PYSHELL_SERVER.
#
# The caller function, run*(), will replace Python calls, in the shell
# command, with running agent program.  The agent program will connect
# to the server to passing a request and information.
#
# Once a client connect to the server.  It pass a request in following
# format.
#
# <verbatim>
# REQ<length of following object><a serialized request object>
# </verbatim>
# 
# Packets for stdin and stdout are following the request.  The client
# can encapsulate the data from stdin into a packet and passed to
# server.  In reverse, the server can pass stdout stream by
# encapsulate content in packets.  The packet format is
#
# <verbatim>
# IPK<data length><data>
# OPK<data length><data>
# </verbatim>
#
# To close a stdin or stdout of a session.  Send a 'IED' or 'OED'.  A
# byte of exit code will follow the 'OED'.
#
# <verbatim>
# IED
# OED<exit code>
# </verbatim>
#
# The fromat of request object looks like following example
#
# <verbatim>
# request = {'request': 'callable name',
#            'environ': {....},
#            'args': ('arg1', 'arg2', ...}
#            }
# </verbatim>
# 
#
import os
import struct
import cPickle as pickle
import asyncore

class server_session(object):
    def __init__(self, server, sock, peer_addr):
        self._server = server
        self._sock = sock
        self._peer_addr = peer_addr
        self._calling_gen = None    # generator
        self._ibuf = []             # input buffer
        self._exit_flag = False
        pass

    def _run(self, callable_name, args, env):
        server = self._server
        calling_gen = server._ns[callable_name](args, env, self)
        if calling_gen == None:
            self.exit(0)
        else:
            calling_gen.next()
            self._calling_gen = calling_gen # a generator
            pass
        pass
    
    def _handle_req(self):
        if self._calling_gen:
            raise RuntimeError, 'this session have called a callable'
        
        sock = self._sock
        sz_str = sock.recv(4)
        if len(sz_str) != 4:
            raise RuntimeError, 'invalid REQ packet, invalid size'
        
        sz = struct.unpack('i', sz_str)[0]
        if sz < 0:
            raise ValueError, 'invalid REQ packet, invalid size'

        data = sock.recv(sz)
        req = pickle.loads(data)
        callable_name = req['request']
        args = req['args']
        env = req['environ']

        self._run(callable_name, args, env)
        pass

    def _handle_ipk(self):
        if not self._calling_gen:
            raise RuntimeError, 'this session have not yet call any callable'
        calling_gen = self._calling_gen

        sock = self._sock
        sz_str = sock.recv(4)
        if len(sz_str) != 4:
            raise RuntimeError, 'invliad IPK packet, invalid size'
        
        sz = struct.unpack('i', sz_str)[0]
        if sz < 0:
            raise ValueError, 'invalid IPK packet, invalid size'

        data = sock.recv(sz)
        self._ibuf.append(data)
        try:
            calling_gen.next()
        except StopIteration:
            self.exit(0)
            pass
        pass

    def _handle_ied(self):
        if not self._calling_gen:
            return

        self._ibuf.append(None)
        calling_gen = self._calling_gen
        try:
            calling_gen.next()
        except StopIteration:
            self.exit(0)
            pass
        pass

    def handle_connection(self):
        if self._exit_flag:
            raise RuntimeError, 'the session is closed'
        
        sock = self._sock
        
        cmd = sock.recv(3)
        if cmd == 'REQ':
            self._handle_req()
        elif cmd == 'IPK':
            self._handle_ipk()
        elif cmd == 'IED':
            self._handle_ied()
        else:
            raise RuntimeError, 'invalid packet %s' % (cmd)
        pass

    def recv(self):
        last = self._ibuf.pop(0)
        return last

    def send(self, data):
        sz = len(data)
        sz_str = struct.pack('i', sz)
        
        pkt = 'OPK' + sz_str + data
        sock = self._sock
        sock.send(pkt)
        pass

    def exit(self, code):
        if self._exit_flag:
            return
        
        pkt = 'OED' + chr(code)
        sock = self._sock
        sock.send(pkt)
        sock.close()
        
        self._exit_flag = True
        pass

    def get_sock(self):
        return self._sock

    def is_exited(self):
        return self._exit_flag
    pass

class server(object):
    def __init__(self, ns):
        self._addr = self._make_server_addr()
        self._ns = ns
        pass

    def _make_server_addr(self):
        import random
        pid = os.getpid()
        rn = random.randint(0, 10000)
        addr = '/tmp/pyshell-server-%d-%d' % (pid, rn)
        return addr

    def listen(self):
        import socket

        sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        sock.bind(self._addr)
        sock.listen(5)
        self._sock = sock
        pass

    def accept(self):
        sock = self._sock
        if not sock:
            raise ValueError, 'invalid socket'
        client_sock, peer_addr = sock.accept()
        session = server_session(self, client_sock, peer_addr)
        return session

    def close(self):
        sock = self._sock
        sock.close()
        self._sock = None

        os.remove(self._addr)
        pass

    def get_addr(self):
        return self._addr

    def get_sock(self):
        return self._sock

    def handle(self):
        class server_dispatcher(object):
            def __init__(self, server, socket_map):
                self._sock = server.get_sock()
                self._server = server
                self._socket_map = socket_map
                pass

            def readable(self):
                return True

            def writable(self):
                return False

            def handle_error(self):
                import traceback
                traceback.print_exc()
                pass

            def handle_read_event(self):
                server = self._server
                session = server.accept()
                if server.is_closed():
                    socket_map = self._socket_map
                    sock = self._sock
                    del socket_map[sock]
                    return

                socket_map = self._socket_map
                sock = session.get_sock()
                socket_map[sock] = session_dispatcher(session, server,
                                                      socket_map)
                pass
            pass

        class session_dispatcher(object):
            def __init__(self, session, server, socket_map):
                self._session = session
                self._server = server
                self._server_sock = server.get_sock()
                self._socket_map = socket_map
                pass

            def readable(self):
                return True

            def writable(self):
                return False

            def handle_error(self):
                import traceback
                traceback.print_exc()
                pass

            def handle_read_event(self):
                session = self._session
                session.handle_connection()
                if session.is_exited():
                    sock = session.get_sock()
                    del self._socket_map[sock]
                    pass

                server = self._server
                if server.is_closed():
                    sock = self._server_sock
                    del self._socket_map[sock]
                    pass
                pass
            pass
        
        sock_map = {}
        sock = self._sock
        serv_disp = server_dispatcher(self, sock_map)
        sock_map[sock] = serv_disp
        
        asyncore.loop(map=sock_map)
        pass

    def is_closed(self):
        return self._sock == None
    pass

class client(object):
    def __init__(self, callable_name, args, env, stdin, stdout):
        self._callable_name = callable_name
        self._args = args
        self._env = env
        self._stdin = stdin
        self._stdout = stdout
        self._sock = None
        pass

    def _server_addr(self):
        env = self._env
        addr = env['PYSHELL_SERVER']
        return addr

    def _connect(self, addr):
        import socket

        sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        sock.connect(addr)
        return sock

    def connect(self):
        server_addr = self._server_addr()
        sock = self._connect(server_addr)
        
        req = {'request': self._callable_name,
               'args': self._args,
               'environ': self._env}
        req_str = pickle.dumps(req)
        
        sz = len(req_str)
        sz_str = struct.pack('i', sz)
        
        pkt = 'REQ' + sz_str + req_str
        sock.send(pkt)

        self._sock = sock
        pass

    def handle(self):
        class stdin_dispatcher(object):
            def __init__(self, stdin, sock, socket_map):
                self._stdin = stdin
                self._sock = sock
                self._socket_map = socket_map
                pass
            
            def readable(self):
                return True

            def writable(self):
                return False

            def handle_error(self):
                import traceback
                traceback.print_exc()
                pass

            def handle_read_event(self):
                data = self._stdin.readline(1024)
                sz = len(data)
                
                if sz == 0:
                    del self._socket_map[self._stdin]
                    self._stdin.close()
                    pkt = 'IED'
                else:
                    sz_str = struct.pack('i', sz)
                    pkt = 'IPK' + sz_str + data
                    pass
                
                sock = self._sock
                sock.send(pkt)
                pass
            pass

        class server_displatcher(object):
            def __init__(self, sock, stdout, socket_map):
                self._sock = sock
                self._stdout = stdout
                self._socket_map = socket_map
                
                socket_map[sock] = self
                pass

            def readable(self):
                return True

            def writable(self):
                return False

            def handle_error(self):
                import traceback
                traceback.print_exc()
                pass

            def _handle_oed(self):
                sock = self._sock
                stdout = self._stdout
                
                stdout.close()
                sock.close()
                for sock in self._socket_map.keys():
                    del self._socket_map[sock]
                    pass
                pass

            def _handle_opk(self):
                sock = self._sock
                stdout = self._stdout
                
                sz_str = sock.recv(4)
                sz = struct.unpack('i', sz_str)[0]
                
                data = sock.recv(sz)

                stdout.write(data)
                pass

            def handle_read_event(self):
                sock = self._sock
                
                cmd = sock.recv(3)
                if cmd == 'OED':
                    self._handle_oed()
                elif cmd == 'OPK':
                    self._handle_opk()
                else:
                    raise RuntimeError, 'invalid packet type'
                pass
            pass

        sock_map = {}
        i_disp = stdin_dispatcher(self._stdin, self._sock, sock_map)
        serv_disp = server_displatcher(self._sock, self._stdout, sock_map)
        
        sock_map[self._stdin] = i_disp
        sock_map[self._sock] = serv_disp

        asyncore.loop(map=sock_map)
        pass
    pass

if __name__ == '__main__':
    import sys

    def test_call(args, env, session):
        print 'test_call'
        print args
        print env
        cnt[0] = cnt[0] + 1
        yield
        while True:
            data = session.recv()
            if data == None:
                break
            session.send('from client %x: %s' % (id(session), data))
            yield
            pass

        cnt[0] = cnt[0] - 1
        if cnt[0] == 0:
            print 'close server'
            s.close()
            pass
        
        print 'end of test_call'
        pass
    
    ns = {'data': 'testdata', 'test_call': test_call}
    s = server(ns)
    s.listen()
    addr = s.get_addr()
    sock = s.get_sock()

    pid = os.fork()
    if pid == 0:                # child (client)
        os.fork()               # two clients
        
        os.environ['PYSHELL_SERVER'] = addr
        c = client('test_call', ['1', '2'], os.environ, sys.stdin, sys.stdout)
        c.connect()
        c.handle()
        pass
    else:                       # parent (server)
        cnt = [0]
        s.handle()
        pass
    pass
