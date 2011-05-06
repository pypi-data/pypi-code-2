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

from __future__ import with_statement

from cubicweb.devtools.testlib import CubicWebTC
from cubicweb.server.session import security_enabled, hooks_control

class PatchReviewWorkflowTC(CubicWebTC):

    def setup_database(self):
        req = self.request()
        self.reviewer = self.create_user(req, 'reviewer', ('users', 'reviewers'))
        self.committer = self.create_user(req, 'committer', ('users',))
        session = self.session
        session.set_pool()
        with security_enabled(session, write=False):
            with hooks_control(session, session.HOOKS_DENY_ALL, 'metadata'):
                vcrepo = session.create_entity(
                    'Repository', repository_committer=self.committer)
                patch = session.create_entity(
                    'Patch', patch_repository=vcrepo)
                session.commit(reset_pool=False)

    def test_wf(self):
        req = self.request()
        patch = req.execute('Patch X').get_entity(0, 0)
        self.failIf(patch.patch_reviewer)
        patch.cw_adapt_to('IWorkflowable').fire_transition('ask review')
        self.commit()
        patch.cw_clear_all_caches()
        self.assertEqual(patch.patch_reviewer[0].eid, self.reviewer.eid)
        with self.login('reviewer'):
            req = self.request()
            rset = req.execute('Any X WHERE X is Patch')
            self.assertListEqual(sorted(x[0] for x in self.action_submenu(req, rset, 'workflow')),
                                 ['accept', 'fold', 'refuse', 'view history', 'view workflow'])
            patch = rset.get_entity(0, 0)
            patch.cw_adapt_to('IWorkflowable').fire_transition('accept')
            self.commit()
            patch.cw_clear_all_caches()
            self.assertListEqual(sorted(x[0] for x in self.action_submenu(req, rset, 'workflow')),
                                 ['fold', 'refuse', 'view history', 'view workflow'])
        with self.login('committer'):
            req = self.request()
            patch = req.execute('Patch X').get_entity(0, 0)
            rset = req.execute('Any X WHERE X is Patch')
            self.assertListEqual(sorted(x[0] for x in self.action_submenu(req, rset, 'workflow')),
                                 ['apply', 'fold', 'refuse', 'reject', 'view history', 'view workflow'])
            patch.cw_adapt_to('IWorkflowable').fire_transition('apply')
            self.commit()
            patch.cw_clear_all_caches()
            self.assertListEqual(sorted(x[0] for x in self.action_submenu(req, rset, 'workflow')),
                                 ['view history'])


if __name__ == '__main__':
    from logilab.common.testlib import unittest_main
    unittest_main()
