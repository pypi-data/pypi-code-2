# -*- coding: utf-8 -*- #
'''WatchVideo Preferences'''
# Copyright (C) 2010, 2011 Carlos Pais <freemind@lavabit.com>
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
###

import os

from watchvideo.qt import QtGui
from watchvideo.qt.QtGui import QComboBox
from watchvideo.ui_preferences import Ui_PreferencesWindow
from watchvideo import notification
from watchvideo import gui_utils
from watchvideo import main
from watchvideo.utils import is_command
import watchvideo.constants as c
from watchvideo.settings import HAS_PLAYER


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
        
        quality_options = self.settings.get_quality_options()
        for option in quality_options:
            cb_qualityOptions = QComboBox(self)
            cb_qualityOptions.addItem(self.tr("Ask Quality"))
            cb_qualityOptions.addItem(self.tr("Low Quality"))
            cb_qualityOptions.addItem(self.tr("High Quality"))
            
            item = QtGui.QTreeWidgetItem([option.capitalize(), ""])
            self.ui.tree_quality.addTopLevelItem(item)
            self.ui.tree_quality.setItemWidget(item, 1, cb_qualityOptions)
            
            cb_qualityOptions.setCurrentIndex(quality_options[option])
            cb_qualityOptions.currentIndexChanged.connect(self.updateGlobalQuality)
        
        
        self.ui.cb_applyToAll.setChecked(bool(self.settings.global_video_quality))
        self.updateGlobalQuality()

        self.ui.cb_builtinPlayer.setChecked(self.settings.use_builtin_player)
        if not HAS_PLAYER or not c.HAS_FFMPEG:
            self.ui.cb_builtinPlayer.setEnabled(False)
            self.ui.cb_builtinPlayer.setChecked(0)
        self.on_builtinPlayer_check()
        
        # Update the window to display the current configuration
        self.ui.ledit_player.setText(self.settings.media_player)
        self.last_valid_player=self.settings.media_player
         
        self.ui.edit_folder.setText(self.settings.download_folder)
         
        self.ui.combo_options.setCurrentIndex(self.settings.after_download)
        self.ui.combo_dc.setCurrentIndex(self.settings.play_downloaded)
         
        self.ui.s_notifyDone.setChecked(self.settings.notify_done)
        self.ui.s_notifyError.setChecked(self.settings.notify_error)
        self.ui.cb_checkLinksAuto.setChecked(self.settings.check_links_auto)
        
        if notification.HAS_PYNOTIFY:
            self.ui.f_note.hide()
        
        # Connect signals with slots
        self.ui.btn_player.clicked.connect(self.browseForFile)
        self.ui.button_folder.clicked.connect(self.browseFolder)
        self.ui.buttonBox.accepted.connect(self.saveSettings)
        self.ui.buttonBox.rejected.connect(self.close)
        self.ui.rb_all_high_quality.clicked.connect(self.setGlobalQuality)
        self.ui.rb_all_low_quality.clicked.connect(self.setGlobalQuality)
        self.ui.rb_all_ask.clicked.connect(self.setGlobalQuality)
        self.ui.cb_builtinPlayer.clicked.connect(self.on_builtinPlayer_check)
        self.ui.cb_applyToAll.clicked.connect(self.updateGlobalQuality)
        
        self.visible = True
        
    def on_builtinPlayer_check(self):
        self.ui.Lmedia_player.setEnabled(not self.ui.cb_builtinPlayer.isChecked())
        self.ui.btn_player.setEnabled(not self.ui.cb_builtinPlayer.isChecked())
        self.ui.ledit_player.setEnabled(not self.ui.cb_builtinPlayer.isChecked())
    
    def updateGlobalQuality(self, index=0):
        """SLOT connected to the quality comboboxes"""
        if self.update_global_quality:
            if self.ui.cb_applyToAll.isChecked():
                global_quality = self.settings.global_video_quality
                if not global_quality: global_quality = "ask"
            else:
                global_quality = self.getGlobalQuality()

            if global_quality == "ask":
                self.ui.rb_all_ask.setChecked(True)
            elif global_quality == "low":
                self.ui.rb_all_low_quality.setChecked(True)
            elif global_quality == "high":
                self.ui.rb_all_high_quality.setChecked(True)
            else:
                self.ui.rb_mixed_quality.setCheckable(True)
                self.ui.rb_mixed_quality.setChecked(True)
        
    def setGlobalQuality(self):
        """SLOT connected to the QRadioButtons "all ask", "all low" and "all high" """
        #if applyToAll is checked, don't alter the values in the comboboxes.
        if self.ui.cb_applyToAll.isChecked(): return
        
        objname = self.sender().objectName()
        for index, type in enumerate(["ask", "low", "high"]):
            if type in objname: break
        
        #Since we're going to change the index of many comboboxes,
        #to prevent the method updateGlobalQuality from being called many times,
        #we use this variable to control it.
        self.update_global_quality = False
        self.ui.rb_mixed_quality.setCheckable(False)
        
        for i in range(self.ui.tree_quality.topLevelItemCount()):
            item = self.ui.tree_quality.topLevelItem(i)
            cb = self.ui.tree_quality.itemWidget(item, 1)
            cb.setCurrentIndex(index)
            
        self.update_global_quality = True
            
    def getGlobalQuality(self):
        """Determines if options are all ask, low, high or other"""
        total_items = self.ui.tree_quality.topLevelItemCount()
        count = 0
        for i in range(self.ui.tree_quality.topLevelItemCount()):
            item = self.ui.tree_quality.topLevelItem(i)
            cb = self.ui.tree_quality.itemWidget(item, 1)
            count += cb.currentIndex()
        
        if count == 0:
            return "ask"
        elif count == total_items:
            return "low"
        elif count == total_items * 2:
            return "high"
        else:
            return ""
      
    
    def saveSettings(self):
        """Saves the settings."""
        
        try:
            self.settings.media_player = self.ui.ledit_player.text()
        except ValueError:
            gui_utils.warning(self, self.tr("Media Player"), self.tr("Given media player is not valid"))
            return 0
        
        self.settings.use_builtin_player = self.ui.cb_builtinPlayer.checkState()
        self.settings.download_folder = self.ui.edit_folder.text()
        self.settings.after_download = self.ui.combo_options.currentIndex()
        self.settings.play_downloaded = self.ui.combo_dc.currentIndex()
        if self.ui.cb_applyToAll.isChecked():
            if self.ui.rb_all_ask.isChecked():
                self.settings.global_video_quality = "ask"
            elif self.ui.rb_all_low_quality.isChecked():
                self.settings.global_video_quality = "low"
            elif self.ui.rb_all_high_quality.isChecked():
                self.settings.global_video_quality = "high"
        elif self.settings.global_video_quality:
            self.settings.remove("global_video_quality")

        for i in range(self.ui.tree_quality.topLevelItemCount()):
            item = self.ui.tree_quality.topLevelItem(i)
            cb = self.ui.tree_quality.itemWidget(item, 1)
            self.settings.set_quality(item.text(0), cb.currentIndex())

        self.settings.notify_done = self.ui.s_notifyDone.checkState()
        self.settings.notify_error = self.ui.s_notifyError.checkState()
        self.settings.check_links_auto = self.ui.cb_checkLinksAuto.checkState()
        
        self.settings.sync()
        
        if self.settings.global_quality != self.parent.global_quality:
          self.parent.switchQuality(next=False)

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

    def closeEvent(self, e):
        self.visible = False
