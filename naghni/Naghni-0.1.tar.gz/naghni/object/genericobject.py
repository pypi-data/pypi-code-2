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

##[ Name        ]## genericobject
##[ Maintainer  ]## Niels Serup <ns@metanohi.org>
##[ Description ]## Contains the base class for level objects
##[ Start date  ]## 2010 July 18

import math

class LevelObject:
    def __init__(self, level, *args, **kargs):
        self.level = level
        self.world = self.level.world
        self.back = self.world.back

        self.fillarea = kargs.get('fillarea')
        self.fillbg = kargs.get('fillbg')

        self.init(*args)

    def init(self):
        pass

    def check_for_collision(self, circ):
        rets = self.collides(circ)
        try:
            evt_radius = rets[0]
        except TypeError:
            evt_radius = rets
        if evt_radius is not None:
            try:
                angle = rets[1]
            except (IndexError, TypeError):
                angle = self.angle
            return angle, evt_radius
        return False

    def update(self):
        pass

    def action(self):
        pass

    def collides(self, circ):
        pass

    def draw(self, **kargs):
        pass
