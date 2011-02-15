#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#-------------------------------------------------------------------------------
"""Executable object."""
__author__ = ('Lance Finn Helsten',)
__version__ = '1.0.1'
__copyright__ = """Copyright (C) 2009 Lance Finn Helsten"""
__license__ = """
This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""
__docformat__ = "reStructuredText en"

__all__ = ['Executable']

import sys
import os
import stat
import shutil
from datetime import datetime
import mimetypes
import weakref
from .ZombieConfig import config, datadir


class Executable:
    """This represents a single executable within the system.
    
    Properties
    ----------
    name
        The name of this executable.
    dirpath
        The path to the specific data directory for this executable.
    binpath
        The path to the executable image for this executable.
    mediatype
        The internet media type of executable.
    datadir
        The data directory that holds executables persistent information.
    execbase
        The base name for all executable directories.
    binaryname
        The base name for an executable's binary image.
    """
    
    @classmethod
    def createname(cls):
        """Create a unique RESTful name for a new executable."""
        name = config.get("pyzombie_filesystem", "execbase")
        name = "{0}_{1}".format(name, datetime.utcnow().strftime("%Y%jT%H%M%SZ"))
        if os.path.isdir(Executable.execdirpath(name)):
            #Need to handle the rare case of duplicate resource names---this
            #will happen all the time in testing, but rarely in production.
            index = 0
            altname = "{0}_{1:03}".format(name, index)
            while os.path.isdir(Executable.execdirpath(altname)):
                index = index + 1
                altname = "{0}_{1:03}".format(name, index)
            name = altname
        return name
    
    @classmethod
    def execdirpath(cls, name):
        return os.path.normpath(os.path.join(datadir(), name))
    
    __cache = {}
    
    @classmethod
    def getcached(cls, name, mediatype=None):
        """Get a cached executable by name. This will create a new executable
        if necessary."""
        if name not in cls.__cache:
            cls.__cache[name] = Executable(name, mediatype)
        return cls.__cache[name]
    
    def __init__(self, name, mediatype=None):
        """
        Parameters
        ----------
        name
            Name of the executable directory.
        mediatype
            The media type for the binary. If none given then the mediatype
            will default to application/octet-stream.
        """
        self.__name = name
        self.__edir = Executable.execdirpath(name)
        self.__bin = os.path.normpath(os.path.join(self.__edir, self.binaryname))
        if os.path.isdir(self.__edir):
            fnames = [f for f in os.listdir(self.__edir) if f.startswith(self.binaryname)]
            if fnames:
                self.__bin = self.__bin + os.path.splitext(fnames[0])[1]
        else:
            os.makedirs(self.__edir)
            if not mediatype:
                mediatype = "application/octet-stream"
            self.__bin = self.__bin + mimetypes.guess_extension(mediatype)
        self.__mediatype = mimetypes.guess_type(self.__bin)
        self.instances = {}
    
    def __str__(self):
        return "<pyzombie.Executable {0}>".format(self.name)

    def readimage(self, fp):
        """Read te image from the persistant store into the file object."""
        execfile = open(self.binpath, "r")
        databuf = execfile.read(4096)
        while databuf:
            fp.write(databuf)
            databuf = fp.read(4096)
        fp.flush()
        execfile.close()
    
    def writeimage(self, fp):
        """Write the image from the file object to the persistant store."""
        execfile = open(self.binpath, "w")
        databuf = fp.read(4096)
        while databuf:
            execfile.write(databuf)
            databuf = fp.read(4096)
        execfile.flush()
        execfile.close()
        os.chmod(self.binpath, stat.S_IRWXU)
    
    def delete(self):
        """Terminate all instances then remove the executable."""
        for i in set(self.instances.values()):
            i.delete()
        shutil.rmtree(self.dirpath, True)
            
    @property
    def datadir(self):
        return datadir()
    
    @property
    def execbase(self):
        return config.get("pyzombie_filesystem", "execbase")
    
    @property
    def binaryname(self):
        return config.get("pyzombie_filesystem", "binary")

    @property
    def name(self):
        """This is the RESTful name of the executable."""
        return self.__name
    
    @property
    def dirpath(self):
        """This is the path to the executable directory."""
        return self.__edir
    
    @property
    def binpath(self):
        """This is the path to the executable file."""
        return self.__bin
    
    @property
    def mediatype(self):
        """This is the internet media type of the executable."""
        return self.__mediatype


