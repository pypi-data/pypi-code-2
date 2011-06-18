#! /usr/bin/python
#
#     config.py
# 
#     Copyright (c) 2010 Umang Varma <umang.me@gmail.com>.
# 
#     This file is part of Pynagram
# 
#     Pynagram is free software: you can redistribute it and/or modify
#     it under the terms of the GNU General Public License as published by
#     the Free Software Foundation, either version 3 of the License, or
#     (at your option) any later version.
# 
#     Pynagram is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU General Public License for more details.
# 
#     You should have received a copy of the GNU General Public License
#     along with Pynagram. If not, see <http://www.gnu.org/licenses/>.
# 
import sys
import os.path
from os import environ
try:
    import json
    json.JSONDecodeError = ValueError
except ImportError:
    import simplejson as json
class pynagram_config(dict):
    """Handles all configuration actions: read, write, defaults, etc"""

    def  __init__(self):
        dict.__init__(self)
        self.changed = False
    
    def _raw_config(self):
        """Returns raw config"""
        try:
            fsock = open(self.pathtoconfigfile())
        except IOError:
            self.writedefault()
            fsock = open(self.pathtoconfigfile())
        configdata = fsock.read()
        fsock.close()
        return configdata

    def readconfig(self):
        """Reads configuration file and returns a dict with data"""
        try:
            data = json.loads(self._raw_config())
        except json.JSONDecodeError:
            self.writedefault()
            data = json.loads(self._raw_config())
        self.clear()
        self.update(data)
        self.setdefault("wordlist", 0)
        if not self["wordlists"]:
            self.adddefaultwl()
            self.writeconfig()

    def writeconfig(self):
        """Writes configuration data provided by the data dict"""
        try:
            fsock = open(self.pathtoconfigfile(), "w")
        except IOError:
            self.createdir()
            fsock = open(self.pathtoconfigfile(), "w")
        self["wordlists"] = [os.path.normpath(x) for x in self["wordlists"]]
        fsock.write(json.dumps(self, indent=4))
        fsock.close()

    def getdefaultwl(self):
        """Returns the default wordlist"""
        tries = [[sys.path[0] + "/../wordlist/wordlist.txt", sys.path[0] + \
                "/wordlist/wordlist.txt", sys.prefix + \
                "/share/pynagram/wordlist.txt"]]
        # A list of list of possible wordlists. Each nested list contains
        # similar wordlists, only one of which will be used. If a wordlist is
        # different, it needs to be placed in a separate list. e.g :
        # [['a1', 'a2', 'a3'], ['b'], ['c']] when a1, a2, a3 are similar
        # wordlists found in different locations and b, c are distinct
        wordlists = []
        for source in tries:
            for path in source:
                if os.path.exists(path):
                    wordlists.append(path)
                    break
        return wordlists
        raise IOError("No wordlist found in any of the expected locations")

    def adddefaultwl(self):
        """Adds the default wordlists"""
        self.setdefault("wordlists", []).extend(self.getdefaultwl())

    def writedefault(self):
        """Writes default config file"""
        self.clear()
        self.adddefaultwl()
        self.writeconfig()

    def pathtoconfig(self):
        """Returns path to configuration file"""
        if sys.platform == 'win32':
             appdata = os.path.join(environ['APPDATA'], "Pynagram")
        else:
             appdata = os.path.expanduser(os.path.join("~", ".pynagram/"))
        return appdata

    def pathtoconfigfile(self):
        """Returns path to config file"""
        return os.path.join(self.pathtoconfig(), "config.txt")

    def createdir(self):
        """Creates the config directory if it doesn't already exist"""
        try:
            os.mkdir(self.pathtoconfig())
        except OSError:
            print self.pathtoconfig() + " already exists. Writing defaults"
            pass # directory already exists

