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

from shutil import rmtree

from logilab.common.shellutils import unzip
from logilab.common.testlib import mock_object

from cubicweb.devtools.testlib import MAILBOX

from cubes.vcsfile.testutils import VCSRepositoryTC
from cubes.vcreview import hooks

def revnums(patch):
    return sorted(vc.revision for vc in patch.patch_revision)


class PatchCreationHooksTC(VCSRepositoryTC):
    _repo_path = u'patchrepo'
    repo_title = u'patch repository'
    commitevery = 1

    @classmethod
    def setUpClass(cls):
        unzip(cls.repo_path + '.zip', cls.datadir)

    @classmethod
    def tearDownClass(cls):
        try:
            rmtree(cls.repo_path)
        except:
            pass

    def setup_database(self):
        super(PatchCreationHooksTC, self).setup_database()
        assert self.execute('INSERT EmailAddress E: E address "admin@cwo", U primary_email E '
                            'WHERE U login "admin"')

    def _create_repo(self):
        vcsrepo = super(PatchCreationHooksTC, self)._create_repo()
        # circular relations, only to make it think it is a patch repository
        vcsrepo.set_relations(has_patch_repository=vcsrepo)
        return vcsrepo

    def test_imported_patches(self):
        patches = self.execute('Patch X ORDERBY X')

        byfile = {}
        bypatch = {}
        for patch in patches.entities():
            files = patch.patch_files()
            if len(files) == 1:
                byfile.setdefault(iter(files).next(), []).append(patch)
            else:
                bypatch[patch] = files
        self.assertEqual(len(byfile), 3, byfile)
        # bypatch check we're correctly following renaming
        self.assertEqual(len(bypatch), 1)
        self.assertEqual(len(patches), 6)

        folded = bypatch.keys()[0]
        self.assertEqual(folded.cw_adapt_to('IWorkflowable').state, 'folded')

        self.assertEqual(len(byfile['patch1.diff']), 2)
        patch1_1 = byfile['patch1.diff'][0]
        self.assertEqual(patch1_1.cw_adapt_to('IWorkflowable').state, 'deleted')
        self.assertEqual(revnums(patch1_1), [0, 1])
        patch1_2 = byfile['patch1.diff'][1]
        self.assertEqual(patch1_2.cw_adapt_to('IWorkflowable').state, 'deleted')
        self.assertEqual(revnums(patch1_2), [7, 8, 9])

        self.assertEqual(len(byfile['patch2.diff']), 1)
        patch2 = byfile['patch2.diff'][0]
        self.assertEqual(patch2.cw_adapt_to('IWorkflowable').state, 'deleted')
        self.assertEqual(revnums(patch2), [0, 1, 2, 5, 6])

        self.assertEqual(len(byfile['patch3.diff']), 2)
        patch3_1 = byfile['patch3.diff'][0]
        self.assertEqual(patch3_1.cw_adapt_to('IWorkflowable').state, 'deleted')
        self.assertEqual(revnums(patch3_1), [3, 4])
        patch3_2 = byfile['patch3.diff'][1]
        history = patch3_2.cw_adapt_to('IWorkflowable').workflow_history
        self.assertEqual(history[-1].previous_state.name, 'pending-review')
        self.assertEqual(history[-1].new_state.name, 'rejected')
        self.assertEqual(revnums(patch3_2), [7, 10, 15])

        self.assertTrue(patch3_2.nosy_list)
        self.assertEqual(len(MAILBOX), 2)
        self.assertEqual(MAILBOX[0].subject, '[%s] patch %s is now in state "pending-review"'
                         % (patch3_2.repository.dc_title(), patch3_2.dc_title()))
        self.assertEqual(MAILBOX[0].recipients, ['admin@cwo'])
        self.assertMultiLineEqual(MAILBOX[0].content, u'''
cubicweb changed status from <in-progress> to <pending-review> for entity
'patch3.diff'

review asked by Sylvain Th\xe9nault <sylvain.thenault@logilab.fr> in 9cf50f15d9a7

url: http://testing.fr/cubicweb/patch/%s\n''' % patch3_2.eid)

        self.assertEqual(MAILBOX[1].subject, '[%s] patch %s is now in state "rejected"'
                         % (patch3_2.repository.dc_title(), patch3_2.dc_title()))
        self.assertEqual(MAILBOX[1].recipients, ['admin@cwo'])
        self.assertMultiLineEqual(MAILBOX[1].content, u'''
cubicweb changed status from <pending-review> to <rejected> for entity
'patch3.diff'

rejected by Sylvain Th\xe9nault <sylvain.thenault@logilab.fr> in a5c0568f81db

url: http://testing.fr/cubicweb/patch/%s\n''' % patch3_2.eid)

        MAILBOX[:] = ()
        req = self.request()
        req.create_entity('Task', title=u'todo', reverse_has_activity=patch3_2)
        done = req.create_entity('Task', title=u'done', reverse_has_activity=patch3_2)
        self.commit()
        self.assertEqual(len(MAILBOX), 2)
        self.assertEqual(MAILBOX[1].subject, '[%s] new task for %s: done'
                         % (patch3_2.repository.dc_title(), patch3_2.dc_title()))
        self.assertEqual(MAILBOX[1].recipients, ['admin@cwo'])
        self.assertMultiLineEqual(MAILBOX[1].content, u'''
done



url: http://testing.fr/cubicweb/task/%s\n''' % done.eid)

        MAILBOX[:] = ()
        done.cw_adapt_to('IWorkflowable').fire_transition('done')
        self.commit()
        self.assertEqual(MAILBOX, [])

        # force state
        patch3_2.cw_adapt_to('IWorkflowable').change_state('pending-review')
        self.commit()

        MAILBOX[:] = ()
        # fake revision from the main repo of our patch repo
        revision = mock_object(repository=self.vcsrepo,
                               description='applied patch patch3.diff',
                               eid=patch3_2.revisions[-1].rev.eid)
        # hi-hack vcsrepo._cw to avoid connections pool pb
        self.vcsrepo._cw = self.session
        op = hooks.SearchAppliedPatchOp.get_instance(self.session)
        op.add_data(revision)
        self.commit() # will process our fake operation
        patch3_2.clear_all_caches()
        self.assertEqual(patch3_2.cw_adapt_to('IWorkflowable').state, 'applied')
        self.assertEqual(patch3_2.applied_at[0].eid, patch3_2.revisions[-1].rev.eid)

        self.assertEqual(len(MAILBOX), 1, MAILBOX)
        self.assertEqual(MAILBOX[0].subject, '[%s] patch %s is now in state "applied"'
                         % (patch3_2.repository.dc_title(), patch3_2.dc_title()))
        self.assertEqual(MAILBOX[0].recipients, ['admin@cwo'])
        self.assertMultiLineEqual(MAILBOX[0].content, u'''
admin changed status from <pending-review> to <applied> for entity
'patch3.diff'



remaining tasks:

- todo

url: http://testing.fr/cubicweb/patch/%s\n''' % patch3_2.eid)



if __name__ == '__main__':
    from logilab.common.testlib import unittest_main
    unittest_main()
