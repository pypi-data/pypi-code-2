#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
A GUI interface to cuevanaapi
"""

import os
import sys
import urllib
import subprocess
from multiprocessing import Process

from PyQt4 import QtGui, QtCore

from . import __version__
import cuevanaapi
from downloaders import megaupload
import utils

from ConfigParser import SafeConfigParser

# cli.__doc__ = ("CuevanaLinks %s - 2011 Martin Gaitán\n"
#               "A program to retrieve movies and series "
#               "(or links to them) from cuevana.tv"
#                % __version__ )

def get_config():
    """
    """
    DEFAULT_PATH = os.path.join(os.path.expanduser("~"), "")
    CONFIG_FILE = os.path.join(DEFAULT_PATH, '.cuevanalinks.cfg')
    
    DEFAULTS = { 'main': {
                    "player": "mplayer -fs {file}",
                    "file_format": "long", 
                  # "download_dir_show": os.path.join( DEFAULT_PATH, "Videos",
                  #                                     "{show}", "{season}"),
                  # "download_dir_movie": os.path.join( DEFAULT_PATH, "Videos",
                  #                                     "{title}" ),
                        },
                }
    config = SafeConfigParser()
    if not os.path.exists(CONFIG_FILE):
        print "There is no config file. Creating default %s" % CONFIG_FILE
        for section, options in DEFAULTS.items():
            for section, options in DEFAULTS.items():
                if not config.has_section(section):
                    config.add_section(section)
                for option, value in options.items():
                    config.set(section, option, value)

        with open(CONFIG_FILE, 'w') as cfg:
            config.write(cfg)
    else:
        with open(CONFIG_FILE, 'r') as cfg:
            config.readfp(cfg)
        
    return config

def background_process(command_list):
    return subprocess.call(command_list,  stdout=subprocess.PIPE, 
                    stderr=subprocess.PIPE)
    

class ListModel(QtCore.QAbstractListModel): 
    def __init__(self, datain, parent=None, *args): 
        """ datain: a list where each item is a row
        """
        QtCore.QAbstractListModel.__init__(self, parent, *args) 
        self.listdata = datain
 
    def rowCount(self, parent=QtCore.QModelIndex()): 
        return len(self.listdata) 
 
    def data(self, index, role): 
        if index.isValid() and role == QtCore.Qt.DisplayRole:
            return QtCore.QVariant(self.listdata[index.row()])
        else: 
            return QtCore.QVariant()


class ContentFrame(QtGui.QFrame):
    def __init__(self):
        super(ContentFrame, self).__init__()
        layout = QtGui.QGridLayout()
        self.title_thumbnail = QtGui.QLabel()
        self.title = QtGui.QLabel()
        self.title_plot = QtGui.QLabel()
        self.title_sources = QtGui.QLabel()
        self.title_subs = QtGui.QLabel()
        for item in self.title_sources, self.title_subs:
            item.setOpenExternalLinks(True)

        for item in self.title, self.title_plot, self.title_sources:
            item.setWordWrap(True)

        layout.addWidget(self.title_thumbnail, 0, 0)
        layout.addWidget(self.title, 1, 0)
        layout.addWidget(self.title_plot, 2, 0)
        layout.addWidget(self.title_sources, 3, 0)
        layout.addWidget(self.title_subs, 4, 0)
        self.setLayout(layout)

class CuevanaGUI(QtGui.QFrame):
    def __init__(self):
        self.app = QtGui.QApplication(sys.argv)
        super(CuevanaGUI, self).__init__()
        self.setWindowTitle('CuevanaLinks %s' % __version__)
        self.resize(800, 600)
        layout = QtGui.QGridLayout()
        self.title = QtGui.QLineEdit(self)
        self.title.setPlaceholderText('Type in Movie/Serie or URL')
        self.title.setToolTip("Look for a movie or show with this title or URL. If it's not an URL and the next box is empty a movie is assummed")
        self.episode = QtGui.QLineEdit(self)
        self.episode.setPlaceholderText('Type in episode or season')
        self.episode.setToolTip("Specifies a season/episode of a show. Examples: S01 (a whole season), s02e04, 1x4. If next box is given retrieve the slices including limits")
        self.end = QtGui.QLineEdit(self)
        self.end.setPlaceholderText('Type in end of season/episode')
        self.end.setToolTip("Specifies the end of season/episode slices (including it). Examples: S01 (a whole season), s02e04, 1x4")
        self.check_subs= QtGui.QCheckBox('Download subtitles (if available)', self)
        self.check_download = QtGui.QCheckBox('Download the contents instead of showing their links', self)
        self.check_play = QtGui.QCheckBox("Play while download. This automatically buffer enough data\n"
            "before call the player. It's possible to define the player\ncommand in the config file", self)
        self.cb_languages = QtGui.QComboBox(self)

        for lang in ('es', 'en', 'pt'):
            self.cb_languages.addItem(lang)

        self.cb_languages.setEditable(False)
        self.cb_languages.setToolTip('Subtitles language')
        self.max_rate = QtGui.QLineEdit(self)
        self.max_rate.setPlaceholderText('Max download rate')
        self.main_list = QtGui.QListView(self)
        self.main_list.setFocus()
        self.content_frame = ContentFrame()
        self.lblStatus = QtGui.QLabel(self)
        layout.addWidget(self.title, 0, 0)
        layout.addWidget(self.episode, 0, 1)
        layout.addWidget(self.check_subs, 1, 0)
        layout.addWidget(self.end, 1, 1)
        layout.addWidget(self.check_download, 2, 0)
        layout.addWidget(self.cb_languages, 2, 1)
        layout.addWidget(self.check_play, 3, 0)
        layout.addWidget(self.max_rate, 3, 1)
        layout.addWidget(self.main_list, 4, 0)
        layout.addWidget(self.content_frame, 4, 1, 1, 2)
        layout.addWidget(self.lblStatus, 5, 0)
        self.setLayout(layout)
        self.center()
        self.title.returnPressed.connect(self.searchTerms)
        self.episode.returnPressed.connect(self.searchTerms)
        self.end.returnPressed.connect(self.searchTerms)
        self.main_list.clicked.connect(self.titlesClicked)

    def center(self):
        screen = QtGui.QDesktopWidget().screenGeometry()
        size = self.geometry()
        self.move((screen.width()-size.width())/2, (screen.height()-size.height())/2)

    def searchTerms(self):
        if self.title:
            self.lblStatus.clear()
            self.updateStatusLabel('Searching...')
            self.enabledItems(False)
            self.updateWindow()
            self.process_terms()

    def process_terms(self):
        if self.check_play.isChecked():
            download = True
	
        self.titles = []
        self.titles_content = []
        show_flag = False
        self.language =  str(self.cb_languages.currentText()).upper()
        filter = None if not self.check_download.isChecked() else 'megaupload'
        api = cuevanaapi.CuevanaAPI(filter)
	
        if str(self.title.text()).startswith(cuevanaapi.URL_BASE) and not str(self.episode.text()):
            try:
                self.updateStatusLabel("Retrieving...")
                content = cuevanaapi.dispatch(str(self.title.text()))
    	    except NotValidURL:
    	        print "Not valid URL of a cuevana's movie/episode"
    	    except Exception, e:        #Fix me
    	        print e
    	        print "Cuevana server has problem. Try in a few minutes"
    	        return
	
    	elif str(self.episode.text()):
    	    print "Searching '%s'...\n" % (str(self.title.text()))
    	    try:
    	        show = api.get_show(str(self.title.text()))
		        
    	        if show:
    	            episodes = show.get_episodes(str(self.episode.text()), str(self.end.text()))
                    for episode in episodes:
                        self.addContents(episode)
                else:
		            self.updateStatusLabel("Nothing found for '%s'." % str(self.title.text()))
            except Exception, e:            #Fix me
                self.updateStatusLabel('Error: %s' % e, True)
                #sys.exit("Cuevana server has problem. Try in a few minutes")

        else:
            #movie
            # print "Searching '%s'...\n" % str(self.title.text())
            try:
                results = api.search(str(self.title.text()))
                if results:
                    for result in results:
                        if isinstance(result, cuevanaapi.Show):
                            self.updateStatusLabel("A show was found for '%s'. "
                                  "Try defining an episode/season" % str(self.title.text()))
                            show_flag = True
                        else:
                            # self.get_or_print(results[0])
                            # self.get_or_print(result)
                            self.addContents(result)
	
                #TODO order result by relevance as done with Shows ?
                #or (better) check len of results and turns interactive if are many
                else:
                    print "Nothing found for '%s'." % str(self.title.text())
        
            except Exception, e:        #FIX ME this is crap
                self.updateStatusLabel('Error: %s' % e, True)
                print "Cuevana.tv has a problem. Try in a few minutes"
                self.enabledItems()
                self.title.setFocus()
                return

        if self.titles:
            self.ml_model = ListModel(self.titles, self)
            self.main_list.setModel(self.ml_model)

        if not show_flag:
            self.lblStatus.clear()

        self.enabledItems()
        self.title.setFocus()
        self.updateWindow()

    def titlesClicked(self, index):
        self.updateStatusLabel('Loading...')
        self.updateWindow()
        self.updateContents(index)

    def addContents(self, content):
        try:
            self.titles_content.append(content)
            self.titles.append(content.pretty_title)
        except Exception, e:
            self.updateStatusLabel('Error: %s' % e, True)
            return False

    def updateContents(self, index):
        if self.titles_content[index.row()].thumbnail:
            title_thumbnail = QtGui.QPixmap()
            title_thumbnail.loadFromData(urllib.urlopen(self.titles_content[index.row()].thumbnail).read())

            if title_thumbnail:
                self.content_frame.title_thumbnail.setPixmap(title_thumbnail)

        self.content_frame.title.setText(self.ml_model.listdata[index.row()])
        self.content_frame.title_plot.setText(self.titles_content[index.row()].plot)
        self.get_or_print(self.titles_content[index.row()])

    def get_or_print(self, content):
        """auxiliar function to practice DRY principle"""

        self.lblStatus.clear()
        config = get_config()
        format = config.get('main', 'file_format')

        if self.check_subs.isChecked():
            try:
                urllib.urlretrieve(content.subs[self.language],
                       content.filename(format=format))
            except Exception, e:        #Fix me 
                print e

        if not self.check_download.isChecked():
            try:
                self.content_frame.title_sources.setText('\n'.join(["<a href='%s'>%s</a>" % (source, source) for source in content.sources]))
                self.content_frame.title_subs.setText("\n<a href='" + content.subs[self.language] +
                                                        "'>" + content.subs[self.language] + "</a>")
            except:
                self.content_frame.title_sources.setText('Error: Unable to get links')
                
        else:
            print "Found %s" % content.pretty_title
            mu_url = content.sources[0]     #FIX ME . always the first one?
            filename= content.filename(format=format, extension='mp4')

            if self.play:
                command_list = config.get('main', 'player').split()

                if '{file}' in command_list:
                    command_list[command_list.index('{file}')] = filename
                else:
                    command_list.append(filename)

                process = Process(target=background_process,
                                  args=(command_list,))
 
                megaupload(mu_url, filename, process.start, max_rate=max_rate)
                process.join()
            else:
                callback = process = None
                megaupload(mu_url, filename, max_rate=max_rate)

    def enabledItems(self, enabled=True):
        for item in self.title, self.episode, self.end:
            item.setEnabled(enabled)

    def updateWindow(self):
        self.repaint()
        self.update()
        self.app.processEvents()

    def updateStatusLabel(self, content, error=False):
        self.lblStatus.setText(content if not error else "<font color='red'>" + content + "</font>")

    def main(self):
        self.show()
        sys.exit(self.app.exec_())

if __name__ == "__main__":
    mw = CuevanaGUI()
    mw.main()
