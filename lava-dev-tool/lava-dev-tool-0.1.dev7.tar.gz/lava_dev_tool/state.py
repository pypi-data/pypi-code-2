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


class StateFragment(DocumentFragment):
    """
    Like DocumentFragment but with helper to reach ci instance and component
    instance.
    """

    @property
    def state(self):
        return self.document

    @property
    def ci(self):
        return self.state.ci


class StateComponent(StateFragment):

    @DocumentBridge.readwrite
    def mode(self):
        """
        Component usage mode?
        """

    @DocumentBridge.fragment
    def branches(self):
        """
        Mapping of component branches
        """

    @DocumentBridge.fragment
    def working_dir(self):
        """
        Information about working directory
        """

    @DocumentBridge.fragment
    def action_outcome(self):
        """
        Information about outcome of attempted actions
        """


class StateComponentWorkingDir(StateFragment):

    @DocumentBridge.readwrite
    def pathname(self):
        """
        Pathname of the working directory used by this component
        """

    @DocumentBridge.readwrite
    def type(self):
        """
        Type of the working tree (branch, tarball or hack)
        """

    @DocumentBridge.readwrite
    def name(self):
        """
        Name of the object backing the working tree
        """


class StateComponentAction(StateFragment):

    @DocumentBridge.fragment
    def installation(self):
        """
        Outcome of installation 
        """

    @DocumentBridge.fragment
    def testing(self):
        """
        Outcome of testing
        """


class StateComponentActionOutcome(StateFragment):

    @DocumentBridge.readwrite
    def is_successful(self):
        """
        Tri-state for action success
        """


class StateComponentBranch(StateFragment):

    @DocumentBridge.readwrite
    def last_update_revision_id(self):
        """
        Revision ID of the last update operation
        """

    @DocumentBridge.readwrite
    def last_update_branch_url(self):
        """
        URL of the branch that was used for last update operation
        """


class State(Document):

    document_schema = {
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "components": {
                "type": "object",
                "default": {},
                "optional": True,
                "additionalProperties": {
                    "type": "object",
                    "default": {},
                    "__fragment_cls": StateComponent,
                    "properties": {
                        "branches": {
                            "type": "object",
                            "default": {},
                            "optional": True,
                            "additionalProperties": {
                                "type": "object",
                                "default": {},
                                "__fragment_cls": StateComponentBranch,
                                "properties": {
                                    "last_update_revision_id": {
                                        "type": "string",
                                        "optional": True,
                                        "default": None,
                                        "requires": "last_update_revision_id"
                                    },
                                    "last_update_branch_url": {
                                        "type":"string",
                                        "optional": True,
                                        "default": None
                                    }}}},
                        "mode": {
                            "type": "string",
                            "optional": True,
                            "default": "track",
                            "enum": ["track", "hack"]
                        },
                        "working_dir": {
                            "type": "object",
                            "default": {},
                            "optional": True,
                            "__fragment_cls": StateComponentWorkingDir,
                            "properties": {
                                "type": {
                                    "type": "string",
                                    "enum": ["branch", "tarball", "hack"]
                                },
                                "name": {
                                    "type": "string"
                                },
                                "pathname": {
                                    "type": "string",
                                    "default": None
                                }
                            }
                        },
                        "action_outcome": {
                            "type": "object",
                            "default": {},
                            "optional": True,
                            "__fragment_cls": StateComponentAction,
                            "additionalProperties": {
                                "type": "object",
                                "default": {},
                                "__fragment_cls": StateComponentActionOutcome,
                                "optional": True,
                                "properties": {
                                    "is_successful": {
                                        "type": ["null", "boolean"],
                                        "optional": True,
                                        "default": None
                                    }
                                }
                            }
                        },
                        # TODO: Determine state properties
                    }}}}}

    def __init__(self, ci, pathname):
        super(State, self).__init__(pathname)
        self.ci = ci

    @DocumentBridge.fragment
    def components(self):
        """
        Mapping to per-component state
        """
