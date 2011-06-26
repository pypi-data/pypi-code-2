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
            self.ui.say("- would update branch {0} from {1}", branch, branch.url)
        elif branch.internal_checkout_exists and no_pull is True:
            self.ui.say("- skipping existing branch {0}", branch)
        else:
            self.ui.say("- updating branch {0} from {1}", branch, branch.url)
            new_history = branch.update_internal_checkout()
            if len(new_history):
                self.ui.say("- got {0:d} new revisions", len(new_history))
                self.ui.say("- now at revision {0}", branch.state.last_update_revision_id)
            else:
                self.ui.say("- no new revisions")
        return True

    def update_tarball(self, tarball):
        did = False
        if not tarball.is_downloaded:
            if self.dry_run:
                self.ui.say("- would download tarball {0} from {1}", tarball, tarball.url)
            else:
                self.ui.say("- downloading tarball {0} from {1}", tarball, tarball.url)
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
            for tarball in component.tarballs:
                did |= self.update_tarball(tarball)
            for branch in component.branches:
                did |= self.update_branch(branch, no_pull)
            if component.working_dir is None:
                working_dir = component.autoselect_working_dir()
                self.ui.say("- selected working directory {0}", working_dir)
                did |= True
            if not did:
                self.ui.say("- nothing do do")
        return did

    def install_component(self, component):
        did = False
        with self.ui.section("> installing component {0}:", component):
            if not component.working_dir_exists:
                did |= self.update_component(component)
            if component.state.action_outcome.installation.is_successful:
                self.ui.say("- already installed")
            else:
                methods = component.info.get_methods_impl(component.working_dir)
                try:
                    self.run_command(methods.install_command, component.working_dir)
                except subprocess.CalledProcessError as ex:
                    self.ui.say("- installation failed with code {0}", ex.returncode)
                    component.state.action_outcome.installation.is_successful = False
                else:
                    component.state.action_outcome.installation.is_successful = True
                did = True
        return did

    def hack_component(self, component):
        if component.state.mode == "hack":
            self.ui.say("- already hacked in: {0}",
                        component.state.working_dir.pathname)
        elif component.info.primary_branch is None:
            self.ui.say("- cannot hack on {0} without a primary branch",
                        component.name)
        elif component.branches[component.info.primary_branch].checkout_exists:
            self.ui.say("- cannot hack on {0} with existing checkout in the way",
                        component.name)
        else:
            with self.ui.section("> hacking component {0}", component):
                component.hack()

    def track_component(self, component):
        if component.state.mode == "track":
            self.ui.say("- already tracking")
        else:
            with self.ui.section("> tracking component {0}", component):
                component.track()
                
    def test_component(self, component):
        did = False
        with self.ui.section("> testing component {0}:", component):
            if not component.working_dir_exists:
                did |= self.update_component(component)
            methods = component.info.get_methods_impl(component.working_dir)
            if methods.test_command is None:
                self.ui.say("- not supported")
            else:
                try:
                    self.ui.say("- starting test program")
                    self.run_command(methods.test_command, component.working_dir)
                except subprocess.CalledProcessError as ex:
                    self.ui.say("- testing failed")
                    component.state.action_outcome.testing.is_successful = False
                else:
                    self.ui.say("- testing succeeded")
                    component.state.action_outcome.testing.is_successful = True
            did = True
        return did

    def show_component_release_info(self, component):
        for release in component.releases:
            with self.ui.section("> release {0}:", release):
                with self.ui.section("- recipe:"):
                    for line in release.recipe.splitlines():
                        self.ui.say("{0}", line)
        if not component.releases:
            self.ui.say("- has no releases")

    def show_component_branch_info(self, component):
        for branch in component.branches:
            with self.ui.section("> branch {0}", branch):
                self.ui.say("- available at {0}", branch.url)
                if not branch.internal_checkout_exists:
                    self.ui.say("- no internal checkout")
                else:
                    with self.ui.section("- internal checkout:"):
                        self.ui.say("- from {0}",
                                    branch.state.last_update_branch_url)
                        self.ui.say("- at revision {0}",
                                    branch.state.last_update_revision_id)
        if not component.branches:
            self.ui.say("- has no branches")

    def show_component_tarball_info(self, component):
        for tarball in component.tarballs:
            with self.ui.section("> tarball {0}:", tarball):
                self.ui.say("- available at {0}", tarball.url)
                self.ui.say("- {0}downloaded",
                            "" if tarball.is_downloaded else "not ")
                self.ui.say("- {0}unpacked",
                            "" if tarball.is_unpacked else "not ")
        if not component.tarballs:
            self.ui.say("- has no branches")

    def show_component_info(self, component):
        with self.ui.section("> component {0}:", component):
            self.ui.say("- is {0}installed",
                        "" if component.state.action_outcome.installation.is_successful else "not ")
            self.show_component_branch_info(component)
            self.show_component_tarball_info(component)
            self.show_component_release_info(component)

    def show_project_info(self, project):
        self.ui.say("project {0}", project.name)
        with self.ui.section("> mainline components:"):
            for component_ref in project.mainline.components:
                component = component_ref.dereference()
                self.show_component_info(component)

    def wipe_localenv(self):
        if self.dry_run:
            self.ui.say("- would wipe local environment")
        else:
            with self.ui.section("> wiping local environment"):
                self.wipe_directory(
                    self.ci.pathnames.localenv_dir)
                self.ui.say("- resetting recorded installation state")
                self.ci.localenv.reset_state()

    def enable_localenv(self):
        if not self.ci.localenv.localenv_exists:
            if self.dry_run:
                self.ui.say("- would enable local environment")
            else:
                self.ui.say("- enabling local environment")
            self.run_command(self.ci.localenv.create_virtualenv_command)

    def start_localenv_shell(self):
        self.enable_localenv()
        self.ui.say("- starting shell in the local environment")
        if not self.dry_run:
            self.run_command(
                self.ci.localenv.start_interactive_shell_command,
                interactive=True)
        self.ui.say("- interactive shell finished")
   
    def run_command(self, args, cwd=None, interactive=False):
        with self.ui.section("- running an external command"):
            if cwd is not None:
                self.ui.say("- in directory {0}", cwd)
            self.ui.say("- command: {0}", " ".join(args))
            if not self.dry_run:
                if interactive:
                    ExternalCommand().run(args=args, cwd=cwd)
                else:
                    ExternalCommandWithDelegate(self.ui).run_checked(args=args, cwd=cwd)

    def wipe_directory(self, path):
        self.ui.say("- wiping directory {0}", path)
        if not self.dry_run:
            if os.path.exists(path):
                shutil.rmtree(path)
