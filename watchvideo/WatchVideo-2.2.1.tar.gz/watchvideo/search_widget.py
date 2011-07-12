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

from watchvideo.qt.QtGui import QDockWidget

class SearchWidget(QDockWidget):
    
    def addAction(self, action):
        self.action = action
        
    def closeEvent(self, event):
        self.action.setChecked(False)
        QDockWidget.closeEvent(self, event)
