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

##[ Name        ]## level
##[ Maintainer  ]## Niels Serup <ns@metanohi.org>
##[ Description ]## Controls levels
##[ Start date  ]## 2010 July 18

import math
from datetime import datetime
from naghni.various import SubList

class Waiter:
    def __init__(self, func, secs):
        self.func = func
        self.wait = secs
        self.time = datetime.now()

    def update(self):
        if (datetime.now() - self.time).seconds >= \
                self.wait:
            self.func()

class Level:
    """A generic level"""
    name="Unnamed level"

    def __init__(self, world):
        self.world = world
        self.back = self.world.back

        self.objects = []
        self.shapes = SubList(self.objects)
        self.solids = SubList(self.objects)
        self.patterns = []
        self.keygroups = self.world.keygroups
        self.main_solid = None

        self.message = None
        self.msg_gone_in = 0
        self.waiters = []

        self.create_level()

    def create_level(self):
        pass

    def start(self):
        self.show_message('Welcome to %s.' % self.name, 3)

    def end(self):
        self.show_message('You have completed this level!', 3)
        self.wait(self.world.next_level, 4)

    def wait(self, func, secs):
        self.waiters.append(Waiter(func, secs))

    def show_message(self, msg, secs):
        self.message = self.world.std_font.write(msg)
        self.msg_time = datetime.now()
        self.msg_gone_in = secs

    def add_solid(self, clas, *args, **kargs):
        solid = clas(self, *args, **kargs)
        self.solids.append(solid)
        if kargs.get('function') == 'character' and \
                kargs.get('lead') in (None, True):
            self.main_solid = solid
        return solid

    def add_shape(self, clas, *args, **kargs):
        shape = clas(self, *args, **kargs)
        self.shapes.append(shape)
        return shape

    def add_pattern(self, path):
        pattern = self.back.create.pattern(
            self.back.load.image(path))
        self.patterns.append(pattern)
        return pattern

    def zoom_in(self, val):
        self.zoom(True, val)

    def zoom_out(self, val):
        self.zoom(False, val)

    def zoom(self, zoom_in, val):
        val /= self.world.current_fps
        val += 1
        if zoom_in:
            self.world.zoom *= val
        else:
            self.world.zoom /= val
        for x in self.patterns:
            x.create()

    def restart(self):
        self.world.start_level(self.world.level_num)

    def update(self):
        dirkeys = self.keygroups[0]
        funckeys = self.keygroups[1]

        downdirkey = dirkeys.current
        dirkey = dirkeys.get_top()
        if downdirkey == 'up':
            self.main_solid.inst.thrust(downdirkey)
        if dirkey in ('left', 'right', 'down'):
            self.main_solid.inst.thrust(dirkey)

        funckey = funckeys.get_top()
        if funckey == 'zoomin':
            self.zoom_in(.9)
        elif funckey == 'zoomout':
            self.zoom_out(.9)
        elif funckey == 'restart':
            self.restart()

        for x in self.patterns:
            x.update()

        for x in self.solids:
            x.update()

        for x in self.waiters:
            x.update()

        if self.msg_gone_in:
            t = (datetime.now() - self.msg_time).seconds
            if t >= self.msg_gone_in:
                self.message = None

    def draw(self):
        self.back.rawblit(self.world.bgsurf)
        for x in self.shapes:
            x.draw()

        for x in self.solids:
            if x != self.main_solid:
                x.draw()

        for x in self.patterns:
            x.draw()

        self.main_solid.draw()

        if self.message:
            self.back.rawblit(self.message, [
                    (self.world.size[i] - self.message.get_size()[i])
                    / 2 for i in range(2)])
