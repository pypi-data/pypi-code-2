import struct

from gameduino.registers import *

# BaseGameduino is the common base for the Gameduino objects in remote and sim

class BaseGameduino(object):

    def dump(self, a, l):
        """ Dump ``l`` bytes memory starting at address ``a`` """
        for i in range(0, l, 16):
            d16 = self.rdstr(a + i, 16)
            print "%04x  %s" % (a + i, " ".join(["%02x" % ord(c) for c in d16]))

    def wr(self, a, v):
        """ Write a single byte ``v`` to address ``a``. """
        self.wrstr(a, chr(v))

    def fill(self, a, v, c):
        """ Fill ``c`` bytes of memory at address ``a`` with value ``v`` """
        self.wrstr(a, chr(v) * c)

    def putstr(self, x, y, v):
        """ Write string ``v`` at screen position (x,y) """
        a = y * 64 + x
        self.wrstr(a, v)

    def wr16(self, a, v):
        """ Write 16-bit value ``v`` at to address ``a`` """
        self.wrstr(a, struct.pack("<H", v))

    def wr32(self, a, v):
        """ Write 32-bit value ``v`` at to address ``a`` """
        self.wrstr(a, struct.pack("<L", v))

    def voice(self, v, wave, freq, lamp, ramp = None):
        """
        Set the state of a voice.

        :param v: voice number 0-63
        :type v: int
        :param wave: wave type, 0 for sine 1 for noise
        :type wave: int
        :param freq: frequency control, in quarter-hertz
        :type freq: int
        :param lamp: left amplitude 0-255
        :type lamp: int
        :param ramp: right amplitude 0-255, defaults to same ``lamp``
        :type ramp: int
        """
        if ramp is None:
            ramp = lamp
        self.wr32(VOICES + (4 * v), freq | (wave << 15) | (lamp << 16) | (ramp << 24))

    def silence(self):
        """ Switch all voices off """
        for i in range(64):
            self.voice(i, 0, 4 * 440, 0, 0)
    
    def copy(self, a, v):
        self.wrstr(a, v)

    def microcode(self, src):
        """
        Halt coprocessor, load microprogram, restart coprocessor

        :param src: microprogram
        :type src: string

        self.wr(J1_RESET, 1)
        self.copy(J1_CODE, src)
        self.wr(J1_RESET, 0)

    def sprite(self, spr, x, y, image, palette, rot, jk = 0):
        """
        Set the state of a hardware sprite

        :param spr: sprite number 0-511
        :param x: x coordinate
        :param y: y coordinate
        :param image: sprite source image 0-63
        :param palette: sprite palette select, 0-15, see below
        :param rot: sprite rotate control 0-7, see :ref:`rotate`
        :param jk: collision class control, 0-1

        Palette select controls the number of colors used for the sprite, the source palette, and which data bits 
        to use as source.

        """

        self.wr32(RAM_SPR + (4 * spr),
                  x | (rot << 9) | (palette << 12) | (y << 16) | (image << 25) | (jk << 31))

    def memory(self):
        """ Returns current image of memory as a 32768 byte string """
        return self.mem.tostring()
