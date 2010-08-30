# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'resources/qt/euca2ools configuration dialog.ui'
#
# Created: Thu Mar  4 16:04:59 2010
#      by: PyQt4 UI code generator 4.7
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(562, 283)
        self.buttonBox = QtGui.QDialogButtonBox(Dialog)
        self.buttonBox.setGeometry(QtCore.QRect(180, 230, 341, 32))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.label = QtGui.QLabel(Dialog)
        self.label.setGeometry(QtCore.QRect(30, 30, 62, 16))
        self.label.setObjectName("label")
        self.label_2 = QtGui.QLabel(Dialog)
        self.label_2.setGeometry(QtCore.QRect(30, 70, 81, 16))
        self.label_2.setObjectName("label_2")
        self.label_3 = QtGui.QLabel(Dialog)
        self.label_3.setGeometry(QtCore.QRect(30, 110, 71, 16))
        self.label_3.setObjectName("label_3")
        self.label_4 = QtGui.QLabel(Dialog)
        self.label_4.setGeometry(QtCore.QRect(30, 150, 62, 16))
        self.label_4.setObjectName("label_4")
        self.label_5 = QtGui.QLabel(Dialog)
        self.label_5.setGeometry(QtCore.QRect(30, 190, 81, 16))
        self.label_5.setObjectName("label_5")
        self.buttonBrowse = QtGui.QPushButton(Dialog)
        self.buttonBrowse.setGeometry(QtCore.QRect(444, 180, 91, 32))
        self.buttonBrowse.setObjectName("buttonBrowse")
        self.textEditURL = QtGui.QLineEdit(Dialog)
        self.textEditURL.setGeometry(QtCore.QRect(120, 21, 411, 31))
        self.textEditURL.setObjectName("textEditURL")
        self.textEditAccessKey = QtGui.QLineEdit(Dialog)
        self.textEditAccessKey.setGeometry(QtCore.QRect(120, 60, 411, 31))
        self.textEditAccessKey.setObjectName("textEditAccessKey")
        self.textEditSecretKey = QtGui.QLineEdit(Dialog)
        self.textEditSecretKey.setGeometry(QtCore.QRect(120, 100, 411, 31))
        self.textEditSecretKey.setObjectName("textEditSecretKey")
        self.textEditKeyPair = QtGui.QLineEdit(Dialog)
        self.textEditKeyPair.setGeometry(QtCore.QRect(120, 140, 411, 31))
        self.textEditKeyPair.setObjectName("textEditKeyPair")
        self.textEditIdentityFile = QtGui.QLineEdit(Dialog)
        self.textEditIdentityFile.setGeometry(QtCore.QRect(120, 180, 321, 31))
        self.textEditIdentityFile.setObjectName("textEditIdentityFile")

        self.retranslateUi(Dialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("accepted()"), Dialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("rejected()"), Dialog.reject)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QtGui.QApplication.translate("Dialog", "euca2ools configuration", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("Dialog", "URL", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("Dialog", "Access key", None, QtGui.QApplication.UnicodeUTF8))
        self.label_3.setText(QtGui.QApplication.translate("Dialog", "Secret key", None, QtGui.QApplication.UnicodeUTF8))
        self.label_4.setText(QtGui.QApplication.translate("Dialog", "Key pair", None, QtGui.QApplication.UnicodeUTF8))
        self.label_5.setText(QtGui.QApplication.translate("Dialog", "Identity file", None, QtGui.QApplication.UnicodeUTF8))
        self.buttonBrowse.setText(QtGui.QApplication.translate("Dialog", "Browse", None, QtGui.QApplication.UnicodeUTF8))


if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    Dialog = QtGui.QDialog()
    ui = Ui_Dialog()
    ui.setupUi(Dialog)
    Dialog.show()
    sys.exit(app.exec_())

