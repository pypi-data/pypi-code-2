#!/usr/bin/env python
# -*- coding: utf-8 -*-

# DotBox Snake: A simple snake implementation using DotBox
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

# The background music is by Ashley Mayhem and is released under the
# Creative Commons Attribution 3.0 license. See
# <http://www.jamendo.com/en/album/61299> and
# <http://creativecommons.org/licenses/by/3.0/> for details. Ashley
# Mayhem has nothing to with DotBox Snake.

## Maintainer: Niels Serup <ns@metanohi.org>

import sys
import os
try: import dotbox # The next line allows for the import of dotbox even when Snake is not installed
except ImportError: sys.path.insert(0, os.path.split(os.path.dirname(os.path.realpath(__file__)))[0]); import dotbox
import random

DIRS = UP, RIGHT, DOWN, LEFT = \
    dotbox.K_UP, dotbox.K_RIGHT, dotbox.K_DOWN, dotbox.K_LEFT
STATES = WAITING, PLAYING = range(2)
CONTRASTS = tuple(map(set, ((UP, DOWN), (RIGHT, LEFT))))

class Snake(dotbox.DotBox):
    def __init__(self, start_length=5, *args):
        dotbox.DotBox.__init__(self, *args)
        self.start_length = start_length
        self.lower_box_color = 22
        self.points_color = 44
        self.points_value_color = 204
        self.state = WAITING

    def begin(self):
        self.play_music(os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                     'dotbox-snake-background-music.ogg'))
        self.new_game()

    def new_game(self):
        self.clear_screen()
        self.new_dir(random.choice(DIRS))
        self.snacks = []
        self.blocks = []
        self.wall = []
        self.points = 0
        self.paused = False
        self.digesting_snacks = 0
        self.digest_snacks(self.start_length, False)
        if self.state == WAITING:
            self.snake_board_size = self.board_size[:]
            snake_text = self.draw_text('SNAKE', (None, None))
            self.wall.extend(snake_text)
            self.pos = self.get_random_point(
                only_free=True, exclude_as_box=snake_text)
        elif self.state == PLAYING:
            self.snake_board_size = (self.board_size[0], self.board_size[1] - 9)
            self.draw_box((0, -9), (-1, -1), self.lower_box_color)
            w, h = self.get_text_size('Points:')
            self.points_pos = (w + 5, -2)
            self.draw_text('Points:', (2, -2), self.points_color)
            self.draw_text('0', self.points_pos, self.points_value_color)
            self.pos = self.get_random_point(only_free=True)
            self.add_snacks()

    def think(self):
        if dotbox.K_p == self.inputs.down_key:
            self.paused = not self.paused
        if self.paused:
            return
        if self.state == WAITING and self.inputs.down_key \
                in (dotbox.K_RETURN, dotbox.K_KP_ENTER):
            self.state = PLAYING
            self.new_game()
        if dotbox.K_ESCAPE == self.inputs.down_key:
            if self.state == WAITING:
                raise dotbox.ExitRequest
            elif self.state == PLAYING:
                self.game_over()
                return

        if self.state == PLAYING:
            for d in self.acceptable_dirs:
                if d == self.inputs.down_key:
                    self.new_dir(d)
                    break
        elif self.state == WAITING:
            if random.randint(1, 10) == 1:
                self.new_dir(random.choice(self.acceptable_dirs))
        if self.dir == UP:
            npos = (self.pos[0], (self.pos[1] - 1) % self.snake_board_size[1])
        elif self.dir == RIGHT:
            npos = ((self.pos[0] + 1) % self.snake_board_size[0], self.pos[1])
        elif self.dir == DOWN:
            npos = (self.pos[0], (self.pos[1] + 1) % self.snake_board_size[1])            
        elif self.dir == LEFT:
            npos = ((self.pos[0] - 1) % self.snake_board_size[0], self.pos[1])
        if npos in self.snacks:
            self.snacks.remove(npos)
            self.digest_snacks()
            self.add_snacks()

        if self.digesting_snacks > 0:
            self.digesting_snacks -= 1
        else:
            self.unmark(self.blocks.pop(0))

        if npos in self.blocks or npos in self.wall:
            self.game_over()
            return

        self.blocks.append(npos)
        self.mark(npos, random.randint(64, 152))

        self.pos = npos

    def new_dir(self, d):
        self.dir = d
        for x in CONTRASTS:
            if d not in x:
                self.acceptable_dirs = tuple(x)

    def add_snacks(self, num=1):
        for i in range(num):
            pos = self.get_random_point(only_free=True)
            self.snacks.append(pos)
            self.mark(pos)

    def digest_snacks(self, num=1, count=True):
        self.digesting_snacks += num
        if count:
            self.points += num
            self.draw_box((self.points_pos[0], -9), (-1, -1), self.lower_box_color)
            self.draw_text(str(self.points), self.points_pos, self.points_value_color)
            if self.state == PLAYING:
                sys.stdout.write('Yum!\n')

    def game_over(self):
        if self.state == PLAYING:
            sys.stdout.write('You got %d snacks!\n' % self.points)
            self.state = WAITING
        self.new_game()

if __name__ == '__main__':
    parser = dotbox.CommandLineParser(
        prog='dotbox-snake',
        usage='Usage: %prog [OPTION]...',
        description='a simple DotBox snake game',
        version='''\
DotBox Snake 0.1.0
Copyright (C) 2011  Niels Serup
License GPLv3+: GNU GPL version 3 or later <http://gnu.org/licenses/gpl.html>
This is free software: you are free to change and redistribute it.
There is NO WARRANTY, to the extent permitted by law.\
''',
        epilog='''\
Press enter to begin a new game, press Escape to exit a running game
or the program, and press P to pause and unpause the game. Use the
arrow keys to control the snake's movements.
''',
        board_size_default=(64, 48),
        block_size_default=(10, 10),
        fps_default=30)

    parser.add_option('-l', '--start-length', dest='start_length', type='int',
                            metavar='INTEGER', default=5, help='''\
Set the snake's start length (defaults to 5)
''')

    options, args = parser.parse_args()

    snake = Snake(options.start_length,
                  options.board_size, options.block_size, options.fullscreen,
                  options.zoomed_fullscreen, options.screen_size,
                  options.fps, 0, 255, options.double_buffering,
                  options.hardware_acceleration,
                  'DotBox Snake', options.mute,
                  options.debug_print)
    snake.start()
