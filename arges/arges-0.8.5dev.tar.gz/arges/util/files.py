# -*- coding: latin-1 -*-

"""files -  this module provides helper function to work with files

@author: Adrián Deccico
"""

import distutils.dir_util 
import os
import re
import stat  

def count_lines_dir(arg_path, ending=".py"):
    """count lines of a directory recursively"""
    lineas_totales = 0
    for root, dirs, files in os.walk(arg_path):
        for name in files:
            if name[len(name)-3:] == ending:
                file = root + "\\" + name
                lineas = count_lines_file(file)
                lineas_totales = lineas_totales + lineas
    return lineas_totales

def count_lines_file(file_name):
    """count lines of a file"""
    count = 0
    f = file(file_name)
    for lines in f:
        count = count + 1
    return count

def getMode(path):
    "return the mode of a path"
    return os.stat(path)[stat.ST_MODE]

def isFile(file_path):
    "return true if it is a regular file"
    return os.path.isfile(file_path)
    
def getExtension(file):
    "return the extension of a file"
    components = file.split(".")
    if components < 2:
        return ""
    else:
        return components[len(components)-1].lower()

def changeFileExtension(file, new_extension):
    "change the extension of a file"
    #@todo: fix bug when file with no extension is provided 
    ext = getExtension(file)
    return file[:len(file)-len(ext)] + new_extension

def lineIsComment(line):
    """return True if the line is a comment"""
    #@todo: use a regex here
    return line.replace(" ", "")[0] == "#"
    
def lineIsBlank(line):
    """return True if the line is a comment"""
    return re.search(r"""^[\W]*$""", line)

def getDir(path):
    """return the directory of a given path""" 
    return os.path.dirname(path)

def getFileName(path, stripExtension=False):
    "given a path return the file name"
    components = os.path.split(path)
    name = components[1]
    if stripExtension:
        name = name.split(",")[0]
    return(name)

def getFileDir(path):
    "given a path return the directory"
    components = os.path.split(path)
    return(components[0])

def createDir(path, shouldFail=True):
    try:
        dir = os.path.normpath(path)
        dir = getFileDir(dir)
        if not os.path.exists(dir):
            distutils.dir_util.mkpath(dir)
    except:
        #fail if it is flagged
        if shouldFail:
            raise NameError,"Directory dir: " + str(dir) + " could not be created"
    if not os.path.exists(dir): 
            raise NameError,"Directory dir: " + str(dir) + " could not be created"

