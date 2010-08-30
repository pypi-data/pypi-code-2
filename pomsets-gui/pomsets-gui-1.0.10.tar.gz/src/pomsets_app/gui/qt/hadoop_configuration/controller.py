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

        automaton = contextManager.automaton()

        configuration = automaton.hadoopConfigurations().get('localhost', None)
        if configuration is None:
            configuration = {'hostname':'localhost'}

        textEditHadoopHome = widget.textEditHadoopHome
        textEditHadoopHome.setText(configuration.get('home', ''))

        checkBoxRelative = widget.checkBoxRelative
        isRelativeToHadoopHome = configuration.get(
            'streaming jar is relative to home', True)
        checkBoxRelative.setChecked(isRelativeToHadoopHome)

        textEditStreamingJar = widget.textEditStreamingJar

        defaultStreamingJar = ''
        if isRelativeToHadoopHome:
            defaultStreamingJar = os.path.join(
                'contrib', 'streaming',
                'hadoop-0.20.1-streaming.jar')
        else:
            defaultStreamingJar = os.path.join(
                defaultHadoopHome, 'contrib', 'streaming',
                'hadoop-0.20.1-streaming.jar')
        textEditStreamingJar.setText(
            configuration.get('streaming jar', defaultStreamingJar))

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
        textEditStreamingJar = widget.textEditStreamingJar

        import user
        initialDir = user.home
        streamingJar = str(textEditStreamingJar.text())
        if len(streamingJar):
            index = streamingJar.rfind(os.path.sep)
            if not index == -1:
                initialDir = streamingJar[:index]
            pass

        fileName = QtGui.QFileDialog.getOpenFileName(
            self,
            QString("Hadoop streaming jar file"), 
            QString(initialDir),
            QString("Jar file (*.jar)"))
        if fileName and len(fileName):
            textEditStreamingJar.setText(fileName)
        return


    def saveValues(self):

        contextManager = self.contextManager()
        automaton = contextManager.automaton()
        widget = self.widget()

        configuration = automaton.hadoopConfigurations().get('localhost', None)
        shouldCreateNewConfig = False
        if configuration is None:
            configuration = {'hostname':'localhost'}
            shouldCreateNewConfig = True

        textEditHadoopHome = widget.textEditHadoopHome
        configuration['home'] = str(textEditHadoopHome.text())


        checkBoxRelative = widget.checkBoxRelative
        isRelativeToHadoopHome = checkBoxRelative.isChecked()
        configuration['streaming jar is relative to home'] = isRelativeToHadoopHome

        textEditStreamingJar = widget.textEditStreamingJar
        configuration['streaming jar'] = str(textEditStreamingJar.text())

        if shouldCreateNewConfig:
            logging.debug("need to implement when no configuration found")
            print "need to implement when no configuration found"
            automaton.addHadoopConfiguration(configuration)

        # save out to file
        configData = AppUtilsModule.createNewConfigDataObject()
        automaton.addConfigToSave(configData)
        AppUtilsModule.saveConfig(configData)

        return


    # END class Controller
    pass
