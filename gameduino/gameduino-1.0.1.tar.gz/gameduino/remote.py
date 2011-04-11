"""
gameduino.remote - remote interface
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The remote interface lets Python scripts read and write
Gameduino memory, via the USB connection and a
simple client running on the Arduino.

The remote interface can be more convenient than compiling and uploading a
Sketch when developing media and coprocessor microprograms.

The Gameduino in this module is similar to the one in :mod:`gameduino.sim`.

"""

import struct
import serial
import time
import array

from gameduino.registers import *
from gameduino.base import BaseGameduino

class Gameduino(BaseGameduino):

    def __init__(self, usbport, speed):
        self.ser = serial.Serial(usbport, speed)
        time.sleep(2)
        assert self.rd(IDENT) == 0x6d, "Missing IDENT"
        self.mem = array.array('B', [0] * 32768)
        self.coldstart()

    def wrstr(self, a, s):
        if not isinstance(s, str):
            s = s.tostring()
        self.mem[a:a+len(s)] = array.array('B', s)
        for i in range(0, len(s), 255):
            sub = s[i:i+255]
            ff = struct.pack(">BH", len(sub), 0x8000 | (a + i)) + sub
            self.ser.write(ff)

    def rd(self, a):
        """ Read byte at address ``a`` """
        ff = struct.pack(">BH", 1, a)
        self.ser.write(ff)
        return ord(self.ser.read(1))

    def rdstr(self, a, n):
        """
        Read ``n`` bytes starting at address ``a``

        :rtype: string of length ``n``.
        """
        ff = struct.pack(">BH", n, a)
        self.ser.write(ff)
        return self.ser.read(n)

    def waitvblank(self):
        while self.rd(VBLANK) == 1:
            pass
        while self.rd(VBLANK) == 0:
            pass

    def linecrc(self, y):
        self.ser.write(struct.pack(">BBH", 0, ord('L'), 2 + y * 2))
        return struct.unpack(">L", self.ser.read(4))[0]

    def coll(self):
        """
        Return the 256 bytes of COLLISION RAM.

        :rtype: list of byte values.
        """
        self.ser.write(struct.pack(">BB", 0, ord('c')))
        return array.array('B', self.ser.read(256)).tolist()

    def collcrc(self):
        self.ser.write(struct.pack(">BB", 0, ord('C')))
        return struct.unpack(">L", self.ser.read(4))[0]

    def memcrc(self, a, s):
        self.ser.write(struct.pack(">BBHH", 0, ord('M'), a, s))
        return struct.unpack(">L", self.ser.read(4))[0]


import array
def readarray(filename):
    return array.array('B', open(filename).read())
