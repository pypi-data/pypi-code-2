# -*- coding: utf-8 -*-
# Copyright (C) 2011 Carlos Pais <freemind@lavabit.com>
# Copyright (C) 2011  Michał Masłowski  <mtjm@mtjm.eu>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


"""
Handling persistent configuration of WatchVideo in UI-independent way.
"""


import os.path
import sys
from watchvideo.qt import QtCore
from watchvideo import main
from watchvideo.utils import is_command
import watchvideo.constants as c
from ConfigParser import SafeConfigParser

try:
    import watchvideo.player
except (ImportError, OSError):
    HAS_PLAYER = False
else:
    assert watchvideo.player
    HAS_PLAYER = True


class Settings(object):

    """All settings in WatchVideo, with file serialization."""

    def __init__(self):
        """Make the configuration from file and defaults."""
        # TODO: maybe instead ignore the content, use defaults when
        # getting value not stored there?
        
        self.settings = self.getSettings()

    # TODO: make an object with dictionary interface for these
    @property
    def global_quality(self):
        """The quality of all plugins, or ``"normal"`` if not one."""
        
        if self.global_video_quality:
            return self.global_video_quality
        else:
            return "custom"
            """options = self.get_quality_options()
            total_items = len(options)
            count = 0
            for option in options:
                count += options[option]
            
            if count == 0:
                return "ask"
            elif count == total_items:
                return "low"
            elif count == total_items * 2:
                return "high"
            else:
                return "user"""

    def get_quality_options(self):
        """Return a dictionary of plugin quality options.

        Keys are plugin class names, values are indices of quality
        preference.
        """
        
        parser = SafeConfigParser()
        parser.read(c.CONFIG_FILE)
        quality_options = {}
        if parser.has_section("VideoQuality"):
            for website in parser.options("VideoQuality"):
                try:
                    quality_options[website] = int(self.quality(website))
                except TypeError:
                    print "Type error with", website
        
        return quality_options

    def quality(self, website):
        """Return quality of specified plugin."""
        return self.settings.value("VideoQuality/" + website)

    def set_quality(self, website, value):
        """Set quality of specified plugin."""
        self.settings.setValue("VideoQuality/" + website, value)

    # TODO: learn what these do, write docstrings

    @property
    def play_downloaded(self):
        return bool(int(self.settings.value("DownloadOptions/double_click_downloads")))

    @play_downloaded.setter
    def play_downloaded(self, value):
        self.settings.setValue("DownloadOptions/double_click_downloads", value)

    @property
    def media_player(self):
        return self.settings.value("media_player")

    @media_player.setter
    def media_player(self, value):
        if not is_command(value):
            raise ValueError("player must be a command")
        self.settings.setValue("media_player", value)

    @property
    def use_builtin_player(self):
        if HAS_PLAYER:
            return bool(int(self.settings.value("use_builtin_player")))
        else:
            return False

    @use_builtin_player.setter
    def use_builtin_player(self, value):
        self.settings.setValue("use_builtin_player", int(value))

    @property
    def notify_done(self):
        return bool(int(self.settings.value("Notification/notify_done")))

    @notify_done.setter
    def notify_done(self, value):
        self.settings.setValue("Notification/notify_done", value)

    @property
    def notify_error(self):
        return bool(int(self.settings.value("Notification/notify_error")))

    @notify_error.setter
    def notify_error(self, value):
        self.settings.setValue("Notification/notify_error", value)

    @property
    def download_folder(self):
        return self.settings.value("DownloadOptions/download_folder")

    @download_folder.setter
    def download_folder(self, value):
        self.settings.setValue("DownloadOptions/download_folder", value)

    @property
    def after_download(self):
        return int(self.settings.value("DownloadOptions/after_download"))

    @after_download.setter
    def after_download(self, value):
        self.settings.setValue("DownloadOptions/after_download", value)

    @property
    def show_search(self):
        value = self.settings.value("Window/show_search")
        try:
            value = int(value)
        except ValueError:
            value = {"true": True, "false": False}[value]
            
        return bool(value)

    @show_search.setter
    def show_search(self, value):
        self.settings.setValue("Window/show_search", value)

    @property
    def window_state(self):
        return self.settings.value("Window/state")

    @window_state.setter
    def window_state(self, value):
        self.settings.setValue("Window/state", value)

    @property
    def window_geometry(self):
        return self.settings.value("Window/geometry")

    @window_geometry.setter
    def window_geometry(self, value):
        self.settings.setValue("Window/geometry", value)
        
    @property
    def global_video_quality(self):
        val = self.settings.value("global_video_quality")
        if val not in ("ask", "low", "high"): 
            return ""
        
        return val
    
    @global_video_quality.setter
    def global_video_quality(self, value):
        self.settings.setValue("global_video_quality", value)
    
    @property
    def check_links_auto(self):
        return bool(int(self.settings.value("check_links_auto")))
    
    @check_links_auto.setter
    def check_links_auto(self, value):
        self.settings.setValue("check_links_auto", int(value))
    
    def remove(self, key):
        self.settings.remove(key)
    
    def sync(self):
        self.settings.sync()
        
    def getSettings(self):
        settings = self.getSettingsFile(QtCore.QSettings.NativeFormat)
        if not self.hasVersion(settings):
            settings = self.getSettingsFile(QtCore.QSettings.IniFormat)
        
        if self.getVersion(settings) == c.VERSION:
            return settings
        else:
            manage_settings = ManageSettings(settings.fileName())
            #if file exists but there's a version mismatch
            if self.hasVersion(settings):
                manage_settings.parseSettings()

        settings.clear()

        if settings.format() != QtCore.QSettings.NativeFormat:
            if os.path.exists(settings.fileName()): os.remove(settings.fileName())
            settings = self.getSettingsFile(QtCore.QSettings.NativeFormat)
        
        end_group = False
        for group in manage_settings.defaults:
            if end_group: 
                settings.endGroup()
                end_group = False

            if group != "General":
                settings.beginGroup(group)
                end_group = True
                    
            options = manage_settings.defaults[group]
            for option in options:
                 settings.setValue(option, options[option])
        
        if end_group: settings.endGroup()
        
        return settings
            
    def getSettingsFile(self, format):
        return QtCore.QSettings(format, QtCore.QSettings.UserScope,
                                 "WatchVideo", "watchvideo")

    def hasVersion(self, settings):
        if settings.value("General/version"):
            return True
        if settings.value("version"):
            return True
            
        return False

    def getVersion(self, settings):
        if settings.value("General/version"):
            return settings.value("General/version")
        if settings.value("version"):
            return settings.value("version")
            
        return ""


class ManageSettings(object):
    def __init__(self, config_file):
        
        self.config_file = config_file

        self.defaults = {}
        self.defaults["General"] = { "version": c.VERSION,
                            "media_player": main.get_default_player(),
                            "use_builtin_player": int(HAS_PLAYER),
                            "check_links_auto": 2,
                            "global_video_quality": "",
                            }
                            
        self.defaults["DownloadOptions"] = { "download_folder": os.path.expanduser("~"),
                                                "after_download": 0,
                                                "double_click_downloads": 0
                                            }
        self.defaults["Notification"] = {"notify_done": 2, "notify_error": 2}
        self.defaults["Window"] = {"state": "", "geometry": "", "show_search":2}

        
        self.map = {}
        self.map["folder"] = "download_folder"
        self.map["mediaplayer"] = "media_player"
        self.map["usebuiltinplayer"] = "use_builtin_player"
        self.map["afterdl"] = "after_download"
        self.map["dc_downloads"] = "double_click_downloads"
        self.map["notifydone"] = "notify_done"
        self.map["notifyerror"] = "notify_error"
        self.map["showsearch"] = "show_search"
        self.map["globalvideoquality"] = "global_video_quality"
        
        self.map_groups = {}
        self.map_groups["DownloadOpt"] = "DownloadOptions"
        self.map_groups["Geometry"] = "Window"
        self.map_groups["%General"] = "General"
    
    def setValue(self, group, key, value):
        self.defaults[group][key] = value
        
    def replaceValue(self, group, key, value):
        if group == "VideoQuality":
            self.defaults[group][key] = value
            return
        
        #test if group is valid
        try:
            self.defaults[group]
        except KeyError:
            try:
                self.defaults[self.map_groups[group]]
                group = self.map_groups[group]
            except KeyError:
                return
        
        #test if key is valid
        try:
            self.defaults[group][key]
            self.defaults[group][key] = value
        except KeyError:
            try:
                self.defaults[group][self.map[key]]
                self.defaults[group][self.map[key]] = value
            except KeyError:
                pass
        
    def parseSettings(self):
        parser = SafeConfigParser()
        parser.read(self.config_file)
        
        for section in parser.sections():
            if section == "VideoQuality":
                self.defaults["VideoQuality"] = {}
                
            for option in parser.options(section):
                if option == "version": continue
                
                if parser.get(section, option):
                    self.replaceValue(section, option, parser.get(section, option))
