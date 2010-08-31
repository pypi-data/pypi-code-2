#!/usr/bin/env python2.6
# encoding: utf-8
"""
table.py

Created by disko on 2010-08-28.
Copyright (c) 2010 binary punks. All rights reserved.
"""

# IMPORTS

import texttable


# IMPLEMENTATION

class MetadataTable(texttable.Texttable):
    """Table for displaying a file's metadata"""
    
    def __init__(self, f, show_filename=True, show_fileinfo=True, show_filetags=True):
        """MetadataTable constructor"""
        
        texttable.Texttable.__init__(self, max_width=0)
        
        self.set_deco(False)
        self.set_cols_align(("r", "l"))
        
        if show_filename and f.fname:
            self.add_row(("filename", f.fname))
        
        if show_fileinfo:
            
            if show_filename:
                self.add_row(("", "-"))
            
            for r in f.info.iteritems():
                self.add_row(r)
            
        
        if show_filetags:
            
            if show_filename or show_fileinfo:
                self.add_row(("", "-"))
            
            for r in f.tags.iteritems():
                self.add_row(r)
            
        
    

