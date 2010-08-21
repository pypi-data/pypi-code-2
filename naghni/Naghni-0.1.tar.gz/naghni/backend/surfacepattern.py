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

##[ Name        ]## surfacepattern
##[ Maintainer  ]## Niels Serup <ns@metanohi.org>
##[ Description ]## contains the SurfacePattern class, making easy
                  # pattern creation very easy
##[ Start date  ]## 2010 July 22

import math

class SurfacePattern:
    def __init__(self, world, surface):
        self.world = world
        self.back = self.world.back

        self.pattern_surface = surface
        try:
            self.size = self.pattern_surface.size
            self.is_vector_pattern = True
        except AttributeError:
            self.size = self.pattern_surface.get_size()
            self.is_vector_pattern = False
        self.display_size = self.size[:]

        self.overlay_surface = \
            self.back.create.surface(*self.world.size)
        self.overlay_surface.set_colorkey(0x000000)
        self.temp_surface = self.back.create.surface(*self.world.size)
        self.temp_surface.set_colorkey(0xffffff)

        self.create()
        self.update()

    def blit(self, surf, pos):
        self.overlay_surface.blit(surf, pos)

    def create(self):
        p_size = [int(s * self.world.zoom) or 1 for s in self.size]
        self.display_size = p_size

        if self.is_vector_pattern:
            pattern = self.pattern_surface.render(*p_size)
        else:
            pattern = self.back.resize(self.pattern_surface, p_size)

        self.bg_surface = self.back.create.surface(
            *[self.world.size[i] + p_size[i] for i in range(2)])


        b_size = self.bg_surface.get_size()
        for i in range(int(math.ceil(b_size[0] / p_size[0])) + 1):
            for j in range(int(math.ceil(b_size[1] / p_size[1])) + 1):
                self.bg_surface.blit(pattern,
                                     (i * p_size[0], j * p_size[1]))

    def update(self):
        self.overlay_surface.fill(self.back.create.color(255, 255, 255))

    def draw(self):
        bg = self.temp_surface
        bg_pos = [(self.world.offset[i] * self.world.zoom) %
                  self.display_size[i] - self.display_size[i]
                  for i in range(2)]

        bg.blit(self.bg_surface, bg_pos)

        bg.blit(self.overlay_surface, (0, 0))

        self.back.rawblit(bg)
