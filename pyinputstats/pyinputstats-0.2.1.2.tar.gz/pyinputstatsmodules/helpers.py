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

import sys
import os
from distutils import dir_util
from xdg import BaseDirectory

import gtk

import time
import datetime
import subprocess
import re
from textwrap import dedent

def strip_data(data):
    """Strips off None-Tuples at the beginning and at the end of a given list.
    
    Also trims chunks of None-Tuples in between and replaces them through
    [(0, 0, 0), (-1, -1, -1)*n, (0, 0, 0)].
    """
    
    ## At the beginning
    for i, datum in enumerate(data):
        pix, clicks, keys =  datum
        if pix is None and clicks is None and keys is None:
            data[i] = (-1, -1, -1)
        else:
            break

    ## At the end
    l = len(data)-1
    for i, datum in enumerate(data[::-1]):
        pix, clicks, keys =  datum
        if pix is None and clicks is None and keys is None:
            data[l-i] = (-1, -1, -1)
        else:
            break
    
    ## Find None-Tuple-Chunks in between
    start = None
    length = 0
    chunks = []
    for i, datum in enumerate(data):
        pix, clicks, keys =  datum
        if pix is None and clicks is None and keys is None:
            if start:
                length += 1
            else:
                start = i
                length = 1
        else:
            if start:
                chunks.append((start, i))
                start = None

    ## Trim those chunks
    for s, l in chunks: 
        if l == 1:
            data[s] == (0, 0, 0)
        elif l == 2:
            data[s:l] == [(0, 0, 0), (0, 0, 0)]
        else:
            data[s+1:l] =  [(-1, -1, -1),]*(l-s-1)
            data[s] = (0, 0, 0)
            data[l-1] = (0, 0, 0)
            #~ data[i] = (0, 0, 0)
    return data

def get_data_dir():
    d = os.path.join(BaseDirectory.xdg_data_home, "pyinputstats")
    if not os.path.exists(d):
        dir_util.mkpath(d)
    return d

def get_autostart_entry():
    """Returns path of our autostart entry or None if no such entry exists
    
    In order to avoid problems, the autostart-entry will be removed, if it
    was disabled via GNOME-Startup-Apps-Dialog."""
    
    d = os.path.join(BaseDirectory.xdg_config_home, "autostart")
    if not os.path.exists(d):
        return None
    
    
    for f in os.listdir(d):
        found = False
        disabled = False
        
        p = os.path.join(d, f)
        with open(p, "r") as fh:
            for line in fh:
                if "Exec" in line and "pyinputstats" in line:
                    found = True
                if "gnome-autostart" in line.lower() and "false" in line.lower():
                    disabled = True
    
        if found and not disabled:
            return p
        elif found and disabled:
            os.remove(p)
            return None

def disable_autostart():
    """Deletes the autostart entry"""
    
    path = get_autostart_entry()
    if path:
        os.remove(path)

def enable_autostart():
    """Creates the autostart entry"""
    
    d = os.path.join(BaseDirectory.xdg_config_home, "autostart")
    if not os.path.exists(d):
        dir_util.mkpath(d)
        
    autostart_file = get_autostart_entry()
    if autostart_file: 
        return autostart_file
        
    fname = "pyinputstats-{0}.desktop"
    counter = 1
    while os.path.exists(fname.format(counter)):
        counter += 1
    fname = fname.format(counter)
    entry = """
[Desktop Entry]
Type=Application
Exec=python '{0}'
Hidden=false
NoDisplay=false
X-GNOME-Autostart-enabled=true
Name[de_DE]=pyInputStats
Name=pyInputStats
Comment[de_DE]=
Comment=
""".format(os.path.abspath(sys.argv[0]))
    
    p = os.path.join(d, fname)
    with open(p, "w") as fh:
        fh.write(entry)
        
    return p
    
def month_days(month):
    year, month = month
    timestamp_start = time.mktime(datetime.date(year, month, 1).timetuple())
    if month < 12:
        timestamp_end = time.mktime(datetime.date(year, month+1, 1).timetuple())
    else:
        timestamp_end = time.mktime(datetime.date(year+1, 1, 1).timetuple())
        
    #~ print timestamp_start,     timestamp_end
    return int(round((timestamp_end - timestamp_start) / (60*60*24)))

def translate_keys(keycode, state):
    keyval, group, level, mods = gtk.gdk.Keymap.translate_keyboard_state(gtk.gdk.keymap_get_default(), keycode, state, 0)
    return gtk.gdk.keyval_name(gtk.gdk.keyval_to_lower(keyval))

def get_char(name):
    uc = gtk.gdk.keyval_to_unicode(gtk.gdk.keyval_from_name(str(name)))
    if uc:
        if uc <= 32:
            return name
        elif str(name).startswith("KP_"):
            return name
        else:
            return unichr(uc)
    else:
        return name

def get_dpi(fallback=96):
    p = subprocess.Popen(["xdpyinfo"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    ret = p.stdout.read()
    rg = re.compile(r"resolution: *(?P<x>[0-9]*)x(?P<y>[0-9]*)")
    res = rg.search(ret)
    if res:
        x, y = res.group("x"), res.group("y")
        if x >= y:
            return int(x)
        else:
            return int(y)
    return fallback
