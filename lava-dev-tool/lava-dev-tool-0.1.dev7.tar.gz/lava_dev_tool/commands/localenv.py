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

from lava_dev_tool.commands import Command


class localenv(Command):
    """
    (Re)create local development environment.
    """

    @classmethod
    def register_arguments(cls, parser):
        super(localenv, cls).register_arguments(parser)
        parser.add_argument("--wipe",
                            help="Wipe existing environment",
                            action="store_true",
                            default=False)

    def invoke_ci(self):
        if self.args.wipe:
            self.actions.wipe_localenv()
        else:
            self.actions.enable_localenv()
