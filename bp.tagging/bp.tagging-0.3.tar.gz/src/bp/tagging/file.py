#!/usr/bin/env python2.6
# encoding: utf-8
"""
file.py

Created by disko on 2010-08-29.
Copyright (c) 2010 binary punks. All rights reserved.
"""

# IMPORTS

import exceptions
import mutagen
import mutagen.mp3
import odict
import preferences
import table


# CONFIGURATION

MP3MODES    = ["stereo", "jointstereo", "dualchannel", "mono", ]
PREFS       = preferences.Preferences()

# IMPLEMENTATION

class File(object):
    """Wrapper for multimedia files with embedded metadata"""
    
    def __init__(self, f=None, fname=None):
        """File constructor method.
        
        :param f:     an object returned by mutagen.File (with easy option enabled)
        :param fname: a valid filesystem path
        """
        
        if ((f is None) and (fname is None)) or (f and fname):
            raise exceptions.ValueError("Either f or fname must be given (but not both).")
        
        if fname:
            f = mutagen.File(fname, easy=True)
        else:
            fname = f.filename
        
        self.f      = f
        self.fname  = fname
    
    
    @property
    def file_extension(self):
        """return the file extension"""
        
        return self.fname.split(".")[-1]
    
    
    @property
    def filename_from_tags(self):
        """compute a (new) filename from available ID3 tags.
        
        the preference values for id3_to_filename_tags and id3_to_filename_separator are used.
        """
        
        tags        = PREFS.id3_to_filename_tags
        separator   = PREFS.id3_to_filename_separator
        filename_parts = [self.getTag(tag) for tag in tags if self.getTag(tag) is not None]
        
        return ".".join((separator.join(filename_parts), self.file_extension))
    
    
    def getTag(self, tag):
        """return the current value for the given tag (or None if the tag does not exist)"""
        
        try:
            return self.tags[tag]
        except KeyError:
            return None
    
    
    @property
    def info(self):
        """return a dictionary containing stream information (length, bitrate, sample rate)"""
        
        info = odict.odict()
        
        if type(self.f.info) == mutagen.mp3.MPEGInfo:
            
            info['bitrate']     = self.f.info.bitrate
            #info['sketchy']     = self.f.info.sketchy
            
            info['version']     = self.f.info.version
            #info['layer']       = self.f.info.layer
            #info['protected']   = self.f.info.protected
            #info['padding']     = self.f.info.padding
            info['sample_rate'] = self.f.info.sample_rate
            
            info['mode']        = MP3MODES[self.f.info.mode]
        
        info.sort(key=lambda x: x[0])
        
        return info
    
    
    @property
    def mime(self):
        """return a list of MIME types"""
        
        return self.f.mime
    
    
    def pprint(self, show_filename=True, show_fileinfo=True, show_filetags=True):
        """print an ASCII table containing available metadata information"""
        
        t = table.MetadataTable(self, show_filename=show_filename, show_fileinfo=show_fileinfo, show_filetags=show_filetags)
        
        print "\n", t.draw(), "\n"
    
    
    def save(self):
        """save the modified file"""
        
        self.f.save()
    
    
    def setTag(self, tag, value):
        """set the value for the given tag"""
        
        value = self.f[tag] = [value,]
        return None
    
    
    @property
    def tags(self):
        """return a dictionary containing human readable tag name/value pairs of type unicode string"""
        
        tags = odict.odict()
        
        if self.f is not None:
            for k in self.f.keys():
                try:
                    if k.find("serato") == -1:
                        tags[k] = u", ".join(self.f[k])
                except mutagen.easyid3.EasyID3KeyError, e:
                    print "Exception", e
            
            tags.sort(key=lambda x: x[0])
        
        return tags
    
    
    @property
    def valid_keys(self):
        """return a list of tag keys that are valid for the file"""
        
        vk = self.f.tags.valid_keys.keys()
        vk.sort()
        
        return vk
    


