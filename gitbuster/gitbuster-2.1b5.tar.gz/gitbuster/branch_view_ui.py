# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'branch_view.ui'
#
# Created: Sat Jun 25 10:02:05 2011
#      by: PyQt4 UI code generator 4.7.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_BranchView(object):
    def setupUi(self, BranchView):
        BranchView.setObjectName("BranchView")
        BranchView.resize(320, 676)
        BranchView.setMinimumSize(QtCore.QSize(320, 0))
        BranchView.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.layout = QtGui.QGridLayout(BranchView)
        self.layout.setObjectName("layout")

        self.retranslateUi(BranchView)
        QtCore.QMetaObject.connectSlotsByName(BranchView)

    def retranslateUi(self, BranchView):
        BranchView.setWindowTitle(QtGui.QApplication.translate("BranchView", "Form", None, QtGui.QApplication.UnicodeUTF8))

