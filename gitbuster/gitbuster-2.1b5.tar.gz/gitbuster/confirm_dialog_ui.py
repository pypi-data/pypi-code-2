# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'confirm_dialog.ui'
#
# Created: Tue May 31 21:29:16 2011
#      by: PyQt4 UI code generator 4.7.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(321, 123)
        self.gridLayout_3 = QtGui.QGridLayout(Dialog)
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.label = QtGui.QLabel(Dialog)
        self.label.setObjectName("label")
        self.gridLayout_3.addWidget(self.label, 5, 0, 1, 3)
        self.gridLayout = QtGui.QGridLayout()
        self.gridLayout.setObjectName("gridLayout")
        self.logCheckBox = QtGui.QCheckBox(Dialog)
        self.logCheckBox.setObjectName("logCheckBox")
        self.gridLayout.addWidget(self.logCheckBox, 0, 0, 1, 1)
        self.forceCheckBox = QtGui.QCheckBox(Dialog)
        self.forceCheckBox.setObjectName("forceCheckBox")
        self.gridLayout.addWidget(self.forceCheckBox, 1, 0, 1, 1)
        self.gridLayout_3.addLayout(self.gridLayout, 6, 0, 1, 4)
        self.buttonBox = QtGui.QDialogButtonBox(Dialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.gridLayout_3.addWidget(self.buttonBox, 7, 3, 1, 1)
        spacerItem = QtGui.QSpacerItem(20, 152, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout_3.addItem(spacerItem, 4, 0, 1, 1)
        self.label_3 = QtGui.QLabel(Dialog)
        self.label_3.setObjectName("label_3")
        self.gridLayout_3.addWidget(self.label_3, 2, 0, 1, 1)
        self.branchCountLayout = QtGui.QGridLayout()
        self.branchCountLayout.setObjectName("branchCountLayout")
        self.gridLayout_3.addLayout(self.branchCountLayout, 3, 0, 1, 4)

        self.retranslateUi(Dialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("accepted()"), Dialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("rejected()"), Dialog.reject)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QtGui.QApplication.translate("Dialog", "Dialog", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("Dialog", "Do you want to continue ?", None, QtGui.QApplication.UnicodeUTF8))
        self.logCheckBox.setText(QtGui.QApplication.translate("Dialog", "Log operations", None, QtGui.QApplication.UnicodeUTF8))
        self.forceCheckBox.setText(QtGui.QApplication.translate("Dialog", "Force committed author/date (instead of letting git update it)", None, QtGui.QApplication.UnicodeUTF8))
        self.label_3.setText(QtGui.QApplication.translate("Dialog", "Select the branch(es) that will be modified :", None, QtGui.QApplication.UnicodeUTF8))

