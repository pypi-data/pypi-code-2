"""views for Version entities

:organization: Logilab
:copyright: 2006-2010 LOGILAB S.A. (Paris, FRANCE), license is LGPL.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
"""
__docformat__ = "restructuredtext en"
_ = unicode

from datetime import date

from logilab.mtconverter import xml_escape

from cubicweb import tags
from cubicweb.selectors import (objectify_selector, is_instance, score_entity,
                                match_search_state, one_line_rset)
from cubicweb.view import StartupView, EntityView, EntityAdapter
from cubicweb.web import uicfg, component, action
from cubicweb.web.views import (primary, baseviews, tabs, xmlrss, navigation,
                                iprogress, ibreadcrumbs)

from cubes.tracker.entities import attr_tuple

_pvs = uicfg.primaryview_section
# in their own tabs
_pvs.tag_object_of(('*', 'done_in', 'Version'), 'hidden')
_pvs.tag_object_of(('*', 'appeared_in', 'Version'), 'hidden')
# in breadcrumb & all
_pvs.tag_subject_of(('Version', 'version_of', '*'), 'hidden')
# in progress stable
_pvs.tag_subject_of(('Version', 'depends_on', 'Version'), 'hidden')
_pvs.tag_subject_of(('Version', 'todo_by', 'CWUser'), 'hidden')
# in title, progress stable
for attr in ('num', 'starting_date', 'prevision_date'):
    _pvs.tag_attribute(('Version', attr), 'hidden')
# display reverse dependencies
_pvs.tag_object_of(('Version', 'depends_on', 'Version'), 'sideboxes')

_pvdc = uicfg.primaryview_display_ctrl
# no label for version's description
_pvdc.tag_attribute(('Version', 'description'), {'showlabel': False})

# primary view and tabs ########################################################

class VersionPrimaryView(tabs.TabbedPrimaryView):
    __select__ = is_instance('Version')
    tabs = tabs.TabbedPrimaryView.tabs[:] + [
        _('tracker.version.tickets_tab'), _('tracker.version.defects_tab')]

    def render_entity_title(self, entity):
        self._cw.add_css('cubes.tracker.css')
        self.w(u'<h1>') #% entity.progress_class())
        self.w('%s %s <span class="state">[%s]</span>' % (
            xml_escape(entity.project.name), xml_escape(entity.num),
            xml_escape(self._cw._(entity.cw_adapt_to('IWorkflowable').state))))
        self.w(u'</h1>\n')


class VersionPrimaryTab(tabs.PrimaryTab):
    __select__ = is_instance('Version')

    def render_entity_relations(self, entity):
        if entity.conflicts:
            self.w(u"<div class='entityDescr'><b>%s</b>:<ul>"
              % display_name(self._cw, 'conflicts', context='Version'))
            vid = len(entity.conflicts) > 1 and 'list' or 'outofcontext'
            self.wview(vid, entity.related('conflicts'))
            self.w(u'</ul></div>')
        super(VersionPrimaryTab, self).render_entity_relations(entity)


class VersionTicketsTab(EntityView):
    __regid__ = 'tracker.version.tickets_tab'
    __select__ = is_instance('Version')

    def cell_call(self, row, col):
        entity = self.cw_rset.get_entity(row, col)
        rset = self._cw.execute(*attr_tuple(entity, 'tickets_rql'))
        nbcol = entity.tickets_rql_nb_displayed_cols
        self._cw.view('table', rset, 'noresult', subvid='incontext',
                      displaycols=range(nbcol), displayfilter=1,
                      displayactions=1, w=self.w)


class VersionDefectsTab(EntityView):
    __regid__ = 'tracker.version.defects_tab'
    __select__ = (is_instance('Version')
                  & score_entity(lambda x: x.is_published()))

    def cell_call(self, row, col):
        entity = self.cw_rset.get_entity(row, col)
        rset = self._cw.execute(*attr_tuple(entity, 'defects_rql'))
        nbcol = entity.defects_rql_nb_displayed_cols
        self._cw.view('table', rset, 'noresult', subvid='incontext',
                      displaycols=range(nbcol), displayfilter=1,
                      displayactions=1, w=self.w)


# ui adapters ##################################################################

class VersionIBreadCrumbsAdapter(ibreadcrumbs.IBreadCrumbsAdapter):
    __select__ = is_instance('Version')

    def parent_entity(self):
        return self.entity.project


class VersionIPrevNextAdapter(navigation.IPrevNextAdapter):
    __select__ = is_instance('Version')

    def previous_entity(self):
        found = False
        for version in self.entity.project.reverse_version_of:
            if found:
                return version
            if version is self.entity:
                found = True

    def next_entity(self):
        return self.entity.next_version(states=None)


class VersionICalendarableAdapter(EntityAdapter):
    __regid__ = 'ICalendarable'
    __select__ = is_instance('Version')

    @property
    def start(self):
        return self.entity.start_date() or self.entity.starting_date or date.today()

    @property
    def stop(self):
        return self.entity.stop_date() or self.entity.prevision_date or date.today()


class VersionICalendarViewsAdapter(EntityAdapter):
    __regid__ = 'ICalendarViews'
    __select__ = is_instance('Version')

    def matching_dates(self, begin, end):
        """return prevision or publication date according to state"""
        if self.entity.in_state[0].name in self.entity.PUBLISHED_STATES:
            if self.entity.publication_date:
                return [self.entity.publication_date]
        elif self.entity.prevision_date:
            return [self.entity.prevision_date]
        return []


# pluggable sections ###########################################################

class VersionProgressTableComponent(component.EntityCtxComponent):
    """display version information table in the context of the project"""
    __regid__ = 'versioninfo'
    __select__ = (component.EntityCtxComponent.__select__
                  & is_instance('Version')
                  & score_entity(lambda x: not x.is_published()))
    context = 'navcontenttop'
    order = 10

    def render_body(self, w):
        view = self._cw.vreg['views'].select('progress_table_view', self._cw,
                                             rset=self.entity.as_rset())
        columns = list(view.columns)
        for col in ('project', 'milestone'):
            try:
                columns.remove(col)
            except ValueError:
                self.warning('could not remove %s from columns' % col)
        view.render(w=w, columns=columns)


# secondary views ##############################################################

class VersionTextView(baseviews.TextView):
    __select__ = is_instance('Version')

    def cell_call(self, row, col):
        entity = self.cw_rset.get_entity(row, col)
        self.w(entity.num)
        self.w(u' [%s]' % self._cw._(entity.cw_adapt_to('IWorkflowable').state))


class VersionIncontextView(baseviews.InContextView):
    __select__ = is_instance('Version')

    def cell_call(self, row, col):
        entity = self.cw_rset.get_entity(row, col)
        self.w(tags.a(entity.num, href=entity.absolute_url()))


class VersionOutOfContextView(baseviews.OutOfContextView):
    __select__ = is_instance('Version')

    def cell_call(self, row, col):
        entity = self.cw_rset.get_entity(row, col)
        if entity.version_of:
            project = entity.version_of[0]
            self.w(tags.a(project.name, href=project.absolute_url()))
        self.w(u'&nbsp;-&nbsp;')
        self.w(u'<a href="%s">' % xml_escape(entity.absolute_url()))
        self.wdata(entity.num)
        self.wdata(u' [%s]' % self._cw._(entity.cw_adapt_to('IWorkflowable').state))
        self.w(u'</a>')


# other views ##################################################################

class VersionProgressTableView(iprogress.ProgressTableView):
    __select__ = is_instance('Version')

    title = _('version progression')

    columns = (_('project'), _('milestone'), _('state'), _('planned_start'),
               _('planned_delivery'), _('depends_on'), _('todo_by'))

    def build_depends_on_cell(self, entity):
        vrset = entity.depends_on_rset()
        if vrset: # may be None
            vid = len(vrset) > 1 and 'list' or 'outofcontext'
            return self._cw.view(vid, vrset, 'null')
        return u''

    def build_planned_start_cell(self, entity):
        """``starting_date`` column cell renderer"""
        if entity.starting_date:
            return self._cw.format_date(entity.starting_date)
        return u''

    def build_planned_delivery_cell(self, entity):
        """``initial_prevision_date`` column cell renderer"""
        imilestone = entity.cw_adapt_to('IMileStone')
        if imilestone.finished():
            return self._cw.format_date(imilestone.completion_date())
        return self._cw.format_date(imilestone.initial_prevision_date())


class VersionsInfoView(StartupView):
    """display versions in state ready or development, or marked as prioritary.
    """
    __regid__ = 'versionsinfo'
    title = _('All current versions')

    def call(self, sort_col=None):
        rql = ('Any X,P,N,PN ORDERBY PN, version_sort_value(N) '
               'WHERE X num N, X version_of P, P name PN, '
               'EXISTS(X in_state S, S name IN ("dev", "ready")) ')
        rset = self._cw.execute(rql)
        self.wview('progress_table_view', rset, 'null')
        url = self._cw.build_url(rql='Any P,X ORDERBY PN, version_sort_value(N) '
                             'WHERE X num N, X version_of P, P name PN')
        self.w(u'<a href="%s">%s</a>\n'
               % (xml_escape(url), self._cw._('view all versions')))


class RssItemVersionView(xmlrss.RSSItemView):
    __select__ = is_instance('Version')

    def cell_call(self, row, col):
        entity = self.cw_rset.complete_entity(row, col)
        self.w(u'<item>\n')
        self.w(u'<guid isPermaLink="true">%s</guid>\n'
               % xml_escape(entity.absolute_url()))
        self.render_title_link(entity)
        self._marker('description', entity.dc_description(format='text/html'))
        self._marker('dc:date', entity.dc_date(self.date_format))
        self.render_user_in_charge(entity)
        self.w(u'</item>\n')

    def render_user_in_charge(self, entity):
        if entity.todo_by:
            for user in entity.todo_by:
                self._marker('dc:creator', user.name())


# actions ######################################################################

class VersionAddTicketAction(action.LinkToEntityAction):
    __regid__ = 'addticket'
    __select__ = (action.LinkToEntityAction.__select__ & is_instance('Version')
                  & score_entity(lambda x: not x.cw_adapt_to('IProgress').finished()))

    title = _('add Ticket done_in Version object')
    target_etype = 'Ticket'
    rtype = 'done_in'
    role = 'object'

    def url(self):
        baseurl = super(VersionAddTicketAction, self).url()
        entity = self.cw_rset.get_entity(0, 0)
        linkto = 'concerns:%s:subject' % (entity.version_of[0].eid)
        return '%s&__linkto=%s' % (baseurl, self._cw.url_quote(linkto))

class VersionSubmitBugAction(VersionAddTicketAction):
    __regid__ = 'submitbug'
    __select__ = (action.LinkToEntityAction.__select__ & is_instance('Version')
                  & score_entity(lambda x: x.cw_adapt_to('IWorkflowable').state in x.PUBLISHED_STATES))

    title = _('add Ticket appeared_in Version object')
    rtype = 'appeared_in'
    category = 'mainactions'

_abaa = uicfg.actionbox_appearsin_addmenu
_abaa.tag_object_of(('*', 'done_in', 'Version'), False)
_abaa.tag_object_of(('*', 'appeared_in', 'Version'), False)


# register messages generated for the form title until catalog generation is fixed
_('creating Ticket (Ticket done_in Version %(linkto)s)')
_('creating Ticket (Ticket appeared_in Version %(linkto)s)')
