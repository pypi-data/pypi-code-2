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

class OptionsForm(QDialog):
   def __init__(self, parent):
      QDialog.__init__(self, parent)

      self.setWindowTitle("Options")
      self.resize(500, 300)
      self.createUI()

      self.accepted = False


   def createUI(self):
      mainLayout = QVBoxLayout()
      self.setLayout(mainLayout)
      
      mainPage = QWidget()
      mainPageLayout = QGridLayout(mainPage)
      
      optionsLabel = QLabel("Additional MPlayer Options")
      mainPageLayout.addWidget(optionsLabel, 0, 0)

      self.optionsBox = QLineEdit()
      mainPageLayout.addWidget(self.optionsBox, 0, 1)

      self.notificationCheck = QCheckBox()
      self.notificationCheck.setText("Current File Notification")
      self.notificationCheck.setChecked(False)
      mainPageLayout.addWidget(self.notificationCheck, 1, 0)
      
      self.deinterlaceCheck = QCheckBox()
      self.deinterlaceCheck.setText("Deinterlace")
      self.deinterlaceCheck.setChecked(True)
      mainPageLayout.addWidget(self.deinterlaceCheck, 2, 0)
      
      self.stopXScreensaverCheck = QCheckBox()
      self.stopXScreensaverCheck.setText("Stop XScreensaver")
      self.stopXScreensaverCheck.setChecked(True)
      mainPageLayout.addWidget(self.stopXScreensaverCheck, 3, 0)

      logPage = QWidget()
      logPageLayout = QHBoxLayout(logPage)

      self.logText = QTextEdit()
      logPageLayout.addWidget(self.logText)

      aboutPage = QWidget()
      aboutPageLayout = QHBoxLayout(aboutPage)
      
      aboutText = QTextEdit()
      aboutText.setAlignment(Qt.AlignCenter)
      aboutText.append("QUI for MPlayer\n")
      aboutText.append("Copyright 2010 Ben Nemec\n")
      aboutText.append("Distributed under the GPLv3\n")
      aboutText.append("Web: http://www.sourceforge.net/projects/qui4mplayer\n")
      aboutText.append("E-Mail: cybertron@nemebean.com\n")
      aboutText.setReadOnly(True)
      aboutPageLayout.addWidget(aboutText)

      tabs = QTabWidget(self)
      tabs.addTab(mainPage, "MPlayer")
      tabs.addTab(logPage, "Log")
      tabs.addTab(aboutPage, "About")
      mainLayout.addWidget(tabs)

      buttonLayout = QHBoxLayout()
      okButton = QPushButton("OK")
      okButton.pressed.connect(self.okPressed)
      buttonLayout.addWidget(okButton)

      cancelButton = QPushButton("Cancel")
      cancelButton.pressed.connect(self.cancelPressed)
      buttonLayout.addWidget(cancelButton)

      mainLayout.addLayout(buttonLayout)


   def okPressed(self):
      self.accepted = True
      self.close()

   def cancelPressed(self):
      self.accepted = False
      self.close()
      