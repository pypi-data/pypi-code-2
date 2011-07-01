# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'long_operation_box.ui'
#
# Created: Wed Jun 29 15:29:03 2011
#      by: PyQt4 UI code generator 4.7.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_LongOperationBox(object):
    def setupUi(self, LongOperationBox):
        LongOperationBox.setObjectName("LongOperationBox")
        LongOperationBox.resize(247, 57)
        self.gridLayout = QtGui.QGridLayout(LongOperationBox)
        self.gridLayout.setObjectName("gridLayout")
        self.label = QtGui.QLabel(LongOperationBox)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)
        self.progressBar = QtGui.QProgressBar(LongOperationBox)
        self.progressBar.setProperty("value", 24)
        self.progressBar.setFormat("")
        self.progressBar.setObjectName("progressBar")
        self.gridLayout.addWidget(self.progressBar, 1, 0, 1, 1)

        self.retranslateUi(LongOperationBox)
        QtCore.QMetaObject.connectSlotsByName(LongOperationBox)

    def retranslateUi(self, LongOperationBox):
        LongOperationBox.setWindowTitle(QtGui.QApplication.translate("LongOperationBox", "Form", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("LongOperationBox", "TextLabel", None, QtGui.QApplication.UnicodeUTF8))

