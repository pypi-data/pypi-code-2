#!/usr/bin/env python2
# coding:utf-8

# ----------------------------------------------------------------------------
# joy2mouse - control your mouse with your joystick/joypad
# Copyright (c) 2011 Daniel Nögel
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3 of the License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
# ----------------------------------------------------------------------------

from Xlib.display import Display
from Xlib import X
from Xlib.ext.xtest import fake_input


class Mouse():
    def __init__(self):
        self.display = Display()

    def press(self, button = 1):
        print button, "press"
        fake_input(self.display, X.ButtonPress, [None, 1, 3, 2, 4, 5][button]) # fix this nonsense
        self.display.sync()

    def release(self, button = 1):
        print button, "release"
        fake_input(self.display, X.ButtonRelease, [None, 1, 3, 2, 4, 5][button])# fix this nonsense
        self.display.sync()
    
    def click(self, button=1):
        print button, "click"
        self.press(button)
        self.release(button)

    def move(self, x, y):
        fake_input(self.display, X.MotionNotify, x=x, y=y)
        #~ self.display.sync()

    def position(self):
        coord = self.display.screen().root.query_pointer()._data
        return coord["root_x"], coord["root_y"]
        
    def move_relative(self, x=0, y=0):
        cur_x, cur_y = self.position()
        self.move(cur_x+x, cur_y+y)

    def screen_size(self):
        width = self.display.screen().width_in_pixels
        height = self.display.screen().height_in_pixels
        return width, height

if __name__ == "__main__":
    m = Mouse()
    m.move_relative(100)
    m.move_relative(100)
