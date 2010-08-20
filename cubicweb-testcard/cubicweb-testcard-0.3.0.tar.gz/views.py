"""cube-specific forms/views/actions/components

:organization: Logilab
:copyright: 2001-2009 LOGILAB S.A. (Paris, FRANCE), license is LGPL v2.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
:license: GNU Lesser General Public License, v2.1 - http://www.gnu.org/licenses
"""
from cubes.tracker.views import project as tracker

from cubicweb.web import uicfg, action
from cubicweb.web.views import primary, tabs, baseviews, navigation, ibreadcrumbs
from cubicweb.selectors import match_search_state, is_instance

_afs = uicfg.autoform_section
_afs.tag_object_of(('TestInstance', 'for_version', 'Version'), 'main', 'hidden')

_pvs = uicfg.primaryview_section
_pvs.tag_object_of(('TestInstance', 'instance_of', '*'), 'hidden')
_pvs.tag_object_of(('*', 'test_case_of', 'Project'), 'hidden')

_abaa = uicfg.actionbox_appearsin_addmenu
_abaa.tag_subject_of(('TestInstance', 'generate_bug', 'Ticket'), True)
_abaa.tag_subject_of(('TestInstance', 'instance_of', 'Card'), False)
_abaa.tag_object_of(('TestInstance', 'instance_of', 'Card'), False)
_abaa.tag_object_of(('TestInstance', 'for_version', 'Version'), False)
_abaa.tag_object_of(('TestInstance', 'filed_under', 'Folder'), False)
_abaa.tag_object_of(('Card', 'test_case_for', 'Ticket'), True)



class TestInstancePrimaryView(primary.PrimaryView):
    __select__ = is_instance('TestInstance')

    def render_entity_title(self, entity):
        title = xml_escape('%s [%s]' % (entity.name, self._cw._(entity.state)))
        self.w(u'<h1><span class="etype">%s</span> %s</h1>'
               % (entity.dc_type().capitalize(), title))

    def render_entity_metadata(self, entity):
        pass

    def render_entity_attributes(self, entity):
        self.w(entity.instance_of[0].view('inlined'))


class TestInstanceOneLineView(baseviews.OneLineView):
    """text representation of a test instance:

    display title and state
    """
    __select__ = is_instance('TestInstance')
    def cell_call(self, row, col):
        super(TestInstanceOneLineView, self).cell_call(row, col)
        entity = self.entity(row, col)
        self.wdata(u' [%s]' % self._cw._(entity.state))


class TestInstanceGenerateBugAction(action.LinkToEntityAction):
    __regid__ = 'submitbug'
    __select__ = match_search_state('normal') & is_instance('TestInstance')
    title = _('add TestCard generate_bug Ticket subject')
    target_etype = 'Ticket'
    rtype = 'generate_bug'
    role = 'subject'
    def url(self):
        entity = self.cw_rset.get_entity(0, 0)
        linkto = '__linkto=concerns:%s:object' % (entity.instance_of[0].test_case_of[0].eid)
        linkto += '&__linkto=generate_bug:%s:subject' % entity.eid
        linkto += '&__linkto=appeared_in:%s:object' % entity.for_version[0].eid
        return '%s&%s' % (action.LinkToEntityAction.url(self), linkto)

class ProjectTestCardsView(tabs.EntityRelationView):
    """display project's test cards"""
    __regid__ = title = _('projecttests')
    __select__ = tabs.EntityRelationView.__select__ & is_instance('Project')
    rtype = 'test_case_of'
    role = 'object'

class ProjectTestCardsTab(ProjectTestCardsView):
    __regid__ = 'testcards_tab'
    __select__ = tabs.EntityRelationView.__select__ & is_instance('Project')
    title = None # should not appears in possible views

if 'testcards_tab' not in tracker.ProjectPrimaryView.tabs:
    tracker.ProjectPrimaryView.tabs.append(_('testcards_tab'))

class ProjectAddTestCard(action.LinkToEntityAction):
    __select__ = (action.LinkToEntityAction.__select__ & is_instance('Project'))
    __regid__ = 'addtestcard'
    target_etype = 'Card'
    rtype = 'test_case_of'
    role = 'object'
    title = _('add Card test_case_of Project object')
    order = 123


# IPrevNext/IBreadCrumbs adapters ##############################################

class TestInstanceIPrevNextAdapter(navigation.IPrevNextAdapter):
    __select__ = is_instance('TestInstance')

    def previous_entity(self):
        entity = self.entity
        rset = self._cw.execute('TestInstance X ORDERBY X DESC LIMIT 1 WHERE '
                                'X for_version V, V eid %(v)s, X eid < %(x)s',
                                {'v': entity.version.eid, 'x': entity.eid})
        if rset:
            return rset.get_entity(0, 0)

    def next_entity(self):
        entity = self.entity
        rset = self._cw.execute('TestInstance X ORDERBY X ASC LIMIT 1 WHERE '
                                'X for_version V, V eid %(v)s, X eid > %(x)s',
                                {'v': entity.version.eid, 'x': entity.eid})
        if rset:
            return rset.get_entity(0, 0)


class TestInstanceIBreadCrumbsAdapter(ibreadcrumbs.IBreadCrumbsAdapter):
    __select__ = is_instance('TestInstance')

    def parent_entity(self):
        return self.entity.version

    def breadcrumbs(self, view=None, recurs=False):
        version = self.parent_entity()
        breadcrumbs = version.cw_adapt_to('IBreadCrumbs').breadcrumbs(view, True)
        url = '%s/%s' % (version.absolute_url(), 'tests')
        breadcrumbs += [(url, self._cw._('tests')), self]
        return breadcrumbs
