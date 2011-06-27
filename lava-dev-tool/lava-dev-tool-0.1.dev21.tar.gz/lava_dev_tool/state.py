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

    @property
    def state(self):
        return self.document

    @property
    def ci(self):
        return self.state.ci


class StateComponent(StateFragment):

    @DocumentBridge.readwrite
    def focus(self):
        pass

    @DocumentBridge.readwrite
    def working_dir(self):
        pass

    @DocumentBridge.fragment
    def branches(self):
        pass

    @DocumentBridge.fragment
    def action_outcome(self):
        pass


class StateComponentAction(StateFragment):
    
    @DocumentBridge.fragment
    def build(self):
        pass

    @DocumentBridge.fragment
    def install(self):
        pass

    @DocumentBridge.fragment
    def test(self):
        pass


class StateComponentActionOutcome(StateFragment):

    @DocumentBridge.readwrite
    def is_successful(self):
        pass

    @DocumentBridge.readwrite
    def trunk_revision_id(self):
        pass

    def mark_as_bad(self, component):
        self._touch(component)
        self.is_successful = False

    def mark_as_good(self, component):
        self._touch(component)
        self.is_successful = True

    def _touch(self, component):
        focus = component.state.focus
        if focus == "branch":
            self.trunk_revision_id = component.trunk.internal_checkout_revision_id
        elif focus == "tarball":
            self.trunk_revision_id = None
        elif focus == "hack":
            self.trunk_revision_id = component.trunk.checkout_revision_id


class StateComponentBranch(StateFragment):

    @DocumentBridge.readwrite
    def last_update_revision_id(self):
        pass

    @DocumentBridge.readwrite
    def last_update_branch_url(self):
        pass


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
                                        "type": "string",
                                        "optional": True,
                                        "default": None
                                    }}}},
                        "focus": {
                            "type": "string",
                            "optional": True,
                            "default": None,
                            "enum": ["branch", "tarball", "hack"]
                        },
                        "working_dir": {
                            "type": "string",
                            "optional": True,
                            "default": None
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
                                    },
                                    "trunk_revision_id": {
                                        "type": ["null", "string"],
                                        "optional": True,
                                        "default": None
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    }


    def __init__(self, ci, pathname):
        super(State, self).__init__(pathname)
        self.ci = ci

    @DocumentBridge.fragment
    def components(self):
        pass
