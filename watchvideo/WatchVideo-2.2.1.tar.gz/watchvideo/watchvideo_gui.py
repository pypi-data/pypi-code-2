#!/usr/bin/env python
# -*- coding: utf-8 -*- #
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
import sys
import os
import subprocess
import time
try:
    import json
    assert json
except ImportError:
    import simplejson as json
    assert json

from watchvideo.qt import QtCore, QtGui
from watchvideo.qt.QtGui import (QMenu, QAction, QIcon, QProgressBar,
                         QPushButton, QSystemTrayIcon,
                         QPixmap, QImage, QMouseEvent, QMainWindow)
from watchvideo.qt.QtCore import QTimer, QSize, QEvent
from watchvideo.ui_main import Ui_MainWindow
from watchvideo.threads import DownloadItem, Convert, Search
from watchvideo.notification import Notification
from watchvideo import main
import watchvideo.constants as c
from watchvideo import gui_utils
from watchvideo.utils import is_command
from watchvideo.tree_widget_item import TreeWidgetItem
from watchvideo.video_info import VideoInfo
from watchvideo.settings import Settings, HAS_PLAYER
from watchvideo.preferences import Preferences

if HAS_PLAYER and c.HAS_FFMPEG:
    from watchvideo.player import Player


class Gui(QtGui.QMainWindow):
    """WatchVideo's main class."""
    #gotVideo = Signal(tuple)  
    
    def __init__(self, app=None, options=None, args=None):
        """Initialize the GUI and many variables and load the configuration."""
        
        
        super(Gui, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.playlistWidget.hide()
        
        self.app = app
        
        # Load settings
        self.settings = Settings()
        
        self.download_urls = {}
        self.download_folder = c.HOME_FOLDER
        self.convert_thread = None
        self.active_download_items = []
        self.downloads_trash = []
        self.match_url = None
        self.action = ""
        self.namelabel = None
        self.menu_active = None
        self.show_confirm_dialog = True
        self.active_tree_widget = None
        self.ignoreMovement = 0
        self.quality_options = ["custom", "ask", "low", "high"]
        #the user can use different temporary quality
        self.global_quality = self.settings.global_quality 
        self.clipboard = QtGui.QApplication.clipboard()
        self.visited_urls = []
        self.searchIconSize = QSize(0, 0)
        
        #create actions for downloads, search and player's right click menu
        self.start = QAction(QIcon(c.PATH_MEDIA + "start.png"), self.tr("Start"), self)
        self.stop = QAction(QIcon(c.PATH_MEDIA + "stop.png"), self.tr("Stop"), self)
        self.remove = QAction(QIcon(c.ICON_REMOVE), self.tr("Remove"), self)
        self.remove_delete = QAction(QIcon(c.ICON_DELETE), self.tr("Remove and delete file"), self)
        self.opendir = QAction(QIcon(c.ICON_OPEN_FOLDER), self.tr("Open Folder"), self)
        self.copyurl = QAction(QIcon(c.ICON_COPY), self.tr("Copy original URL"), self)
        self.a_play_local = QAction(self.tr("Play local file"), self)
        self.a_download = QAction(QIcon(c.ICON_DOWNLOAD), self.tr("Download"), self)
        
        
        if HAS_PLAYER and c.HAS_FFMPEG:
          self.player = Player(self)
          #self.ui.horizontalLayout.addWidget(self.player.slider)
          self.ui.videoWidget.installEventFilter(self)
          self.ui.playlistWidget.installEventFilter(self)
          self.videoWidgetParent = self.ui.videoWidget.parentWidget()
          

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
          self.onReplayClicked(next=False)#update button's icon
        else:
          self.ui.tab_widget.removeTab(0)
          self.player = None
        
        #cancel button
        self.b_cancelSearch = QPushButton("Cancel", self.ui.statusbar)
        self.b_cancelSearch.clicked.connect(self.cancelSearch)
        self.b_cancelSearch.hide()
        
        #quality button
        self.btn_quality = QPushButton(self.ui.statusbar)
        self.btn_quality.setFlat(True)
        self.ui.statusbar.addPermanentWidget(self.btn_quality)
        self.switchQuality(next=False)
        
        #create tray icon
        self.trayicon = QSystemTrayIcon(QIcon(c.ICON_WATCHVIDEO), self.app)
        self.trayicon.show()
        
        self.notification = Notification(self.trayicon, self.settings)
        

        self.dialogs = {
            'about': None,        # The instance of the "About..." window will be stored here
            'preferences': None,        # The instance of the "Preferences" window will be stored here
            'add_videos': None,
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
        self.clipboard.dataChanged.connect(self.clipboardDataChanged)
       
        self.ui.btn_replay.clicked.connect(self.onReplayClicked)
        self.btn_quality.clicked.connect(self.switchQuality)

        #search related signals
        self.ui.searchLine.returnPressed.connect(self.searchYoutube)
        self.ui.b_search.pressed.connect(self.searchYoutube)
        self.ui.resultsWidget.itemDoubleClicked.connect(self.onSearchDoubleClick)
        self.a_download.triggered.connect(self.onDownloadActionPressed)
        self.ui.resultsWidget.customContextMenuRequested.connect(self.showResultsRightClickMenu)
        self.ui.a_viewSearch.toggled.connect(lambda state: self.ui.dockWidget.setVisible(state))
        
        self.loadWindow() #loads window geometry, widgets' size, etc
        
        if len(args) > 0:
            if options.down:
                self.action = "download"
                self.getFilesUrl(args)
            elif options.more:
                self.action = "clipboard"
                self.getFilesUrl(args)
            else:
                self.action = "play"
                self.getFilesUrl(args)
                
        

    def clipboardDataChanged(self):
        if not self.settings.check_links_auto: return
        
        if "http" in self.clipboard.text():
            text = self.clipboard.text().split()
            text = [ url for url in text if url not in self.visited_urls and "http://" in url ]
            
            if text:
                self.action = "clipboard-auto"
                self.getFilesUrl(text)
            
      
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
            download_item.copyAfterComplete(self.settings.download_folder, name)
            tree_item = TreeWidgetItem([name, "-", "", "0", "00:00:00"], 
                                        download_item)
                                        
            #insert QProgressBar
            self.ui.tree_downloads.addTopLevelItem(tree_item)
            self.ui.tree_downloads.setItemWidget(tree_item, 2, QProgressBar(self.ui.tree_downloads))
            
            self.active_download_items.append(tree_item)
            if not self.timer_check_downloads.isActive():
                self.timer_check_downloads.start(1000)

                
        else:
            urls = [ item.getOriginalUrl() for item in self.ui.resultsWidget.selectedItems()]
            self.action = "download"
            self.getFilesUrl(urls)
            
            
    def onSearchDoubleClick(self, item, pos):
        """On double click play the video - ToDo: Add option in preferences"""
        last_index = self.ui.resultsWidget.topLevelItemCount() - 1
        if not self.search.isRunning() and self.ui.resultsWidget.indexOfTopLevelItem(item) == last_index:
            self.ui.resultsWidget.takeTopLevelItem(last_index)
            self.searchYoutube(False)
            return
        
        self.action = "play"
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
            if image != QImage(c.ICON_ADD) and (image.width() > self.searchIconSize.width() and 
            image.height() > self.searchIconSize.height()):
                self.searchIconSize = QSize(image.width(), image.height())
                self.ui.resultsWidget.setIconSize(QSize(image.width(),image.height()))
                
                #image = gui_utils.setTextOnImage(image, "")
                
            item[1].setIcon(0, QIcon(QPixmap.fromImage(image)))
        self.ui.resultsWidget.addTopLevelItem(item[1])
    
    def onReplayClicked(self, checked=False, next=True):
        
        if next:
            i = self.player.repeat_modes.index(self.player.repeat)
            if i == len(self.player.repeat_modes) - 1:
                i = 0
            else:
                i += 1
                
            self.player.repeat = self.player.repeat_modes[i]
      
        if self.player.repeat == "none":
            self.ui.btn_replay.setIcon(self.disabled_replay_icon)
            self.ui.btn_replay.setToolTip(self.tr("Don't repeat"))
        elif self.player.repeat == "one":
            self.ui.btn_replay.setIcon(self.enabled_replay_icon)
            self.ui.btn_replay.setToolTip(self.tr("Repeat track"))
        else:
            self.ui.btn_replay.setIcon(QIcon(c.ICON_PLAYLIST_REPEAT))
            self.ui.btn_replay.setToolTip(self.tr("Repeat playlist"))
        

    def switchQuality(self, checked=False, next=True):
    
        if next: #when clicking in the button
            quality_options = self.quality_options
            if self.settings.global_video_quality: #remove the "custom" key
                quality_options = quality_options[1:]
            
            try:
                i = quality_options.index(self.global_quality)
                if i == len(quality_options) - 1:  i = 0
                else: i += 1
            except ValueError:
                i = 0
                
            option = quality_options[i]
        else:
            option = self.global_quality = self.settings.global_quality
        
        if option == "ask":
            icon = QIcon(c.ICON_ASK_QUALITY)
            msg = self.tr("A dialog to choose the format will appear for all videos with more than one format available.")
            img = "<img src='%s'><br></br>" % c.ICON_ASK_QUALITY
        elif option == "low":
            icon = QIcon(c.ICON_LOW_QUALITY)
            msg = self.tr("All videos are played/downloaded in the lowest quality available.")
            img = "<img src='%s'><br></br>" % c.ICON_LOW_QUALITY
        elif option == "high":
            icon = QIcon(c.ICON_HIGH_QUALITY)
            msg = self.tr("All videos are played/downloaded in the highest quality available.")
            img = "<img src='%s'><br></br>" % c.ICON_HIGH_QUALITY
        else:
            icon = QIcon(c.ICON_CUSTOM_QUALITY)
            msg = self.tr("The videos are played/downloaded according to what " + \
            "was defined in preferences. If it's the first time accessing a particular " + \
            "website through WatchVideo, the default action will be to ask for the quality.")
            img = "<img src='%s'><br></br>" % c.ICON_CUSTOM_QUALITY
        
        self.global_quality = img.split(":/media/")[1].split("-")[0]
        self.btn_quality.setToolTip(img+msg)
        self.btn_quality.setIcon(icon)
   
    def onDownloadDoubleClick(self, item, pos):
        #Open the folder containing the video or play it.
        download = item.getDownload()
        if not self.settings.play_downloaded:
            self.playDownload(download)
        else:
            self.openDir(os.path.split(download.dest_file)[0])
    
    def playDownload(self, download):
        if os.path.exists(download.dest_file):
            filename = os.path.split(download.dest_file)[1]
            Thread(target=main.play, args=(download.dest_file, filename,
            self.settings.media_player)).start()
                
                
    def startDownloads(self):
        if self.active_tree_widget is None: return
        for item in self.active_tree_widget.selectedItems():
            download = item.getDownload().resume()

    def stopDownloads(self):
        if self.active_tree_widget is None: return
        for item in self.active_tree_widget.selectedItems():
            download = item.getDownload()
            download.stop()
            item.setText(3, "Paused")
            item.setText(4, "Paused")

                    
    def removeTriggered(self):
        downloads_removed = []
        if self.active_tree_widget is None: return
        
        answer = None
 
        for item in self.active_tree_widget.selectedItems():
            download = item.getDownload()
            
            if answer is None:
                if not download.isActive():
                    answer = QtGui.QMessageBox.Yes
                else:
                    answer = gui_utils.confirm(self, "Abort Download(s)", self.tr("This will abort the download(s) too, are you sure?"))
            
            if answer == QtGui.QMessageBox.No: return
            
            if "playlist" in self.active_tree_widget.objectName():
                if download == self.player.download:
                    self.player.stop()
                
                if item in self.player.treeWidgetItems:
                    self.player.treeWidgetItems.remove(item)
                    
            
            if download.isActive():
                download.abort()
                self.downloads_trash.append(download)
            
            #remove the item
            self.removeDownloadItem(item)
            
            downloads_removed.append(download)
        
        if ( "downloads" in self.active_tree_widget.objectName()
        and self.active_tree_widget.topLevelItemCount() == 0 ):
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
            self.active_tree_widget = self.ui.tree_downloads
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
        self.action = ""
        if not videos: return
        
        if videos[0].down: #download
            self.ui.tab_widget.setCurrentIndex(1)
            for video in videos:
                if len(video.name) * 7 > self.ui.tree_downloads.header().sectionSize(0):
                    self.ui.tree_downloads.header().resizeSection(0, len(video.name)*7)
                
                download_item = DownloadItem(video.url, video.dl_url, video.filepath, video.after_complete, self)
                
                item = TreeWidgetItem([video.name, "-", "", "0", "00:00:00"], download_item)
                #insert QProgressBar
                self.ui.tree_downloads.addTopLevelItem(item)
                self.ui.tree_downloads.setItemWidget(item, 2, QProgressBar(self.ui.tree_downloads))
                
                download_item.start()
                self.active_download_items.append(item)
                
                if not self.timer_check_downloads.isActive():
                    self.timer_check_downloads.start(750)
        else: #Play
            self.ui.tab_widget.setCurrentIndex(0)
            if self.settings.use_builtin_player:
                for video in videos:
                    item = DownloadItem(video.url, video.dl_url, video.filepath, video.after_complete, self)
                    self.player.loadfile(video.filepath, item)
            else:
                #names = [video.name for video in videos]
                #urls = [video.dl_url for video in videos]
                for video in videos:
                    Thread(target=main.play, args=(video.dl_url, video.name,
                        self.settings.media_player)).start()
                    time.sleep(2)
                
        
        

    def afterComplete(self, download_item):
        start_thread = False
        if download_item.after_complete == 1: #play option
            Thread(target=main.play, args=(download_item.dest_file, os.path.split(download_item.dest_file)[1],
            self.settings.media_player)).start()
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
                if self.settings.notify_done:
                    self.notification.show(title_done, self.convert_thread.filename)
                self.ui.statusbar.showMessage(title_done + ": " + self.convert_thread.filename)
            else:
                self.notification.show(title_error, self.convert_thread.filename)
                self.ui.statusbar.showMessage(title_error + ": " + self.convert_thread.filename)
                if self.settings.notify_error:
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
        urls = [url for url in urls if "http" in url and len(url) > len("http")] 

        if urls:
            print urls
            #add cancel button
            self.b_cancelSearch.show()
            self.ui.statusbar.insertPermanentWidget(0, self.b_cancelSearch)
            self.cleanStatusTip()
            
            
            if "clipboard" in self.action: 
                quality = "ask"
            else:
                quality = self.global_quality
            
            self.match_url = main.Match(urls, quality, fast=False) #start a check thread       
            Thread(target=self.match_url.match, args=()).start()
            
            self.timer_match_urls.start(750)
        else:
            self.ui.statusbar.showMessage(self.tr("No valid URLs found."))
    

    
    def isCheckingDone(self):
        """Called in intervals of 750ms to see if the url thread is ready"""
        if self.match_url.done:
            self.timer_match_urls.stop()
            mediums = self.match_url.mediums
            ready_mediums = self.match_url.ready_mediums
            #a new website might have been added to the settings file
            #through ConfigParser, so we need to sync the QSettings instance with
            #the settings' file
            if self.match_url.update_settings: self.settings.sync()
            self.match_url = None
            self.resetStatusBar()
            
            if not mediums and not ready_mediums:
                self.ui.statusbar.showMessage(self.tr("No supported services were found"))
                self.b_cancelSearch.setText(self.tr("Close"))
                return
            
            #append mediums' urls to the visited urls
            for medium in mediums.keys() + ready_mediums.keys():
                self.visited_urls.append(medium.url)
            
            if self.action == "clipboard-auto":
                for medium in mediums: 
                    self.notification.show("WatchVideo", medium.title)
                self.action = "clipboard"
                
            if "clipboard" in self.action:
                for medium in ready_mediums:
                    mediums[medium] = [ready_mediums[medium]]
                ready_mediums = None
            
            if mediums:
                if "clipboard" in self.action:
                    self.showAddVideos(mediums)
                else:
                    self.showAddVideos(mediums, format_mode=True)
                
            if ready_mediums: 
                self.processVideos(ready_mediums)
                
                
        elif self.match_url.url: #if the url is valid, show it
            self.ui.statusbar.showMessage(self.tr("Currently checking: ") + self.match_url.url)
    
    
    def clearCompleted(self):
        for i in xrange(self.ui.tree_downloads.topLevelItemCount()-1, -1, -1):
            item = self.ui.tree_downloads.topLevelItem(i)
            download = item.getDownload()
            
            if download.completed:
                self.ui.tree_downloads.takeTopLevelItem(i)
                
        self.ui.a_clearCompleted.setDisabled(True)
        
    def updateDownloads(self):
        if not self.active_download_items:
            if self.timer_check_downloads.isActive():
                self.timer_check_downloads.stop()
            return
        
        for download in self.downloads_trash:
            if download.aborted: self.downloads_trash.remove(download)
        
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
                
                if self.settings.notify_done:
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
        
        if not dir:
            directories = set()
            for item in self.active_tree_widget.selectedItems():
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
            
            self.ui.statusbar.showMessage(self.tr("Opening download directory %s with %s") % (" ".join(directories), filemanager), 5000)

    def processVideos(self, mediums=None):
        
        if mediums is None: return
        
        videos = []
        
        for medium in mediums:
            format = mediums[medium]
            videos.append(VideoInfo(medium.title, medium.url, format.url))
        
        if self.action == "download":
            for video in videos: 
                video.folder = self.settings.download_folder
                video.after_complete = self.settings.after_download
        elif self.action == "play":
            for video in videos: video.toPlay()
        
        self.addNewDownloads(videos)

    #dialogs
    def showAddVideos(self, urls=None, format_mode=False):
        if self.dialogs["add_videos"] is None:
            from watchvideo.add_videos import AddVideosDialog
            self.dialogs["add_videos"] = AddVideosDialog(self, self.settings)
        
        self.dialogs["add_videos"].load(urls, format_mode)
        if self.isVisible():
            self.dialogs["add_videos"].show()
            self.dialogs["add_videos"].activateWindow()
        
        

    def showPreferences(self):
        """Displays the Preferences dialog."""
        self.dialogs['preferences'] = Preferences(self, self.settings)
        self.dialogs['preferences'].show()
        self.dialogs['preferences'].activateWindow()
        
    def showAbout(self):
        """Displays the About dialog."""
        if self.dialogs['about'] is None:
            from watchvideo.about import AboutDialog
            self.dialogs['about'] = AboutDialog(self)
        
        self.dialogs['about'].show()
        self.dialogs['about'].activateWindow()
        
    def addFromClipboard(self):
        urls = self.getClipboardText().split()
        objname = self.sender().objectName()
        if "a_" in objname:
            objname = objname.split("a_")[1]
        self.action = objname
        self.getFilesUrl(urls)
        
    def getClipboardText(self):
        return self.clipboard.text()
        
    def copyOriginalUrl(self):
        """Copies the original url to the Clipboard"""
        if self.menu_active == "download":
            urls = [item.getOriginalUrl() for item in self.ui.tree_downloads.selectedItems()]
        elif self.menu_active == "search":
            urls = [item.getOriginalUrl() for item in self.ui.resultsWidget.selectedItems()]
        elif self.menu_active == "playlist":
            urls = [item.getOriginalUrl() for item in self.ui.playlistWidget.selectedItems()]
        else:
            urls = [self.player.getOriginalUrl()]
        self.clipboard.setText("\n".join(urls))
        
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
        if self.settings.use_builtin_player:
            item = DownloadItem(video.url, video.dl_url, video.filepath, video.after_complete, self)
            self.player.loadfile(video.filepath, item)
        else:
            Thread(target=main.play, args=(video.dl_url, video.name,
            self.settings.media_player)).start()
            
    def removeDownloadItem(self, item, rmFromGui=True):
        """item: is a TreeWidgetItem
           rmFromGui: if true, removes the item from the QTreeWidget """
            
        if item in self.active_download_items:
            self.active_download_items.remove(item)
            
        if rmFromGui:
            i = self.active_tree_widget.indexOfTopLevelItem(item)
            if i != -1:
                if "playlist" in self.active_tree_widget.objectName():
                    del self.player.counters[i]
                self.active_tree_widget.takeTopLevelItem(i)
        
    
    def openWindow(self, activation):
        if activation in (3, 2): #show/hide window
            if self.isVisible():
                self.hide()
                for dialog in self.dialogs:
                    if self.dialogs[dialog] and self.dialogs[dialog].isVisible():
                        self.dialogs[dialog].hide()

            else:
                self.show()
                for dialog in self.dialogs:
                    if self.dialogs[dialog] and self.dialogs[dialog].visible:
                        self.dialogs[dialog].show()
                
                if self.dialogs['add_videos'] and self.dialogs['add_videos'].mediums:
                    self.dialogs['add_videos'].show()
                
    def eventFilter(self, obj, event):
        if obj == self.ui.videoWidget:

            if self.ignoreMovement:
                self.ignoreMovement -= 1
                return False
                
            if  event.type() == QEvent.MouseMove:
                if self.ui.videoWidget.width() - 50 < event.x() < self.ui.videoWidget.width():
                    self.ui.playlistWidget.show()
                    self.ignoreMovement = 8
                    self.player.startTextMoveTimer()
                else:
                    self.ui.playlistWidget.hide()
                    self.player.stopTextMoveTimer()

                return True
            elif event.type() == QEvent.MouseButtonDblClick:
                self.player.setFullscreen()
                return True
            else:
                return False
        elif obj == self.ui.playlistWidget:
            
            if self.ignoreMovement:
                self.ignoreMovement -= 1
                return False
                
            if  event.type() == QEvent.MouseMove:
                if event.x() < 0 or event.x() > self.ui.playlistWidget.width() or\
                event.y() < 0 or event.y() > self.ui.playlistWidget.height():
                    self.ui.playlistWidget.hide()
                    self.player.stopTextMoveTimer()
                    self.ignoreMovement = 10
                return True
            else:
                return False
    
        return QtGui.QMainWindow.eventFilter(obj, event)
    
    def isEverythingAborted(self):
        abortCompleted = True 
        for download_item in self.active_download_items:
            if not download_item.getDownload().aborted:
                download_item.getDownload().abort()
                return False
                     
        if self.player and self.player.areDownloadsActive():
            return False
           
        #just a measure for extra security when closing the app
        for download in self.downloads_trash:
            if not download.aborted:
                return False
                
        if self.dialogs["add_videos"] and not self.dialogs["add_videos"].isFinished():
            return False
            
        return True
    
    def abortDownloads(self):
        for download_item in self.active_download_items:
            download = download_item.getDownload()
            if download.isActive(): download.abort()
                
        if self.player: 
            self.player.reset(downloads=True)
            
        if self.dialogs["add_videos"] and not self.dialogs["add_videos"].isFinished():
            self.dialogs["add_videos"].close()
    
    def saveWindow(self):
        self.settings.window_state = self.saveState()
        self.settings.window_geometry = self.saveGeometry()
        self.settings.show_search = self.ui.a_viewSearch.isChecked()

        
    def loadWindow(self):
        if self.settings.window_geometry:
            self.restoreGeometry(self.settings.window_geometry)
        if self.settings.window_state:
            self.restoreState(self.settings.window_state)

        self.ui.a_viewSearch.setChecked(self.settings.show_search)
        
    
    def close_window(self):
        """called by self.close_timer"""
        self.show_confirm_dialog = False
        self.close()
    
    def closeEvent(self, event):
        if self.active_download_items or (self.player and self.player.isActive()) or (
        self.dialogs["add_videos"] and not self.dialogs["add_videos"].isFinished()):
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
                    return
            else:
                event.ignore()
                return
           

        self.saveWindow()
        
                
def run():
    app = QtGui.QApplication(sys.argv)
    
    from optparse import OptionParser
    parser = OptionParser(usage="usage: %prog [options] URL", \
    version=c.VERSION)
    
    parser.add_option("-d", "--download",
                        action="store_true",
                        dest="down",
                        default=False,
                        help="Specify links to download.")
                        
    parser.add_option("-m", "--more",
                        action="store_true",
                        dest="more",
                        default=False,
                        help="Shows a dialog where you can configure the" +\
                        "videos' available options and actions.")
    
    parser.add_option("-l", "--lang",
                        action="store",
                        dest="lang",
                        default=False,
                        help="Run WatchVideo in another language.")
    
    (options, args) = parser.parse_args()
    

    # Assert it to avoid pyflakes unused import warning -- resource
    # module imports have side effects.
    import watchvideo.translations_rc
    assert watchvideo.translations_rc

    if options.lang:
        locale = options.lang
    else:
        locale = QtCore.QLocale.system().name()
        
    translator = QtCore.QTranslator()
    translator.load(':/po/' + locale.split('_')[0])
    app.installTranslator(translator)

    mainApp = Gui(app, options, args)
    mainApp.show()

    try:
        app.exec_()
    except KeyboardInterrupt:
        sys.exit()



        
