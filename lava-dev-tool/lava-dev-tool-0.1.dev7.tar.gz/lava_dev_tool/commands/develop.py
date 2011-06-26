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


class hack(ComponentAffectingCommand):
    """
    Switch selected components into HACK mode.

    Components that you HACK on have a checkout you can edit.
    """

    def invoke_ci(self):
        for component in self.get_affected_components():
            self.actions.hack_component(component)


class track(ComponentAffectingCommand):
    """
    Switch selected components into TRACK mode.

    Components that you TRACK have no local changes and are updated along with
    the project.
    """

    def invoke_ci(self):
        for component in self.get_affected_components():
            self.actions.track_component(component)
