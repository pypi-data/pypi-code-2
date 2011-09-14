# -*- coding: iso-8859-1 -*-
# @Begin License@
# This file is part of QUI for MPlayer.
#
# QUI for MPlayer is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# QUI for MPlayer is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with QUI for MPlayer.  If not, see <http:#www.gnu.org/licenses/>.
#
# Copyright 2010-2011 Ben Nemec
# @End License@

import sys

class NTreeReader:
   @staticmethod
   def getWord(line, num):
      rest = line.lstrip()
      value, sep, rest = rest.partition(" ")
      for i in range(num):
         rest = rest.lstrip() # In case of extra whitespace
         value, sep, rest = rest.partition(" ")
      return value
      
         
   def __init__(self, filename = None, inFile = None, level = 0):
      self.children = []
      self.data = dict()
      self.level = level

      if not filename and not inFile:
         return

      if filename:
         inFile = open(filename)

      firstLine = True
      current = inFile.tell()

      line = self.readLineFromFile(inFile)
      
      while line:
         originalLen = len(line)
         stripLine = line.lstrip()
         stripLen = len(stripLine)
         lineLevel = originalLen - stripLen

         if len(stripLine) < 1:
            continue

         if firstLine:
            self.name = stripLine
            firstLine = False

         if lineLevel > self.level:
            inFile.seek(current)
            newReader = NTreeReader(inFile = inFile, level = lineLevel)
            self.children.append(newReader)
         elif lineLevel < self.level:
            inFile.seek(current)
            return
         else:
            self.readData(stripLine)
            current = inFile.tell()

         line = self.readLineFromFile(inFile)


   def readData(self, line):
      key, sep, value = line.partition(" ")
      self.data[key] = value


   def readLineFromFile(self, inFile):
      """Read a line from the file and strip the trailing \n if present"""
      retval = inFile.readline()
      if len(retval) and retval[-1] == "\n":
         retval = retval[:-1]
      return retval


   def readLine(self, default, name):
      if name in self.data:
         return self.data[name]
      return default


   def read(self, default, name, num = 0):
      if not name in self.data:
         return default

      value = self.getWord(self.data[name], num)

      return value


   def numChildren(self):
      return len(self.children)

   def getChild(self, childNum):
      return self.children[childNum]

   def getChildByName(self, childName):
      for child in self.children:
         if child.name == childName:
            return child
      return None

   def __iter__(self):
      return self.children.__iter__()