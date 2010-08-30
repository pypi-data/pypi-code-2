# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'resources/qt/select definition dialog.ui'
#
# Created: Thu Mar  4 16:19:49 2010
#      by: PyQt4 UI code generator 4.7
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(381, 436)
        self.buttonBox = QtGui.QDialogButtonBox(Dialog)
        self.buttonBox.setGeometry(QtCore.QRect(20, 390, 341, 32))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.labelName = QtGui.QLabel(Dialog)
        self.labelName.setGeometry(QtCore.QRect(30, 350, 62, 16))
        self.labelName.setObjectName("labelName")
        self.treeWidgetDefinitions = QtGui.QTreeWidget(Dialog)
        self.treeWidgetDefinitions.setGeometry(QtCore.QRect(20, 20, 341, 301))
        self.treeWidgetDefinitions.setObjectName("treeWidgetDefinitions")
        self.treeWidgetDefinitions.headerItem().setText(0, "1")
        self.treeWidgetDefinitions.header().setVisible(False)
        self.textEditName = QtGui.QLineEdit(Dialog)
        self.textEditName.setGeometry(QtCore.QRect(80, 341, 281, 31))
        self.textEditName.setObjectName("textEditName")

        self.retranslateUi(Dialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("accepted()"), Dialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("rejected()"), Dialog.reject)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QtGui.QApplication.translate("Dialog", "Dialog", None, QtGui.QApplication.UnicodeUTF8))
        self.labelName.setText(QtGui.QApplication.translate("Dialog", "Name", None, QtGui.QApplication.UnicodeUTF8))


if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    Dialog = QtGui.QDialog()
    ui = Ui_Dialog()
    ui.setupUi(Dialog)
    Dialog.show()
    sys.exit(app.exec_())

