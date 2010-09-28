"""Forge cube hooks

:organization: Logilab
:copyright: 2006-2010 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
"""
__docformat__ = "restructuredtext en"

from datetime import datetime

from cubicweb import ValidationError
from cubicweb.server.hook import Hook, Operation
from cubicweb.selectors import is_instance
from cubicweb.server import hook

from cubes.tracker import hooks as tracker
from cubes.nosylist import hooks as nosylist


# configure dependency cubes hooks #############################################

tracker.VersionStatusChangeHook.ticket_states_start_version.add('done')
tracker.VersionStatusChangeHook.ticket_states_start_version.add('validation pending')

# permission propagation configuration
# not necessary on: generate_bug, instance_of, recommends, mailinglist_of
tracker.S_RELS |= set(('documented_by', 'attachment', 'screenshot'))
tracker.O_RELS |= set(('test_case_of', 'test_case_for', 'for_version',
                       'comments'))


nosylist.S_RELS |= tracker.S_RELS
nosylist.O_RELS |= tracker.O_RELS


# forge specific hooks #########################################################

class ChangeTicketStateOnVersionStatusChange(Hook):
    __regid__ = 'change_ticket_state_on_version_status_change'
    events = ('after_add_entity',)
    __select__ = Hook.__select__ & is_instance('TrInfo')

    def __call__(self):
        forentity = self.entity.for_entity
        if forentity.e_schema != 'Version':
            return
        if self.entity.new_state.name == 'published':
            for ticket in forentity.reverse_done_in:
                iwf = ticket.cw_adapt_to('IWorkflowable')
                if iwf.state == 'done':
                    msg = self._cw._('version published')
                    try:
                        iwf.fire_transition('ask validation',
                                            comment=msg,
                                            commentformat=u'text/plain')
                    except ValidationError, ex:
                        self.error('error while trying to change ticket state after version publishing: %s', ex)

class AdjustPendingTicketState(Operation):
    def precommit_event(self):
        iwf = self.ticket.cw_adapt_to('IWorkflowable')
        if (iwf.state == 'validation pending' and
            (not self.ticket.done_in
             or self.ticket.done_in[0].cw_adapt_to('IWorkflowable').state != 'published')):
            msg = self.session._('moved away from published version')
            iwf.change_state('open', comment=msg, commentformat=u'text/plain')


class ChangeTicketStateOnDoneInChange(Hook):
    """automatically add user who adds a comment to the nosy list"""
    __regid__ = 'change_ticket_state_on_done'
    events = ('after_delete_relation',)
    __select__ = Hook.__select__ & hook.match_rtype('done_in',)

    def __call__(self):
        ticket = self._cw.entity_from_eid(self.eidfrom)
        version = self._cw.entity_from_eid(self.eidto)
        # only change tickets in the validation pending state, not done
        # (since we want this behaviour to occurs for tickets moved
        # from a published version to an unpublished one, usually because
        # of non-validation
        if ticket.cw_adapt_to('IWorkflowable').state == 'validation pending':
            AdjustPendingTicketState(self._cw, ticket=ticket)


class ResetLoadLeftOnTicketStatusChange(Hook):
    __regid__ = 'reset_load_left_on_ticket'
    events = ('after_add_entity',)
    __select__ = Hook.__select__ & is_instance('TrInfo',)

    def __call__(self):
        forentity = self.entity.for_entity
        if forentity.e_schema != 'Ticket':
            return
        newstate = self.entity.new_state.name
        if newstate in ('done', 'rejected', 'deprecated'):
            # ticket is done, set load_left to 0
            attrs = {'load_left': 0}
            if newstate in ('rejected', 'deprecated'):
                # also reset load in that case, we don't want initial estimation
                # to be taken into account
                attrs['load'] = 0
            forentity.set_attributes(**attrs)


class SetTicketLoadLeft(Hook):
    """automatically set load_left according to load if unspecified"""
    __regid__ = 'set_ticket_load'
    events = ('before_add_entity', 'before_update_entity')
    __select__ = Hook.__select__ & is_instance('Ticket',)

    def __call__(self):
        edited = self.entity.edited_attributes
        has_load_left = 'load_left' in edited
        if 'load' in edited and self.entity.load_left is None:
            self.entity.load_left = self.entity['load']
        elif not has_load_left and 'load_left' in edited:
            # cleanup, this may cause undesired changes
            del self.entity['load_left']


class SetNosyListBeforeAddComment(Hook):
    """automatically add user who adds a comment to the nosy list"""
    __regid__ = 'set_nosy_list_before_add_comment'
    events = ('after_add_relation',)
    __select__ = Hook.__select__ & hook.match_rtype('comments',)

    def __call__(self):
        if self._cw.is_internal_session:
            return
        comment = self._cw.entity_from_eid(self.eidfrom)
        entity = comment.cw_adapt_to('ITree').root()
        if 'nosy_list' in entity.e_schema.subject_relations():
            x = entity.eid
        else:
            x = comment.eid
        self._cw.execute('SET X nosy_list U WHERE X eid %(x)s, U eid %(u)s, '
                         'NOT X nosy_list U',
                         {'x': x, 'u': self._cw.user.eid})


class SetModificationDateAfterAddComment(Hook):
    """update root entity's modification date after adding a comment"""
    __regid__ = 'set_modification_date_after_comment'
    events = ('after_add_relation',)
    __select__ = Hook.__select__ & hook.match_rtype('comments',)

    def __call__(self):
        entity = self._cw.entity_from_eid(self.eidto)
        while entity.e_schema == 'Comment':
            entity = entity.cw_adapt_to('ITree').root()
        entity.set_attributes(modification_date=datetime.now())


class TicketDoneInProgressHook(Hook):
    __regid__ = 'ticket_done_in_progress'
    __select__ = Hook.__select__ & hook.match_rtype('done_in',)
    events = ('after_add_relation', 'after_delete_relation', )

    def __call__(self):
        version = self._cw.entity_from_eid(self.eidto)
        version.update_progress()


class TicketProgressHook(Hook):
    __regid__ = 'ticket_progress'
    __select__ = Hook.__select__ & is_instance('Ticket',)
    events = ('after_update_entity', )

    def __call__(self):
        if 'load' in self.entity.edited_attributes or \
               'load_left' in self.entity.edited_attributes:
            try:
                self.entity.done_in[0].update_progress()
            except IndexError:
                # not yet attached to a version
                pass
