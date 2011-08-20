#!/usr/bin/env python
# -*- coding: utf-8 -*-

# alart: a pseudo-random art generator
# Copyright (C) 2010, 2011  Niels Serup

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

## Maintainer: Niels Serup <ns@metanohi.name>
# Use own random functions in a command-line environment.

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

alart.command_line_entry(None, PoorRandomness())
