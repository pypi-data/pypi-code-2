# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'wordlists.ui'
#
# Created: Mon Jun  7 15:50:28 2010
#      by: PyQt4 UI code generator 4.7.3
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_Wordlists(object):
    def setupUi(self, Wordlists):
        Wordlists.setObjectName("Wordlists")
        Wordlists.setWindowModality(QtCore.Qt.ApplicationModal)
        Wordlists.resize(535, 358)
        Wordlists.setModal(True)
        self.verticalLayoutWidget = QtGui.QWidget(Wordlists)
        self.verticalLayoutWidget.setGeometry(QtCore.QRect(10, 10, 511, 331))
        self.verticalLayoutWidget.setObjectName("verticalLayoutWidget")
        self.verticalLayout = QtGui.QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.wls = QtGui.QListWidget(self.verticalLayoutWidget)
        self.wls.setAcceptDrops(True)
        self.wls.setObjectName("wls")
        self.horizontalLayout.addWidget(self.wls)
        self.verticalLayout_2 = QtGui.QVBoxLayout()
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.pb_add = QtGui.QPushButton(self.verticalLayoutWidget)
        self.pb_add.setObjectName("pb_add")
        self.verticalLayout_2.addWidget(self.pb_add)
        self.pb_remove = QtGui.QPushButton(self.verticalLayoutWidget)
        self.pb_remove.setObjectName("pb_remove")
        self.verticalLayout_2.addWidget(self.pb_remove)
        spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout_2.addItem(spacerItem)
        self.pb_save = QtGui.QPushButton(self.verticalLayoutWidget)
        self.pb_save.setObjectName("pb_save")
        self.verticalLayout_2.addWidget(self.pb_save)
        self.pb_cancel = QtGui.QPushButton(self.verticalLayoutWidget)
        self.pb_cancel.setObjectName("pb_cancel")
        self.verticalLayout_2.addWidget(self.pb_cancel)
        self.horizontalLayout.addLayout(self.verticalLayout_2)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.label = QtGui.QLabel(self.verticalLayoutWidget)
        self.label.setWordWrap(True)
        self.label.setObjectName("label")
        self.verticalLayout.addWidget(self.label)

        self.retranslateUi(Wordlists)
        QtCore.QMetaObject.connectSlotsByName(Wordlists)

    def retranslateUi(self, Wordlists):
        Wordlists.setWindowTitle(QtGui.QApplication.translate("Wordlists", "Word Lists", None, QtGui.QApplication.UnicodeUTF8))
        self.pb_add.setText(QtGui.QApplication.translate("Wordlists", "&Add", None, QtGui.QApplication.UnicodeUTF8))
        self.pb_remove.setText(QtGui.QApplication.translate("Wordlists", "&Remove", None, QtGui.QApplication.UnicodeUTF8))
        self.pb_save.setText(QtGui.QApplication.translate("Wordlists", "&Save", None, QtGui.QApplication.UnicodeUTF8))
        self.pb_cancel.setText(QtGui.QApplication.translate("Wordlists", "&Cancel", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("Wordlists", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'Sans\'; font-size:10pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">You may drag and drop text from a <span style=\" font-style:italic;\">text-editor</span> or file(s) from a <span style=\" font-style:italic;\">file browser</span> onto the word list selector above to add word lists.</p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Click \'<span style=\" text-decoration: underline;\">S</span>ave\' to save your settings and start a new game.</p></body></html>", None, QtGui.QApplication.UnicodeUTF8))

