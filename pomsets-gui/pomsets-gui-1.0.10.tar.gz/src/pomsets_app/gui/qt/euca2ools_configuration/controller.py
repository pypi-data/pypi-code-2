import logging
import os

from PyQt4.QtCore import *
from PyQt4 import QtGui

import pypatterns.filter as FilterModule

import pomsets.parameter as ParameterModule

import pomsets_app.utils as AppUtilsModule
import pomsets_app.gui.qt as QtModule

class Controller(QtModule.Controller, QtGui.QDialog):


    def __init__(self, *args, **kwds):
        QtGui.QDialog.__init__(self, *args, **kwds)
        QtModule.Controller.__init__(self)
        return

    def populate(self):

        widget = self.widget()
        contextManager = self.contextManager()

        controllerValues = {}
        try:
            controllerValues = contextManager.automaton().getCloudControllerCredentialsForAPI('euca2ools')
        except KeyError:
            pass

        textEditURL = widget.textEditURL
        textEditURL.setText(controllerValues.get('url', ''))

        textEditAccessKey = widget.textEditAccessKey
        textEditAccessKey.setText(controllerValues.get('access key', ''))

        textEditSecretKey = widget.textEditSecretKey
        textEditSecretKey.setText(controllerValues.get('secret key', ''))

        textEditKeyPair = widget.textEditKeyPair
        textEditKeyPair.setText(controllerValues.get('user key pair', ''))

        textEditIdentityFile = widget.textEditIdentityFile
        textEditIdentityFile.setText(controllerValues.get('identity file', ''))
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


    @pyqtSlot()
    def on_buttonBrowse_clicked(self):
        widget = self.widget()
        textEditIdentityFile = widget.textEditIdentityFile

        import user
        initialDir = user.home
        identityFile = str(textEditIdentityFile.text())
        if len(identityFile):
            index = identityFile.rfind(os.path.sep)
            if not index == -1:
                initialDir = identityFile[:index]
            pass

        fileName = QtGui.QFileDialog.getOpenFileName(
            self,
            QString("SSH identity file"), 
            QString(initialDir))
        if fileName and len(fileName):
            textEditIdentityFile.setText(fileName)
        return


    def saveValues(self):

        widget = self.widget()
        contextManager = self.contextManager()
        automaton = contextManager.automaton()

        shouldCreateNew = False
        controllerValues = {}
        try:
            controllerValues = automaton.getCloudControllerCredentialsForAPI('euca2ools')
        except KeyError, e:
            shouldCreateNew = True
            pass

        textEditKeyPair = widget.textEditKeyPair
        controllerValues['user key pair'] = str(textEditKeyPair.text())

        textEditURL = widget.textEditURL
        controllerValues['url'] = str(textEditURL.text())

        textEditAccessKey = widget.textEditAccessKey
        controllerValues['access key'] = str(textEditAccessKey.text())

        textEditSecretKey = widget.textEditSecretKey
        controllerValues['secret key'] = str(textEditSecretKey.text())

        textEditIdentityFile = widget.textEditIdentityFile
        controllerValues['identity file'] = str(textEditIdentityFile.text())

        if shouldCreateNew:
            automaton.addCloudControllerCredential(
                'Eucalyptus', 'euca2ools', **controllerValues)
            pass

        # save out to file
        configData = AppUtilsModule.createNewConfigDataObject()
        automaton.addConfigToSave(configData)
        AppUtilsModule.saveConfig(configData)

        return


    # END class Controller
    pass
