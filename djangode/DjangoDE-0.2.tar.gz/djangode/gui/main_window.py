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

import os

from djangode import global_objects
from djangode.project import Project
from djangode.utils import get_config_value, set_config_value
from djangode.utils.qt import QtCore, QtGui

from debug_bar import DebugBar
from dialogs import AboutDialog, DjangoDESettingsDialog, ProjectSettingsDialog
from editor import Editor
from left_bar import LeftBar
from toolbar import create_toolbar
import wizards

class MainWindow(QtGui.QMainWindow):
    def __init__(self):
        QtGui.QMainWindow.__init__(self)

        self.setWindowTitle('DjangoDE')
        if global_objects.icon is not None:
            self.setWindowIcon(QtGui.QIcon(global_objects.icon))

        self.statusBar().showMessage('Welcome to DjangoDE')

        self.editor = Editor()

        self.setup_actions()

        geometry = get_config_value("geometry")
        if geometry is not None:
            self.restoreGeometry(geometry)

        state = get_config_value("state")
        if state is not None:
            self.restoreState(state)

        self.setCentralWidget(self.editor)

        self.toolbar = create_toolbar(self)

        self.debug_bar = DebugBar(self)
        self.addDockWidget(QtCore.Qt.BottomDockWidgetArea, self.debug_bar)

        self.left_bar = LeftBar(self)
        self.addDockWidget(QtCore.Qt.LeftDockWidgetArea, self.left_bar)

        last_project = get_config_value("last_project")
        if last_project:
            global_objects.project = Project(last_project)
            global_objects.project.runner.start()
        self.reload_project()

    def setup_actions(self):
        self.actions = {}
        menu = self.menuBar()

        exit = QtGui.QAction(QtGui.QIcon.fromTheme("application-exit"), 'Exit', self)
        exit.setShortcut('Ctrl+Q')
        exit.setStatusTip('Exit application')
        exit.triggered.connect(self.close)
        self.actions["exit"] = exit

        new_file = QtGui.QAction(QtGui.QIcon.fromTheme("document-new"), 'New File', self)
        new_file.setShortcut('Ctrl+N')
        new_file.setStatusTip('New file')
        new_file.triggered.connect(self.editor.new_file)
        self.actions["new_file"] = new_file

        open_file = QtGui.QAction(QtGui.QIcon.fromTheme("document-open"), 'Open File', self)
        open_file.setStatusTip('Open an existing file')
        open_file.triggered.connect(self.editor.open_file_action)
        self.actions["open_file"] = open_file

        save_file = QtGui.QAction(QtGui.QIcon.fromTheme("document-save"), 'Save File', self)
        save_file.setShortcut('Ctrl+S')
        save_file.setStatusTip('Save file')
        save_file.triggered.connect(self.editor.save_file)
        self.actions["save_file"] = save_file

        file_menu = menu.addMenu("&File")
        file_menu.addAction(new_file)
        file_menu.addAction(open_file)
        file_menu.addAction(save_file)
        file_menu.addAction(exit)

        new_project = QtGui.QAction(QtGui.QIcon.fromTheme("document-new"), 'New Project', self)
        new_project.setStatusTip('Create a new Django site or a DjangoDE project from an existing site')
        new_project.triggered.connect(self.new_project)
        self.actions["new_project"] = new_project

        open_project = QtGui.QAction(QtGui.QIcon.fromTheme("document-open"), 'Open Project', self)
        open_project.setStatusTip('Open an existing DjangoDE project')
        open_project.triggered.connect(self.open_project)
        self.actions["open_project"] = open_project

        close_project = QtGui.QAction(QtGui.QIcon.fromTheme("document-close"), 'Close Project', self)
        close_project.setStatusTip('Close the currently open DjangoDE project')
        close_project.triggered.connect(self.close_project)
        self.actions["close_project"] = close_project

        project_settings = QtGui.QAction('Project Settings', self)
        project_settings.setStatusTip('Configure the currently open DjangoDE project')
        project_settings.triggered.connect(self.project_settings)
        self.actions["project_settings"] = project_settings

        project_menu = menu.addMenu("&Project")
        project_menu.addAction(new_project)
        project_menu.addAction(open_project)
        project_menu.addAction(close_project)
        project_menu.addSeparator()
        project_menu.addAction(project_settings)
        self.manage_commands = project_menu.addMenu("Manage Commands")

        add_new_app = QtGui.QAction('Create A New App', self)
        add_new_app.setStatusTip('Starts a brand new Django application in this project')
        add_new_app.triggered.connect(self.add_new_app)
        self.actions["add_new_app"] = add_new_app

        self.manage_commands.addAction(add_new_app)

        debug_play = QtGui.QAction(QtGui.QIcon.fromTheme("media-playback-start"), "Continue", self)
        debug_play.triggered.connect(self.debug_play)
        debug_play.setEnabled(False)
        self.actions["debug_play"] = debug_play

        toggle_breakpoint  = QtGui.QAction("Toggle Breakpoint", self)
        toggle_breakpoint.setShortcut(QtGui.QKeySequence("F9"))
        toggle_breakpoint.triggered.connect(self.editor.toggle_breakpoint)
        self.actions["toggle_breakpoint"] = toggle_breakpoint

        project_menu = menu.addMenu("&Debug")
        project_menu.addAction(toggle_breakpoint)

        djangode_settings = QtGui.QAction('DjangoDE Settings', self)
        djangode_settings.setStatusTip('Configure DjangoDE')
        djangode_settings.triggered.connect(self.djangode_settings)
        self.actions["djangode_settings"] = djangode_settings

        project_menu = menu.addMenu("&Settings")
        project_menu.addAction(djangode_settings)

        about = QtGui.QAction('About DjangoDE', self)
        about.setStatusTip('About DjangoDE')
        about.triggered.connect(self.about)
        self.actions["about"] = about

        about_django = QtGui.QAction('About Django', self)
        about_django.setStatusTip('About Django')
        about_django.triggered.connect(self.about_django)
        self.actions["about_django"] = about_django

        help_menu = menu.addMenu("&Help")
        help_menu.addAction(about)
        help_menu.addAction(about_django)
        self.actions["about_django"] = about_django

    def about(self):
        self.about_dialog = AboutDialog()
        self.about_dialog.show()

    def about_django(self):
        """Open the Django Website in a tab"""
        pass

    def new_project(self):
        wizards.NewProjectWizard().exec_()

    def open_project(self):
        filename = QtGui.QFileDialog.getOpenFileName(self, "Open a manage.py file.", os.path.expanduser('~'), "manage.py (*.py)")

        global_objects.project = Project(unicode(filename[0]))
        global_objects.project.runner.start()
        self.reload_project()

    def close_project(self):
        if global_objects.project is not None:
            global_objects.project.close()
            global_objects.project = None
            self.reload_project()

    def project_settings(self):
        self.project_settings_dialog = ProjectSettingsDialog()
        self.project_settings_dialog.show()

    def djangode_settings(self):
        self.djangode_settings_dialog = DjangoDESettingsDialog()
        self.djangode_settings_dialog.show()

    def closeEvent(self, event):
        set_config_value("geometry", self.saveGeometry())
        set_config_value("state", self.saveState())
        set_config_value("last_project", global_objects.project.manage_file if global_objects.project is not None else "")

        if global_objects.project is not None:
            global_objects.project.close()
            global_objects.project = None

        self.project_settings_dialog = None

        return QtGui.QMainWindow.closeEvent(self, event)

    def reload_project(self):
        if global_objects.project is None:
            self.actions["close_project"].setEnabled(False)
            self.actions["project_settings"].setEnabled(False)
            self.actions["add_new_app"].setEnabled(False)
        else:
            self.actions["close_project"].setEnabled(True)
            self.actions["project_settings"].setEnabled(True)
            self.actions["add_new_app"].setEnabled(True)

        self.left_bar.reload_project()
        self.editor.reload_project()

    def add_new_app(self):
        name, ok = QtGui.QInputDialog.getText(self, "DjangoED", "Please enter the name of the new application:")

        if ok and name:
            global_objects.project.add_new_app(str(name))

            QtGui.QMessageBox.information(self, "DjangoED", "Your new application was created.")

    def debug_play(self):
        global_objects.project.debug_play()
