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

import threading
import os
import time
from datetime import datetime, timedelta

from getmediumurl.reader import ReaderError

import watchvideo.constants as c
from watchvideo.main import MATCHER, get_new_file
from watchvideo.qt.QtCore import QThread, QTimer
from watchvideo.qt.QtGui import (QTreeWidgetItem, QImage)
from watchvideo.youtubesearch import YoutubeSearch
from watchvideo.searchparams import SearchParams
from watchvideo.tree_widget_item import TreeWidgetItem
from watchvideo.qt.QtCore import Signal

import shutil


class Convert(threading.Thread):
    '''Thread to convert to Ogg Vorbis or Theora, or rips the audio from the video'''
    def __init__(self, callback, filepath, audio_only=True, remove_original=True):
        self.callback = callback
        self.filepath = filepath
        self.filename = os.path.split(filepath)[1]
        self.audio_only = audio_only
        self.remove_original = remove_original
        self.type = callback.__name__
        self.successful = False
        self.done = False
        
        threading.Thread.__init__(self)
        
    def run(self):
        if self.type == "rip":
            self.successful = self.callback(self.filepath, self.remove_original)
        else:
            self.successful = self.callback(self.filepath, self.audio_only, self.remove_original)
            
        self.done = True
   
    def isDone(self):
        return self.done
        

class Download(threading.Thread):
    """Downloads the video"""
    
    def __init__(self, video, path, title=""):
        self.video = video
        self.path = path
        self.title = title
        self.local_size = 0
        self.remote_size_kb = 0
        self.stop = False #if true means the download is paused
        self.abort = False #if true the download will stop
        self.done = False       

        threading.Thread.__init__(self)
    
    def run(self):
        
        try:
            remote_file = c.OPENER.open(self.video)
            local_file = open(self.path, 'wb')
            local_size = 0.0
            remote_size = int(remote_file.info()['content-length'])
            self.remote_size_kb = remote_size // 1024

            while local_size < remote_size:
                if self.abort: break
                
                if self.stop is False: 
                    buffering = remote_file.read(4096)
                    local_file.write(buffering)
                    local_size += len(buffering)
                    self.local_size = local_size // 1024
                    
            remote_file.close()
            local_file.close()
            if local_size > 0.0:
                self.done = True

        except IOError:
            pass    # The process was killed, 
                    #probably because the user closed the GUI

    def isDone(self):
        return self.done

class DownloadItem(QThread):
    def __init__(self, url, dl_url, dest_file, after_complete=0, parent=None):
        self.url = url
        self.dest_file = dest_file
        self.new_path = None  #is used when saving a video from the player
        self.dl_url = dl_url
        self.after_complete = after_complete
        self.completed = False
        self._abort = self.aborted = False
        self._stop = False
        self.init_date = datetime.now()
        self.stop_date = None
        self.time_passed = timedelta(seconds=0)
        self.time_left_str = "00:00:00"
        self.time_stopped = timedelta(seconds=0)
        self.downloaded = 0
        self.local_size_ant = 0
        self.timeout = 0
        self.speed = 0.0
        self.check_download = QTimer()
        self.check_download.timeout.connect(self.checkDownloadState)
        self.speed_unit = "KiB/s"
        bytes = self.getFileSizeInBytes()
        self.size_kib = bytes // 1024
        
        #set unit size
        self.size, self.size_unit = self.setSize(bytes)
    
        super(DownloadItem, self).__init__(parent)
        
    def run(self):
        self.threadDl = Download(self.dl_url, self.dest_file)
        self.threadDl.start()
        self.check_download.start(1000)
        
    def checkDownloadState(self):
        self.timeout += 1
        self.threadDl.stop = self._stop
        self.threadDl.abort = self._abort
        
        if self._abort:
            if not self.threadDl.isAlive():
                self.check_download.stop()
                if os.path.exists(self.dest_file):
                    os.remove(self.dest_file)
                self.aborted = True
            return
            
        self.time_passed = datetime.now() - self.init_date
        
        if self._stop and self.stop_date is None: #if stopped
            self.stop_date = datetime.now()
        
        if self.stop_date and not self._stop: #if restarted 
            self.time_stopped += datetime.now() - self.stop_date
            self.stop_date = None
            
        self.calcTimeLeft()
            
        #timeout
        if self.timeout == 20 and self.threadDl.local_size == 0:
            self._abort = True
            return

        #if finished
        if self.threadDl.isDone():
            if self.new_path:
                shutil.copy(self.dest_file, self.new_path)
            self.completed = True
            self.check_download.stop()
        #else update 
        elif self.local_size_ant < self.threadDl.local_size:
            self.speed = self.threadDl.local_size - self.local_size_ant
            self.speed, self.speed_unit = self.setSize(self.speed * 1024)
            self.speed_unit += "/s"
            self.local_size_ant = self.downloaded = self.threadDl.local_size #in KiB
        

    def calcTimeLeft(self):
        sec = float(str(self.time_passed-self.time_stopped).split(':')[2])
        min = float(str(self.time_passed-self.time_stopped).split(':')[1]) * 60
        hour = float(str(self.time_passed-self.time_stopped).split(':')[0]) * 3600
        
        time_passed_sec = sec + min + hour
        
        try:
            time_left_sec = ((self.size_kib - self.downloaded) * time_passed_sec) / self.downloaded
            self.time_left_str = time.strftime('%H:%M:%S', time.gmtime(time_left_sec))
        except ZeroDivisionError:
            pass
        
    def setSize(self, size):
        """receives size in bytes"""
        unit = "???"
        for unit in ("B", "KiB", "MiB", "GiB", "TiB", "PiB"):
            if size < 2**10:
                return size, unit
            else: 
                size /= 2**10
                
        return size, unit
                
    def getFileSizeInBytes(self):
        remote_file = c.OPENER.open(self.dl_url)
        bytes = int(remote_file.info()['content-length'])
        return bytes
        
    def copyAfterComplete(self, path, name):
        new_dest = get_new_file(path, name)
        if self.completed:
            shutil.copy(self.dest_file, new_dest)
        else:
            self.new_path = new_dest
            
            
    def abort(self):
        self._abort = True

    def stop(self):
        self._stop = True
    
    def isStopped(self):
        return self._stop
        
    def resume(self):
        self._stop = False
        
        
        
class Search(QThread):
    gotVideo = Signal(tuple)
    def __init__(self, parent, start_pos):
        super(Search, self).__init__(parent)
        self.parent = parent
        self.images = []
        self._abort = False
        self.start_pos = start_pos
        self.gotVideo.connect(self.parent.addResult)
    
    
    def run(self):
        s = SearchParams()
        s.setKeywords(self.parent.ui.searchLine.text())

        yt = YoutubeSearch()
        videos = yt.search(s, 10, self.start_pos)
       
        for video in videos:
            if self._abort: return
            
            description = "%s \nby: %s " % (video.title, video.author_name)
            
            #item = TreeWidgetItem(["" , description], video, self.parent.ui.resultsWidget)
            item = TreeWidgetItem([description], video, self.parent.ui.resultsWidget)
            
            data = self.getThumbnail(video.thumbnail)
            if data: 
                image = QImage.fromData(data)
            else:
                image = None

            self.gotVideo.emit((image, item))
        
        #item = QTreeWidgetItem(self.parent.ui.resultsWidget, ["" , self.tr("Show More")])
        item = QTreeWidgetItem(self.parent.ui.resultsWidget, [ self.tr("Show More")])
        self.gotVideo.emit((QImage(c.ICON_ADD), item))
        
        self.parent.clear_search = True
    
    def getThumbnail(self, url):
        try:
            return MATCHER.urlreader(url).content
        except ReaderError:
            print "Error while getting the thumbnail"

    def abort(self):
        self._abort = True
