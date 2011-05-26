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

import os
import sys
import tempfile
import time
from subprocess import Popen, PIPE, STDOUT

from watchvideo.qt import QtGui
import watchvideo.vlc as vlc
from watchvideo.qt import QtCore
from watchvideo.qt.QtCore import QObject
from watchvideo.slider import Slider
from watchvideo.qt.QtCore import Qt, QSize
import watchvideo.constants as c
import watchvideo.gui_utils as gui_utils
from watchvideo.tree_widget_item import TreeWidgetItem
from watchvideo.qt.QtGui import QProgressBar, QIcon

class Player(QObject):
    def __init__(self, pparent):
        self.parent = pparent
        QObject.__init__(self, self.parent)
       
        self.slider = self.parent.ui.progressBar #Slider(orientation=Qt.Horizontal, parent=pparent)
        self.paused = False
        self.download = None
        self.timer_load_file = None
        self.playing = False
        self.check_playback_timer = None
        self.timer_update_progressbar = None
        self.timer_load_file = None
        self.stopped_player = False
        self.last_value = 0.0
        self.filename = ""
        self.completed = False
        self.repeat = True
        self.repeat_modes = ["all", "one", "none"]
        self.repeat = "all"
        self.stopped = False
        self.treeWidgetItems = []
        self.activeItem = None
        
        # creating a basic vlc instance
        self.Instance = vlc.Instance()
        # creating an empty vlc media player
        self.MediaPlayer = self.Instance.media_player_new()
        self.slider.add_player(self.MediaPlayer)
        self.MediaPlayer.set_xwindow(self.parent.ui.videoWidget.winId())
        
        self.parent.ui.stackedWidget.setEnabled(False)
        self.parent.ui.btn_stop.setEnabled(False)
        
        self.timer_load_file = QtCore.QTimer(self.parent)
        self.timer_load_file.timeout.connect(self._load_file)
        
        self.check_playback_timer = QtCore.QTimer(self.parent)
        self.check_playback_timer.timeout.connect(self.check_playback)
        
        self.timer_update_progressbar = QtCore.QTimer(self.parent)
        self.timer_update_progressbar.timeout.connect(self.update_progressbar)
        
        self.wait_timer = QtCore.QTimer(self.parent)
        self.wait_timer.timeout.connect(self.play)
        
        self.move_text_timer = QtCore.QTimer(self.parent)
        self.move_text_timer.timeout.connect(self.moveText)
        
        #buttons
        self.parent.ui.btn_play.clicked.connect(self.play)
        self.parent.ui.btn_pause.clicked.connect(self.pause)
        self.parent.ui.btn_stop.clicked.connect(self.stop)
        
        #playlist
        self.parent.ui.playlistWidget.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.parent.ui.playlistWidget.customContextMenuRequested.connect(self.showRightClickMenu)
        self.parent.ui.playlistWidget.itemDoubleClicked.connect(self.playItem)
        self.update_downloads_timer = QtCore.QTimer(self.parent)
        self.update_downloads_timer.timeout.connect(self.update_downloads)
        
        self.parent.ui.playlistWidget.setIconSize(QSize(16,16))
        self.parent.ui.playlistWidget.header().setResizeMode(0, QtGui.QHeaderView.ResizeToContents)
        
        self.text_length = int(self.parent.ui.playlistWidget.width() / 9)
        self.counters = []
    
    def __del__(self):
        #qtwatchvideo process keeps running if this destructor isn't here
        pass
    
    def setFullscreen(self):
        """not working"""
        return
        print "fullscreen"
        #print "set full screen!"
        #window = QtGui.QWidget()
        #window.show()
        #self.parent.ui.videoWidget.setParent(window)
        self.MediaPlayer.set_xwindow(window.winId())
        if self.MediaPlayer.is_playing():
            self.MediaPlayer.set_fullscreen(True)

    
    def play(self):
        if self.wait_timer.isActive(): self.wait_timer.stop()
        if self.MediaPlayer.is_playing(): return
        
        if self.stopped:
            #if stopped and the download was aborted
            if not os.path.exists(self.filepath): return
            self.slider.loadfile(self.filepath)
            self.parent.ui.btn_stop.setEnabled(True)
        
        if self.download and self.completed:
            self.slider.loadfile(self.filepath)
            self.MediaPlayer.stop()
        
        if not self.check_playback_timer.isActive(): 
            self.check_playback_timer.start(750)
            
        self.activeItem.setIcon(0, QIcon(c.ICON_START))
        self.MediaPlayer.play()
        self.slider.start()
        self.playing = True
        self.paused = self.stopped = False
        self.completed = False
        self.parent.ui.stackedWidget.setCurrentIndex(1) #set pause button
        self.parent.ui.stackedWidget.setEnabled(True)
        
    def pause(self, checked, en_widget=True):
        self.activeItem.setIcon(0, QIcon(c.ICON_PAUSE))
        self.MediaPlayer.pause()
        self.paused = True
        self.slider.pause()
        self.parent.ui.stackedWidget.setCurrentIndex(0)
        self.parent.ui.btn_play.setEnabled(en_widget)
    
    
    def complete(self):
        print "completed"
        self.slider.complete()
        self.completed = True
        self.parent.ui.videoWidget.setStyleSheet("background-color: rgb(0, 0, 0);")
        self.parent.ui.stackedWidget.setCurrentIndex(0) #show play button
        self.playing = False
        
        if self.repeat == "none": return
        
        if self.repeat == "all":
            i = self.parent.ui.playlistWidget.indexOfTopLevelItem(self.activeItem)
            if i == self.parent.ui.playlistWidget.topLevelItemCount() - 1:
                i = 0
            else:
                i += 1
            
            self.playItem(self.parent.ui.playlistWidget.topLevelItem(i), i)
        else:
            self.play()
        
    
    def stop(self):
        self.stopped = True
        self.activeItem.setIcon(0, QIcon(c.ICON_STOP))
        self.reset()

    def restart(self):
        print "reloading file...."
        self.completed = True
        self.play()
        
        
    def loadfile(self, filepath, download, isNew=True):
        self.reset(progressBar=True) #reset everything
        self.parent.ui.stackedWidget.setEnabled(False)

        self.download = download
        self.filename = os.path.split(filepath)[1]
        
        if isNew:
            self.filepath = tempfile.gettempdir() + "/" + os.path.split(filepath)[1]
            self.activeItem = treeItem = TreeWidgetItem([], download, self.parent.ui.playlistWidget)
            treeItem.setToolTip(1, self.filename)
            self.counters.append(0)
            progressBar = QProgressBar(self.parent.ui.playlistWidget)
            progressBar.setFormat("%p% " + self.filename[:self.text_length])
            self.treeWidgetItems.append(treeItem)
            self.parent.ui.playlistWidget.addTopLevelItem(treeItem)
            self.parent.ui.playlistWidget.setItemWidget(treeItem, 1, progressBar)
            
            self.download.dest_file = self.filepath
            self.download.start()
        else:
            self.filepath = filepath
            
        if not self.update_downloads_timer.isActive():
            self.update_downloads_timer.start(1000)
        
        for i in xrange(self.parent.ui.playlistWidget.topLevelItemCount()):
            treeItem = self.parent.ui.playlistWidget.topLevelItem(i)
            if treeItem != self.activeItem:
                treeItem.setIcon(0, QIcon())
        
        self.activeItem.setIcon(0, QIcon(c.ICON_START))

        #set name on label
        self.parent.ui.nameLabel.setText(self.filename)

        self.bitrate = None
        self.total_duration = None
        self.curr_total_duration = None
        self.wait_time = 2 #wait counter to give time for the video to download
        self.last_value = 0.0
        
        #only start playing the file after some bytes are downloaded
        self.timer_load_file.start(1000)
        
    def _load_file(self):
        message = self.tr("Loading video, please wait...")
        self.parent.ui.statusbar.showMessage(message)
        
        if not os.path.exists(self.filepath): return
        
        self.slider.startProgressBar()
        
        if not self.timer_update_progressbar.isActive():
            self.timer_update_progressbar.start(1000)

        filesize = os.path.getsize(self.filepath)
        if filesize < 4096: return #4096 bytes minimum (random) to check for info in the file
        
        if not self.total_duration or not self.bitrate:
            self.total_duration = self.get_duration(self.filepath)
            self.bitrate = self.get_bitrate(self.filepath)
            return
        
        progress = (os.path.getsize(self.filepath) / float((self.download.size_kib*1024))) * 100
        self.parent.ui.statusbar.showMessage("%s %.1f%%" % (message, progress))
        
        if progress < 10:
            #load at least 10% of the video before start playing
            return
            
        self.timer_load_file.stop()
        self.parent.ui.statusbar.clearMessage()
        
        self.setTimeFormat()
        
        #load file
        # create the media
        filepath = self.filepath.encode(sys.getfilesystemencoding())
        self.Media = self.Instance.media_new(filepath)
        # parse the metadata of the file
        self.Media.parse()
        
        # put the media in the media player
        self.MediaPlayer.set_media(self.Media)
        self.MediaPlayer.play()
        
        self.playing = True
        self.stopped = self.completed = False
        self.slider.loadfile(self.filepath)

        
        #update buttons' state
        self.parent.ui.stackedWidget.setEnabled(True)
        self.parent.ui.stackedWidget.setCurrentIndex(1)
        self.parent.ui.btn_stop.setEnabled(True)
        
        self.check_playback_timer.start(750)
        
    def current_max_time(self):       
        return os.path.getsize(self.filepath) // self.bitrate
        
        
    def check_playback(self):
        if self.paused: return
        
        if not self.MediaPlayer.is_playing():
            if self.slider.max < 1000:
                self.restart()
            else:
                self.complete()
                
            return
        
        self.setTime() #set current playing time
            
        if self.download.completed: return
        
        self.slider.max = self.current_max_time() * 1000 / self.total_duration
        
        if self.MediaPlayer.get_position() * 1000  > self.slider.max:
            self.pause(False, en_widget=False)
            self.wait_timer.start(self.wait_time * 1000)
            self.wait_time += 2
    
    def setTimeFormat(self):
        #%M should have a 60 value, but since we want to always include minutes
        #and seconds, we put %M value also with 1
        self.timefmt = ""
        timefmts = [("%H:", 3600), ("%M:", 1), ("%S", 1)]
        
        for fmt in timefmts:
            value = fmt[1]
            if self.total_duration // value == 0: continue
            self.timefmt += fmt[0]
    
        self.total_duration_str = time.strftime(self.timefmt, time.gmtime(self.total_duration))
    
    def setTime(self):
        curr_pos = self.MediaPlayer.get_time() / 1000
        curr_pos_str = time.strftime(self.timefmt, time.gmtime(curr_pos))
        self.parent.ui.timeLabel.setText(curr_pos_str + "/" + self.total_duration_str)
    
            
    def update_progressbar(self):
        self.slider.progress = self.download.downloaded * 1000 / self.download.size_kib

        if self.download.completed:
            self.slider.max = 1000
            #hack to set the progressbar at 100%
            #self.progressbar.setValue(self.download.size_kib)
            self.slider.progress = self.slider.progress_max
            #stop checking, it's done!
            self.timer_update_progressbar.stop()
    
    def reset(self, progressBar=False, downloads=False):
        self.parent.ui.videoWidget.setStyleSheet("background-color: rgb(0, 0, 0);")
        self.parent.ui.stackedWidget.setCurrentIndex(0) #show play button
        self.parent.ui.btn_stop.setEnabled(False)
        self.parent.ui.timeLabel.setText("00:00/00:00")
        self.parent.ui.nameLabel.setText("")
        
        if self.move_text_timer.isActive():
            self.move_text_timer.stop()
    
        if self.download:            
            if not self.download.completed:
                if self.timer_update_progressbar.isActive(): 
                    self.timer_update_progressbar.stop()
                    
                self.parent.ui.stackedWidget.setEnabled(False)#disable play button
                
                #if the user aborts the download, there's no point showing the
                #progress in the progress bar
                self.slider.progress = self.slider.progress_max = 0
            
            if self.timer_load_file.isActive(): 
                self.timer_load_file.stop()
            if self.check_playback_timer.isActive(): 
                self.check_playback_timer.stop()
            
            #could be playing from complete or incomplete file
            if self.isPlaying(): self.MediaPlayer.stop()
                   
            self.slider.reset(progressBar)
            self.playing = False
            self.paused = False
            
        if downloads:
            if self.update_downloads_timer.isActive:
                self.update_downloads_timer.stop()
                
            for treeItem in self.treeWidgetItems:
                download = treeItem.getDownload()
                if download.isActive: download.abort()

    def get_duration(self, filepath):
        #return duration in seconds
        process = Popen(("ffmpeg", "-i", str(filepath)), stdout=PIPE,
                        stdin=PIPE,stderr=STDOUT)

        output = process.communicate()[0].decode("latin-1")
        duration = seconds = None
        
        for line in output.split('\n'):
            if "Duration:" in line:
                duration = line.split("Duration:")[1].split(',')[0].strip()
                seconds = int(duration.split(":")[0]) * 3600 + int(duration.split(":")[1]) * 60 + \
                            int(duration.split(":")[2].split(".")[0])
                break
                
        return seconds

        
    def get_bitrate(self, filepath):
        #return bitrate (if available) in bytes/s
        process = Popen(("ffmpeg", "-i", str(filepath)),stdout=PIPE,
                stdin=PIPE,stderr=STDOUT)

        output = process.communicate()[0].decode("latin-1")
        bitrate = None
        
        for line in output.splitlines():
            if "bitrate:" in line:
                bitrate = line.split("bitrate:")[1].split(" ")[1]
                if bitrate == "N/A": 
                    bitrate = None
                else:
                    bitrate = int(bitrate) * 1024 / 8
                    
                #print "bitrate: ", bitrate
                return bitrate
     
     
    def update_downloads(self):
        if not self.treeWidgetItems:
            if self.update_downloads_timer.isActive():
                self.update_downloads_timer.stop()
            return
        
        for treeItem in self.treeWidgetItems:
            download = treeItem.getDownload()
            progressBar = self.parent.ui.playlistWidget.itemWidget(treeItem, 1)
            
            if download.completed:
                self.treeWidgetItems.remove(treeItem)
                progressBar.setMaximum(download.size_kib)
                progressBar.setValue(download.size_kib)
            elif download.aborted:
                i = self.parent.ui.playlistWidget.indexOfTopLevelItem(treeItem)
                self.parent.ui.playlistWidget.takeTopLevelItem(i)
                self.treeWidgetItems.remove(treeItem)
            else:
                progressBar.setMaximum(download.size_kib)
                progressBar.setValue(download.downloaded)
            
    def playItem(self, item, pos):
        self.activeItem = item
        download = item.getDownload()
        self.loadfile(download.dest_file, download, isNew=False)
        
    def showRightClickMenu(self, point):
        if self.parent.ui.playlistWidget.selectedItems():
            self.parent.active_tree_widget = self.parent.ui.playlistWidget
            paused_found = False
            active_found = False
            completed_found = False
            self.parent.menu_active = "playlist"
            
            for item in self.parent.ui.playlistWidget.selectedItems():
                download = item.getDownload()
                
                if download.isStopped():
                    paused_found = True
                elif download.completed:
                    completed_found = True
                else:
                    active_found = True
                    
            self.parent.a_play_local.setEnabled(False)
            
            if active_found: #if an active download is found
                if not self.parent.stop.isEnabled(): self.parent.stop.setEnabled(True)
            else:
                if self.parent.stop.isEnabled(): self.parent.stop.setEnabled(False)
            
            if paused_found: #if a paused download is found
                if not self.parent.start.isEnabled(): self.parent.start.setEnabled(True)
            else:
                if self.parent.start.isEnabled(): self.parent.start.setEnabled(False)
            
            
            
            point = QtGui.QCursor.pos()
            self.parent.menu.exec_(point)
        
    def moveText(self):
        for i in xrange(self.parent.ui.playlistWidget.topLevelItemCount()):
            treeItem = self.parent.ui.playlistWidget.topLevelItem(i)
            fullname = " ~ " + treeItem.toolTip(1)
            if len(fullname) > self.text_length:
                progressBar = self.parent.ui.playlistWidget.itemWidget(treeItem, 1)
                buff_text = ""
                counter_begin = 0
                if self.counters[i] + self.text_length < len(fullname):
                    buff_text = fullname[self.counters[i]:self.counters[i]+self.text_length]
                else:
                    buff_text = fullname[self.counters[i]:]
                    counter_begin = self.counters[i] + self.text_length - len(fullname)
                    buff_text += fullname[:counter_begin]
                
                progressBar.setFormat("%p% " + buff_text)
                
                if self.counters[i] < len(fullname) - 1:
                    self.counters[i] += 1
                else:
                    self.counters[i] = 0
    
    def startTextMoveTimer(self):
        if ( self.parent.ui.playlistWidget.topLevelItemCount() > 0 and 
        not self.move_text_timer.isActive() ):
            self.move_text_timer.start(150)
        
    def stopTextMoveTimer(self):
        if self.move_text_timer.isActive():
            self.move_text_timer.stop()
        
    def isActive(self):
        return self.MediaPlayer.is_playing() or self.paused or self.areDownloadsActive()
        
    def areDownloadsActive(self):
        for item in self.treeWidgetItems:
            download = item.getDownload()
            if download.isActive(): return True
        
        return False
        
    def isPlaying(self):
        return self.MediaPlayer.is_playing() or self.paused
        
    def getFileName(self):
        return self.filename
        
    def getOriginalUrl(self):
        if self.download:
            return self.download.url
        else:
            return None
            
    def getDownloadItem(self):
        return self.download
    

    

