#!/usr/bin/env python
"""
Module QT4APP -- Python Qt 4 Application Objects
Sub-Package GUI.TOOLKITS.QT4 of Package PLIB -- Python GUI Toolkits
Copyright (C) 2008-2011 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains the Qt 4 GUI application objects.
"""

from PyQt4 import Qt as qt

from plib.gui.defs import *
from plib.gui._base import app

from _qt4common import _PQtCommunicator


class PQtAboutDialog(app.PAboutDialogBase):
    
    attrnames = [ 'name',
        'version',
        'copyright',
        'license',
        'description',
        'developers',
        'website',
        'icon' ]
    
    formatstr = "%(aname)s %(aversion)s\n%(adescription)s\n%(acopyright)s\n%(adevelopers)s\n%(awebsite)s"
    
    def __getattribute__(self, name):
        # Here we have to modify the hack somewhat
        attrnames = object.__getattribute__(self, 'attrnames')
        if name in attrnames:
            object.__getattribute__(self, '__dict__')['temp'] = name
            name = 'store'
        return object.__getattribute__(self, name)
    
    def store(self, data):
        name = self.temp
        del self.temp
        if name == 'developers':
            data = ", ".join(data)
        setattr(self, "a%s" % name, data)
    
    def display(self):
        caption = "About %s" % self.aname
        # Leave out icon here (setting it in set_iconfile below is enough, and
        # including it here will raise an exception if there is no icon)
        body = self.formatstr % dict(
            ("a%s" % name, getattr(self, "a%s" % name))
            for name in self.attrnames if name != 'icon')
        qt.QMessageBox.about(self.mainwidget, caption, body)


class _PQtMainMixin(qt.QMainWindow, _PQtCommunicator):
    """Mixin class for Qt top windows and main windows.
    """
    
    aboutdialogclass = PQtAboutDialog
    
    def _get_w(self):
        return self.width()
    w = property(_get_w)
    
    def _show_window(self):
        qt.QMainWindow.show(self)
    
    def _hide_window(self):
        qt.QMainWindow.hide(self)
    
    def set_iconfile(self, iconfile):
        self.setWindowIcon(qt.QIcon(qt.QPixmap(iconfile)))
    
    def set_caption(self, caption):
        self.setWindowTitle(caption)
    
    def sizetoscreen(self, maximized):
        if maximized:
            if self.shown:
                self.showMaximized()
            else:
                self._showMax = True
        else:
            desktop = self.app.desktop()
            self.resize(
                desktop.width() - self.sizeoffset,
                desktop.height() - self.sizeoffset)
    
    def sizetoclient(self, clientwidth, clientheight):
        self.resize(clientwidth, clientheight)
    
    def center(self):
        desktop = self.app.desktop()
        s = self.frameSize() # FIXME: this appears to give wrong values!
        x, y = s.width(), s.height()
        self.move((desktop.width() - x)/2, (desktop.height() - y)/2)
    
    def show_init(self):
        if hasattr(self, '_showMax'):
            self.showMaximized()
            del self._showMax
        else:
            qt.QMainWindow.show(self)
    
    def exit(self):
        self.close()
    
    def closeEvent(self, event):
        # 'automagic' code for SIGNAL_QUERYCLOSE
        if self.acceptclose():
            self._emit_event(SIGNAL_CLOSING)
            event.accept()
        else:
            event.ignore()
    
    def hideEvent(self, event):
        self._emit_event(SIGNAL_HIDDEN)


class PQtTopWindow(_PQtMainMixin, app.PTopWindowBase):
    """Customized Qt top window class.
    """
    
    def __init__(self, parent, cls=None):
        _PQtMainMixin.__init__(self)
        app.PTopWindowBase.__init__(self, parent, cls)
        self.abouttoolkitfunc = self.app.aboutQt
        self.setCentralWidget(self.clientwidget)
    
    def show_init(self):
        app.PTopWindowBase.show_init(self)
        _PQtMainMixin.show_init(self)


class PQtApplication(qt.QApplication, app.PApplicationBase, _PQtCommunicator):
    """Customized Qt application class.
    """
    
    _local_loop = None
    
    def __init__(self, arglist=[], cls=None, use_mainwindow=False):
        qt.QApplication.__init__(self, arglist)
        app.PApplicationBase.__init__(self, arglist, cls, use_mainwindow)
        self.mainwin = self.createMainWidget()
        #self.setMainWidget(self.mainwin)
        
        # 'automagic' signal connection
        self.setup_notify(SIGNAL_BEFOREQUIT, self.before_quit)
    
    def _eventloop(self):
        self.exec_()
    
    def process_events(self):
        self.processEvents()
    
    # For use when multiplexing with other event types (e.g.,
    # in a NotifierClient
    
    def enter_yield(self):
        if self._local_loop is None:
            self._local_loop = qt.QEventLoop()
            self._local_loop.exec_()
    
    def exit_yield(self):
        if self._local_loop is not None:
            self._local_loop.exit()
            del self._local_loop
