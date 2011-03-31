#
# $Id: Test102multiprocessmix.py 97 2011-03-28 06:49:25Z patrick $
#
# Copyright 2011 Patrick Atamaniuk
#
# This source code is freely redistributable and may be used for
# any purpose.  This copyright notice must be maintained.
# Patrick Atamaniuk and Contributors are not responsible for
# the consequences of using this software.
#
from multiprocessing import Process, Pipe
import unittest
import pysox
from pysox.sox import PY3
from pysox.combiner import SocketOutput, MixSockets

class SoxBufferProcessMixTestCase(unittest.TestCase):

    class IEffs(pysox.CCustomEffect):
        """generate audio"""
        junks=3
        sample=4
        def drain(self, buffer_object):
            """create a few samples"""
            if 0 == self.junks:
                return 0
            self.junks -= 1
            l = 3
            for i in range(l):
                print('generating sample ',self.sample)
                buffer_object[i*2] = self.sample
                buffer_object[i*2+1] = -self.sample
                self.sample -= 1
            return l*2
    
    class IEffr(pysox.CCustomEffect):
        """read audio from socket in binary bytes format and mix them"""
        inputs = None
        currentInput = 0
        numInputs = 0
        def set_recv_channels(self, conns):
            self.inputs = conns
            self.numInputs = len(conns)
            
        def drain(self, buf):
            """receive input from socket"""
            print("IEffr drain")
            self.currentInput = 0
            while self.currentInput < self.numInputs:
                conn = self.inputs[self.currentInput]

# Second variant, involving a bytes intermediate object
                try:
                    data = conn.recv_bytes()
                except EOFError:
                    print('IEffr EOF')
                    self.currentInput += 1
                    continue
                print("IEffr td",type(data), len(data), data)
                print("IEffr td",len(buf))
                if not data or not len(data):
                    print("IEffr data is None, channel %s is finished"%self.currentInput)
                    buf.writebytes(b'')
                else:
                    # MIX the stuff
                    buf.writebytes(data)
                    print('IEffr check',buf.tolist())
                self.currentInput += 1

            return len(buf)
            print("IEffr drain end")
            return 0
    
    
    class OEffr(pysox.CCustomEffect):
        result = []
        """write audio to stdout"""
        def flow(self, ibuf, obuf, isamp):
            """read from ibuf and end the chain by providing 0 output"""
            print("OEffr flow", isamp, len(ibuf))
            print('OEffr check',ibuf.tolist())
            self.result += ibuf.tolist()
            return 0 #0 samples put in obuf, we are end of chain

    def mainchain(self, conns):
        """read audio from socket and write to stdout"""
        output = self.OEffr("output", [])
        input = MixSockets("input", conns)
        #input.set_recv_channels(conns)
        input.get_out_signal().set_param(rate=44100, channels=2, precision=32)
        chain = pysox.CEffectsChain()
        chain.add_effect(input)
        chain.add_effect(output)
        chain.flow_effects()
        print(output.result)
        odata = [4, -4, 3, -3, 2, -2, 1, -1, 0, 0, -1, 1, -2, 2, -3, 3, -4, 4]
        odata = [4, -4, 2, -2, 2, -2, 0, -0, 0, 0, -0, 0, -2, 2, -2, 2, -4, 4]
        #odata = map(lambda x:2*x, odata)
        self.assert_(output.result == odata, 'Chain received correct data')
        print("mainchain done.")
    
    def subchain(self, conn, n):
        """generate audio and send to socket"""
        input = self.IEffs("input", [])
        input.get_in_signal().set_param(rate=44100, channels=2, precision=32)
        input.get_out_signal().set_param(rate=44100, channels=2, precision=32)
        output = SocketOutput("output", [conn])
        chain = pysox.CEffectsChain()
        chain.add_effect(input)
        chain.add_effect(output)
        chain.flow_effects()
        print("subchain %s done."%n)

    def test_001_mppipe(self):
        """Test buffer transport between processes and mix 2 signals"""
        parent_conn, child1_conn = Pipe()
        parent2_conn, child2_conn = Pipe()
        p = Process(target=self.subchain, args=(child1_conn, 1))
        p.start()
        p2 = Process(target=self.subchain, args=(child2_conn, 2))
        p2.start()
        self.mainchain([parent_conn, parent2_conn])
        p.join()
        p2.join()
