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

    @property
    def primary_branch(self):
        """
        Name of the primary branch, if any
        """
        value = self["primary_branch"].value
        if value is None and len(self.component.branches) == 1:
            value = list(self.component.branches)[0].name
        return value

    @property
    def primary_tarball(self):
        """
        Name of the primary tarball, if any
        """
        value = self["primary_tarball"].value
        if value is None and len(self.component.tarballs) == 1:
            value = list(self.component.tarball)[0]
        return value

    @DocumentBridge.readonly
    def methods(self):
        """
        Entry point of methods to load for interacting with this component.
        """

    def get_methods_impl(self, working_dir):
        if self.methods == "python":
            import lava_dev_tool.methods
            cls = lava_dev_tool.methods.PythonComponentMethods
        elif self.methods == "python+setuptools":
            import lava_dev_tool.methods
            cls = lava_dev_tool.methods.PythonPlusSetuptoolsComponentMethods
        else:
            # XXX: Why does pkg_resources make it so hard to load an entrypoint by name :/
            raise NotImplementedError()
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

    @property
    def name(self):
        """
        Shortcut for getting the tarball name
        """
        return self.item

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
        raise NotImplementedError

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
    def checkout_dir(self):
        """
        Path of the "public" checkout directory.
        """
        return os.path.join(
            self.ci.pathnames.code_dir,
            self.component.name,
            self.name)

    @property
    def internal_checkout_exists(self):
        return os.path.exists(self.internal_checkout_dir)

    @property
    def checkout_exists(self):
        return os.path.exists(self.checkout_dir)

    def update_internal_checkout(self):
        return self.get_branch_ops().update_internal_checkout()

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
    """
    Component is the basic element of a project.

    Component encapsulates a releasable entity (like application or library)
    contained in one source tree.

    Each component can have any number of branches. Typically one branch named
    'trunk' is where most of the work is occurring.

    Each component can have any number of releases. A release designates a
    branch (or branches) and a tag. The purpose of allowing multiple branches
    is to have special "packaging" branches that allow us to create Debian
    packages.

    Each component release can be converted into a source package.

    Each component release can be converted into a binary package.

    Each component release can be uploaded to a PPA
    """

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
                    "primary_branch": {
                        "type": "string",
                        "default": None,
                        "optional": True},
                    "primary_tarball": {
                        "type": "string",
                        "default": None,
                        "optional": True},
                    "methods": {
                        "type": "string"},
                }
            },
            "branches": {
                "type": "object",
                "optional": True,
                "default": {},
                "additionalProperties": {
                    "type": "object",
                    "__fragment_cls": ComponentBranch,
                    "additionalProperties": False,
                    "properties": {
                        "vcs": {
                            "type": "string",
                            "enum": ["bzr"]},
                        "url": {
                            "type": "string"}}}},
            "tarballs": {
                "type": "object",
                "optional": True,
                "default": {},
                "additionalProperties": {
                    "type": "object",
                    "__fragment_cls": ComponentTarball,
                    "properties": {
                        "url": {
                            "type": "string"},
                        "root_dir": {
                            "type": "string"},
                        "md5": {
                            "type": "string",
                            "optional": True}}}},
            "releases": {
                "type": "object",
                "default": {},
                "optional": True,
                "additionalProperties": {
                    "type": "object",
                    "__fragment_cls": ComponentRelease,
                    "properties": {
                        "recipe": {
                            "type": "array",
                            "items": {
                                "type": "string"}}}}}}}

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
        """
        Component information
        """

    @DocumentBridge.fragment
    def branches(self):
        """
        Component branches
        """

    @DocumentBridge.fragment
    def tarballs(self):
        """
        Component tarballs
        """

    @DocumentBridge.fragment
    def releases(self):
        """
        Component releases
        """

    @property
    def state(self):
        """
        Component state
        """
        return self.ci.state.components[self.name]

    @property
    def is_downloaded(self):
        return (
            all((branch.internal_checkout_exists for branch in self.branches))
            and all((tarball.is_downloaded for tarball in self.tarballs)))

    @property
    def working_dir(self):
        pathname = self.state.working_dir.pathname
        if pathname is None:
            return self.autoselect_working_dir()
        else:
            return pathname 

    @property
    def working_dir_exists(self):
        if self.working_dir is None:
            raise WrongState("There is no working directory specified for component {0}".format(self))
        return os.path.exists(self.working_dir)

    def hack_on_branch(self, branch):
        if branch.checkout_exists:
            raise WrongState("Component checkout already exists")
        branch.create_checkout()
        self.state.mode = "hack"
        self.state.working_dir.pathname = branch.checkout_dir
        self.state.working_dir.type = "branch"
        self.state.working_dir.name = branch.name

    def hack(self):
        if self.state.mode == "hack":
            raise WrongState("Already being hacked")
        if self.info.primary_branch is None:
            raise ImproperlyConfigured("No primary branch")
        self.hack_on_branch(
            self.branches[self.info.primary_branch])

    def track(self, ui):
        if self.state.mode == "track":
            raise WrongState("Component already tracked")
        self.state.mode = "track"
        self.autoselect_working_dir()

    def autoselect_working_dir(self):
        if self.info.primary_branch is not None:
            branch = self.branches[self.info.primary_branch]
            self.state.working_dir.pathname = branch.internal_checkout_dir
            self.state.working_dir.name = branch.name
            self.state.working_dir.type = "branch"
            return branch.internal_checkout_dir
        elif self.info.primary_tarball is not None:
            tarball = self.tarbals[self.info.primary_tarball]
            self.state.working_dir.pathname = tarball.unpacked_dir
            self.state.working_dir.name = tarball.name
            self.state.working_dir.type = "tarball"
            return tarball.unpacked_dir
        else:
            raise ImproperlyConfigured("Component {0} has neither primary branch nor primary tarball".format(self))
