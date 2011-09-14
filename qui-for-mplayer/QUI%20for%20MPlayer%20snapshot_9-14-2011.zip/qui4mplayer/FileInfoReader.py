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

from NTreeReader import *
from PyQt4.QtCore import *

class FileInfoReader(QObject):
   finished = pyqtSignal()
   
   def __init__(self, process):
      QObject.__init__(self)
      self.title = ""
      self.time = -1
      self.seekScale = 1
      self.video = False
      self.process = process

      self.process.readyReadStandardOutput.connect(self.readStdout)
      self.process.readyReadStandardError.connect(self.readStderr)
      self.process.finished.connect(self.finish)


   def readStdout(self):
      lines = self.process.readAllStandardOutput().data().splitlines()
      for line in lines:
         if line.find("Title: ") != -1:
            self.title = line[8:]
         if line.find("Name: ") != -1:
            self.title = line[7:]
         if line.find("A:") != -1:
            a, sep, tempLine = line.partition(":")
            value = NTreeReader.getWord(tempLine, 0)
            self.time = int(float(value))

            a, sep, tempLine = line.partition("of")
            value = NTreeReader.getWord(tempLine, 0)
            self.seekScale = float(self.time) / float(value)
         if line.find("ID_VIDEO") != -1:
            self.video = True
         if line.find("ID_LENGTH") != -1:
            if self.video:
               self.time = int(float(line[10:]))
               self.process.kill()
               self.finished.emit()
               break
            
            
   def readStderr(self):
      lines = self.process.readAllStandardError().data().splitlines()
      for line in lines:
         print "Error:", line


   def finish(self, status):
      self.finished.emit()