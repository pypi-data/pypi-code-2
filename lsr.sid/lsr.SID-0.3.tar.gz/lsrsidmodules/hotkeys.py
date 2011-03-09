#!/usr/bin/env python
# coding:utf-8

# lsrSID - Python HVSC browser and sidplay2 GUI.
# Copyright (C) 2010  Daniel Nögel
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

# This script was inspired by Chris Brown's gnome-media-keys script for amarok

import gobject
import os, sys
import logging


try:
    import dbus
    from dbus import glib
except Exception, inst:
    logging.error("python-dbus and libdbus-glib needed for hotkey support")
    #~ raise
    
#
# Checks
#

# Check if Gnome Settings Daemon is running:
ret = os.popen("ps -C gnome-settings-daemon|grep settings").read()
if ret == "":
    logging.error("gnome-settings-daemon not running - not hotkey support available")
    #~ raise ImportError("gnome-settings-daemon not running - not hotkey support available")

# Gnome Version for dbus selection
VERSION = os.popen('LANG=C gnome-about --gnome-version|grep Version|cut -d \" \" -f 2').read()
if VERSION == "": VERSION = "2.18"

class Hotkeys(object):
    def __init__(self, main):
        if not "dbus" in sys.modules.keys():
            logging.error("dbus not found")
            return
        
        self.main = main
        
        bus = dbus.SessionBus()
        # Connect to signal:
        if VERSION > "2.20":
            try:
                object = bus.get_object("org.gnome.SettingsDaemon", "/org/gnome/SettingsDaemon/MediaKeys")
                object.connect_to_signal("MediaPlayerKeyPressed", self.ev_key_pressed, dbus_interface='org.gnome.SettingsDaemon.MediaKeys')
            except:
                logging.error("Error connecting to SettingsDaemon - no hotkeys available.")
        else:
            try:
                object = bus.get_object("org.gnome.SettingsDaemon", "/org/gnome/SettingsDaemon")
                object.connect_to_signal("MediaPlayerKeyPressed", self.ev_key_pressed, dbus_interface="org.gnome.SettingsDaemon")
            except:
                logging.error("Error connecting to SettingsDaemon - not hotkeys available.")

    def ev_key_pressed(self, *keys):
        print keys
        for key in keys:
            if key == "Play":
                self.main.gui.tbPlayStop_clicked_cb(None)
            elif key == "Stop":
                self.main.gui.tbPlayStop_clicked_cb(None)
            elif key == "Next":
                self.main.gui.tbNext_clicked_cb(None)
            elif key == "Previous":
                self.main.gui.tbPrev_clicked_cb(None)
