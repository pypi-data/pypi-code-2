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

##[ Name        ]## world
##[ Maintainer  ]## Niels Serup <ns@metanohi.org>
##[ Description ]## Controls the major points of everything
##[ Start date  ]## 2010 July 14

import sys
import os
import math
from datetime import datetime

from naghni.level import Level as GenericLevel
from naghni.statusprinter import StatusPrinter
from naghni.backend.locals import *
import naghni.various as various

class World(object):
    def __init__(self, etc, error=None):
        for x in eval(str(etc)).items():
            self.__setattr__(*x)

        if error is None:
            self.error = various.usable_error
        else:
            self.error = error

        self.status = StatusPrinter(self, 'World', 'white', 'green')
        self.status('''\
Naghni is free software: you are free to change and redistribute it
under the terms of the GNU GPL, version 3 or any later version.
There is NO WARRANTY, to the extent permitted by law. See
<http://metanohi.org/projects/naghni/> for downloads and documentation.''')

    def start(self):
        self.status('Starting game...')

        datapaths = ('/usr/local/share/naghni/data',
                     '/usr/share/naghni/data',
                     os.path.join(os.path.split(os.path.dirname(
                        __file__))[0], 'data')
                     )

        self.orig_dir = os.getcwd()
        found_data_path = False
        for x in datapaths:
            if os.path.isdir(x):
                os.chdir(x)
                found_data_path = True
                break
        if not found_data_path:
            self.error('no data directory found')

        self.zoom = 1
        self.running = False

        self.max_fps = 50
        self.current_fps = 30

        self.offset = [0, 0]

        if self.backend_name == 'pygame':
            import naghni.backend.pygamebackend as backend
            self.back = backend.GraphicsSoundBackend(self, require_pygame='1.8.1')
        else:
            self.error('backend "%s" is not supported' %
                       self.backend_name)

        self.back.set.title('Naghni')
        self.back.set.icon(self.back.load.image('naghni-icon.png'))
        self.std_font = self.back.create.font(path='fonts/chumbly.ttf')

        self.bgsurf = self.back.create.surface(*self.size)
        self.bgsurf.fill(self.back.create.color(255, 255, 255))

        dirkeys = various.KeyGroup(up=K_UP, down=K_DOWN,
                                   left=K_LEFT, right=K_RIGHT)
        funckeys = various.KeyGroup(zoomin=K_PAGEUP,
                                    zoomout=K_PAGEDOWN,
                                    restart=K_r)
        debugkeys = various.KeyGroup(KMOD_SHIFT, fps=K_f)
        self.keygroups = [dirkeys, funckeys, debugkeys]

        self.levels = []
        self.level_num = 0
        if self.levelpath:
            self.load_level(os.path.join(
                    self.orig_dir, self.levelpath))
            self.start_level(0)
        else:
            for x in os.walk('naghnilevels'):
                for y in sorted(x[2]):
                    if y.endswith('~') or y.endswith('.pyc') or \
                            (y.startswith('#') and y.endswith('#')) \
                            or y == '__init__.py':
                        continue
                    self.load_level(os.path.join(x[0], y))
                self.start_level(0)

        self.run()

    def load_level(self, path):
        abspath = os.path.abspath(path)
        spl = os.path.split(abspath)
        spl2 = os.path.split(spl[0])

        sys.path.append(spl2[0])
        mod = '%s.%s' % (spl2[1], spl[1][:spl[1].rfind('.')])
        level = __import__(mod, globals(), locals(),
                           ['Level'], -1)
        self.levels.append(level.Level)
        #exec(open(path).read() + \
        #         '\nself.levels.append(Level)')

    def start_level(self, num):
        self.level = self.levels[num](self)
        self.level.start()

    def next_level(self):
        self.level_num = (self.level_num + 1) % len(self.levels)
        self.start_level(self.level_num)

    def run(self):
        self.clock = self.back.create.clock()
        self.running = True

        while self.running:
            mods = self.back.get.mods()
            for x in self.keygroups:
                x.update()
            for event in self.back.get.events():
                if event.type == QUIT:
                    self.running = False
                    break
                elif event.type == KEYDOWN:
                    for x in self.keygroups:
                        x.check(event.key, mods)
                elif event.type == KEYUP:
                    for x in self.keygroups:
                        x.uncheck(event.key, mods)

            self.level.update()
            self.update_offset()
            self.draw()

            self.current_fps = 1000.0 / self.clock.tick(self.max_fps)

    def update_offset(self):
        size = self.size
        epix = self.level.main_solid.radius * 2
        zoomextra = [(s / self.zoom - s) / 2 for s in self.size]
        cpos = self.level.main_solid.pos
        csize = self.level.main_solid.radius * self.zoom * 2
        if csize > size[0] / 2:
            self.offset[0] = -(cpos[0] - epix / 2 - (size[0] - csize) / \
                2 / self.zoom + zoomextra[0])
        elif cpos[0] - epix < -self.offset[0] - zoomextra[0]:
            self.offset[0] = -(cpos[0] - epix) - zoomextra[0]
        elif cpos[0] - size[0] + epix > -self.offset[0] + zoomextra[0]:
            self.offset[0] = -(cpos[0] - size[0] + epix) + zoomextra[0]
        if csize > size[1] / 2:
            self.offset[1] = cpos[1] - epix / 2 - (size[1] - csize) / \
                2 / self.zoom + zoomextra[1]
        elif cpos[1] - epix < self.offset[1] - zoomextra[1]:
            self.offset[1] = cpos[1] - epix + zoomextra[1]
        elif cpos[1] - size[1] + epix > self.offset[1] + zoomextra[1]:
            self.offset[1] = cpos[1] - size[1] + epix - zoomextra[1]

    def draw(self):
        self.level.draw()
        if 'fps' in self.keygroups[2].toggled:
            self.back.rawblit(self.std_font.write('FPS: ' +
                    str(int(self.current_fps))), (10, 10))
        self.back.flip()

    def end(self):
        self.status('Stopping game...')
