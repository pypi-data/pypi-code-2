# -*- coding: latin-1 -*-

"""util -  this module provides miscellaneous functions 

@author: Adrián Deccico
"""

import files
import os
import sys
import random

import util

def dirExists(dir):
    return os.path.exists(dir)

def fileExists(file):
    return dirExists(file)

def getAppName():
    """get the name of the application"""
    appname = util.files.getFileName(sys.argv[0])
    return appname

def getAppConfigFileName(ext):
    """ 
        It just gives me the filename of the configuration file. 
        It's the name of the program but with the extension changed.
    """
    config_file = getAppName()
    config_file = util.files.changeFileExtension(config_file, ext)
    return config_file

def getAppDir():
    """get the dir of the application"""
    appdir = os.path.dirname(os.path.abspath(sys.argv[0]))
    return appdir

def getHomeDir():
    """get the home dir of the user, taking into account the OS"""
    if sys.platform.upper()== "WIN32":
        appdir = os.path.dirname(os.path.expanduser("~") + "/")
    else:
        #here I hope that the rest of the OS's of the universe (excepting Windows) 
        #have a well defined $HOME environment variable 
        appdir = os.environ.get("HOME")
    return appdir

def getAppConfigName(ext="ini"):
    """get the configuration file name according to the application"""
    config_file = getAppConfigFileName(ext)
    app_dir = util.files.changeFileExtension(config_file, "")
    app_dir  = app_dir[:len(app_dir)-1] #get the app name without last dot
    config_file = getHomeDir() + os.path.sep + "." + app_dir + os.path.sep + app_dir + ".ini"
    util.files.createDir(config_file)
    return config_file

def getLogFileName(ext="log"):
    """get the configuration file name according to the application"""
    log_file = getAppName()
    log_file = util.files.changeFileExtension(log_file, ext)
    log_file = getAppDir() + os.path.sep + files.getFileName(log_file)
    return log_file

def __my_generator():
    i = 0
    while True:
        yield i
        i += 1

my_random = __my_generator()    
def getRandomNumber():
    return my_random.next()
