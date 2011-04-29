# coding:utf-8

# pyInputStats - An application for mouse and keyboard statistics
# Copyright (C) 2011  Daniel Nögel
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3 of the License.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

# example taken from here: https://gist.github.com/402801

import sys
import math
import time
import threading

from Xlib import X, XK, display
from Xlib.ext import record
from Xlib.protocol import rq

from collections import defaultdict

import helpers

DPI = helpers.get_dpi()
print "Assuming DPI being {0}".format(DPI)
DPC = DPI/2.54

class DataCollector(object):
    def __init__(self):
        self.last_coords = None

        self.total_distance = 0
        self.total_keys = 0
        self.total_buttons = 0
        self.keys_pressed = defaultdict(int)
        
        t = threading.Thread(target=self.start_recording)
        t.start()
      
    def get_data(self):
        if self.total_distance == 0 and self.total_keys == 0 and self.total_buttons == 0:
            return None
        d = {"distance":self.total_distance, "keys":self.total_keys, "buttons":self.total_buttons, "keys_pressed":self.keys_pressed, "time":time.time()}
        self.total_distance = 0
        self.total_keys = 0
        self.total_buttons = 0
        self.keys_pressed = defaultdict(int)
        return d
      
    def start_recording(self):
        self.local_dpy = display.Display()
        self.record_dpy = display.Display()
        
        r = self.record_dpy.record_get_version(0, 0)
        self.ctx = self.record_dpy.record_create_context(
                0,
                [record.AllClients],
                [{
                        'core_requests': (0, 0),
                        'core_replies': (0, 0),
                        'ext_requests': (0, 0, 0, 0),
                        'ext_replies': (0, 0, 0, 0),
                        'delivered_events': (0, 0),
                        'device_events': (X.KeyRelease, X.MotionNotify),
                        'errors': (0, 0),
                        'client_started': False,
                        'client_died': False,
                }])
        self.record_dpy.record_enable_context(self.ctx, self.record_callback)
        
        self.record_dpy.record_free_context(self.ctx)
        
    def quit(self):
        self.local_dpy.record_disable_context(self.ctx)
        self.local_dpy.flush()

    def record_callback(self, reply):
        #~ print reply
        if reply["category"] in [4,5] :return
        
        event, data = rq.EventField(None).parse_binary_value(reply.data, self.record_dpy.display, None, None)
        #~ event = ord(data[0])
        
        if event.type == X.KeyRelease:
            #~ print event.detail
           
            #~ print event.state
            #~ print event.detail
            #~ keysym = self.local_dpy.keycode_to_keysym(event.detail, 0)
            self.keys_pressed[(event.detail, event.state)] += 1
            #~ print self.keys_pressed.items()
            #~ print keysym, 676
            #~ import gtk
            #~ print gtk.gdk.keyval_name(keysym)
            #~ print keysym
            self.total_keys += 1
        elif event.type == X.MotionNotify:
            #~ x = ord(data[20]) + (ord(data[21])*255)
            #~ y = ord(data[22]) + (ord(data[23])*255)
            x = event.root_x
            y = event.root_y
            if self.last_coords:
                xdiff = self.last_coords[0] - x
                ydiff = self.last_coords[1] - y
                
                diff = math.sqrt(xdiff**2 + ydiff**2)
                self.total_distance += diff
                self.last_coords = (x, y)
            else:
                self.last_coords = (x, y)
            #~ raw_input()
        elif event.type == X.ButtonRelease:
            self.total_buttons += 1

if __name__ == "__main__":
    app = DataCollector()
