# DjangoDE, an integrated development environment for Django
# Copyright (C) 2010-2011 Andrew Wilkinson
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.

from djangode.utils.qt import QtCore, QtGui, Signal

class DebugBar(QtGui.QDockWidget):
    set_visibility = Signal((bool, ))

    def __init__(self, parent_window):
        QtGui.QDockWidget.__init__(self, parent_window)
        self.setObjectName("DebugBar")

        self.base_widget = QtGui.QWidget()
        self.setWidget(self.base_widget)

        self.layout = QtGui.QHBoxLayout()

        self.frames = QtGui.QListWidget(self.base_widget)
        self.frames.addItem("frames")
        self.local_vars = QtGui.QListWidget(self.base_widget)
        self.local_vars.addItem("local_vars")

        self.layout.addWidget(self.frames)
        self.layout.addWidget(self.local_vars)

        self.base_widget.setLayout(self.layout)

        self.set_visibility.connect(self.do_set_visibility)

        self.set_visibility.emit(False)

    def update_data(self, frames, local_vars):
        self.frames.clear()
        for file_name, lineno in frames:
            self.frames.addItem("%s:%i" % (file_name, lineno))

        self.local_vars.clear()
        for var in local_vars:
            self.local_vars.addItem("%s - %s" % var)

    def do_set_visibility(self, visible):
        self.setVisible(visible)