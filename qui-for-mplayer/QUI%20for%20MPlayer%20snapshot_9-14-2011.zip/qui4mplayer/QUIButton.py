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
from PyQt4.QtCore import *
import os, imp, sys

class QUIButton(QPushButton):
   def __init__(self, parent = None):
      QPushButton.__init__(self, parent)


   def main_is_frozen(self):
      return (hasattr(sys, "frozen") or # new py2exe
                hasattr(sys, "importers") # old py2exe
                or imp.is_frozen("__main__")) # tools/freeze


   def get_main_dir(self):
      if self.main_is_frozen():
         return os.path.abspath(os.path.dirname(sys.executable))
      else:
         return os.path.dirname(__file__)


   def setPixmap(self, filename):
      base = os.path.join(self.get_main_dir(), "images")
      pixmap = QPixmap(os.path.join(base, filename))
      icon = QIcon(pixmap)
      iconSize = QSize(pixmap.width(), pixmap.height())
      self.setIconSize(iconSize)
      self.setIcon(icon)