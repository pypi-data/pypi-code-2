# skein.py
# Copyright 2009, 2010 Hagen Fürstenau <hagen@zhuliguan.net>
#
# This file is part of PySkein.
#
# PySkein is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

__version__ = "0.7"

from _skein import skein256, skein512, skein1024, threefish


###
### Skein-PRNG ###
###

import random

class Random(random.Random):
    _BPF = random.BPF
    _RECIP_BPF = random.RECIP_BPF
    _MASK = (1<<_BPF) - 1
    _TWEAK = bytes(15) + b"\x3f"
    _random = random

    def __init__(self, seed=None, hasher=skein512):
        """Initialize SkeinRandom instance.

        - 'seed' as in method seed().
        - 'hasher' may be skein256, skein512, or skein1024.
        """
        self._hasher = hasher
        self._state_bytes = hasher().block_size
        self._state = bytes(self._state_bytes)
        self._counter0 = bytes(self._state_bytes)
        self._counter1 = b"\1" + bytes(self._state_bytes-1)
        super().__init__(seed)


    def seed(self, seed=None):
        """Initialize internal state from hashable object.

        If seed is a bytes object, set state according to Skein specification.
        Otherwise derive a bytes object from the seed using random.Random.
        """
        if not isinstance(seed, bytes):
            r = self._random.Random(seed)
            seed = bytes(r.randrange(256) for _ in range(self._state_bytes))
        self._state = self._hasher(self._state+seed).digest()
        self._buffer = b""
        self._number = 0
        self._bits = 0


    def read(self, n):
        """Return n random bytes.

        The stream of random bytes is reproducible for a given seed:

        >>> r = Random(seed)
        >>> assert r.read(m)+r.read(n) == Random(seed).read(m+n)
        """
        if n < 0:
            raise ValueError("number of random bytes needs to be >= 0")
        if len(self._buffer) < n:
            chunks = [self._buffer]
            blocks = ((n-len(self._buffer)-1) // self._state_bytes) + 1
            for i in range(1, blocks+1):
                output = threefish(self._state, self._TWEAK).encrypt_block
                self._state = output(self._counter0)
                chunks.append(output(self._counter1))
            self._buffer = b"".join(chunks)
            assert len(self._buffer) >= n
        res, self._buffer = self._buffer[:n], self._buffer[n:]
        return res


    def random(self):
        """Get the next random number in the range [0.0, 1.0)."""
        bits = self._bits
        for b in self.read((self._BPF-self._bits-1)//8+1):
            self._number |= b << bits
            bits += 8
        r = self._number & self._MASK
        self._number >>= self._BPF
        self._bits = bits - self._BPF
        return r * self._RECIP_BPF


    def getstate(self):
        """Return internal state; can be passed to setstate() later."""
        return (self._state,
                self._buffer, self._number, self._bits,
                self.gauss_next)


    def setstate(self, state):
        """Restore internal state from object returned by getstate()."""
        (self._state,
            self._buffer, self._number, self._bits,
            self.gauss_next) = state

del random


###
### Stream Cipher ###
###

class StreamCipher:
    DIGEST_BITS = 2**64-1

    def __init__(self, key, nonce=b"", hasher=skein512):
        self._h = hasher(key=key, nonce=nonce, digest_bits=self.DIGEST_BITS)
        self._pos = 0

    def encrypt(self, plain):
        newpos = self._pos + len(plain)
        stream = self._h.digest(self._pos, newpos)
        self._pos = newpos
        try:
            return bytes(x^y for x, y in zip(plain, stream))
        except TypeError as e:
            raise TypeError("argument must be a bytes object") from e

    decrypt = encrypt
