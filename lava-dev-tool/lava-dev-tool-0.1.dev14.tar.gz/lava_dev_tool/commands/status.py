
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


class attic:
    def _component_release_info(self, component):
        for release in component.releases:
            with self.ui.section("* release {0}", release):
                with self.ui.section(" + recipe"):
                    for line in release.recipe.splitlines():
                        self.ui.say("{0}", line)

    def _component_branch_info(self, component):
        for branch in component.branches:
            with self.ui.section("* branch {0} from {1}", branch, branch.url):
                self.ui.say("{0}checkout available",
                            "" if branch.checkout_exists else "no ")

    def _component_tarball_info(self, component):
        for tarball in component.tarballs:
            with self.ui.section(
                "* tarball {0} from {1}",
                tarball, tarball.url):
                self.ui.say("{0}downloaded",
                            "" if tarball.is_downloaded else "not ")
                self.ui.say("{0}unpacked",
                            "" if tarball.is_unpacked else "not ")

    def _component_info(self, component):
        self.ui.say("* {0}", component)
        with self.ui.indent():
            self._component_branch_info(component)
            self._component_tarball_info(component)
            self._component_release_info(component)

    def _get_data_set(self):
        for component in sorted(self.get_affected_components(), key=lambda component: component.name):
            mode = component.info.mode
            patches = None
            if mode == 'development':
                if component.info.primary_branch.checkout_exists:
                    helper = component.info.primary_branch.get_vcs_helper()
                    if helper is not None:
                        patches = helper.get_patch_delta()
                    else:
                        patches = WrongState("unsupported vcs")
                else:
                    patches = WrongState("no tree")
            else:
                patches = WrongState("wrong mode")
            yield {
                "name": component.name,
                "patches": patches, 
                "build": NotImplemented,
                "test":  NotImplemented,
                "mode": component.info.mode}
    def _format_patches(self, patches):
        if isinstance(patches, WrongState):
            return str(WrongState)
        local_extra, parent_extra = patches 
        return "{outgoing}^ v{incoming}".format(
            outgoing=len(local_extra),
            incoming=len(parent_extra))


class FancyDataSetRenderer(DataSetRenderer):

    def _render_cell(self, row, column, maxlen):
        on = ""
        off = ""
        if column == "mode" and row[column] == "HACK":
            on = ANSI.sequence(ANSI.cmd_fg + ANSI.cyan, ANSI.cmd_bright)
        elif column in ("testing", "installation") and row[column] == "failed":
            on = ANSI.sequence(ANSI.cmd_fg + ANSI.red, ANSI.cmd_bright)
        elif column in ("testing", "installation") and row[column] == "ok":
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
                "mode": component.state.mode,
                "delta": None,
                "origin": component.state.working_dir,
                "working_dir": component.state.working_dir,
                "is_downloaded": component.is_downloaded,
                "testing": component.state.action_outcome.testing.is_successful,
                "installation": component.state.action_outcome.installation.is_successful,
            }

    def _format_delta(self, delta):
        if delta is None:
            return "-"

    def _format_yes_no(self, yes_no):
        if yes_no:
            return "yes"
        else:
            return "no"

    def _format_origin(self, working_dir):
        try:
            return "{0}:{1}".format(working_dir.type, working_dir.name)
        except KeyError:
            return "-"

    def _format_working_dir(self, working_dir):
        if working_dir.pathname is not None:
            return working_dir.pathname.replace(self.ci.pathnames.workspace_dir, "...")
        else:
            return "-"

    def _format_tri_state(self, yes_no_null):
        if yes_no_null is None:
            return "-"
        elif yes_no_null:
            return "ok"
        else:
            return "failed"

    def _format_mode(self, mode):
        if mode == "track":
            return "TRACK"
        elif mode == "hack":
            return "HACK"
        else:
            raise NotImplementedError()

    def invoke_ci(self):
        renderer = FancyDataSetRenderer(
            empty="There are no components in your project mainline",
            header_separator="-",
            caption="Project status",
            separator=" | ",
            order=[
                "component",
                "mode",
                "delta",
                "origin",
                "working_dir",
                "is_downloaded",
                "testing",
                "installation",
            ],
            row_formatter={
                'mode': self._format_mode,
                'origin': self._format_origin,
                'delta': self._format_delta,
                'working_dir': self._format_working_dir,
                'installation': self._format_tri_state,
                'is_downloaded': self._format_yes_no,
                'testing': self._format_tri_state,
            },
            column_map={
                "component": "Component",
                "mode": "Mode",
                "delta": "Delta",
                "origin": "Origin",
                "working_dir": "Working Directory",
                "is_downloaded": "Downloaded?",
                "testing": "Testing",
                "installation": "Installation",
            }
        )
        data_set = self._get_data_set()
        renderer.render(data_set)
