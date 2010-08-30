# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'resources/qt/edit parameter dialog.ui'
#
# Created: Wed Jun  9 15:53:10 2010
#      by: PyQt4 UI code generator 4.7
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(402, 439)
        self.buttonBox = QtGui.QDialogButtonBox(Dialog)
        self.buttonBox.setGeometry(QtCore.QRect(100, 390, 281, 32))
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
        self.labelFlag.setGeometry(QtCore.QRect(20, 190, 62, 16))
        self.labelFlag.setObjectName("labelFlag")
        self.labelDirection = QtGui.QLabel(Dialog)
        self.labelDirection.setGeometry(QtCore.QRect(20, 110, 62, 16))
        self.labelDirection.setObjectName("labelDirection")
        self.comboBoxDirection = QtGui.QComboBox(Dialog)
        self.comboBoxDirection.setGeometry(QtCore.QRect(120, 105, 261, 31))
        self.comboBoxDirection.setObjectName("comboBoxDirection")
        self.checkBoxCommandline = QtGui.QCheckBox(Dialog)
        self.checkBoxCommandline.setGeometry(QtCore.QRect(20, 150, 131, 20))
        self.checkBoxCommandline.setObjectName("checkBoxCommandline")
        self.checkBoxOptional = QtGui.QCheckBox(Dialog)
        self.checkBoxOptional.setGeometry(QtCore.QRect(20, 230, 131, 20))
        self.checkBoxOptional.setObjectName("checkBoxOptional")
        self.checkBoxFile = QtGui.QCheckBox(Dialog)
        self.checkBoxFile.setGeometry(QtCore.QRect(20, 270, 131, 20))
        self.checkBoxFile.setObjectName("checkBoxFile")
        self.checkBoxList = QtGui.QCheckBox(Dialog)
        self.checkBoxList.setGeometry(QtCore.QRect(20, 310, 131, 20))
        self.checkBoxList.setObjectName("checkBoxList")
        self.checkBoxDistributeFlag = QtGui.QCheckBox(Dialog)
        self.checkBoxDistributeFlag.setGeometry(QtCore.QRect(20, 350, 131, 20))
        self.checkBoxDistributeFlag.setObjectName("checkBoxDistributeFlag")
        self.textEditName = QtGui.QLineEdit(Dialog)
        self.textEditName.setGeometry(QtCore.QRect(120, 21, 261, 31))
        self.textEditName.setObjectName("textEditName")
        self.textEditDescription = QtGui.QLineEdit(Dialog)
        self.textEditDescription.setGeometry(QtCore.QRect(120, 60, 261, 31))
        self.textEditDescription.setObjectName("textEditDescription")
        self.textEditFlag = QtGui.QLineEdit(Dialog)
        self.textEditFlag.setGeometry(QtCore.QRect(120, 180, 261, 31))
        self.textEditFlag.setObjectName("textEditFlag")

        self.retranslateUi(Dialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("accepted()"), Dialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("rejected()"), Dialog.reject)
        QtCore.QMetaObject.connectSlotsByName(Dialog)
        Dialog.setTabOrder(self.textEditName, self.textEditDescription)
        Dialog.setTabOrder(self.textEditDescription, self.comboBoxDirection)
        Dialog.setTabOrder(self.comboBoxDirection, self.checkBoxCommandline)
        Dialog.setTabOrder(self.checkBoxCommandline, self.textEditFlag)
        Dialog.setTabOrder(self.textEditFlag, self.checkBoxOptional)
        Dialog.setTabOrder(self.checkBoxOptional, self.checkBoxFile)
        Dialog.setTabOrder(self.checkBoxFile, self.checkBoxList)
        Dialog.setTabOrder(self.checkBoxList, self.checkBoxDistributeFlag)
        Dialog.setTabOrder(self.checkBoxDistributeFlag, self.buttonBox)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QtGui.QApplication.translate("Dialog", "Edit parameter", None, QtGui.QApplication.UnicodeUTF8))
        self.labelName.setText(QtGui.QApplication.translate("Dialog", "Name", None, QtGui.QApplication.UnicodeUTF8))
        self.labelDescription.setText(QtGui.QApplication.translate("Dialog", "Description", None, QtGui.QApplication.UnicodeUTF8))
        self.labelFlag.setText(QtGui.QApplication.translate("Dialog", "Flag", None, QtGui.QApplication.UnicodeUTF8))
        self.labelDirection.setText(QtGui.QApplication.translate("Dialog", "Direction", None, QtGui.QApplication.UnicodeUTF8))
        self.checkBoxCommandline.setText(QtGui.QApplication.translate("Dialog", "Commandline", None, QtGui.QApplication.UnicodeUTF8))
        self.checkBoxOptional.setText(QtGui.QApplication.translate("Dialog", "Optional", None, QtGui.QApplication.UnicodeUTF8))
        self.checkBoxFile.setText(QtGui.QApplication.translate("Dialog", "File", None, QtGui.QApplication.UnicodeUTF8))
        self.checkBoxList.setText(QtGui.QApplication.translate("Dialog", "List", None, QtGui.QApplication.UnicodeUTF8))
        self.checkBoxDistributeFlag.setText(QtGui.QApplication.translate("Dialog", "Distribute flag", None, QtGui.QApplication.UnicodeUTF8))


if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    Dialog = QtGui.QDialog()
    ui = Ui_Dialog()
    ui.setupUi(Dialog)
    Dialog.show()
    sys.exit(app.exec_())

