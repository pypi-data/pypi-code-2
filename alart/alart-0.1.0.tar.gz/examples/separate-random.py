#!/usr/bin/env python
#~Public domain
# Use own random functions

import alart
import datetime
import math

class PoorRandomness(object):
    def __init__(self):
        self.state = 0.0

    def random(self):
        self.state = math.fmod(
            self.state + datetime.datetime.now().microsecond / 1e6, 1)
        return self.state

    def randint(self, a, b):
        return int(math.floor(self.random() * (b - a + 1))) + a

random = PoorRandomness()
size = (320, 240)
formats = ('pygame',)
gen = alart.Alart(size, formats, random)
gen.generate()
