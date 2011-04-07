"""forge specific entities class for imported entities

:organization: Logilab
:copyright: 2006-2010 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
"""
__docformat__ = "restructuredtext en"

from datetime import datetime, date, timedelta

from logilab.common.date import nb_open_days

from cubicweb.entities import AnyEntity, fetch_config
from cubicweb.entities.adapters import IFTIndexableAdapter
from cubicweb.selectors import is_instance

from cubes.card.entities import Card as BaseCard
from cubes.file.entities import File as BaseFile
from cubes.comment.entities import Comment as BaseComment
from cubes.email.entities import Email as BaseEmail
from cubes.tracker.entities import project, version, ticket
from cubes.tracker.entities import ProjectItemMixIn, fixed_orderby_rql


# project / extproject #########################################################


class ExtProject(AnyEntity):
    __regid__ = 'ExtProject'
    __permissions__ = ('developer', 'client')

    fetch_attrs, fetch_order = fetch_config(['name', 'description', 'description_format'])

    def dc_title(self, format='text/plain'):
        return self.name


class Project(project.Project):

    __permissions__ = ('developer', 'client')
    fetch_attrs = project.Project.fetch_attrs + ('homepage', 'summary')

    TICKET_DEFAULT_STATE_RESTR = 'S name IN ("open","done","waiting feedback","in-progress","validation pending")'

    # number of columns to display
    tickets_rql_nb_displayed_cols = 10
    sort_defs = (('in_state', 'S'), ('num', 'VN'), ('type', 'TT'),
                 ('priority', 'PR'))
    def tickets_rql(self, limit=None):
        return ('Any B,TT,NOW - CD, NOW - BMD, U,PR,S,C,V,group_concat(TN),BDF,BD,BC,VN,P,BT,CD,BMD,UL '
                'GROUPBY B,TT,CD,PR,S,C,V,U,VN,BDF,BD,BC,P,BT,BMD,UL %s %s WHERE '
                'B type TT, B priority PR, B in_state S, B creation_date CD, '
                'B description_format BDF, B description BD, B load_left BC, '
                'B title BT, B modification_date BMD, '
                'B load C, T? tags B, T name TN, B done_in V?, V num VN, '
                'B created_by U?, U login UL, B concerns P, P eid %%(x)s'
                % (fixed_orderby_rql(self.sort_defs),
                   limit and ' LIMIT %s' % limit or ''),
                {'x': self.eid})


class ProjectIFTIndexableAdapter(IFTIndexableAdapter):
    __select__ = is_instance('Project')
    entity_weight = 20.0


# version ######################################################################

class Version(version.Version):

    fetch_attrs = ('num', 'description', 'description_format', 'in_state')

    # version'specific logic ##################################################

    def velocity(self):
        """return computed velocity or None if some information is missing"""
        iprogress = self.cw_adapt_to('IProgress')
        if iprogress.finished():
            stop = self.stop_date()
        else:
            stop =  date.today()
        start = self.start_date()
        if stop is None or start is None or start > stop:
            return None
        nb_days = nb_open_days(start, stop)
        if nb_days:
            return iprogress.progress_info()['done'] / float(nb_days)
        return None

    def tarball_name(self):
        return '%s-%s.tar.gz' % (self.project.name, self.num)

    def estimated_load(self):
        """return the actually estimated load of the version:
        even if some tasks are marked as done, consider their estimated load and
        not there effective load

        notice that actually 2 values are returned :
        * the estimated load
        * the number of tasks which have no estimated time
        """
        missing = 0
        total = 0
        for entity in self.reverse_done_in:
            estimated_load = entity.load or 0
            if estimated_load is None:
                missing += 1
            else:
                total += estimated_load
        return (total, missing)

    def update_progress(self):
        progress_target = 0
        progress_todo = 0
        progress_done = 0
        for ticket in self.reverse_done_in:
            progress_target += ticket.corrected_load()
            progress_todo += ticket.corrected_load_left()
        progress_done = max(0, progress_target - progress_todo)
        self.set_attributes(progress_target=progress_target,
                            progress_todo=progress_todo,
                            progress_done=progress_done)

    # ui utilities ############################################################

    # number of columns to display
    tickets_rql_nb_displayed_cols = 8
    sort_defs = (('in_state', 'S'), ('type', 'TT'), ('priority', 'PR'))
    def tickets_rql(self):
        """rql for tickets done / todo in this version"""
        return ('Any B,TT,PR,S,C,AC,U,group_concat(TN), TI,D,DF,V '
                'GROUPBY B,TT,PR,S,C,AC,U,TI,D,DF,V %s '
                'WHERE B type TT, B priority PR, B load_left AC, B load C, '
                'B in_state S, T? tags B, T name TN, B created_by U?,'
                'B done_in V, V eid %%(x)s, '
                'B title TI, B description D, B description_format DF'
                % fixed_orderby_rql(self.sort_defs), {'x': self.eid})

    defects_rql_nb_displayed_cols = 5
    def defects_rql(self):
        """rql for defects appeared in this version"""
        return ('Any B,S,V,U,group_concat(TN), BT,BD,BDF '
                'GROUPBY B,S,V,U,BT,BD,BDF ORDERBY S '
                'WHERE B in_state S, T? tags B, T name TN, B created_by U?,'
                'B done_in V?, B appeared_in X, X eid %(x)s, '
                'B title BT, B description BD, B description_format BDF',
                {'x': self.eid})


class VersionIMileStoneAdapter(version.VersionIMileStoneAdapter):

    def progress_info(self):
        """returns a dictionary describing load and progress of the version"""
        entity = self.entity
        return {'estimated': entity.progress_target,
                'done': entity.progress_done,
                'todo': entity.progress_todo,
                'notestimated': len([t for t in entity.reverse_done_in
                                     if t.load is None]),
                }

    def eta_date(self):
        """return expected date based on remaining tasks and velocity"""
        entity = self.entity
        if entity.cw_adapt_to('IWorkflowable').state != 'dev':
            return None
        velocity = entity.velocity()
        if velocity is None:
            return None
        # XXX if velocity == 0, use a hidden attribute which is computed from
        #     precedent version's velocity
        velocity = velocity or 1
        return datetime.now() + timedelta(self.todo / velocity)

# qui peut le plus peut le moins
class VersionIProgressAdapter(VersionIMileStoneAdapter):
    __regid__ = 'IProgress'

# ticket #######################################################################

class Ticket(ticket.Ticket):

    fetch_attrs = ('title', 'type', 'priority', 'load', 'load_left', 'in_state')
    noload_cost = 10

    # ticket'specific logic ###################################################

    OPEN_STATES = frozenset(('open', 'waiting feedback', 'in-progress'))

    def corrected_load(self):
        if self.load is not None:
            return self.load
        return self.noload_cost

    def corrected_load_left(self):
        if self.load_left is not None:
            return self.load_left
        return self.corrected_load()

class TicketIFTIndexableAdapter(IFTIndexableAdapter):
    __select__ = is_instance('Ticket')
    entity_weight = 10.0


# forge specific entities and library overrides ################################

class License(AnyEntity):
    __regid__ = 'License'
    fetch_attrs = ('name', 'url')


# XXX should be independant of testcard cube'schema
class Card(ProjectItemMixIn, BaseCard):
    fetch_attrs = ('title', 'wikiid')

    @property
    def project(self):
        """project item interface"""
        if self.reverse_documented_by:
            return self.reverse_documented_by[0]
        if self.test_case_of:
            return self.test_case_of[0]
        if self.test_case_for:
            return self.test_case_for[0].project


class Comment(BaseComment):

    @property
    def project(self):
        """project item interface"""
        try:
            return self.cw_adapt_to('ITree').root().project
        except AttributeError:
            return None


class File(ProjectItemMixIn, BaseFile):

    @property
    def project(self):
        """project item interface"""
        if self.reverse_documented_by:
            return self.reverse_documented_by[0]
        if self.reverse_attachment:
            return self.reverse_attachment[0].project
        if self.reverse_screenshot:
            return self.reverse_screenshot[0].project


# XXX necessary?
class Email(ProjectItemMixIn, BaseEmail):
    pass


def registration_callback(vreg):
    vreg.register_all(globals().values(), __name__,
                      (VersionIMileStoneAdapter, VersionIProgressAdapter))
    vreg.register_and_replace(VersionIMileStoneAdapter,
                              version.VersionIMileStoneAdapter)
    vreg.register_and_replace(VersionIProgressAdapter,
                              version.VersionIProgressAdapter)
