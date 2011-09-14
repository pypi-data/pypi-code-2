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
from QUITableWidgetItem import *
from SavePlaylistForm import *
from NTreeReader import *
from MPlayer import *
import os.path

class QUITableWidget(QTableWidget):
   currentTimeUpdated = pyqtSignal()
   playlistSaved = pyqtSignal()
   
   def __init__(self):
      QTableWidget.__init__(self)

      self.current = -1
      self.majorVersion = 1
      self.minorVersion = 0
      self.lastSelected = -1
      self.currentPlaylist = ""
      self.timer = QTimer()
      self.timer.timeout.connect(self.checkComplete)

      self.setColumnCount(2)
      self.setColumnWidth(1, 100)
      self.viewport().setAcceptDrops(True)
      self.setDragEnabled(True)
      self.setDragDropMode(QAbstractItemView.DragDrop)
      self.setDropIndicatorShown(True)
      self.setToolTip("Drag and drop files or directories here to add them to the playlist")
      self.setSelectionBehavior(QAbstractItemView.SelectRows)

      titles = QStringList()
      titles.append("Title")
      titles.append("Time")
      self.setHorizontalHeaderLabels(titles)

      header = self.horizontalHeader()
      header.setResizeMode(0, QHeaderView.Stretch)
      header.setResizeMode(1, QHeaderView.ResizeToContents)
      header.setDefaultAlignment(Qt.AlignLeft)

      header = self.verticalHeader()
      header.setDefaultSectionSize(20)


   def dragEnterEvent(self, event):
      event.accept()

   def dragMoveEvent(self, event):
      event.accept()
      
   def dropEvent(self, event):
      md = event.mimeData()
      position = event.pos()
      
      if md.hasUrls():
         urls = md.urls()
         dropRow = -1
         for url in urls:
            pyurl = url.toLocalFile().toAscii().data()
            dropRow = self.rowAt(position.y())
            if self.lastSelected != -1:
               self.add(pyurl, dropRow)
            else:
               self.add(pyurl)

         if self.lastSelected > dropRow:
            self.lastSelected += 1
            
         if self.lastSelected != -1:
            self.removeRow(self.lastSelected)
            
         event.accept()
      else:
         event.ignore()

   def mimeData(self, items):
      data = QMimeData()
      urls = []

      for i in items:
         if i.filename != "":
            urls.append(QUrl(i.filename))

      data.setUrls(urls)
      return data

   def mousePressEvent(self, event):
      self.lastSelected = self.rowAt(event.y())
      QTableWidget.mousePressEvent(self, event)

   def mouseReleaseEvent(self, event):
      self.lastSelected = -1
      QTableWidget.mouseReleaseEvent(self, event)


   def add(self, rawurl, row = -1):
      pyurl = rawurl
      if os.path.exists(pyurl):
         pyurl = os.path.abspath(rawurl)
      if os.path.isdir(pyurl):
         realurls = os.listdir(pyurl)
         realurls.sort()
         # Note that this isn't very intelligent right now - it tries to add everything in the directory
         # no matter what type of file it may be
         for i in realurls:
            self.addFile(os.path.join(pyurl, i), row)
      else:
         self.addFile(pyurl, row)

      self.timer.start(1000)


   # I recommend not calling this directly - the add function above is a safer way to add files
   def addFile(self, filename, row):
      newItem = QUITableWidgetItem()
      newItem.filename = filename
      newItem.setText(os.path.split(filename)[1])
      newItem.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled | Qt.ItemIsDragEnabled | Qt.ItemIsDropEnabled)

      if row == -1:
         row = self.rowCount()
      self.insertRow(row)
      self.setItem(row, 0, newItem)
      newItem = QUITableWidgetItem(True)
      self.setItem(row, 1, newItem)
      
      
   def updateHighlight(self):
      for col in range(self.columnCount()):
         for row in range(self.rowCount()):
            item = self.item(row, col)
            if item:
               if row == self.current:
                  item.setBackground(self.palette().alternateBase())
                  self.scrollTo(self.indexFromItem(item))
               else:
                  item.setBackground(QBrush())


   def clearPlaylist(self):
      while self.rowCount():
         self.removeRow(0)
      self.current = -1
      self.currentPlaylist = ""


   def savePlaylist(self):
      showSaveForm = True
      if self.currentPlaylist != "":
         overwriteForm = QMessageBox()
         overwriteForm.setText("Overwrite existing playlist?")
         overwriteForm.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
         overwrite = overwriteForm.exec_()
         
         if overwrite == QMessageBox.Yes:
            showSaveForm = False
         
      if showSaveForm:
         saveForm = SavePlaylistForm(self)
         saveForm.exec_()
         
         if saveForm.result() != QDialog.Accepted:
            return
            
         self.currentPlaylist = os.path.join(os.path.expanduser("~/.qui/Playlists"), str(saveForm.name.text()))

      saveFile = open(self.currentPlaylist, 'w')
      saveFile.write("Major " + str(self.majorVersion) + "\n")
      saveFile.write("Minor " + str(self.minorVersion) + "\n")
      for row in range(self.rowCount()):
         item = self.item(row, 0)
         saveFile.write("File\n")
         saveFile.write("   Filename " + item.filename + "\n")
         
      self.playlistSaved.emit()


   def loadPlaylist(self, playlist):
      reader = NTreeReader(playlist)

      major = int(reader.read(0, "Major"))
      if major != self.majorVersion:
         message = QMessageBox()
         message.setText("Playlist file version mismatch")
         message.exec_()
         return
         
      self.clearPlaylist()

      for node in reader:
         filename = ""
         filename = node.readLine(filename, "Filename")
         self.add(filename)
         
      self.currentPlaylist = playlist


   def leaveEvent(self, event):
      self.clearSelection()


   def checkComplete(self):
      if self.fieldsPopulated():
         self.timer.stop()
      else:
         for row in range(self.rowCount()):
            titleItem = self.item(row, 0)
            timeItem = self.item(row, 1)
            
            if titleItem.info.finished():
               if titleItem.info.title != "":
                  titleItem.setText(titleItem.info.title)
               timeItem.setText(MPlayer.formatTime(titleItem.info.time))
               timeItem.time = titleItem.info.time
               timeItem.seekScale = titleItem.info.seekScale
               if row == self.current:
                  self.currentTimeUpdated.emit()


   def fieldsPopulated(self):
      """Check if all of the fields of the playlist have been populated by the async threads"""
      for row in range(self.rowCount()):
         titleItem = self.item(row, 0)
         timeItem = self.item(row, 1)
         if not timeItem or not (titleItem.info.finished() and titleItem.info.time == timeItem.time):
            return False
      return True


   def contextMenuEvent(self, event):
      menu = QMenu()
      menu.addAction("Delete", self.deleteClicked)
      menu.exec_(event.globalPos())


   def deleteClicked(self):
      self.removeRow(self.currentRow())
            
               
               
