# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui/settings.ui'
#
# Created: Thu Sep  8 16:31:03 2011
#      by: PyQt4 UI code generator 4.7.3
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(495, 253)
        self.gridLayout = QtGui.QGridLayout(Dialog)
        self.gridLayout.setObjectName("gridLayout")
        self.buttonBox = QtGui.QDialogButtonBox(Dialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.gridLayout.addWidget(self.buttonBox, 2, 0, 1, 1)
        self.tabWidget = QtGui.QTabWidget(Dialog)
        self.tabWidget.setObjectName("tabWidget")
        self.pad_tab = QtGui.QWidget()
        self.pad_tab.setObjectName("pad_tab")
        self.groupBox = QtGui.QGroupBox(self.pad_tab)
        self.groupBox.setGeometry(QtCore.QRect(10, 60, 451, 81))
        self.groupBox.setObjectName("groupBox")
        self.label = QtGui.QLabel(self.groupBox)
        self.label.setGeometry(QtCore.QRect(10, 50, 121, 16))
        self.label.setObjectName("label")
        self.label_2 = QtGui.QLabel(self.groupBox)
        self.label_2.setGeometry(QtCore.QRect(10, 20, 121, 16))
        self.label_2.setObjectName("label_2")
        self.AccessCodeEdit = QtGui.QLineEdit(self.groupBox)
        self.AccessCodeEdit.setGeometry(QtCore.QRect(130, 50, 311, 21))
        self.AccessCodeEdit.setObjectName("AccessCodeEdit")
        self.PadHostEdit = QtGui.QLineEdit(self.groupBox)
        self.PadHostEdit.setGeometry(QtCore.QRect(130, 20, 311, 21))
        self.PadHostEdit.setObjectName("PadHostEdit")
        self.converterSelect = QtGui.QComboBox(self.pad_tab)
        self.converterSelect.setGeometry(QtCore.QRect(290, 20, 171, 22))
        self.converterSelect.setObjectName("converterSelect")
        self.label_3 = QtGui.QLabel(self.pad_tab)
        self.label_3.setGeometry(QtCore.QRect(170, 20, 111, 16))
        self.label_3.setObjectName("label_3")
        self.tabWidget.addTab(self.pad_tab, "")
        self.gridLayout.addWidget(self.tabWidget, 0, 0, 1, 1)

        self.retranslateUi(Dialog)
        self.tabWidget.setCurrentIndex(0)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("accepted()"), Dialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("rejected()"), Dialog.reject)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QtGui.QApplication.translate("Dialog", "Настройки", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox.setTitle(QtGui.QApplication.translate("Dialog", "Синхронизация с zenpad.ru", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("Dialog", "Код доступа", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("Dialog", "Домен блокнота", None, QtGui.QApplication.UnicodeUTF8))
        self.label_3.setText(QtGui.QApplication.translate("Dialog", "Формат данных", None, QtGui.QApplication.UnicodeUTF8))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.pad_tab), QtGui.QApplication.translate("Dialog", "Настройки блокнота", None, QtGui.QApplication.UnicodeUTF8))

