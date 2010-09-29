# -*- coding: latin-1 -*-

"""ini -  this module provides helper function to work with ini files

@author: Adrián Deccico
"""

import ConfigParser
import os

import strings
import introspection
import util

class Ini:
    
    __instance = None
    
    def __init__(self, file_name = None):
        if file_name is None:
            file_name = util.getAppConfigName()
            
        self.file_name = file_name
        self.config = ConfigParser.SafeConfigParser()
        # This method is overriden because otherwise, it'll lowercase all the params.
        self.config.optionxform = lambda x: str(x)
        
        if not os.path.isfile(self.file_name): 
            mode = "w"
        else:
            mode = "r"
        self.config.readfp(open(self.file_name,mode))

    def getInstance(self, rat_dir = None):
        """implementation of the singleton design pattern"""
        if Ini.__instance == None:
            Ini.__instance = Ini(rat_dir)
        return Ini.__instance
    
    def get(self, section, option, default_value, raw=False, vars=None):
        """
            Get value from a section
        """
        
        ret = None
        original_value = default_value
        default_value = str(default_value)
        
        #make sure that the section exists
        if not self.config.has_section(section):
            self.config.add_section(section)
        
        if not self.config.has_option(section, option):
            self.config.set(section, option, default_value)
            ret = default_value
        else:
            ret = self.config.get(section, option, raw, vars)
        
        ret = self.__transformTheValue(original_value, ret)    
        return ret
    
    def __transformTheValue(self, original_value, ret):
        """transform the value according to the original type value
        parameters:
            original_value: has the type of value that we want to return
            ret: has the return value, that   
        """
        if introspection.isBool(original_value):
            #process the boolean
            if str(ret).upper() in ["FALSE", "0", "NO", "FALSO"]:
                return False
            else:
                return True
        #default return
        return ret
    
    def getOptions(self, section):
        """get a dictionary containing all the options from a section"""
        options = {}
        if not self.config.has_section(section):
            self.config.add_section(section)
            return options
        list_options = self.config.items(section)
        for i in list_options:
            param_key = strings.formatTestParameter(i[0]) 
            options[param_key] = [strings.removeComment(i[1]).strip()]
        return options 
    
    def set(self, section, option, value):
        """set an option within a section"""
        if not self.config.has_section(section):
            self.config.add_section(section)
        self.config.set(section, option, str(value))
   
    def write(self):
        """write the file"""
        self.config.write(open(self.file_name,"w"))
        