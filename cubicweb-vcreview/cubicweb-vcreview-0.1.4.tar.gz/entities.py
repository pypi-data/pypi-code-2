# copyright 2011 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
# contact http://www.logilab.fr -- mailto:contact@logilab.fr
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the Free
# Software Foundation, either version 2.1 of the License, or (at your option)
# any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License along
# with this program. If not, see <http://www.gnu.org/licenses/>.
"""cubicweb-vcreview entity's classes"""

from logilab.common.decorators import monkeypatch

from cubicweb.entities import AnyEntity

from cubes.comment import entities as comment
from cubes.vcsfile import entities as vcsfile
from cubes.task import entities as task


class InsertionPoint(AnyEntity):
    __regid__ = 'InsertionPoint'
    @property
    def parent(self):
        return self.point_of[0]


class Patch(AnyEntity):
    __regid__ = 'Patch'

    def dc_title(self):
        return self.patch_name

    @property
    def patch_name(self):
        return self.revisions[-1].file.path

    @property
    def repository(self):
        return self.patch_repository[0]

    @property
    def revisions(self):
        return sorted(self.patch_revision, key=lambda x: x.revision)

    def patch_files(self):
        return set(vc.file.path for vc in self.patch_revision)

    active_states = ('pending-review', 'in-progress')
    def is_active(self):
        return self.cw_adapt_to('IWorkflowable').state in self.active_states


@monkeypatch(vcsfile.DeletedVersionContent, 'patch')
@property
def patch(self):
    return self.reverse_patch_revision and self.reverse_patch_revision[0]


@monkeypatch(vcsfile.Repository, 'patchrepo_of')
@property
def patchrepo_of(self):
    return self.reverse_has_patch_repository and self.reverse_has_patch_repository[0]

@monkeypatch(vcsfile.Repository, 'patchrepo')
@property
def patchrepo(self):
    return self.has_patch_repository and self.has_patch_repository[0]

@monkeypatch(task.Task, 'activity_of')
@property
def activity_of(self):
    return self.reverse_has_activity and self.reverse_has_activity[0]


class CommentITreeAdapter(comment.CommentITreeAdapter):
    def path(self):
        path = super(CommentITreeAdapter, self).path()
        rootrset = self._cw.eid_rset(path[0])
        if rootrset.description[0][0] == 'InsertionPoint':
            path.insert(0, rootrset.get_entity(0, 0).parent.eid)
        return path


def registration_callback(vreg):
    vreg.register_all(globals().values(), __name__, (CommentITreeAdapter,))
    vreg.register_and_replace(CommentITreeAdapter, comment.CommentITreeAdapter)
