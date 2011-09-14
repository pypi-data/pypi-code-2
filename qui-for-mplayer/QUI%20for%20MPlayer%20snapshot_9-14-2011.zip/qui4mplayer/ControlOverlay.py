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
from PyQt4.QtGui import QDialog, QGridLayout, QSlider
from QUIButton import *
class ControlOverlay(QDialog):
   mouseInControls = pyqtSignal()
   def __init__(self, parent):
      QDialog.__init__(self, parent)
      
      self.mainLayout = QGridLayout(self)
      
      self.playButton = QUIButton()
      self.playButton.setPixmap("PlaySmall.png")
      self.mainLayout.addWidget(self.playButton, 0, 0)
      self.fullscreenButton = QUIButton()
      self.fullscreenButton.setPixmap("Fullscreen.png")
      self.fullscreenButton.setCheckable(True)
      self.mainLayout.addWidget(self.fullscreenButton, 0, 1)
      
      self.timeSlider = QSlider()
      self.timeSlider.setOrientation(Qt.Horizontal)
      self.timeSlider.setMinimumWidth(150)
      self.timeSlider.setPageStep(10)
      self.mainLayout.addWidget(self.timeSlider, 0, 2)
      
      self.timeLabel = QLabel()
      self.mainLayout.addWidget(self.timeLabel, 0, 3)
      
      self.oldPos = None
      self.setMouseTracking(True)
      self.setWindowTitle("Controls")
      

   def hideEvent(self, event):
      self.oldPos = self.pos()


   def showEvent(self, event):
      if self.oldPos:
         self.move(self.oldPos)
         
   def moveEvent(self, event):
      self.mouseInControls.emit()

   def mouseMoveEvent(self, event):
      self.mouseInControls.emit()
      