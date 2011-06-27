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


# TODO: Roll this into CI, it makes no sense standalone anymore

class Pathnames(object):
    """
    Helper class to calculate various (numerous) pathnames used by lava-dev-tool
    """

    STATE_DIR = ".lava-dev-tool"

    def __init__(self, workspace_dir):
        self._workspace_dir = workspace_dir

    @property
    def workspace_dir(self):
        """
        Workspace directory is the place where STATE_DIR is located
        """
        return self._workspace_dir

    @property
    def component_dir(self):
        """
        Component directory is where component definition files are located
        """
        return os.path.join(self._workspace_dir, "project", "components")

    @property
    def code_dir(self):
        """
        Code directory is where per-project-per-branch source checkouts are
        located
        """
        return os.path.join(self._workspace_dir, "code")

    @property
    def branches_dir(self):
        """
        Private directory with downloaded branches.
        """
        return os.path.join(self._workspace_dir, self.STATE_DIR, "branches")

    @property
    def tarballs_dir(self):
        """
        Private directory with downloaded tarballs
        """
        return os.path.join(self._workspace_dir, self.STATE_DIR, "tarballs")

    @property
    def localenv_dir(self):
        """
        Local environment root directory.

        This is where we put virtualenv in for example
        """
        return os.path.join(self._workspace_dir, self.STATE_DIR, "localenv")

    @property
    def localenv_python(self):
        """
        Pathname of the localenv python interpreter
        """
        return os.path.join(self.localenv_dir, "bin", "python")

    @property
    def localenv_pip(self):
        """
        Pathname of the localenv pip script
        """
        return os.path.join(self.localenv_dir, "bin", "pip")

    @property
    def project_file(self):
        """
        Project configuration file
        """
        return os.path.join(self._workspace_dir, "project", "project.json")

    @property
    def state_file(self):
        """
        Local project state file.
        """
        return os.path.join(self._workspace_dir, self.STATE_DIR, "state.json")
