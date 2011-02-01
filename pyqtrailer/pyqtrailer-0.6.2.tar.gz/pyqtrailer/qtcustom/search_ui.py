# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/w0rm/work/projects/pyqtrailer/pyqtrailer/qtcustom/search.ui'
#
# Created: Tue Feb  1 12:53:54 2011
#      by: PyQt4 UI code generator 4.7.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_Search(object):
    def setupUi(self, Search):
        Search.setObjectName("Search")
        Search.resize(265, 79)
        self.gridLayout = QtGui.QGridLayout(Search)
        self.gridLayout.setObjectName("gridLayout")
        self.splitter = QtGui.QSplitter(Search)
        self.splitter.setOrientation(QtCore.Qt.Horizontal)
        self.splitter.setObjectName("splitter")
        self.label = QtGui.QLabel(self.splitter)
        self.label.setObjectName("label")
        self.lineEdit = QtGui.QLineEdit(self.splitter)
        self.lineEdit.setObjectName("lineEdit")
        self.gridLayout.addWidget(self.splitter, 0, 0, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(Search)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.gridLayout.addWidget(self.buttonBox, 1, 0, 1, 1)

        self.retranslateUi(Search)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("accepted()"), Search.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("rejected()"), Search.reject)
        QtCore.QMetaObject.connectSlotsByName(Search)

    def retranslateUi(self, Search):
        Search.setWindowTitle(QtGui.QApplication.translate("Search", "Dialog", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("Search", "Search for:", None, QtGui.QApplication.UnicodeUTF8))

