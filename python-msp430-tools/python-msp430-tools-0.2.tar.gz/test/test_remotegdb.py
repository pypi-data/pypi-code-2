#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2002-2010 Chris Liechti <cliechti@gmx.net>
# All Rights Reserved.
# Simplified BSD License (see LICENSE.txt for full text)


import sys
if sys.platform == 'win32':
    from twisted.internet import win32eventreactor
    win32eventreactor.install()
    #~ del sys.modules['twisted.internet.reactor']

import gdb
from twisted.python import usage, log
from twisted.internet import app
from twisted.internet import reactor
from twisted.internet.protocol import ClientFactory
from twisted.trial import unittest
from twisted.internet.error import ProcessTerminated

ok = 1

class GDBTestClient(gdb.GDBClient):
    def __init__(self):
        gdb.GDBClient.__init__(self)
        self.messages = []

    def connectionMade(self):
        print "connection ok"
        reactor.crash()

    def reset(self):
        self.messages = []
        
    def output(self, message):
        #~ print "O: %r" % message
        self.messages.append(message)

class GDBTestFactory(ClientFactory):
    def buildProtocol(self, addr):
        self.gdb = GDBTestClient()
        self.gdb.factory = self
        return self.gdb
    
    def clientConnectionLost(self, connector, reason):
        print "connection failed:", reason.getErrorMessage()
        reactor.stop()
        global ok
        ok = 0

    def clientConnectionFailed(self, connector, reason):
        print "connection failed:", reason.getErrorMessage()
        reactor.stop()
        global ok
        ok = 0

class TestRealTarget(unittest.TestCase):
    def setUp(self):
        """per test initialization"""
        self.gdb = factory.gdb
    
    def tearDown(self):
        """per test de-initialization"""
    
    def testReadMemory1(self):
        deferred = self.gdb.gdbReadMemory(0x0ff0, 2)
        result = unittest.deferredResult(deferred)
        self.failUnlessEqual(result, '\xf1\x49')
    def testReadMemory2(self):
        deferred = self.gdb.gdbReadMemory(0x0ff0, 1)
        result = unittest.deferredResult(deferred)
        self.failUnlessEqual(result, '\xf1')
    def testReadMemory3(self):
        deferred = self.gdb.gdbReadMemory(0x0ff1, 1)
        result = unittest.deferredResult(deferred)
        self.failUnless(result == '\x49')

    def testWriteMemory(self):
        deferred = self.gdb.gdbWriteMemory(0x200, '\x7b\x00')
        result = unittest.deferredResult(deferred)
        self.failUnlessEqual(result, None)
        deferred = self.gdb.gdbReadMemory(0x200, 2)
        result = unittest.deferredResult(deferred)
        self.failUnless(result == '\x7b\x00')

    def testWriteMemoryBinary(self):
        deferred = self.gdb.gdbWriteMemoryBinary(0x200, '\x7d$\x7b')
        result = unittest.deferredResult(deferred)
        self.failUnless(result == None)
        deferred = self.gdb.gdbReadMemory(0x200, 3)
        result = unittest.deferredResult(deferred)
        self.failUnless(result == '\x7d$\x7b')

    def testReadRegisters(self):
        deferred = self.gdb.gdbReadRegisters()
        result = unittest.deferredResult(deferred)
        self.failUnless(len(result) == 16) #can't guess register contents

    def testWriteRegisters(self):
        #read regs, cause cant guess R0..R3
        deferred = self.gdb.gdbReadRegisters()
        result = unittest.deferredResult(deferred)
        self.failUnless(len(result) == 16) #can't guess register contents
        first = result
        second = first[0:4] + range(12)
        #write regs
        deferred = self.gdb.gdbWriteRegisters(second)
        result = unittest.deferredResult(deferred)
        self.failUnlessEqual(result, None)
        #read back and check
        deferred = self.gdb.gdbReadRegisters()
        result = unittest.deferredResult(deferred)
        self.failUnless(len(result) == 16) #can't guess register contents
        self.failUnlessEqual(result[3:], second[3:])

    def testWriteRegister(self):
        deferred = self.gdb.gdbWriteRegister(4, 123)
        result = unittest.deferredResult(deferred)
        self.failUnlessEqual(result, None)
        #read back
        deferred = self.gdb.gdbReadRegister(4)
        result = unittest.deferredResult(deferred)
        self.failUnlessEqual(result, 123)

    def testLastSignal(self):
        deferred = self.gdb.gdbLastSignal()
        result = unittest.deferredResult(deferred)
        self.failUnlessEqual(result[0], gdb.STOP_THREAD)

    def testUnknownCommand(self):
        deferred = self.gdb.gdbCommand('Hg0')
        failure = unittest.deferredError(deferred)
        failure.trap(gdb.GDBUnknownCommandError)

    def testMonitor(self):
        deferred = self.gdb.gdbMonitor('puc')
        result = unittest.deferredResult(deferred)
        self.failUnlessEqual(result, None)
        self.failUnless(self.gdb.messages == ['Resetting by PUC...', ' Reset OK\n'])

    def testMonitorHelp(self):
        deferred = self.gdb.gdbMonitor('help')
        result = unittest.deferredResult(deferred)
        self.failUnlessEqual(result, None)

if __name__ == '__main__':
    class Options(usage.Options):
        """command line options"""
        optParameters = [
            ['exe',         'e', None,              'if testing through stdio the name of the executable'],
            ['remote',      'r', 'localhost',       'remote hostname'],
            ['outfile',     'o', None,              'Logfile [default: sys.stdout]'],
        ]
        
    o = Options()
    try:
        o.parseOptions()
    except usage.UsageError, errortext:
        print "%s: %s" % (sys.argv[0], errortext)
        print "%s: Try --help for usage details." % (sys.argv[0])
        raise SystemExit, 1

    logFile = sys.stdout
    if o.opts['outfile']:
        logFile = o.opts['outfile']
    log.startLogging(logFile, setStdout=0)
    
    if o.opts['exe'] is None:
        #~ print "connecting to remote GDB"
        host = o.opts['remote']
        port = 3333
        if ':' in host:
            host, port = host.split(':')
            port = int(port)
        
        factory = GDBTestFactory()
        reactor.connectTCP(host, port, factory)
        reactor.run()       #run until conection is made
        if not ok: raise SystemExit, 1
        #~ reactor.runUntilCurrent()
    else:
        import proc_popen       #Process class hack
        gdb.GDBTIMEOUT = 0.1
        
        from twisted.internet import protocol
        class WCProcessProtocol(GDBTestClient, protocol.ProcessProtocol):
            def connectionMade(self):
                print "connectionMade"
                #~ self.transport.closeStdin()

            def outReceived(self, data):
                #~ print "!!! outReceived(%r)" % data
                self.dataReceived(data)
            
            def errReceived(self, data):
                pass
                #~ print "!!! errReceived(%r)" % data
                sys.stderr.write(data)
            
            def processEnded(self, status):
                print "processEnded", status
                reactor.stop()
                global ok
                ok = 0
        wcProcess = WCProcessProtocol()
        class F: pass
        factory = F()
        factory.gdb = wcProcess
        print "exe = %r" % o.opts['exe']
        reactor.spawnProcess(wcProcess, o.opts['exe'], [o.opts['exe']])
        #~ reactor.run()       #run until conection is made
        if not ok: raise SystemExit, 1
        
    print "running tests..."
    from twisted.trial import util, reporter as reps
    reporter = reps.VerboseTextReporter(sys.stdout)
    suite = unittest.TestSuite()
    import __main__
    suite.addModule(__main__)
    suite.run(reporter)
    factory.gdb.transport.loseConnection()
    sys.exit(not reporter.allPassed())
