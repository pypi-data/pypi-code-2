#!/usr/bin/env python
# -*- coding: utf-8 -*-

# DotBox: A mini library for block-based games
# Copyright (C) 2011  Niels Serup

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

## Maintainer: Niels Serup <ns@metanohi.org>


# Keep in mind that this code is designed to work with both Python
# 2.6+ and Python 3.x.

# Note: The part of this code where drawing occurs could use some
# optimization. With too many blocks, all that looping takes too long.

import sys
import atexit
import operator
import itertools
import array
import random
import optparse
try: # Python 3
    from functools import reduce
except ImportError:
    pass
import pygame
from pygame.locals import *

# The original data and the Python code generator is in the 'extra/' directory.
_font_data = {'!':(1,((1,),(1,),(1,),(0,),(1,))),' ':(3,((0,0,0),(0,0,0),(0,0,0),(0,0,0),(0,0,0))),'"':(2,((1,1),(0,),(0,),(0,),(0,))),"'":(1,((1,),(0,),(0,),(0,),(0,))),'-':(3,((0,),(0,),(1,1,1),(0,),(0,))),',':(2,((0,),(0,),(0,),(1,1),(0,1))),'.':(2,((0,),(0,),(0,),(1,1),(1,1))),'1':(4,((0,1,1),(1,0,1),(0,0,1),(0,0,1),(0,1,1,1))),'0':(4,((0,1,1),(1,0,0,1),(1,0,0,1),(1,0,0,1),(0,1,1))),'3':(3,((1,1),(0,0,1),(1,1),(0,0,1),(1,1))),'2':(4,((0,1,1),(1,0,0,1),(0,0,1),(0,1),(1,1,1,1))),'5':(3,((1,1,1),(1,),(1,1),(0,0,1),(1,1))),'4':(3,((1,),(1,0,1),(1,1,1),(0,0,1),(0,0,1))),'7':(4,((1,1,1,1),(0,0,0,1),(0,0,1),(0,1),(0,1))),'6':(4,((0,1,1,1),(1,),(1,1,1),(1,0,0,1),(0,1,1))),'9':(4,((0,1,1),(1,0,0,1),(0,1,1,1),(0,0,0,1),(0,0,0,1))),'8':(4,((0,1,1),(1,0,0,1),(0,1,1),(1,0,0,1),(0,1,1))),';':(2,((1,1),(1,1),(0,),(1,1),(0,1))),':':(2,((1,1),(1,1),(0,),(1,1),(1,1))),'?':(4,((0,1,1),(1,0,0,1),(0,0,1),(0,0,0,0),(0,1))),'A':(4,((0,1,1),(1,0,0,1),(1,1,1,1),(1,0,0,1),(1,0,0,1))),'C':(4,((0,1,1,1),(1,),(1,),(1,),(0,1,1,1))),'B':(4,((1,1,1),(1,0,0,1),(1,1,1),(1,0,0,1),(1,1,1))),'E':(4,((1,1,1,1),(1,),(1,1,1),(1,),(1,1,1,1))),'D':(4,((1,1),(1,0,1),(1,0,0,1),(1,0,0,1),(1,1,1))),'G':(4,((0,1,1,1),(1,0,0),(1,0,1,1),(1,0,0,1),(0,1,1))),'F':(4,((1,1,1,1),(1,),(1,1,1),(1,),(1,))),'I':(3,((1,1,1),(0,1),(0,1),(0,1),(1,1,1))),'H':(4,((1,0,0,1),(1,0,0,1),(1,1,1,1),(1,0,0,1),(1,0,0,1))),'K':(4,((1,0,0,1),(1,0,1),(1,1),(1,0,1),(1,0,0,1))),'J':(4,((1,1,1,1),(0,0,0,1),(0,0,0,1),(1,0,0,1),(0,1,1))),'M':(5,((1,0,0,0,1),(1,1,0,1,1),(1,0,1,0,1),(1,0,0,0,1),(1,0,0,0,1))),'L':(4,((1,),(1,),(1,),(1,),(1,1,1,1))),'O':(5,((0,1,1,1),(1,0,0,0,1),(1,0,0,0,1),(1,0,0,0,1),(0,1,1,1))),'N':(5,((1,0,0,0,1),(1,1,0,0,1),(1,0,1,0,1),(1,0,0,1,1),(1,0,0,0,1))),'Q':(5,((0,1,1,1),(1,0,0,0,1),(1,0,0,0,1),(1,0,0,1),(0,1,1,0,1))),'P':(4,((1,1,1),(1,0,0,1),(1,1,1,1),(1,),(1,))),'S':(4,((0,1,1,1),(1,),(0,1,1),(0,0,0,1),(1,1,1))),'R':(4,((1,1,1),(1,0,0,1),(1,1,1,1),(1,0,1),(1,0,0,1))),'U':(4,((1,0,0,1),(1,0,0,1),(1,0,0,1),(1,0,0,1),(0,1,1))),'T':(5,((1,1,1,1,1),(0,0,1),(0,0,1),(0,0,1),(0,0,1))),'W':(7,((1,0,1,0,1,0,1),(1,0,1,0,1,0,1),(0,1,0,1,0,1),(0,1,0,1,0,1),(0,0,1,0,1))),'V':(5,((1,0,0,0,1),(1,0,0,0,1),(0,1,0,1),(0,1,0,1),(0,0,1))),'Y':(5,((1,0,0,0,1),(0,1,0,1),(0,0,1),(0,0,1),(0,0,1))),'X':(5,((1,0,0,0,1),(0,1,0,1),(0,0,1),(0,1,0,1),(1,0,0,0,1))),'Z':(5,((1,1,1,1,1),(0,0,0,1),(0,0,1),(0,1),(1,1,1,1,1))),'_':(3,((0,),(0,),(0,),(0,),(1,1,1)))}

class ExitRequest(Exception):
    pass

class DotBoxInputs(object):
    def __init__(self):
        self.down = None
        self.down_key = None
        self.down_unicode = ''
        self.up = None
        self.up_key = None
        self.pressed_keys = []
        self.mods = 0

    def update(self):
        self.mods = pygame.key.get_mods()

    def press(self, event):
        self.down = event
        self.down_key = event.key
        self.down_unicode = event.unicode.lower()
        self.pressed_keys.append(self.down_key)
        self.update()
        
    def release(self, event):
        self.up = event
        self.up_key = event.key
        try:
            self.pressed_keys.remove(self.up_key)
        except ValueError:
            pass
        self.update()

    def reset_keys(self):
        self.down = None
        self.down_key = None
        self.down_unicode = ''
        self.up = None
        self.up_key = None

class DotBox(object):
    def __init__(self, board_size, block_size=None, fullscreen=False, 
                 zoomed_fullscreen=False, screen_size=None,
                 fps=30, background=255, foreground=0, double_buffering=True,
                 hardware_acceleration=True, caption='DotBox program', mute=False,
                 debug_print=False):
        try:
            self.board_size = self.check_size_tuple(board_size)
        except Exception:
            raise Exception('no board size given!')
        try:
            self.block_size = self.check_size_tuple(block_size)
        except Exception:
            raise Exception('no block size given!')
        self.zoomed_fullscreen = zoomed_fullscreen
        self.fullscreen = not zoomed_fullscreen and fullscreen
        self.screen_size = screen_size
        try:
            if len(set(self.screen_size)) == 1 and self.screen_size[0] is None:
                self.screen_size = None
        except TypeError:
            pass
        self.fps = fps
        self.background = background
        self.foreground = foreground
        self.double_buffering = double_buffering
        self.hardware_acceleration = hardware_acceleration
        self.caption = caption
        self.mute = mute
        self.debug_print = debug_print
        self.box = self.create_blocks()
        self.box_len = len(self.box)
        self.prev_box = self.create_blocks()
        self.point_table = [self.get_pos_point(i) for i in range(self.box_len)]
        self.inputs = DotBoxInputs()
        self.init()

    def check_size_tuple(self, obj):
        if obj is None:
            raise Exception
        try:
            obj = list(obj)
            if obj[0] is None:
                obj[0] = obj[1]
            else:
                try:
                    if obj[1] is None:
                        obj[1] = obj[0]
                except IndexError:
                    obj.append(obj[0])
            if obj[0] == obj[1] == None:
                raise Exception
            return tuple(obj)
        except TypeError:
            return (obj, obj)                

    def create_blocks(self):
        return array.array('B', (self.background,) * reduce(operator.mul, self.board_size))
        
    def init(self):
        pass

    def begin(self):
        pass

    def think(self):
        pass

    def start(self):
        pygame.display.init()
        atexit.register(pygame.quit)
        if not self.mute:
            pygame.mixer.pre_init(44100) # Sound files must be resampled
            pygame.mixer.init()          # to 44.1 kHz

        self.create_palette()
        self.create_screen()

        pygame.display.set_caption(self.caption)
        pygame.mouse.set_visible(False)

        self.clock = pygame.time.Clock()
        self.begin()
        try:
            self.run_loop()
        except ExitRequest:
            pass

    def run_loop(self):
        while True:
            self.inputs.reset_keys()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    raise ExitRequest
                elif event.type in (pygame.KEYDOWN, pygame.KEYUP):
                    if event.type == pygame.KEYDOWN:
                        self.inputs.press(event)
                    elif event.type == pygame.KEYUP:
                        self.inputs.release(event)
                        
            self.think()
            self.draw()
            if self.debug_print:
                sys.stdout.write('FPS: %f\n' % self.clock.get_fps())
            self.clock.tick(self.fps)

    def get_point_pos(self, x, y):
        return int((y % self.board_size[1]) * self.board_size[0] + x % self.board_size[0])

    def get_pos_point(self, pos):
        return pos % self.board_size[0], int(pos / self.board_size[0])

    def create_palette(self):
        self.palette = list(itertools.product(range(0, 256, 51), repeat=3))
        self.palette.extend(tuple((i / 10,) * 3 for i in range(60, 2560, 64)))
        self.palette = tuple(self.palette)

    def get_rgb(self, num):
        return self.palette[num]

    def clear_screen(self):
        for i in range(self.box_len):
            self.box[i] = self.background

    def hshift(self, d=1):
        if d < 0:
            rng = range(-d)
            for i in range(0, self.box_len, self.board_size[0]):
                for x in rng:
                    self.box.insert(i + self.board_size[0] - 1, self.box.pop(i))
        else:
            rng = range(d)
            for i in range(0, self.box_len, self.board_size[0]):
                for x in rng:
                    self.box.insert(i, self.box.pop(i + self.board_size[0] - 1))

    def vshift(self, d=1):
        if d < 0:
            for i in range(-d * self.board_size[0]):
                self.box.insert(self.box_len - 1, self.box.pop(0))
        else:
            for i in range(d * self.board_size[0]):
                self.box.insert(0, self.box.pop())
                    
    def blit_surface(self, x, y):
        self.screen.blit(self.block_surface, (
                self.screen_offset[0] + self.block_size[0] * x,
                self.screen_offset[1] + self.block_size[1] * y))
                
    def draw(self):
        for x in range(self.board_size[0]):
            for y in range(self.board_size[1]):
                pos = self.get_point_pos(x, y)
                if self.box[pos] != self.prev_box[pos]:
                    self.prev_box[pos] = self.box[pos]
                    self.block_surface.fill(self.get_rgb(self.box[pos]))
                    self.blit_surface(x, y)
        pygame.display.flip()

    def play_music(self, path, times=-1):
        if not self.mute:
            pygame.mixer.music.load(path)
            pygame.mixer.music.play(times)

    def load_sound(self, path):
        if not self.mute:
            return pygame.mixer.Sound(path)

    def mark(self, pos, color=None):
        if color is None:
            color = self.foreground
        self.box[self.get_point_pos(*pos)] = color

    def unmark(self, pos):
        self.mark(pos, self.background)

    def get_font_data(self, char):
        if char not in _font_data:
            char = char.upper()
            if char not in _font_data:
                char = char.lower()
                if char not in _font_data:
                    char = ' '
        return _font_data[char]

    def get_text_size(self, text):
        width = 0
        height = -1
        for line in text.split('\n'):
            w = tuple(self.get_font_data(x)[0] for x in line)
            w = sum(w) + len(w) - 1
            if w > width:
                width = w
            height += 6
        return width, height

    def draw_box(self, lt, rb, color=None):
        if color is None:
            color = self.background
        for x in range(lt[0] % self.board_size[0],
                       rb[0] % self.board_size[0] + 1):
            for y in range(lt[1] % self.board_size[1],
                           rb[1] % self.board_size[1] + 1):
                self.mark((x, y), color)

    def draw_text(self, text, pos, color=None):
        if color is None:
            color = self.foreground
        pos = list(pos[:])
        if None in pos or pos[0] < 0 or pos[1] < 0:
            size = self.get_text_size(text)
            if pos[0] is None:
                pos[0] = int((self.board_size[0] - size[0]) / 2)
            elif pos[0] < 0:
                pos[0] -= size[0]
            if pos[1] is None:
                pos[1] = int((self.board_size[1] - size[1]) / 2)
            elif pos[1] < 0:
                pos[1] -= size[1]
        orig_pos = pos[:]
        ps = []
        for line in text.split('\n'):
            for char in line:
                width, data = self.get_font_data(char)
                y = pos[1]
                for line in data:
                    x = pos[0]
                    for point in line:
                        if point:
                            p = (x, y)
                            ps.append(p)
                            self.mark(p, color)
                        x += 1
                    y += 1
                pos[0] += width + 1
            pos[0] = orig_pos[0]
            pos[1] += 6
        return ps

    def get_random_point(self, only_free=False,
                         exclude=None, exclude_as_box=None):
        if only_free:
            indexes = []
            i = 0
            for x in self.box:
                if x == self.background:
                    indexes.append(i)
                i += 1
            if exclude is None and exclude_as_box is None:
                return self.get_pos_point(random.choice(indexes))
            else:
                temp_oks = [self.get_pos_point(x) for x in indexes]
        elif exclude is not None or exclude_as_box is not None:
            temp_oks = []
        if exclude is not None or exclude_as_box is not None:
            temp_oks.extend(self.point_table)
            if exclude is not None:
                for x in exclude:
                    temp_oks.remove(x)
            if exclude_as_box is not None:
                lt = min(exclude_as_box)
                rb = max(exclude_as_box)
                for x in range(lt[0], rb[0]):
                    for y in range(lt[1], rb[1]):
                        temp_oks.remove((x, y))
            return random.choice(temp_oks)
        # Else:
        return random.choice(self.point_table)
    
    def create_screen(self):
        if self.zoomed_fullscreen:
            try:
                info = pygame.display.Info()
                self.screen_size = (info.current_w, info.current_h)
                if self.screen_size[0] == -1: # in this case, [1] will also be -1
                    raise Exception('your SDL is too old for width and height detection')
            except Exception:
                raise Exception('your PyGame is too old for width and height detection')
        elif self.fullscreen:
            self.screen_size = (640, 480)

        if self.block_size is not None:
            self.virtual_size = tuple(self.block_size[i] * self.board_size[i]
                                      for i in range(2))
            if self.screen_size is None:
                self.screen_size = self.virtual_size
                self.screen_offset = (0, 0)
            else:
                get_ratio = lambda i: self.screen_size[i] / float(
                    self.board_size[i]) / self.block_size[i]
                if self.screen_size[0] is None:
                    ratio = get_ratio(1)
                elif self.screen_size[1] is None:
                    ratio = get_ratio(0)
                else:
                    ratio = min(tuple(get_ratio(i) for i in range(2)))
                self.block_size = tuple(int(ratio * x) for x in self.block_size)
                if self.screen_size[0] is None:
                    self.screen_size = (self.block_size[0] * self.board_size[0], self.screen_size[1])
                elif self.screen_size[1] is None:
                    self.screen_size = (self.screen_size[0], self.block_size[1] * self.board_size[1])
                self.screen_offset = tuple(int((self.screen_size[i] - self.block_size[i]
                                                * self.board_size[i]) / 2) for i in range(2))

        flags = 0
        if self.zoomed_fullscreen:
            flags = pygame.NOFRAME
        elif self.fullscreen:
            flags = pygame.FULLSCREEN
            if self.hardware_acceleration:
                flags |= pygame.HWSURFACE
        if self.double_buffering:
            if flags != 0:
                flags = flags | pygame.DOUBLEBUF
            else:
                flags = pygame.DOUBLEBUF

        # Create the screen
        self.screen = pygame.display.set_mode(
            self.screen_size, flags, 8)
        self.screen.set_palette(self.palette)

        # Create the background surface
        self.background_surface = pygame.Surface(self.screen_size, 0, 8)
        self.background_surface.set_palette(self.palette)
        self.background_surface.fill(self.get_rgb(self.background))
        self.screen.blit(self.background_surface, (0, 0))
        pygame.display.flip()

        self.block_surface = pygame.Surface(self.block_size, 0, 8)
        self.block_surface.set_palette(self.palette)
        # self.block_surfaces = []
        # for i in range(self.board_size[0]):
        #     column = []
        #     for j in range(self.board_size[1]):
        #         surf = pygame.Surface(self.block_size, 0, 8)
        #         surf.set_palette(self.palette)
        #         column.append(surf)
        #     self.block_surfaces.append(tuple(column))
        # self.block_surfaces = tuple(self.block_surfaces)

class CommandLineParser(optparse.OptionParser):
    def __init__(self, **kwds):
        self.board_size_default = kwds.get('board_size_default')
        self.block_size_default = kwds.get('block_size_default')
        self.screen_size_default = kwds.get('screen_size_default')
        self.fps_default = kwds.get('fps_default')
        self.zoomed_fullscreen_default = kwds.get('zoomed_fullscreen_default') or False
        self.fullscreen_default = kwds.get('fullscreen_default') or False
        self.mute_default = kwds.get('mute_default') or False
        self.debug_print_default = kwds.get('debug_print_default') or False
        self.double_buffering_default = kwds.get('double_buffering_default') or True
        self.hardware_acceleration_default = kwds.get('hardware_acceleration_default') or True
        self.board_size = kwds.get('board_size')
        self.block_size = kwds.get('block_size')
        self.screen_size = kwds.get('screen_size')
        self.fps = kwds.get('fps')
        self.zoomed_fullscreen = kwds.get('zoomed_fullscreen')
        self.fullscreen = kwds.get('fullscreen')
        self.mute = kwds.get('mute')
        self.debug_print = kwds.get('debug_print')
        self.double_buffering = kwds.get('double_buffering')
        self.hardware_acceleration = kwds.get('hardware_acceleration')
        self._del_kwds(kwds, 'board_size_default', 'block_size_default',
                      'screen_size_default', 'fps_default',
                      'zoomed_fullscreen_default', 'fullscreen_default',
                      'mute_default', 'debug_print_default',
                      'double_buffering_default', 'hardware_acceleration_default',
                      'board_size', 'block_size',
                      'screen_size', 'fps', 'zoomed_fullscreen',
                      'fullscreen', 'mute', 'debug_print', 'double_buffering',
                      'hardware_acceleration')
        optparse.OptionParser.__init__(self, **kwds)

        if self.board_size is None:
            h = 'set the number of blocks in use'
            if self.board_size_default is not None:
                h += ' (defaults to %dx%d)' % tuple(self.board_size_default)
            self.add_option('-s', '--board-size', dest='board_size',
                            metavar='[COLUMNS]x[ROWS]|SIZE',
                            default=self.board_size_default, help=h)

        if self.block_size is None:
            h = 'set the size of a block'
            if self.block_size_default is not None:
                h += ' (defaults to %dx%d)' % tuple(self.block_size_default)
            self.add_option('-b', '--block-size', dest='block_size',
                            metavar='[WIDTH]x[HEIGHT]|SIZE',
                            default=self.block_size_default, help=h)

        if self.screen_size is None:
            h = '''\
set the size of the screen (defaults to a size that fits the number of
blocks and the blocksize). DotBox will always make sure to keep the
blocks within the limits imposed on it by the screen size without
stretching them out of proportion, which might result in borders
around the centered body of the window
'''
            if self.screen_size_default is not None:
                h += ' (defaults to %dx%d)' % tuple(self.screen_size_default)
            self.add_option('-d', '--screen-size', dest='screen_size',
                            metavar='[WIDTH]x[HEIGHT]|SIZE',
                            default=self.screen_size_default, help=h)

        if self.fps is None:
            h = 'set how many frames should be generated per second'
            if self.fps_default is not None:
                h += ' (defaults to %d)' % self.fps_default
            self.add_option('-p', '--fps', dest='fps', type='int',
                            metavar='INTEGER',
                            default=self.fps_default, help=h)

        if self.zoomed_fullscreen is None:
            h = '''\
Play the game in zoomed fullscreen (recommended as an often prettier
alternative to normal SDL fullscreen)
'''
            if self.zoomed_fullscreen_default:
                lc = '--no-zoomed-fullscreen'
                cl = 'store_false'
            else:
                lc = '--zoomed-fullscreen'
                cl = 'store_true'
            self.add_option('-f', lc, dest='zoomed_fullscreen', action=cl,
                            default=self.zoomed_fullscreen_default, help=h)

        if self.fullscreen is None:
            h = 'Play the game in basic SDL fullscreen (not recommended)'
            if self.fullscreen_default:
                lc = '--no-fullscreen'
                cl = 'store_false'
                h = 'Do not ' + h[0].lower() + h[1:]
            else:
                lc = '--fullscreen'
                cl = 'store_true'
            self.add_option('-F', lc, dest='fullscreen', action=cl,
                            default=self.fullscreen_default, help=h)

        if self.mute is None:
            h = 'Mute the sound'
            if self.mute_default:
                lc = '--no-mute'
                cl = 'store_false'
                h = 'Do not ' + h[0].lower() + h[1:]
            else:
                lc = '--mute'
                cl = 'store_true'
            self.add_option('-m', lc, dest='mute', action=cl,
                            default=self.mute_default, help=h)

        if self.debug_print is None:
            h = 'Print debug text'
            if self.debug_print_default:
                lc = '--no-debug-print'
                cl = 'store_false'
                h = 'Do not ' + h[0].lower() + h[1:]
            else:
                lc = '--debug-print'
                cl = 'store_true'
            self.add_option('-g', lc, dest='debug_print', action=cl,
                            default=self.debug_print_default, help=h)

        if self.double_buffering is None:
            h = 'Use double buffering'
            if self.double_buffering_default:
                lc = '--no-double-buffering'
                cl = 'store_false'
                h = 'Do not ' + h[0].lower() + h[1:]
            else:
                lc = '--double-buffering'
                cl = 'store_true'
            self.add_option('-u', lc, dest='double_buffering', action=cl,
                            default=self.mute_default, help=h)

        if self.hardware_acceleration is None:
            h = 'Use hardware acceleration'
            if self.hardware_acceleration_default:
                lc = '--no-hardware-acceleration'
                cl = 'store_false'
                h = 'Do not ' + h[0].lower() + h[1:]
            else:
                lc = '--hardware-acceleration'
                cl = 'store_true'
            self.add_option('-a', lc, dest='hardware_acceleration', action=cl,
                            default=self.hardware_acceleration_default, help=h)

    def _del_kwds(self, dct, *strs):
        for x in strs:
            try:
                del dct[x]
            except KeyError:
                pass

    def parse_args(self, *args, **kwds):
        self.parsed_options, self.parsed_args = \
            optparse.OptionParser.parse_args(self, *args, **kwds)
        opt_dict = eval(str(self.parsed_options))
        for key in ('board_size', 'block_size', 'screen_size', 'fps',
                    'zoomed_fullscreen', 'fullscreen', 'mute',
                    'double_buffering', 'hardware_acceleration'):
            if not key in opt_dict:
                exec('self.parsed_options.%s = self.%s' % (key, key))

        self._extra_parse()
        return self.parsed_options, self.parsed_args

    def _int_or_none(self, string):
        try:
            return int(string)
        except ValueError:
            return None

    def _AxB_parse(self, obj):
        if obj is None:
            return
        if isinstance(obj, tuple):
            return obj
        else:
            try:
                return tuple(map(self._int_or_none, obj.split('x')))
            except Exception:
                self.error('incorrect syntax: %s' % obj)

    def _extra_parse(self):
        if self.block_size is None:
            self.parsed_options.block_size = self._AxB_parse(self.parsed_options.block_size)
        if self.board_size is None:
            self.parsed_options.board_size = self._AxB_parse(self.parsed_options.board_size)
        if self.screen_size is None:
            self.parsed_options.screen_size = self._AxB_parse(self.parsed_options.screen_size)
            
