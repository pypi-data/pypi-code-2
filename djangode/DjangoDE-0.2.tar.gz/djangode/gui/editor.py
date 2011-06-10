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

from djangode import global_objects
from djangode.utils.qt import QtCore, QtGui, Signal, Slot

from browser_tab import BrowserTab
from python_editor import PythonEditor

class Editor(QtGui.QTabWidget):
    open_file = Signal((str, ), (str, int), (str, str), )
    set_debug_line = Signal((str, int))

    def __init__(self):
        QtGui.QTabWidget.__init__(self)

        self.setTabsClosable(True)

        self.tabCloseRequested.connect(self.close_tab)

        self.open_files = {}

        self.insertTab(0, BrowserTab(self), "Browser")

        self.open_file[str].connect(self.do_open_file)
        self.open_file[(str, str)].connect(self.do_open_file)
        self.open_file[(str, int)].connect(self.do_open_file)
        self.set_debug_line.connect(self.do_set_debug_line)

    def new_file(self):
        editor = PythonEditor(None)

        idx = self.insertTab(0, editor, "New File")
        self.setCurrentIndex(idx)
        editor.setFocus(QtCore.Qt.OtherFocusReason)

        self.process_open_files()

    def open_file_action(self):
        filename = QtGui.QFileDialog.getOpenFileName(global_objects.main_window, "Open File", QtCore.QDir.homePath(), "Python (*.py)")

        self.open_file[(str, int)].emit(filename, 0)

    def save_file(self):
        self.widget(self.currentIndex()).save()

    @Slot(str)
    @Slot(str, str)
    @Slot(str, int)
    def do_open_file(self, file_name, seek=None):
        file_name = unicode(file_name)

        if file_name.endswith(".pyc"):
            file_name = file_name[:-1]

        if file_name.endswith(".py"):
            if file_name in self.open_files:
                self.setCurrentIndex(self.open_files[file_name])
                editor = self.widget(self.open_files[file_name])
            else:
                editor = PythonEditor(self, file_name)

                idx = self.insertTab(0, editor, file_name)
                self.setCurrentIndex(idx)

                self.process_open_files()

            if isinstance(seek, int):
                editor.scroll_to_line(seek)
            elif isinstance(seek, str):
                editor.scroll_to_first_instance(seek)
            else:
                editor.scroll_to_top()

    def open_url(self, url):
        tab = BrowserTab(self)
        tab.url_bar.setText("/")
        tab.url_changed("/")

        idx = self.insertTab(0, tab, "Browser")
        self.setCurrentIndex(idx)

    def process_open_files(self):
        self.open_files = {}
        for i in range(self.count()):
            if hasattr(self.widget(i), "file_name"):
                self.open_files[self.widget(i).file_name] = i

    def close_tab(self, i):
        if self.widget(i).close():
            self.removeTab(i)
            self.process_open_files()

    def reload_project(self):
        for i in range(self.count()):
            if isinstance(self.widget(i), BrowserTab):
                self.widget(i).reload()

    def get_editor_for_file(self, file_name):
        file_name = unicode(file_name)

        if file_name not in self.open_files:
            return None

        return self.widget(self.open_files[file_name])

    def do_set_debug_line(self, filename, line_no):
        self.get_editor_for_file(filename).set_debug_line(line_no)

    def toggle_breakpoint(self):
        current_widget = self.currentWidget()
        if isinstance(current_widget, PythonEditor):
            current_widget.toggle_breakpoint()
