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
__VERSION__="ete2-2.0rev111" 
# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'open_newick.ui'
#
# Created: Mon Sep 14 11:11:49 2009
#      by: PyQt4 UI code generator 4.5.4
#
# WARNING! All changes made in this file will be lost!

try:
    from PyQt4 import QtCore, QtGui
except ImportError:
    import QtCore, QtGui

class Ui_OpenNewick(object):
    def setupUi(self, OpenNewick):
        OpenNewick.setObjectName("OpenNewick")
        OpenNewick.resize(569, 353)
        self.comboBox = QtGui.QComboBox(OpenNewick)
        self.comboBox.setGeometry(QtCore.QRect(460, 300, 81, 23))
        self.comboBox.setObjectName("comboBox")
        self.widget = QtGui.QWidget(OpenNewick)
        self.widget.setGeometry(QtCore.QRect(30, 10, 371, 321))
        self.widget.setObjectName("widget")

        self.retranslateUi(OpenNewick)
        QtCore.QMetaObject.connectSlotsByName(OpenNewick)

    def retranslateUi(self, OpenNewick):
        OpenNewick.setWindowTitle(QtGui.QApplication.translate("OpenNewick", "Dialog", None, QtGui.QApplication.UnicodeUTF8))
