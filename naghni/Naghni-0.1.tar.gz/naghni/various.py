#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Naghni: a breath-taking side-scroller focusing on round lifeforms
# Copyright (C) 2010  Niels Serup, based on various.py from
# Dililatum <http://metanohi.org/projects/dililatum/>

# This file is part of Naghni.
#
# Naghni is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Naghni is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Naghni.  If not, see <http://www.gnu.org/licenses/>.

##[ Name        ]## various
##[ Maintainer  ]## Niels Serup <ns@metanohi.org>
##[ Description ]## Various minor (but still important) parts
##[ Start date  ]## 2010 July 14

import sys
import Image
import math

def error(msg, cont=True, pre=None):
    errstr = str(msg) + '\n'
    if pre is not None:
        errstr = pre + ': ' + errstr
    sys.stderr.write(errstr)
    if cont is not True:
        try:
            sys.exit(cont)
        except Exception:
            sys.exit(1)

def usable_error(msg, cont=True):
    error(msg, cont, 'naghni: ')

nothing = lambda *a: None

class Container:
    pass

class KeyGroup:
    def __init__(self, *mods, **keys):
        self.keys = keys
        if mods:
            self.mods = mods[0]
            for x in range(1, len(mods)):
                self.mods &= mods[i]
        else:
            self.mods = 0
        self.revkeys = {}
        for key, val in keys.items():
            self.revkeys[val] = key
        self.keys_list = keys.values()
        self.list = []
        self.current = ''
        self.toggled = []

    def check(self, key, mods):
        if self.mods and not mods & self.mods:
            return
        if key in self.keys_list:
            self.list.append(key)
        try:
            name = self.revkeys[key]
            self.current = name
            if name not in self.toggled:
                self.toggled.append(name)
            else:
                self.toggled.remove(name)
        except KeyError:
            self.current = ''

    def uncheck(self, key, mods):
        try:
            self.list.remove(key)
        except ValueError:
            pass
        self.current = ''

    def update(self):
        self.current = ''

    def get_top(self):
        try:
            return self.revkeys[self.list[-1]]
        except (IndexError, KeyError):
            return

class SubList(list):
    def __init__(self, parent, *args):
        self.parent = parent
        list.__init__(self, *args)

    def append(self, val):
        self.parent.append(val)
        list.append(self, val)

    def remove(self, val):
        self.parent.remove(val)
        list.remove(self, val)

inf = float('inf')
try:
    math.isinf(0)
    isinf = math.isinf
except AttributeError:
    isinf = lambda n: abs(n) == inf

def surface_to_string(surface, format_in, format_out=None):
    if format_out is None:
        format_out = format_in

    img = Image.frombuffer(
        format_out, (surface.get_width(), surface.get_height()),
        surface.get_data(), 'raw', format_in, 0, 1)

    return img.tostring('raw', format_out, 0, 1)
