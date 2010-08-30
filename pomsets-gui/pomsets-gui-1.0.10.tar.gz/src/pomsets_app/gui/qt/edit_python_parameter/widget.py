# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'pomsets-gui/resources/qt/edit python parameter dialog.ui'
#
# Created: Mon Jul 19 12:52:06 2010
#      by: PyQt4 UI code generator 4.7.3
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(400, 302)
        self.buttonBox = QtGui.QDialogButtonBox(Dialog)
        self.buttonBox.setGeometry(QtCore.QRect(100, 260, 281, 32))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Apply|QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.labelName = QtGui.QLabel(Dialog)
        self.labelName.setGeometry(QtCore.QRect(20, 30, 62, 16))
        self.labelName.setObjectName("labelName")
        self.labelDescription = QtGui.QLabel(Dialog)
        self.labelDescription.setGeometry(QtCore.QRect(20, 70, 81, 16))
        self.labelDescription.setObjectName("labelDescription")
        self.labelFlag = QtGui.QLabel(Dialog)
        self.labelFlag.setGeometry(QtCore.QRect(20, 150, 62, 16))
        self.labelFlag.setObjectName("labelFlag")
        self.checkBoxFile = QtGui.QCheckBox(Dialog)
        self.checkBoxFile.setGeometry(QtCore.QRect(20, 190, 131, 20))
        self.checkBoxFile.setObjectName("checkBoxFile")
        self.checkBoxList = QtGui.QCheckBox(Dialog)
        self.checkBoxList.setGeometry(QtCore.QRect(20, 220, 131, 20))
        self.checkBoxList.setObjectName("checkBoxList")
        self.textEditName = QtGui.QLineEdit(Dialog)
        self.textEditName.setGeometry(QtCore.QRect(120, 21, 261, 31))
        self.textEditName.setObjectName("textEditName")
        self.textEditDescription = QtGui.QLineEdit(Dialog)
        self.textEditDescription.setGeometry(QtCore.QRect(120, 60, 261, 31))
        self.textEditDescription.setObjectName("textEditDescription")
        self.textEditKeyword = QtGui.QLineEdit(Dialog)
        self.textEditKeyword.setGeometry(QtCore.QRect(120, 140, 261, 31))
        self.textEditKeyword.setObjectName("textEditKeyword")
        self.labelFlagType = QtGui.QLabel(Dialog)
        self.labelFlagType.setGeometry(QtCore.QRect(20, 110, 81, 16))
        self.labelFlagType.setObjectName("labelFlagType")
        self.comboBoxType = QtGui.QComboBox(Dialog)
        self.comboBoxType.setGeometry(QtCore.QRect(120, 100, 261, 31))
        self.comboBoxType.setObjectName("comboBoxType")

        self.retranslateUi(Dialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("accepted()"), Dialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("rejected()"), Dialog.reject)
        QtCore.QMetaObject.connectSlotsByName(Dialog)
        Dialog.setTabOrder(self.textEditName, self.textEditDescription)
        Dialog.setTabOrder(self.textEditDescription, self.textEditKeyword)
        Dialog.setTabOrder(self.textEditKeyword, self.checkBoxFile)
        Dialog.setTabOrder(self.checkBoxFile, self.checkBoxList)
        Dialog.setTabOrder(self.checkBoxList, self.buttonBox)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QtGui.QApplication.translate("Dialog", "Edit Python parameter", None, QtGui.QApplication.UnicodeUTF8))
        self.labelName.setText(QtGui.QApplication.translate("Dialog", "Name", None, QtGui.QApplication.UnicodeUTF8))
        self.labelDescription.setText(QtGui.QApplication.translate("Dialog", "Description", None, QtGui.QApplication.UnicodeUTF8))
        self.labelFlag.setText(QtGui.QApplication.translate("Dialog", "Keyword", None, QtGui.QApplication.UnicodeUTF8))
        self.checkBoxFile.setText(QtGui.QApplication.translate("Dialog", "File", None, QtGui.QApplication.UnicodeUTF8))
        self.checkBoxList.setText(QtGui.QApplication.translate("Dialog", "List", None, QtGui.QApplication.UnicodeUTF8))
        self.labelFlagType.setText(QtGui.QApplication.translate("Dialog", "Python type", None, QtGui.QApplication.UnicodeUTF8))

