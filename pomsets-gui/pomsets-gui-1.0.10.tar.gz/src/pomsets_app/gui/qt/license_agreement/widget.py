# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'resources/qt/license agreement.ui'
#
# Created: Mon Mar  8 11:11:43 2010
#      by: PyQt4 UI code generator 4.7
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(541, 453)
        self.comboBoxLicense = QtGui.QComboBox(Dialog)
        self.comboBoxLicense.setGeometry(QtCore.QRect(20, 40, 281, 31))
        self.comboBoxLicense.setObjectName("comboBoxLicense")
        self.label = QtGui.QLabel(Dialog)
        self.label.setGeometry(QtCore.QRect(20, 20, 171, 16))
        self.label.setObjectName("label")
        self.textEditLicense = QtGui.QTextEdit(Dialog)
        self.textEditLicense.setGeometry(QtCore.QRect(20, 80, 501, 291))
        self.textEditLicense.setObjectName("textEditLicense")
        self.checkBoxRead = QtGui.QCheckBox(Dialog)
        self.checkBoxRead.setGeometry(QtCore.QRect(30, 380, 261, 20))
        self.checkBoxRead.setObjectName("checkBoxRead")
        self.buttonAgree = QtGui.QPushButton(Dialog)
        self.buttonAgree.setGeometry(QtCore.QRect(400, 410, 115, 32))
        self.buttonAgree.setObjectName("buttonAgree")
        self.buttonDisagree = QtGui.QPushButton(Dialog)
        self.buttonDisagree.setGeometry(QtCore.QRect(280, 410, 115, 32))
        self.buttonDisagree.setObjectName("buttonDisagree")

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QtGui.QApplication.translate("Dialog", "License agreement", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("Dialog", "Please choose a license:", None, QtGui.QApplication.UnicodeUTF8))
        self.checkBoxRead.setText(QtGui.QApplication.translate("Dialog", "I have read the terms of the license", None, QtGui.QApplication.UnicodeUTF8))
        self.buttonAgree.setText(QtGui.QApplication.translate("Dialog", "I agree", None, QtGui.QApplication.UnicodeUTF8))
        self.buttonDisagree.setText(QtGui.QApplication.translate("Dialog", "I disagree", None, QtGui.QApplication.UnicodeUTF8))

