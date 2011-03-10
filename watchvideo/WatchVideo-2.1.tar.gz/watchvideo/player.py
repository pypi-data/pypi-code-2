#!/usr/bin/env python
# -*- coding: utf-8 -*- #

import os
import sys
import tempfile
from subprocess import Popen, PIPE, STDOUT

from watchvideo.qt import QtGui
import watchvideo.vlc as vlc
from watchvideo.qt import QtCore
from watchvideo.slider import Slider
from watchvideo.qt.QtCore import Qt
import watchvideo.constants as c
import watchvideo.gui_utils as gui_utils


class Player(object):
    def __init__(self, parent):
        self.parent = parent
        self.slider = Slider(Qt.Horizontal, parent)
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
        self.download_shared = False
        self.stopped = False
        
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
        
        #buttons
        self.parent.ui.btn_play.clicked.connect(self.play)
        self.parent.ui.btn_pause.clicked.connect(self.pause)
        self.parent.ui.btn_stop.clicked.connect(self.stop)
        
    
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
            self.check_playback_timer.start(1000)
            

            
        
        self.MediaPlayer.play()
        self.slider.start()
        self.playing = True
        self.paused = self.stopped = False
        self.completed = False
        self.parent.ui.stackedWidget.setCurrentIndex(1) #set pause button
        self.parent.ui.stackedWidget.setEnabled(True)
        
    def pause(self, checked, en_widget=True):
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
        if self.repeat:
          self.play()
        
    def stop(self):
        if self.download.completed or self.download.aborted:
            answer = QtGui.QMessageBox.Yes
        else:
            answer = gui_utils.confirm(self.parent, "Abort Download", "This will abort the download too, are you sure?")
   
        if answer == QtGui.QMessageBox.Yes:
            self.stopped = True
            self.reset()

    def restart(self):
        print "reloading file...."
        self.completed = True
        self.play()
        
        
    def loadfile(self, filepath, download):
        self.reset() #reset everything
        
        self.parent.ui.stackedWidget.setEnabled(False)
        
        
        self.filepath = tempfile.gettempdir() + "/" + os.path.split(filepath)[1]
        self.filename = os.path.split(filepath)[1]
        self.download = download
        self.download.dest_file = self.filepath
        self.download.start()

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
        if not os.path.exists(self.filepath): return
        
        if not self.timer_update_progressbar.isActive():
            self.timer_update_progressbar.start(1000)
        
        filesize = os.path.getsize(self.filepath)
        if filesize < 4096: return #4096 bytes minimum (random) to check for info in the file
        
        if not self.total_duration or not self.bitrate:
            self.total_duration = self.get_duration(self.filepath)
            self.bitrate = self.get_bitrate(self.filepath)
            return
        elif (self.current_max_time() / float(self.total_duration)) * 100 < 10:
            #load at least 10% of the video before start playing
            return
            
        self.timer_load_file.stop()
        
        self.completed = False
        
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
        self.slider.loadfile(self.filepath)
        self.slider.setMaximum(1000)
        self.slider.progress_max = 1000
        
        #update buttons' state
        self.parent.ui.stackedWidget.setEnabled(True)
        self.parent.ui.stackedWidget.setCurrentIndex(1)
        self.parent.ui.btn_stop.setEnabled(True)
        
        self.check_playback_timer.start(1000)
        
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
            
        if self.download.completed: return
        
        self.slider.max = self.current_max_time() * 1000 / self.total_duration
        
        if self.MediaPlayer.get_position() * 1000  > self.slider.max:
            self.pause(False, en_widget=False)
            self.wait_timer.start(self.wait_time * 1000)
            self.wait_time += 2
            
            
    def update_progressbar(self):
        self.slider.progress = self.download.downloaded * 1000 / self.download.size_kib

        if self.download.completed:
            self.slider.max = 1000
            #hack to set the progressbar at 100%
            #self.progressbar.setValue(self.download.size_kib)
            self.slider.progress = self.slider.progress_max
            #stop checking, it's done!
            self.timer_update_progressbar.stop()
    
    def reset(self):
        self.parent.ui.videoWidget.setStyleSheet("background-color: rgb(0, 0, 0);")
        self.parent.ui.stackedWidget.setCurrentIndex(0) #show play button
        self.parent.ui.btn_stop.setEnabled(False)
    
        if self.download:            
            if not self.download.completed:
                if not self.download_shared:
                    self.download.abort()
                                 
                if self.timer_update_progressbar.isActive(): 
                    self.timer_update_progressbar.stop()
            
            
            if self.timer_load_file.isActive(): 
                self.timer_load_file.stop()
            if self.check_playback_timer.isActive(): 
                self.check_playback_timer.stop()
            
            #could be playing from complete or incomplete file
            if self.isPlaying(): self.MediaPlayer.stop()
                   
            self.slider.reset()
            self.playing = False

    def get_duration(self, filepath):
        #return duration in seconds
        process = Popen(("ffmpeg", "-i", str(filepath)),stdout=PIPE,
                stdin=PIPE,stderr=STDOUT)

        output = process.communicate()[0]
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

        output = process.communicate()[0]
        bitrate = None
        
        for line in output.splitlines():
            if "bitrate:" in line:
                bitrate = line.split("bitrate:")[1].split(" ")[1]
                if bitrate == "N/A": 
                    bitrate = None
                else:
                    bitrate = int(bitrate) * 1024 / 8
                    
                print "bitrate: ", bitrate
                return bitrate
                
        
    def isActive(self):
        return self.MediaPlayer.is_playing() or self.paused or self.isDownloadActive()
        
    def isDownloadActive(self):
        if self.download and not self.download.completed:
            return not self.download.aborted
        
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
        self.download_shared = True
        return self.download
    

    

