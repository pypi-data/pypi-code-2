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

from PyQt4.QtGui import QDialog, QGridLayout, QLabel, QLineEdit, QPushButton

class AddDialog(QDialog):
   def __init__(self, parent):
      QDialog.__init__(self, parent)

      self.playlist = parent.fileList

      mainLayout = QGridLayout(self)

      titleLabel = QLabel("Examples:")
      mainLayout.addWidget(titleLabel, 0, 0, 1, 2)
      dvdLabel = QLabel("DVD track 1 - dvd://1")
      mainLayout.addWidget(dvdLabel, 1, 0, 1, 2)
      vcdLabel = QLabel("VCD track 2 - vcd://2")
      mainLayout.addWidget(vcdLabel, 2, 0, 1, 2)
      streamLabel = QLabel("Stream - http://address:port/path")
      mainLayout.addWidget(streamLabel, 3, 0, 1, 2)

      self.inputBox = QLineEdit()
      mainLayout.addWidget(self.inputBox, 4, 0, 1, 2)
      
      addButton = QPushButton("Add")
      addButton.clicked.connect(self.addClicked)
      mainLayout.addWidget(addButton, 5, 0)

      closeButton = QPushButton("Close")
      closeButton.clicked.connect(self.close)
      mainLayout.addWidget(closeButton, 5, 1)


   def addClicked(self):
      self.playlist.add(self.inputBox.text().toAscii().data())