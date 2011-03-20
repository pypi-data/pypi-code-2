import struct
import time
import array
import math
import itertools
import wave

from gameduino.registers import *
from gameduino.base import BaseGameduino

class Gameduino(object):

    def __init__(self):
        self.mem = array.array('B', [0] * 32768)

    def wrstr(self, a, s):
        if not isinstance(s, str):
            s = s.tostring()
        self.mem[a:a+len(s)] = array.array('B', s)

    def rd(self, a):
        return self.mem[a]

    def rdstr(self, a, n):
        return self.mem[a:a+n].tostring()

    def writewave(self, duration, dst):
        sintab = [int(127 * math.sin(2 * math.pi * i / 128.)) for i in range(128)]
        nsamples = int(8000 * duration)
        master = [i/8000. for i in range(nsamples)]
        lacc = [0] * nsamples
        racc = [0] * nsamples
        for v in range(64):
            if v == self.rd(RING_START):
                print v, max(lacc)
                ring = [s/256 for s in lacc]
                lacc = [0] * nsamples
                racc = [0] * nsamples

            (freq,la,ra) = struct.unpack("<HBB", self.rdstr(VOICES + 4 * v, 4))
            if la or ra:
                tone = [sintab[int(m * freq * 32) & 0x7f] for m in master]
                if self.rd(RING_START) <= v < self.rd(RING_END):
                    lacc = [o + la * (r * t) / 256 for (o,r,t) in zip(lacc, ring, tone)]
                    racc = [o + ra * (r * t) / 256 for (o,r,t) in zip(racc, ring, tone)]
                else:
                    lacc = [o + la * t for (o,t) in zip(lacc, tone)]
                    racc = [o + ra * t for (o,t) in zip(racc, tone)]
        merged = [None,None] * nsamples
        merged[0::2] = lacc
        merged[1::2] = racc
        raw = array.array('h', merged)
        w = wave.open(dst, "wb")
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(8000)
        w.writeframesraw(raw)
        w.close()

def readarray(filename):
    return array.array('B', open(filename).read())


