# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/w0rm/projects/python/pyqtrailer/pyqtrailer/qtcustom/settings.ui'
#
# Created: Sun Sep 19 18:11:00 2010
#      by: PyQt4 UI code generator 4.7.3
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_SettingsDialog(object):
    def setupUi(self, SettingsDialog):
        SettingsDialog.setObjectName("SettingsDialog")
        SettingsDialog.resize(467, 282)
        self.gridLayout = QtGui.QGridLayout(SettingsDialog)
        self.gridLayout.setObjectName("gridLayout")
        self.groupBox_2 = QtGui.QGroupBox(SettingsDialog)
        self.groupBox_2.setObjectName("groupBox_2")
        self.horizontalLayout = QtGui.QHBoxLayout(self.groupBox_2)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.downloadPath = QtGui.QLineEdit(self.groupBox_2)
        self.downloadPath.setText("")
        self.downloadPath.setObjectName("downloadPath")
        self.horizontalLayout.addWidget(self.downloadPath)
        self.browseButton = QtGui.QPushButton(self.groupBox_2)
        self.browseButton.setObjectName("browseButton")
        self.horizontalLayout.addWidget(self.browseButton)
        self.gridLayout.addWidget(self.groupBox_2, 0, 0, 1, 2)
        self.groupBox = QtGui.QGroupBox(SettingsDialog)
        self.groupBox.setMaximumSize(QtCore.QSize(16777215, 150))
        self.groupBox.setObjectName("groupBox")
        self.gridLayout_2 = QtGui.QGridLayout(self.groupBox)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.filterList = QtGui.QListWidget(self.groupBox)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.filterList.sizePolicy().hasHeightForWidth())
        self.filterList.setSizePolicy(sizePolicy)
        self.filterList.setMinimumSize(QtCore.QSize(80, 110))
        self.filterList.setMaximumSize(QtCore.QSize(80, 110))
        self.filterList.setObjectName("filterList")
        QtGui.QListWidgetItem(self.filterList)
        QtGui.QListWidgetItem(self.filterList)
        QtGui.QListWidgetItem(self.filterList)
        QtGui.QListWidgetItem(self.filterList)
        QtGui.QListWidgetItem(self.filterList)
        QtGui.QListWidgetItem(self.filterList)
        self.gridLayout_2.addWidget(self.filterList, 0, 0, 3, 1)
        self.qualityUp = QtGui.QToolButton(self.groupBox)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("../../../../../../../usr/share/icons/oxygen/32x32/actions/go-up.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.qualityUp.setIcon(icon)
        self.qualityUp.setObjectName("qualityUp")
        self.gridLayout_2.addWidget(self.qualityUp, 0, 1, 1, 1)
        self.qualityDown = QtGui.QToolButton(self.groupBox)
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap("../../../../../../../usr/share/icons/oxygen/32x32/actions/go-down.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.qualityDown.setIcon(icon1)
        self.qualityDown.setObjectName("qualityDown")
        self.gridLayout_2.addWidget(self.qualityDown, 1, 1, 1, 1)
        spacerItem = QtGui.QSpacerItem(20, 45, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout_2.addItem(spacerItem, 2, 1, 1, 1)
        self.gridLayout.addWidget(self.groupBox, 1, 0, 1, 1)
        self.groupBox_3 = QtGui.QGroupBox(SettingsDialog)
        self.groupBox_3.setMaximumSize(QtCore.QSize(16777215, 150))
        self.groupBox_3.setObjectName("groupBox_3")
        self.verticalLayout = QtGui.QVBoxLayout(self.groupBox_3)
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout_3 = QtGui.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.label = QtGui.QLabel(self.groupBox_3)
        self.label.setObjectName("label")
        self.horizontalLayout_3.addWidget(self.label)
        spacerItem1 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_3.addItem(spacerItem1)
        self.spinReadAhead = QtGui.QSpinBox(self.groupBox_3)
        self.spinReadAhead.setMaximumSize(QtCore.QSize(16777215, 30))
        self.spinReadAhead.setMinimum(1)
        self.spinReadAhead.setMaximum(10)
        self.spinReadAhead.setProperty("value", 4)
        self.spinReadAhead.setObjectName("spinReadAhead")
        self.horizontalLayout_3.addWidget(self.spinReadAhead)
        self.verticalLayout.addLayout(self.horizontalLayout_3)
        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.label_2 = QtGui.QLabel(self.groupBox_3)
        self.label_2.setObjectName("label_2")
        self.horizontalLayout_2.addWidget(self.label_2)
        spacerItem2 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem2)
        self.spinParallelDownload = QtGui.QSpinBox(self.groupBox_3)
        self.spinParallelDownload.setMaximumSize(QtCore.QSize(16777215, 30))
        self.spinParallelDownload.setMinimum(1)
        self.spinParallelDownload.setMaximum(5)
        self.spinParallelDownload.setProperty("value", 2)
        self.spinParallelDownload.setObjectName("spinParallelDownload")
        self.horizontalLayout_2.addWidget(self.spinParallelDownload)
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        self.gridLayout.addWidget(self.groupBox_3, 1, 1, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(SettingsDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.gridLayout.addWidget(self.buttonBox, 2, 1, 1, 1)

        self.retranslateUi(SettingsDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("accepted()"), SettingsDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("rejected()"), SettingsDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(SettingsDialog)

    def retranslateUi(self, SettingsDialog):
        SettingsDialog.setWindowTitle(QtGui.QApplication.translate("SettingsDialog", "Dialog", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox_2.setTitle(QtGui.QApplication.translate("SettingsDialog", "&Download path", None, QtGui.QApplication.UnicodeUTF8))
        self.browseButton.setText(QtGui.QApplication.translate("SettingsDialog", "Browse", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox.setTitle(QtGui.QApplication.translate("SettingsDialog", "&Quality priority", None, QtGui.QApplication.UnicodeUTF8))
        __sortingEnabled = self.filterList.isSortingEnabled()
        self.filterList.setSortingEnabled(False)
        self.filterList.item(0).setText(QtGui.QApplication.translate("SettingsDialog", "480p", None, QtGui.QApplication.UnicodeUTF8))
        self.filterList.item(1).setText(QtGui.QApplication.translate("SettingsDialog", "720p", None, QtGui.QApplication.UnicodeUTF8))
        self.filterList.item(2).setText(QtGui.QApplication.translate("SettingsDialog", "1080p", None, QtGui.QApplication.UnicodeUTF8))
        self.filterList.item(3).setText(QtGui.QApplication.translate("SettingsDialog", "640x360", None, QtGui.QApplication.UnicodeUTF8))
        self.filterList.item(4).setText(QtGui.QApplication.translate("SettingsDialog", "320x180", None, QtGui.QApplication.UnicodeUTF8))
        self.filterList.item(5).setText(QtGui.QApplication.translate("SettingsDialog", "480x204", None, QtGui.QApplication.UnicodeUTF8))
        self.filterList.setSortingEnabled(__sortingEnabled)
        self.qualityUp.setText(QtGui.QApplication.translate("SettingsDialog", "...", None, QtGui.QApplication.UnicodeUTF8))
        self.qualityDown.setText(QtGui.QApplication.translate("SettingsDialog", "...", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox_3.setTitle(QtGui.QApplication.translate("SettingsDialog", "&Performance", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("SettingsDialog", "Read ahead processes", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("SettingsDialog", "Maxiumum parallel downloads", None, QtGui.QApplication.UnicodeUTF8))

