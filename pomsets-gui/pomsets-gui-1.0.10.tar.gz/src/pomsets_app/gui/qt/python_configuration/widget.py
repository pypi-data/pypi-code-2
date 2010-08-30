# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'pomsets-gui/resources/qt/python configuration dialog.ui'
#
# Created: Tue Aug 24 12:18:41 2010
#      by: PyQt4 UI code generator 4.7
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_dialog(object):
    def setupUi(self, dialog):
        dialog.setObjectName("dialog")
        dialog.resize(279, 180)
        self.buttonBox = QtGui.QDialogButtonBox(dialog)
        self.buttonBox.setGeometry(QtCore.QRect(20, 140, 241, 32))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.groupBox = QtGui.QGroupBox(dialog)
        self.groupBox.setGeometry(QtCore.QRect(20, 20, 241, 101))
        self.groupBox.setObjectName("groupBox")
        self.executeLocalButton = QtGui.QRadioButton(self.groupBox)
        self.executeLocalButton.setGeometry(QtCore.QRect(20, 30, 103, 20))
        self.executeLocalButton.setChecked(True)
        self.executeLocalButton.setObjectName("executeLocalButton")
        self.executePicloudButton = QtGui.QRadioButton(self.groupBox)
        self.executePicloudButton.setGeometry(QtCore.QRect(20, 60, 161, 20))
        self.executePicloudButton.setObjectName("executePicloudButton")

        self.retranslateUi(dialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("accepted()"), dialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("rejected()"), dialog.reject)
        QtCore.QMetaObject.connectSlotsByName(dialog)

    def retranslateUi(self, dialog):
        dialog.setWindowTitle(QtGui.QApplication.translate("dialog", "Python", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox.setTitle(QtGui.QApplication.translate("dialog", "Execute Python functions:", None, QtGui.QApplication.UnicodeUTF8))
        self.executeLocalButton.setText(QtGui.QApplication.translate("dialog", "Locally", None, QtGui.QApplication.UnicodeUTF8))
        self.executePicloudButton.setText(QtGui.QApplication.translate("dialog", "Using PiCloud", None, QtGui.QApplication.UnicodeUTF8))


if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    dialog = QtGui.QDialog()
    ui = Ui_dialog()
    ui.setupUi(dialog)
    dialog.show()
    sys.exit(app.exec_())

