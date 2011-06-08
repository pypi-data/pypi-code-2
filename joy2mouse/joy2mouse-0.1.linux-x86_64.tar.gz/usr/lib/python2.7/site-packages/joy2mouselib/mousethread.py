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

import threading
import time
#~ import Queue

import mouse

class MouseThread(threading.Thread):
    def __init__(self, pointermode):
        threading.Thread.__init__(self)
        
        self.pointermode = pointermode
        
        self.mouse = mouse.Mouse()
        self.x = 0 
        self.y = 0
        
        #~ self.queue = Queue.Queue()
        self.running = True

    def run(self):
        
        while self.running:
            if self.x != 0 or self.y != 0:
                #~ print self.x, self.y
                self.mouse.move_relative(self.x, self.y)
                if not self.pointermode:
                    self.x, self.y = 0, 0 
            time.sleep(1/500.0)
            #~ else:
                #~ self.queue.get(block=True)
                #~ try:
                    #~ while self.queue.get(block=False):
                        #~ pass
                #~ except Queue.Empty:
                    #~ pass
    
