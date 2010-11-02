# #START_LICENSE###########################################################
#
#
# This file is part of the Environment for Tree Exploration program
# (ETE).  http://ete.cgenomics.org
#  
# ETE is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#  
# ETE is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY
# or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public
# License for more details.
#  
# You should have received a copy of the GNU General Public License
# along with ETE.  If not, see <http://www.gnu.org/licenses/>.
#
# 
#                     ABOUT THE ETE PACKAGE
#                     =====================
# 
# ETE is distributed under the policy of the GPL copyleft license
# (2008-2010). ETE is developed in the context of a research
# community. References and citations to the specific methods
# implemented are indicated in the documentation of the corresponding
# functions.
#
# ETE original authors and references can be found in the last ETE
# publication:
#
# [1] ETE: a python Environment for Tree Exploration. Jaime
# Huerta-Cepas, Joaquin Dopazo and Toni Gabaldon. BMC Bioinformatics
# 2010,:24doi:10.1186/1471-2105-11-24
#
# If you use ETE for your analysis, please support its development by
# citing the program.
#
# The ETE package is currently written and maintained by Jaime Huerta-Cepas
# (jhcepas@gmail.com)
#
# Documentation can be found at http://ete.cgenomics.org
#
# 
# #END_LICENSE#############################################################
__VERSION__="ete2-2.0rev110" 
# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'search_dialog.ui'
#
# Created: Mon Sep 14 11:11:49 2009
#      by: PyQt4 UI code generator 4.5.4
#
# WARNING! All changes made in this file will be lost!

try:
    from PyQt4 import QtCore, QtGui
except ImportError:
    import QtCore, QtGui


class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.setWindowModality(QtCore.Qt.ApplicationModal)
        Dialog.resize(424, 160)
        self.buttonBox = QtGui.QDialogButtonBox(Dialog)
        self.buttonBox.setGeometry(QtCore.QRect(140, 120, 171, 32))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setCenterButtons(True)
        self.buttonBox.setObjectName("buttonBox")
        self.leaves_only = QtGui.QCheckBox(Dialog)
        self.leaves_only.setWindowModality(QtCore.Qt.NonModal)
        self.leaves_only.setGeometry(QtCore.QRect(30, 80, 181, 24))
        self.leaves_only.setObjectName("leaves_only")
        self.attrType = QtGui.QComboBox(Dialog)
        self.attrType.setGeometry(QtCore.QRect(80, 40, 181, 23))
        self.attrType.setObjectName("attrType")
        self.attrType.addItem(QtCore.QString())
        self.attrType.addItem(QtCore.QString())
        self.attrType.addItem(QtCore.QString())
        self.attrType.addItem(QtCore.QString())
        self.attrType.addItem(QtCore.QString())
        self.attrType.addItem(QtCore.QString())
        self.attrType.addItem(QtCore.QString())
        self.attrType.addItem(QtCore.QString())
        self.label = QtGui.QLabel(Dialog)
        self.label.setGeometry(QtCore.QRect(10, 10, 181, 20))
        self.label.setObjectName("label")
        self.attrName = QtGui.QLineEdit(Dialog)
        self.attrName.setGeometry(QtCore.QRect(270, 10, 113, 25))
        self.attrName.setObjectName("attrName")
        self.attrValue = QtGui.QLineEdit(Dialog)
        self.attrValue.setGeometry(QtCore.QRect(270, 40, 113, 25))
        self.attrValue.setObjectName("attrValue")

        self.retranslateUi(Dialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("accepted()"), Dialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("rejected()"), Dialog.reject)
        QtCore.QMetaObject.connectSlotsByName(Dialog)
        Dialog.setTabOrder(self.attrName, self.attrType)
        Dialog.setTabOrder(self.attrType, self.attrValue)
        Dialog.setTabOrder(self.attrValue, self.leaves_only)
        Dialog.setTabOrder(self.leaves_only, self.buttonBox)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QtGui.QApplication.translate("Dialog", "Dialog", None, QtGui.QApplication.UnicodeUTF8))
        self.leaves_only.setText(QtGui.QApplication.translate("Dialog", "Search only for leaf nodes", None, QtGui.QApplication.UnicodeUTF8))
        self.attrType.setItemText(0, QtGui.QApplication.translate("Dialog", "is", None, QtGui.QApplication.UnicodeUTF8))
        self.attrType.setItemText(1, QtGui.QApplication.translate("Dialog", "contains", None, QtGui.QApplication.UnicodeUTF8))
        self.attrType.setItemText(2, QtGui.QApplication.translate("Dialog", "== ", None, QtGui.QApplication.UnicodeUTF8))
        self.attrType.setItemText(3, QtGui.QApplication.translate("Dialog", ">=", None, QtGui.QApplication.UnicodeUTF8))
        self.attrType.setItemText(4, QtGui.QApplication.translate("Dialog", ">", None, QtGui.QApplication.UnicodeUTF8))
        self.attrType.setItemText(5, QtGui.QApplication.translate("Dialog", "<=", None, QtGui.QApplication.UnicodeUTF8))
        self.attrType.setItemText(6, QtGui.QApplication.translate("Dialog", "<", None, QtGui.QApplication.UnicodeUTF8))
        self.attrType.setItemText(7, QtGui.QApplication.translate("Dialog", "matches this regular expression", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("Dialog", "Search nodes with attribute", None, QtGui.QApplication.UnicodeUTF8))
        self.attrName.setText(QtGui.QApplication.translate("Dialog", "name", None, QtGui.QApplication.UnicodeUTF8))
