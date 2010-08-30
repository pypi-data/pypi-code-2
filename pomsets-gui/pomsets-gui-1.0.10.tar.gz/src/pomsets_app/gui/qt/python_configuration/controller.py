import logging
import os

from PyQt4.QtCore import *
from PyQt4 import QtGui

import pypatterns.filter as FilterModule

import pomsets.parameter as ParameterModule

import pomsets_app.utils as AppUtilsModule
import pomsets_app.gui.qt as QtModule

class Controller(QtModule.Controller, QtGui.QDialog):

    ENV_LOCAL = 'local'
    ENV_PICLOUD = 'picloud'

    def __init__(self, *args, **kwds):
        QtGui.QDialog.__init__(self, *args, **kwds)
        QtModule.Controller.__init__(self)
        return

    def getPersistedExecuteEnvironment(self):
        widget = self.widget()
        contextManager = self.contextManager()

        pomsetContext, pomsetReferencePath, isEditable = \
            contextManager.currentDisplayedPomsetInfo()

        execEnvs = pomsetContext.executeEnvironments() or []
        pythonExecEnv = 'pomsets.python.PythonEval'
        for key, envPath in execEnvs:
            if key == 'python eval':
                pythonExecEnv = envPath
        
        if pythonExecEnv == 'pomsets.picloud.PythonEval':
            return Controller.ENV_PICLOUD
        return Controller.ENV_LOCAL


    def persistExecuteEnvironment(self, value):
        widget = self.widget()
        contextManager = self.contextManager()

        pomsetContext, pomsetReferencePath, isEditable = \
            contextManager.currentDisplayedPomsetInfo()

        if value == Controller.ENV_PICLOUD:
            pomsetContext.addExecuteEnvironment(
                'python eval',
                'pomsets.picloud.PythonEval')
            pomsetContext.addCommandBuilder(
                'python eval',
                'pomsets.picloud.CommandBuilder')
        else:
            pomsetContext.addExecuteEnvironment(
                'python eval',
                'pomsets.python.PythonEval')
            pomsetContext.addCommandBuilder(
                'python eval',
                'pomsets.python.CommandBuilder')

        pomsetContext.isModified(True)
        contextManager.mainWindow().emit(
            SIGNAL("OnPomsetModified(PyQt_PyObject)"), pomsetContext)

        return


    def populate(self):

        widget = self.widget()
        contextManager = self.contextManager()

        persistedEnv = self.getPersistedExecuteEnvironment()
        if persistedEnv == Controller.ENV_PICLOUD:
            # set to picloud
            widget.executePicloudButton.setChecked(True)
        else:
            # set to local
            widget.executeLocalButton.setChecked(True)
            pass

        return


    @pyqtSlot(QtGui.QAbstractButton)
    def on_buttonBox_clicked(self, button):
        widget = self.widget()
        buttonRole = widget.buttonBox.buttonRole(button)
        if buttonRole == QtGui.QDialogButtonBox.ApplyRole:
            self.saveValues()
            pass
        if buttonRole == QtGui.QDialogButtonBox.AcceptRole:
            self.saveValues()
            self.accept()
            pass
        if buttonRole == QtGui.QDialogButtonBox.RejectRole:
            self.reject()
            pass
        return


    def saveValues(self):

        contextManager = self.contextManager()
        automaton = contextManager.automaton()
        widget = self.widget()
        
        persistedEnv = self.getPersistedExecuteEnvironment()

        if widget.executePicloudButton.isChecked():
            # do something only if changed
            if persistedEnv != Controller.ENV_PICLOUD:
                self.persistExecuteEnvironment(Controller.ENV_PICLOUD)
                pass
            pass
        else:
            # do something only if changed
            if persistedEnv != Controller.ENV_LOCAL:
                self.persistExecuteEnvironment(Controller.ENV_LOCAL)
                pass
            pass


        return


    # END class Controller
    pass
