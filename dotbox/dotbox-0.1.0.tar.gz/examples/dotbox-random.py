#!/usr/bin/env python
# -*- coding: utf-8 -*-

# DotBox random: random color blocks
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

class DotRandom(dotbox.DotBox):
    def begin(self):
        for y in range(self.board_size[1]):
            for x in range(self.board_size[0]):
                self.mark((x, y), random.randint(0, 255))

    def think(self):
        if dotbox.K_ESCAPE == self.inputs.down_key:
            raise dotbox.ExitRequest
        for i in range(10):
            self.mark(self.get_random_point(), random.randint(0, 255))

if __name__ == '__main__':
    parser = dotbox.CommandLineParser(
        prog='dotbox-random',
        usage='Usage: %prog [OPTION]...',
        description='generates random color blocks',
        epilog='''\
''',
        version='''\
DotBox random 0.1.0
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

    dot_random = DotRandom(
        options.board_size, options.block_size, options.fullscreen,
        options.zoomed_fullscreen, options.screen_size,
        options.fps, 0, 255, options.double_buffering,
        options.hardware_acceleration, 'DotText',
        options.mute, options.debug_print)
    dot_random.start()
