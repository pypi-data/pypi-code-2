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
import subprocess
import tarfile
import urllib

from lava_dev_tool.document import (
    Document,
    DocumentBridge,
    DocumentFragment,
)
from lava_dev_tool.errors import (
    ImproperlyConfigured,
    WrongState,
)
from lava_dev_tool.bzr_helper import BranchOpsBzr
from lava_dev_tool.utils import mkdir_p


__all__ = ["Component", "ComponentTarball", "ComponentBranch", "ComponentInfo"]


class ComponentFragment(DocumentFragment):
    """
    Like DocumentFragment but with helper properties to reach ci instance and
    component instance. It builds on an assumption that self.document is an
    instance of Component.
    """

    @property
    def component(self):
        """
        Shortcut for accessing the component this item belongs to
        """
        return self.document

    @property
    def ci(self):
        """
        Shortcut for accessing the CI this item belongs to
        """
        return self.component.ci


class ComponentInfo(ComponentFragment):

    @DocumentBridge.readonly
    def methods(self):
        """
        Entry point of methods to load for interacting with this component.
        """

    def get_methods_cls(self):
        import lava_dev_tool.methods
        if self.methods == "python":
            return lava_dev_tool.methods.PythonComponentMethods
        elif self.methods == "python+setuptools":
            return lava_dev_tool.methods.PythonPlusSetuptoolsComponentMethods
        else:
            # XXX: Why does pkg_resources make it so hard to load an entrypoint by name :/
            raise NotImplementedError()

    def get_methods_impl(self, working_dir):
        cls = self.get_methods_cls()
        return cls(self.component, working_dir)


class ComponentTarball(ComponentFragment):

    @DocumentBridge.readonly
    def url(self):
        """
        Shortcut for getting the tarball URL
        """

    @DocumentBridge.readonly
    def root_dir(self):
        """
        Shortcut for getting the name of the root directory inside the tarball
        """

    @DocumentBridge.readonly
    def name(self):
        """
        Shortcut for getting the tarball name
        """

    def __str__(self):
        return self.name

    @property
    def tarball_pathname(self):
        """
        Tarball pathname.

        Tarballs are stored in per-component directory, underneath the code
        directory.
        """
        return os.path.join(
            self.ci.pathnames.tarballs_dir,
            self.component.name,
            self.name)

    @property
    def is_downloaded(self):
        """
        Shortcut to check if a tarball has been downloaded.

        Note: This does not check if the tarball is valid or not.
        """
        return os.path.exists(self.tarball_pathname)

    @property
    def is_valid(self):
        """
        Shortcut to check if a tarball is valid (correct checksum, signature)
        """
        if not self.is_downloaded:
            raise WrongState("tarball not yet downloaded") 
        raise NotImplementedError()

    def download(self):
        """
        Download the tarball from the network.
        """
        parent_dir = os.path.dirname(self.tarball_pathname)
        mkdir_p(parent_dir)
        if not os.path.exists(self.tarball_pathname):
            urllib.urlretrieve(self.url, self.tarball_pathname)

    @property
    def unpacked_dir(self):
        """
        Unpacked directory.

        This is the pathname of the unpacked directory that is contained in the
        tarball.
        """
        return os.path.join(
            self.ci.pathnames.tarballs_dir,
            self.component.name,
            self.root_dir)

    @property
    def is_unpacked(self):
        """
        Shortcut to check if the tarball is unpacked
        """
        return os.path.exists(self.unpacked_dir)

    def unpack(self):
        if not self.is_downloaded:
            raise WrongState("tarball is not downloaded yet")
        if self.is_unpacked:
            raise WrongState("tarball already unpacked")
        destdir = os.path.dirname(self.tarball_pathname)
        mkdir_p(destdir)
        with tarfile.TarFile.open(self.tarball_pathname, "r:*") as tarball:
            tarball.extractall(path=destdir)
        if not self.is_unpacked:
            raise ImproperlyConfigured(
                ("It seems that tarball {0} for component {1} has wrong"
                 " root_dir").format(self, self.component))


class ComponentBranch(ComponentFragment):

    def __str__(self):
        return self.name

    @property
    def name(self):
        return self.item

    @DocumentBridge.readonly
    def url(self):
        """
        VCS-specific URL of this branch
        """

    @DocumentBridge.readonly
    def vcs(self):
        """
        VCS used by this branch
        """

    @property
    def internal_checkout_dir(self):
        """
        Path of the internal checkout directory.
        """
        return os.path.join(
            self.ci.pathnames.branches_dir,
            self.component.name,
            self.name)

    @property
    def internal_checkout_exists(self):
        return os.path.exists(self.internal_checkout_dir)

    @property
    def internal_checkout_revision_id(self):
        return self.state.last_update_revision_id

    def update_internal_checkout(self):
        return self.get_branch_ops().update_internal_checkout()

    @property
    def checkout_dir(self):
        """
        Path of the "public" checkout directory.
        """
        return os.path.join(
            self.ci.pathnames.code_dir,
            self.component.name,
            self.name)

    @property
    def checkout_exists(self):
        return os.path.exists(self.checkout_dir)

    @property
    def checkout_revision_id(self):
        return self.get_branch_ops().checkout_revision_id()
    
    def create_checkout(self):
        if not self.internal_checkout_exists:
            raise WrongState("No internal checkout available")
        return self.get_branch_ops().create_checkout()

    @property
    def state(self):
        return self.component.state.branches[self.name]

    def get_branch_ops(self):
        if self.vcs == "bzr":
            return BranchOpsBzr(self)
        elif self.vcs == "git":
            raise NotImplementedError("Git is not supported yet")
        else:
            raise ImproperlyConfigured(
                ("Unsupported VCS {0} used by branch {1} of component"
                 " {2}").format(self.vcs, self.name, self.component))


class ComponentRelease(DocumentFragment):

    def __str__(self):
        return self.version

    @property
    def version(self):
        return self.item

    @property
    def recipe(self):
        return "\n".join(self["recipe"].value)


class Component(Document):

    document_schema = {
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "info": {
                "type": "object",
                "default": {},
                "__fragment_cls": ComponentInfo,
                "optional": True,
                "additionalProperties": False,
                "properties": {
                    "methods": {
                        "type": "string"},
                }
            },
            "trunk": {
                "__fragment_cls": ComponentBranch,
                "type": "object",
                "optional": True,
                "default": {},
                "additionalProperties": False,
                "properties": {
                    "vcs": {
                        "type": "string",
                        "enum": ["bzr"]
                    },
                    "url": {
                        "type": "string"
                    }
                }
            },
            "tarball": {
                "__fragment_cls": ComponentTarball,
                "type": "object",
                "optional": True,
                "default": {},
                "additionalProperties": False,
                "properties": {
                    "url": {
                        "type": "string",
                    },
                    "root_dir": {
                        "type": "string"
                    },
                    "name": {
                        "type": "string"
                    }
                }
            }
        }
    }

    def __init__(self, ci, pathname):
        super(Component, self).__init__(pathname)
        self.ci = ci

    def __str__(self):
        return self.name

    @property
    def name(self):
        return os.path.basename(self.pathname)[:-len(".json")]

    @DocumentBridge.fragment
    def info(self):
        pass

    @DocumentBridge.fragment
    def trunk(self):
        pass

    @DocumentBridge.fragment
    def tarball(self):
        pass

    @property
    def state(self):
        return self.ci.state.components[self.name]

    @property
    def is_installed(self):
        return self.state.action_outcome.install.is_successful

    @property
    def is_built(self):
        return self.state.action_outcome.build.is_successful

    @property
    def is_downloaded(self):
        items = []
        if self.trunk:
            items.append(self.trunk.internal_checkout_exists)
        if self.tarball:
            items.append(self.tarball.is_downloaded)
        return all(items)

    @property
    def working_dir_exists(self):
        if self.state.working_dir is None:
            raise WrongState("There is no working directory specified for component {0}".format(self))
        return os.path.exists(self.state.working_dir)

    @property
    def working_dir_revision_id(self):
        if self.state.focus == "branch":
            return self.trunk.internal_checkout_revision_id
        elif self.state.focus == "tarball":
            return None
        elif self.state.focus == "hack":
            self.trunk.checkout_revision_id

    def focus_on_hacking(self):
        if self.state.focus == "hack":
            raise WrongState("Already using local branch")
        if not self.trunk:
            raise ImproperlyConfigured("No trunk to branch from")
        if self.trunk.checkout_exists:
            raise WrongState("Component checkout already exists")
        # XXX: move to action
        self.trunk.create_checkout()
        self._switch_focus("hack", self.trunk.checkout_dir)

    def focus_on_branch(self):
        if self.state.focus == "branch":
            raise WrongState("Already using upstream branch")
        if not self.trunk:
            raise ImproperlyConfigured("No trunk to track")
        self._switch_focus("branch", self.trunk.internal_checkout_dir)

    def focus_on_tarball(self):
        if self.state.focus == "tarball":
            raise WrongState("Already using tarball")
        if not self.tarball:
            raise ImproperlyConfigured("No tarball to use")
        if not self.tarball.is_unpacked:
            raise WrongState("Tarball not unpacked")
        self._switch_focus("tarball", self.tarball.unpacked_dir)

    def _switch_focus(self, focus, working_dir):
        # TODO: Yank existing installed copy from localenv
        self.state.action_outcome.build.revert_to_default()
        self.state.action_outcome.test.revert_to_default()
        self.state.focus = focus 
        self.state.working_dir = working_dir 

    def autofocus(self):
        if self.state.focus is not None:
            return
        if self.trunk:
            self.focus_on_branch()
        elif self.tarball:
            self.focus_on_tarball()
        else:
            raise ImproperlyConfigured("Component without trunk and tarball")

    @property
    def needs_install(self):
        # TODO: check if the version in working dir needs to be installed
        # Scenario:
        # - update -> version 1
        # - install -> installed version 1
        # - update -> version 2
        # - needs_install == True
        return not self.is_installed

    @property
    def needs_building(self):
        return not self.is_built

    def build(self, actions):
        """
        Build the component.

        :param actions:
            Delegate used to invoke run_command()
        """
        if not self.working_dir_exists:
            raise WrongState("no working directory")
        methods = self.info.get_methods_impl(self.state.working_dir)
        try:
            actions.run_checked_command(methods.build_command, self.state.working_dir)
        except subprocess.CalledProcessError:
            self.state.action_outcome.build.mark_as_bad(self)
        else:
            self.state.action_outcome.build.mark_as_good(self)

    def clean(self, actions):
        """
        Clean the component

        :param actions:
            Delegate used to invoke run_command()
        """
        if not self.working_dir_exists:
            raise WrongState("no working directory")
        methods = self.info.get_methods_impl(self.state.working_dir)
        try:
            actions.run_checked_command(methods.clean_command, self.state.working_dir)
        except subprocess.CalledProcessError:
            # XXX: corrupt state
            pass
        else:
            self.state.action_outcome.build.revert_to_default()

    def install(self, actions):
        """
        Install the component.

        :param actions:
            Delegate used to invoke run_command()
        """
        if not self.working_dir_exists:
            raise WrongState("no working directory")
        methods = self.info.get_methods_impl(self.state.working_dir)
        try:
            actions.run_checked_command(methods.install_command, self.state.working_dir)
        except subprocess.CalledProcessError:
            self.state.action_outcome.install.mark_as_bad(self)
        else:
            self.state.action_outcome.install.mark_as_good(self)

    def uninstall(self, actions):
        """
        Uninstall the component.

        :param actions:
            Delegate used to invoke run_command()
        """
        if not self.working_dir_exists:
            raise WrongState("no working directory")
        if not self.state.action_outcome.install.is_successful:
            raise WrongState("not installed")
        methods = self.info.get_methods_impl(self.state.working_dir)
        try:
            actions.run_checked_command(methods.uninstall_command, self.state.working_dir)
        except subprocess.CalledProcessError:
            # XXX: corrupt state
            pass
        else:
            self.state.action_outcome.install.revert_to_default()

    def test(self, actions):
        if not self.working_dir_exists:
            raise WrongState("no working directory")
        if not self.ci.localenv.localenv_exists:
            raise WrongState("no local environment")
        if not self.supports_testing:
            raise ImproperlyConfigured("testing not supported")
        methods = self.info.get_methods_impl(self.state.working_dir)
        try:
            actions.run_checked_command(methods.test_command, self.state.working_dir)
        except subprocess.CalledProcessError:
            self.state.action_outcome.test.mark_as_bad(self)
        else:
            self.state.action_outcome.test.mark_as_good(self)

    @property
    def supports_testing(self):
        cls = self.info.get_methods_cls()
        return cls.supports_testing()
