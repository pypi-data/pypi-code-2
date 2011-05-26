# -*- coding: utf-8 -*-
# Copyright (C) 2010, 2011 Carlos Pais <freemind@lavabit.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from watchvideo.qt import QtGui, QtCore

def selectFolder(parent=None, title="Select the destination folder", start_path=""):
    folder = QtGui.QFileDialog.getExistingDirectory(parent,
                title,
                start_path,
                QtGui.QFileDialog.ShowDirsOnly | QtGui.QFileDialog.DontResolveSymlinks
            )
            
    return folder
    
def selectFile(parent=None, title="Select an executable file", start_path="/usr/bin"):
    filepath = QtGui.QFileDialog.getOpenFileName(parent,
                title,
                start_path
                )
    
    return filepath
    
def warning(parent=None, title="Warning", msg="Warning"):
    QtGui.QMessageBox.warning(parent, title, msg,QtGui.QMessageBox.Ok,)   


def confirm(parent=None, title="Overwrite", msg="Do you wish to overwrite?"):
    confirm = QtGui.QMessageBox.warning(parent, 
            title,
            msg,
            QtGui.QMessageBox.Yes, QtGui.QMessageBox.No,
        )
    return confirm
    
def getGreyedIcon(iconpath, size=QtCore.QSize(16, 16)):
    icon = QtGui.QIcon(iconpath)
    pix = icon.pixmap(size, QtGui.QIcon.Disabled)
    return QtGui.QIcon(pix)
    
def setTextOnImage(image, text):
    # tell the painter to draw on the QImage
    painter = QtGui.QPainter(image)
    painter.setPen(QtCore.Qt.white)
    painter.setFont(QtGui.QFont("Arial", 15))
    # you probably want the to draw the text to the rect of the image
    painter.drawText(image.rect(), QtCore.Qt.AlignRight | QtCore.Qt.AlignBottom, text)
    
    return image

