#!/usr/bin/env python
# -*- coding: utf-8 -*-

# shadowloss: a stickman-oriented game against time
# Copyright (C) 2010  Niels Serup

# This file is part of shadowloss.
#
# shadowloss is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# shadowloss is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with shadowloss.  If not, see <http://www.gnu.org/licenses/>.

##[ Name        ]## shadowloss.world
##[ Maintainer  ]## Niels Serup <ns@metanohi.org>
##[ Description ]## Controls the major aspects of the game
##[ Start date  ]## 2010 September 13

import os
import pygame
from pygame.locals import *
import fnmatch
from shadowloss.settingsparser import SettingsParser
from shadowloss.level import *
import shadowloss.cairogame as cairogame
import shadowloss.various as various
import shadowloss.generalinformation as ginfo

INVALID_FILENAMES = (
    '*~', '#*#'
    )

config_file_translations = {
    'verbose': 'term_verbose',
    'color errors': 'term_color_errors',
    'fullscreen': 'use_fullscreen',
    'zoom': 'disp_zoom',
    'fakefullscreen': 'use_fakefullscreen',
    'size': 'disp_size',
    'border': 'use_border',
    'hwaccel': 'use_hwaccel',
    'doublebuf': 'use_doublebuf',
    'max fps': 'max_fps',
    'show debug': 'show_debug',
    'mute': 'mute'
}

class World(SettingsParser):
    virtual_size=(600, 200)

    def __init__(self, **options):
        SettingsParser.__init__(self, config_file_translations,
                                **options)
        # Get values, or set them to default ones
        self.set_if_nil('error_function', various.usable_error)
        self.set_if_nil('data_dir', ginfo.global_data_dir)
        self.set_if_nil('term_verbose', True)
        self.set_if_nil('term_color_errors', True)
        self.set_if_nil('use_fullscreen', False)
        self.set_if_nil('disp_zoom', 1)
        self.set_if_nil('use_fakefullscreen', False)
        self.set_if_nil('disp_size', None)
        self.set_if_nil('use_border', True)
        self.set_if_nil('use_hwaccel', True)
        self.set_if_nil('use_doublebuf', True)
        self.set_if_nil('max_fps', None)
        self.set_if_nil('show_debug', False)
        self.set_if_nil('mute', False)

        self.levels = options.get('levels') or []

        if self.disp_size is not None:
                    # Parse display size input
            try:
                spl = self.disp_size.split('x')
                self.disp_size = []
                for i in range(2):
                    if spl[i] == '':
                        self.disp_size.append(None)
                    else:
                        self.disp_size.append(int(spl[i]))
                if len(self.disp_size) < 2:
                    raise Exception()
            except Exception:
                self.error('size syntax is wrong, use [WIDTH]x[HEIGHT], quitting', True)

    def error(self, msg, done=None):
        if self.term_verbose:
            self.error_function(msg, done, color=self.term_color_errors)

    def status(self, msg):
        if self.term_verbose:
            print ginfo.program_name + ': ' + msg

    def create_level(self, path):
        return Level(self, path)

    def set_current_level(self, num):
        if num is None:
            self.current_level = None
        else:
            self.current_level = self.levels[num]
        self.current_level_index = num
        self.current_level.switch_hook()

    def previous_level(self):
        if self.current_level_index > 0:
            n = self.current_level_index - 1
            self.set_current_level(n)

    def next_level(self):
        self.set_current_level((self.current_level_index + 1) %
                               len(self.levels))

    def accepts_filename(self, fn):
        for x in INVALID_FILENAMES:
            if fnmatch.fnmatch(fn, x):
                return False

        return True

    def start(self):
        pygame.display.init()
        pygame.font.init()
        pygame.mixer.pre_init(44100) # Sound files must be resampled
        pygame.mixer.init()          # to 44.1 kHz

        self.create_screen()

        pygame.display.set_caption(ginfo.program_name)
        pygame.mouse.set_visible(False)

        self.std_font = pygame.font.Font(
            os.path.join(self.data_dir, 'fonts',
            'UniversalisADFCdStd-Bold.otf'), 250)

        if not self.levels:
            for x in os.walk(os.path.join(self.data_dir, 'levels')):
                for y in x[2]:
                    if self.accepts_filename(y):
                        self.levels.append(os.path.join(x[0], y))
            self.levels.sort()
                        
        self.levels = [self.create_level(x) for x in self.levels]
        self.set_current_level(0)

        self.shooting = False

        self.clock = pygame.time.Clock()
        if self.max_fps is not None:
            self.tick = lambda: self.clock.tick(self.max_fps)
        else:
            self.tick = self.clock.tick

        if not self.mute:
            pygame.mixer.music.load(
                os.path.join(self.data_dir, 'music', 'bgmusic.ogg'))
            pygame.mixer.music.play(-1)
        self.run()

    def end(self):
        pass

    def create_screen(self):
        # The screen is by default just a window of the same
        # dimensions as the virtual screen. This can be changed to
        # fullscreen (still with the same dimensions) or to different
        # dimensions, eventually with bars if the height ratio differs
        # from the width ratio.
        flags = 0
        barsize = None
        self.screen_bars = [None, None]
        self.screen_offset = [0, 0] # Might get changed if bars need
                                    # to be added
        if self.use_fakefullscreen or self.disp_size is not None:
            # Get dimensions (screen size if use_fakefullscreen,
            # user-specified size otherwise)
            if self.use_fakefullscreen or (self.disp_size is not None and
                                           self.disp_size[0] is None and
                                           self.disp_size[1] is None):
                try:
                    info = pygame.display.Info()
                    screen_size = info.current_w, info.current_h
                    if screen_size[0] == -1: # in this case, size[1] will also be -1
                        self.error('your SDL is too old for width and height detection', True)
                except Exception:
                    self.error('your PyGame is too old for width and height detection', True)
            else:
                screen_size = list(self.disp_size)
            if screen_size[0] is None:
                self.disp_zoom = screen_size[1] / float(self.virtual_size[1])
                screen_size[0] = int(self.virtual_size[0] * self.disp_zoom)
            elif screen_size[1] is None:
                self.disp_zoom = screen_size[0] / float(self.virtual_size[0])
                screen_size[1] = int(self.virtual_size[1] * self.disp_zoom)
            else:
                # The given width and height might not match the ratio
                # of the virtual width and height. Fix this by adding
                # bars. Sometimes bars should be on the x axis,
                # sometimes on the y axis. This is what a and b stands
                # for.
                scales = [screen_size[i] / float(self.virtual_size[i]) for i in range(2)]
                if scales[0] < scales[1]: a = 0; b = 1
                else:                     a = 1; b = 0

                self.disp_zoom = scales[a]
                self.screen_offset[b] = int((screen_size[b] -
                                             self.virtual_size[b] * self.disp_zoom) / 2)
                barsize = [0, 0]
                barsize[a] = screen_size[a]
                barsize[b] = self.screen_offset[b]
            self.window_size = screen_size
            self.status('Modified size of game is: %dx%d' % tuple(self.window_size))
            if not self.use_border or self.use_fakefullscreen:
                flags = NOFRAME
            if self.use_doublebuf:
                if flags is not 0:
                    flags |= DOUBLEBUF
                else:
                    flags = DOUBLEBUF
            if self.use_fullscreen:
                if flags is not 0:
                    flags |= FULLSCREEN
                else:
                    flags = FULLSCREEN
                if self.use_hwaccel:
                    flags |= HWSURFACE
        else:
            # Check if a zoom level has been given
            if self.disp_zoom != 1:
                self.window_size = [int(x * self.disp_zoom) for x in self.virtual_size]
                self.status('Scaled size of game is: %dx%d' % tuple(self.window_size))
            else:
                self.window_size = self.virtual_size
            if not self.use_border or self.use_fakefullscreen:
                flags = NOFRAME
            if self.use_doublebuf:
                if flags is not 0:
                    flags = flags | DOUBLEBUF
                else:
                    flags = DOUBLEBUF
            if self.use_fullscreen:
                if flags is not 0:
                    flags = flags | FULLSCREEN
                else:
                    flags = FULLSCREEN
                if self.use_hwaccel:
                    flags |= HWSURFACE

        self.real_size = [self.window_size[i] - self.screen_offset[i]
                          * 2 for i in range(2)]
        if self.disp_zoom is None:
            self.disp_zoom = float(self.real_size) / self.virtual_size
        # Finally create the screen
        self.screen = pygame.display.set_mode(self.window_size, flags,
                                              32)
        cairogame.set_screen(self.screen)
        if barsize is not None:
            self.screen_bars[b] = pygame.Surface(barsize).convert()
            self.screen_bars[b].fill((255, 255, 255))

        # Create the background surface
        self.bgsurface = pygame.Surface(self.window_size).convert()
        self.bgsurface.fill((0, 0, 0))

    def debug_print(self, text):
        if self.show_debug:
            print text

    def run(self):
        done = False
        while not done:
            if self.show_debug:
                self.print_debug_information()

            letters = []
            for x in pygame.event.get():
                if x.type == KEYDOWN:
                    if x.key == K_ESCAPE:
                        done = True
                    if self.current_level.status == PLAYING:
                        if x.key == K_SPACE:
                            self.shooting = True
                        else:
                            letter = x.unicode.lower()
                            if letter:
                                letters.append(letter)
                    else:
                        if x.key == K_SPACE or x.key == K_RIGHT:
                            self.next_level()
                        elif x.key == K_LEFT:
                            self.previous_level()
                        elif x.key == K_r:
                            self.current_level.start()
                elif x.type == KEYUP:
                    if x.key == K_SPACE:
                        if self.current_level.status == PLAYING:
                            self.shooting = False
                elif x.type == QUIT:
                    done = True
            self.current_level.update(letters)
            self.draw()
            self.tick()

    def print_debug_information(self):
        print 'FPS:', self.clock.get_fps()

    # Programmer's note: Sorry about all these different
    # point-to-another-point functions. It is messy.
    
    def center_point(self, p, rect):
        """Center a point in the window based on a stickfigure frame"""
        x = ((self.virtual_size[0] - rect[0]) / 2 + p[0]) * \
            self.disp_zoom + self.screen_offset[0]
        y = (self.virtual_size[1] - p[1]) * self.disp_zoom + self.screen_offset[1]
        return int(x), int(y)

    def normal_point(self, p, rect):
        """Modify point so that it's positioned the right place"""
        x = (p[0] * self.disp_zoom) - rect[0] / 2 + self.screen_offset[0]
        y = self.real_size[1] - p[1] * self.disp_zoom - rect[1] + self.screen_offset[1]
        return int(x), int(y)

    def real_point(self, x, y):
        """Get a point's real value instead of its virtual value"""
        x = self.screen_offset[0] + x * self.disp_zoom
        y = self.screen_offset[1] + y * self.disp_zoom
        return [x, y]

    def true_point(self, p, man_pos, x_real=None, y_real=None):
        """Convert a point's coordinates to something useful"""
        if x_real:
            x = p[0] - man_pos + self.real_size[0] / 2 + \
                self.screen_offset[0]
        else:
            x = (p[0] - man_pos + self.virtual_size[0] / 2) * \
                self.disp_zoom + self.screen_offset[0]
        if y_real:
            y = self.real_size[1] - p[1] + self.screen_offset[1]
        else:
            y = (self.virtual_size[1] - p[1]) * self.disp_zoom \
                + self.screen_offset[1]

        return x, y

    def draw_circle(self, pos, radius, man_pos, color=(255, 255, 255),
        x_real=None, y_real=None):
        radius = int(radius * self.disp_zoom)
        pos = self.true_point(pos, man_pos, x_real, y_real)
        cairogame.draw_circle(color, pos, radius)
        return pos

    def draw_line(self, p1, p2, line_width, color=(255, 255, 255),
                  no_point_conversion=False):
        if not no_point_conversion:
            p1 = self.true_point(p1)
            p2 = self.true_point(p2)
        line_width *= self.disp_zoom
        cairogame.draw_line(color, p1, p2, line_width)
        return p1, p2

    def draw_stickfigure_line(self, p1, p2, body_rect, color=(255, 255, 255)):
        p1 = self.center_point(p1, body_rect)
        p2 = self.center_point(p2, body_rect)
        line_width = 3 * self.disp_zoom
        cairogame.draw_line(color, p1, p2, line_width)

    def draw_stickfigure_circle(self, pos, radius, body_rect, color=(255, 255, 255)):
        pos = self.center_point(pos, body_rect)
        radius = int(radius * self.disp_zoom)
        cairogame.draw_circle(color, pos, radius)
        return pos

    def finish_stickfigure_draw(self):
        cairogame.finish_draw()

    def draw_wall(self, start, end, color=(255, 255, 255)):
        start = self.real_point(start, 0)
        end = self.real_point(end, 0)
        if start[0] == -float('inf'):
            start[0] = -1
        if end[0] == float('inf'):
            end[0] = self.real_size[0] + 1
        end[1] += self.real_size[1]
        size = [end[i] - start[i] for i in range(2)]
        rect = pygame.Rect(start, size)
        pygame.draw.rect(self.screen, color, rect)

    def create_text(self, text, text_height=75, color=(255, 255,
    255)):
        surf = self.std_font.render(text, True, color)
        size = surf.get_size()
        text_height *= self.disp_zoom
        ratio = size[1] / text_height
        size = int(size[0] / ratio), int(text_height)
        surf = pygame.transform.smoothscale(surf, size)
        return surf

    def blit(self, surf, pos):
        self.screen.blit(surf, self.normal_point(pos, surf.get_size()))

    def fill_borders(self, color=(255, 255, 255)):
        for x in self.screen_bars:
            if x is not None:
                x.fill(color)

    def draw(self):
        self.screen.blit(self.bgsurface, (0, 0))
        
        self.current_level.draw()

        if self.screen_bars[0] is not None:
            self.screen.blit(self.screen_bars[0], (0, 0))
            self.screen.blit(self.screen_bars[0],
                             (self.window_size[0] -
                              self.screen_bars[0].get_size()[0], 0))
        if self.screen_bars[1] is not None:
            self.screen.blit(self.screen_bars[1], (0, 0))
            self.screen.blit(self.screen_bars[1],
                             (0, self.window_size[1] -
                              self.screen_bars[1].get_size()[1]))

        pygame.display.flip()
