
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

from lava_dev_tool.commands import Command
from lava_dev_tool.errors import WrongState 
from lava_dev_tool.renderer import DataSetRenderer
from lava_dev_tool.ui import ANSI


class FancyDataSetRenderer(DataSetRenderer):

    def _render_cell(self, row, column, maxlen):
        on = ""
        off = ""
        if column == "test" and row[column] == "unsupported":
            on = ANSI.sequence(ANSI.cmd_fg + ANSI.yellow, ANSI.cmd_bright)
        elif column == "focus" and row[column] == "HACK":
            on = ANSI.sequence(ANSI.cmd_fg + ANSI.cyan, ANSI.cmd_bright)
        elif column in ("build", "test", "install") and row[column] == "failed":
            on = ANSI.sequence(ANSI.cmd_fg + ANSI.red, ANSI.cmd_bright)
        elif column in ("build", "test", "install") and row[column] == "ok":
            on = ANSI.sequence(ANSI.cmd_fg + ANSI.green, ANSI.cmd_bright)
        if on != "":
            off = ANSI.sequence(ANSI.cmd_reset)
        text = super(FancyDataSetRenderer, self)._render_cell(row, column, maxlen)
        return on + text + off


class status(Command):
    """
    Display information about each component in mainline
    """

    def _get_data_set(self):
        for component in sorted(
            [comp_ref.dereference() for comp_ref in self.ci.project.mainline.components],
            key=lambda component: component.name):
            yield {
                "component": component,
                "focus": component.state.focus,
                "delta": component,
                "origin": component.state.working_dir,
                #"working_dir": component.state.working_dir,
                "is_downloaded": component.is_downloaded,
                "build": (component, component.state.action_outcome.build),
                "test": (component, component.state.action_outcome.test),
                "install": (component, component.state.action_outcome.install),
            }

    def _format_delta(self, component):
        if component.state.focus == "hack":
            from lava_dev_tool.bzr_helper import BzrHelper
            bzr = BzrHelper.get_instance()
            extra_a, extra_b = bzr.num_unmerged_between(
                component.trunk.checkout_dir,
                component.trunk.internal_checkout_dir)
            return "{0} extra / {1} missing".format(extra_a, extra_b)
        else:
            return "N/A"

    def _format_yes_no(self, yes_no):
        if yes_no:
            return "yes"
        else:
            return "no"

    def _format_focus(self, focus):
        if focus is None:
            return ""
        else:
            return focus

    def _format_working_dir(self, working_dir):
        if working_dir:
            return working_dir.replace(self.ci.pathnames.workspace_dir, "...")
        else:
            return ""

    def _format_action_outcome(self, co):
        component, outcome = co
        text = self._format_tri_state(outcome.is_successful)
        if component.state.focus in ("branch", "hack") and outcome.trunk_revision_id is not None:
            from lava_dev_tool.bzr_helper import BzrHelper
            bzr = BzrHelper.get_instance()
            num_patches = bzr.num_patches_between(
                component.state.working_dir,
                outcome.trunk_revision_id,
                component.working_dir_revision_id)
            if num_patches != 0:
                return "{0} ~{1:d}".format(text, num_patches)
        elif component.state.focus in ("branch", "hack") and outcome.trunk_revision_id is None:
            return "never"
        return text

    def _format_test_action_outcome(self, co):
        component, outcome = co
        if not component.supports_testing:
            return "unsupported"
        else:
            return self._format_action_outcome(co)

    def _format_tri_state(self, yes_no_null):
        if yes_no_null is None:
            return ""
        elif yes_no_null:
            return "ok"
        else:
            return "failed"

    def invoke_ci(self):
        renderer = FancyDataSetRenderer(
            empty="There are no components in your project mainline",
            header_separator="-",
            caption="Project status",
            separator=" | ",
            order=[
                "component",
                "focus",
                "delta",
                #"working_dir",
                "is_downloaded",
                "build",
                "test",
                "install",
            ],
            row_formatter={
                "focus": self._format_focus,
                'delta': self._format_delta,
                #'working_dir': self._format_working_dir,
                'is_downloaded': self._format_yes_no,
                'build': self._format_action_outcome,
                'test': self._format_test_action_outcome,
                'install': self._format_action_outcome,
            },
            column_map={
                "component": "Component",
                "focus": "focus",
                "delta": "Delta",
                #"working_dir": "Working Directory",
                "is_downloaded": "Downloaded?",
                "build": "Build",
                "test": "Test",
                "install": "Install",
            }
        )
        data_set = self._get_data_set()
        renderer.render(data_set)


class check(Command):
    """
    Check that project and component files from mainline are correct (syntax
    wise)
    """

    def invoke_ci(self):
        self.ci.project.check()
        self.ui.say("Project seems to be okay")


class info(Command):
    """
    Display basic information about the project
    """

    def invoke_ci(self):
        return self.actions.show_project_info(self.ci.project)


class sequence(Command):
    """
    Display basic information about the project
    """

    def invoke_ci(self):
        self.actions.enable_localenv()
        for component in [ref.dereference() for ref in self.ci.project.mainline.components]:
            self.actions.build_component(component)
            if component.supports_testing:
                self.actions.test_component(component)
            self.actions.install_component(component)
