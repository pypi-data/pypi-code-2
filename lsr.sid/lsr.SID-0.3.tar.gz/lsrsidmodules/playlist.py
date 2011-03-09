#!/usr/bin/env python
# coding:utf-8

import re

header = """; This Playlist was generated with lsR.sid
; HVSC Browser
; http://launchpad.net/lsr.sid
;
; You have to set the Basedir
; of your HVSC Collection

[SIDPLAY/Playlist]
Format=2
Order=Normal
Basedir={basedir}
Repeat=No
"""

template = """
file={path}
hash={hash}
name={title}
author={author}
copyright={copyright}
songs={songs}
subtune={subtune}
time={time}
"""


AUTO_MODE = -1
HASH_MODE = 0
PATH_MODE = 1

def read_playlist(path, mode=AUTO_MODE):
    with open(path, "r") as fh:
        content = fh.read()
        
        ## Matches hashes ans Paths
        #~ rg = re.compile(r"file=(.*)[\s\w]*hash=(.*)[^\n\n]", re.MULTILINE)
        
        ## Matches Files
        rg_file = re.compile(r"file=(.*)")
        file_list = rg_file.findall(content)
        ## Matches Hashes
        rg_hash = re.compile(r"hash=(.*)")
        hash_list = rg_hash.findall(content)
        
        if (mode == AUTO_MODE and hash_list) or mode == HASH_MODE:
            return HASH_MODE, hash_list
        else:
            return PATH_MODE, file_list
            
        
        return 
    
def write_playlist(data, path, basedir):
    with open(path, "w") as fh:
        fh.write(header.format(basedir=basedir))
        
        for sid in data:
            fh.write(
                template.format(
                    path = sid.path.replace(basedir, ""),
                    hash = sid.hash, 
                    title = sid.title,
                    author = sid.artist,
                    copyright = sid.copyright,
                    songs = sid.subsongs,
                    subtune = sid.startsong,
                    time = sid.get_songlength(sid.startsong),
                    
                )
            )
    

    
