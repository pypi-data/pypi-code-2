""" A simple telnet server that exposes a simple Python REPL. """

import socket
import sys
import traceback
import app

from .process import Process
from . import util


TELNET_PORT = 23

class TelnetServer(Process):
    serviceName = "telnet"
    serviceIncludes = ["sessionManager"]

    def StartProcess(self):
        self.clients = []
        for port in [TELNET_PORT]:
            acceptor = socket.socket()
            try:
                acceptor.bind(("0.0.0.0", port))
                acceptor.listen(5)
            except socket.error, e:
                self.log.warning("Telnet server not accepting connection on port %s because: %s", port, e)
                return

            self.log.info("Telnet server accepting on port %s", port)
            self.New(self.Accept, acceptor)

    def StopProcess(self):
        pass

    def Accept(self, acceptor):
        while self.running:
            s, addr = acceptor.accept()
            addr, port = s.getpeername()
            self.log.info("Telnet: Accepted a connection from %s:%s", addr, port)
            t = self.New(self.Handler, s)
            t.name += " - client %s:%s" % (addr, port)
            t.session = self.sessionManager.CreateSession(userid = "auto", username = "telnetter")

    def Handler(self, s):
        greeting = "Telnetz0r greets you\r\nThis is a telnet session for '%s'\r\nHost platform: %s\r\n"
        greeting = greeting % (util.GetAppTitle(app.app.appName), sys.platform)
        s.send(greeting)
        cmd= ""
        g = {}
        l = {}
        self.clients.append(s)
        addr, port = s.getpeername()

        while self.running:
            try:
                ##self.log.info(">>Telnetzor calling recv, fileno=%s", s.fileno())
                data = s.recv(1000000)
                if not data:
                    raise socket.error()
            except Exception:
                self.log.info("Telnet: Remote connection closed from %s:%s", addr, port)
                util.GetSession().Close()
                #s.shutdown(socket.SHUT_RDWR) # In case of other exceptions than close
                break
            cmd += data
            if data.endswith("\r\n"):
                self.New(self.Execute, cmd[:-2], g, s, l)
                cmd = ""

        self.clients.remove(s)

    def Execute(self, cmd, g, s, l):
        tmp = sys.stdout, sys.stderr
        import cStringIO
        io = cStringIO.StringIO()
        sys.stdout = sys.stderr = io

        try:
            self.Exec(cmd, g, l)
        except Exception, e:
            traceback.print_exc(io)
        finally:
            sys.stdout, sys.stderr = tmp

        v = io.getvalue()
        try:
            if v:
                s.send(v.replace("\n", "\r\n"))
            s.send(">>> ")
        except socket.error, e:
            pass

    def Exec(self, cmd, g, l):
        exec(cmd, g, l)
