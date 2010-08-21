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

##[ Name        ]## genericbackend
##[ Maintainer  ]## Niels Serup <ns@metanohi.org>
##[ Description ]## Generic graphics/sound backend
##[ Start date  ]## 2010 July 14

import math
import naghni.various as various

class GraphicsSoundBackend(object):
    def __init__(self, world, *args, **kargs):
        self.world = world
        self.screen = None

        self.draw = various.Container()
        self.draw.line = self.draw_line
        self.draw.rect = self.draw_rect
        self.draw.polygon = self.draw_polygon
        self.draw.circle = self.draw_circle
        self.draw.shape = self.draw_shape

        self.create = various.Container()
        self.create.surface = self.create_surface
        self.create.pattern = self.create_pattern
        self.create.color = self.create_color
        self.create.font = self.create_font
        self.create.clock = self.create_clock

        self.load = various.Container()
        self.load.image = self.load_image
        self.load.vector = self.load_vector

        self.get = various.Container()
        self.get.events = self.get_events
        self.get.mods = self.get_mods

        self.set = various.Container()
        self.set.icon = self.set_icon
        self.set.title = self.set_title
        self.set.bg_surface = self.set_bg_surface

        self.init(*args, **kargs)
        self.default_color = self.create.color(0, 0, 0)

    def get_real_pos(self, vpos):
        rpos = [0, 0]

        if various.isinf(vpos[1]):
            if vpos[1] > 0:
                if self.world.zoom < 1:
                    rpos[1] = -self.world.size[1] / self.world.zoom
                else:
                    rpos[1] = 0
            else:
                if self.world.zoom < 1:
                    rpos[1] = self.world.size[1] + self.world.size[1] / self.world.zoom
                else:
                    rpos[1] = self.world.size[1] + 1
        else:
            rpos[1] = (self.world.offset[1] + self.size[1] - vpos[1] - self.world.size[1] / 2) * self.world.zoom + self.world.size[1] / 2

        if various.isinf(vpos[0]):
            if vpos[0] > 0:
                if self.world.zoom < 1:
                    rpos[0] = self.world.size[0] + self.world.size[0] / self.world.zoom
                else:
                    rpos[0] = self.world.size[0] + 1
            else:
                if self.world.zoom < 1:
                    rpos[0] = -self.world.size[0] / self.world.zoom
                else:
                    rpos[0] = 0
        else:
            rpos[0] = (self.world.offset[0] + vpos[0] - self.world.size[0] / 2) * self.world.zoom + self.world.size[0] / 2
        return rpos

    def get_virtual_coor(self, i, coor):
        if i == 0:
            return (coor - self.world.size[0] / 2) / self.world.zoom + self.world.size[0] / 2 - self.world.offset[0]
        elif i == 1:
            return -(coor - (self.world.size[1] / 2) / self.world.zoom + self.world.size[1] / 2 - self.world.offset[1] + self.size[1])

    def get_virtual_pos(self, rpos):
        vpos = [0, 0]
        vpos[0] = (rpos[0] - self.world.size[0] / 2) / self.world.zoom + self.world.size[0] / 2 - self.world.offset[0]
        vpos[1] = -(rpos[1] - (self.world.size[1] / 2) / self.world.zoom + self.world.size[1] / 2 - self.world.offset[1] + self.size[1])
        return vpos

    def is_visible(self, *points):
        x = [p[0] for p in points]
        y = [p[1] for p in points]
        return max(x) >= 0 and min(x) < self.size[0] and \
            max(y) >= 0 and min(y) < self.size[1]

    def init(self, *args, **kargs):
        pass

    def rawblit(self, *args, **kargs):
        pass

    def blit(self, *args, **kargs):
        pass

    def flip(self):
        pass

    def resize(self, world, *args, **kargs):
        pass

    ### CREATE ###
    def create_surface(self, width, height, **kargs):
        pass

    def create_pattern(self, surf):
        pass

    def create_color(self, *args, **kargs):
        pass

    def create_font(self, **kargs):
        pass

    def create_clock(self):
        pass

    ### DRAW ###
    def draw_line(self, start_pos, end_pos, **kargs):
        pass

    def draw_rect(self, *points, **kargs):
        pass

    def draw_polygon(self, *points, **kargs):
        pass

    def draw_shape(self, shape, **kargs):
        pass

    def draw_circle(self, radius, pos, **kargs):
        pass

    ### LOAD ###
    def load_image(self, path, alpha=True):
        pass

    def load_vector(self, path):
        pass

    ### GET ###
    def get_events(self):
        pass

    def get_mods(self):
        pass

    ### SET ###
    def set_title(self, text):
        pass

    def set_icon(self, surf):
        pass

    def set_bg_surface(self, surf):
        pass
