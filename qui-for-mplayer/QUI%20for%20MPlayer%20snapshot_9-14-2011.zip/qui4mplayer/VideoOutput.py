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
from PyQt4.QtGui import QWidget, QGridLayout, QLabel, QSizePolicy, QRegion
from PyQt4.QtCore import QTimer
from QUIButton import *
from ControlOverlay import *

class VideoOutput(QWidget):
   fullscreenDisabled = pyqtSignal()
   def __init__(self, parent, keyHandler):
      QWidget.__init__(self, parent)

      self.fullscreen = False
      self.keyPressHandler = keyHandler
      self.moveControls = False
      self.frameHeight = 0

      self.controlTimer = QTimer()
      self.controlTimer.setInterval(2000)

      self.createUI()
      self.controlTimer.timeout.connect(self.hideControls)
      
      self.setMouseTracking(True)
      self.setWindowTitle("Fullscreen Output")
      self.hide()
      
      
   def createUI(self):
      palette = QPalette()
      palette.setColor(QPalette.Background, Qt.black)
      self.setPalette(palette)
      self.setAutoFillBackground(True)
      
      self.videoLabel = VideoOutputLabel(self)

      self.controls = ControlOverlay(self)
      self.controls.fullscreenButton.toggled.connect(self.setFullscreen)
      self.controls.mouseInControls.connect(self.controlTimer.stop)
      
      
   def setSize(self, width, height):
      self.videoLabel.videoWidth = width
      self.videoLabel.videoHeight = height
      self.videoLabel.setSize(width, height)
      
      
   def resizeEvent(self, event):
      self.videoLabel.aspectResize(event.size().width(), event.size().height())
      if self.moveControls:
         x = self.size().width() / 2 + self.pos().x() - self.controls.frameGeometry().width() / 2
         y = self.size().height() + self.pos().y() - self.controls.frameGeometry().height() - self.frameHeight
         self.controls.move(x, y)
         self.moveControls = False
      
      
   def setFullscreen(self, fs):
      if fs and self.fullscreen:
         return
      
      self.fullscreen = fs
      self.controls.fullscreenButton.setChecked(fs)
      if fs:
         # Now that we're in a splitter the window is two levels above us
         window = self.parent().parent()
         position = window.pos()
         window.saveSplitterPosition()
         # This is something of a hack to get around the fact that the controls window is not decorated yet when we
         # get to the resizeEvent, so we can't calculate the proper position including window frame.  This assumes
         # that the main window will have the same height frame as the controls window (probably not safe, but I think)
         # in general it will be true)
         self.frameHeight = window.frameGeometry().height() - window.height()
         self.setParent(None)
         self.move(position) # Make sure we maximize to the right Xinerama screen
         self.showFullScreen()
         self.moveControls = True
         
         self.controls.show()
         self.controlTimer.start()
      else:
         self.controls.hide()
         self.setCursor(QCursor(Qt.ArrowCursor))
         self.fullscreenDisabled.emit()
         
         
   def setFitToWidth(self, fit):
      self.videoLabel.fitToWidth = fit
      self.videoLabel.aspectResize(self.width(), self.height())
         
         
   def mouseMoveEvent(self, event):
      if self.fullscreen:
         self.controls.show()
         self.controlTimer.start()
         self.setCursor(QCursor(Qt.ArrowCursor))
         
         
   def mouseDoubleClickEvent(self, event):
      self.setFullscreen(not self.fullscreen)


   def mousePressEvent(self, event):
      self.hideControls()

   def hideControls(self):
      self.controls.hide()
      if self.fullscreen:
         self.setCursor(QCursor(Qt.BlankCursor))


   def keyPressEvent(self, event):
      if not self.keyPressHandler(event):
         QWidget.keyPressHandler(self, event)


class VideoOutputLabel(QLabel):
   def __init__(self, parent = None):
      QWidget.__init__(self, parent)
      self.videoWidth = 1
      self.videoHeight = 1
      self.fitToWidth = False
      self.setMouseTracking(True)
      
   
   def setSize(self, width, height):
      self.setMinimumSize(width, height)
      self.setMaximumSize(width, height)
      self.resize(width, height)
      
      
   def aspectResize(self, width, height):
      if (float(width) / float(height) < float(self.videoWidth) / float(self.videoHeight)) or self.fitToWidth:
         newHeight = int(float(self.videoHeight * width) / self.videoWidth)
         self.setSize(width, newHeight)
         self.move(0, (height - newHeight) / 2)
      else:
         newWidth = int(float(self.videoWidth * height) / self.videoHeight)
         self.setSize(newWidth, height)
         self.move((width - newWidth) / 2, 0)


