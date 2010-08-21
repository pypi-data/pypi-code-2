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

##[ Name        ]## pygamebackend
##[ Maintainer  ]## Niels Serup <ns@metanohi.org>
##[ Description ]## PyGame backend
##[ Start date  ]## 2010 July 14

import os.path
import pygame
from pygame.locals import *

import naghni.backend.genericbackend as generic
import naghni.backend.vectorgraphics as vector
from naghni.backend.font import Font
from naghni.backend.surfacepattern import SurfacePattern

class Color(pygame.Color):
    def mix_color(self, color):
        a = self.normalize()
        b = color.normalize()
        r = a[0] * (1.0 - b[3]) + b[0] * b[3]
        g = a[1] * (1.0 - b[3]) + b[1] * b[3]
        b = a[2] * (1.0 - b[3]) + b[2] * b[3]
        return Color(int(r * 255), int(g * 255), int(b * 255))

class GraphicsSoundBackend(generic.GraphicsSoundBackend):
    def init(self, **kargs):
        require_pygame = kargs.get('require_pygame')
        if require_pygame is not None and \
                tuple([int(x) for x in require_pygame.split('.')]) > \
                pygame.version.vernum:
            self.world.error(
                'PyGame version too old; use at least version %s'
                % require_pygame, False)
        pygame.display.init()
        pygame.font.init()
        # Sound files must be sampled to 44.1 kHz
        pygame.mixer.pre_init(44100)
        pygame.mixer.init()
        pygame.mouse.set_visible(False)

        self.start_screen()
        self.bgsurf = self.screen

    def start_screen(self):
        world = self.world

        if world.is_fakefullscreen:
            info = pygame.display.Info()
            self.size = info.current_w, info.current_h
            world.size = self.size
        else:
            self.size = world.size

        flags = 0
        if world.is_fullscreen:
            flags |= FULLSCREEN
        if world.has_hwaccel:
            flags |= HWSURFACE
        if world.has_doublebuf:
            flags |= DOUBLEBUF
        if not world.has_border or world.is_fakefullscreen:
            flags |= NOFRAME
        self.screen = pygame.display.set_mode(self.size, flags, 32)

    def rawblit(self, surf, pos=(0, 0), area=None):
        if area is not None:
            area = pygame.Rect(area[0], [area[1][i] - area[0][i] for i
                                         in range(2)])
            self.bgsurf.blit(surf, pos, area)
        else:
            self.bgsurf.blit(surf, pos)

    def raw_rawblit(self, surf, pos=(0, 0), area=None):
        if area is not None:
            area = pygame.Rect(area[0], [area[1][i] - area[0][i] for i
                                         in range(2)])
            self.screen.blit(surf, pos, area)
        else:
            self.screen.blit(surf, pos)

    def blit(self, surf, pos=(0, 0)):
        self.rawblit(surf, self.get_real_pos(pos))

    def flip(self):
        pygame.display.flip()

    def resize(self, surface, size):
        return pygame.transform.smoothscale(surface, size)

    ### CREATE ###
    def create_surface(self, width, height, **kargs):
        surf = pygame.Surface((width, height))
        if kargs.get('alpha'):
            surf = surf.convert_alpha()
        return surf

    def create_pattern(self, surf):
        return SurfacePattern(self.world, surf)

    def create_color(self, *args, **kargs):
        arglen = len(args)
        typ = (kargs.get('type') or 'RGB').upper()
        if typ == 'RGB':
            return Color(*args)
        elif typ == 'HSL':
            col = Color(0)
            args = list(args)
            if arglen == 3:
                args.append(1)
            args = [args[0] * 360, args[1] * 100, \
                args[2] * 100, args[3] * 100]
            map(int, args)
            col.hsla = args
            return col

    def create_font(self, **kargs):
        kargs['create'] = pygame.font.Font
        return Font(self.world, **kargs)

    def create_clock(self):
        return pygame.time.Clock()

    ### DRAW ###
    def draw_line(self, start_pos, end_pos, **kargs):
        color = kargs.get('color') or self.default_color
        width = kargs.get('width') or 1
        surf = kargs.get('surf') or self.bgsurf
        fillarea = kargs.get('fillarea') or None
        raw = kargs.get('raw') or False
        asrect = kargs.get('asrect') or False
        if fillarea is None:
            if not raw:
                pygame.draw.line(surf, color, self.get_real_pos(start_pos),
                                 self.get_real_pos(end_pos), width)
            else:
                pygame.draw.line(surf, color, start_pos, end_pos,
                                 width)
        else:
            kargs['width'] = 0
            if not raw:
                top = float('-inf')
                left = float('-inf')
                bottom = float('inf')
                right = float('inf')
            else:
                top = self.world.size[1]
                left = 0
                bottom = 0
                right = self.world.size[0]
            if fillarea == (0, -1):
                points = (
                    start_pos, end_pos, (end_pos[0], top),
                    (start_pos[0], top))
            elif fillarea == (0, 1):
                points = (
                    start_pos, end_pos, (end_pos[0], bottom),
                    (start_pos[0], bottom))
            elif fillarea == (-1, 0):
                points = (
                    start_pos, end_pos, (left, end_pos[1]),
                    (left, start_pos[1]))
            elif fillarea == (1, 0):
                points = (
                    start_pos, end_pos, (right, end_pos[1]),
                    (right, start_pos[1]))

            if asrect:
                self.draw.rect(*points, **kargs)
            else:
                self.draw.polygon(*points, **kargs)

    def draw_rect(self, *points, **kargs):
        color = kargs.get('color') or self.default_color
        width = kargs.get('width') or 0
        surf = kargs.get('surf') or self.bgsurf
        raw = kargs.get('raw') or False
        fillbg = kargs.get('fillbg')

        if not raw:
            points = [self.get_real_pos(x) for x in points]

        if self.is_visible(*points):
            xs = [x[0] for x in points]
            ys = [x[1] for x in points]
            top = min(ys)
            left = min(xs)
            bottom = max(ys)
            right = max(xs)
            rect = pygame.Rect(left, top, right - left, bottom - top)

            if fillbg:
                pygame.draw.rect(fillbg.overlay_surface, 0x000000, rect, 0)
            else:
                pygame.draw.rect(surf, color, rect, width)

    def draw_polygon(self, *points, **kargs):
        color = kargs.get('color') or self.default_color
        width = kargs.get('width') or 0
        surf = kargs.get('surf') or self.bgsurf
        raw = kargs.get('raw') or False
        fillbg = kargs.get('fillbg')

        if not raw:
            points = [self.get_real_pos(x) for x in points]

        if self.is_visible(*points):
            if fillbg:
                pygame.draw.polygon(fillbg.overlay_surface, 0x000000, points, 0)
            else:
                pygame.draw.polygon(surf, color, points, width)

    def draw_circle(self, radius, pos, **kargs):
        color = kargs.get('color') or self.default_color
        width = kargs.get('width') or 0
        surf = kargs.get('surf') or self.bgsurf
        raw = kargs.get('raw') or False
        border = kargs.get('border')
        borderwidth = kargs.get('borderwidth') or 1
        fillbg = kargs.get('fillbg')

        if not raw:
            pos = self.get_real_pos(pos)
            radius = radius * self.world.zoom

        pos = [int(x) for x in pos]
        radius = int(radius)
        if fillbg:
            pygame.draw.circle(fillbg.overlay_surface, 0x000000, pos,
                               radius, 0)
        else:
            pygame.draw.circle(surf, color, pos,
                               radius, width)

        if border:
            borderwidth = int(borderwidth)
            if borderwidth == 0:
                borderwidth = 1
            if borderwidth >= radius:
                borderwidth = radius - 1
            if borderwidth < 0:
                borderwidth = 0
            pygame.draw.circle(surf, border, pos,
                               radius, borderwidth)
 
    def draw_shape(self, shape, **kargs):
        for x in shape:
            self.draw.line(*x, **kargs)

    ### LOAD ###
    def load_image(self, path, alpha=True):
        try:
            img = pygame.image.load(path)
            if alpha:
                return img.convert_alpha()
            else:
                return img.convert()
        except Exception:
            return self.load_vector(path)

    def load_vector(self, path):
        path = os.path.normpath(path)
        fname = os.path.split(path)[1]
        p = fname.rfind('.') + 1
        if p != 0 and p < len(fname):
            extension = fname[p:].lower()
        else:
            extension = 'svg' # Default vector format
        if extension == 'svg':
            return vector.SVGSurface(self, path, pygame.image.frombuffer)
        else:
            self.world.error('"%s" format is not supported' % extension)

    ### GET ###
    def get_events(self):
        return pygame.event.get()

    def get_mods(self):
        return pygame.key.get_mods()

    ### SET ###
    def set_title(self, text):
        return pygame.display.set_caption(text)

    def set_icon(self, surf):
        return pygame.display.set_icon(surf)

    def set_bg_surface(self, surf):
        self.bgsurf = surf
