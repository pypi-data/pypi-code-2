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
"""cubicweb-trackervcs specific hooks and operations"""

import re

from cubicweb import typed_eid
from cubicweb.server import hook
from cubicweb.selectors import is_instance

from cubes.tracker import hooks as tracker

TICKET_EID_RGX = re.compile('#(\d+)')

class SearchRevisionTicketOp(hook.DataOperationMixIn,
                             hook.Operation):
    """search magic words in revision's commit message:

        closes #<ticket eid>

    When found, the ticket is marked as closed by the revision and its state is
    changed.
    """
    def precommit_event(self):
        for rev in self.get_data():
            # search for instruction
            for line in rev.description.splitlines():
                words = [w.lower() for w in re.findall('#?\w+', line.strip())]
                try:
                    idx = words.index('closes')
                except ValueError:
                    continue
                for eid in TICKET_EID_RGX.findall(' '.join(words[idx+1:])):
                    rset = self.session.execute(
                        'Ticket X WHERE X eid %(x)s, T concerns P, '
                        'P source_repository R, R eid %(r)s',
                        {'x': typed_eid(eid), 'r': rev.repository.eid})
                    if rset:
                        ticket = rset.get_entity(0, 0)
                        ticket.set_relations(closed_by=rev)
                        iwf = ticket.cw_adapt_to('IWorkflowable')
                        for tr in iwf.possible_transitions():
                            if tr.name in ('done', 'close'):
                                iwf.fire_transition(tr)
                                break

class RevisionAdded(hook.Hook):
    __regid__ = 'trackervcs.revistion-to-ticket-state'
    __select__ = hook.Hook.__select__ & is_instance('Revision')
    events = ('after_add_entity',)

    def __call__(self):
        repo = self.entity.repository
        if repo.reverse_source_repository:
            SearchRevisionTicketOp.get_instance(self._cw).add_data(self.entity)


tracker.S_RELS |= set(('source_repository', 'has_patch_repository',
                       'patch_revision',
                       'has_activity', ))
tracker.O_RELS |= set(('patch_repository', 'point_of',))


def registration_callback(vreg):
    if vreg.config['trusted-vcs-repositories']:
        vreg.register(RevisionAdded)
