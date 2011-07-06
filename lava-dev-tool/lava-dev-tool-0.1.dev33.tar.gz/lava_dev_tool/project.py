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

from lava_dev_tool.document import (
    Document,
    DocumentBridge,
    DocumentFragment,
)
from lava_dev_tool.errors import WrongState
from lava_dev_tool.utils import mkdir_p


class ProjectFragment(DocumentFragment):
    """
    Like DocumentFragment but with helper to reach ci instance
    """

    @property
    def ci(self):
        return self.document.ci


class ProjectDevelopmentLine(ProjectFragment):
    """
    Project development line is a named collection of components
    """

    def __str__(self):
        return self.name

    @property
    def name(self):
        return self.item

    @DocumentBridge.fragment
    def localenv(self):
        pass

    @DocumentBridge.fragment
    def components(self):
        pass


class LocalEnvironment(ProjectFragment):

    @property
    def localenv_exists(self):
        return os.path.exists(self.ci.pathnames.localenv_dir)

    def reset_state(self):
        for comp_state in self.ci.state.components:
            comp_state.action_outcome.revert_to_default()

    @property
    def create_virtualenv_command(self):
        cmd = ["virtualenv"]
        if self.python:
            cmd.append("--python={0}".format(self.python))
        if self.no_site_packages:
            cmd.append("--no-site-packages")
        #cmd.append("--prompt=lava-dev-tool[{0}] ".format(self.document.name)
        cmd.append(self.ci.pathnames.localenv_dir)
        return cmd

    @property
    def start_interactive_shell_command(self):
        return [
            "bash",
            "--init-file",
            "{0}/bin/activate".format(
                self.ci.pathnames.localenv_dir)]

    @DocumentBridge.readonly
    def python(self):
        """
        Python interpreter to use
        """

    @DocumentBridge.readonly
    def no_site_packages(self):
        """
        Restrict access to packages installed in the host system
        """


class ComponentReference(ProjectFragment):
    """
    Reference to a component
    """

    @property
    def name(self):
        return self.value

    def __str__(self):
        return self.name

    def dereference(self):
        return self.ci.get_component(self.name)


class Project(Document):
    """
    Project document.
    """

    document_schema = {
        "type": "object",
        "properties": {
            "name": {
                "type": "string",
                "default": "(edit project.json to specify a name)",
                "optional": True,
            },
            "mainline": {
                "type": "object",
                "__fragment_cls": ProjectDevelopmentLine,
                "default": {},
                "optional": True,
                "properties": {
                    "localenv": {
                        "__fragment_cls": LocalEnvironment,
                        "type": "object",
                        "default": {},
                        "optional": True,
                        "properties": {
                            "python": {
                                "type": "string",
                                "default": None,
                                "optional": True,
                            },
                            "no_site_packages": {
                                "type": "bool",
                                "default": True,
                                "optional": True,
                            }
                        }
                    },
                    "components": {
                        "type": "array",
                        "default": [],
                        "items": {
                            "type": "string",
                            "__fragment_cls": ComponentReference
                        }
                    }
                }
            }
        }
    }

    def __init__(self, ci, pathname):
        super(Project, self).__init__(pathname)
        self.ci = ci

    @DocumentBridge.readonly
    def name(self):
        """
        Project name
        """

    @DocumentBridge.fragment
    def mainline(self):
        """
        The main development line of the project
        """

    def check(self):
        for component_ref in self.mainline.components:
            component_ref.dereference()
