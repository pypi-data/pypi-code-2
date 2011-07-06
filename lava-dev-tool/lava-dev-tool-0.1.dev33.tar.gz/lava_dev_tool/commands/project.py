
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

import re
import functools

from lava_dev_tool.ci import CI
from lava_dev_tool.commands import Command
from lava_dev_tool.errors import WrongState 
from lava_dev_tool.renderer import DataSetRenderer
from lava_dev_tool.ui import ANSI


class ANSIAwareDataSetRenderer(DataSetRenderer):
    """
    DataSetRenderer that formats text correctly when using ANSI character
    sequences for terminal formatting.
    """

    def visual_length_of(self, text):
        """
        Calculate the length of the text, skipping the escape sequences
        """
        return len(re.sub("\033\[[^m]+m", '', text))


def apply_color_map(mapping, text):
    color_or_cmd = mapping.get(text, ANSI.default)
    cmd_list = [ANSI.cmd_fg + color_or_cmd] if isinstance(color_or_cmd, str) else color_or_cmd
    return "{on}{text}{off}".format(
        on=ANSI.sequence(*cmd_list),
        text=text,
        off=ANSI.sequence(ANSI.cmd_reset))


def color_map(mapping):
    def decor(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            text = func(*args, **kwargs)
            return apply_color_map(mapping, text)
        return wrapper
    return decor


def column(name, mapping=None):
    def decor(func):
        if mapping:
            func = color_map(mapping)(func)
        func.name = name
        return func
    return decor


class status(Command):
    """
    Display information about each component in mainline
    """

    @classmethod
    def register_arguments(cls, parser):
        super(status, cls).register_arguments(parser)
        group = parser.add_mutually_exclusive_group()
        group.add_argument("-d", "--only-dependencies",
                           dest="filter",
                           default=None,
                           action="store_const",
                           const="dependency",
                           help="List only components with role=dependency")
        group.add_argument("-p","--only-products",
                           dest="filter",
                           action="store_const",
                           const="product",
                           help="List only components with role=product")
        group.add_argument("-u", "--only-unspecified",
                           dest="filter",
                           action="store_const",
                           const="unspecified",
                           help="List only components with role=unspecified")

    @column("Component")
    def component(self, component):
        return component.name

    @column("Focus", {
        "hack": ANSI.cyan,
        "branch": ANSI.magenta,
        "tarball": ANSI.black,
    })
    def focus(self, component):
        return component.state.focus

    @column("Focus target")
    def focus_target(self, component):
        return component.state.focus_target or ""

    @column("Role", {
        "unspecified": ANSI.yellow,
        "dependency": ANSI.black,
        "product": [ANSI.cmd_fg + ANSI.white, ANSI.cmd_bg + ANSI.black],
    })
    def role(self, component):
        return component.info.role

    @column("Build")
    def build(self, component):
        return self._action_outcome(component, component.state.action_outcome.build)

    @column("Test", {"unsupported": [ANSI.cmd_bg + ANSI.yellow, ANSI.cmd_bright]})
    def test(self, component):
        if not component.supports_testing:
            return "unsupported"
        return self._action_outcome(component, component.state.action_outcome.test)

    @column("Install")
    def install(self, component):
        return self._action_outcome(component, component.state.action_outcome.install)

    def _action_outcome(self, component, outcome):
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
        return text

    @column("Patches")
    def patches(self, component):
        if component.state.focus == "hack":
            from lava_dev_tool.bzr_helper import BzrHelper
            bzr = BzrHelper.get_instance()
            extra_a, extra_b = bzr.num_unmerged_between(
                component.trunk.checkout_dir,
                component.trunk.internal_checkout_dir)
            if extra_a > 0 and extra_b > 0:
                return "{0} outgoing / {1} incoming".format(extra_a, extra_b)
            if extra_a > 0:
                return "{0} outgoing".format(extra_a)
            if extra_b > 0:
                return "{0} incoming".format(extra_b)
        return "-"

    @color_map({
        "pass": ANSI.green,
        "fail": ANSI.red
    })
    def _format_tri_state(self, yes_no_null):
        if yes_no_null is None:
            return "-"
        elif yes_no_null:
            return "pass"
        else:
            return "fail"

    @color_map({
        "yes": ANSI.green,
        "no": ANSI.red
    })
    def _format_yes_no(self, yes_no):
        if yes_no:
            return "yes"
        else:
            return "no"

    @column("Offline")
    def offline(self, component):
        return self._format_yes_no(component.is_downloaded)

    def invoke_ci(self):
        columns = [
            self.component,
            self.role,
            self.focus,
            self.focus_target,
            self.patches,
            self.offline,
            self.build,
            self.test,
            self.install,
        ]
        empty = "There are no components in your project mainline"
        components = [comp_ref.dereference() for comp_ref in self.ci.project.mainline.components]
        if self.args.filter:
            # When filtering do not display the role column
            columns.remove(self.role)
            # And give a better message when nothing matches
            empty="There are no components with the specified role in your project mainline"
            components = [component for component in components if component.info.role == self.args.filter]

        renderer = ANSIAwareDataSetRenderer(
            empty=empty,
            header_separator="-",
            caption="Project status",
            separator=" | ",
            order=[column.__name__ for column in columns],
            row_formatter=dict([(column.__name__, column) for column in columns]),
            column_map=dict([(column.__name__, column.name) for column in columns])
        )
        components.sort(key=lambda component: (component.info.role, component.name))
        dataset = [
            dict([(column.__name__, component) for column in columns])
            for component in components]
        renderer.render(dataset)


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
    Build, test (if possible) and install components in a sequence
    """

    def invoke_ci(self):
        self.actions.enable_localenv()
        for component in [ref.dereference() for ref in self.ci.project.mainline.components]:
            self.actions.uninstall_component(component)
            self.actions.clean_component(component)
            self.actions.build_component(component)
            if component.supports_testing:
                self.actions.test_component(component)
            self.actions.install_component(component)


class init(Command):
    """
    Initialize the project
    """

    @classmethod
    def register_arguments(cls, parser):
        parser.add_argument(
            "workspace_dir",
            help="Use explicit state directory (instead of searching)")

    def invoke(self):
        ci = CI.create(self.args.workspace_dir)
