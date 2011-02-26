# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'confirm_dialog.ui'
#
# Created: Sat Feb 26 18:04:23 2011
#      by: PyQt4 UI code generator 4.7.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(321, 123)
        self.gridLayout_2 = QtGui.QGridLayout(Dialog)
        self.gridLayout_2.setObjectName("gridLayout_2")
        spacerItem = QtGui.QSpacerItem(20, 152, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout_2.addItem(spacerItem, 1, 0, 1, 1)
        self.countLabel = QtGui.QLabel(Dialog)
        self.countLabel.setText("")
        self.countLabel.setWordWrap(True)
        self.countLabel.setObjectName("countLabel")
        self.gridLayout_2.addWidget(self.countLabel, 0, 0, 1, 2)
        self.label = QtGui.QLabel(Dialog)
        self.label.setObjectName("label")
        self.gridLayout_2.addWidget(self.label, 2, 0, 1, 2)
        self.gridLayout = QtGui.QGridLayout()
        self.gridLayout.setObjectName("gridLayout")
        self.logCheckBox = QtGui.QCheckBox(Dialog)
        self.logCheckBox.setObjectName("logCheckBox")
        self.gridLayout.addWidget(self.logCheckBox, 0, 0, 1, 1)
        self.scriptCheckBox = QtGui.QCheckBox(Dialog)
        self.scriptCheckBox.setObjectName("scriptCheckBox")
        self.gridLayout.addWidget(self.scriptCheckBox, 0, 1, 1, 1)
        self.gridLayout_2.addLayout(self.gridLayout, 3, 0, 1, 2)
        self.buttonBox = QtGui.QDialogButtonBox(Dialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.gridLayout_2.addWidget(self.buttonBox, 4, 1, 1, 1)

        self.retranslateUi(Dialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("accepted()"), Dialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("rejected()"), Dialog.reject)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QtGui.QApplication.translate("Dialog", "Dialog", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("Dialog", "Do you want to continue ?", None, QtGui.QApplication.UnicodeUTF8))
        self.logCheckBox.setText(QtGui.QApplication.translate("Dialog", "Log operations", None, QtGui.QApplication.UnicodeUTF8))
        self.scriptCheckBox.setText(QtGui.QApplication.translate("Dialog", "Generate migration scripts", None, QtGui.QApplication.UnicodeUTF8))

