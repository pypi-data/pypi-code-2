#!/usr/bin/env python
# -*- coding: utf-8 -*- #
'''WatchVideo constants'''

###
#
# WatchVideo is the legal property of Leonardo Gastón De Luca
# leo[at]kde.org.ar Copyright (c) 2009 Leonardo Gastón De Luca
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.

# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
###

import os.path
import tempfile
import urllib2

import pkg_resources

from watchvideo.utils import is_command


VERSION = pkg_resources.get_distribution("WatchVideo").version

AGENT = 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.1.1) '\
'Gecko/20090718 IceCat/3.5.3'
OPENER = urllib2.build_opener()
OPENER.addheaders = [('User-agent', AGENT)]

HOME_FOLDER = os.path.join(os.path.expanduser("~"), "")
HISTORY_PATH = HOME_FOLDER + ".watchvideo_history"

#get user's firefox or GNU icecat profile folder
FIREFOX_PATH = HOME_FOLDER + ".mozilla/firefox/"
FIREFOX_SESSION = None
if not os.path.exists(FIREFOX_PATH):
    FIREFOX_PATH = HOME_FOLDER + ".gnuzilla/icecat/"
    if not os.path.exists(FIREFOX_PATH):
        FIREFOX_PATH = None
        
if FIREFOX_PATH:
    #FIREFOX_PATH = HOME_FOLDER + ".gnuzilla/icecat/" #delete
    for entry in os.listdir(FIREFOX_PATH):
        if "default" in entry and os.path.isdir(FIREFOX_PATH + entry):
          FIREFOX_PATH += entry + "/"
          if os.path.exists(FIREFOX_PATH + "sessionstore.js"):
            FIREFOX_SESSION = FIREFOX_PATH + "sessionstore.js"
            break

#Icons
PATH_MEDIA = ":/media/"
ICON_WATCHVIDEO = PATH_MEDIA + "watchvideo-32x32.png"
ICON_QUIT = PATH_MEDIA + "quit.png"
ICON_DOWNLOAD = PATH_MEDIA + "internet-download.png"
ICON_PREFERENCES = PATH_MEDIA + "preferences.png"
ICON_START = PATH_MEDIA + "start.png"
ICON_STOP = PATH_MEDIA + "stop.png"
ICON_OPEN_FOLDER = PATH_MEDIA + "folder-open.png"
ICON_ERROR = PATH_MEDIA + "error.png"
ICON_VALID = PATH_MEDIA + "dialog-ok-apply.png"
ICON_ADD = PATH_MEDIA + "list-add.svg"
ICON_REMOVE = PATH_MEDIA + "list-remove.png"
ICON_COPY = PATH_MEDIA + "edit-copy.png"
ICON_REPEAT = PATH_MEDIA + "refresh.png"
ICON_NO_REPEAT = PATH_MEDIA + "no-repeat.png"
ICON_NORMAL_QUALITY = PATH_MEDIA + "normal-quality.png"
ICON_HIGH_QUALITY = PATH_MEDIA + "high-quality.png"

#FileManagers
FILEMANAGERS=["xdg-open","dolphin","d3lphin","konqueror","gnome-open","nautilus",\
            "thunar","rox"]

TEMP_PATH = tempfile.gettempdir()

HAS_FFMPEG = is_command("ffmpeg")
HAS_FFMPEG2THEORA = is_command("ffmpeg2theora")

