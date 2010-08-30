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

class Table(texttable.Texttable):
    """Table for displaying rename operations (old filename => new filename)"""
    
    def __init__(self, rows):
        
        texttable.Texttable.__init__(self, max_width=0)
        
        self.set_deco(self.HEADER)
        self.header(("current filename", "=>", "new filename"))
        self.set_cols_align(("l", "c", "l"))
        
        for row in rows:
            self.add_row((row[0], "=>", row[1]))
        
    

