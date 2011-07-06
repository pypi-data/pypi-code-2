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
        self.helper.mock_typical_component()
        with self.helper.mocked_ci() as ci:
            comp = ci.get_component("comp")
            self.assertEqual(comp.name, "comp")

    def test_component_acessing_info_works(self):
        self.helper.mock_typical_component()
        with self.helper.mocked_ci() as ci:
            comp = ci.get_component("comp")
            self.assertIsInstance(comp.info, ComponentInfo)

    def test_component_acessing_branches_works(self):
        self.helper.mock_typical_component()
        with self.helper.mocked_ci() as ci:
            comp = ci.get_component("comp")
            self.assertIsInstance(comp.trunk, ComponentBranch)
            self.assertEqual(comp.trunk.vcs, "bzr")
            self.assertEqual(comp.trunk.url, "lp:dummy")
