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

__version__ = "0.6.3"

from _skein import skein256, skein512, skein1024, threefish


###
### Skein-PRNG ###
###

import random

class Random(random.Random):
    # These two constants may be modified to use a different algorithm:
    HASHER = skein512
    STATE_BYTES = 512 // 8

    # Each Skein call produces new state bytes and enough bits for 80 floats:
    _BPF = random.BPF
    _RECIP_BPF = random.RECIP_BPF
    _DIGEST_BITS = 8*STATE_BYTES + 10*8*_BPF
    _MASK = 2**_BPF - 1
    _random = random

    def __init__(self, seed=None):
        """Initialize SkeinRandom instance.

        Optional argument as in method seed().
        """
        self._state = bytes(self.STATE_BYTES)
        super().__init__(seed)

    def seed(self, seed=None):
        """Initialize internal state from hashable object.

        If seed is a bytes object, set state according to Skein specification.
        Otherwise derive a bytes object from the seed using random.Random.
        """
        if not isinstance(seed, bytes):
            r = self._random.Random(seed)
            seed = bytes(r.randrange(256) for _ in range(self.STATE_BYTES))
        self._state = self.HASHER(self._state+seed).digest()
        self._buffer = []

    def random(self):
        """Get the next random number in the range [0.0, 1.0)."""
        if not self._buffer:
            # Produce enough random bits...
            h = self.HASHER(self._state, digest_bits=self._DIGEST_BITS)
            data = h.digest()
            # ...to update the state...
            self._state = data[:self.STATE_BYTES]
            # ...and fill the buffer:
            n = 0
            bits = 0
            BPF = self._BPF
            for b in data[self.STATE_BYTES:]:
                n <<= 8
                n |= b
                bits += 8
                if bits >= BPF:
                    self._buffer.append(n & self._MASK)
                    n >>= BPF
                    bits -= BPF
            # assert bits == 0 and n == 0
        return self._buffer.pop() * self._RECIP_BPF

    def getstate(self):
        """Return internal state; can be passed to setstate() later."""
        return self._state, self._buffer[:], self.gauss_next

    def setstate(self, state):
        """Restore internal state from object returned by getstate()."""
        self._state, buffer, self.gauss_next = state
        self._buffer = buffer[:]

del random
