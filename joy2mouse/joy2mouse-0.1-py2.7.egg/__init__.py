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

import joystick
import mouse
import keyboard
import profiles
import mousethread
import sys

import gobject

__NAME__ = "joy2mouse"
__VERSION__ = 0.1
__AUTHOR__ = "Daniel Nögel"

class App(object):
    def __init__(self, options):
        
        self.device = profiles.config.config.get("device", "/dev/input/js0")
        self.divisor = float(profiles.config.config.get("divisor", 20000))
        self.pointermode = profiles.config.config.get("pointermode", "True").lower().strip().startswith("t")
        
        if options.profile:
            self.read_profiles(options.profile)
        else:
            print "No profile selected"
            print "use -p to select one from .joy2mouse"
            print 
            self.default_profile()
        
        self.mouse = mouse.Mouse()
        self.keyboard = keyboard.Keyboard()
        self.joystick = joystick.Joystick(self.device)

        self.mousethread = mousethread.MouseThread(self.pointermode)
        self.mousethread.start()

        if self.watch_axis:
            self.joystick.connect("axis", self.axis_event)
        if self.mappings != {}:
            self.joystick.connect("button", self.button_event)
            
    def default_profile(self):
        self.mappings = {}
        self.watch_axis = [i for i in range(0, 6)]
        for i in range(0, 5):
            self.mappings[i] = ("mouse", i+1)
            
    def read_profiles(self, profile):
        config = profiles.config.config
        
        if not profile in config:
            print "ERROR: Profile '{0}' not found".format(profile)
            sys.exit(1)
        
        self.device = config[profile].get("device", self.device)
        self.divisor = float(config[profile].get("divisor", self.divisor))
        self.pointermode = config[profile].get("pointermode", str(self.pointermode)).lower().strip().startswith("t")

        if "axis" in config[profile]:
            self.watch_axis = [int(i) for i in config[profile]["axis"].strip().split()]
        else:
            self.watch_axis = None
            
        self.mappings = {}
        
        for i in range(0, 100):
            if str(i) in config[profile]:
                if "mouse" in config[profile][str(i)].strip():
                    self.mappings[i] = ("mouse", int(config[profile][str(i)].replace("mouse", "").strip()))
                else:
                    self.mappings[i] = ("key", config[profile][str(i)].strip())
        print self.mappings
        
    def button_event(self, signal, number, value, init):
        if init:
            return 
            
        
        if not number in self.mappings:
            return
        
        mode = self.mappings[number][0]
        
        if mode == "mouse":
            if value == 1:
                self.mouse.press(self.mappings[number][1])
            elif value == 0:
                self.mouse.release(self.mappings[number][1])
        else:
            if value == 1:
                self.keyboard.press_key(self.mappings[number][1])
            elif value == 0:
                self.keyboard.release_key(self.mappings[number][1])
        
        
    def axis_event(self, signal, number, value, init):
        if init: 
            return
        if number not in self.watch_axis:
            return
        #~ self.axis[number] = value
        #~ return
        
        #~ self.mousethread.queue.put(1)
        
        if number % 2 == 0 and value != 0:
            self.mousethread.x = value/self.divisor
        elif number % 2 != 0 and value != 0:
            self.mousethread.y = value/self.divisor
        elif number % 2 == 0 and value == 0:
            self.mousethread.x = 0
        elif number % 2 != 0 and value == 0:
            self.mousethread.y = 0
        #~ print value,  number, "!!!!"
        



