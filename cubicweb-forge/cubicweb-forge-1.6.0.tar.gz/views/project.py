"""views for Project entities

:organization: Logilab
:copyright: 2006-2010 LOGILAB S.A. (Paris, FRANCE), license is LGPL.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
"""
__docformat__ = "restructuredtext en"
_ = unicode

from logilab.mtconverter import xml_escape

from cubicweb.selectors import one_line_rset, score_entity, is_instance
from cubicweb.view import EntityView
from cubicweb import tags, uilib
from cubicweb.web import uicfg, action
from cubicweb.web.views import primary, tabs, baseviews

from cubes.tracker.views import project as tracker

from cubes.testcard import views as testcard

tracker.ProjectStatsView.default_rql = (
    'Any P, PN WHERE P is Project, P name PN, '
    'P in_state S, S name "active development"')

# primary view and tabs ########################################################

class ExtProjectPrimaryView(primary.PrimaryView):
    __select__ = is_instance('ExtProject')
    show_attr_label = False

    def render_entity_title(self, entity):
        title = u'<a href="%s">%s</a>' % (xml_escape(entity.homepage),
                                          xml_escape(entity.name))
        self.w(u'<h1><span class="etype">%s</span> %s</h1>'
               % (entity.dc_type().capitalize(), title))

tracker.ProjectPrimaryView.tabs +=  [
    _('documentation_tab'), _('screenshots_tab'),
    _('codebrowser_tab')]


_pvs = uicfg.primaryview_section
_pvs.tag_attribute(('Project', 'downloadurl'), 'hidden')
_pvs.tag_subject_of(('Project', 'recommends', '*'), 'attributes')
_pvs.tag_object_of(('Project', 'recommends', '*'), 'hidden')
_pvs.tag_object_of(('*', 'license_of', 'Project'), 'attributes')
_pvs.tag_object_of(('*', 'mailinglist_of', 'Project'), 'attributes')
_pvs.tag_subject_of(('*', 'documented_by', '*'), 'hidden')

_pvdc = uicfg.primaryview_display_ctrl
for attr in ('homepage', 'vcsurl', 'reporturl', 'downloadurl'):
    _pvdc.tag_attribute(('Project', attr), {'vid': 'urlattr'})


# XXX cleanup or explain View/Tab duality

class ProjectDocumentationView(tabs.EntityRelationView):
    """display project's documentation"""
    __regid__ = title = _('projectdocumentation')
    __select__ = tabs.EntityRelationView.__select__ & is_instance('Project')
    rtype = 'documented_by'
    target = 'object'

class ProjectDocumentationTab(ProjectDocumentationView):
    __regid__ = 'documentation_tab'
    title = None # should not appears in possible views
    __select__ = ProjectDocumentationView.__select__ & one_line_rset()


class ProjectScreenshotsView(tabs.EntityRelationView):
    """display project's screenshots"""
    __regid__ = title = _('projectscreenshots')
    __select__ = tabs.EntityRelationView.__select__ & is_instance('Project')
    rtype = 'screenshot'
    target = 'object'
    vid = 'gallery'

class ProjectScreenshotsTab(ProjectScreenshotsView):
    __regid__ = 'screenshots_tab'
    __select__ = tabs.EntityRelationView.__select__ & is_instance('Project')
    title = None # should not appears in possible views

class ProjectBrowseTab(EntityView):
    __regid__ = 'codebrowser_tab'
    __select__ = is_instance('Project') & score_entity(lambda x: x.vcsurl)
    title = None # should not appears in possible views

    def cell_call(self, row, col):
        entity = self.cw_rset.get_entity(row, col)
        # XXX browse sub-tab
        # XXX may not be an hg repo
        w = self.w
        _ = self._cw._
        w(u'<h4>%s</h4>' % _('Browse source'))
        w(u'<p>%s</p>' % _('You can browse the source code by following <a href="%s">this link</a>.')
          % xml_escape(entity.vcsurl))
        w(u'<h4>%s</h4>' % _('Command-Line Access'))
        w(u'<p>%s</p>' % _('Use this command to check out the latest project source code:'))
        w(u'<br/><pre>')
        w(u'# %s' % _('Non-members may check out a read-only working copy anonymously over HTTP.'))
        w(u'<br/>')
        w(u'hg clone %s' % xml_escape(entity.vcsurl))
        w(u'</pre>')


# secondary views ##############################################################

class ExtProjectOutOfContextView(baseviews.OutOfContextView):
    """project's secondary view display project's url, which is not
    displayed in the one line / text views
    """
    __select__ = is_instance('ExtProject')

    def cell_call(self, row, col):
        entity = self.cw_rset.get_entity(row, col)
        self.w(u'&nbsp;')
        self.w(tags.a(entity.name, href=entity.absolute_url()))
        if getattr(entity, 'homepage', None):
            self.w(u'&nbsp;')
            self.w(tags.a(entity.homepage, href=entity.homepage))


class ProjectTextView(baseviews.TextView):
    __select__ = is_instance('Project')

    def cell_call(self, row, col):
        """ text_view representation of a project """
        entity = self.cw_rset.get_entity(row, col)
        self.w(entity.name)
        state = entity.cw_adapt_to('IWorkflowable').state
        if state != 'active development':
            self.w(u' [%s]' % self._cw._(state))


class ProjectOutOfContextView(tracker.ProjectOutOfContextView):
    """project's secondary view display project's url, which is not
    displayed in the one line / text views
    """
    __select__ = is_instance('Project')

    def cell_call(self, row, col):
        entity = self.cw_rset.get_entity(row, col)
        self.w(tags.a(entity.name, href=entity.absolute_url()))
        if getattr(entity, 'homepage', None):
            self.w(u'&nbsp;')
            self.w(tags.a(entity.homepage, href=entity.homepage))
        # no summary on ext project
        if getattr(entity, 'summary', None):
            self.w(u'&nbsp;')
            self.w(xml_escape(entity.summary))

# Project actions #############################################################

class ProjectTestReportsAction(action.Action):
    __regid__ = 'testreports'
    __select__ = is_instance('Project') & score_entity(lambda x: x.reporturl)

    title = _('test reports')
    order = 220
    def url(self):
        entity = self.cw_rset.get_entity(0, 0)
        rql = uilib.rql_for_eid(entity.eid)
        return self._cw.build_url('embed', rql=rql, url=entity.reporturl,
                              vtitle=self._cw._(self.title))

class ProjectAddRelatedAction(action.LinkToEntityAction):
    __select__ = (action.LinkToEntityAction.__select__ & is_instance('Project')
                  & score_entity(lambda x: x.cw_adapt_to('IWorkflowable').state != 'moved'))

class ProjectAddTicket(ProjectAddRelatedAction):
    __regid__ = 'addticket'
    rtype = 'concerns'
    role = 'object'
    target_etype = 'Ticket'
    title = _('add Ticket concerns Project object')
    order = 110

class ProjectAddVersion(ProjectAddRelatedAction):
    __regid__ = 'addversion'
    rtype = 'version_of'
    role = 'object'
    target_etype = 'Version'
    title = _('add Version version_of Project object')
    order = 112

class ProjectAddDocumentationCard(ProjectAddRelatedAction):
    __regid__ = 'adddocumentationcard'
    rtype = 'documented_by'
    role = 'subject'
    target_etype = 'Card'
    title = _('add Project documented_by Card subject')
    order = 120

class ProjectAddDocumentationFile(ProjectAddRelatedAction):
    __regid__ = 'adddocumentationfile'
    rtype = 'documented_by'
    role = 'subject'
    target_etype = 'File'
    title = _('add Project documented_by File subject')
    order = 121

class ProjectAddScreenshot(ProjectAddRelatedAction):
    __regid__ = 'addscreenshot'
    rtype = 'screenshot'
    role = 'subject'
    target_etype = 'File'
    title = _('add Project screenshot File subject')
    order = 122

class ProjectAddSubProject(ProjectAddRelatedAction):
    __regid__ = 'addsubproject'
    rtype = 'subproject_of'
    role = 'object'
    target_etype = 'Project'
    title = _('add Project subproject_of Project object')
    order = 130


class ProjectAddTestCard(testcard.ProjectAddTestCard):
    __select__ = ProjectAddRelatedAction.__select__

# register messages generated for the form title until catalog generation is fixed
# some are missing because they are defined in tracker
_('creating Card (Project %(linkto)s) documented_by Card')
_('creating File (Project %(linkto)s) documented_by File')
_('creating File (Project %(linkto)s) screenshot File')

_abaa = uicfg.actionbox_appearsin_addmenu
for cls in ProjectAddRelatedAction.__subclasses__():
    if cls.role == 'object':
        _abaa.tag_object_of(('*', cls.rtype, 'Project'), False)
    else:
        _abaa.tag_subject_of(('Project', cls.rtype, '*'), False)

# del cls local identifier else ProjectAddVersion is referenced twice and it
# triggers a registration error
del cls

def registration_callback(vreg):
    vreg.register_all(globals().values(), __name__,
                      (ProjectOutOfContextView, ProjectAddTestCard))
    vreg.register_and_replace(ProjectOutOfContextView, tracker.ProjectOutOfContextView)
    vreg.register_and_replace(ProjectAddTestCard, testcard.ProjectAddTestCard)
