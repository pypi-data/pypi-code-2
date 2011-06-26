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
from lava_dev_tool.localenv import LocalEnvironment


class CI(object):
    """
    Class representing the global lava-dev-tool state
    """
    def __init__(self, root=None):
        if root is None:
            root = os.getenv("LAVA_CI_PRJ")
        if root is None:
            root = os.getcwd()
            while root != "/":
                if os.path.exists(os.path.join(root, Pathnames.STATE_DIR)):
                    break
                root = os.path.normpath(os.path.join(root, ".."))
        if not os.path.exists(os.path.join(root, Pathnames.STATE_DIR)):
            raise ImproperlyConfigured((
                "Unable to find {0} anywhere,"
                " please initialize the project"
                " first").format(Pathnames.STATE_DIR))
        self.pathnames = Pathnames(root)
        self.project = self._load_project()
        self.state = self._load_state()
        self.localenv = self._load_local_env()

    def _find_components(self):
        try:
            for name in os.listdir(self.pathnames.component_dir):
                pathname = os.path.join(self.pathnames.component_dir, name)
                if os.path.isfile(pathname) and pathname.endswith(".json"):
                    yield pathname
        except OSError as ex:
            if ex.errno == errno.ENOENT:
                raise ImproperlyConfigured(
                    "You need to create 'components' directory in your project"
                    " branch")
            else:
                raise

    def get_component(self, name):
        pathname = os.path.join(self.pathnames.component_dir, name + ".json")
        if not os.path.exists(pathname):
            raise ImproperlyConfigured(
                "Component {0} does not exist".format(name))
        comp = Component(self, pathname)
        comp.load()
        return comp

    def _load_project(self):
        prj = Project(self, self.pathnames.project_file)
        prj.load(ignore_missing=True)
        return prj

    def _load_state(self):
        state = State(self, self.pathnames.state_file)
        state.load(ignore_missing=True)
        return state

    def _load_local_env(self):
        return LocalEnvironment(self)

    def save_state(self):
        self.state.save()
