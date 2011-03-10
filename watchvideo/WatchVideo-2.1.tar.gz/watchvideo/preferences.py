#!/usr/bin/env python
# -*- coding: utf-8 -*- #
'''WatchVideo Preferences'''
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

import os

from watchvideo.qt import QtCore, QtGui
from watchvideo.qt.QtGui import QComboBox
from watchvideo.ui_preferences import Ui_PreferencesWindow
from watchvideo import notification
from watchvideo import gui_utils
from watchvideo import main
from watchvideo.utils import is_command
import watchvideo.constants as c

try:
    import watchvideo.player
except ImportError:
    HAS_PLAYER = False
else:
    assert watchvideo.player
    HAS_PLAYER = True


class Preferences(QtGui.QDialog):
    """The class responsible for the Preferences window."""
    
    def __init__(self, parent, settings):
        """Initialize the GUI."""
        
        super(Preferences, self).__init__(parent)
        self.ui = Ui_PreferencesWindow()
        self.ui.setupUi(self)
        
        self.settings = settings
        self.parent = parent
        self.ordered_options = []
        self.update_global_quality = True

        #Populate the QTreeWidget with the plugins' names and options
        self.ui.tree_quality.header().resizeSection(0, 350)
        plugins = main.MATCHER.plugins.values()
        for plugin in plugins:
            plug_name = plugin.get_plugin_name()

            if plugin.has_high_quality():
                cb_qualityOptions = QComboBox(self)
                cb_qualityOptions.addItem("Normal")
                cb_qualityOptions.addItem("High")
                
                item = QtGui.QTreeWidgetItem([plug_name, ""])
                self.ui.tree_quality.addTopLevelItem(item)
                self.ui.tree_quality.setItemWidget(item, 1, cb_qualityOptions)
                
                cb_qualityOptions.setCurrentIndex(int(self.settings.value('VideoQuality/%s' % plug_name)))
        
        #update the bottom radiobuttons when a combobox changes its state
        for i in range(self.ui.tree_quality.topLevelItemCount()):
            item = self.ui.tree_quality.topLevelItem(i)
            cb = self.ui.tree_quality.itemWidget(item, 1)
            cb.currentIndexChanged.connect(self.updateGlobalQuality)
            
        self.updateGlobalQuality(0)
        
        
        self.ui.cb_builtinPlayer.setChecked(self.isChecked(self.settings.value('General/useBuiltinPlayer')))
        if not HAS_PLAYER or not c.HAS_FFMPEG:
            self.ui.cb_builtinPlayer.setEnabled(False)
            self.ui.cb_builtinPlayer.setChecked(0)
        self.on_builtinPlayer_check()
            
        
        # Update the window to display the current configuration
        self.ui.ledit_player.setText(self.settings.value('General/mediaPlayer'))
        self.last_valid_player=self.settings.value('General/mediaPlayer')
        
        self.ui.edit_folder.setText(self.settings.value('DownloadOpt/folder'))
        
        self.ui.combo_options.setCurrentIndex(self.isChecked(self.settings.value('DownloadOpt/afterDl')))
        self.ui.combo_dc.setCurrentIndex(self.isChecked(self.settings.value('DownloadOpt/dc_downloads')))
        
        self.ui.s_notifyDone.setChecked(self.isChecked(self.settings.value('Notification/notifyDone')))
        self.ui.s_notifyError.setChecked(self.isChecked(self.settings.value('Notification/notifyError')))
        
        if notification.HAS_PYNOTIFY:
            self.ui.f_note.hide()

        
        # Connect signals with slots
        self.ui.btn_player.clicked.connect(self.browseForFile)
        self.ui.button_folder.clicked.connect(self.browseFolder)
        self.ui.buttonBox.accepted.connect(self.saveSettings)
        self.ui.buttonBox.rejected.connect(self.close)
        self.ui.rb_all_high_quality.clicked.connect(self.setHighQualityToAll)
        self.ui.rb_all_low_quality.clicked.connect(self.setLowQualityToAll)
        self.ui.cb_builtinPlayer.clicked.connect(self.on_builtinPlayer_check)
        
    def on_builtinPlayer_check(self):
        self.ui.Lmedia_player.setEnabled(not self.ui.cb_builtinPlayer.isChecked())
        self.ui.btn_player.setEnabled(not self.ui.cb_builtinPlayer.isChecked())
        self.ui.ledit_player.setEnabled(not self.ui.cb_builtinPlayer.isChecked())
    
    def updateGlobalQuality(self, index):
        if self.update_global_quality:
            global_quality = self.getQualityFromAll()
            if global_quality is None:
                self.ui.rb_mixed_quality.setCheckable(True)
                self.ui.rb_mixed_quality.setChecked(True)
            elif global_quality == "low":
                self.ui.rb_all_low_quality.setChecked(True)
            else:
                self.ui.rb_all_high_quality.setChecked(True)
        
    def setLowQualityToAll(self):
        #Since we're going to change the index of many comboboxes,
        #to prevent them to send a signal everytime, we use this 
        #variable to control the updateGLobalQuality
        self.update_global_quality = False 
        self.setQualityToAll(0)
        self.ui.rb_mixed_quality.setCheckable(False)
        self.update_global_quality = True
        
    def setHighQualityToAll(self):
        #Since we're going to change the index of many comboboxes,
        #to prevent them to send a signal everytime, we use this 
        #variable to control the updateGLobalQuality
        self.update_global_quality = False 
        self.setQualityToAll(1)
        self.ui.rb_mixed_quality.setCheckable(False)
        self.update_global_quality = True
        

    def setQualityToAll(self, value=0):
        for i in range(self.ui.tree_quality.topLevelItemCount()):
            item = self.ui.tree_quality.topLevelItem(i)
            cb = self.ui.tree_quality.itemWidget(item, 1)
            cb.setCurrentIndex(value)
            
    def getQualityFromAll(self):
        high_quality_count = low_quality_count = i = 0
        for i in range(self.ui.tree_quality.topLevelItemCount()):
            item = self.ui.tree_quality.topLevelItem(i)
            cb = self.ui.tree_quality.itemWidget(item, 1)
            if cb.currentIndex() == 0:
                low_quality_count += 1
            else:
                high_quality_count += 1
        
        i += 1
        
        if i == low_quality_count:
            return "low"
        elif i == high_quality_count:
            return "high"
        else:
            return None
      
    
    def saveSettings(self):
        """Saves the settings."""
        
        #if self.ui.s_rememberUrl.checkState() == 2:
            #self.urlStorage.sync()
        
        if self.isValidPlayer():        
            self.settings.setValue('General/mediaPlayer', self.ui.ledit_player.text())
        elif not self.ui.cb_builtinPlayer.checkState():
            gui_utils.warning(self, self.tr("Media Player"), self.tr("Given media player is not valid"))
            return 0
            
        self.settings.setValue('General/useBuiltinPlayer', int(self.ui.cb_builtinPlayer.checkState()))
        
        self.settings.setValue('DownloadOpt/folder', self.ui.edit_folder.text())
        self.settings.setValue('DownloadOpt/afterDl', self.ui.combo_options.currentIndex())
        self.settings.setValue('DownloadOpt/dc_downloads', self.ui.combo_dc.currentIndex())

        for i in range(self.ui.tree_quality.topLevelItemCount()):
            item = self.ui.tree_quality.topLevelItem(i)
            cb = self.ui.tree_quality.itemWidget(item, 1)
            self.settings.setValue('VideoQuality/%s' % item.text(0), cb.currentIndex())

        self.settings.setValue('Notification/notifyDone', int(self.ui.s_notifyDone.checkState()))
        self.settings.setValue('Notification/notifyError', int(self.ui.s_notifyError.checkState()))
        self.settings.sync()
        
        #self.parent.settings.sync()
        self.parent.settings = self.settings
        if Preferences.getGlobalQuality(self.settings) != self.parent.global_quality:
          self.parent.switchQuality()
        #self.parent.adjustInputs(updatedSettings=True)
        #self.parent.loadConfig()
        self.close()

    def check_save_url(self):
        if self.ui.save_url.isChecked():
            self.ui.save_url_disk.setEnabled(True)
        else:
            if self.ui.save_url_disk.isChecked():
                self.ui.save_url_disk.setChecked(False)
            self.ui.save_url_disk.setDisabled(True)
            
    def browseForFile(self):
        filepath = gui_utils.selectFile(self)
        if filepath: 
            self.ui.ledit_player.setText(os.path.split(filepath)[1])

    def browseFolder(self):
        """Shows a folder selection dialog and (if the user doesn't cancel it) 
        sets the new destination in the input."""
        folder = gui_utils.selectFolder(self, self.ui.edit_folder.text())
        if folder: self.ui.edit_folder.setText(folder)
    
    def isValidPlayer(self):
        return is_command(self.ui.ledit_player.text())
    

    def isChecked(self, value):
        if type(value).__name__ == "unicode":
          return int(value)
        
        return False
        
    @classmethod
    def getGlobalQuality(cls, settings):
        options = cls.getQualityOptions(settings)
        high_quality = 0
  
        for opt in options:
          if options[opt] == 1:
            high_quality += 1

        if len(options) == high_quality:
          return "high"
         
        return "normal"
    
    @classmethod
    def getQualityOptions(cls, settings):
        plugins = main.MATCHER.plugins.values()
        quality_options = {}
        for plugin in plugins:
            plug_name = plugin.get_plugin_name()
            value = settings.value("VideoQuality/%s" % plug_name)
            if value is not None:
              quality_options[plug_name] = int(value)
              
        return quality_options
            
    @classmethod
    def loadSettings(cls, parent):
        """Returns a QSettings instance and, if needed, populates it with the default settings."""
        
        settings = QtCore.QSettings(QtCore.QSettings.IniFormat, QtCore.QSettings.UserScope, 'WatchVideo', 'watchvideo')
        
        if not settings.contains('General/version') or settings.value('General/version') != c.VERSION:
            cls.defaultSettings(settings, parent)
        
        return settings
    

    @classmethod
    def defaultSettings(cls, settings, parent):
        """Overwrittes a QSettings instance with all default settings."""
        
        from os.path import expanduser
        
        settings.clear()    # Delete everything from the file
        
        settings.beginGroup('General')
        settings.setValue('version', c.VERSION)
        settings.setValue('mediaPlayer', main.get_default_player())
        settings.setValue('useBuiltinPlayer', 0)
        settings.endGroup()

        settings.beginGroup('DownloadOpt')
        settings.setValue('folder', expanduser('~'))
        settings.setValue('afterDl', 0)
        settings.setValue('dc_downloads', 0)
        settings.endGroup()
        
        settings.beginGroup('VideoQuality')
        plugins = main.MATCHER.plugins.values()
        for plugin in plugins:
            if plugin.has_high_quality():
                settings.setValue(plugin.__name__, 0)
        settings.endGroup()

        settings.beginGroup('Notification')
        settings.setValue('notifyDone', 2)
        settings.setValue('notifyError', 0)
        settings.endGroup()

        settings.beginGroup('Geometry')
        settings.setValue('windowWidth', parent.width())
        settings.setValue('windowHeight', parent.height())
        settings.setValue('searchWidth', parent.ui.dockWidget.width())
        settings.setValue('showSearch', 1)
        settings.endGroup()
    
