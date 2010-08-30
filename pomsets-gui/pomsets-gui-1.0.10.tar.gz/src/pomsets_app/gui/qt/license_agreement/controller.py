from __future__ import with_statement

import logging
import os

import StringIO

from PyQt4.QtCore import *
from PyQt4 import QtGui

import pomsets_app.utils as AppUtilsModule

import pomsets_app.gui.qt as QtModule
import pomsets_app.gui.qt.application as ApplicationModule

class Controller(QtModule.Controller, QtGui.QDialog):

    LICENSE_FILES = ['gpl-2.0.txt',
                     'gpl-3.0.txt',
                     'commercial.txt']
    LICENSE_LABELS = ['Non-commercial | GPL v2',
                      'Non-commercial | GPL v3',
                      'Commercial | 30 day evaluation']
    
    def __init__(self, *args, **kwds):
        QtGui.QDialog.__init__(self, *args, **kwds)
        QtModule.Controller.__init__(self)

        return

    def populate(self):

        widget = self.widget()
        contextManager = self.contextManager()

        comboBoxLicense = widget.comboBoxLicense
        comboBoxLicense.addItems(Controller.LICENSE_LABELS)

        self.populateLicense()

        return

    def populateLicense(self):
        widget = self.widget()
        resourcePath = ApplicationModule.getDefaultResourcePath()

        licenseType = str(widget.comboBoxLicense.currentText())
        licenseIndex = Controller.LICENSE_LABELS.index(licenseType)
        licenseFile = Controller.LICENSE_FILES[licenseIndex]
        licensePath = os.path.join(resourcePath, 'licenses', licenseFile)
        
        textEditLicense = widget.textEditLicense
        with open(licensePath, 'r') as f:
            licenseText = ''.join(f.readlines())
            textEditLicense.setText(licenseText)
            pass

        return

    def userHasReadLicense(self):
        checkBoxRead = self.widget().checkBoxRead
        return checkBoxRead.isChecked()

    def saveUserAgreement(self):

        configDir = AppUtilsModule.getDefaultConfigDir()
        if not os.path.exists(configDir):
            os.makedirs(configDir)

        licenseFile = self.contextManager().app().getLicenseFile()
        if os.path.exists(licenseFile):
            return

        # this will create the file
        with open(licenseFile, 'w') as f:
            pass
        
        return


    @pyqtSlot()
    def on_buttonAgree_clicked(self):
        if not self.userHasReadLicense():
            # show a message box
            messageBox = QtGui.QMessageBox(self)
            messageBox.setText('Please check the box to indicate that you have read the license')
            messageBox.show()
            return

        self.saveUserAgreement()
        self.accept()
        return

    @pyqtSlot()
    def on_buttonDisagree_clicked(self):
        self.reject()
        return

    @pyqtSlot(str)
    def on_comboBoxLicense_currentIndexChanged(self, value):
        self.populateLicense()
        return



    # END class Controller
    pass
