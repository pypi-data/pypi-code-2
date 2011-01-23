#!/usr/bin/env python
# -*- coding: utf-8 -*-

# DotBox simple-text: A simple text example
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

class DotText(dotbox.DotBox):
    def __init__(self, text=None, *args):
        dotbox.DotBox.__init__(self, *args)
        self.text = text or '0123456789\nABCDEFGHIJKLMNOPQRSTUVWXYZ\n?!.,_-:;"\''
        self.h = random.randint(-1, 1)
        self.v = random.randint(-1, 1)

    def begin(self):
        self.draw_text(self.text, (None, None))

    def think(self):
        if dotbox.K_ESCAPE == self.inputs.down_key:
            raise dotbox.ExitRequest
        self.hshift(self.h)
        self.vshift(self.v)
        if random.randint(1, 5) == 1:
            self.h = random.randint(-1, 1)
        if random.randint(1, 5) == 1:
            self.v = random.randint(-1, 1)

if __name__ == '__main__':
    parser = dotbox.CommandLineParser(
        prog='dotbox-simple-text',
        usage='Usage: %prog [OPTION]... [TEXT]',
        description='a simple DotBox text example',
        epilog="Prints 0-9, A-Z, '?', '!', '.', ',', '_', '-', ':', ';', '\"', \"'\" and ' ' by default",
        version='''\
DotBox simple-text 0.1.0
Copyright (C) 2011  Niels Serup
License GPLv3+: GNU GPL version 3 or later <http://gnu.org/licenses/gpl.html>
This is free software: you are free to change and redistribute it.
There is NO WARRANTY, to the extent permitted by law.\
''',
        board_size_default=(144, 21),
        block_size_default=(4, 5),
        fps_default=30,
        mute=True,
        debug_print_default=True)

    options, args = parser.parse_args()

    dot_text = DotText(' '.join(args) or None,
                       options.board_size, options.block_size, options.fullscreen,
                       options.zoomed_fullscreen, options.screen_size,
                       options.fps, 0, 255, options.double_buffering,
                       options.hardware_acceleration, 'DotText',
                       options.mute, options.debug_print)
    dot_text.start()
