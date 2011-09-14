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
from FileInfoReader import *
import threading, time, os
from PyQt4.QtCore import *

class PlaylistFileInfo(QThread):
   """MPlayer kind of sucks at guessing the length of some files, particularly VBR MP3's.  This class uses MPlayer to play the file
   as fast as possible and keeps track of the ending time as reported by MPlayer, which will be very close to the actual time."""
   limitRunning = threading.Semaphore(1) # Default to a single instance running at a time
   def __init__(self, item):
      QThread.__init__(self)

      self.title = ""
      self.time = -1
      self.seekScale = 1
      self.item = item
      self.processFinished = False


   def run(self):
      while self.item.filename == "":
         time.sleep(1)

      if not os.path.exists(self.item.filename):
         self.time = 0
         return

      PlaylistFileInfo.limitRunning.acquire()

      self.process = QProcess()

      # Because of the way queued slots work in PyQt, we need the signals and slots of the process to be owned by the same thread
      # (this QThread object is owned by the main thread, not itself) so we create a separate object to handle the signals
      # that will be owned by this thread (because it's created in the run function).
      self.infoReader = FileInfoReader(self.process)
      self.infoReader.finished.connect(self.finish)

      #for windows nowaveheader is needed to work bugfree

      if os.name == "nt":
            aocommand = "pcm:nowaveheader:fast:file="
      else:
            aocommand = "pcm:fast:file="


      args = []
      args.append("-identify")
      args.append("-vc")
      args.append("null")
      args.append("-vo")
      args.append("null")
      args.append("-ao")
      args.append(aocommand + os.devnull)
      args.append(self.item.filename)
      self.process.start("mplayer", args)
      self.exec_()


   def finished(self):
      return self.processFinished


   def finish(self):
      self.title = self.infoReader.title
      self.time = self.infoReader.time
      self.seekScale = self.infoReader.seekScale
      self.processFinished = True
      PlaylistFileInfo.limitRunning.release()
      self.exit()