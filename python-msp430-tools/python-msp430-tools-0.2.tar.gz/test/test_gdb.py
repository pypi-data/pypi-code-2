#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2002-2010 Chris Liechti <cliechti@gmx.net>
# All Rights Reserved.
# Simplified BSD License (see LICENSE.txt for full text)

from twisted.trial import unittest
from twisted.internet import reactor, defer
import gdb
from binascii import hexlify, unhexlify
from cStringIO import StringIO

gdb.GDBTIMEOUT = 0.1

class TestGDB(gdb.GDBClient):
    def __init__(self):
        gdb.GDBClient.__init__(self)
        self.reset()
        
    def reset(self):
        self.messages = []
        self.transport = StringIO()
        
    def output(self, message):
        self.messages.append(message)

class TestProtocol(unittest.TestCase):
    def setUp(self):
        """per test initialization"""
        self.gdb = TestGDB()
    
    def tearDown(self):
        """per test de-initialization"""
    
    def testOutput(self):
        self.gdb.dataReceived('$o68656c6c6f#16')
        self.failUnlessEqual(self.gdb.transport.getvalue(), '+')
        self.failUnlessEqual(self.gdb.messages, ['hello'])

    def testBrokenPacket(self):
        self.gdb.dataReceived('$garbage$o68656c6c6f#16')
        self.failUnlessEqual(self.gdb.transport.getvalue(), '+')
        self.failUnlessEqual(self.gdb.messages, ['hello'])
        #broken crc
        self.gdb.reset()
        self.gdb.dataReceived('$garbage#1$o68656c6c6f#16')
        self.failUnlessEqual(self.gdb.transport.getvalue(), '+')
        self.failUnlessEqual(self.gdb.messages, ['hello'])
        #broken crc without frame start
        self.gdb.reset()
        self.gdb.dataReceived('#1$o68656c6c6f#16')
        self.failUnlessEqual(self.gdb.transport.getvalue(), '+')
        self.failUnlessEqual(self.gdb.messages, ['hello'])
    
    def testWrongCRC(self):
        self.gdb.dataReceived('$o68656c6c6f#00')
        self.failUnlessEqual(self.gdb.transport.getvalue(), '-')
        self.gdb.reset()
        self.gdb.dataReceived('$o68656c6c6f#z*')
        self.failUnlessEqual(self.gdb.transport.getvalue(), '')

    def testRemoteError(self):
        deferred = self.gdb.gdbReadMemory(0x1234, 1234)       #dummy request
        self.gdb.dataReceived('+$E00#a5')
        failure = unittest.deferredError(deferred)
        failure.trap(gdb.GDBRemoteError)
        self.failUnlessEqual(failure.value.getErrorCode(), 0)

    def testNoAckAndNack(self):
        deferred = self.gdb.gdbReadMemory(0x1234, 1234)       #dummy request
        old_errorcounter = self.gdb.errorcounter
        self.gdb.dataReceived('-')
        self.gdb.dataReceived('-')
        self.gdb.dataReceived('-')
        self.failUnlessEqual(old_errorcounter + 3, self.gdb.errorcounter)
        #now let it time-out
        failure = unittest.deferredError(deferred)
        failure.trap(gdb.GDBRemoteTimeout)

    def testUnknownCommand(self):
        deferred = self.gdb.gdbCommand('Hg0')
        self.failUnlessEqual(self.gdb.transport.getvalue(), '$Hg0#df')
        self.gdb.dataReceived('+$#00')
        failure = unittest.deferredError(deferred)
        failure.trap(gdb.GDBUnknownCommandError)

    def testMemRead(self):
        deferred = self.gdb.gdbReadMemory(0x0ff0, 4)
        self.failUnlessEqual(self.gdb.transport.getvalue(), '$mff0,4#c9')
        self.gdb.dataReceived('+$f1490043#cb')
        result = unittest.deferredResult(deferred)
        self.failUnlessEqual(result, '\xf1\x49\x00\x43')

    def testQuerry(self):
        deferred = self.gdb.gdbQuerry('Offsets')
        self.failUnlessEqual(self.gdb.transport.getvalue(), '$qOffsets#4b')
        self.gdb.dataReceived('+$Text=0;Data=0;Bss=0#04')
        result = unittest.deferredResult(deferred)
        self.failUnlessEqual(result, 'Text=0;Data=0;Bss=0')

    def testLastSignal(self):
        deferred = self.gdb.gdbLastSignal()
        self.failUnlessEqual(self.gdb.transport.getvalue(), '$?#3f')
        self.gdb.dataReceived('+$T0600:00f0;04:1fc2;#8a')
        result = unittest.deferredResult(deferred)
        self.failUnlessEqual(result, (gdb.STOP_THREAD, 6, ['00:00f0', '04:1fc2']))

    def testReadRegisters(self):
        deferred = self.gdb.gdbReadRegisters()
        self.failUnlessEqual(self.gdb.transport.getvalue(), '$g#67')
        self.gdb.dataReceived('+$00f00003000000001fc2121cb6b0108ac0a162408fcc01000000000002000000#98')
        result = unittest.deferredResult(deferred)
        self.failUnlessEqual(result,  [0xf000, 0x0300, 0x0000, 0x0000,
                                       0xc21f, 0x1c12, 0xb0b6, 0x8a10,
                                       0xa1c0, 0x4062, 0xcc8f, 0x0001,
                                       0x0000, 0x0000, 0x0002, 0x0000])

    def testWriteRegisters(self):
        deferred = self.gdb.gdbWriteRegisters([0xf000, 0x0300, 0x0000, 0x0000,
                                               0xc21f, 0x1c12, 0xb0b6, 0x8a10,
                                               0xa1c0, 0x4062, 0xcc8f, 0x0001,
                                               0x0000, 0x0000, 0x0002, 0x0000])
        self.failUnlessEqual(self.gdb.transport.getvalue(), '$G00f00003000000001fc2121cb6b0108ac0a162408fcc01000000000002000000#df' )
        self.gdb.dataReceived('+$OK#9a')
        result = unittest.deferredResult(deferred)
        self.failUnlessEqual(result, None)

    def testWriteRegister(self):
        deferred = self.gdb.gdbWriteRegister(4, 123)
        self.failUnlessEqual(self.gdb.transport.getvalue(), '$P4=7b00#ba')
        self.gdb.dataReceived('+$OK#9a')
        result = unittest.deferredResult(deferred)
        self.failUnlessEqual(result, None)

    def testReadRegister(self):
        deferred = self.gdb.gdbReadRegister(4)
        self.failUnlessEqual(self.gdb.transport.getvalue(), '$p4#a4')
        self.gdb.dataReceived('+$7b00#f9')
        result = unittest.deferredResult(deferred)
        self.failUnlessEqual(result, 123)

    def testWriteMemory(self):
        deferred = self.gdb.gdbWriteMemoryBinary(0x200, '\x7b\x00')
        self.failUnlessEqual(self.gdb.transport.getvalue(), '$X200,2:{\x00#fd')
        self.gdb.dataReceived('+$OK#9a')
        result = unittest.deferredResult(deferred)
        self.failUnlessEqual(result, None)

    def testMonitor(self):
        deferred = self.gdb.gdbMonitor('erase')
        self.failUnlessEqual(self.gdb.transport.getvalue(), '$qRcmd,6572617365#33')
        self.gdb.dataReceived('+')
        self.gdb.dataReceived('$O45726173696e672074617267657420666c617368202d20#49')
        self.gdb.dataReceived('$O616c6c2e2e2e#ad')
        self.gdb.dataReceived('$O20457261736564204f4b0a#4c')
        self.gdb.dataReceived('$OK#9a')
        self.failUnlessEqual(self.gdb.transport.getvalue(), '$qRcmd,6572617365#33++++')
        result = unittest.deferredResult(deferred)
        self.failUnlessEqual(result, None)
        self.failUnlessEqual(self.gdb.messages, ['Erasing target flash - ', 'all...', ' Erased OK\n'])

    def testContinue(self):
        deferred = self.gdb.gdbContinueWithSignal(6)
        self.failUnlessEqual(self.gdb.transport.getvalue(),'$C06#a9')
        self.gdb.dataReceived('+$T0200:48f0;04:bbc2;#bf')
        result = unittest.deferredResult(deferred)
        self.failUnlessEqual(result, (gdb.STOP_THREAD, 2, ['00:48f0', '04:bbc2']))

    def testInterrupt(self):
        self.gdb.gdbInterrupt()
        self.failUnlessEqual(self.gdb.transport.getvalue(), '\x03')

if __name__ == '__main__':
    
    #~ cmd = 'o'+hexlify('hello')
    #~ checksum = 0
    #~ for character in cmd:
        #~ checksum = (checksum + ord(character)) & 0xff
    #~ print '$%s#%02x' % (cmd, checksum)
    
    import sys
    from twisted.scripts import trial
    sys.argv.append('-o')
    sys.argv.extend(['-f', sys.argv[0]])
    trial.run()
