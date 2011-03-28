import os
import sys
import imp
import sets
import signal
import itertools

from twisted.internet import reactor, protocol, defer, error
from twisted.python import log, reflect
from twisted.protocols import basic
from twisted.web import server, resource

gen = itertools.count()

class Connector(protocol.ProcessProtocol):
    """
    A L{ProcessProtocol} subclass.

    @ivar process: the child process
    @type process: L{SubProcessProtocol} subclass

    @ivar finished: a deferred triggered when the process dies.
    @type finished: L{defer.Deferred}

    @ivar name: Unique name for the connector, much like a pid.
    @type name: int
    """

    def __init__(self, proto, name=None):
        """
        @param proto: An instance or subclass of L{amp.AMP}
        @type proto: L{amp.AMP}

        @param name: optional name of the subprocess.
        @type name: int
        """
        self.finished = defer.Deferred()
        self.process = proto
        self.name = name
        if name is None:
            self.name = gen.next()

    def signalProcess(self, signalID):
        """
        Send the signal signalID to the child process

        @param signalID: The signal ID that you want to send to the
                        corresponding child
        @type signalID: C{str} or C{int}
        """
        return self.transport.signalProcess(signalID)

    def connectionMade(self):
        log.msg("Subprocess %s started." % (self.name,))
        self.process.makeConnection(self)

    def loseConnection(self):
        self.transport.loseConnection()

    def loseWritingSide(self):
        self.transport.closeStdin()

    # Transport
    disconnecting = False

    def write(self, data):
        self.transport.write(data)

    def getPeer(self):
        return ('subprocess',)

    def getHost(self):
        return ('no host',)

    def childDataReceived(self, childFD, data):
        if childFD == 1:
            self.process.dataReceived(data)
            return
        self.errReceived(data)

    def errReceived(self, data):
        for line in data.strip().splitlines():
            log.msg("FROM %s: %s" % (self.name, line))

    def processEnded(self, status):
        log.msg("Process: %s ended" % (self.name,))
        self.process.connectionLost(status)
        if status.check(error.ProcessDone):
            self.finished.callback('')
            return
        self.finished.errback(status)

class SubProcessProtocol(basic.Int32StringReceiver):
    MAX_LENGTH = 2**24 # 16MB

    def __init__(self):
        self._d = None

    def die(self):
        """
        Send the hardest terminal signal to the child process
        """
        self.transport.signalProcess(signal.SIGKILL)

    def send(self, string):
        self._d = defer.Deferred()
        self.sendString(string)
        self.transport.loseWritingSide()
        return self._d

    def stringReceived(self, string):
        self._d.callback(string)
        self.transport.loseConnection()

    def getName(self):
        return self.transport.name

BOOTSTRAP = """\
from quebert import phelpers
phelpers.main()
"""

class ProcessStarter(object):

    connectorFactory = Connector
    def __init__(self, bootstrap=BOOTSTRAP, args=(), env={},
                 path=None, uid=None, gid=None, usePTY=0,
                 packages=()):
        """
        @param bootstrap: Startup code for the child process
        @type  bootstrap: C{str}

        @param args: Arguments that should be supplied to every child
                     created.
        @type args: C{tuple} of C{str}

        @param env: Environment variables that should be present in the
                    child environment
        @type env: C{dict}

        @param path: Path in which to run the child
        @type path: C{str}

        @param uid: if defined, the uid used to run the new process.
        @type uid: C{int}

        @param gid: if defined, the gid used to run the new process.
        @type gid: C{int}

        @param usePTY: Should the child processes use PTY processes
        @type usePTY: 0 or 1

        @param packages: A tuple of packages that should be guaranteed
                         to be importable in the child processes
        @type packages: C{tuple} of C{str}
        """
        self.bootstrap = bootstrap
        self.args = args
        self.env = env
        self.path = path
        self.uid = uid
        self.gid = gid
        self.usePTY = usePTY
        self.packages = packages

    def __repr__(self):
        """
        Represent the ProcessStarter with a string.
        """
        return """ProcessStarter(bootstrap=%r,
                                 args=%r,
                                 env=%r,
                                 path=%r,
                                 uid=%r,
                                 gid=%r,
                                 usePTY=%r,
                                 packages=%r)""" % (self.bootstrap,
                                                        self.args,
                                                        self.env,
                                                        self.path,
                                                        self.uid,
                                                        self.gid,
                                                        self.usePTY,
                                                        self.packages)

    def _checkRoundTrip(self, obj):
        """
        Make sure that an object will properly round-trip through 'qual' and
        'namedAny'.

        Raise a L{RuntimeError} if they aren't.
        """
        tripped = reflect.namedAny(reflect.qual(obj))
        if tripped is not obj:
            raise RuntimeError("importing %r is not the same as %r" %
                               (reflect.qual(obj), obj))

    def startProcess(self, entrypoint, parent=None):
        """

        """
        self._checkRoundTrip(entrypoint)
        entryPath = reflect.qual(entrypoint)

        if parent is None:
            parent = SubProcessProtocol
        prot = self.connectorFactory(parent())

        return self.startPythonProcess(prot, entryPath)


    def startPythonProcess(self, prot, *args):
        """
        @param prot: a L{protocol.ProcessProtocol} subclass
        @type prot: L{protocol.ProcessProtocol}

        @param args: a tuple of arguments that will be added after the
                     ones in L{self.args} to start the child process.

        @return: a tuple of the child process and the deferred finished.
                 finished triggers when the subprocess dies for any reason.
        """
        spawnProcess(prot, self.bootstrap, args+self.args, env=self.env,
                     path=self.path, uid=self.uid, gid=self.gid,
                     usePTY=self.usePTY, packages=self.packages)

        # XXX: we could wait for startup here, but ... is there really any
        # reason to?  the pipe should be ready for writing.  The subprocess
        # might not start up properly, but then, a subprocess might shut down
        # at any point too. So we just return amp and have this piece to be
        # synchronous.
        return prot.process, prot.finished

def spawnProcess(processProtocol, bootstrap, args=(), env={},
                 path=None, uid=None, gid=None, usePTY=0,
                 packages=()):
    env = env.copy()

    pythonpath = []
    for pkg in packages:
        p = os.path.split(imp.find_module(pkg)[1])[0]
        if p.startswith(os.path.join(sys.prefix, 'lib')):
            continue
        pythonpath.append(p)
    pythonpath = list(sets.Set(pythonpath))
    pythonpath.extend(env.get('PYTHONPATH', '').split(os.pathsep))
    env['PYTHONPATH'] = os.pathsep.join(pythonpath)
    args = (sys.executable, '-c', bootstrap) + args
    # childFDs variable is needed because sometimes child processes
    # misbehave and use stdout to output stuff that should really go
    # to stderr. Of course child process might even use the wrong FDs
    # that I'm using here, 3 and 4, so we are going to fix all these
    # issues when I add support for the configuration object that can
    # fix this stuff in a more configurable way.
    return reactor.spawnProcess(processProtocol, sys.executable, args,
                                env, path, uid, gid, usePTY)

def executeTask(entry, taskString, *args):
    p = ProcessStarter(args=args)
    subprocess, f = p.startProcess(entry)
    sent = subprocess.send(taskString)
    d = defer.DeferredList([f, sent], fireOnOneErrback=True, fireOnOneCallback=True)
    d.addBoth(lambda r: r[0])
    return subprocess, d


class ExecutorPage(resource.Resource):
    def __init__(self, func, conf, killOnExit=False):
        resource.Resource.__init__(self)
        self.func = func
        self.conf = conf
        self.killOnExit = killOnExit
        self._children = {}
        self.running = True

    def getChild(self, *args):
        return self

    def close(self):
        return defer.DeferredList(self._children.values())

    def render(self, request):
        def _cb(data):
            request.write(data)
            request.finish()
        def _eb(reason):
            request.setResponseCode(500)
            request.finish()
        def _kill(reason, child):
            log.msg("Unexpected disconnect from client, killing child")
            child.die()
        def _cleanup(_, child):
            self._children.pop(child.getName(), None)

        if not self.running:
            request.setResponseCode(500)
            return "Closing down"

        host = request.getHeader('host')
        child, d = executeTask(self.func,
                               request.content.read(),
                               request.uri,
                               host,
                               self.conf)
        self._children[child.getName()] = d
        if self.killOnExit:
            request.notifyFinish().addErrback(_kill, child)

        d.addCallbacks(_cb, _eb).addBoth(_cleanup, child)
        return server.NOT_DONE_YET
