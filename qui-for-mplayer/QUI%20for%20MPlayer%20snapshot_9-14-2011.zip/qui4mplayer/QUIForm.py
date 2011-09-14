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
from QUITableWidget import *
from MPlayer import *
from NTreeReader import *
from OptionsForm import *
from QUIButton import *
from VideoOutput import *
from AddDialog import *
from PlaylistFileInfo import *
import sys, random, os, imp

class QUIForm(QDialog):
   def __init__(self, parent = None):
      QWidget.__init__(self, parent)
      self.settingsMajor = 1
      self.settingsMinor = 1
      self.fileNotification = False
      self.disableSeek = False
      self.oldWidth = self.width()
      self.oldHeight = self.height()
      self.traceEnabled = False # Debugging, always shut this off before release

      if sys.version_info[0] >= 2 and sys.version_info[1] >= 6:
         import multiprocessing, threading
         try:
            count = multiprocessing.cpu_count()
            PlaylistFileInfo.limitRunning = threading.Semaphore(count)
         except:
            pass # Means we couldn't get the CPU count, just leave it at 1

      self.loadSettings()

      self.videoOutput = VideoOutput(self, self.keyPressHandler)
      self.videoOutput.fullscreenDisabled.connect(self.fullscreenDisabled)
      self.videoOutput.controls.playButton.clicked.connect(self.playClicked)
      self.videoOutput.controls.timeSlider.sliderMoved.connect(self.sliderMoved)
      self.videoOutput.controls.timeSlider.sliderReleased.connect(self.fsSliderReleased)
      self.videoOutput.controls.timeSlider.valueChanged.connect(self.seek)

      self.resize(400, 400)
      self.setWindowTitle("QUI for MPlayer")

      if os.name == "nt":
         self.setWindowIcon(QIcon('images/play.png'))
      else:
        self.setWindowFlags(Qt.SubWindow)
      self.setAttribute(Qt.WA_QuitOnClose)
      self.setFocusPolicy(Qt.ClickFocus)

      self.ensureDirectories()

      splitterLayout = QGridLayout(self)
      self.splitter = QSplitter()
      self.splitter.setHandleWidth(10)
      splitterLayout.addWidget(self.splitter, 0, 0)

      mainLayout = QVBoxLayout()
      mainLayout.setContentsMargins(0, 0, 0, 0)
      self.mainWidget = QWidget()
      self.mainWidget.setLayout(mainLayout)
      self.splitter.addWidget(self.mainWidget)
      self.addVideoOutput()

      self.createMainButtons(mainLayout)
      self.createPlaylist(mainLayout)
      if os.name == "nt":
         pass
      else:
         self.createTrayIcon()

      self.fileList.doubleClicked.connect(self.fileDoubleClicked)
      self.fileList.currentTimeUpdated.connect(self.updateTime)

      self.timer = QTimer()
      self.timer.setInterval(1000)
      self.timer.timeout.connect(self.timerUpdate)
      self.currentTime = 0

      self.fillPlaylistBox()

      random.seed()

      self.optionsForm = OptionsForm(self)

      self.applySettings()

      self.mplayer = MPlayer(self.videoOutput.videoLabel, self.buildMPlayerOptions())
      self.mplayer.fileFinished.connect(self.nextClicked)
      self.mplayer.playbackStarted.connect(self.playbackStarted)
      self.mplayer.foundAspect.connect(self.setAspect)
      self.mplayer.foundVolume.connect(self.volumeSlider.setValue)
      self.mplayer.foundVideo.connect(self.showVideo)
      self.mplayer.loadedNewFile.connect(self.newFileLoaded)
      self.mplayer.process.finished.connect(self.syncWithMPlayer)

      self.mplayer.logWidget = self.optionsForm.logText

      filters = ["Multimedia Files (*.mp3 *.wav *.wma *.ogg *.mpg *.mpeg *.avi *.wmv)",
                "All Files (*.*)"]
      self.addFileDialog = QFileDialog(self, "Add Files or Folders", os.path.expanduser("~"))
      self.addFileDialog.setNameFilters(filters)

      self.handleArguments()

      self.show()


   def createMainButtons(self, mainLayout):
      layout = QHBoxLayout()
      mainLayout.addLayout(layout)
      mainLayout.setStretchFactor(layout, 10)

      playButton = QUIButton()
      playButton.setMaximumSize(75, 75)
      playButton.setMinimumSize(75, 75)
      playButton.setPixmap("Play.png")
      playButton.clicked.connect(self.playClicked)
      layout.addWidget(playButton)
      self.playButton = playButton

      nextButton = QUIButton()
      nextButton.setMaximumSize(50, 50)
      nextButton.setMinimumSize(50, 50)
      nextButton.setPixmap("Next.png")
      nextButton.clicked.connect(self.nextClicked)
      layout.addWidget(nextButton)

      innerLayout = QVBoxLayout()
      layout.addLayout(innerLayout)

      title = QLabel("Title")
      title.setMinimumWidth(100)
      innerLayout.addWidget(title)
      self.titleLabel = title

      artist = QLabel("Artist")
      artist.setMinimumWidth(100)
      innerLayout.addWidget(artist)
      self.artistLabel = artist

      timeLabel = QLabel("Time")
      innerLayout.addWidget(timeLabel)
      self.timeLabel = timeLabel

      timeSlider = QSlider()
      timeSlider.setOrientation(Qt.Horizontal)
      timeSlider.setMinimumSize(100, 0)
      timeSlider.setPageStep(10)
      timeSlider.sliderMoved.connect(self.sliderMoved)
      timeSlider.sliderReleased.connect(self.sliderReleased)
      timeSlider.valueChanged.connect(self.seek)
      innerLayout.addWidget(timeSlider)
      self.timeSlider = timeSlider


      volumeSlider = QSlider()
      volumeSlider.setOrientation(Qt.Vertical)
      volumeSlider.sliderMoved.connect(self.setVolume)
      volumeSlider.valueChanged.connect(self.setVolume)
      volumeSlider.setRange(0, 100)
      layout.addWidget(volumeSlider)
      self.volumeSlider = volumeSlider


   def createPlaylist(self, mainLayout):
      layout = QHBoxLayout()

      self.playlistBox = QComboBox()
      self.playlistBox.activated[str].connect(self.playlistSelected)

      layout.addWidget(self.playlistBox)
      layout.setStretchFactor(self.playlistBox, 50)

      self.playlistMenu = QMenu()

      playlistMenuButton = QPushButton("Actions")
      playlistMenuButton.setMenu(self.playlistMenu)

      layout.addWidget(playlistMenuButton)
      layout.setStretchFactor(playlistMenuButton, 10)

      mainLayout.addLayout(layout)

      self.fileList = QUITableWidget()
      self.fileList.playlistSaved.connect(self.fillPlaylistBox)

      mainLayout.addWidget(self.fileList)
      mainLayout.setStretchFactor(self.fileList, 100)

      # Has to be done after creating fileList
      self.populatePlaylistMenu()


   def populatePlaylistMenu(self):
      self.playlistMenu.addAction("Clear Playlist", self.fileList.clearPlaylist)
      self.playlistMenu.addAction("Save Playlist", self.fileList.savePlaylist)
      self.playlistMenu.addAction("Load Playlist", self.loadPlaylist)
      self.playlistMenu.addSeparator()
      self.playlistMenu.addAction("Add File(s)...", self.showAddFileDialog)
      self.playlistMenu.addAction("Add Folder...", self.showAddFolderDialog)
      self.playlistMenu.addAction("Add Special...", self.showAddSpecialDialog)
      self.playlistMenu.addSeparator()

      self.loopAction = QAction("Loop", self)
      self.loopAction.setCheckable(True)
      self.loopAction.setChecked(True)
      self.playlistMenu.addAction(self.loopAction)

      self.stopAfterCurrentAction = QAction("Stop After Current", self)
      self.stopAfterCurrentAction.setCheckable(True)
      self.playlistMenu.addAction(self.stopAfterCurrentAction)

      self.randomAction = QAction("Random", self)
      self.randomAction.setCheckable(True)
      self.playlistMenu.addAction(self.randomAction)

      self.randomFirstAction = QAction("Random First", self)
      self.randomFirstAction.setCheckable(True)
      self.playlistMenu.addAction(self.randomFirstAction)

      self.playlistMenu.addSeparator()
      self.fullscreenAction = QAction("Fullscreen", self)
      self.fullscreenAction.setCheckable(True)
      self.fullscreenAction.triggered.connect(self.videoOutput.setFullscreen)
      self.playlistMenu.addAction(self.fullscreenAction)

      self.fitToWidthAction = QAction("Fit To Width", self)
      self.fitToWidthAction.setCheckable(True)
      self.fitToWidthAction.triggered.connect(self.videoOutput.setFitToWidth)
      self.playlistMenu.addAction(self.fitToWidthAction)

      self.playlistMenu.addSeparator()
      self.optionsAction = QAction("Options...", self)
      self.optionsAction.triggered.connect(self.showOptions)
      self.playlistMenu.addAction(self.optionsAction)


   def createTrayIcon(self):
      self.trayIconMenu = QMenu()
      self.trayIconMenu.addAction("Play/Pause", self.playClicked)
      self.trayIconMenu.addAction("Next", self.nextClicked)
      self.trayIconMenu.addSeparator()
      self.trayIconMenu.addAction("Quit", self.close)

      self.trayIcon = QSystemTrayIcon(self)
      self.trayIcon.setToolTip("QUI for MPlayer")
      self.setTrayIcon("Pause.png")
      self.trayIcon.setContextMenu(self.trayIconMenu)
      self.trayIcon.activated.connect(self.iconActivated)
      self.trayIcon.show()


   def handleArguments(self):
      for path in sys.argv[1:]:
         self.fileList.add(path)

      if len(sys.argv) > 1:
         self.playClicked()


   def buildMPlayerOptions(self):
      retval = self.optionsForm.optionsBox.text()
      if self.optionsForm.deinterlaceCheck.isChecked():
         retval += " -vf-add yadif"
      if self.optionsForm.stopXScreensaverCheck.isChecked():
         retval += " -stop-xscreensaver"
      return retval


   def closeEvent(self, event):
      self.trace("closeEvent")
      # Check that mplayer is ended
      self.mplayer.end()
      self.saveSettings()
      event.accept()


   def playClicked(self):
      self.trace("playClicked")
      if self.mplayer.filename == "":
         self.nextClicked()
      else:
         self.mplayer.play()

      self.syncWithMPlayer()

   def syncWithMPlayer(self):
      if os.name == "nt":
        pass
      else:
         self.trace("syncWithMPlayer")
         if self.mplayer.playing:
            if self.mplayer.inPlayback:
               self.timer.start()
            self.setTrayIcon("Play.png")
            self.playButton.setPixmap("Pause.png")
            self.videoOutput.controls.playButton.setPixmap("PauseSmall.png")
         else:
            self.timer.stop()
            self.setTrayIcon("Pause.png")
            self.playButton.setPixmap("Play.png")
            self.videoOutput.controls.playButton.setPixmap("PlaySmall.png")

         self.titleLabel.setText(self.mplayer.title)
         self.titleLabel.setToolTip(self.mplayer.title)

         self.artistLabel.setText(self.mplayer.artist)
         self.artistLabel.setToolTip(self.mplayer.artist)


   def nextClicked(self):
      self.trace("nextClicked")
      self.mplayer.loadFile(self.nextFile())
      self.syncWithMPlayer()


   def nextFile(self):
      self.trace("nextFile")
      if self.fileList.rowCount() < 1:
         return ""

      if (not self.loopAction.isChecked() and self.fileList.current >= self.fileList.rowCount() - 1) or self.stopAfterCurrentAction.isChecked():
         self.fileList.current = -1
         return ""

      if not self.randomAction.isChecked() and not (self.randomFirstAction.isChecked() and self.fileList.current == -1):
         self.fileList.current += 1
         if self.fileList.current >= self.fileList.rowCount():
            self.fileList.current = 0
      else:
         self.fileList.current = random.randint(0, self.fileList.rowCount() - 1)

      self.fileList.updateHighlight()

      return self.fileList.item(self.fileList.current, 0).filename


   def fileDoubleClicked(self, index):
      self.trace("fileDoubleClicked")
      self.fileList.current = index.row()
      self.fileList.updateHighlight()
      self.mplayer.loadFile(self.fileList.item(index.row(), 0).filename)
      self.playButton.setPixmap("Pause.png")
      if not self.mplayer.playing:
         self.mplayer.play()


   def playbackStarted(self):
      self.trace("playbackStarted")
      self.syncWithMPlayer()

      self.currentTime = 0
      self.disableSeek = True
      self.timeSlider.setValue(0)
      self.videoOutput.controls.timeSlider.setValue(0)
      self.disableSeek = False
      self.updateTime()
      self.timer.start()

      if self.fileNotification:
         messageText = self.mplayer.title + " by " + self.mplayer.artist
         self.trayIcon.showMessage("Now playing", messageText, msecs = 5000)


   def setAspect(self):
      if self.mplayer.aspect > .0001:
         self.videoOutput.setSize(self.mplayer.aspect * 1000, 1000)
         # Need to trigger a resize event in order to make sure the video is resized correctly for the new aspect
         # Resize to same size won't do the trick
         self.videoOutput.resize(1, 1)
         self.videoOutput.resize(self.videoOutput.width(), self.videoOutput.height())


   def updateTime(self):
      currentItem = self.fileList.item(self.fileList.current, 1)
      playlistTime = currentItem.time
      if playlistTime != 0:
         self.mplayer.length = playlistTime
         self.mplayer.seekScale = currentItem.seekScale
      self.fillTimeLabel()
      self.timeSlider.setMaximum(self.mplayer.length)
      self.videoOutput.controls.timeSlider.setMaximum(self.mplayer.length)


   def timerUpdate(self):
      self.trace("timerUpdate")
      self.currentTime += 1
      self.disableSeek = True
      if self.currentTime > self.mplayer.length:
         self.mplayer.length = self.currentTime
         self.timeSlider.setMaximum(self.mplayer.length)
         self.videoOutput.controls.timeSlider.setMaximum(self.mplayer.length)

      if not self.timeSlider.isSliderDown() and not self.videoOutput.controls.timeSlider.isSliderDown():
         self.fillTimeLabel()
         self.timeSlider.setValue(self.currentTime)
         self.videoOutput.controls.timeSlider.setValue(self.currentTime)
      self.disableSeek = False


   # Don't need separate versions of this function because the value is passed in, and it doesn't matter
   # which slider it came from.
   def sliderMoved(self, value):
      self.trace("sliderMoved")
      self.fillTimeLabel(value)

   def sliderReleased(self):
      self.trace("sliderReleased")
      value = self.timeSlider.value()
      self.seek(value)

   def fsSliderReleased(self):
      self.trace("fsSliderReleased")
      value = self.videoOutput.controls.timeSlider.value()
      self.seek(value)


   def seek(self, value):
      self.trace("seek")
      if not self.disableSeek and not self.timeSlider.isSliderDown() and not self.videoOutput.controls.timeSlider.isSliderDown():
         self.mplayer.seek(value)
         self.currentTime = value
         self.fillTimeLabel()


   def fillTimeLabel(self, time = None):
      if time == None:
         time = self.currentTime
      self.timeLabel.setText(self.mplayer.formattedTime(time) + "/" + self.mplayer.formattedTime())
      self.videoOutput.controls.timeLabel.setText(self.timeLabel.text())
      self.trayIcon.setToolTip("QUI for MPlayer\n" + self.mplayer.title + " by " + self.mplayer.artist + "\n" + self.timeLabel.text())


   def fillPlaylistBox(self):
      directory = os.path.expanduser("~/.qui/Playlists")
      files = os.listdir(directory)
      files.sort()

      self.playlistBox.clear()

      for f in files:
         self.playlistBox.addItem(f)

      self.playlistBox.setCurrentIndex(-1)


   def playlistSelected(self, selected):
      self.trace("playlistSelected")
      directory = os.path.expanduser("~/.qui/Playlists")
      f = os.path.join(directory, str(selected))
      self.fileList.loadPlaylist(f)


   def ensureDirectories(self):
      base = os.path.expanduser("~/.qui")
      playlists = os.path.join(base, "Playlists")

      if not os.path.exists(base):
         os.mkdir(base)
      if not os.path.exists(playlists):
         os.mkdir(playlists)


   def saveSettings(self):
      self.trace("saveSettings")
      with open(os.path.expanduser("~/.qui/settings"), 'w') as f:
         f.write("Major " + str(self.settingsMajor))
         f.write("\n")
         f.write("Minor " + str(self.settingsMinor))
         f.write("\n")
         f.write("Loop " + str(self.loopAction.isChecked()))
         f.write("\n")
         # I'm leaving this one out for the moment because it doesn't make sense to save it between runs - the reading code
         # is still there though so it can just be uncommented if it needs to be saved in the future.
         #f.write("StopAfterCurrent " + str(self.stopAfterCurrentAction.isChecked()))
         #f.write("\n")
         f.write("Random " + str(self.randomAction.isChecked()))
         f.write("\n")
         f.write("RandomFirst " + str(self.randomFirstAction.isChecked()))
         f.write("\n")
         f.write("MPlayerOptions " + self.optionsForm.optionsBox.text())
         f.write("\n")
         f.write("FileNotification " + str(self.fileNotification))
         f.write("\n")
         f.write("Deinterlace " + str(self.optionsForm.deinterlaceCheck.isChecked()))
         f.write("\n")
         f.write("StopXScreensaver " + str(self.optionsForm.stopXScreensaverCheck.isChecked()))


   def loadSettings(self):
      self.trace("loadSettings")
      try:
         self.reader = NTreeReader(os.path.expanduser("~/.qui/settings"))
      except IOError:
         self.reader = NTreeReader()
         print "Settings file not found, will use defaults"


   def applySettings(self):
      self.trace("applySettings")
      self.loopAction.setChecked(self.reader.read("True", "Loop")[0] == "T")
      self.stopAfterCurrentAction.setChecked(self.reader.read("False", "StopAfterCurrent")[0] == "T")
      self.randomAction.setChecked(self.reader.read("False", "Random")[0] == "T")
      self.randomFirstAction.setChecked(self.reader.read("False", "RandomFirst")[0] == "T")
      self.optionsForm.optionsBox.setText(self.reader.readLine("", "MPlayerOptions"))
      self.optionsForm.notificationCheck.setChecked(self.reader.read("False", "FileNotification")[0] == "T")
      self.optionsForm.deinterlaceCheck.setChecked(self.reader.read("True", "Deinterlace")[0] == "T")
      self.optionsForm.stopXScreensaverCheck.setChecked(self.reader.read("True", "StopXScreensaver")[0] == "T")
      self.fileNotification = (self.reader.read("False", "FileNotification")[0] == "T")


   def showOptions(self):
      self.trace("showOptions")
      self.optionsForm.exec_()

      if self.optionsForm.accepted:
         self.mplayer.extraOptions = self.buildMPlayerOptions()
         self.fileNotification = self.optionsForm.notificationCheck.isChecked()
         messageBox = QMessageBox()
         messageBox.setText("MPlayer must be restarted to apply new options.  Restart it now?")
         messageBox.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
         messageBox.setDefaultButton(QMessageBox.Yes)
         messageBox.setWindowTitle("Restart Required")
         ret = messageBox.exec_()

         if ret == QMessageBox.Yes:
            self.mplayer.restart()


   def setVolume(self, vol):
      self.trace("setVolume")
      self.mplayer.setVolume(vol)


   def loadPlaylist(self):
      selectedPlaylist = QFileDialog.getOpenFileName(self, "Open Playlist")
      if selectedPlaylist != "":
         self.fileList.loadPlaylist(selectedPlaylist)


   def iconActivated(self, reason):
      if reason == QSystemTrayIcon.Trigger:
         self.show()  # Urgh, I hate working around bugs in WM's
         self.hide()
         self.show()
      elif reason == QSystemTrayIcon.MiddleClick:
         self.playClicked()



   def main_is_frozen(self):
      return (hasattr(sys, "frozen") or # new py2exe
              hasattr(sys, "importers") # old py2exe
              or imp.is_frozen("__main__")) # tools/freeze


   def get_main_dir(self):
      if self.main_is_frozen():
            return os.path.abspath(os.path.dirname(sys.executable))
      else:
         return os.path.dirname(__file__)


   def setTrayIcon(self, filename):
      base = os.path.join(self.get_main_dir(), "images")
      self.trayIcon.setIcon(QIcon(os.path.join(base, filename)))


   def changeEvent(self, event):
      if event.type() == QEvent.WindowStateChange and self.isMinimized():
         self.hide()
         self.setWindowState(self.windowState() & ~Qt.WindowMinimized)
         event.accept()
      else:
         QDialog.changeEvent(self, event)


   def showVideo(self):
      self.trace("showVideo")
      doResize = False
      if not self.videoOutput.isVisible():
         doResize =  True
         self.oldWidth = self.width()
         self.oldHeight = self.height()
         newWidth = self.width() + 400
      self.videoOutput.show()
      self.videoOutput.setSize(self.mplayer.width, self.mplayer.height)
      if doResize:
         saveWidth = self.mainWidget.width() + self.splitter.handleWidth() / 2
         self.resize(newWidth, self.height())
         self.splitter.moveSplitter(saveWidth, 1)

      self.videoOutput.setFullscreen(False) # If we were fullscreen previously, MPlayer starting a new file is going to mess us up anyway


   def newFileLoaded(self):
      self.trace("newFileLoaded")
      if self.videoOutput.isVisible():
         self.resize(self.oldWidth, self.oldHeight)
         self.videoOutput.hide()


   def saveSplitterPosition(self):
      self.splitterState = self.splitter.saveState()


   def fullscreenDisabled(self):
      self.trace("fullscreenDisabled")
      self.addVideoOutput()
      self.fullscreenAction.setChecked(False)
      self.splitter.restoreState(self.splitterState)


   def addVideoOutput(self):
      self.trace("addVideoOutput")
      self.splitter.addWidget(self.videoOutput)


   def keyPressEvent(self, event):
      if not self.keyPressHandler(event):
         QDialog.keyPressEvent(self, event)


   def keyPressHandler(self, event):
      if event.key() == Qt.Key_Space:
         self.playClicked()
      elif event.key() == Qt.Key_F:
         self.videoOutput.setFullscreen(not self.videoOutput.fullscreen)
      elif event.key() == Qt.Key_Left:
         self.currentTime -= 10
         if self.currentTime < 0:
            self.currentTime = 0
         self.mplayer.seek(self.currentTime)
      elif event.key() == Qt.Key_Right:
         self.currentTime += 10
         if self.currentTime > self.mplayer.length:
            self.currentTime = self.mplayer.length
         self.mplayer.seek(self.currentTime)
      elif event.key() == Qt.Key_Escape:
         self.videoOutput.setFullscreen(False)
      else:
         return False
      return True


   def showAddFileDialog(self):
      self.addFileDialog.setFileMode(QFileDialog.ExistingFiles)
      self.showFileFolderDialog()

   def showAddFolderDialog(self):
      self.addFileDialog.setFileMode(QFileDialog.Directory)
      self.showFileFolderDialog()

   def showFileFolderDialog(self):
      if self.addFileDialog.exec_() == QDialog.Accepted:
         for f in self.addFileDialog.selectedFiles():
            self.fileList.add(str(f))


   def showAddSpecialDialog(self):
      dialog = AddDialog(self)
      dialog.exec_()


   def trace(self, text):
      if self.traceEnabled:
         print text
