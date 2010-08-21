#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Naghni: a breath-taking side-scroller focusing on round lifeforms
# Copyright (C) 2010  Niels Serup

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

##[ Name        ]## shapes
##[ Maintainer  ]## Niels Serup <ns@metanohi.org>
##[ Description ]## Contains classes for lines, etc.
##[ Start date  ]## 2010 July 18

import math
from naghni.object.genericobject import LevelObject
import naghni.various as various

class MinimalLine:
    def __init__(self, pos1, pos2):
        self.pos1 = list(pos1)
        self.pos2 = list(pos2)
        self.length = self.get_length()

    def get_length(self):
        return math.hypot(self.pos2[0] - self.pos1[0],
                          self.pos2[1] - self.pos1[1])

class Shape(LevelObject):
    def __init__(self, level, *args, **kargs):
        self.bounce_off = True
        LevelObject.__init__(self, level, *args, **kargs)

class Line(Shape):
    def init(self, pos1, pos2, **kargs):
        self.pos1 = list(pos1)
        self.pos2 = list(pos2)
        for p in self.pos1, self.pos2:
            for i in range(2):
                try:
                    p[i] = float(p[i])
                except Exception, e:
                    self.world.error(
                        'value "%s" cannot be converted to a float' %
                        str(p[i]), False)

        infs = 0
        for x in self.pos1:
            if various.isinf(x):
                infs += 1
        for x in self.pos2:
            if various.isinf(x):
                infs += 1
        if infs > 2:
            self.world.error('no more than 2 infinite values can be \
used in a line', False)
        if various.isinf(self.pos1[0]) and various.isinf(self.pos2[1]) or \
                various.isinf(self.pos1[1]) and various.isinf(self.pos2[0]):
            self.world.error('infinite values must be used on the same \
axis', False)
        self.pos1w = self.pos1[:]
        self.pos2w = self.pos2[:]
        for i in range(2):
            if self.pos1w[i] > self.pos2w[i]:
                t = self.pos1w[i]
                self.pos1w[i] = self.pos2w[i]
                self.pos2w[i] = t
        for i in range(2):
            j = (i + 1) % 2
            if various.isinf(self.pos2[j]) and not various.isinf(self.pos2[i]) \
                    and not various.isinf(self.pos1[i]):
                self.pos2[i] = self.pos1[i]
            if various.isinf(self.pos1[j]) and not various.isinf(self.pos1[i]) \
                    and not various.isinf(self.pos2[i]):
                self.pos1[i] = self.pos2[i]

        self.asrect = self.pos1[0] == self.pos2[0] or self.pos1[1] == self.pos2[1]

        self.angle = self.get_angle()
        self.length = self.get_length()

    def get_angle(self):
        return math.atan2((self.pos2[1] - self.pos1[1]),
                          (self.pos2[0] - self.pos1[0]))

    def get_length(self):
        try:
            return math.hypot(self.pos2[0] - self.pos1[0],
                              self.pos2[1] - self.pos1[1])
        except OverflowError:
            return float('inf')

    def collides(self, circ):
        nradius = abs(circ.pos[0] - self.pos1w[0])
        if various.isinf(self.pos1w[1]) or various.isinf(self.pos2w[1]):
            if self.pos1w[1] < circ.pos[1] < self.pos2w[1] and \
                    nradius <= circ.radius:
                return nradius
        nradius = abs(circ.pos[1] - self.pos1w[1])
        if various.isinf(self.pos1w[0]) or various.isinf(self.pos2w[0]):
            if self.pos1w[0] < circ.pos[0] < self.pos2w[0] and \
                    nradius <= circ.radius:
                return nradius

        pos0 = [self.pos1[0], self.pos2[0]]
        pos1 = [self.pos1[1], self.pos2[1]]

        if circ.pos[0] + circ.radius < min(pos0) \
                or circ.pos[0] - circ.radius > max(pos0) \
                or circ.pos[1] + circ.radius < min(pos1) \
                or circ.pos[1] - circ.radius > max(pos1):
            return

        va = [circ.pos[0] - self.pos1[0], circ.pos[1] - self.pos1[1]]
        vb = [self.pos2[0] - self.pos1[0], self.pos2[1] -
              self.pos1[1]]
        try:
            va1 = [((va[0] * vb[0] + va[1] * vb[1]) /
                    (math.hypot(*vb) ** 2)) * vbx
                   for vbx in vb]
        except (ZeroDivisionError, OverflowError):
            return
        va1len = math.hypot(*va1)
        nradius = math.sqrt(math.hypot(*va) ** 2 - va1len ** 2)
        if nradius <= circ.radius and va1len - circ.radius <= self.length:
            return nradius

    def draw(self):
        self.world.back.draw.line(self.pos1, self.pos2,
                                  fillarea=self.fillarea,
                                  fillbg=self.fillbg,
                                  asrect=self.asrect)

class AdvancedShape:
    def cache_lines(self, precision):
        self.lines = []
        for x in self.shape(precision):
            self.lines.append(Line(self.level, *x))

class BezierCurve(Shape, AdvancedShape):
    def init(self, pos1, pos2, pos3, **kargs):
        self.pos1 = pos1
        self.pos2 = pos2
        self.pos3 = pos3

        self.lines_length = MinimalLine(pos1, pos2).length + \
            MinimalLine(pos2, pos3).length
        self.lines_num = self.lines_length / 300
        self.cache_lines(self.lines_num)

    def shape(self, precision, transform=None):
        pos1 = self.pos1
        pos2 = self.pos2
        pos3 = self.pos3
        if transform is not None:
            pos1 = transform(pos1)
            pos2 = transform(pos2)
            pos3 = transform(pos3)
        diff12 = [pos2[i] - pos1[i] for i in range(2)]
        diff23 = [pos3[i] - pos2[i] for i in range(2)]

        cp = pos1
        for i in range(int(precision)):
            p1 = [pos1[j] + diff12[j] * (i / precision) for j in range(2)]
            p2 = [pos2[j] + diff23[j] * (i / precision) for j in range(2)]
            ndiff = [p2[j] - p1[j] for j in range(2)]
            np = [p1[j] + ndiff[j] * (i / precision) for j in range(2)]
            yield cp, np
            cp = np
        yield cp, pos3

    def collides(self, circ):
        pos0 = [self.pos1[0], self.pos2[0], self.pos3[0]]
        pos1 = [self.pos1[1], self.pos2[1], self.pos3[1]]
        if circ.pos[0] + circ.radius < min(pos0) \
                or circ.pos[0] - circ.radius > max(pos0) \
                or circ.pos[1] + circ.radius < min(pos1) \
                or circ.pos[1] - circ.radius > max(pos1):
            return

        for x in self.lines:
            evt_radius = x.collides(circ)
            if evt_radius is not None:
                return evt_radius, x.angle

    def draw(self):
        shape = self.shape(self.lines_num, self.world.back.get_real_pos)
        self.world.back.draw.shape(shape, fillarea=self.fillarea,
                                   fillbg=self.fillbg, raw=True)
