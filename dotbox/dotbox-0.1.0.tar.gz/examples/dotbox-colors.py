#!/usr/bin/env python
# -*- coding: utf-8 -*-

# DotBox colors: only 256 of them
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

import sys
import random
try: import dotbox # The next line allows for the import of dotbox even when Snake is not installed
except ImportError: import os; sys.path.insert(0, os.path.split(os.path.dirname(os.path.realpath(__file__)))[0]); import dotbox

class DotColors(dotbox.DotBox):
    def begin(self):
        i = 0
        for y in range(self.board_size[1]):
            for x in range(self.board_size[0]):
                self.mark((x, y), i)
                i += 1

    def think(self):
        if dotbox.K_ESCAPE == self.inputs.down_key:
            raise dotbox.ExitRequest
        if dotbox.K_LEFT in self.inputs.pressed_keys:
            self.hshift(-1)
        elif dotbox.K_RIGHT in self.inputs.pressed_keys:
            self.hshift(1)
        if dotbox.K_UP in self.inputs.pressed_keys:
            self.vshift(-1)
        elif dotbox.K_DOWN in self.inputs.pressed_keys:
            self.vshift(1)

if __name__ == '__main__':
    parser = dotbox.CommandLineParser(
        prog='dotbox-colors',
        usage='Usage: %prog [OPTION]...',
        description='shows the usable palette of colors',
        epilog='''\
The color value increases from the left top to the right bottom
horizontally. Use the arrow keys to move the color blocks.
''',
        version='''\
DotBox colors 0.1.0
Copyright (C) 2011  Niels Serup
License GPLv3+: GNU GPL version 3 or later <http://gnu.org/licenses/gpl.html>
This is free software: you are free to change and redistribute it.
There is NO WARRANTY, to the extent permitted by law.\
''',
        board_size=(16, 16),
        mute=True,
        block_size_default=(10, 10),
        fps_default=20)

    options, args = parser.parse_args()

    dot_colors = DotColors(
        options.board_size, options.block_size, options.fullscreen,
        options.zoomed_fullscreen, options.screen_size,
        options.fps, 0, 255, options.double_buffering,
        options.hardware_acceleration, 'DotText',
        options.mute, options.debug_print)
    dot_colors.start()
