# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'resources/qt/cloud pool dialog.ui'
#
# Created: Fri Mar  5 17:45:33 2010
#      by: PyQt4 UI code generator 4.7
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(881, 421)
        self.buttonBox = QtGui.QDialogButtonBox(Dialog)
        self.buttonBox.setGeometry(QtCore.QRect(500, 380, 341, 32))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Close)
        self.buttonBox.setObjectName("buttonBox")
        self.buttonCredentials = QtGui.QPushButton(Dialog)
        self.buttonCredentials.setGeometry(QtCore.QRect(40, 380, 115, 32))
        self.buttonCredentials.setObjectName("buttonCredentials")
        self.buttonAssign = QtGui.QPushButton(Dialog)
        self.buttonAssign.setGeometry(QtCore.QRect(160, 380, 115, 32))
        self.buttonAssign.setObjectName("buttonAssign")
        self.buttonUnassign = QtGui.QPushButton(Dialog)
        self.buttonUnassign.setGeometry(QtCore.QRect(280, 380, 115, 32))
        self.buttonUnassign.setObjectName("buttonUnassign")
        self.buttonRefresh = QtGui.QPushButton(Dialog)
        self.buttonRefresh.setGeometry(QtCore.QRect(400, 380, 115, 32))
        self.buttonRefresh.setObjectName("buttonRefresh")
        self.tableInstances = QtGui.QTableWidget(Dialog)
        self.tableInstances.setGeometry(QtCore.QRect(20, 20, 841, 351))
        self.tableInstances.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
        self.tableInstances.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)
        self.tableInstances.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.tableInstances.setObjectName("tableInstances")
        self.tableInstances.setColumnCount(8)
        self.tableInstances.setRowCount(0)
        item = QtGui.QTableWidgetItem()
        self.tableInstances.setHorizontalHeaderItem(0, item)
        item = QtGui.QTableWidgetItem()
        self.tableInstances.setHorizontalHeaderItem(1, item)
        item = QtGui.QTableWidgetItem()
        self.tableInstances.setHorizontalHeaderItem(2, item)
        item = QtGui.QTableWidgetItem()
        self.tableInstances.setHorizontalHeaderItem(3, item)
        item = QtGui.QTableWidgetItem()
        self.tableInstances.setHorizontalHeaderItem(4, item)
        item = QtGui.QTableWidgetItem()
        self.tableInstances.setHorizontalHeaderItem(5, item)
        item = QtGui.QTableWidgetItem()
        self.tableInstances.setHorizontalHeaderItem(6, item)
        item = QtGui.QTableWidgetItem()
        self.tableInstances.setHorizontalHeaderItem(7, item)
        self.tableInstances.horizontalHeader().setVisible(True)
        self.tableInstances.verticalHeader().setVisible(False)

        self.retranslateUi(Dialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("accepted()"), Dialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("rejected()"), Dialog.reject)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QtGui.QApplication.translate("Dialog", "Manage cloud pool", None, QtGui.QApplication.UnicodeUTF8))
        self.buttonCredentials.setText(QtGui.QApplication.translate("Dialog", "Credentials", None, QtGui.QApplication.UnicodeUTF8))
        self.buttonAssign.setText(QtGui.QApplication.translate("Dialog", "Assign", None, QtGui.QApplication.UnicodeUTF8))
        self.buttonUnassign.setText(QtGui.QApplication.translate("Dialog", "Unassign", None, QtGui.QApplication.UnicodeUTF8))
        self.buttonRefresh.setText(QtGui.QApplication.translate("Dialog", "Refresh", None, QtGui.QApplication.UnicodeUTF8))
        self.tableInstances.horizontalHeaderItem(0).setText(QtGui.QApplication.translate("Dialog", "Service", None, QtGui.QApplication.UnicodeUTF8))
        self.tableInstances.horizontalHeaderItem(1).setText(QtGui.QApplication.translate("Dialog", "API", None, QtGui.QApplication.UnicodeUTF8))
        self.tableInstances.horizontalHeaderItem(2).setText(QtGui.QApplication.translate("Dialog", "Reservation ID", None, QtGui.QApplication.UnicodeUTF8))
        self.tableInstances.horizontalHeaderItem(3).setText(QtGui.QApplication.translate("Dialog", "Instance ID", None, QtGui.QApplication.UnicodeUTF8))
        self.tableInstances.horizontalHeaderItem(4).setText(QtGui.QApplication.translate("Dialog", "Image ID", None, QtGui.QApplication.UnicodeUTF8))
        self.tableInstances.horizontalHeaderItem(5).setText(QtGui.QApplication.translate("Dialog", "IP Address", None, QtGui.QApplication.UnicodeUTF8))
        self.tableInstances.horizontalHeaderItem(6).setText(QtGui.QApplication.translate("Dialog", "Key name", None, QtGui.QApplication.UnicodeUTF8))
        self.tableInstances.horizontalHeaderItem(7).setText(QtGui.QApplication.translate("Dialog", "Assigned", None, QtGui.QApplication.UnicodeUTF8))


if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    Dialog = QtGui.QDialog()
    ui = Ui_Dialog()
    ui.setupUi(Dialog)
    Dialog.show()
    sys.exit(app.exec_())

