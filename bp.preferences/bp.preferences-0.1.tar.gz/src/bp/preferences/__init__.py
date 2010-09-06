#!/usr/bin/env python
# encoding: utf-8
"""
preferences.py

Created by Andreas Kaiser on 2010-09-04.
Copyright (c) 2010 Xo7 GmbH. All rights reserved.
"""

# IMPORTS

import os
import os.path
import Preferences as Base
import unittest


# IMPLEMENTATION

class Preferences(Base.Preferences):
    """bp.preferences"""
    
    def __init__(self, filename):
        
        self.filename = filename
        self.load_files()
    
    
    def _toString(self, value):
        """Converts a string enclosed with single or double quotes to a Python string without quotes.
        This is needed e.g. to support preference values with leading/trailing whitespace characters."""
        
        return value.replace("'", "").replace('"', '')
    
    
    def load_files(self):
        """
        Preferences are loaded in this order:
            
            -   package_location/file_name.cfg  (contains default preferences)
            -   /etc/file_name
            -   ~/.file_name
            -   current_working_direcory/file_name
        
        """
        
        paths = [
            os.path.join(os.path.dirname(__file__), '%s.cfg' % self.filename),
            os.path.join('/etc',                    self.filename),
            os.path.join(os.path.expanduser('~'),   '.%s' % self.filename),
            os.path.join(os.getcwd(),               self.filename),
        ]
        
        for path in paths:
            if os.path.isfile(path):
                self.read_file(path)
        
    
    

# TESTS

class preferencesTests(unittest.TestCase):
    
    def setUp(self):
        self.p = Preferences("bp.preferences")
    
    
    def testDefaults(self):
        self.p.dump()
    
    def tearDown(self):
        pass
    

if __name__ == '__main__':
    unittest.main()
