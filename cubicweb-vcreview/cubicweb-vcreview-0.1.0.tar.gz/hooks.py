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
"""cubicweb-vcreview specific hooks and operations"""

from cubicweb.server import hook
from cubicweb.selectors import is_instance

IGNORE_FILES = set( ('README', 'series', '.hgignore') )

class LinkOrCreatePatchOp(hook.DataOperationMixIn, hook.Operation):
    containercls = list

    def precommit_event(self):
        for entity in self.get_data():
            patch = None
            # if the revision is a renaming another one which is linked to the
            # patch (take care DeletedVersionContent has not vc_rename relation)
            if getattr(entity, 'vc_rename', None) and entity.vc_rename[0].patch:
                patch = entity.vc_rename[0].patch
            else:
                # search for previous revision of the patch file
                branches = set(x.branch for x in entity.rev.parent_revision)
                for branch in branches:
                    parent = entity.previous_version(branch)
                    if parent is not None and parent.patch:
                        patch = parent.patch
                        break
            # create a new patch entity if no one found or if found a closed
            # patch and this is not a file deletion
            if patch is None or (not patch.is_active() and entity.__regid__ == 'VersionContent'):
                patch = self.session.create_entity(
                    'Patch', patch_repository=entity.rev.from_repository)
            patch.set_relations(patch_revision=entity)
            # patch file is being removed: mark it on the patch entity if still
            # active
            if entity.__regid__ == 'DeletedVersionContent' and patch.is_active():
                if self.session.added_in_transaction(patch.eid):
                    self.session.execute('SET X in_state S WHERE X eid %(x)s, S name %(state)s',
                                         {'x': patch.eid, 'state': 'deleted'})
                    # patch.cw_adapt_to('IWorkflowable').change_state('deleted')
                else:
                    patch.cw_adapt_to('IWorkflowable').fire_transition('file deleted')


class LinkOrCreatePatchHook(hook.Hook):
    __regid__ = 'vcreview.create-patch'
    __select__ = hook.Hook.__select__ & is_instance('VersionContent',
                                                    'DeletedVersionContent')
    events = ('after_add_entity',)

    def __call__(self):
        entity = self.entity
        # skip file not from a patch repository
        if not entity.repository.patchrepo_of:
            return
        if entity.file.name in IGNORE_FILES:
            return
        LinkOrCreatePatchOp.get_instance(self._cw).add_data(entity)


# use late operation to be executed after workflow operation
class SearchPatchStateInstructionOp(hook.DataOperationMixIn,
                                    hook.LateOperation):
    """search magic word in revision's commit message:

        <patch path> ready for review

    When found, the patch will be marked as pending review. You can put multiple
    instructions like this, one per line.
    """
    containercls = list
    def precommit_event(self):
        for rev in self.get_data():
            # search patches among files modified by the revision
            candidates = {}
            for vc in rev.reverse_from_revision:
                if vc.patch and vc.patch.cw_adapt_to('IWorkflowable').state == 'in-progress':
                    candidates[vc.file.path] = vc.patch
            # search for instruction
            for line in rev.description.splitlines():
                words = line.strip().split()
                if words[0] in candidates and words[1:4] == ['ready', 'for', 'review']:
                    patch = candidates.pop(words[0])
                    patch.cw_adapt_to('IWorkflowable').fire_transition(
                        'ask review', 'review asked by %s in %s' % (
                            rev.author, rev.changeset or rev.revision))


class SearchAppliedPatchOp(hook.DataOperationMixIn,
                           hook.Operation):
    """search magic word in revision's commit message:

        applied patch <patch path>

    When found, the patch is marked as applied and linked to the revision.
    """
    containercls = list
    def precommit_event(self):
        for rev in self.get_data():
            patchrepo = rev.repository.patchrepo
            # search patches among in-progress/deleted/pending-review
            candidates = {}
            for patch in self.session.execute(
                # order by so that we consider the latest patch with activities
                # in case of conflict (may have due to search of 'deleted'
                # status)
                'Any P ORDERBY P ASC WHERE P patch_revision VC, VC from_revision REV, '
                'REV from_repository R, R eid %(r)s, P in_state PS, '
                'PS name IN ("in-progress", "deleted", "pending-review")',
                {'r': patchrepo.eid}).entities():
                candidates[patch.patch_name] = patch
            # search for instruction
            for line in rev.description.splitlines():
                words = line.strip().split()
                if words[-1] in candidates and words[-3:-1] == ['applied', 'patch']:
                    patch = candidates.pop(words[-1])
                    patch.cw_adapt_to('IWorkflowable').fire_transition('accept')
                    patch.set_relations(applied_at=rev)


class RevisionAdded(hook.Hook):
    __regid__ = 'vcreview.auto-change-patch-state'
    __select__ = hook.Hook.__select__ & is_instance('Revision')
    events = ('after_add_entity',)

    def __call__(self):
        repo = self.entity.repository
        if repo.patchrepo_of:
            # patch repository
            SearchPatchStateInstructionOp.get_instance(self._cw).add_data(self.entity)
        elif repo.patchrepo:
            # main repository linked to patch repository
            SearchAppliedPatchOp.get_instance(self._cw).add_data(self.entity)


from cubes.nosylist import hooks as nosylist
nosylist.S_RELS |= set(('has_activity',))
nosylist.O_RELS |= set(('patch_repository',))
