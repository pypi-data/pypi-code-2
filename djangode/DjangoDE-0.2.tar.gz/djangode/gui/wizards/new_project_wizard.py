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
from djangode.utils.qt import QtCore, QtGui

class NewProjectWizard(QtGui.QWizard):
    def __init__(self):
        QtGui.QWizard.__init__(self)

        self.addPage(NewProjectType(self))
        self.addPage(NewProjectLocation(self))
        self.addPage(ExistingProjectLocation(self))
        self.addPage(FinalScreen(self))

    def accept(self):
        if self.page(0).new_project.isChecked():
            project = Project.new_django_project(unicode(self.page(1).directory_path.text()), unicode(self.page(1).project_name.text()))
        else:
            project = Project(unicode(self.page(2).manage_path.text()))

        global_objects.project = project

        global_objects.window.reload_project()

        return QtGui.QWizard.accept(self)

class NewProjectType(QtGui.QWizardPage):
    def __init__(self, parent):
        QtGui.QWizardPage.__init__(self, parent)

        self.setTitle("Create A New DjangoDE Project")
        self.setSubTitle("Specify whether you want to create a brand new Django project, or create a DjangoDE project from an existing site.")

        vbox = QtGui.QVBoxLayout(self)

        group = QtGui.QButtonGroup(vbox)
        group.setExclusive(True)

        self.new_project = QtGui.QRadioButton("Create a new Django project")
        self.new_project.setChecked(True)
        group.addButton(self.new_project)
        vbox.addWidget(self.new_project)

        self.existing_project = QtGui.QRadioButton("Use an existing Django project")
        group.addButton(self.existing_project)
        vbox.addWidget(self.existing_project)

        self.setLayout(vbox)

    def nextId(self):
        if self.new_project.isChecked():
            return 1
        else:
            return 2

class NewProjectLocation(QtGui.QWizardPage):
    def __init__(self, parent):
        QtGui.QWizardPage.__init__(self, parent)

        self.setTitle("Create A New Django Project")
        self.setSubTitle("Choose the location for your new project and give it a name.")

        vbox = QtGui.QVBoxLayout(self)

        project_name_layout = QtGui.QHBoxLayout()
        vbox.addLayout(project_name_layout)

        project_name_layout.addWidget(QtGui.QLabel("Project Name:"))
        self.project_name = QtGui.QLineEdit()
        self.project_name.textChanged.connect(self.key_down)
        project_name_layout.addWidget(self.project_name)

        directory_layout = QtGui.QHBoxLayout()
        vbox.addLayout(directory_layout)

        directory_layout.addWidget(QtGui.QLabel("Directory:"))
        self.directory_path = QtGui.QLineEdit(QtCore.QDir.homePath())
        self.directory_path.textChanged.connect(self.key_down)
        directory_layout.addWidget(self.directory_path)

        self.directory_button = QtGui.QPushButton("Choose Directory")
        self.directory_button.clicked.connect(self.choose_directory)
        directory_layout.addWidget(self.directory_button)

        self.setLayout(vbox)

        self.is_complete = False

    def nextId(self):
        return 3

    def isComplete(self):
        return self.project_name.text() != "" and self.directory_path.text() != ""

    def choose_directory(self):
        project_dir = QtGui.QFileDialog.getExistingDirectory(self, "Choose A Directory To Create The Project In", QtCore.QDir.homePath())
        self.directory_path.clear()
        self.directory_path.insert(project_dir)

    def key_down(self, _):
        if self.isComplete() != self.is_complete:
            self.completeChanged.emit()
            self.is_complete = self.isComplete()

class ExistingProjectLocation(QtGui.QWizardPage):
    def __init__(self, parent):
        QtGui.QWizardPage.__init__(self, parent)

        self.setTitle("Use An Existing Django Project")
        self.setSubTitle("Locate your existing manage.py file.")

        vbox = QtGui.QVBoxLayout(self)

        manage_layout = QtGui.QHBoxLayout()
        vbox.addLayout(manage_layout)

        manage_layout.addWidget(QtGui.QLabel("Path To manage.py:"))
        self.manage_path = QtGui.QLineEdit()
        self.manage_path.textChanged.connect(self.key_down)
        manage_layout.addWidget(self.manage_path)

        self.manage_button = QtGui.QPushButton("Choose File")
        self.manage_button.clicked.connect(self.choose_file)
        manage_layout.addWidget(self.manage_button)

        self.setLayout(vbox)

        self.is_complete = False

    def nextId(self):
        return 3

    def isComplete(self):
        return self.manage_path.text() != "" and os.path.exists(self.manage_path.text())

    def choose_file(self):
        manage_file = QtGui.QFileDialog.getOpenFileName(self, "Choose A Directory To Create The Project In", QtCore.QDir.homePath(),
            "Python Files (*.py)", "Python Files (*.py)")
        self.manage_path.clear()
        self.manage_path.insert(manage_file)

    def key_down(self, _):
        if self.isComplete() != self.is_complete:
            self.completeChanged.emit()
            self.is_complete = self.isComplete()

# If we can work out how to disable or hide the Next button on NewProjectLocation then this screen should be removed.
class FinalScreen(QtGui.QWizardPage):
    def __init__(self, parent):
        QtGui.QWizardPage.__init__(self, parent)

        self.setTitle("Your New DjangoDE Project Will Now Be Created")
