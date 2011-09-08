# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui/add_pad.ui'
#
# Created: Thu Sep  8 16:31:03 2011
#      by: PyQt4 UI code generator 4.7.3
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(400, 157)
        self.buttonBox = QtGui.QDialogButtonBox(Dialog)
        self.buttonBox.setGeometry(QtCore.QRect(10, 120, 381, 32))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.lineEdit = QtGui.QLineEdit(Dialog)
        self.lineEdit.setGeometry(QtCore.QRect(238, 60, 131, 21))
        self.lineEdit.setMaxLength(30)
        self.lineEdit.setObjectName("lineEdit")
        self.label_root = QtGui.QLabel(Dialog)
        self.label_root.setGeometry(QtCore.QRect(5, 60, 221, 20))
        self.label_root.setLayoutDirection(QtCore.Qt.RightToLeft)
        self.label_root.setObjectName("label_root")
        self.label_2 = QtGui.QLabel(Dialog)
        self.label_2.setGeometry(QtCore.QRect(380, 60, 21, 20))
        self.label_2.setObjectName("label_2")
        self.label_3 = QtGui.QLabel(Dialog)
        self.label_3.setGeometry(QtCore.QRect(10, 10, 381, 41))
        self.label_3.setAlignment(QtCore.Qt.AlignCenter)
        self.label_3.setObjectName("label_3")
        self.converterSelect = QtGui.QComboBox(Dialog)
        self.converterSelect.setGeometry(QtCore.QRect(240, 90, 131, 22))
        self.converterSelect.setObjectName("converterSelect")
        self.label = QtGui.QLabel(Dialog)
        self.label.setGeometry(QtCore.QRect(116, 90, 111, 20))
        self.label.setObjectName("label")

        self.retranslateUi(Dialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("accepted()"), Dialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("rejected()"), Dialog.reject)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QtGui.QApplication.translate("Dialog", "Новый блокнот", None, QtGui.QApplication.UnicodeUTF8))
        self.label_root.setText(QtGui.QApplication.translate("Dialog", "TextLabel", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("Dialog", "/", None, QtGui.QApplication.UnicodeUTF8))
        self.label_3.setText(QtGui.QApplication.translate("Dialog", "Укажите папку, в которой будет размещаться блокнот\n"
"(используйте только английские буквы, цифры и тире)", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("Dialog", "Формат данных", None, QtGui.QApplication.UnicodeUTF8))

