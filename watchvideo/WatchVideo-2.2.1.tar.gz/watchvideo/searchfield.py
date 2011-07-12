# -*- coding: utf-8 -*-
# Copyright (C) 2011 Carlos Pais <freemind@lavabit.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from watchvideo.qt.QtGui import QLineEdit
from watchvideo.qt.QtCore import Qt

class SearchField (QLineEdit):
    def __init__(self, parent, string=""):
        super(SearchField, self).__init__(parent)
        self.setText(self.tr("Search..."))
        self.inactiveTextInPlace = True
        self.textEdited.connect(self.onTextEdited)
        self.resultsWidget = None
        self.inactiveTextStyleSheet()
    
    def focusInEvent(self, event):
        if self.inactiveTextInPlace:
            self.clear()
            self.setStyleSheet("")
        QLineEdit.focusInEvent(self, event)
    
    def focusOutEvent(self, event):
        if self.inactiveTextInPlace:
            self.setText(self.tr("Search..."))
            self.inactiveTextStyleSheet()
        QLineEdit.focusOutEvent(self, event)
        
    def keyPressEvent(self, event):
        key = event.key()
       
        if key != Qt.Key_Backspace and key != Qt.Key_Enter:
            self.inactiveTextInPlace = False
            
        QLineEdit.keyPressEvent(self, event)
        
    def onTextEdited(self):
        if len( str(self.text()) ) == 0:
            self.inactiveTextInPlace = True
            for i in xrange(self.resultsWidget.topLevelItemCount()-1, -1, -1):
                self.resultsWidget.takeTopLevelItem(i)
                
            
    def addResultsWidget(self, resultsWidget):
        self.resultsWidget = resultsWidget

    def isEmpty(self):
        if len( str(self.text()) ) == 0 or self.inactiveTextInPlace:
            return True
        
        return False
        
    def inactiveTextStyleSheet(self):
        self.setStyleSheet("color: rgb(131, 131, 131);")
