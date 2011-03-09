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

class FolderException(Exception):
    desc = "The given folder is not a valid HVSC folder"
    name = "Folder Error"
class FileException(Exception):
    desc = "File not found"
    name = "File Error"


class PlaybackException(Exception):
    desc = "An unknown error occured during playback"
    name = "Playback Error"
class DeviceBusyException(Exception):
    desc = "Could not playback sound: The sound device seems to be busy\nIts recommended to install the package 'alsa-oss'."
    name = "Device Error"
