#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''Watchvideo base - contains download, play and match functions 
shared by the GUI and CLI.
'''
# Copyright (C) 2010, 2011  Michał Masłowski  <mtjm@mtjm.eu>
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

import sys
import os
from subprocess import Popen, PIPE, STDOUT
from ConfigParser import SafeConfigParser
from getmediumurl import Matcher

import watchvideo.constants as c


#: An instance of :class:`getmediumurl.Matcher` used by WatchVideo.
MATCHER = Matcher()

class Match(object):
    def __init__(self, urls, quality="custom", fast=False):
        self.urls = urls
        self.url = None
        self.title = "Unknown"
        self._stop = False
        self.done = False
        self.invalid_urls = []
        self.mediums = {}
        self.ready_mediums = {}
        self.fast = fast
        self.parser = None
        self.quality = quality #by default it's "custom"
        self.quality_string = ["ask", "low", "high"]
        self.update_settings = False
        
        if c.HAS_CONFIG_FILE:
            self.parser = SafeConfigParser()
            self.parser.read(c.CONFIG_FILE)
            if not self.parser.has_section("VideoQuality"): 
                self.parser.add_section("VideoQuality")


    def match(self):
        '''Matching regexps
         @urls: a list with the urls or just a string with one url
         @down: boolean to specify if it's to download or play directly
         @valid_videos: returns a list of VideoInfo objects.
         @invalid_urls: returns a list with the invalid urls
         '''
        
        if isinstance(self.urls, basestring):
            self.urls = (self.urls,)

        
        for url in self.urls:
            if self._stop: break
            self.url = url
            
            try:
                plugin = MATCHER.match(url, fast=self.fast)
            except:
                plugin = None

            if plugin is None: 
                self.invalid_urls.append(url)
                continue
            
            for medium in plugin:
                if self.parser and not self.parser.has_option("VideoQuality", medium.website):
                    self.update_settings = True
                    self.parser.set("VideoQuality", medium.website, "0")
                
                try:
                    formats = list(medium)
                except:
                    self.invalid_urls.append(url)
                    continue
                    
                if len(formats) == 1:
                    self.ready_mediums[medium] = formats[0]
                    continue
                
                quality = self.quality
                
                if self.quality == "custom" and self.parser:
                    if self.parser.has_option("VideoQuality", medium.website):
                        opt = int(self.parser.get("VideoQuality", medium.website))
                        quality = self.quality_string[opt]
                    else:
                        quality = "ask"
                            
                if quality == "ask":
                    self.mediums[medium] = formats
                elif quality == "low":
                    self.ready_mediums[medium] = min(formats)
                elif quality == "high":
                    self.ready_mediums[medium] = max(formats)
        
                
        if self.update_settings:
            with open(c.CONFIG_FILE, "w") as configfile:
                self.parser.write(configfile)
            
        self.done = True

    def stop(self):
        self._stop = True
        

def describe_format(mformat):
    """Return *mformat* as human-readable string."""
    text = ""
    if mformat.width is not None and mformat.height is not None:
        text = "%dx%d" % (mformat.width, mformat.height)
    if mformat.mime_type:
        if text:
            text += " "
        text += mformat.mime_type
    return text




def download(url, title=None):
    '''Downloads file from a given url. 
    Currently is only used by the cli version. The download function for the GUI 
    is in the threads.py and uses almost the same code.
    ToDo: GUI and CLI should use the same download function
    '''
    try:
        if title is None: title = "video"
        title = get_new_file(".", title)
        
        remote_file = c.OPENER.open(url)
        local_file = open(title, 'wb')
        local_size = 0.0
        remote_size = int(remote_file.info()['content-length'])
        remote_size_kb = remote_size // 1024
        print '\r'
        while local_size < remote_size:
            percent = 100 * local_size / remote_size
            complete = ''.join(['=' * (int(percent) // 2)])
            joint = ''.join([' ' * (50 - len(complete))])
            sys.stdout.write('\r%6d/%d KiB [ %05.2f%%]|%s%s|'
            % (local_size // 1024, remote_size_kb, float(percent),\
            complete, joint))
            buffering = remote_file.read(4096)
            local_file.write(buffering)
            local_size += len(buffering)
            sys.stdout.flush()
        sys.stdout.flush()
        remote_file.close()
        local_file.close()
        equals = '=' * 50
        sys.stdout.write('\r%6d/%d KiB [100.00%%]|%s|\n'
        % (remote_size_kb, remote_size_kb, equals))
        print '\r'
    except KeyboardInterrupt:
        if os.path.exists(title):
            os.remove(title)
        print '\r'
        sys.exit()

_DEFAULT_PLAYER = None

def get_default_player():
    global _DEFAULT_PLAYER
    if _DEFAULT_PLAYER is not None:
        return _DEFAULT_PLAYER
    for m in ('video/avi', 'video/mp4', 'video/flv'):
        player = Popen(("xdg-mime", "query", "default", m),
                       stdout = PIPE).communicate()[0].decode("ascii") \
                       .split('.')[0]
        if player:  #if a player was found, exit
            if player == "dragonplayer": player = "dragon" #hack
            _DEFAULT_PLAYER = player
            return player
    _DEFAULT_PLAYER = "vlc"
    return "vlc"  # if no other player found

def play(url, title, player=None):
    '''Play'''
    if player is None:
        player = get_default_player()
    
    print "Playing %s" % title
    option = ""
    try:
        if os.name == "nt": 
            os.filestart(url)
            
        elif os.name == "posix":
            if "http://" not in url: #if it's not an url
                if not os.path.exists(url): #if it's not a file
                    print "Not a valid URL or file"
                    raise KeyboardInterrupt
                else:
                    url = url.replace('"', '\"')

            if not player:
                print "Player not found!"
                raise KeyboardInterrupt
            
            if player == "totem": option = "--enqueue"
            
            Popen((player, option, url))
    except KeyboardInterrupt:
        print '\r'
        sys.exit()

def get_new_file(folder, name):
    """Checks if the folder+name is valid and if it's not adds a number
    tag to not overwrite existing files"""
    
    if folder == "." or not os.path.exists(folder):
        folder = os.getcwd()

    if os.sep in name:
        name = name.replace(os.sep, "-")
        
    filepath = os.path.join(folder, name)
    
    for i in xrange(1, 30):
        if not os.path.exists(filepath):
            break
        
        if "_00" in filepath[-4:-1]:
            filepath = " ".join(filepath.split('_')[:-1])

        filepath += "_00" + str(i)

    return filepath
    
def file_exists(folder, name):
    return os.path.exists(os.path.join(folder, name))
    
    
def get_file_info(filepath):
    process = Popen(("ffmpeg", "-i", filepath),stdout=PIPE,
            stdin=PIPE,stderr=STDOUT)
    output = process.communicate()[0]

    for line in output.split('\n'):
        if "Audio:" in line:
            audio = line.split("Audio:")[1].split(',')
            audio = [ a.strip() for a in audio ]
        elif "Video:" in line:
            video = line.split("Video:")[1].split(',')
            video = [ v.strip() for v in video ]
            
    return video, audio

def rip(filepath, remove_original=True):
    '''Extracts the audio from the video'''
    if not c.HAS_FFMPEG:
        print '''You need to install 'ffmpeg' in order to extract the audio'''
        return False

    video, audio = get_file_info(filepath)
    if audio is None: return False
    
    #remove the extension from the video's name, if it exists
    video_ext = filepath.split('.')[-1]
    if video_ext == video[0]:
        filepath_name = ".".join(filepath.split('.')[:-1])
    else:
        filepath_name = filepath
        
    filepath = filepath.replace('"', '\\"')
    
    ext = audio[0]
        
    output = Popen(("ffmpeg", "-y", "-i", filepath, "-vn",
                    "-acodec", "copy", "%s.%s" % (filepath_name, ext)),
                   stdout=PIPE, stderr=PIPE)
    output.communicate()

    if output.returncode == 0:
        if remove_original: os.remove(filepath) #remove the original video
        return True
    
    return False
    
def convert(filepath, audio_only=True, remove_original=True):
    '''Converts video file to Ogg Vorbis (audio) or Theora (video)'''
    if not c.HAS_FFMPEG:
        print '''You need to install 'ffmpeg' in order to extract information 
	about the video'''
        return False
    
    if not c.HAS_FFMPEG2THEORA:
        print '''You need to install 'ffmpeg2theora' in order to convert \
            videos to the Ogg Vorbis or Theora formats.'''
        return False
    
    filepath_name = filepath.split('.')[0]
    
    print filepath
    video, audio = get_file_info(filepath)
    if audio is None: return False
    
    #remove the extension from the video's name, if it exists
    video_ext = filepath.split('.')[-1]
    if video_ext == video[0]:
        filepath_name = ".".join(filepath.split('.')[:-1])
    else:
        filepath_name = filepath
    
    filepath = filepath.replace('"', '\\"')

    args = ["ffmpeg2theora"]

    try:
        audiobitrate = audio[4].strip(" kb/s")
    except IndexError:
        audiobitrate = ""
    else:
        if int(audiobitrate) >= 10:
            args.extend(("--audiobitrate", audiobitrate))
            
    args.append("--no-skeleton")

    if audio_only:
        name_pattern = "%s.oga"
        args.append("--novideo")
    else:
        name_pattern = "%s.ogv"

    args.extend((filepath, "-o", name_pattern % filepath_name))

    process = Popen(args, stdout=PIPE, stderr=PIPE)
    process.communicate()
    
    if process.returncode == 0: 
        if remove_original: os.remove(filepath)
        return True
    
    return False
    
