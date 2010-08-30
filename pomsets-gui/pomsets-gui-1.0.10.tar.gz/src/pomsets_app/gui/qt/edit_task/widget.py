# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'resources/qt/edit task dialog.ui'
#
# Created: Wed Jun  9 15:53:05 2010
#      by: PyQt4 UI code generator 4.7
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(450, 456)
        self.buttonBox = QtGui.QDialogButtonBox(Dialog)
        self.buttonBox.setGeometry(QtCore.QRect(250, 410, 181, 32))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.labelName = QtGui.QLabel(Dialog)
        self.labelName.setGeometry(QtCore.QRect(20, 30, 62, 16))
        self.labelName.setObjectName("labelName")
        self.labelComment = QtGui.QLabel(Dialog)
        self.labelComment.setGeometry(QtCore.QRect(20, 70, 71, 16))
        self.labelComment.setObjectName("labelComment")
        self.labelParameters = QtGui.QLabel(Dialog)
        self.labelParameters.setGeometry(QtCore.QRect(20, 150, 91, 16))
        self.labelParameters.setObjectName("labelParameters")
        self.tableParameters = QtGui.QTableWidget(Dialog)
        self.tableParameters.setGeometry(QtCore.QRect(20, 180, 411, 171))
        self.tableParameters.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
        self.tableParameters.setObjectName("tableParameters")
        self.tableParameters.setColumnCount(4)
        self.tableParameters.setRowCount(0)
        item = QtGui.QTableWidgetItem()
        self.tableParameters.setHorizontalHeaderItem(0, item)
        item = QtGui.QTableWidgetItem()
        self.tableParameters.setHorizontalHeaderItem(1, item)
        item = QtGui.QTableWidgetItem()
        self.tableParameters.setHorizontalHeaderItem(2, item)
        item = QtGui.QTableWidgetItem()
        self.tableParameters.setHorizontalHeaderItem(3, item)
        self.textEditName = QtGui.QLineEdit(Dialog)
        self.textEditName.setGeometry(QtCore.QRect(100, 21, 331, 31))
        self.textEditName.setObjectName("textEditName")
        self.textEditComment = QtGui.QLineEdit(Dialog)
        self.textEditComment.setGeometry(QtCore.QRect(100, 60, 331, 31))
        self.textEditComment.setObjectName("textEditComment")
        self.buttonChangeGroup = QtGui.QPushButton(Dialog)
        self.buttonChangeGroup.setGeometry(QtCore.QRect(20, 360, 121, 32))
        self.buttonChangeGroup.setObjectName("buttonChangeGroup")
        self.checkBoxCritical = QtGui.QCheckBox(Dialog)
        self.checkBoxCritical.setGeometry(QtCore.QRect(20, 110, 87, 20))
        self.checkBoxCritical.setObjectName("checkBoxCritical")
        self.buttonToggleStaging = QtGui.QPushButton(Dialog)
        self.buttonToggleStaging.setGeometry(QtCore.QRect(150, 360, 141, 32))
        self.buttonToggleStaging.setObjectName("buttonToggleStaging")

        self.retranslateUi(Dialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("accepted()"), Dialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("rejected()"), Dialog.reject)
        QtCore.QMetaObject.connectSlotsByName(Dialog)
        Dialog.setTabOrder(self.textEditName, self.textEditComment)
        Dialog.setTabOrder(self.textEditComment, self.checkBoxCritical)
        Dialog.setTabOrder(self.checkBoxCritical, self.tableParameters)
        Dialog.setTabOrder(self.tableParameters, self.buttonChangeGroup)
        Dialog.setTabOrder(self.buttonChangeGroup, self.buttonToggleStaging)
        Dialog.setTabOrder(self.buttonToggleStaging, self.buttonBox)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QtGui.QApplication.translate("Dialog", "Edit task", None, QtGui.QApplication.UnicodeUTF8))
        self.labelName.setText(QtGui.QApplication.translate("Dialog", "Name", None, QtGui.QApplication.UnicodeUTF8))
        self.labelComment.setText(QtGui.QApplication.translate("Dialog", "Comment", None, QtGui.QApplication.UnicodeUTF8))
        self.labelParameters.setText(QtGui.QApplication.translate("Dialog", "Parameters", None, QtGui.QApplication.UnicodeUTF8))
        self.tableParameters.horizontalHeaderItem(0).setText(QtGui.QApplication.translate("Dialog", "Name", None, QtGui.QApplication.UnicodeUTF8))
        self.tableParameters.horizontalHeaderItem(1).setText(QtGui.QApplication.translate("Dialog", "Stage file", None, QtGui.QApplication.UnicodeUTF8))
        self.tableParameters.horizontalHeaderItem(2).setText(QtGui.QApplication.translate("Dialog", "Sweep", None, QtGui.QApplication.UnicodeUTF8))
        self.tableParameters.horizontalHeaderItem(3).setText(QtGui.QApplication.translate("Dialog", "Parameter sweep group", None, QtGui.QApplication.UnicodeUTF8))
        self.buttonChangeGroup.setText(QtGui.QApplication.translate("Dialog", "Change group", None, QtGui.QApplication.UnicodeUTF8))
        self.checkBoxCritical.setText(QtGui.QApplication.translate("Dialog", "Critical", None, QtGui.QApplication.UnicodeUTF8))
        self.buttonToggleStaging.setText(QtGui.QApplication.translate("Dialog", "Toggle staging", None, QtGui.QApplication.UnicodeUTF8))


if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    Dialog = QtGui.QDialog()
    ui = Ui_Dialog()
    ui.setupUi(Dialog)
    Dialog.show()
    sys.exit(app.exec_())

