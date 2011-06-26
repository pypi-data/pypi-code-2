# Copyright (C) 2010, 2011 Linaro Limited
#
# Author: Zygmunt Krynicki <zygmunt.krynicki@linaro.org>
#
# This file is part of lava-dev-tool
#
# lava-dev-tool is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License version 3
# as published by the Free Software Foundation
#
# lava-dev-tool is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with lava-dev-tool.  If not, see <http://www.gnu.org/licenses/>.

import os
from abc import ABCMeta, abstractproperty


class ComponentMethods(object):

    __metaclass__ = ABCMeta

    def __init__(self, component, working_dir):
        if working_dir is None:
            raise ValueError("working_dir cannot be None")
        self.component = component
        self.working_dir = working_dir

    @abstractproperty
    def install_command(self):
        pass

    @abstractproperty
    def uninstall_command(self):
        pass

    @abstractproperty
    def test_command(self):
        pass

    @abstractproperty
    def develop_command(self):
        pass


class PythonComponentMethods(ComponentMethods):

    @property
    def setup_py_pathname(self):
        return os.path.join(self.working_dir, "setup.py")

    @property
    def setup_py_exists(self):
        return os.path.exists(self.setup_py_pathname)

    @property
    def install_command(self):
        return [
            self.component.ci.pathnames.localenv_python,
            self.setup_py_pathname,
            "install"]

    @property
    def uninstall_command(self):
        return [
            self.component.ci.pathnames.localenv_pip,
            "uninstall",
            "-e",
            self.component.ci.pathnames.localenv_dir,
            "--yes",
            self.component.name]

    @property
    def develop_command(self):
        return None

    @property
    def test_command(self):
        return None


class PythonPlusSetuptoolsComponentMethods(PythonComponentMethods):

    @property
    def develop_command(self):
        return [
            self.component.ci.pathnames.localenv_python,
            self.setup_py_pathname,
            "develop"]

    @property
    def test_command(self):
        return [
            self.component.ci.pathnames.localenv_python,
            self.setup_py_pathname,
            "test"]
