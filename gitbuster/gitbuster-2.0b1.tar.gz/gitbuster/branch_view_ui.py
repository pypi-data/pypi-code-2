# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'branch_view.ui'
#
# Created: Wed Jun  1 18:00:31 2011
#      by: PyQt4 UI code generator 4.8.3
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_BranchView(object):
    def setupUi(self, BranchView):
        BranchView.setObjectName(_fromUtf8("BranchView"))
        BranchView.resize(320, 676)
        BranchView.setMinimumSize(QtCore.QSize(320, 0))
        BranchView.setMaximumSize(QtCore.QSize(320, 16777215))
        self.gridLayout = QtGui.QGridLayout(BranchView)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.label = QtGui.QLabel(BranchView)
        self.label.setText(_fromUtf8(""))
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)
        self.graphicsView = QtGui.QGraphicsView(BranchView)
        self.graphicsView.setFocusPolicy(QtCore.Qt.NoFocus)
        self.graphicsView.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        self.graphicsView.setSceneRect(QtCore.QRectF(0.0, 0.0, 260.0, 10000.0))
        self.graphicsView.setAlignment(QtCore.Qt.AlignBottom|QtCore.Qt.AlignJustify)
        self.graphicsView.setObjectName(_fromUtf8("graphicsView"))
        self.gridLayout.addWidget(self.graphicsView, 1, 0, 1, 1)

        self.retranslateUi(BranchView)
        QtCore.QMetaObject.connectSlotsByName(BranchView)

    def retranslateUi(self, BranchView):
        BranchView.setWindowTitle(QtGui.QApplication.translate("BranchView", "Form", None, QtGui.QApplication.UnicodeUTF8))

