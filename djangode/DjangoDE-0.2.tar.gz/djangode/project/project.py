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

import logging
import os
import pickle

from django.core.management.commands.startproject import Command as StartProject

from url_model import UrlModel
from djangode import global_objects
from djangode.utils import Runner, RunnerStopped

from project_settings import ProjectSettings

logger = logging.getLogger("djangode.project.project")

class Project(object):
    def __init__(self, manage_file):
        self.manage_file = manage_file
        self.root_dir = os.path.dirname(self.manage_file)

        self.runner = Runner(manage_file)
        self.runner.start()

        self.current_debug_line = None

        try:
            self.settings = ProjectSettings(open(self.root_dir + os.sep + ".djangode.conf", "rb"))
        except IOError:
            self.settings = ProjectSettings()

    def __del__(self):
        self.close()

    def close(self):
        self.runner.stop()

        if self.settings.dirty:
            self.settings.save_to_file(open(self.root_dir + os.sep + ".djangode.conf", "wb"))

    def add_new_app(self, name):
        os.system(self.manage_file + " startapp " + name)

    def get_urls_model(self):
        try:
            return UrlModel(self.runner.send_message("get_urls"))
        except RunnerStopped, e:
            logger.error("Failed to get urls.")
            return UrlModel()

    def get_settings_names(self):
        try:
            return self.runner.send_message("get_settings_names")
        except RunnerStopped, e:
            logger.error("Failed to get settings.")
            return []

    def get_setting_value(self, setting_name):
        try:
            resp = self.runner.send_message("get_setting_value", setting_name)
        except RunnerStopped, e:
            logger.error("Failed to get setting %s." % (setting_name, ))
            return None
        else:
            if resp is None:
                return None
            else:
                return pickle.loads(resp)

    def get_pythonpath(self):
        try:
            return self.runner.send_message("get_pythonpath")
        except RunnerStopped, e:
            logger.error("Failed to get pythonpath.")
            return []        

    def module_contents(self, module_name):
        try:
            resp = self.runner.send_message("module_contents", module_name)
        except RunnerStopped, e:
            logger.error("Failed to get module contents %s." % (module_name, ))
            return None
        else:
            if resp is None:
                return None
            else:
                return pickle.loads(resp)

    def module_file(self, module_name):
        try:
            return self.runner.send_message("module_file", module_name)
        except RunnerStopped, e:
            logger.error("Failed to get module file %s." % (module_name, ))
            return None

    def debug(self, filename, line, local_vars):
        global_objects.window.debug_bar.update_data([(filename, line)], local_vars)
        global_objects.window.debug_bar.set_visibility.emit(True)

        global_objects.window.editor.open_file[(str, int)].emit(filename, line)
        global_objects.window.editor.set_debug_line.emit(filename, line)

        global_objects.window.actions["debug_play"].setEnabled(True)

    def debug_play(self):
        global_objects.window.actions["debug_play"].setEnabled(False)
        global_objects.window.debug_bar.set_visibility.emit(False)

        for filename in global_objects.window.editor.open_files.keys():
            global_objects.window.editor.set_debug_line.emit(filename, 0)

        self.runner.send_message("continue_running")

    def set_breakpoints(self):
        breakpoints = []
        for filename, tab_index in global_objects.window.editor.open_files.items():
            editor = global_objects.window.editor.widget(tab_index)

            for break_line in editor.breakpoints:
                breakpoints.append((filename, break_line))

        self.runner.send_message("set_breakpoints", breakpoints)

    @property
    def base_path(self):
        return os.path.dirname(self.manage_file)

    @staticmethod
    def new_django_project(directory_path, project_name):
        os.chdir(directory_path)

        StartProject().handle_label(project_name)

        if not os.path.exists(directory_path + os.sep + project_name + os.sep + "manage.py"):
            raise ValueError, "Failed to create the new project."

        return Project(directory_path + os.sep + project_name + os.sep + "manage.py")
