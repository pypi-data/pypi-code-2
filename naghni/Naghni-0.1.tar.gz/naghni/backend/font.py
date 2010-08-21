#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Naghni: a breath-taking side-scroller focusing on round lifeforms
# Copyright (C) 2010  Niels Serup, based on font.py from
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

##[ Name        ]## font
##[ Maintainer  ]## Niels Serup <ns@metanohi.org>
##[ Description ]## Contains the Font class, which makes it possible
                  # to write text 
##[ Start date  ]## 2010 July 14

class Font:
    def __init__(self, world, **kargs):
        self.world = world
        self.back = self.world.back
        self.path = kargs.get('path')
        self.size = kargs.get('size') or 20
        self.create_font = kargs.get('create')

        self.font = self.create_font(self.path, self.size)

    def write(self, text, **kargs):
        color = kargs.get('color') or self.back.create.color(0, 0, 0)
        antialias = kargs.get('antialias') or True
        size = kargs.get('size')
        if size is not None and size != self.size:
            self.size = size
            self.font = self.create_font(self.path, self.size)

        return self.font.render(text, antialias, color)
