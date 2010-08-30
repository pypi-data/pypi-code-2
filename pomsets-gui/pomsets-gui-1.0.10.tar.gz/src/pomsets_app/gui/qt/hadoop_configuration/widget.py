# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'resources/qt/hadoop configuration dialog.ui'
#
# Created: Thu Mar  4 21:37:13 2010
#      by: PyQt4 UI code generator 4.7
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(560, 180)
        self.buttonBox = QtGui.QDialogButtonBox(Dialog)
        self.buttonBox.setGeometry(QtCore.QRect(190, 130, 341, 32))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.label = QtGui.QLabel(Dialog)
        self.label.setGeometry(QtCore.QRect(20, 29, 111, 16))
        self.label.setObjectName("label")
        self.textEditHadoopHome = QtGui.QLineEdit(Dialog)
        self.textEditHadoopHome.setGeometry(QtCore.QRect(140, 20, 391, 31))
        self.textEditHadoopHome.setObjectName("textEditHadoopHome")
        self.label_2 = QtGui.QLabel(Dialog)
        self.label_2.setGeometry(QtCore.QRect(20, 69, 101, 16))
        self.label_2.setObjectName("label_2")
        self.textEditStreamingJar = QtGui.QLineEdit(Dialog)
        self.textEditStreamingJar.setGeometry(QtCore.QRect(140, 60, 301, 31))
        self.textEditStreamingJar.setObjectName("textEditStreamingJar")
        self.buttonBrowse = QtGui.QPushButton(Dialog)
        self.buttonBrowse.setGeometry(QtCore.QRect(444, 60, 91, 32))
        self.buttonBrowse.setObjectName("buttonBrowse")
        self.checkBoxRelative = QtGui.QCheckBox(Dialog)
        self.checkBoxRelative.setGeometry(QtCore.QRect(150, 100, 231, 20))
        self.checkBoxRelative.setObjectName("checkBoxRelative")

        self.retranslateUi(Dialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("accepted()"), Dialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("rejected()"), Dialog.reject)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QtGui.QApplication.translate("Dialog", "Hadoop configuration", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("Dialog", "HADOOP_HOME", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("Dialog", "Streaming jar", None, QtGui.QApplication.UnicodeUTF8))
        self.buttonBrowse.setText(QtGui.QApplication.translate("Dialog", "Browse", None, QtGui.QApplication.UnicodeUTF8))
        self.checkBoxRelative.setText(QtGui.QApplication.translate("Dialog", "Relative to HADOOP_HOME", None, QtGui.QApplication.UnicodeUTF8))


if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    Dialog = QtGui.QDialog()
    ui = Ui_Dialog()
    ui.setupUi(Dialog)
    Dialog.show()
    sys.exit(app.exec_())

