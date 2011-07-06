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
import contextlib

import mockfs

from lava_dev_tool.ci import CI


class CIHelper(object):

    def __init__(self):
        self.fs = mockfs.MockedFileSystem()
        with self.fs.record():
            os.mkdir(".lava-dev-tool")
            os.mkdir("project")
            os.mkdir("project/components")

    def mock_typical_component(self):
        self.make_mocked_component(
            "comp",
            """
            {
                "info": {
                    "methods": "no-op"
                },
                "trunk": {
                    "vcs": "bzr",
                    "url": "lp:dummy"
                }
            }
            """)

    def mock_typical_project(self):
        self.make_mocked_project(
            """
            {
                "name": "project name",
                "mainline": {
                    "components": [
                        "comp"
                    ]
                }
            }
            """)


    def make_mocked_component(self, name, text):
        with self.fs.record():
            with open("project/components/{0}.json".format(name), "wt") as stream:
                stream.write(text)

    def make_mocked_project(self, text):
        with self.fs.record():
            with open("project/project.json", "wt") as stream:
                stream.write(text)

    @contextlib.contextmanager
    def mocked_ci(self):
        with self.fs.replay():
            yield CI("")
