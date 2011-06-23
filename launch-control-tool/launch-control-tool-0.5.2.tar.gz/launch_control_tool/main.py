# Copyright (C) 2011  Linaro Limited
#
# Author: Zygmunt Krynicki <zygmunt.krynicki@linaro.org>
# Author: Michael Hudson-Doyle <michael.hudson@linaro.org>
#
# This file is part of launch-control-tool.
#
# launch-control-tool is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License version 3
# as published by the Free Software Foundation
#
# launch-control-tool is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with launch-control-tool.  If not, see <http://www.gnu.org/licenses/>.


from lava_tool.dispatcher import LavaDispatcher, run_with_dispatcher_class


class LaunchControlDispatcher(LavaDispatcher):

    toolname = 'launch_control_tool'
    description = """
    Command line tool for interacting with Launch Control
    """
    epilog = """
    Please report all bugs using the Launchpad bug tracker:
    http://bugs.launchpad.net/launch-control-tool/+filebug
    """


def main():
    run_with_dispatcher_class(LaunchControlDispatcher)
