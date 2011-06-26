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

from lava_dev_tool.commands import ComponentAffectingCommand


class update(ComponentAffectingCommand):
    """
    Update selected components
    """

    @classmethod
    def register_arguments(cls, parser):
        super(update, cls).register_arguments(parser)
        parser.add_argument("--no-pull",
                            action="store_true",
                            default=False,
                            help="Do not update/pull existing branches")

    def invoke_ci(self):
        for component in self.get_affected_components():
            self.actions.update_component(component, self.args.no_pull)
