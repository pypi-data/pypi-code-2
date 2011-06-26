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

import contextlib 
import os

from bzrlib.branch import Branch
from bzrlib.commands import install_bzr_command_hooks
from bzrlib.library_state import BzrLibraryState
from bzrlib.log import get_history_change
from bzrlib.plugin import set_plugins_path
from bzrlib.trace import DefaultConfig
from bzrlib.transport import get_transport
from bzrlib.ui import SilentUIFactory
from bzrlib.workingtree import WorkingTree

from lava_dev_tool.utils import mkdir_p


class BzrHelper(object):

    _instance = None

    def __init__(self):
        # Work around a bug in bzrlib.initialize(setup_ui=False)
        self._bzr_state = BzrLibraryState(
            ui=SilentUIFactory(),
            trace=DefaultConfig())
        self._bzr_state._start()
        # suggested by lifeless
        install_bzr_command_hooks()
        # load just the launchpad plugin
        set_plugins_path()
        import bzrlib.plugins.launchpad

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    @contextlib.contextmanager
    def _unlocking_read_lock(self, obj):
        lock = obj.lock_read()
        yield obj
        lock.unlock()

    @contextlib.contextmanager
    def _unlocking_write_lock(self, obj):
        lock = obj.lock_write()
        yield obj
        lock.unlock()

    def simple_branch_op(self, from_url, to_path):
        """
        Do something equivalent to:

            bzr branch from_url to_path

        And return the ID of the branched revision
        """
        # <bzr-code>
        with self._unlocking_read_lock(Branch.open(from_url)) as branch_from:
            revision_id = branch_from.last_revision()
            transport_to = get_transport(to_path)
            dir = branch_from.bzrdir.sprout(transport_to.base, revision_id,
                                        possible_transports=[transport_to],
                                        source_branch=branch_from)
            # XXX: Should this be unlocked too?
            branch_to = dir.open_branch()
            old_revision_id = branch_to.get_rev_id(0)
            new_revision_id = branch_to.last_revision()
            # XXX: using internal bzr stuff, is there a public API to do this?
            from bzrlib.tag import _merge_tags_if_possible
            _merge_tags_if_possible(branch_from, branch_to)
        return (old_revision_id, new_revision_id)

    def simple_pull_op(self, from_url, to_path):
        """
        Do something equivalent to:

            bzr branch from_url to_path

        :return: (old_revision_id, new_revision_id)
        """
        with contextlib.nested(
            self._unlocking_write_lock(
                WorkingTree.open_containing(to_path)[0]),
            self._unlocking_read_lock(
                Branch.open(from_url))
        ) as (tree_to, branch_from):
            branch_to = tree_to.branch
            old_revision_id = branch_to.last_revision()
            tree_to.pull(branch_from)
            new_revision_id = branch_to.last_revision()
        return (old_revision_id, new_revision_id)

    def get_history_change(self, branch_path, old_revision_id, new_revision_id):
        """
        Get history between two revisions of a particular branch

        :return (old_history, new_history)
        """
        with self._unlocking_read_lock(
            Branch.open_containing(branch_path)[0]) as branch:
            old_history, new_history = get_history_change(
                old_revision_id, new_revision_id,
                branch.repository)
        return old_history, new_history

    def __broken_get_patch_delta(self):
        """
        Returns a tuple (outgoing, incoming) with the number
        of patches that are available but have not been merged
        either here or in trunk. The "trunk" is whatever we
        branched from.
        """
        # XXX: Ugly way to load bzr
        BzrHelper.get_instance()
        from bzrlib.missing import find_unmerged
        with (self._branch_from_path(self.component_branch.internal_checkout_dir),
              self._branch_from_url(self.component_branch.working_checkout_dir)) as (
                  local_branch, parent_branch):
            local_extra, parent_extra = find_unmerged(
                local_branch, parent_branch)
            return local_extra, parent_extra


class BranchOpsBzr(object):

    def __init__(self, component_branch):
        self.component_branch = component_branch
        self.bzr = BzrHelper.get_instance()

    def update_internal_checkout(self):
        """
        Update or create internal checkout
        
        :return: new_history (array of stuff) 
        """
        if self.component_branch.internal_checkout_exists:
            old_revision_id, new_revision_id = self.bzr.simple_pull_op(
                self.component_branch.url,
                self.component_branch.internal_checkout_dir)
        else:
            mkdir_p(os.path.dirname(self.component_branch.internal_checkout_dir))
            old_revision_id, new_revision_id = self.bzr.simple_branch_op(
                self.component_branch.url,
                self.component_branch.internal_checkout_dir)
        self.component_branch.state.last_update_revision_id = new_revision_id
        self.component_branch.state.last_update_branch_url = self.component_branch.url
        old_history, new_history = self.bzr.get_history_change(
            self.component_branch.internal_checkout_dir,
            old_revision_id, new_revision_id)
        return new_history

    def create_checkout(self):
        """
        Create public checkout
        """
        mkdir_p(os.path.dirname(self.component_branch.checkout_dir))
        self.bzr.simple_branch_op(
            self.component_branch.internal_checkout_dir,
            self.component_branch.checkout_dir)
