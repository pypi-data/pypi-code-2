# -*- coding: utf-8 -*- #

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

