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

import configobj
import os

class Configuration(object):
    def __init__(self):

        ## stores the config file URI
        self.home_config = os.path.join(os.path.expanduser("~"), ".joy2mouse")
        
        
        if not os.path.exists(self.home_config):
            with open(self.home_config, "w") as fh:
                fh.write(DEFAULT)    

        self.config = configobj.ConfigObj(self.home_config)

DEFAULT = """# Default joystick device to read from
device = /dev/input/js0
# In order to speed up or slow down the mouse movements, change this field
# the higher the value, the slower the pointer!
divisor = 20000

[Example]
axis = 0 1
0 = mouse 1
1 = mouse 2
4 = mouse 4
5 = mouse 5

[Minecraft]
# Profile's device will overwrite the default device
device = /dev/input/js0
# Profile's divisor will overwrite the default divisor
divisor = 15000
axis = 0 1 4 5 
0 = mouse 1
1 = mouse 2
2 = w
3 = space
4 = mouse 4
5 = mouse 5
"""

config = Configuration()
