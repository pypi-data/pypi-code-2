#!/usr/bin/env python
# coding:utf-8

# lsrSID - Python HVSC browser and sidplay2 GUI.
# Copyright (C) 2010  Daniel Nögel
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3 of the License.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import os
import re
import shlex
import Queue
import time
import logging
import threading
import subprocess

import exceptions
import helpers
import sidinfo

class Job(object):
    def __init__(self, command, sid=None, subtune=None, startpos=None):
        self.command = command
        
        self.sid = sid
        self.subtune = subtune
        self.startpos =startpos

class PlaySID(threading.Thread):
    def __init__(self, main, queue):
        self.main = main
        threading.Thread.__init__(self)
        
        self.main.events.add_event("now-playing")
        self.main.events.add_event("track-over")
        self.main.events.add_event("playback-stopped")
        
        self.pipe = None
        self.queue = queue
        
        self.reset_timer()
        self.playing = False
        #~ self.current_track = None
        self.current_sid = None
        self.current_subtune = None
        #~ self.current_track_length = None
        self.hold = True
        
        self.options = {}
        
        self.error = None
        
        self.aoss_available = self.check_aoss_available()
    
    def check_aoss_available(self):
        pipe = subprocess.Popen("aoss", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if pipe.wait() == 127:
            logging.info(""""'aoss' not found
Its recommended to install the package 'alsa-oss'" as the underlying sidplayer
uses OSS for sound playback. OSS is deprecated in linux - with alsa-oss the
OSS-interface is wrapped to the ALSA-interface which is more up-to-date.""")
            return False
        else:
            logging.info("'aoss' found")
        return True
           
    def reset_timer(self):
        self.playback_start_time = 0
        #~ self._timer = 0
    def start_playing(self, startpos=None):
        self.reset_timer()
        if startpos:
            self.playback_start_time = time.time() - startpos
        else:
            self.playback_start_time = time.time()
        self.hold = False
        self.playing = True
    def stop_playing(self, hold=False):
        self.hold = hold
        self.main.events.raise_event("playback-stopped", hold)
        self.reset_timer()
        self.playing = False
        
        self.current_sid = None
        self.current_subtune = None
    
    @property
    def timer(self):
        if not self.playing:
            return None
        return time.time() - self.playback_start_time 
    #~ @property.setter
    #~ def timer(self, value)
        #~ pass
        
    def run(self):
        """main loop - runs until a quit-job is put into the queue"""
        
        while 1:
            ## Exit the loop if we get a QUIT Task
                
            try:
                #~ job = self.queue.get(block=True, timeout=1)
                job = self.queue.get(block=True, timeout=1)
            except Queue.Empty:
                #~ self.clear()
                continue
            
            if job.command == "QUIT":
                logging.info("... exiting ripper loop.")
                return
            elif job.command == "PLAY":
                print "play", job.sid.path
                self.play(job)
            
            #~ time.sleep(1)
            #~ print "waiting"
            
    def cancel_all(self):
        done = False
        while not done:
            try:
                job = self.queue.get(block=False)
            except Queue.Empty:
                done = True
        self.cancel()
    def cancel(self, hold=False):
        self.stop_playing(hold)
        if self.pipe and self.pipe.poll() is None:
            self.pipe.kill()
        
    def play(self, job):

        self.reset_timer()
        
        self.pipe = subprocess.Popen(self.get_cmd(job), shell=False, bufsize=1, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        self.start_playing(job.startpos)
        self.main.events.raise_event("now-playing", job.sid )
        
        while self.pipe.poll() is None:
            #~ t = self.pipe.stderr.read(10)
            #~ print t
            #~ hits = re.findall(r"([0-9]+:[0-9]+)", t.strip())
            #~ if hits:
                #~ print hits[-1], sidinfo.readable_time_to_seconds(hits[-1])
                #~ self.timer = sidinfo.readable_time_to_seconds(hits[-1])
                
                

            #~ t = self.timer
            #~ m, s = divmod(t, 60)
            #~ print "%02d:%02d" % (m, s)
            time.sleep(1)
        self.stop_playing()
        ## cancel
        if self.pipe.poll() == -9: return
        ## error
        if self.pipe.poll() != 0:
            #~ print "error"
            out = self.pipe.stdout.read()
            if out:
                logging.info(out)
            err = self.pipe.stderr.read()
            logging.error(err)
            if "device or resource busy" in err.lower():
                self.error = (exceptions.DeviceBusyException, err)
            else:
                self.error = (exceptions.PlaybackException, err)
        else:
            self.main.events.raise_event("track-over")
            
        
    def get_cmd(self, job):
        sid = job.sid
        fl = sid.path
        if job.subtune is None:
            subtune = sid.startsong
        else:
            subtune = job.subtune
        length = None
            
        COMMAND = "aoss padsp sidplay2 -os !!STARTPOS!! !!LENGTH!! !!TRACK!! '{file}'"
        if self.aoss_available:
            COMMAND = "{cmd}".format(cmd=COMMAND)
        if subtune:
            COMMAND = COMMAND.replace("!!TRACK!!", "-o{subtune}".format(subtune=subtune))
        else:
            COMMAND = COMMAND.replace("!!TRACK!!", "")

        try:
            time = sid.get_songlength(subtune)
        except KeyError:
            time = None
            pass
            
        self.current_sid = sid
        self.current_subtune = subtune
        
        ## If we jump to a specific start pos in the track (e.g. -b30), we
        # neet to substract this amount of seconds from the max-time
        # (-t param)
            
        if job.startpos: 
            COMMAND = COMMAND.replace("!!STARTPOS!!", "-b{startpos}".format(startpos=job.startpos))
            t = time
            t -= job.startpos
            time = sidinfo.seconds_to_readable_time(t)
        else:
            COMMAND = COMMAND.replace("!!STARTPOS!!", "".format(""))
        
            
        if length:
            COMMAND = COMMAND.replace("!!LENGTH!!", " -t{length}".format(length=length))
        else:
            if time:
                COMMAND = COMMAND.replace("!!LENGTH!!", " -t{length}".format(length=time))
            else:
                COMMAND = COMMAND.replace("!!LENGTH!!", "")
            
        COMMAND = COMMAND.format(file=fl)
        logging.info(COMMAND)
        return shlex.split(COMMAND)
