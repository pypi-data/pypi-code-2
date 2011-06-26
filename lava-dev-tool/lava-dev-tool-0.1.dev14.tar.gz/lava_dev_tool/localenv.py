
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

from lava_dev_tool.errors import WrongState
from lava_dev_tool.utils import mkdir_p


class LocalEnvironment(object):

    def __init__(self, ci):
        self.ci = ci

    @property
    def localenv_exists(self):
        return os.path.exists(self.ci.pathnames.localenv_dir)

    def reset_state(self):
        for comp_state in self.ci.state.components:
            comp_state.action_outcome.revert_to_default()

    @property
    def create_virtualenv_command(self):
        return ["virtualenv",
                "--no-site-packages",
                self.ci.pathnames.localenv_dir]

    @property
    def start_interactive_shell_command(self):
        return [
            "bash",
            "--init-file",
            "{0}/bin/activate".format(
                self.ci.pathnames.localenv_dir)]
