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
import table


# CONFIGURATION

MP3MODES = ["stereo", "jointstereo", "dualchannel", "mono", ]


# IMPLEMENTATION

class File(object):
    """Wrapper for multimedia files with embedded metadata"""
    
    def __init__(self, f=None, fname=None):
        """File constructor method.
        
        :param f:     an object returned by mutagen.File (with easy option enabled)
        :param fname: a valid filesystem path
        """
        
        if ((f is None) and (fname is None)) or (f and fname):
            raise exeptions.ValueError("Either f or fname must be given (but not both).")
        
        if fname:
            f = mutagen.File(fname, easy=True)
        else:
            fname = f.filename
        
        self.f      = f
        self.fname  = fname
    
    @property
    def mime(self):
        """return a list of MIME types"""
        
        return self.f.mime
    
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
    def tags(self):
        """return a dictionary containing human readable tag name/value pairs of type unicode string"""
        
        tags = odict.odict()
        
        for k in self.f.keys():
            tags[k] = u", ".join(self.f[k])
        
        tags.sort(key=lambda x: x[0])
        
        return tags
    
    def pprint(self, show_filename=True, show_fileinfo=True, show_filetags=True):
        """print an ASCII table containing available metadata information"""
        
        t = table.MetadataTable(self, show_filename=show_filename, show_fileinfo=show_fileinfo, show_filetags=show_filetags)
        
        print "\n", t.draw(), "\n"
    


