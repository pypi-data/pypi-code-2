#!/usr/bin/env python
# encoding: utf-8
"""
preferences.py

Created by Andreas Kaiser on 2010-09-04.
Copyright (c) 2010 Xo7 GmbH. All rights reserved.
"""

# IMPORTS

import bp.preferences
import unittest

# CONFIGURATION

FILENAME    = "bp.tagging"


# IMPLEMENTATION

class Preferences(bp.preferences.Preferences):
    """bp.tagging Preferences"""
    
    _module_path = __file__
    
    def __init__(self):
        
        bp.preferences.Preferences.__init__(self, FILENAME)
    
    
    @property
    def id3_to_filename_tags(self):
        """preference value (converted to list)"""
        
        return self.get("id3_to_filename_tags").replace(" ", "").split(",")
    
    
    @property
    def id3_to_filename_separator(self):
        
        return self._toString(self.get("id3_to_filename_separator"))
    

# TESTS

class preferencesTests(unittest.TestCase):
    
    # NB: at least some tests will fail with non default preferences
    
    def setUp(self):
        self.p = Preferences()
    
    
    def test_dump(self):
        self.p.dump()
    
    def test_id3_to_filename_tags(self):
        self.assertEquals(self.p.id3_to_filename_tags, ["artist","title","version"])
    
    def test_id3_to_filename_separator(self):
        self.assertEquals(self.p.id3_to_filename_separator, " - ")
    
    
    def tearDown(self):
        pass
    

if __name__ == '__main__':
    unittest.main()
