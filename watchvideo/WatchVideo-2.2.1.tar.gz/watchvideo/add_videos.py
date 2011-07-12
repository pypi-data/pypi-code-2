#!/usr/bin/env python
# -*- coding: utf-8 -*-
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


from threading import Thread
import os.path

from watchvideo.qt import QtCore, QtGui
from watchvideo.qt.QtCore import QSize
from watchvideo.qt.QtGui import QPushButton, QIcon, QComboBox
from watchvideo.ui_add_videos import Ui_AddVideos
from watchvideo import gui_utils
import watchvideo.constants as c
from watchvideo.video_info import VideoInfo
from watchvideo import main
from watchvideo.main import describe_format
from watchvideo.tree_widget_item import TreeWidgetItem

class AddVideosDialog(QtGui.QDialog):
    def __init__(self, parent, settings=None):
        super(AddVideosDialog, self).__init__(parent)
        self.ui = Ui_AddVideos()
        self.ui.setupUi(self)

        self.ui.buttonBox.addButton(QPushButton(QIcon(c.ICON_ADD), self.tr("Add")), QtGui.QDialogButtonBox.AcceptRole)
        
        #init some variables
        self.parent = parent
        self.invalid_urls = []
        self.match_url = None
        self.settings = settings
        self.mediums = {}

        self.ui.label_status.setWordWrap(True)
        
        #connect buttons
        self.ui.b_checkLinks.clicked.connect(self.checkLinks)
        
        self.ui.rb_playDirectly.clicked.connect(self.checkedPlayDirectly)
        self.ui.rb_download.clicked.connect(self.checkedDownload)
        self.ui.b_folder.clicked.connect(self.selectFolder)
        self.ui.buttonBox.accepted.connect(self.add)
        self.ui.buttonBox.rejected.connect(self.close)
        self.ui.tree_validLinks.itemDoubleClicked.connect(self.itemDoubleClicked)
        
        self.ui.tree_validLinks.header().setResizeMode(0, QtGui.QHeaderView.ResizeToContents)
        
        self.icon_error = QIcon(c.ICON_ERROR)
        
        self.timerThread = QtCore.QTimer()
        self.timerThread.timeout.connect(self.isCheckingDone)
        self.visible = True
    
    def load(self, mediums, format_mode):
        #Set preferred after download option
        self.ui.combo_options.setCurrentIndex(int(self.settings.after_download))
        #set preferred folder
        self.ui.ledit_destFolder.setText(self.settings.download_folder)


        if mediums:
            self.ui.g_pasteLinks.hide()
            self.ui.b_checkLinks.hide()
            if self.height() < 520:
                self.resize(self.width(), 520)

            if format_mode:
                #format mode means the current action is different from the
                # 'clipboard' action
                self.hideDownloadOptions()
                
                if self.parent.action == "play":
                    self.ui.rb_playDirectly.setChecked(True)
                else:
                    self.ui.rb_download.setChecked(True)
                    
                
                self.setWindowTitle(self.tr("Choose Format"))
            else:
                self.showDownloadOptions()
                
            for medium in mediums:
                self.mediums[medium] = mediums[medium]
                
            self.addUrlsToTree(mediums)
        else:
            if not self.ui.tedit_pasteLinks.isEnabled():
                self.ui.tedit_pasteLinks.setEnabled(True)
            self.ui.g_pasteLinks.show()
            self.ui.b_checkLinks.show()
            self.showDownloadOptions()


    def hideDownloadOptions(self):
        self.ui.rb_playDirectly.hide()
        self.ui.rb_download.hide()
        self.ui.frame_dl.hide()
    
    def showDownloadOptions(self):
        self.ui.frame_dl.show()
        self.ui.rb_playDirectly.show()
        self.ui.rb_download.show()
        
    def itemDoubleClicked(self, item, column):
        if column == 0:
            item.setFlags(item.flags() | QtCore.Qt.ItemIsEditable)
        else:
            item.setFlags(item.flags() & ~QtCore.Qt.ItemIsEditable)
    
    def closeEvent(self, e):
        self.stopChecking()
        self.mediums = {}
        if not os.path.exists(self.ui.ledit_destFolder.text()):
            self.ui.ledit_destFolder.setText(self.settings.download_folder)
        self.ui.tree_validLinks.clear()
        self.ui.label_status.setText("")
        for i in xrange(self.ui.tree_validLinks.topLevelItemCount()-1, -1, -1):
           self.ui.tree_validLinks.takeTopLevelItem(i)
        self.visible = False
        print "Closing Add Videos Dialog"
        
        
    def stopChecking(self):
        if self.match_url and not self.match_url.done: self.match_url.stop()
        if self.timerThread.isActive(): self.timerThread.stop()
            
    def checkedPlayDirectly(self):
        self.ui.frame_dl.hide()
        
    def checkedDownload(self):
        self.ui.frame_dl.show()
    
    def checkLinks(self, checked=False, urls=None):
        self.stopChecking()
        if not urls:
            urls = self.ui.tedit_pasteLinks.toPlainText().split('\n')
        
        self.ui.tedit_pasteLinks.clear()
        self.ui.tedit_pasteLinks.setDisabled(True)
        urls = [url for url in urls if "http" in url and len(url) > len("http")] 
        
        if urls:
            self.ui.label_status.setText("Checking... please wait.")
            self.ui.tree_validLinks.clear()
                        
            self.match_url = main.Match(urls, quality="ask")        
            Thread(target=self.match_url.match, args=()).start()

            self.timerThread.start(750)
        else:
            self.ui.tedit_pasteLinks.setEnabled(True)
            
    def isCheckingDone(self):
        """Called in intervals of 750ms to see if the url thread is ready"""
        if self.match_url.done:
            self.timerThread.stop()
            self.ui.label_status.setText("")
            self.mediums = self.match_url.mediums
            for medium in self.match_url.ready_mediums:
                self.mediums[medium] = [self.match_url.ready_mediums[medium]]
            self.invalid_urls = self.match_url.invalid_urls
            self.addUrlsToTree()
        elif self.match_url.url: #if the url is valid, show it
            self.ui.label_status.setText("Currently checking: %s" % self.match_url.url)

    
    def addUrlsToTree(self, mediums=None):
        self.match_url = None
        
        if mediums is None: mediums = self.mediums
        
        for medium in mediums:
            item = TreeWidgetItem([medium.website+": "+medium.title, ""], medium, self.ui.tree_validLinks)
            item.setCheckState(0, QtCore.Qt.Checked)
            self.ui.tree_validLinks.addTopLevelItem(item)
            combobox = QComboBox(self.ui.tree_validLinks)
     
            try:
                for format in mediums[medium]:
                    combobox.addItem(describe_format(format))
            except TypeError:
                format_desc = describe_format(mediums[medium])
                combobox.addItem(format_desc)
        
            self.ui.tree_validLinks.setItemWidget(item, 1, combobox)
            
        
        for url in self.invalid_urls:
            item = QtGui.QTreeWidgetItem(self.ui.tree_validLinks, [url, ""])
            item.setIcon(0, self.icon_error)
            self.ui.tree_validLinks.addTopLevelItem(item)
            
        self.ui.tedit_pasteLinks.setEnabled(True)
        
    def add(self):
        if not os.path.exists(self.ui.ledit_destFolder.text()):
            gui_utils.warning(self, title=self.tr("Warning"), 
            msg=self.tr("The given download folder doesn't exist!"))
            return
            
        download = self.ui.rb_download.isChecked()
        dest_folder = self.ui.ledit_destFolder.text()
        after_dl = self.ui.combo_options.currentIndex()
        videos = []
        
        for i in xrange(self.ui.tree_validLinks.topLevelItemCount()):
            item = self.ui.tree_validLinks.topLevelItem(i)
            
            if item.checkState(0):
                combobox = self.ui.tree_validLinks.itemWidget(item, 1)
                medium = item.getMedium()
                format = self.mediums[medium][combobox.currentIndex()]
                name = item.text(0)
                overwrite = True
                
                
                if main.file_exists(dest_folder, name):
                    answer = gui_utils.confirm(self, title=self.tr("Overwrite"),
                    msg=self.tr("Do you wish to overwrite this file?") + '\n' + name)
                    
                    if answer == QtGui.QMessageBox.No:
                        filepath = main.get_new_file(dest_folder, name)
                        name = os.path.split(filepath)[1]
                        overwrite = False
                
                videos.append(VideoInfo(name, medium.url, format.url,
                download, dest_folder, after_dl, overwrite))
                
        if not videos or self.ui.tree_validLinks.topLevelItemCount() == 0:
            gui_utils.warning(self, msg=self.tr("There are no valid links to add!"))
        else:
            self.close()
            self.parent.addNewDownloads(videos)
                    
    def selectFolder(self):
        folder = gui_utils.selectFolder(self, self.ui.ledit_destFolder.text())
        if folder: self.ui.ledit_destFolder.setText(folder)
        
    def show(self):
        self.visible = True
        super(AddVideosDialog, self).show()

    def isFinished(self):
        if self.match_url:
            return self.match_url.done
        return True
