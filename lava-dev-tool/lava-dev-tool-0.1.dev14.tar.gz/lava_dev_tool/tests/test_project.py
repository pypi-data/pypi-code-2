
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
from lava_dev_tool.component import Component
from lava_dev_tool.project import (
    Project,
    ProjectDevelopmentLine,
    ComponentReference,
)


class ProjectTests(TestCase):

    def setUp(self):
        super(ProjectTests, self).setUp()
        self.helper = CIHelper()

    def test_projet_name(self):
        self.helper.make_mocked_project(
            """
            {
            "name": "project name"
            }
            """)
        with self.helper.mocked_ci() as ci:
            self.assertEqual(ci.project.name, "project name")

    def test_projet_mainline(self):
        self.helper.make_mocked_project("{}")
        with self.helper.mocked_ci() as ci:
            self.assertIsInstance(ci.project, Project)
            self.assertIsInstance(ci.project.mainline, ProjectDevelopmentLine)

    def test_project_component_refs(self):
        self.helper.make_mocked_project(
        """
            {
                "mainline": {
                    "components": [
                        "comp"
                    ]
                }
            }
        """)
        with self.helper.mocked_ci() as ci:
            comp_ref = ci.project.mainline.components[0]
            self.assertIsInstance(comp_ref, ComponentReference)
            self.assertEqual(comp_ref.name, "comp")

    def test_project_component_deferencencing(self):
        self.helper.make_mocked_project(
        """
            {
                "mainline": {
                    "components": [
                        "comp"
                    ]
                }
            }
        """)
        self.helper.make_mocked_component("comp", "{}")
        with self.helper.mocked_ci() as ci:
            comp_ref = ci.project.mainline.components[0]
            comp = comp_ref.dereference()
            self.assertIsInstance(comp, Component)
