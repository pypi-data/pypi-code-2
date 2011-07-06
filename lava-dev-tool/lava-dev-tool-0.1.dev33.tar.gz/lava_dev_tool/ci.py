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

import errno
import os

from lava_dev_tool.component import Component
from lava_dev_tool.errors import ImproperlyConfigured
from lava_dev_tool.pathnames import Pathnames
from lava_dev_tool.project import Project
from lava_dev_tool.state import State
from lava_dev_tool.utils import mkdir_p


class CI(object):
    """
    Class representing the global lava-dev-tool state
    """
    def __init__(self, workspace_dir=None):
        if workspace_dir is None:
            workspace_dir = os.getenv("LAVA_CI_PRJ")
        if workspace_dir is None:
            workspace_dir = os.getcwd()
            while workspace_dir != "/":
                if os.path.exists(os.path.join(workspace_dir, Pathnames.STATE_DIR)):
                    break
                workspace_dir = os.path.normpath(os.path.join(workspace_dir, ".."))
        if not os.path.exists(os.path.join(workspace_dir, Pathnames.STATE_DIR)):
            raise ImproperlyConfigured((
                "Unable to find {0} anywhere,"
                " please initialize the project"
                " first").format(Pathnames.STATE_DIR))
        self.pathnames = Pathnames(workspace_dir)
        self.project = self._load_project()
        self.state = self._load_state()
        self.localenv = self.project.mainline.localenv
        self.components = {}

    @classmethod
    def create(cls, workspace_dir):
        pathnames = Pathnames(workspace_dir)
        if os.path.exists(pathnames.state_dir):
            raise ValueError("Selected directory already contains the lava-dev-tool state directory")
        mkdir_p(pathnames.state_dir)
        return cls(workspace_dir)

    def _load_component(self, name):
        pathname = os.path.join(self.pathnames.component_dir, name + ".json")
        if not os.path.exists(pathname):
            raise ImproperlyConfigured(
                "Component {0} does not exist".format(name))
        comp = Component(self, pathname)
        comp.load()
        return comp

    def get_component(self, name):
        if name not in self.components:
            self.components[name] = self._load_component(name)
        return self.components[name]

    def _load_project(self):
        prj = Project(self, self.pathnames.project_file)
        prj.load(ignore_missing=True)
        return prj

    def _load_state(self):
        state = State(self, self.pathnames.state_file)
        state.load(ignore_missing=True)
        return state

    def save_state(self):
        self.state.save()
