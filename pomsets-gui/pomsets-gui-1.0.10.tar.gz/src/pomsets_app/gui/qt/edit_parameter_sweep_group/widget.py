# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'resources/qt/edit parameter sweep group.ui'
#
# Created: Sun Mar 14 15:53:21 2010
#      by: PyQt4 UI code generator 4.7
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(401, 348)
        self.buttonBox = QtGui.QDialogButtonBox(Dialog)
        self.buttonBox.setGeometry(QtCore.QRect(190, 300, 191, 32))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.buttonUseOwnGroup = QtGui.QRadioButton(Dialog)
        self.buttonUseOwnGroup.setGeometry(QtCore.QRect(20, 20, 181, 20))
        self.buttonUseOwnGroup.setObjectName("buttonUseOwnGroup")
        self.buttonUseOtherGroup = QtGui.QRadioButton(Dialog)
        self.buttonUseOtherGroup.setGeometry(QtCore.QRect(20, 50, 211, 20))
        self.buttonUseOtherGroup.setObjectName("buttonUseOtherGroup")
        self.listWidget = QtGui.QListWidget(Dialog)
        self.listWidget.setGeometry(QtCore.QRect(20, 90, 361, 192))
        self.listWidget.setObjectName("listWidget")

        self.retranslateUi(Dialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("accepted()"), Dialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("rejected()"), Dialog.reject)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QtGui.QApplication.translate("Dialog", "Specify parameter sweep group", None, QtGui.QApplication.UnicodeUTF8))
        self.buttonUseOwnGroup.setText(QtGui.QApplication.translate("Dialog", "Use own group", None, QtGui.QApplication.UnicodeUTF8))
        self.buttonUseOtherGroup.setText(QtGui.QApplication.translate("Dialog", "Become member of group", None, QtGui.QApplication.UnicodeUTF8))


if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    Dialog = QtGui.QDialog()
    ui = Ui_Dialog()
    ui.setupUi(Dialog)
    Dialog.show()
    sys.exit(app.exec_())

