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

import subprocess

import lava_tool

from lava_dev_tool.actions import Actions
from lava_dev_tool.ci import CI
from lava_dev_tool.document import DocumentError
from lava_dev_tool.errors import ImproperlyConfigured
from lava_dev_tool.ui import TextUI


class Command(lava_tool.interface.Command):
    """
    Base class for lava-dev-tool commands
    """

    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)
        self.ui = TextUI()

    @classmethod
    def register_arguments(cls, parser):
        super(Command, cls).register_arguments(parser)
        parser.add_argument(
            "-n", "--dry-run",
            default=False,
            action="store_true",
            help="Do not invoke any actions, instead show what would be done")

    def invoke(self):
        try:
            self.ci = CI()
            self.actions = Actions(
                self.ci, self.ui, self.args.dry_run)
            self.invoke_ci()
            if not self.args.dry_run:
                self.ci.save_state()
            return 0
        except (DocumentError, ImproperlyConfigured, ValueError) as ex:
            self.ui.nesting = []
            self.ui.say("Error: {0}", ex)
        except subprocess.CalledProcessError as ex:
            self.ui.nesting = []
            self.ui.say("Sub-command failed: {0}", ex)
        return 1

    # TODO: abstractmethod
    def invoke_ci(self):
        raise NotImplementedError()


class ComponentAffectingCommand(Command):
    """
    Base class for commands that act on one or more components
    """

    @classmethod
    def register_arguments(cls, parser):
        super(ComponentAffectingCommand, cls).register_arguments(parser)
        group = parser.add_mutually_exclusive_group(required=True)
        group.add_argument(
            "-a", "--all",
            default=False,
            action="store_true",
            help="Act on all components in mainline")
        group.add_argument(
            "-c", "--components",
            nargs="*",
            metavar="NAME",
            help="Act on specific components")

    def get_affected_components(self):
        if self.args.all:
            project = self.ci.project
            return [ref.dereference() for ref in project.mainline.components]
        else:
            return [self.ci.get_component(name) for name in
                    self.args.components]
