import ConfigParser
# The MIT License
# 
# Copyright (c) 2007 Suncoast Partnership 
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
# 

import string
import sys
import os
import fileutils
from clsexceptions import fileNotFoundError

class clsConfigParser(fileNotFoundError):
    """
    >>> import clsIniUtils
    >>> cp = clsIniUtils.clsConfigParser('fileConverter.ini')
    >>> pd = cp.getConfig()
    >>> pd
    {'filelocations.basepath': 'C:\\\Documents and Settings\\\user.PC885314341208\\\My Documents\\\Development\\\AlexandriaConsulting\\\ManateeCountySchools\\\Data', 'options.debug': '1', 'database.name': 'manateecountyschools', 'database.textdbname': 'manateecountyschools', 'options.debugfile': 'debug.txt', 'filelocations.used_file_extensions': '.used', 'options.first_line_header': 'False', 'filelocations.outputlocation': 'outputdir', 'database.filename': 'manateecountyschools.db', 'filelocations.file_extensions': 'csv', 'options.systemmode': 'Test', 'options.debuglevel': '1', 'database.path': 'C:\\\Documents and Settings\\\user.PC885314341208\\\My Documents\\\Development\\\AlexandriaConsulting\\\ManateeCountySchools\\\Data\\\database'}
    >>>
    >>> cp.setConfig("newSection", "newOption","newValue")
    >>> pd = cp.getConfig()
    >>> pd
    {'filelocations.basepath': 'C:\\\Documents and Settings\\\user.PC885314341208\\\My Documents\\\Development\\\AlexandriaConsulting\\\ManateeCountySchools\\\Data', 'options.debug': '1', 'database.name': 'manateecountyschools', 'database.textdbname': 'manateecountyschools', 'options.debugfile': 'debug.txt', 'filelocations.used_file_extensions': '.used', 'options.first_line_header': 'False', 'filelocations.outputlocation': 'outputdir', 'database.filename': 'manateecountyschools.db', 'filelocations.file_extensions': 'csv', 'options.systemmode': 'Test', 'options.debuglevel': '1', 'newsection.newoption': 'newValue', 'database.path': 'C:\\\Documents and Settings\\\user.PC885314341208\\\My Documents\\\Development\\\AlexandriaConsulting\\\ManateeCountySchools\\\Data\\\database'}
    >>> pd['newsection.newoption']
    'newValue'
    >>> pd['newSection.newOption']
    Traceback (most recent call last):
      File "<stdin>", line 1, in <module>
    KeyError: 'newSection.newOption'
    >>> cp = clsIniUtils.clsConfigParser('fileConverter2.ini')
    Error 1001:
    Indicates: Configuration(INI) file: fileConverter2.ini was not found.  Please check and try again
    In Location: clsIniUtils
    
    """
    
    #class fileNotFound(Exception):
    #    def __init__(self, *args):
    #        print "Error %s: \nIndicates: %s\nIn Location: %s" % (args[1], args[0], args[2])
    
    """
    This is the clsIniUtils module.
    
    This module is a class version of iniutils.  It allows for the same functionality as iniutils,
    with the exception that it can write back the INI file upon completion.
    
    
    """
    def __name__(self):
        print "clsConfigParser"
        
    def __init__(self, file, config={}, pBackupFile=False):
        """
        __init__() method.
        
        should be called at minimum with a file as the first parameter.
        This will open the file defined/structured as an INI (win) style text file.
        
        [section]
        option=value
        option2=value2
        
        etc.
        
        These variables can be accessed by the variable declared in your program as
        
        PD['section.option']
        
        after the class has been instantiated, PD can be populated by calling the getConfig() method.
        
        """
        
        self.cp = ConfigParser.ConfigParser()
        self.backupFile = pBackupFile
        
        try:
            self.checkExists(file)
        except fileNotFoundError:
            theError = ("Configuration(INI) file: %s was not found.  Please check and try again" % file, 1001, self.__module__)
            raise fileNotFoundError, theError

        self.config = self.LoadConfig(file, config)
        #if pBackupFile == True:
            #self.fu = fileutils.FileUtilities()
    
    def checkExists(self, file):
        if os.path.isfile(file):
            pass
        else:
            theError = ("Configuration(INI) file: %s was not found.  Please check and try again" % file, 1001, self.__module__)
            raise fileNotFoundError, theError
    
    def dumpConfig(self, file):
        """ Dumps the configuration object to a file (store the ini)"""
        # check if the file exists
        if os.path.isfile(file):
            
        # if it does, back it up (if the user wants it backed up
            if self.backupFile == True:
                fileutils.backupFile(file)
            
        # dump the file to the file system.
        fo = open(file, 'w')
        
        self.cp.write(fo)
        
        fo.close()
        
    def getConfig(self):
        '''
        Returns the dictionary defined as { ['section.option'] = value, ['section.option2'] = value }
        
        '''
        return self.config
    
    def setConfig(self, section, option, value):
        '''
        setConfig(section, option, value)
        
        This method allows updating of the values stored in the ConfigurationParser Object.
        It is mainly used for writing the INI file used in the dumpConfig() method.
        
        '''
        try:
            self.cp.set(section, option, value)
        except ConfigParser.NoSectionError:
            try:
                self.cp.add_section(section)
                self.cp.set(section, option, value)
            except:
                return  
        self.pd = self.refreshConfig()
        
    def LoadConfig(self, file, config={}):
        """
        returns a dictionary with keys of the form
        <section>.<option> and the corresponding values
        """
        config = config.copy()
        self.cp.read(file)
        # call the refresh method to update the dictionary structure
        # cause now we can update values via the setConfig method
        return self.refreshConfig()
        
    def refreshConfig(self):
        # wipe out the current configuration(dictionary)
        config = {}
        for sec in self.cp.sections():
            name = string.lower(sec)
            for opt in self.cp.options(sec):
                config[name + "." + string.lower(opt)] = string.strip(
                    self.cp.get(sec, opt))
        return config

def _test():
    import doctest
    doctest.testmod()

if __name__ == "__main__":
    _test()

if __name__=="__main__":
#    print LoadConfig("some.ini", _ConfigDefault)
    _ConfigDefault = {}
    try:
        newConfig = clsConfigParser("fileConverter.ini", _ConfigDefault, True)
    except fileNotFoundError:
        sys.exit(-1)
    
    pd = newConfig.getConfig()
    print "OldStyle: ", pd
    print newConfig.dumpConfig("fileConverter.new.ini")
    