"""tracker specific hooks

:organization: Logilab
:copyright: 2006-2010 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
"""
__docformat__ = "restructuredtext en"

from itertools import chain

from logilab.common.decorators import classproperty
from logilab.common.compat import any

from cubicweb import ValidationError
from cubicweb.utils import transitive_closure_of
from cubicweb.schema import META_RTYPES
from cubicweb.selectors import is_instance
from cubicweb.server import hook
from cubicweb.hooks import notification

# automatization hooks #########################################################

class VersionStatusChangeHook(hook.Hook):
    """when a ticket is done, automatically set its version'state to 'dev' if
      necessary
    """
    __regid__ = 'version_status_change_hook'
    __select__ = hook.Hook.__select__ & hook.match_rtype('in_state',)
    events = ('after_add_relation',)
    ticket_states_start_version = set(('in-progress',))

    def __call__(self):
        entity = self._cw.entity_from_eid(self.eidfrom)
        if entity.e_schema != 'Ticket':
            return
        iwf = entity.cw_adapt_to('IWorkflowable')
        if iwf.state in self.ticket_states_start_version \
               and entity.in_version():
            versioniwf = entity.in_version().cw_adapt_to('IWorkflowable')
            if any(tr for tr in versioniwf.possible_transitions()
                   if tr.name == 'start development'):
                versioniwf.fire_transition('start development')


class TicketDoneInChangeHook(hook.Hook):
    """when a ticket is attached to a version and it's identical to another one,
    attach the other one as well
    """
    __regid__ = 'ticket_done_in_change'
    __select__ = hook.Hook.__select__ & hook.match_rtype('done_in',)
    events = ('after_add_relation',)

    def __call__(self):
        entity = self._cw.entity_from_eid(self.eidfrom)
        execute = entity._cw.execute
        for identic in entity.identical_to:
            iversion = identic.in_version()
            iveid = iversion and iversion.eid
            if iveid != self.eidto:
                try:
                    execute('SET X done_in V WHERE X eid %(x)s, V eid %(v)s',
                            {'x': identic.eid, 'v': self.eidto})
                except:
                    self.exception("can't synchronize version")


class TicketStatusChangeHook(hook.Hook):
    """when a ticket status change and it's identical to another one, change the
    state of the other one as well
    """
    __regid__ = 'ticket_status_change_hook'
    __select__ = hook.Hook.__select__ & is_instance('TrInfo')
    events = ('after_add_entity',)

    def __call__(self):
        trinfo = self.entity
        forentity = trinfo.for_entity
        if forentity.e_schema != 'Ticket' or not forentity.identical_to:
            return
        synchronized = self._cw.transaction_data.setdefault(
            'ticket_wf_synchronized', set())
        if forentity.eid in synchronized:
            return
        synchronized.add(forentity.eid)
        pstate = trinfo.previous_state
        tr = trinfo.transition
        for identic in forentity.identical_to:
            if identic.eid in synchronized:
                continue
            idiwf = identic.cw_adapt_to('IWorkflowable')
            if idiwf.current_state and idiwf.current_state.eid == pstate.eid:
                try:
                    idiwf.fire_transition(tr.name, trinfo.comment,
                                          trinfo.comment_format)
                except:
                    self.exception("can't synchronize identical ticket's state")


# verification hooks ###########################################################

class CheckProjectCyclesHook(hook.Hook):
    __regid__ = 'check_project_cycles'
    __select__ = hook.Hook.__select__ & hook.match_rtype('subproject_of',)
    events = ('before_add_relation',)

    def __call__(self):
        # detect cycles
        proj = self._cw.entity_from_eid(self.eidfrom)
        for child in transitive_closure_of(proj, 'reverse_subproject_of'):
            if self.eidto == child.eid:
                msg = self._cw._('you cannot link these entities, they would form a cycle')
                raise ValidationError(self.eidto, {'child' : msg})


# notification hooks ###########################################################

class BeforeUpdateVersion(notification.EntityUpdateHook):
    __regid__ = 'before_update_version'
    __select__ = notification.EntityUpdateHook.__select__ & is_instance('Version')
    skip_attrs = META_RTYPES | set(('description', 'description_format', 'num'))

class BeforeUpdateTicket(notification.EntityUpdateHook):
    __regid__ = 'before_update_ticket'
    __select__ = notification.EntityUpdateHook.__select__ & is_instance('Ticket')
    skip_attrs = META_RTYPES | set(('done_in', 'concerns', 'description_format'))

class BeforeInVersionChangeHook(hook.Hook):
    __regid__ = 'before_in_version_change'
    __select__ = hook.Hook.__select__ & hook.match_rtype('done_in',)
    events = ('before_add_relation',)

    def __call__(self):
        if self.eidfrom in self._cw.transaction_data.get('neweids', ()):
            return # entity is being created
        changes = self._cw.transaction_data.setdefault('changes', {})
        thisentitychanges = changes.setdefault(self.eidfrom, set())
        oldrset = self._cw.execute("Any VN WHERE V num VN, T done_in V, T eid %(eid)s",
                                  {'eid': self.eidfrom})
        oldversion = oldrset and oldrset[0][0] or None
        newrset = self._cw.execute("Any VN WHERE V num VN, V eid %(eid)s",
                                  {'eid': self.eidto})
        newversion = newrset[0][0]
        if oldversion != newversion:
            thisentitychanges.add(('done_in', oldversion, newversion))
            notification.EntityUpdatedNotificationOp(self._cw)


# require_permission propagation hooks #########################################

# relations where the "main" entity is the subject
S_RELS = set()
# relations where the "main" entity is the object
O_RELS = set(('concerns', 'version_of', 'subproject_of'))
# not necessary on:
#
# * "secondary" relations: todo_by, done_in, appeared_in, depends_on, uses
# * no propagation needed: wf_info_for
#
# XXX: see_also

# relations where the "main" entity is the subject/object that should be skipped
# when propagating to entities linked through some particular relation
SKIP_S_RELS = set()
SKIP_O_RELS = set()


class AddEntitySecurityPropagationHook(hook.PropagateRelationHook):
    """propagate permissions when new entity are added"""
    __regid__ = 'add_entity_security_propagation'
    __select__ = (hook.PropagateRelationHook.__select__
                  & hook.match_rtype_sets(S_RELS, O_RELS))
    main_rtype = 'require_permission'
    subject_relations = S_RELS
    object_relations = O_RELS


class AddPermissionSecurityPropagationHook(hook.PropagateRelationAddHook):
    __regid__ = 'add_permission_security_propagation'
    __select__ = (hook.PropagateRelationAddHook.__select__
                  & hook.match_rtype('require_permission'))
    subject_relations = S_RELS
    object_relations = O_RELS
    skip_subject_relations = SKIP_S_RELS
    skip_object_relations = SKIP_O_RELS

class DelPermissionSecurityPropagationHook(hook.PropagateRelationDelHook):
    __regid__ = 'del_permission_security_propagation'
    __select__ = (hook.PropagateRelationDelHook.__select__
                  & hook.match_rtype('require_permission'))
    subject_relations = S_RELS
    object_relations = O_RELS
    skip_subject_relations = SKIP_S_RELS
    skip_object_relations = SKIP_O_RELS


# has_group_permission propagation hooks #######################################

class AddGroupPermissionSecurityPropagationHook(hook.Hook):
    """propagate on group users when a permission is granted to a group"""
    __regid__ = 'add_group_permission_security_propagation'
    __select__ = hook.Hook.__select__ & hook.match_rtype('require_group',)
    events = ('after_add_relation',)
    rql = ('SET U has_group_permission P WHERE U in_group G, P eid %(p)s, G eid %(g)s,'
           'NOT U has_group_permission P')

    def __call__(self):
        if self._cw.describe(self.eidfrom)[0] != 'CWPermission':
            return
        self._cw.execute(self.rql, {'p': self.eidfrom, 'g': self.eidto})


class DelGroupPermissionSecurityPropagationHook(AddGroupPermissionSecurityPropagationHook):
    """propagate on group users when a permission is removed to a group"""
    __regid__ = 'del_group_permission_security_propagation'
    events = ('after_delete_relation',)
    rql = ('DELETE U has_group_permission P WHERE U in_group G, P eid %(p)s, G eid %(g)s,'
           'NOT EXISTS(U in_group G2, P require_group G2)')


class AddInGroupSecurityPropagationHook(hook.Hook):
    """propagate group permission to users when a permission is granted to a group"""
    __regid__ = 'add_in_group_permission_security_propagation'
    __select__ = hook.Hook.__select__ & hook.match_rtype('in_group',)
    events = ('after_add_relation',)
    rql = ('SET U has_group_permission P WHERE U eid %(u)s, P require_group G, '
           'G eid %(g)s, NOT U has_group_permission P')

    def __call__(self):
        self._cw.execute(self.rql, {'u': self.eidfrom, 'g': self.eidto})


class DelInGroupSecurityPropagationHook(AddInGroupSecurityPropagationHook):
    """propagate on existing entities when a permission is deleted"""
    __regid__ = 'del_in_group_permission_security_propagation'
    events = ('after_delete_relation',)
    rql = ('DELETE U has_group_permission P WHERE U eid %(u)s, P require_group G, '
           'G eid %(g)s, NOT EXISTS(U in_group G2, P require_group G2)')
