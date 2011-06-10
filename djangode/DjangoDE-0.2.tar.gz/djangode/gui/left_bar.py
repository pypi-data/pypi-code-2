# DjangoDE, an integrated development environment for Django
# Copyright (C) 2010 Andrew Wilkinson
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

import pickle
import os
import os.path

from djangode import global_objects
from djangode.project import Url, UrlInclude
from djangode.utils.qt import QtCore, QtGui, Slot

from app_pane import AppPane

class LeftBar(QtGui.QDockWidget):
    def __init__(self, parent_window):
        QtGui.QDockWidget.__init__(self, parent_window)
        self.setObjectName("LeftBar")

        self.tabs = None
        self.build_tabs()

    def build_tabs(self):
        if self.tabs is not None:
            self.tabs.clear()
        else:
            self.tabs = QtGui.QTabWidget(self)
            self.tabs.setTabPosition(QtGui.QTabWidget.West)

        self.urls = URLsPane(self)
        self.tabs.addTab(self.urls, "URLs")

        if global_objects.project is not None:
            apps = global_objects.project.get_setting_value("INSTALLED_APPS")

            self.apps_panes = {}

            if apps is not None:
                for app in apps:
                    self.apps_panes[app] = AppPane(self, app)

                    self.tabs.addTab(self.apps_panes[app], app)

        self.settings_pane = SettingsPane(self)
        self.tabs.addTab(self.settings_pane, "Settings")

        self.files = QtGui.QTreeView(self)
        self.files_model = QtGui.QFileSystemModel()
        self.files_model.setRootPath(unicode(QtCore.QDir.homePath))
        self.files.setModel(self.files_model)

        self.tabs.addTab(self.files, "Files")

        self.setWidget(self.tabs)

    def reload_project(self):
        self.build_tabs()

        if global_objects.project is not None:
            self.files_model.setRootPath(os.path.dirname(global_objects.project.manage_file))
        else:
            self.files_model.setRootPath("/")

class SettingsPane(QtGui.QWidget):
    def __init__(self, parent):
        QtGui.QWidget.__init__(self, parent)

        self.settings_layout = QtGui.QVBoxLayout()

        self.settings = QtGui.QListWidget(self)
        self.settings.itemDoubleClicked.connect(self.open_setting)

        self.open_settings_button = QtGui.QPushButton("Open Settings", self)
        self.open_settings_button.clicked.connect(self.open_settings)

        self.settings_layout.addWidget(self.settings)
        self.settings_layout.addWidget(self.open_settings_button)

        self.setLayout(self.settings_layout)

        if global_objects.project is not None:
            for setting in global_objects.project.get_settings_names():
                self.settings.addItem(setting)

    @Slot()
    def open_settings(self):
        global_objects.main_window.editor.open_file[(str, int)].emit(os.path.join(global_objects.project.base_path, "settings.py"), 0)

    @Slot(QtGui.QListWidgetItem)
    def open_setting(self, item):
        setting = item.text()

        #global_objects.main_window.editor.do_open_file(os.path.join(global_objects.project.base_path, "settings.py"), setting)
        global_objects.main_window.editor.open_file[(str, str)].emit(os.path.join(global_objects.project.base_path, "settings.py"), setting)

class URLsPane(QtGui.QWidget):
    def __init__(self, parent):
        QtGui.QWidget.__init__(self, parent)

        self.layout = QtGui.QVBoxLayout()

        self.urls = QtGui.QTreeWidget(self)
        self.urls.itemDoubleClicked.connect(self.open_url)

        open_urls_button = QtGui.QPushButton("Open URLs", self)
        open_urls_button.clicked.connect(self.open_urls)

        self.layout.addWidget(self.urls)
        self.layout.addWidget(open_urls_button)

        self.setLayout(self.layout)

        if global_objects.project is not None:
            self.urls_model = global_objects.project.get_urls_model()
            self.update_urls()

    def open_urls(self):
        global_objects.main_window.editor.open_file[(str, int)].emit(os.path.join(global_objects.project.base_path, "urls.py"), 0)

    def update_urls(self):
        self.urls.clear()

        def add_urls(node, url):
            new_node = QtGui.QTreeWidgetItem([url.re_text])
            node.addChild(new_node)

            if isinstance(url, UrlInclude):
                for child in url.children:
                    add_urls(new_node, child)
            elif isinstance(url, Url):
                new_node.setData(0, 32, pickle.dumps(url.func_name, 0))

        root = QtGui.QTreeWidgetItem(["/"])
        self.urls.addTopLevelItem(root)

        for url in self.urls_model.root_url.children:
            add_urls(root, url)

    def open_url(self, tree_item):
        if tree_item.text(0) == "/":
            global_objects.main_window.editor.open_url("/")
        else:
            url = pickle.loads(str(tree_item.data(0, 32).toString()))

            global_objects.main_window.editor.open_file[(str, str)].emit(url[0], url[1])
