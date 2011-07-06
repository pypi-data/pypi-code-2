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

"""
Interface classes and extension points for public-facing APIs
"""

from abc import ABCMeta, abstractmethod, abstractproperty


class IBranch(object):
    """
    Abstraction of a version branch that exists as a standalone directory on
    the local filesystem.

    This is not able to cover _all_ the possible things that people refer to as
    branch. It roughly represents a Bazaar branch or Git repository and the
    master branch inside.
    """

    __metaclass__ = ABCMeta

    @abstractproperty
    def is_dirty(self):
        """
        Check if the branch has uncommitted changes that are not ignored.
        """

    @abstractproperty
    def pristinize(self):
        """
        Remove all the uncommitted changes, including all the files that are
        ignored but are present in the tree.
        
        This is equivalent to:

            bzr revert && bzr clean-tree && bzr clean-tree --ignored 
        """

    @abstractproperty
    def pathname(self):
        """
        Pathname on the local filesystem
        """

    @abstractmethod
    def get_revision_id(self):
        """
        Return the identifier of the top of the branch
        """

    @abstractmethod
    def sprout_to_pathname(self, pathname):
        """
        Create a local branch from the copy of the remote branch an its current
        state.
        
        :return Locally created Branch
        """

    @abstractmethod
    def pull_without_merge(self, remote_branch):
        """
        Pull all the revisions from remote branch if it can be done so by the
        means of git fast forward of bzr pull.

        :raises BranchHasDiverged: if the operation is not possible.
        :raises IncompatibleBranch: when other_branch is using a foreign VCS.
        """

    @abstractmethod
    def count_patches_between(self, from_revision_id, to_revision_id):
        """
        Count the number of patches between two revisions present in this
        branch. Either revision may be None, in which case it represents the
        first and last revision respectively.

        :return number of patches between the two revisions
        """

    @abstractmethod
    def count_umerged_patches(self, other_branch):
        """
        Count the number of patches that exist in this branch but not merged in
        other branch (and vice versa, this is not symmetric).

        :return tuple of integers (this_new, other_new)
        :raises IncompatibleBranch: when other_branch is using a foreign VCS.
        """


class IRemoteBranch(object):
    """
    Abstraction of a version control  branch that does not exist in the local
    file system and is beyond our control.
    """

    __metaclass__ = ABCMeta

    @abstractmethod
    def sprout_to_pathname(self, pathname):
        """
        Create a local branch from the copy of the remote branch an its current
        state.
        
        :return Locally created Branch
        """


class IVCS(object):
    """
    Abstraction of a version control system.

    Has an ability to open a branch from a pathname.
    """

    __metaclass__ = ABCMeta

    @abstractmethod
    def open(self, pathname):
        """
        Get an instance of IBranch pointing at the specified pathname.

        .. note::
            This method is a workaround for lack of abstractclassmethod. It
            belongs on the IBranch interface really.
        """

    @abstractmethod
    def open_remote(self, url):
        """
        Get an instance of IRemoteBranch pointing at the specified URL
        """


class IComponent(object):
    """
    Abstraction of a component, part of a project
    """

    __metaclass__ = ABCMeta

    @abstractproperty
    def build_command(self):
        """
        Get the command that would build the component
        """

    @abstractproperty
    def clean_command(self):
        """
        Get the command that would clean the working directory. Cleaning is
        complementary to building.
        """

    @abstractproperty
    def install_command(self):
        """
        Get the command that would install the component in the local
        environment.
        """

    @abstractproperty
    def uninstall_command(self):
        """
        Get the command that would remove the component from the local
        environment. Removal is complementary to installation.
        """

    @abstractproperty
    def test_command(self):
        """
        Get the command that would run the test suite of the component
        """

    @abstractproperty
    def develop_command(self):
        """
        Get the command that would setup this component for development
        """

    @classmethod
    def supports_testing(cls):
        """
        Check if this component supports running tests
        """
