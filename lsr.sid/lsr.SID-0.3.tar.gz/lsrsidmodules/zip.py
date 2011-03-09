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

import os
import tempfile
import zipfile

class ZipManager(object):
    def __init__(self, main):
        self.main = main
        
        self.convert_zip("/home/daniel/Desktop/HVSC_53-all-of-them.zip")
        
        
    def convert_zip(self, path):
        
        tmp = tempfile.mkdtemp()
        tmp2 = tempfile.mkdtemp()
        
        zip = zipfile.ZipFile(path)
        zip.extractall(tmp)
        zip.close()
        
        fl = os.listdir(tmp)[0]
        path = os.path.join(tmp, fl)
        
        if os.path.isfile(path):
            zip = zipfile.ZipFile(path)
            zip.extractall(tmp)
            zip.close()
            
            fl = os.listdir(tmp2)[0]
            path = os.path.join(tmp2, fl)
            
        zip = zipfile.ZipFile("fertig.zip", "w", zipfile.ZIP_DEFLATED)
        zip.write
