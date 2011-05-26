# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'src_ui/ui_choose_format.ui'
#
# Created: Sat May  7 23:32:54 2011
#      by: PyQt4 UI code generator 4.7.4
#
# WARNING! All changes made in this file will be lost!

from watchvideo.qt import QtCore, QtGui

class Ui_ChooseFormat(object):
    def setupUi(self, ChooseFormat):
        ChooseFormat.setObjectName("ChooseFormat")
        ChooseFormat.setWindowModality(QtCore.Qt.WindowModal)
        ChooseFormat.resize(479, 213)
        self.verticalLayout = QtGui.QVBoxLayout(ChooseFormat)
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.tree_medias = QtGui.QTreeWidget(ChooseFormat)
        self.tree_medias.setRootIsDecorated(False)
        self.tree_medias.setObjectName("tree_medias")
        self.tree_medias.header().setVisible(True)
        self.tree_medias.header().setDefaultSectionSize(300)
        self.tree_medias.header().setHighlightSections(False)
        self.tree_medias.header().setMinimumSectionSize(100)
        self.tree_medias.header().setSortIndicatorShown(False)
        self.tree_medias.header().setStretchLastSection(True)
        self.horizontalLayout.addWidget(self.tree_medias)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.buttonBox = QtGui.QDialogButtonBox(ChooseFormat)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(ChooseFormat)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("accepted()"), ChooseFormat.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("rejected()"), ChooseFormat.reject)
        QtCore.QMetaObject.connectSlotsByName(ChooseFormat)

    def retranslateUi(self, ChooseFormat):
        ChooseFormat.setWindowTitle(QtGui.QApplication.translate("ChooseFormat", "Choose Format", None, QtGui.QApplication.UnicodeUTF8))
        self.tree_medias.headerItem().setText(0, QtGui.QApplication.translate("ChooseFormat", "Title", None, QtGui.QApplication.UnicodeUTF8))
        self.tree_medias.headerItem().setText(1, QtGui.QApplication.translate("ChooseFormat", "Format", None, QtGui.QApplication.UnicodeUTF8))

