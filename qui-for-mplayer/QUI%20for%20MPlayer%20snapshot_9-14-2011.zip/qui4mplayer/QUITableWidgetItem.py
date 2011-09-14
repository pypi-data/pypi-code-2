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

from PyQt4.QtGui import *
from PlaylistFileInfo import *

class QUITableWidgetItem(QTableWidgetItem):
   def __init__(self, noInfo = False):
      QTableWidgetItem.__init__(self)

      self.filename = ""
      self.time = 0
      self.seekScale = 1
      if not noInfo:
         self.info = PlaylistFileInfo(self)
         self.info.start()