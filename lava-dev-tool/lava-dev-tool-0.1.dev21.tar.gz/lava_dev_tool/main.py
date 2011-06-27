# Copyright (C) 2010, 2011 Linaro Limited
#
# Author: Zygmunt Krynicki <zygmunt.krynicki@linaro.org>
# Author: Michael Hudson-Doyle <michael.hudson@linaro.org>
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

from lava_tool.dispatcher import LavaDispatcher, run_with_dispatcher_class


class LavaDevToolDispatcher(LavaDispatcher):

    toolname = 'lava_dev_tool'
    description = """
    LAVA development tool
    """
    epilog = """
    Please report all bugs using the Launchpad bug tracker:
    http://bugs.launchpad.net/lava-dev-tool/+filebug
    """


def main():
    run_with_dispatcher_class(LavaDevToolDispatcher)
