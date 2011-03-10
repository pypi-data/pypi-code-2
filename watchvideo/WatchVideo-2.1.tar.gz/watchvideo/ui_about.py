# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'src_ui/ui_about.ui'
#
# Created: Tue Mar  8 20:42:02 2011
#      by: PyQt4 UI code generator 4.7.4
#
# WARNING! All changes made in this file will be lost!

from watchvideo.qt import QtCore, QtGui

class Ui_AboutDialog(object):
    def setupUi(self, AboutDialog):
        AboutDialog.setObjectName("AboutDialog")
        AboutDialog.resize(500, 400)
        AboutDialog.setMaximumSize(QtCore.QSize(500, 400))
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/media/watchvideo-32x32.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        AboutDialog.setWindowIcon(icon)
        AboutDialog.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.verticalLayout = QtGui.QVBoxLayout(AboutDialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.tabWidget = QtGui.QTabWidget(AboutDialog)
        self.tabWidget.setObjectName("tabWidget")
        self.t_about = QtGui.QWidget()
        self.t_about.setObjectName("t_about")
        self.tabWidget.addTab(self.t_about, "")
        self.t_credits = QtGui.QWidget()
        self.t_credits.setObjectName("t_credits")
        self.gridLayout = QtGui.QGridLayout(self.t_credits)
        self.gridLayout.setObjectName("gridLayout")
        self.tedit_credits = QtGui.QTextEdit(self.t_credits)
        self.tedit_credits.setReadOnly(True)
        self.tedit_credits.setObjectName("tedit_credits")
        self.gridLayout.addWidget(self.tedit_credits, 0, 0, 1, 1)
        self.tabWidget.addTab(self.t_credits, "")
        self.t_license = QtGui.QWidget()
        self.t_license.setObjectName("t_license")
        self.gridLayout_2 = QtGui.QGridLayout(self.t_license)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.tedit_license = QtGui.QTextEdit(self.t_license)
        self.tedit_license.setReadOnly(True)
        self.tedit_license.setObjectName("tedit_license")
        self.gridLayout_2.addWidget(self.tedit_license, 0, 0, 1, 1)
        self.tabWidget.addTab(self.t_license, "")
        self.verticalLayout.addWidget(self.tabWidget)
        self.b_close = QtGui.QPushButton(AboutDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.b_close.sizePolicy().hasHeightForWidth())
        self.b_close.setSizePolicy(sizePolicy)
        self.b_close.setLayoutDirection(QtCore.Qt.RightToLeft)
        self.b_close.setObjectName("b_close")
        self.verticalLayout.addWidget(self.b_close)

        self.retranslateUi(AboutDialog)
        self.tabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(AboutDialog)

    def retranslateUi(self, AboutDialog):
        AboutDialog.setWindowTitle(QtGui.QApplication.translate("AboutDialog", "About", None, QtGui.QApplication.UnicodeUTF8))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.t_about), QtGui.QApplication.translate("AboutDialog", "About", None, QtGui.QApplication.UnicodeUTF8))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.t_credits), QtGui.QApplication.translate("AboutDialog", "Credits", None, QtGui.QApplication.UnicodeUTF8))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.t_license), QtGui.QApplication.translate("AboutDialog", "License", None, QtGui.QApplication.UnicodeUTF8))
        self.b_close.setText(QtGui.QApplication.translate("AboutDialog", "Close", None, QtGui.QApplication.UnicodeUTF8))

from watchvideo import icons_rc
assert icons_rc
