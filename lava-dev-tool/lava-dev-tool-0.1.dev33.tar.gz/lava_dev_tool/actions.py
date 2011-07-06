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
import shutil
import subprocess

from lava_dev_tool.ui import ANSI
from lava_dev_tool.extcmd import (
    ExternalCommand,
    ExternalCommandWithDelegate)


class Actions(object):
    """
    Actions represent things that commands can do.

    A command is an action with exposed user interface.
    """

    def __init__(self, ci, ui, dry_run):
        self.ui = ui
        self.ci = ci
        self.dry_run = dry_run

    def update_branch(self, branch, no_pull=False):
        if self.dry_run:
            self.ui.say("- would update branch {0} from {1}", branch,
                        branch.url)
        elif branch.internal_checkout_exists and no_pull is True:
            self.ui.say("- skipping existing branch {0}", branch)
        else:
            self.ui.say("- updating branch {0} from {1}", branch, branch.url)
            new_history = branch.update_internal_checkout()
            if len(new_history):
                self.ui.say("- got {0:d} new revisions", len(new_history))
                self.ui.say("- now at revision {0}",
                            branch.state.last_update_revision_id)
            else:
                self.ui.say("- no new revisions")
        return True

    def update_tarball(self, tarball):
        did = False
        if not tarball.is_downloaded:
            if self.dry_run:
                self.ui.say("- would download tarball {0} from {1}", tarball,
                            tarball.url)
            else:
                self.ui.say("- downloading tarball {0} from {1}", tarball,
                            tarball.url)
                tarball.download()
            did |= True
        if not tarball.is_unpacked:
            if self.dry_run:
                self.ui.say("- would unpack {0}", tarball)
            else:
                self.ui.say("- unpacking {0}", tarball)
                tarball.unpack()
            did |= True
        return did

    def update_component(self, component, no_pull=False):
        did = False
        with self.ui.section("> updating component {0}:", component):
            if component.trunk and (
                not component.trunk.internal_checkout_exists or no_pull is False):
                did |= self.update_branch(component.trunk)
            if component.tarball:
                did |= self.update_tarball(component.tarball)
            if component.state.working_dir is None:
                component.autofocus()
            if not did:
                self.ui.say("- nothing to do")
        return did

    def build_component(self, component):
        with self.ui.section("> building component {0}:", component):
            if not component.working_dir_exists:
                did |= self.update_component(component)
            if component.needs_building:
                if not self.dry_run:
                    component.build(self)
            else:
                self.ui.say("- already built")

    def clean_component(self, component):
        with self.ui.section("> cleaning component {0}:", component):
            if not component.working_dir_exists:
                self.ui.say("- no working directory")
                return
            if not self.dry_run:
                component.clean(self)

    def install_component(self, component):
        with self.ui.section("> installing component {0}:", component):
            if not component.working_dir_exists:
                did |= self.update_component(component)
            if component.needs_building:
                self.build_component(component)
            if component.needs_install:
                if not self.dry_run:
                    component.install(self)
            else:
                self.ui.say("- already installed")

    def uninstall_component(self, component):
        with self.ui.section("> uninstalling component {0}:", component):
            if not component.working_dir_exists:
                self.ui.say("- no working directory")
                return
            if component.is_installed:
                if not self.dry_run:
                    component.uninstall(self)
            else:
                self.ui.say("- not installed")

    def test_component(self, component):
        with self.ui.section("> testing component {0}:", component):
            if not component.working_dir_exists:
                self.update_component(component)
            if not component.supports_testing:
                self.ui.say("- not supported")
            else:
                if component.needs_building:
                    self.build_component(component)
                if not self.dry_run:
                    component.test(self)

    def hack_component(self, component):
        with self.ui.section("> hack branch of {0}", component):
            if not component.trunk:
                self.ui.say("- no trunk to hack on")
                return
            if component.state.focus == "hack":
                self.ui.say("- already hacking trunk")
                return
            #if component.trunk.checkout_exists:
            #    self.ui.say("- cannot hack with existing checkout in the way")
            #    return
            if not component.trunk.internal_checkout_exists:
                self.update_component(component)
            self.ui.say("- hacking in {0}", component.trunk.checkout_dir)
            component.focus_on_hacking()

    def track_component(self, component):
        with self.ui.section("> track branch of {0}", component):
            if not component.trunk:
                self.ui.say("- no trunk to track")
                return True
            if component.state.focus == "branch":
                #self.ui.say("- already tracking trunk")
                return
            self.ui.say("- tracking {0}", component.trunk.url)
            component.focus_on_branch()
            return True

    def focus_component_on_branch(self, component):
        with self.ui.section("> focusing on branch of {0}", component):
            from lava_dev_tool.errors import ImproperlyConfigured, WrongState
            try:
                component.focus_on_branch()
            except (ImproperlyConfigured, WrongState) as ex:
                self.ui.say("- {0}", str(ex))

    def focus_component_on_tarball(self, component):
        with self.ui.section("> focusing on tarball of {on}{comp}{off}",
                             on=ANSI.sequence(ANSI.cmd_fg + ANSI.magenta, ANSI.cmd_bright),
                             comp=component.name,
                             off=ANSI.sequence(ANSI.cmd_fg + ANSI.default, ANSI.cmd_not_bright)):
            from lava_dev_tool.errors import ImproperlyConfigured, WrongState
            try:
                component.focus_on_tarball()
            except (ImproperlyConfigured, WrongState) as ex:
                self.ui.say("- {on}{err}{off}", 
                            on=ANSI.sequence(ANSI.cmd_fg + ANSI.red),
                            err=str(ex),
                            off=ANSI.sequence(ANSI.cmd_fg + ANSI.default))

    def show_component_release_info(self, component):
        for release in component.releases:
            with self.ui.section("> release {0}:", release):
                with self.ui.section("- recipe:"):
                    for line in release.recipe.splitlines():
                        self.ui.say("{0}", line)
        if not component.releases:
            self.ui.say("- has no releases")

    def show_component_branch_info(self, component):
        branch = component.trunk
        if not branch:
            self.ui.say("- has no branch")
            return
        with self.ui.section("> branch {0}", branch):
            self.ui.say("- available at {0}", branch.url)
            if not branch.internal_checkout_exists:
                self.ui.say("- no internal checkout")
            else:
                with self.ui.section("> internal checkout:"):
                    self.ui.say("- from {0}",
                                branch.state.last_update_branch_url)
                    self.ui.say("- at revision {0}",
                                branch.state.last_update_revision_id)

    def show_component_tarball_info(self, component):
        tarball = component.tarball
        if not tarball:
            self.ui.say("- has no tarball")
            return
        with self.ui.section("> tarball {0}:", tarball):
            self.ui.say("- available at {0}", tarball.url)
            self.ui.say("- {0}downloaded",
                        "" if tarball.is_downloaded else "not ")
            self.ui.say("- {0}unpacked",
                        "" if tarball.is_unpacked else "not ")

    def show_component_info(self, component):
        with self.ui.section("> component {0}:", component):
            self.ui.say("- is {0}installed",
                        "" if component.state.action_outcome.install.is_successful else "not ")
            self.show_component_branch_info(component)
            self.show_component_tarball_info(component)
            #self.show_component_release_info(component)

    def show_project_info(self, project):
        self.ui.say("project {0}", project.name)
        with self.ui.section("> mainline components:"):
            for component_ref in project.mainline.components:
                component = component_ref.dereference()
                self.show_component_info(component)

    def wipe_localenv(self):
        with self.ui.section("> wiping local environment"):
            self.wipe_directory(self.ci.pathnames.localenv_dir)
            self.ui.say("- resetting recorded install state")
            if not self.dry_run:
                self.ci.localenv.reset_state()

    def enable_localenv(self):
        if not self.ci.localenv.localenv_exists:
            self.ui.say("- enabling local environment")
            self.run_command(self.ci.localenv.create_virtualenv_command)

    def start_localenv_shell(self):
        self.enable_localenv()
        self.ui.say("- starting shell in the local environment")
        self.run_command(
            self.ci.localenv.start_interactive_shell_command,
            interactive=True)
        self.ui.say("- interactive shell finished")

    def run_checked_command(self, args, cwd=None, interactive=False):
        with self.ui.section("> running an external command"):
            if cwd is not None:
                self.ui.say("- in directory {0}", cwd)
            self.ui.say("- command: {0}", " ".join(args))
            if self.dry_run:
                self.ui.say("- (not actually invoked)")
                return
            try:
                if interactive:
                    ExternalCommand().run_checked(args=args, cwd=cwd)
                else:
                    ExternalCommandWithDelegate(self.ui).run_checked(args=args, cwd=cwd)
            except subprocess.CalledProcessError as ex:
                self.ui.say("- failed with return code {0}", ex.returncode)
                raise

    def run_command(self, args, cwd=None, interactive=False):
        try:
            self.run_checked_command(args, cwd, interactive)
        except subprocess.CalledProcessError as ex:
            pass

    def wipe_directory(self, path):
        self.ui.say("- wiping directory {0}", path)
        if not self.dry_run:
            if os.path.exists(path):
                shutil.rmtree(path)
