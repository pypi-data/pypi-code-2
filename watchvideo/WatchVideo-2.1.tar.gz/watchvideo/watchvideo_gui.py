#!/usr/bin/env python
# -*- coding: utf-8 -*- #
'''WatchVideo GUI'''
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
import sys
import os
import subprocess
try:
    import json
    assert json
except ImportError:
    import simplejson as json
    assert json

from watchvideo.qt import QtCore, QtGui
from watchvideo.qt.QtGui import (QMenu, QAction, QIcon, QProgressBar,
                         QPushButton, QSystemTrayIcon,
                         QPixmap, QImage)
from watchvideo.qt.QtCore import QTimer, QSize
from watchvideo.ui_main import Ui_MainWindow
from watchvideo.threads import DownloadItem, Convert, Search
from watchvideo.preferences import Preferences, HAS_PLAYER
from watchvideo.notification import Notification
from watchvideo import main
import watchvideo.constants as c
from watchvideo import gui_utils
from watchvideo.utils import is_command
from watchvideo.tree_widget_item import TreeWidgetItem


if HAS_PLAYER and c.HAS_FFMPEG:
    from watchvideo.player import Player


class Gui(QtGui.QMainWindow):
    """WatchVideo's main class."""
    #gotVideo = Signal(tuple)  
    
    def __init__(self, app=None, urls=None):
        """Initialize the GUI and many variables and load the configuration."""
        
        
        super(Gui, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        
        self.app = app
        
        
        # Load settings
        self.settings = Preferences.loadSettings(self)
        
        
        self.download_urls = {}
        self.download_folder = c.HOME_FOLDER
        self.convert_thread = None
        self.active_download_items = []
        self.download_items = []
        self.videos_info = []
        self.match_url = None
        self.qaction_pressed = ""
        self.namelabel = None
        self.menu_active = None
        self.show_confirm_dialog = True
        
        #create actions for downloads, search and player's right click menu
        self.start = QAction(QIcon(c.PATH_MEDIA + "start.png"), self.tr("Start"), self)
        self.stop = QAction(QIcon(c.PATH_MEDIA + "stop.png"), self.tr("Stop"), self)
        self.remove = QAction(QIcon(c.ICON_REMOVE), self.tr("Remove"), self)
        self.remove_delete = QAction(QIcon(c.ICON_REMOVE), self.tr("Remove and delete file"), self)
        self.opendir = QAction(QIcon(c.ICON_OPEN_FOLDER), self.tr("Open Folder"), self)
        self.copyurl = QAction(QIcon(c.ICON_COPY), self.tr("Copy original URL"), self)
        self.a_play_local = QAction(self.tr("Play local file"), self)
        self.a_download = QAction(QIcon(c.ICON_DOWNLOAD), self.tr("Download"), self)
        
        if HAS_PLAYER and c.HAS_FFMPEG:
          self.player = Player(self)
          self.ui.horizontalLayout.addWidget(self.player.slider)

          #player's right click menu
          self.ui.videoWidget.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
          self.menu_player = QMenu(self)
          self.menu_player.addAction(self.copyurl)
          self.menu_player.addAction(self.a_download)
          self.ui.videoWidget.customContextMenuRequested.connect(self.showPlayerRightClickMenu)
          
          
          self.ui.nameLabel.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse)
          #repeat button
          self.disabled_replay_icon = gui_utils.getGreyedIcon(c.ICON_REPEAT)
          self.enabled_replay_icon = QIcon(c.ICON_REPEAT)
          self.ui.btn_replay.setFlat(True) 
        else:
          self.ui.tab_widget.removeTab(0)
          self.player = None
        
        #cancel button
        self.b_cancelSearch = QPushButton("Cancel", self.ui.statusbar)
        self.b_cancelSearch.clicked.connect(self.cancelSearch)
        self.b_cancelSearch.hide()
        
        #quality icons
        self.high_quality_icon = QIcon(c.ICON_HIGH_QUALITY)
        self.normal_quality_icon = QIcon(c.ICON_NORMAL_QUALITY)
        self.high_quality_description = "<img src='%s'><br></br>Videos are downloaded in high quality, if available." % c.ICON_HIGH_QUALITY
        self.normal_quality_description = "<img src='%s'><br></br>Videos are downloaded in normal quality." % c.ICON_NORMAL_QUALITY
        
        if Preferences.getGlobalQuality(self.settings) == "high":
          icon = self.high_quality_icon
          self.global_quality = "high"
          description = self.high_quality_description
        else:
          icon = self.normal_quality_icon
          description = self.normal_quality_description
          self.global_quality = "normal"
        
        self.btn_quality = QPushButton(icon, "", self.ui.statusbar)
        self.btn_quality.setFlat(True)
        self.btn_quality.setToolTip(description)
        self.ui.statusbar.addPermanentWidget(self.btn_quality)
        
        #create tray icon
        self.trayicon = QSystemTrayIcon(QIcon(c.ICON_WATCHVIDEO), self.app)
        self.trayicon.show()
        
        self.notification = Notification(self.trayicon, self.settings)
        

        self.dialogs = {
            'about': None,        # The instance of the "About..." window will be stored here
            'preferences': None,        # The instance of the "Preferences" window will be stored here
            'playlist': None,
            'history': None,
            'add_videos': None
            }

        
        if c.FIREFOX_SESSION is None:
            self.ui.a_searchBrowser.setDisabled(True)
        

        
        self.ui.tree_downloads.setColumnCount(5)
        self.ui.tree_downloads.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.menu = QMenu(self)
        
        #Timers
        self.timer_check_downloads = QTimer(self)
        self.timer_check_downloads.timeout.connect(self.updateDownloads)
        self.convert_timer = QTimer(self)
        self.convert_timer.timeout.connect(self.isConversionDone)
        self.timer_match_urls = QTimer(self)
        self.timer_match_urls.timeout.connect(self.isCheckingDone)
        self.close_timer = QTimer(self)
        self.close_timer.timeout.connect(self.close_window)
        self.close_timer.setSingleShot(True)
        
        #stuff related to the search
        self.search = None
        self.ui.searchLine.addResultsWidget(self.ui.resultsWidget)
        self.ui.resultsWidget.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.ui.searchLine.setFocus(QtCore.Qt.MouseFocusReason)
        self.ui.dockWidget.addAction(self.ui.a_viewSearch)
        self.abort_search_timer = QTimer(self)
        self.abort_search_timer.timeout.connect(self.searchYoutube)
        self.abort_search_timer.setSingleShot(True)
        
        #add actions to the search's right click menu
        self.search_menu = QMenu(self)
        self.search_menu.addAction(self.copyurl)
        self.search_menu.addAction(self.a_download)
        
        #add actions to the download's right click menu
        self.menu.addAction(self.start)
        self.menu.addAction(self.stop)
        self.menu.addSeparator()
        self.menu.addAction(self.remove)
        self.menu.addAction(self.remove_delete)
        self.menu.addSeparator()
        self.menu.addAction(self.opendir)
        self.menu.addAction(self.copyurl)
        self.menu.addAction(self.a_play_local)

        
        # connect signals with slots
        self.ui.a_addVideos.triggered.connect(self.showAddVideos)
        self.ui.a_searchBrowser.triggered.connect(self.searchBrowser)
        self.ui.a_clearCompleted.triggered.connect(self.clearCompleted)
        self.ui.a_preferences.triggered.connect(self.showPreferences)
        self.ui.a_about.triggered.connect(self.showAbout)
        self.ui.a_quit.triggered.connect(self.close)
        self.ui.a_clipboard.triggered.connect(self.addFromClipboard)
        self.ui.a_clipboard.hovered.connect(self.showStatusMessage)
        self.ui.a_play.triggered.connect(self.addFromClipboard)
        self.ui.a_play.hovered.connect(self.showStatusMessage)
        self.ui.a_download.triggered.connect(self.addFromClipboard)
        self.ui.a_download.hovered.connect(self.showStatusMessage)
        self.copyurl.triggered.connect(self.copyOriginalUrl)
        self.ui.tree_downloads.customContextMenuRequested.connect(self.showRightClickMenu)
        self.ui.tree_downloads.itemDoubleClicked.connect(self.onDownloadDoubleClick)
        self.start.triggered.connect(self.startDownloads)
        self.stop.triggered.connect(self.stopDownloads)
        self.remove.triggered.connect(self.removeTriggered)
        self.remove_delete.triggered.connect(self.removeAndDelete)
        self.opendir.triggered.connect(self.openDir)
        self.trayicon.activated.connect(self.openWindow)
        self.a_play_local.triggered.connect(self.play)
       
        self.ui.btn_replay.clicked.connect(self.onReplayClicked)
        self.btn_quality.clicked.connect(self.switchQuality)

        #search related signals
        self.ui.searchLine.returnPressed.connect(self.searchYoutube)
        self.ui.b_search.pressed.connect(self.searchYoutube)
        self.ui.resultsWidget.itemDoubleClicked.connect(self.onSearchDoubleClick)
        self.a_download.triggered.connect(self.onDownloadActionPressed)
        self.ui.resultsWidget.customContextMenuRequested.connect(self.showResultsRightClickMenu)
        self.ui.a_viewSearch.toggled.connect(lambda state: self.ui.dockWidget.setVisible(state))
        
        
        #Used to programatically resize the search dockWidget
        self.sizelabel = SizeLabel(parent=self.ui.dockWidgetContents)
        self.sizelabel.resize(self.sizelabel.width(), 0)
        self.ui.verticalLayout_3.addWidget(self.sizelabel)
        self.loadWindowGeometry()
        
        if urls: self.getFilesUrl(urls)
      
      
    def showPlayerRightClickMenu(self):
        if self.player and self.player.download:
            self.menu_active = "player"
            point = QtGui.QCursor.pos() 
            self.menu_player.exec_(point)
    
    
    def onDownloadActionPressed(self):
        """Used by the player and search"""
        if self.menu_active == "player":
            download_item = self.player.getDownloadItem()
            name = os.path.split(download_item.dest_file)[1]
            download_item.copyAfterComplete(self.settings.value("DownloadOpt/folder"), name)
            tree_item = TreeWidgetItem([name, "-", "", "0", "00:00:00"], 
                                        download_item)
                                        
            #insert QProgressBar
            self.ui.tree_downloads.addTopLevelItem(tree_item)
            self.ui.tree_downloads.setItemWidget(tree_item, 2, QProgressBar(self))
            
            self.active_download_items.append(tree_item)
            self.download_items.append(tree_item)
            if not self.timer_check_downloads.isActive():
                self.timer_check_downloads.start(1000)

                
        else:
            urls = [ item.getOriginalUrl() for item in self.ui.resultsWidget.selectedItems()]
            self.qaction_pressed = self.tr("Download")
            self.getFilesUrl(urls)
            
            
    def onSearchDoubleClick(self, item, pos):
        """On double click play the video - ToDo: Add option in preferences"""
        last_index = self.ui.resultsWidget.topLevelItemCount() - 1
        if not self.search.isRunning() and self.ui.resultsWidget.indexOfTopLevelItem(item) == last_index:
            self.ui.resultsWidget.takeTopLevelItem(last_index)
            self.searchYoutube(False)
            return
        
        self.qaction_pressed = self.tr("Play")
        self.getFilesUrl([item.getOriginalUrl()])
        
    
    def searchYoutube(self, clear_previous_search=True):
        if self.ui.searchLine.isEmpty():
            return
    
        if self.search and self.search.isRunning():
            self.search.abort()
            self.abort_search_timer.start(1000)
            return
        
        if clear_previous_search:
            for i in xrange(self.ui.resultsWidget.topLevelItemCount()-1, -1, -1):
                self.ui.resultsWidget.takeTopLevelItem(i)
            
        start_pos = self.ui.resultsWidget.topLevelItemCount() + 1
        
        self.search = Search(self, start_pos)
        self.search.start()
    
    
    def addResult(self, item):
        image = item[0]
        if image:
            if image != QImage(c.ICON_ADD):
                self.ui.resultsWidget.setIconSize(QSize(image.width(),image.height()))
                image = gui_utils.setTextOnImage(image, "")
                
            item[1].setIcon(0, QIcon(QPixmap.fromImage(image)))
        self.ui.resultsWidget.addTopLevelItem(item[1])
    
    def onReplayClicked(self):
      self.player.repeat = not self.player.repeat
      
      if self.player.repeat:
        self.ui.btn_replay.setIcon(self.enabled_replay_icon)
      else:
        self.ui.btn_replay.setIcon(self.disabled_replay_icon)
        
   
    def switchQuality(self):
      if self.global_quality == "high":
        self.btn_quality.setIcon(self.normal_quality_icon)
        self.global_quality = "normal"
        self.btn_quality.setToolTip(self.normal_quality_description)
      else:
        self.btn_quality.setIcon(self.high_quality_icon)
        self.global_quality = "high"
        self.btn_quality.setToolTip(self.high_quality_description)
   
    def onDownloadDoubleClick(self, item, pos):
        #Open the folder containing the video or play it.
        download = item.getDownload()
        if int(self.settings.value('DownloadOpt/dc_downloads')) == 0:
            self.playDownload(download)
        else:
            self.openDir(os.path.split(download.dest_file)[0])
    
    def playDownload(self, download):
        if os.path.exists(download.dest_file):
            filename = os.path.split(download.dest_file)[1]
            Thread(target=main.play, args=(download.dest_file, filename,
            self.settings.value('General/mediaPlayer'))).start()
                
                
    def startDownloads(self):
        for item in self.ui.tree_downloads.selectedItems():
            download = item.getDownload()
            download.resume()

    def stopDownloads(self):
        for item in self.ui.tree_downloads.selectedItems():
            download = item.getDownload()
            download.stop()
            item.setText(3, "Paused")
            item.setText(4, "Paused")

                    
    def removeTriggered(self):
        downloads_removed = []
        
        for item in self.ui.tree_downloads.selectedItems():
            download = item.getDownload()
            
            if not download.completed:
                download.abort()
            
            #remove the item
            self.removeDownloadItem(item)
            
            downloads_removed.append(download)
        
        if self.ui.tree_downloads.topLevelItemCount() == 0:
            self.ui.a_clearCompleted.setDisabled(True)
                    
        return downloads_removed
                        
            
    
    def removeAndDelete(self):
        downloads_removed = self.removeTriggered()
        
        for download in downloads_removed:
            os.remove(download.dest_file)


    def showResultsRightClickMenu(self, point):
        if self.ui.resultsWidget.selectedItems():
            self.menu_active = "search"
            point = QtGui.QCursor.pos() 
            self.search_menu.exec_(point) 
     
    def showRightClickMenu(self, point):
        if self.ui.tree_downloads.selectedItems():
            paused_found = False
            active_found = False
            completed_found = False
            self.menu_active = "download"
            
            for item in self.ui.tree_downloads.selectedItems():
                download = item.getDownload()
                
                if download.isStopped():
                    paused_found = True
                elif download.completed:
                    completed_found = True
                else:
                    active_found = True
                    
                    
            if completed_found:
                self.a_play_local.setEnabled(True)
            else:
                self.a_play_local.setEnabled(False)
            
            if active_found: #if an active download is found
                if not self.stop.isEnabled(): self.stop.setEnabled(True)
            else:
                if self.stop.isEnabled(): self.stop.setEnabled(False)
            
            if paused_found: #if a paused download is found
                if not self.start.isEnabled(): self.start.setEnabled(True)
            else:
                if self.start.isEnabled(): self.start.setEnabled(False)
                        
            point = QtGui.QCursor.pos() 
            self.menu.exec_(point)
        
        
    def addNewDownloads(self, videos):
        if not videos: 
            del self.videos_info [:]
            return
        
        if videos[0].down: #download
            self.ui.tab_widget.setCurrentIndex(1)
            for video in videos:
                if len(video.name) * 7 > self.ui.tree_downloads.header().sectionSize(0):
                    self.ui.tree_downloads.header().resizeSection(0, len(video.name)*7)
                
                download_item = DownloadItem(video.url, video.dl_url, video.filepath, video.after_complete, self)
                
                item = TreeWidgetItem([video.name, "-", "", "0", "00:00:00"], download_item)
                #insert QProgressBar
                self.ui.tree_downloads.addTopLevelItem(item)
                self.ui.tree_downloads.setItemWidget(item, 2, QProgressBar(self))
                
                download_item.start()
                self.download_items.append(item)
                self.active_download_items.append(item)
                
                if not self.timer_check_downloads.isActive():
                    self.timer_check_downloads.start(750)
        else: #Play
            self.ui.tab_widget.setCurrentIndex(0)
            if int(self.settings.value("General/useBuiltinPlayer")):
                video = videos[0] #for now the player only supports one video at a time
                item = DownloadItem(video.url, video.dl_url, video.filepath, video.after_complete, self)
                self.player.loadfile(video.filepath, item)
            else:
                for video in videos:
                    Thread(target=main.play, args=(video.dl_url, video.name,
                    self.settings.value('General/mediaPlayer'))).start()
                
        
        self.qaction_pressed = ""
        del self.videos_info [:]

    def afterComplete(self, download_item):
        start_thread = False
        if download_item.after_complete == 1: #play option
            Thread(target=main.play, args=(download_item.dest_file, os.path.split(download_item.dest_file)[1],
            self.settings.value('General/mediaPlayer'))).start()
        elif download_item.after_complete == 2: #convert to Ogg Vorbis
            self.convert_thread = Convert(main.convert, download_item.dest_file)
            start_thread = True
        elif download_item.after_complete == 3: #convert to Ogg Theora
            self.convert_thread = Convert(main.convert, download_item.dest_file, audio_only=False)
            start_thread = True
        elif download_item.after_complete == 4: #rip audio option
            self.convert_thread = Convert(main.rip, download_item.dest_file)
            start_thread = True
            
        if start_thread:
            self.convert_thread.start()
            self.convert_timer.start(750)
            
            
    def isConversionDone(self):
        if self.convert_thread.type == "rip":
            message_waiting = self.tr("Ripping audio of") + " " + self.convert_thread.filename
            title_done = self.tr("Audio Ripped")
            title_error = self.tr("Error ripping audio")
        else:
            message_waiting = self.tr("Converting video:") + " " + self.convert_thread.filename
            title_done = self.tr("Video Converted")
            title_error = self.tr("Error converting video")

        if self.convert_thread.isDone():
            self.convert_timer.stop()

            if self.convert_thread.successful:
                self.notification.show(title_done, self.convert_thread.filename)
                self.ui.statusbar.showMessage(title_done + ": " + self.convert_thread.filename)
            else:
                self.notification.show(title_error, self.convert_thread.filename)
                self.ui.statusbar.showMessage(title_error + ": " + self.convert_thread.filename)
                if self.settings.value("Notification/notifyError"):
                    self.notification.show(title_error, self.convert_thread.filename)
            
            self.convert_thread = None
        else:
            self.ui.statusbar.showMessage(message_waiting)

    def searchBrowser(self):
        session = json.loads(open(c.FIREFOX_SESSION).read().strip("()"))
        urls = []

        #search windows and tabs open in firefox
        for window in session["windows"]:
            for tab in window["tabs"]:
                for entry in tab["entries"]:
                    try:
                        urls.append(entry["url"])
                    except IndexError:
                        pass
        
        self.getFilesUrl(urls, fast=True)
                        

    def getFilesUrl(self, urls, fast=False):
        if self.match_url: return
        urls = [url for url in urls if url[:7] == "http://" and len(url) != len("http://")] 

        if urls:
            print urls
            #add cancel button
            self.b_cancelSearch.show()
            self.ui.statusbar.insertPermanentWidget(0, self.b_cancelSearch)
            self.cleanStatusTip()
            
            #define the quality before getting the URLs
            quality = Preferences.getQualityOptions(self.settings)
            if self.global_quality == "high":
              for q in quality: quality[q] = 1
            else:
              for q in quality: quality[q] = 0
            
            self.match_url = main.Match(urls, quality, fast=False) #start a check thread       
            Thread(target=self.match_url.match, args=()).start()
            

            self.timer_match_urls.start(750)
        else:
            self.ui.statusbar.showMessage(self.tr("No valid URLs found."))
    

    
    def isCheckingDone(self):
        """Called in intervals of 750ms to see if the url thread is ready"""
        if self.match_url.done:
            self.timer_match_urls.stop()
            self.match_url.done = False
            valid_videos = self.match_url.valid_videos
            self.match_url = None
            
            if valid_videos:
                self.resetStatusBar()
                
                if self.qaction_pressed == self.tr("Download"):
                    for video in valid_videos: 
                        video.folder = self.settings.value("DownloadOpt/folder")
                        video.after_complete = self.settings.value("DownloadOpt/afterDl")
                    self.addNewDownloads(valid_videos)
                elif self.qaction_pressed == self.tr("Play"):
                    for video in valid_videos: video.toPlay()
                    self.addNewDownloads(valid_videos)
                else:
                    self.showAddVideos(valid_videos)
                
            else:
                self.ui.statusbar.showMessage(self.tr("No supported services were found"))
                self.b_cancelSearch.setText(self.tr("Close"))
        elif self.match_url.url: #if the url is valid, show it
            self.ui.statusbar.showMessage(self.tr("Currently checking: ") + self.match_url.url)
    
    
    def clearCompleted(self):
        for i in xrange(self.ui.tree_downloads.topLevelItemCount()-1, -1, -1):
            item = self.ui.tree_downloads.topLevelItem(i)
            download = item.getDownload()
            
            if download.completed:
                self.download_items.remove(item)
                self.ui.tree_downloads.takeTopLevelItem(i)
                
        self.ui.a_clearCompleted.setDisabled(True)
        
    def updateDownloads(self):
        if not self.active_download_items:
            if self.timer_check_downloads.isActive():
                self.timer_check_downloads.stop()
            return
        
        for download_item in self.active_download_items:
            download = download_item.getDownload()
            if download.isStopped(): continue
            
            progressBar = self.ui.tree_downloads.itemWidget(download_item, 2)
            total_size = download.size
            unit = download.size_unit
            downloaded = download.downloaded
            speed = round(download.speed, 2)
            speed_unit = download.speed_unit
            time_left_str = download.time_left_str
            
            if download.completed:
                progressBar.setMaximum(download.size_kib)
                progressBar.setValue(download.size_kib)
                download_item.setText(3, "Completed") #Cleans the 'speed' column
                download_item.setText(4, "Completed") #Cleans the 'time left' column
                self.active_download_items.remove(download_item)
                
                if not self.ui.a_clearCompleted.isEnabled():
                    self.ui.a_clearCompleted.setEnabled(True)
                
                if self.settings.value("Notification/notifyDone"):
                    self.notification.show(self.tr("Download Finished"), 
                    os.path.split(download.dest_file)[1])
                
                self.afterComplete(download)
                
            else:
                download_item.setText(1, str(total_size) + " " + unit)
                progressBar.setMaximum(download.size_kib)
                progressBar.setValue(downloaded)
                
                download_item.setText(3, str(speed) + " " + speed_unit)
                download_item.setText(4, time_left_str)

    def openDir(self, dir=None):
        
        if dir is None:
            directories = set()
            for item in self.ui.tree_downloads.selectedItems():
                download = item.getDownload()
                directories.add(os.path.split(download.dest_file)[0])
            
            filemanager = None
        else:
            directories = (dir,)
        
        for manager in c.FILEMANAGERS:
            if is_command(manager):
                filemanager = manager
                break

        if filemanager:
            for directory in directories:
                subprocess.Popen((filemanager, directory))
            
            self.ui.statusbar.showMessage(self.tr("Opening download directory ") +
            " ".join(directories) + " " + self.tr("with") + " " + filemanager, 5000)
            
    #dialogs
    def showAddVideos(self, urls=None):
        if self.dialogs["add_videos"] is None:
            from watchvideo.add_videos import AddVideosDialog
            self.dialogs["add_videos"] = AddVideosDialog(self)
       
        self.dialogs["add_videos"].load_settings(self.settings)
        if urls: 
            self.dialogs["add_videos"].load_valid_urls(urls)
            self.dialogs["add_videos"].ui.g_pasteLinks.hide()
            self.dialogs["add_videos"].ui.b_checkLinks.hide()
            self.dialogs["add_videos"].ui.l_highquality.hide()
            self.dialogs["add_videos"].ui.cb_highquality.hide()
        else:
            self.dialogs["add_videos"].ui.g_pasteLinks.show()
            self.dialogs["add_videos"].ui.b_checkLinks.show()
            self.dialogs["add_videos"].ui.l_highquality.show()
            self.dialogs["add_videos"].ui.cb_highquality.show()
            
        self.dialogs["add_videos"].show()
        self.dialogs["add_videos"].activateWindow()
        
        

    def showPreferences(self):
        """Displays the Preferences dialog."""
        self.dialogs['preferences'] = Preferences(self, self.settings)
        self.dialogs['preferences'].show()
        self.dialogs['preferences'].activateWindow()
        self.dialogs['preferences'] = None
        
    def showAbout(self):
        """Displays the About dialog."""
        if self.dialogs['about'] is None:
            from watchvideo.about import AboutDialog
            self.dialogs['about'] = AboutDialog(self)
        
        self.dialogs['about'].show()
        self.dialogs['about'].activateWindow()
        
    def addFromClipboard(self):
        urls = self.getClipboardText().split()
        self.qaction_pressed = self.sender().text()
        self.getFilesUrl(urls)
        
    def getClipboardText(self):
        return QtGui.QApplication.clipboard().text()
        
    def copyOriginalUrl(self):
        """Copies the original url to the Clipboard"""
        if self.menu_active == "download":
            urls = [item.getOriginalUrl() for item in self.ui.tree_downloads.selectedItems()]
        elif self.menu_active == "search":
            urls = [item.getOriginalUrl() for item in self.ui.resultsWidget.selectedItems()]
        else:
            urls = [self.player.getOriginalUrl()]
        QtGui.QApplication.clipboard().setText("\n".join(urls))
        
    def showStatusMessage(self):
        if not self.match_url:
            self.sender().setStatusTip(self.getClipboardText())
            self.sender().showStatusText()
            
    def cleanStatusTip(self):
        self.ui.a_clipboard.setStatusTip("")
        self.ui.a_download.setStatusTip("")
        self.ui.a_play.setStatusTip("")
    
    def cancelSearch(self):
        self.stopChecking()
        self.resetStatusBar()
        
    def stopChecking(self):
        if self.match_url:
            self.match_url.stop = True
            self.timer_match_urls.stop()
            self.match_url = None
            
    def resetStatusBar(self):
        self.ui.statusbar.showMessage("")
        self.ui.statusbar.removeWidget(self.b_cancelSearch)
        
    def play(self, video):
        if self.settings.value("General/useBuiltinPlayer"):
            item = DownloadItem(video.url, video.dl_url, video.filepath, video.after_complete, self)
            self.player.loadfile(video.filepath, item)
        else:
            Thread(target=main.play, args=(video.dl_url, video.name,
            self.settings.value('General/mediaPlayer'))).start()
            
    def removeDownloadItem(self, item, rmFromGui=True):
        """item: is a TreeWidgetItem
           rmFromGui: if true, removes the item from the QTreeWidget """

        self.download_items.remove(item)
        if item in self.active_download_items:
            self.active_download_items.remove(item)
            
        if rmFromGui:
            i = self.ui.tree_downloads.indexOfTopLevelItem(item)
            self.ui.tree_downloads.takeTopLevelItem(i)
        
    
    def openWindow(self, activation):
        if activation in (3, 2): #show/hide window
            if self.isVisible():
                self.hide()
            else:
                self.show()
    
    def isEverythingAborted(self):
        abortCompleted = True 
        for download_item in self.active_download_items:
            if not download_item.getDownload().aborted:
                download_item.getDownload().abort()
                abortCompleted = False
                     
        if self.player and self.player.isDownloadActive():
            abortCompleted = False
         
        return abortCompleted
    
    def abortDownloads(self):
        for download_item in self.active_download_items:
            if not download_item.getDownload().aborted:
                download_item.getDownload().abort()
                
        if self.player: 
            self.player.reset()
    
    def saveWindowGeometry(self):
        self.settings.setValue("Geometry/windowWidth", self.width())
        self.settings.setValue("Geometry/windowHeight", self.height())
        self.settings.setValue("Geometry/searchWidth", self.ui.dockWidget.width())
        self.settings.setValue("Geometry/showSearch", int(self.ui.a_viewSearch.isChecked()))
        
    def loadWindowGeometry(self):
        if self.settings.value("Geometry/windowWidth"):
            width = int(self.settings.value("Geometry/windowWidth"))
            height = int(self.settings.value("Geometry/windowHeight"))
            self.resize(width, height)
            
            width = int(self.settings.value("Geometry/searchWidth"))
            self.sizelabel.customWidth = width
            if self.settings.value("Geometry/showSearch") is not None:
                self.ui.a_viewSearch.setChecked(int(self.settings.value("Geometry/showSearch")))
       
    
    def close_window(self):
        """called by self.close_timer"""
        self.show_confirm_dialog = False
        self.close()
    
    def closeEvent(self, event):
        if self.active_download_items or (self.player and self.player.isActive()):
            if self.show_confirm_dialog:
                answer = gui_utils.confirm(self, title="Quit?",
                msg=self.tr("There are still some tasks active, do you really want to quit?" + 
                "\n(you won't be able to continue them after quitting)"))
            else:
                answer = QtGui.QMessageBox.Yes
            
            if answer == QtGui.QMessageBox.Yes:
                self.abortDownloads()
                if not self.isEverythingAborted():
                    #hide GUI so it gets out of the user's way while the app is closing
                    self.hide() 
                    self.close_timer.start(750)
                    event.ignore()
            else:
                event.ignore()
                
        self.saveWindowGeometry()
                
class SizeLabel(QtGui.QLabel):
    """Used to programatically resize the search dockWidget"""
    def __init__(self, text="", parent=None):
        super(SizeLabel, self).__init__(text, parent)
        self.customWidth = self.width()
        
    def sizeHint(self):
        return QSize(self.customWidth, self.height())
                
def run():
    app = QtGui.QApplication(sys.argv)
    
    urls = [arg for arg in sys.argv if "http://" in arg and len(arg) > len("http://")]
    
    # Assert it to avoid pyflakes unused import warning -- resource
    # module imports have side effects.
    import watchvideo.translations_rc
    assert watchvideo.translations_rc

    locale = QtCore.QLocale.system().name()
    translator = QtCore.QTranslator()
    translator.load(':/po/' + locale.split('_')[0])
    
    app.installTranslator(translator)

    
    mainApp = Gui(app, urls)
    mainApp.show()

    try:
        app.exec_()
    except KeyboardInterrupt:
        sys.exit()

        
