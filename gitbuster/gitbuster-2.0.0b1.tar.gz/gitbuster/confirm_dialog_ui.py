# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'confirm_dialog.ui'
#
# Created: Fri May 27 18:58:49 2011
#      by: PyQt4 UI code generator 4.8.3
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName(_fromUtf8("Dialog"))
        Dialog.resize(321, 123)
        self.gridLayout_3 = QtGui.QGridLayout(Dialog)
        self.gridLayout_3.setObjectName(_fromUtf8("gridLayout_3"))
        self.label = QtGui.QLabel(Dialog)
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout_3.addWidget(self.label, 5, 0, 1, 3)
        self.gridLayout = QtGui.QGridLayout()
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.logCheckBox = QtGui.QCheckBox(Dialog)
        self.logCheckBox.setObjectName(_fromUtf8("logCheckBox"))
        self.gridLayout.addWidget(self.logCheckBox, 0, 0, 1, 1)
        self.scriptCheckBox = QtGui.QCheckBox(Dialog)
        self.scriptCheckBox.setObjectName(_fromUtf8("scriptCheckBox"))
        self.gridLayout.addWidget(self.scriptCheckBox, 0, 1, 1, 1)
        self.gridLayout_3.addLayout(self.gridLayout, 6, 0, 1, 4)
        self.buttonBox = QtGui.QDialogButtonBox(Dialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout_3.addWidget(self.buttonBox, 7, 3, 1, 1)
        spacerItem = QtGui.QSpacerItem(20, 152, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout_3.addItem(spacerItem, 4, 0, 1, 1)
        self.label_3 = QtGui.QLabel(Dialog)
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.gridLayout_3.addWidget(self.label_3, 2, 0, 1, 1)
        self.branchCountLayout = QtGui.QGridLayout()
        self.branchCountLayout.setObjectName(_fromUtf8("branchCountLayout"))
        self.gridLayout_3.addLayout(self.branchCountLayout, 3, 0, 1, 4)

        self.retranslateUi(Dialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), Dialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), Dialog.reject)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QtGui.QApplication.translate("Dialog", "Dialog", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("Dialog", "Do you want to continue ?", None, QtGui.QApplication.UnicodeUTF8))
        self.logCheckBox.setText(QtGui.QApplication.translate("Dialog", "Log operations", None, QtGui.QApplication.UnicodeUTF8))
        self.scriptCheckBox.setText(QtGui.QApplication.translate("Dialog", "Generate migration scripts", None, QtGui.QApplication.UnicodeUTF8))
        self.label_3.setText(QtGui.QApplication.translate("Dialog", "Select the branch(es) that will be modified :", None, QtGui.QApplication.UnicodeUTF8))

