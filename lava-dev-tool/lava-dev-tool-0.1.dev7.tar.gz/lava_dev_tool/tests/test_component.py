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


from unittest import TestCase

from lava_dev_tool.tests.helpers import CIHelper
from lava_dev_tool.component import (
    ComponentBranch,
    ComponentInfo,
)


class ComponentTests(TestCase):

    def setUp(self):
        super(ComponentTests, self).setUp()
        self.helper = CIHelper()

    def test_component_name(self):
        self.helper.make_mocked_component("comp", "{}")
        with self.helper.mocked_ci() as ci:
            comp = ci.get_component("comp")
            self.assertEqual(comp.name, "comp")

    def test_component_acessing_info_works(self):
        self.helper.make_mocked_component("comp", "{}")
        with self.helper.mocked_ci() as ci:
            comp = ci.get_component("comp")
            self.assertIsInstance(comp.info, ComponentInfo)
            self.assertEqual(None, comp.info.primary_tarball)
            self.assertEqual(None, comp.info.primary_branch)

    def test_component_acessing_branches_works(self):
        self.helper.make_mocked_component(
            "comp",
            """
            {
                "branches": {
                    "trunk": {
                        "vcs": "bzr",
                        "url": "lp:dummy"
                    }
                }
            }
            """)
        with self.helper.mocked_ci() as ci:
            comp = ci.get_component("comp")
            self.assertIsInstance(comp.branches["trunk"], ComponentBranch)
            self.assertEqual(comp.branches["trunk"].vcs, "bzr")
            self.assertEqual(comp.branches["trunk"].url, "lp:dummy")
