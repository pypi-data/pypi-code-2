#!/usr/bin/env python
# -*- coding: utf-8 -*- #

from watchvideo.ui_about import Ui_AboutDialog
from watchvideo.qt import QtCore, QtGui
import watchvideo.constants as c


copyright = u"Copyright © 2010 Leonardo Gastón De Luca"

credits = \
u"""
Developers:
Carlos Pais <freemind@lavabit.com>
Michał Masłowski <mtjm@mtjm.eu>
Miguel Angel Souto
Leonardo Gastón De Luca <leo@kde.org.ar>


Thanks to:
Python Programming Language <http://www.python.org/>
Qt4 Libraries <http://qt.nokia.com/products/>
FFmpeg <http://www.ffmpeg.org/>
FFmpeg2Theora <http://v2v.cc/~j/ffmpeg2theora/>
VLC <http://www.videolan.org/>
Libnotify
Mariano Street
Edgar Morales
""".strip()

license = \
"""
This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
""".strip()

class AboutDialog(QtGui.QDialog):
    def __init__(self, parent):
        super(AboutDialog, self).__init__(parent)
        self.ui = Ui_AboutDialog()
        self.ui.setupUi(self)
        
        description = self.tr("\n\nWatchVideo is a small application to play, " +
        "download or convert videos (to Ogg) from various youtube-like sites.\n" + "It's made in PyQt4.")
        
        #creates a Svg widget
        svg_icon = QtGui.QLabel()
        svg_icon.setPixmap(QtGui.QPixmap(":/media/watchvideo-200x200.png"))
        
        label_desc = QtGui.QLabel(description + "\n\n" + 
        copyright + "\n" + self.tr("Version: ") + c.VERSION + " beta")
        
        label_desc.setSizePolicy(QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Preferred))
        label_desc.setMaximumSize(self.maximumSize())
        label_desc.setWordWrap(True)

        vbox = QtGui.QVBoxLayout(self.ui.t_about)
        vbox.addWidget(svg_icon)
        vbox.setAlignment(svg_icon, QtCore.Qt.AlignHCenter)
        vbox.addWidget(label_desc)
        vbox.setAlignment(label_desc, QtCore.Qt.AlignJustify)
        
        self.ui.tedit_credits.setText(credits)
        self.ui.tedit_license.setText(license)
        
        self.ui.b_close.clicked.connect(self.close)
        
        
    
