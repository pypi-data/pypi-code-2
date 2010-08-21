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

##[ Name        ]## vectorgraphics
##[ Maintainer  ]## Niels Serup <ns@metanohi.org>
##[ Description ]## surface classes for vector graphics
##[ Start date  ]## 2010 July 22

import cairo
import numpy
from naghni.various import surface_to_string
from naghni.external.rsvgwrapper import rsvg

class VectorSurface:
    def __init__(self, backend, *args, **kargs):
        self.back = backend
        self.world = self.back.world
        self.init(*args, **kargs)

    def init(self):
        pass

class SVGSurface(VectorSurface):
    def init(self, path, surf_func):
        self.svg = rsvg.Handle(path)
        self.size = map(float, self.svg.get_dimension_data()[:2])
        self.load_data = surf_func

    def render(self, *size):
        size = [s < 1 and 1 or s for s in size]
        isize = [int(s) for s in size]
        data = numpy.empty(isize[0] * isize[1] * 4, dtype=numpy.int8)

        cairo_surface = cairo.ImageSurface.create_for_data(
            data, cairo.FORMAT_ARGB32, isize[0], isize[1], isize[0] * 4)

        ctx = cairo.Context(cairo_surface)
        ctx.scale(*[size[i] / self.size[i] for i in range(2)])
        self.svg.render_cairo(ctx)

        data_str = surface_to_string(cairo_surface, 'BGRA', 'RGBA')
        return self.load_data(data_str, isize, 'RGBA')
