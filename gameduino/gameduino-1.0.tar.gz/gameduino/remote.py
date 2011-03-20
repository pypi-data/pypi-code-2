import struct
import serial
import time
import array

from gameduino.registers import *
from gameduino.base import BaseGameduino

class Gameduino(BaseGameduino):

    def __init__(self, usbport, speed):
        self.ser = serial.Serial(usbport, speed)
        # time.sleep(2)
        self.mem = array.array('B', [0] * 32768)
        self.wr(J1_RESET, 1)
        self.fill(RAM_PIC, 0, 10 * 1024)
        self.wr16(SCROLL_X, 0)
        self.wr16(SCROLL_Y, 0)

    def wrstr(self, a, s):
        if not isinstance(s, str):
            s = s.tostring()
        self.mem[a:a+len(s)] = array.array('B', s)
        for i in range(0, len(s), 255):
            sub = s[i:i+255]
            ff = struct.pack(">BH", len(sub), 0x8000 | (a + i)) + sub
            self.ser.write(ff)

    def rd(self, a):
        ff = struct.pack(">BH", 1, a)
        self.ser.write(ff)
        return ord(self.ser.read(1))

    def rdstr(self, a, n):
        ff = struct.pack(">BH", n, a)
        self.ser.write(ff)
        return self.ser.read(n)


import array
def readarray(filename):
    return array.array('B', open(filename).read())

