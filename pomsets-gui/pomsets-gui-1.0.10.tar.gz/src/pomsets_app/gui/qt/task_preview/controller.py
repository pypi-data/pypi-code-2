import logging
import os

import StringIO

from PyQt4.QtCore import *
from PyQt4 import QtGui

import pomsets_app.gui.qt as QtModule

class Controller(QtModule.Controller, QtGui.QDialog):


    def __init__(self, *args, **kwds):
        QtGui.QDialog.__init__(self, *args, **kwds)
        QtModule.Controller.__init__(self)

        return

    def populate(self):

        widget = self.widget()
        contextManager = self.contextManager()

        stream = StringIO.StringIO()
        contextManager.outputCommandsToStream(stream)

        textEditCommands = widget.textEditCommands
        textEditCommands.setText(stream.getvalue())

        return


    # END class Controller
    pass
