#!/usr/bin/env python
# -*- coding: utf-8 -*- #
'''Watchvideo base - contains download, play and match functions 
shared by the GUI and CLI.
'''
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

import sys
import os
from subprocess import Popen, PIPE, STDOUT

from getmediumurl import Matcher

import watchvideo.constants as c


#: An instance of :class:`getmediumurl.Matcher` used by WatchVideo.
MATCHER = Matcher()

class Match(object):
    def __init__(self, urls, quality_options={}, fast=False):
        self.urls = urls
        self.url = None
        self.title = "Unknown"
        self.stop = False
        self.done = False
        self.valid_videos = []
        self.invalid_urls = []
        #stores an index (1-High quality; 0-Low/Noraml quality)
        self.quality_options = quality_options 
        self.fast = fast

    def match(self):
        '''Matching regexps
         @urls: a list with the urls or just a string with one url
         @down: boolean to specify if it's to download or play directly
         @valid_videos: returns a list of VideoInfo objects.
         @invalid_urls: returns a list with the invalid urls
         '''

        from watchvideo.video_info import VideoInfo
        
        if isinstance(self.urls, basestring):
            self.urls = (self.urls,)
            
        for url in self.urls:
            if self.stop: break
            high_quality = False
            self.url = url
            plugin = MATCHER.match(url, fast=self.fast)
            
            if plugin is None: 
                self.invalid_urls.append(url)
                continue
            
            if plugin.__class__.__name__ in self.quality_options:
                if self.quality_options[plugin.__class__.__name__] == 1:
                    high_quality = True

            dl_url = plugin.get_file_url(high_quality)
            if dl_url:
                title = plugin.title
                if title is None: title = "Title Not Found"
                self.valid_videos.append(VideoInfo(title, url, dl_url))
            
        self.done = True

def download(url, title=None):
    '''Downloads file from a given url. 
    Currently is only used by the cli version. The download function for the GUI 
    is in the threads.py and uses almost the same code.
    ToDo: GUI and CLI should use the same download function
    '''
    try:
        if title is None: title = "video"
        if os.path.exists(title):
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
            local_size += 4096
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
                       stdout = PIPE).stdout.read().decode("ascii") \
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
            
            Popen((player, url))
    except KeyboardInterrupt:
        print '\r'
        sys.exit()

def get_new_file(folder, name):
    """Checks if the folder+name is valid and if it's not adds a number
    tag to not overwrite existing files"""
    
    filepath = os.path.join(folder, name)
    
    for i in xrange(1, 30):
        if not os.path.exists(filepath):
            break
        
        if "_00" in filepath[-4:-1]:
            filepath = " ".join(filepath.split('_')[:-1])

        filepath += "_00" + str(i)
    
    return filepath
    
def check_if_file_exists(folder, name):
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
    
