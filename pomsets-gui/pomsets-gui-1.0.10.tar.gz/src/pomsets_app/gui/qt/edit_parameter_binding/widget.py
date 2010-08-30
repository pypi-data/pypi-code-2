# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'resources/qt/edit parameter binding dialog.ui'
#
# Created: Thu Mar  4 14:39:27 2010
#      by: PyQt4 UI code generator 4.7
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(451, 371)
        self.buttonBox = QtGui.QDialogButtonBox(Dialog)
        self.buttonBox.setGeometry(QtCore.QRect(80, 320, 341, 32))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.checkBoxSweep = QtGui.QCheckBox(Dialog)
        self.checkBoxSweep.setGeometry(QtCore.QRect(30, 20, 241, 20))
        self.checkBoxSweep.setObjectName("checkBoxSweep")
        self.textEditValues = QtGui.QPlainTextEdit(Dialog)
        self.textEditValues.setGeometry(QtCore.QRect(30, 90, 391, 211))
        self.textEditValues.setObjectName("textEditValues")
        self.label = QtGui.QLabel(Dialog)
        self.label.setGeometry(QtCore.QRect(40, 60, 62, 16))
        self.label.setObjectName("label")

        self.retranslateUi(Dialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("accepted()"), Dialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("rejected()"), Dialog.reject)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QtGui.QApplication.translate("Dialog", "Edit parameter binding", None, QtGui.QApplication.UnicodeUTF8))
        self.checkBoxSweep.setText(QtGui.QApplication.translate("Dialog", "Treat value as parameter sweep", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("Dialog", "Value", None, QtGui.QApplication.UnicodeUTF8))


if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    Dialog = QtGui.QDialog()
    ui = Ui_Dialog()
    ui.setupUi(Dialog)
    Dialog.show()
    sys.exit(app.exec_())

