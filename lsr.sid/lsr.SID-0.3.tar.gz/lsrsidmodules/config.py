#!/usr/bin/env python
# -*- coding: utf-8 -*-

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

import operator
import configobj
import os
import logging
import shutil
import distutils

import helpers

class Config(object):
    def __init__(self):

        ## stores the config file URI
        self.home_config = os.path.join(helpers.get_config_dir(), "lsrsid.cfg")
        
        if not os.path.exists(helpers.get_config_dir()):
            try:
                distutils.dir_util.mkpath(helpers.get_config_dir())        
            except Exception, inst:
                logging.error(inst)
        
        if not os.path.exists(self.home_config):
            with open(self.home_config, "w") as fh:
                fh.write(DEFAULT)    

        self.config = configobj.ConfigObj(self.home_config)
        
    def get_value(self, section, option, default=None, func=None):
        if not section in self.config: 
            logging.debug ("No section '%s:%s': returning default value (%s)" % (section, option, str(default)))
            if func is None:
                return default
            else:
                return func(default)
        if not option in self.config[section]: 
            logging.debug ("No option '%s:%s': returning default value (%s)" % (section, option, str(default)))
            if func is None:
                return default
            else:
                return func(default)
        value = self.config[section][option]
        if value.isdigit():
            ret = int(value)
        elif (self.isbool(value)):
            ret = self.parsebool(value)
        else:
            ret = value

        if func is None:
            return ret
        else:
            return func(ret)
            
    def get_value2(self, section, subsection, option, default=None, func=None):
        if not section in self.config: 
            logging.debug ("No section '%s::%s:%s': returning default value (%s)" % (section, subsection, option, str(default)))
            if func is None:
                return default
            else:
                return func(default)
        if not subsection in self.config[section]: 
            logging.debug ("No subsection '%s:%s:%s': returning default value (%s)" % (section, subsection, option, str(default)))
            if func is None:
                return default
            else:
                return func(default)                
        if not option in self.config[section][subsection]: 
            logging.debug ("No option '%s:%s:%s': returning default value (%s)" % (section, subsection, option, str(default)))
            if func is None:
                return default
            else:
                return func(default)
        value = self.config[section][subsection][option]
        if value.isdigit():
            ret = int(value)
        elif (self.isbool(value)):
            ret = self.parsebool(value)
        else:
            ret = value

        if func is None:
            return ret
        else:
            return func(ret)            

    def set_value2(self, section, subsection, option, value, func=None):
        if not section in self.config:
            self.config[section] = {}
        if not subsection in self.config[section]:
            self.config[section][subsection] = {}
        if func is not None:
            self.config[section][subsection][option] = str(func(value))
        else:
            self.config[section][subsection][option] = str(value)
        self.config.write()    
            
    def set_value(self, section, option, value, func=None):
        if not section in self.config:
            self.config[section] = {}
        if func is not None:
            self.config[section][option] = str(func(value))
        else:
            self.config[section][option] = str(value)
        self.config.write()
    
    def isfloat(self, f):
        if not operator.isNumberType(f):
            return False
        if f % 1: 
            return True
        else: 
            return False

    def isbool(self, string):
        if string.upper() == "TRUE" or string.upper() == "FALSE":
            return True
        return False

    def parsebool(self, string):
        return string[0].upper()=="T"    
        
        
# This default config file will be written to disk, if no other config
# file can be found        
DEFAULT = ""
