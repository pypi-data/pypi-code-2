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

from lava_dev_tool.document import (
    Document,
    DocumentBridge,
    DocumentFragment,
)


class ProjectFragment(DocumentFragment):
    """
    Like DocumentFragment but with helper to reach ci instance
    """

    @property
    def ci(self):
        return self.document.ci


class ProjectDevelopmentLine(ProjectFragment):
    """
    Project development line is a named collection of components
    """

    def __str__(self):
        return self.name

    @property
    def name(self):
        return self.item

    @DocumentBridge.fragment
    def components(self):
        """
        Array of component references
        """


class ComponentReference(ProjectFragment):
    """
    Reference to a component
    """

    @property
    def name(self):
        return self.value

    def __str__(self):
        return self.name

    def dereference(self):
        return self.ci.get_component(self.name)


class Project(Document):
    """
    Project document.
    """

    document_schema = {
        "type": "object",
        "properties": {
            "name": {
                "type": "string",
                "optional": True,
            },
            "mainline": {
                "type": "object",
                "__fragment_cls": ProjectDevelopmentLine,
                "default": {},
                "optional": True,
                "properties": {
                    "components": {
                        "type": "array",
                        "items": {
                            "type": "string",
                            "__fragment_cls": ComponentReference}}}}}}

    def __init__(self, ci, pathname):
        super(Project, self).__init__(pathname)
        self.ci = ci

    @DocumentBridge.readonly
    def name(self):
        """
        Project name
        """

    @DocumentBridge.fragment
    def mainline(self):
        """
        The main development line of the project
        """

    def check(self):
        for component_ref in self.mainline.components:
            component_ref.dereference()
