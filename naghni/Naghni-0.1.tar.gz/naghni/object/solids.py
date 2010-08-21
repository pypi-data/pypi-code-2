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

##[ Name        ]## solids
##[ Maintainer  ]## Niels Serup <ns@metanohi.org>
##[ Description ]## Contains classes for circles, etc.
##[ Start date  ]## 2010 July 18

import math
from naghni.object.genericobject import LevelObject
from naghni.object.shapes import Line
from naghni.object.solidtypes import *

class Solid(LevelObject):
    def __init__(self, level, *args, **kargs):
        try:
            self.density = kargs['density']
            del kargs['density']
        except KeyError:
            self.density = 0.1
        try:
            typ = kargs['function']
            if typ == 'eat':
                self.type = Edible
            elif typ == 'hole':
                self.type = Hole
            elif typ == 'air':
                self.type = Air
            elif typ == 'character':
                self.type = Character
            else:
                self.type = Ground
            del kargs['function']
        except KeyError:
            self.type = Ground

        self.speed = [0, 0]
        self.bounce_off = True
        LevelObject.__init__(self, level, *args, **kargs)
        self.color = self.color_from_density()
        self.inst = self.type(self)
        self.update = self.inst.update
        self.action = self.inst.action
        self.draw = self.inst.draw

    def get_area(self):
        return 0

    def get_speed(self):
        return math.hypot(*self.speed)

    def get_mass(self):
        return self.get_area() * self.density

    def get_angle(self):
        return math.atan2(self.speed[1], self.speed[0])

    def color_from_density(self, lightness=0.4):
        return self.back.create.color(self.density * 0.8 + 0.2, 0.7, lightness, type='HSL')

class Circle(Solid):
    def init(self, pos, radius):
        self.pos = list(pos)
        self.radius = radius

    def get_area(self):
        return self.radius ** 2 * math.pi

    def collides(self, circ):
        length = math.hypot(*[self.pos[i] - circ.pos[i] for i in
                              range(2)])

        if length <= self.radius + circ.radius:
            try:
                angle = 2*math.pi-math.atan((self.pos[0] - circ.pos[0]) /
                                  (self.pos[1] - circ.pos[1]))
            except ZeroDivisionError:
                angle = 0
            self.action()
            return length - self.radius, angle

    def add_mass(self, mass, density):
        s_area = self.get_area()
        s_mass = s_area * self.density
        area = mass / density + s_area
        self.radius = math.sqrt(area / math.pi)
        n_mass = s_mass + mass
        self.density = n_mass / area
        self.color = self.color_from_density()

    def draw(self, **kargs):
        kargs['fillbg'] = self.fillbg
        if not 'color' in kargs:
            kargs['color'] = self.color
        self.back.draw.circle(self.radius, self.pos, **kargs)

class Polygon(Solid):
    def init(self, pos, *points):
        self.pos = pos
        self.points = points
        self.cache_lines()

    def cache_lines(self):
        self.lines = []
        pp = self.points[-1]
        for i in range(len(self.points)):
            cp = self.points[i]
            self.lines.append(Line(self.level, pp, cp))
            pp = cp

    def get_area(self):
        x = [p[0] for p in self.points]
        y = [p[1] for p in self.points]
        pl = len(self.points)
        return 0.5 * sum([x[i] * y[(i + 1) % pl]
                          - x[(i + 1) % pl] * y[i]
                          for i in range(pl)])

    def collides(self, circ):
        for x in self.lines:
            evt_radius = x.collides(circ)
            if evt_radius is not None:
                self.action()
                return evt_radius, x.angle

    def draw(self, **kargs):
        kargs['fillbg'] = self.fillbg
        if not 'color' in kargs:
            kargs['color'] = self.color
        self.back.draw.polygon(*self.points, **kargs)

class RegularPolygon(Polygon):
    def init(self, pos, radius, sides):
        pts = []
        x = pos[0]
        y = pos[1]
        r = radius
        f = math.pi * 2 / sides
        for i in range(sides):
            v = i * f
            pts.append([x + math.cos(v) * r, y + math.sin(v) * r])

        self.radius = radius
        self.sides = sides
        Polygon.init(self, pos, *pts)
