# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui/sync.ui'
#
# Created: Thu Sep  8 16:31:03 2011
#      by: PyQt4 UI code generator 4.7.3
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(476, 363)
        self.verticalLayout = QtGui.QVBoxLayout(Dialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.stage = QtGui.QLabel(Dialog)
        self.stage.setText("")
        self.stage.setAlignment(QtCore.Qt.AlignCenter)
        self.stage.setObjectName("stage")
        self.verticalLayout.addWidget(self.stage)
        self.progress = QtGui.QProgressBar(Dialog)
        self.progress.setProperty("value", 0)
        self.progress.setObjectName("progress")
        self.verticalLayout.addWidget(self.progress)
        self.logEdit = QtGui.QPlainTextEdit(Dialog)
        self.logEdit.setReadOnly(True)
        self.logEdit.setCenterOnScroll(False)
        self.logEdit.setObjectName("logEdit")
        self.verticalLayout.addWidget(self.logEdit)
        self.buttonBox = QtGui.QDialogButtonBox(Dialog)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QtGui.QApplication.translate("Dialog", "Синхронизация с zenpad.ru", None, QtGui.QApplication.UnicodeUTF8))

