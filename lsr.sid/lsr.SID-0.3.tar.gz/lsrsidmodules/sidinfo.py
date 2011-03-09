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

import re
import os
import hashlib

## Constants
HEADER_SIZE_V1 = 118
HEADER_SIZE_V2 = 124
LOAD_ADDRESS_SIZE = 2

CIA_SPEED       = 60
VBL_SPPED       = 0
NTSC_CLOCK      = 2


def get_infos(path):
    """Returns a dict with information about a given sid-file.
    
    
    """
    ##22 54 86
    info = {}
    with open(path, "rb") as fh:
        content = fh.read()
        info['type'] = unicode(content[:4].decode("iso8859-1"))
        info['version'] = ord(content[5])
        info['subsongs'] = ord(content[15])
        info['startsong'] = ord(content[17])
        info['title'] = unicode(content[22:54].strip(chr(0)).decode("iso8859-1"))
        info['artist'] = unicode(content[54:86].strip(chr(0)).decode("iso8859-1"))
        info['copyright'] = unicode(content[86:118].strip(chr(0)).decode("iso8859-1"))
        info['size'] = os.path.getsize(path)
        info['hash'] = get_md5_hash(None, content)
    return info

def seconds_to_readable_time(s):
    """Returns a human readable time string (mm:ss)"""
    
    m, s = divmod(s, 60)
    return "%02d:%02d" % (m, s)

def readable_time_to_seconds(s):
    
    """Takes a time string like "01:30" and returns seconds"""
    m, s = s.split(":")
    s = int(s) + int(m)*60
    
    return s
    
def get_md5_hash(path, content=None):
    """Returns a md5 hash of a given SID file.
    
    This hash is compatible to the Songlength Database which md5-hashes
    are calculated in a specific way!
    
    If content is given, path will be ignored."""
        
    is_ntsc = False
    is_psid_specific = False
    
    if not content:
        with open(path, "rb") as fh:
            content = fh.read()
    
    md = hashlib.md5()
    
    dataoffset = ord(content[6])<<8 | ord(content[7])
    loadaddress = ord(content[8])<<8 | ord(content[9])
    numsongs = ord(content[14])<<8 | ord(content[15])
    
    IS_RSID = content[:4] == "RSID"
    
    if not IS_RSID:
        speed =  ord(content[18])<<24 | ord(content[19])<<16 | ord(content[20])<<8 | ord(content[21]);
    else:
        speed = 4294967295
    
    if dataoffset == HEADER_SIZE_V2:
        is_ntsc = (ord(content[119])&12) == 8
        if not IS_RSID:
            is_psid_specific = (ord(content[119])&2) > 0
    elif dataoffset != HEADER_SIZE_V1:
            raise Exception("Wrong Header Size")
    
    # loadAddress = 0  -> loadAddress is in front of the data
    # loadAddress > 0  -> loadAddress is in header
    if loadaddress == 0:
        dataoffset += LOAD_ADDRESS_SIZE
    
    # hash sid data (without load address)
    md.update(content[dataoffset:])
    
    md.update(content[11])
    md.update(content[10])
    md.update(content[13])
    md.update(content[12])
    md.update(content[15])
    md.update(content[14])
    
    for i in range(0, numsongs):
        if not is_psid_specific:
            if i < 31:
                VbiSpeed = not(speed & (1<<i))
            else:
                VbiSpeed = not(speed & (1<<31))
        else:
            VbiSpeed = not(speed & (1<<(i%32)))
            
        if VbiSpeed:
            md.update(chr(VBL_SPPED))
        else:
            md.update(chr(CIA_SPEED))
    
    if is_ntsc:
        md.update(chr(NTSC_CLOCK))
    
    #~ print "Infos:"
    #~ print "PSID: ", not IS_RSID
    #~ print "NTSC: ", is_ntsc
    #~ print "Speed: ", speed
    #~ print "Songs: ", numsongs
    
    return unicode(md.hexdigest())
    

def recursive_read_directory(basedir, songlength_database, num=1000):
    """Reads a directory recursively and returns a list with all the 
    sids in it.
    
    Needs a instance of the songlength database
    """
    sids = []
    
    for root, dirs, files in os.walk(unicode(basedir), topdown=True):
        for file in sorted(files):
            if file.lower().endswith(".sid"):
                p = os.path.join(root, file)
                info = get_infos(p)
                info["path"] = p
                
                times = songlength_database.query_path(p)

                t = [str(readable_time_to_seconds(t[0])) for t in times]
                info["times"] = u",".join(t)
                
                p = p.replace(basedir, "")
                info["path"] = p
                info["hash"] = get_md5_hash(os.path.join(basedir, p.lstrip("/")))
                
                sids.append(info)
                
                if len(sids) >= num:
                    yield sids
                    sids = []
    
    if sids:
        yield sids
    
    #~ return sids
                

class SongLengthDatabase(object):   
    """Parses the songlength database and gives access to it"""

    def __init__(self, path):
        """Path: The path to the songlength.txt file"""
        
        self.basedir = path
        
        if self.basedir:
            self._load_database()
    
    def _load_database(self):        
        self.db = os.path.join(self.basedir, "DOCUMENTS", "Songlengths.txt")
        
        self.db_available = os.path.exists(self.db)
        
        
        self.db_path = {}
        self.db_hash = {}
        if self.db_available:
            with open(self.db, "r") as fh:
                content = unicode(fh.read())
                rg = re.compile(ur"; (?P<path>[^\s]*)\s*(?P<hash>[A-Za-z0-9]*)=(.*)\s?", re.MULTILINE)
                hits = rg.findall(content)
                for hit in hits:
                    times = re.findall(ur"([0-9:]+)\(?([A-Z]?)\)?", hit[2])
                    self.db_path[hit[0]] = times
                    self.db_hash[hit[1]] = times

    def query_path(self, path):
        """Returns the songlengths of a given SID file
        
        Its recommended to use the query_hash-function as the path
        of the SIDs might change from time to time"""
        
        
        ## Get a valid SLDB-path
        path = path.replace(self.basedir, "")
        
        try:
            return self.db_path[path]
        except KeyError:
            ## FIXME
            return [(u"2:00", u"")]*50
        
    def query_hash(self, hash):
        """Returns the songlengths of a SID file. This SID file is 
        identified via its MD5 hash.
        
        Warning: You need to use get_md5_hash() or get_infos() in order
        to get a proper MD5 hash of the sid!
        """
        try:
            return self.db_hash[hash]
        except KeyError:
            ## FIXME
            return [(u"2:00", u"")]*50

