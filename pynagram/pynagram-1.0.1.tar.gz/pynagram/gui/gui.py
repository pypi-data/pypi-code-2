#!/usr/bin/env python
#
#     gui.py
#
#     Copyright (c) 2009, 2010, 2011 Umang Varma <umang.me@gmail.com>.
#
#     This file is part of Pynagram
#
#     Pynagram is free software: you can redistribute it and/or modify
#     it under the terms of the GNU General Public License as published by
#     the Free Software Foundation, either version 3 of the License, or
#     (at your option) any later version.
#
#     Pynagram is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU General Public License for more details.
#
#     You should have received a copy of the GNU General Public License
#     along with Pynagram. If not, see <http://www.gnu.org/licenses/>.
#

from PyQt4 import QtCore, QtGui
from qt_struct import Ui_MainWindow
from qt_about import Ui_About
from qt_wl import Ui_Wordlists

import random
import time


from pynagram.backend import anagram

class About(QtGui.QDialog):
    """This class is the About Dialog"""

    def __init__(self, parent=None, icon=None):
        QtGui.QWidget.__init__(self, parent)
        self.ui = Ui_About()
        self.ui.setupUi(self)
        wind_icon = icon or QtGui.QIcon()
        self.setWindowIcon(wind_icon)

    def start(self):
        self.show()

class Wordlists(QtGui.QDialog, Ui_Wordlists):
    """This class is the Word lists Dialog"""

    def __init__(self, parent=None, icon=None, config=None):
        self.config = config
        QtGui.QWidget.__init__(self, parent)
        self.setupUi(self)
        wind_icon = icon or QtGui.QIcon()
        self.setWindowIcon(wind_icon)
        #
        QtCore.QObject.connect(self.pb_save, QtCore.SIGNAL("clicked()"), \
                                                self.saveconfig)
        QtCore.QObject.connect(self.pb_cancel, QtCore.SIGNAL("clicked()"), \
                                                self.cancelconfig)
        QtCore.QObject.connect(self.pb_add, QtCore.SIGNAL("clicked()"), \
                                                self.addwl)
        QtCore.QObject.connect(self.pb_remove, QtCore.SIGNAL("clicked()"), \
                                                self.removewl)
        #
        self.wls.__class__.dragEnterEvent = self.dragEnterEvent
        self.wls.__class__.dragMoveEvent = self.dragEnterEvent
        self.wls.__class__.dropEvent = self.drop
        self.readfromconfig()
       # 
    
    def addwl(self):
        files = list(QtGui.QFileDialog.getOpenFileNames(self, "Select word " + \
                "lists", "", "Text Files (*.txt);; All Files (*)"))
        for wl in files:
            self.config["wordlists"].append(str(wl))
        self.readfromconfig()

    def removewl(self):
        current_row = self.wls.currentRow()
        self.config["wordlists"].pop(current_row)
        self.readfromconfig()
        self.wls.setCurrentRow((self.wls.count() > current_row and current_row)
                or current_row -1)

    def saveconfig(self):
        self.config["wordlist"] = self.wls.currentRow()
        self.config.writeconfig()
        self.config.changed = True
        self.close()

    def cancelconfig(self):
        self.config.readconfig()
        self.close()

    def dragEnterEvent(self, event):
        if (event.mimeData().hasFormat("text/uri-list") or
                event.mimeData().hasFormat("text/plain")):
            event.accept()
        else:
            event.reject()

    def drop(self, event):
        data = event.mimeData()
        if data.hasFormat("text/uri-list"):
            self.config["wordlists"].extend( \
                    [str(x.toLocalFile()) for x in data.urls()])
            self.readfromconfig()
        elif data.hasFormat("text/plain"):
            path = "%s/wl%d.txt"%(self.config.pathtoconfig(), time.time())
            fsock = open(path , "w")
            fsock.write(data.text())
            fsock.close()
            self.config["wordlists"].append(path)
            self.readfromconfig()
    
    def readfromconfig(self):
        self.wls.clear()
        self.wls.addItems(self.config["wordlists"])
        self.wls.setCurrentRow(self.config["wordlist"])

class App(QtGui.QMainWindow):
    """This class handles the GUI."""

    def __init__(self, parent=None, config=None):
        """Initializes the code for the GUI"""
        self.pynagram = anagram.Anagram()
        self.config = config
        self.typed = []
        self.available_letters = []
        self.widgets = {}
        self.last_word = ""
        self.last_word_color = "000"
        self.solved = False
        self.time_started = 0
        self.time_elapsed = 0
        self.times_shuffled = 0
        self.timer = QtCore.QTimer()
        self.shuffle_timer = QtCore.QTimer()
        #
        QtGui.QWidget.__init__(self, parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.wind_icon = QtGui.QIcon()
        self.wind_icon.addFile('/usr/share/pixmaps/pynagram.xpm')
        self.wind_icon.addFile('icons/pixmaps/pynagram.xpm')
        self.setWindowIcon(self.wind_icon)
        #
        QtCore.QObject.connect(self.ui.actionSolve, \
                    QtCore.SIGNAL("triggered()"), self.actionSolve_activate)
        QtCore.QObject.connect(self.ui.actionNew, \
                        QtCore.SIGNAL("triggered()"), self.actionNew_activate)
        QtCore.QObject.connect(self.ui.actionAbout, \
                    QtCore.SIGNAL("triggered()"), self.actionAbout_activate)
        QtCore.QObject.connect(self.ui.actionWordlists, \
                QtCore.SIGNAL("triggered()"), self.actionWordlists_activate)
        QtCore.QObject.connect(self.timer, QtCore.SIGNAL("timeout()"), \
                                                    self.__update_status_bar)
        QtCore.QObject.connect(self.shuffle_timer, QtCore.SIGNAL("timeout()"),\
                                                                self.__shuffle)
        self.timer.start(1000)

    def init_game(self):
        """Initializes a game."""
        self.pynagram.start_new()
        self.available_letters = self.pynagram.letters[:]
        self.last_word = ""
        self.typed = []
        self.show()
        random.shuffle(self.available_letters)
        self.time_started = time.time()
        self.__reflect_letters()
        self.__update_words()
        self.times_shuffled = 0
        self.shuffle_timer.start(25)
        self.time_started = time.time()

    def __shuffle(self):
        """Shuffles the letters"""
        if self.times_shuffled < 10:
            random.shuffle(self.available_letters)
            self.resize(self.sizeHint())
            self.times_shuffled += 1
            self.__reflect_letters()
        else:
            self.shuffle_timer.stop()

    def __reflect_letters(self):
        """Updates the labels in the GUI

        to reflect the state of the variables in this class."""
        self.ui.l_avail.setText(" ".join(self.available_letters))
        self.ui.l_typed.setText(" ".join(self.typed))
        self.ui.l_last.setText(("Last word: <b><font color=\"#%s\">" + \
        "%s</font></b>") % (self.last_word_color, self.last_word))

    def __update_words(self):
        """Updates the list of words in the Pynagram window"""
        a_words = self.pynagram.words.keys()
        a_words.sort()
        a_words.sort(lambda x, y: len(x) - len(y))
        if not False in self.pynagram.words.values():
            self.solved = True
        per_column = len(a_words)/5 + 1
        for x in xrange(0, 5):
            words = [((self.pynagram.words[word] or self.solved) and word) \
                or "_ " * len(word) for word in \
                        a_words[x*per_column:(x+1)*per_column]]
            getattr(self.ui, "l_solved_" + str(x+1)).setText(\
                "<br>".join([(word in self.pynagram.words and \
                self.pynagram.words[word] and self.solved and \
                (" <b>%s</b>"%word)) or word for \
                word in words]))
        self.__update_status_bar()

    def __update_status_bar(self):
        s_time = ""
        if not (self.solved or self.pynagram.solved_all):
            self.time_elapsed = int(time.time() - self.time_started)
        if self.time_elapsed >= 300 and not self.solved:
            self.solved = True
            self.actionSolve_activate()
        s_time = "Time: %s" % (time.strftime("%M:%S", \
                            time.gmtime(300 - self.time_elapsed)))
        s_score = "Score: %d" % self.pynagram.score
        self.ui.statusbar.showMessage(s_score + "\t" + s_time)

    def actionNew_activate(self):
        self.solved = False
        if not self.pynagram.qualified:
            self.pynagram.clear_all()
        self.init_game()

    def actionAbout_activate(self):
        w_about = About(icon=self.wind_icon)
        w_about.exec_()

    def actionWordlists_activate(self):
        self.config.changed = False
        w_wl = Wordlists(icon = self.wind_icon, config = self.config)
        w_wl.exec_()
        self.config.readconfig() # Reverts any unsaved config 
        if self.config.changed:
            self.config.changed = False
            wl = self.config["wordlists"][self.config.setdefault("wordlist", 0)]
            self.pynagram.read_from_file(wl)
            self.pynagram.qualified = False
            self.actionNew_activate()

    def actionSolve_activate(self):
        self.available_letters.extend(self.typed)
        self.typed = []
        self.__update_status_bar()
        self.solved = True
        self.__reflect_letters()
        self.__update_words()
        
    
    def keyPressEvent(self, event):
        if not self.solved:
            key = int(event.key())
            if 64 < key < 123 and chr(key).lower() in self.available_letters:
                # If an available letter has been typed
                letter = chr(key).lower()
                self.typed.append(letter)
                self.available_letters.remove(letter)
            elif key == 16777216:
                # Escape
                self.available_letters.extend(self.typed)
                self.typed = []
            elif key == 16777219 and len(self.typed) > 0:
                # Backspace
                self.available_letters.append(self.typed.pop())
            elif key == 32:
                # Spacebar
                random.shuffle(self.available_letters)
            elif key == 16777221 or key == 16777220:
                # Enter
                word = "".join(self.typed)
                result, already_typed = self.pynagram.guess(word)
                if already_typed:
                    self.last_word_color = "ff0"
                elif (not already_typed) and result:
                    self.last_word_color = "0f0"
                else:
                    self.last_word_color = "f00"
                self.last_word = word
                self.available_letters.extend(self.typed)
                self.typed = []
                self.__update_words()
            self.__reflect_letters()
