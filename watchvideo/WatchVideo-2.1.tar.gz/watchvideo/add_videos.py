#!/usr/bin/env python
# -*- coding: utf-8 -*- #

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


from threading import Thread
import os.path

from watchvideo.qt import QtCore, QtGui
from watchvideo.qt.QtGui import QPushButton, QIcon
from watchvideo.ui_add_videos import Ui_AddVideos
from watchvideo import gui_utils
import watchvideo.constants as c
from watchvideo.video_info import VideoInfo
from watchvideo import main

class AddVideosDialog(QtGui.QDialog):
    def __init__(self, parent, settings=None):
        super(AddVideosDialog, self).__init__(parent)
        self.ui = Ui_AddVideos()
        self.ui.setupUi(self)

        self.ui.buttonBox.addButton(QPushButton(QIcon(c.ICON_ADD), self.tr("Add")), QtGui.QDialogButtonBox.AcceptRole)
        
        #init some variables
        self.parent = parent
        self.valid_videos = [] 
        self.invalid_urls = []
        self.match_url = None

        self.ui.label_status.setWordWrap(True)
        
        #connect buttons
        self.ui.b_checkLinks.clicked.connect(self.checkLinks)
        
        self.ui.rb_playDirectly.clicked.connect(self.checkedPlayDirectly)
        self.ui.rb_download.clicked.connect(self.checkedDownload)
        self.ui.b_folder.clicked.connect(self.selectFolder)
        self.ui.buttonBox.accepted.connect(self.add)
        self.ui.buttonBox.rejected.connect(self.cancel)
        self.ui.tree_validLinks.itemDoubleClicked.connect(self.itemDoubleClicked)
        
        self.ui.tree_validLinks.setColumnCount(3)
        self.ui.tree_validLinks.header().setResizeMode(2, QtGui.QHeaderView.ResizeToContents)
        self.ui.tree_validLinks.header().setSectionHidden(3, True)
        
        self.icon_error = QtGui.QIcon(c.ICON_ERROR)
        self.icon_valid = QtGui.QIcon(c.ICON_VALID)
    
    def load_settings(self, settings):
        #Set preferred after download option
        self.ui.combo_options.setCurrentIndex(int(settings.value('DownloadOpt/afterDl')))
        
        #set preferred folder
        self.ui.ledit_destFolder.setText(settings.value('DownloadOpt/folder'))
        
        self.settings = settings
    
    def load_valid_urls(self, urls):
        self.valid_videos = urls
        self.addUrlsToTree()
        
    def itemDoubleClicked(self, item, column):
        if column == 0:
            item.setFlags(item.flags() | QtCore.Qt.ItemIsEditable)
        else:
            item.setFlags(item.flags() & ~QtCore.Qt.ItemIsEditable)
    
    def closeEvent(self, e):
        self.cancel()

    def cancel(self):
        self.stopChecking()
        #self.ui.tedit_pasteLinks.clear()
        if not os.path.exists(self.ui.ledit_destFolder.text()):
            self.ui.ledit_destFolder.setText(self.settings.value('DownloadOpt/folder'))
        self.ui.tree_validLinks.clear()
        self.close()
        
    def stopChecking(self):
        if self.match_url:
            self.match_url.stop = True
            self.timerThread.stop()
            
    def checkedPlayDirectly(self):
        self.ui.frame_dl.hide()
        
    def checkedDownload(self):
        self.ui.frame_dl.show()
    
    def checkLinks(self):
        self.stopChecking()
        urls = self.ui.tedit_pasteLinks.toPlainText().split('\n')
        self.ui.tedit_pasteLinks.clear()
        self.ui.tedit_pasteLinks.setDisabled(True)

        urls = [ url for url in urls if url[:7] == "http://" and len(url) != len("http://")]
        
        if urls:
            self.ui.label_status.setText("Checking... please wait.")
            self.ui.tree_validLinks.clear()
            
            qualityOptions = {}
            if self.ui.cb_highquality.isChecked():
                qualityOptions = self.parent.getQualityOptions()
                #set all options to high quality (1)
                for plug_name in qualityOptions:
                    qualityOptions[plug_name] = 1

            
            self.match_url = main.Match(urls, quality_options=qualityOptions)        
            Thread(target=self.match_url.match, args=()).start()

            self.timerThread = QtCore.QTimer()
            self.timerThread.timeout.connect(self.isCheckingDone)
            self.timerThread.start(750)
        else:
            self.ui.tedit_pasteLinks.setEnabled(True)
            
    def isCheckingDone(self):
        """Called in intervals of 750ms to see if the url thread is ready"""
        if self.match_url.done:
            self.timerThread.stop()
            self.timerThread = None
            self.invalid_urls = self.match_url.invalid_urls
            self.valid_videos = self.match_url.valid_videos
            self.match_url = None
            self.ui.label_status.setText("")
            self.addUrlsToTree()
        elif self.match_url.url: #if the url is valid, show it
            self.ui.label_status.setText("Currently checking: %s" % self.match_url.url)
            
    def addUrlsToTree(self):
        for video in self.valid_videos:
            if len(video.name) * 6 > self.ui.tree_validLinks.header().sectionSize(0):
                self.ui.tree_validLinks.header().resizeSection(0, len(video.name)*6)
            
            item = QtGui.QTreeWidgetItem([video.name, video.url, "", video.dl_url])
            item.setIcon(0, self.icon_valid)
            item.setCheckState(2, QtCore.Qt.Checked)
            
            self.ui.tree_validLinks.addTopLevelItem(item)
        
        for url in self.invalid_urls:
            item = QtGui.QTreeWidgetItem(["", url, "", ""])
            item.setIcon(0, self.icon_error)
            self.ui.tree_validLinks.addTopLevelItem(item)
            
        self.ui.tedit_pasteLinks.setEnabled(True)
        
    def add(self):
        if not os.path.exists(self.ui.ledit_destFolder.text()):
            gui_utils.warning(self, title=self.tr("Warning"), 
            msg=self.tr("The given download folder doesn't exist!"))
            return
            
        download_option = self.ui.rb_download.isChecked()
        dest_folder = self.ui.ledit_destFolder.text()
        after_dl = self.ui.combo_options.currentIndex()

        videos_info = []
        for i in xrange(self.ui.tree_validLinks.topLevelItemCount()):
            item = self.ui.tree_validLinks.topLevelItem(i)
            if item.checkState(2):
                
                name = item.text(0)
                overwrite = True
                if main.check_if_file_exists(dest_folder, name):
                    answer = gui_utils.confirm(self, title=self.tr("Overwrite"),
                    msg=self.tr("Do you wish to overwrite this file?") + '\n' + name)
                    
                    if answer == QtGui.QMessageBox.No:
                        filepath = main.get_new_file(dest_folder, name)
                        name = os.path.split(filepath)[1]
                        overwrite = False
                
                videos_info.append(VideoInfo(name, item.text(1), item.text(3),
                download_option, dest_folder, after_dl, overwrite))
                
        if not videos_info or self.ui.tree_validLinks.topLevelItemCount() == 0:
            gui_utils.warning(self, msg=self.tr("There are no valid links to add!"))
        else:
            self.parent.videos_info = videos_info #to delete
            self.close()
            self.parent.addNewDownloads(videos_info)
                    
    def selectFolder(self):
        folder = gui_utils.selectFolder(self, self.ui.ledit_destFolder.text())
        if folder: self.ui.ledit_destFolder.setText(folder)
        
        



