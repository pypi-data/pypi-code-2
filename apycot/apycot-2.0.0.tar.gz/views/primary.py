"""this module contains the primary views for apycot entities

:organization: Logilab
:copyright: 2008-2010 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
:license: General Public License version 2 - http://www.gnu.org/licenses
"""
__docformat__ = "restructuredtext en"

from logilab.mtconverter import xml_escape
from logilab.common.tasksqueue import PRIORITY, MEDIUM

from cubicweb import Unauthorized, NoSelectableObject, tags
from cubicweb.selectors import (is_instance, has_related_entities, none_rset,
                                match_user_groups, match_kwargs, match_form_params,
                                score_entity)
from cubicweb.view import EntityView
from cubicweb.web import (Redirect, uicfg, component, box,
                          formfields as ff, formwidgets as fwdgs)
from cubicweb.web.views import primary, tabs, forms, baseviews, tableview
from cubicweb.web.views import ibreadcrumbs, idownloadable, navigation

from cubes.narval.logformat import log_to_html
from cubes.narval.views import no_robot_index, startplan
from cubes.apycot.views import anchor_name


_pvs = uicfg.primaryview_section
_pvdc = uicfg.primaryview_display_ctrl


class InfoLogMixin(object):

    def display_info_section(self, entity):
        rset = self._cw.execute(
            'Any X,T,L,V ORDERBY T,L WHERE X is CheckResultInfo, '
            'X type T, X label L, X value V, X for_check AE, AE eid %(ae)s',
            {'ae': entity.eid})
        title = self._cw._('execution information')
        self.wview('table', rset, 'null', title=title, displaycols=range(1, 4),
                   divid='info%s'%entity.eid)


class InheritedRelationView(EntityView):
    __regid__ = 'apycot.inherited'
    __select__ = match_kwargs('rtype')

    def cell_call(self, row, col, rtype, role):
        entity = self.cw_rset.get_entity(row, col)
        final = self._cw.vreg.schema.rschema(rtype).final
        owner, value = entity.owner_and_value(rtype, final)
        if owner is None:
            self.w(self._cw._('no value specified'))
        elif final:
            self.w(owner.printable_value(rtype))
        else:
            self.w(value.view('incontext'))
        if owner is not None and owner is not entity:
            self.w(self._cw._('inherited from %s')
                   % value.view('incontext'))


class InheritedConfigAttributeView(EntityView):
    __regid__ = 'apycot.inherited.config'
    __select__ = match_kwargs('rtype')

    def cell_call(self, row, col, rtype, role):
        prop = {'check_config': 'apycot_configuration',
                'check_environment': 'apycot_process_environment'}[rtype]
        entity = self.cw_rset.get_entity(row, col)
        parents = entity.config_parents()
        valdict = getattr(entity, prop)()
        owndict = getattr(entity, 'my_%s' % prop)
        values = []
        for key, val in valdict.items():
            if key in owndict:
                parent = ''
            else:
                for parent in parents:
                    gvaldict = getattr(parent, 'my_%s' % prop)
                    if key in gvaldict:
                        parent = parent.view('oneline')
                        break
                else:
                    parent = u'???'
            if isinstance(val, list):
                for val in val:
                    values.append( (xml_escape(key), xml_escape(val), parent) )
            else:
                values.append( (xml_escape(key), xml_escape(val), parent) )
        if valdict:
            #self.w(u'<h4>%s</h4>' % label)
            headers = (self._cw._('key'), self._cw._('value'),
                       self._cw._('inherited from'))
            self.wview('pyvaltable', pyvalue=sorted(values), headers=headers)
        else:
            self.w(self._cw._('no value specified'))
            #self.field(label, self._cw._('no value specified'), tr=False)

_pvs.tag_attribute(('*', 'check_config'), 'attributes')
_pvdc.tag_attribute(('*', 'check_config'), {'vid': 'apycot.inherited.config'})
_pvs.tag_attribute(('*', 'check_environment'), 'attributes')
_pvdc.tag_attribute(('*', 'check_environment'), {'vid': 'apycot.inherited.config'})

# ProjectEnvironment ###########################################################

# custom view displaying repository, dealing with inheritance
_pvs.tag_subject_of(('ProjectEnvironment', 'local_repository', '*'), 'attributes')
_pvdc.tag_subject_of(('ProjectEnvironment', 'local_repository', '*'),
                     {'vid': 'apycot.inherited', 'rtypevid': True})
# custom view displaying all test configurations (including inherited config)
_pvs.tag_object_of(('*', 'use_environment', 'ProjectEnvironment'), 'relations')
_pvdc.tag_object_of(('*', 'use_environment', 'ProjectEnvironment'),
                    {'vid': 'apycot.pe.tc', 'rtypevid': True, 'showlabel': False})
# viewing reverse dependencies, should use outofcontext view defined below
_pvdc.tag_object_of(('*', 'on_environment', '*'),
                    {'subvid': 'outofcontext'})
# though dependencies are in the test configuration table, don't show them in
# automatic generation
_pvs.tag_object_of(('*', 'for_environment', '*'), 'hidden')
# in title
_pvs.tag_attribute(('ProjectEnvironment', 'name'), 'hidden')
# in breadcrumb
_pvs.tag_object_of(('*', 'has_apycot_environment', 'ProjectEnvironment'), 'hidden')
# in tab
_pvs.tag_object_of(('*', 'using_environment', 'ProjectEnvironment'), 'hidden')

class ProjectEnvironmentPrimaryView(tabs.TabbedPrimaryView):
    __select__ = is_instance('ProjectEnvironment')

    tabs = [_('apycot.pe.tab_config'), 'narval.recipe.tab_executions']
    default_tab = 'apycot.pe.tab_config'

    html_headers = no_robot_index


class PEConfigTab(tabs.PrimaryTab):
    __regid__ = 'apycot.pe.tab_config'
    __select__ = is_instance('ProjectEnvironment')


class PEExecutionTab(EntityView):
    # must be named like this for proper redirection to this tab when a test is started
    __regid__ = 'narval.recipe.tab_executions'
    __select__ = (is_instance('ProjectEnvironment') &
                  has_related_entities('use_environment', 'object'))

    html_headers = no_robot_index

    def cell_call(self, row, col):
        rset = self._cw.execute(
            'Any T,TC,T,TB,TST,TET,TF, TS ORDERBY TST DESC WHERE '
            'T status TS, T using_config TC, T branch TB, '
            'T starttime TST, T endtime TET, T log_file TF?, '
            'TC use_environment PE, PE eid %(pe)s',
            {'pe': self.cw_rset[row][col]})
        self.wview('apycot.te.summarytable', rset, 'noresult', showpe=False)


class PETestConfigView(EntityView):
    __regid__ = 'apycot.pe.tc'
    __select__ = (is_instance('ProjectEnvironment')
                  & match_kwargs('rtype')
                  & score_entity(lambda x: x.all_configurations()))

    html_headers = no_robot_index

    def cell_call(self, row, col, rtype, role):
        assert rtype == 'use_environment' and role == 'object'
        self.w(u'<hr/>')
        pe = self.cw_rset.get_entity(row, col)
        self.w(u'<table class="projectEnvConfiguration">')
        self.w(u'<thead><tr><th>%s</th><th>%s</th><th>&#160;</th></tr></thead><tbody>'
               % (self._cw._('TestConfig'), self._cw._('TestDependency_plural')))
        for owner, tc in pe.all_configurations().values():
            self.w(u'<tr><td>')
            tc.view('oneline', w=self.w)
            if owner is not pe:
                self.w(u' (%s)' % self._cw._('inherited from %s') % value.view('incontext'))
            self.w(u'</td><td>')
            rset = tc.environment_dependencies_rset(pe)
            if rset:
                self.wview('csv', rset)
            else:
                self.w(u'&#160;')
            self.w(u'</td><td>')
            iwf = tc.cw_adapt_to('IWorkflowable')
            if iwf.state == 'activated':
                try:
                    form = self._cw.vreg['forms'].select('apycot.starttestform',
                                                         self._cw, entity=tc,
                                                         environment=pe)
                except NoSelectableObject:
                    self.w(u'&#160;')
                else:
                    self.w(form.render())
            else:
                self.w(iwf.printable_state)
            self.w(u'</td></tr>')
        self.w(u'</tbody></table>')


class PEIBreadCrumbsAdapter(ibreadcrumbs.IBreadCrumbsAdapter):
    __select__ = is_instance('ProjectEnvironment')
    def parent_entity(self):
        """hierarchy, used for breadcrumbs"""
        return self.entity.project


# TestConfig ##################################################

_pvdc.tag_attribute(('TestConfig', 'start_mode'),
                    {'vid': 'apycot.tc.startmode'})
_pvdc.tag_attribute(('TestConfig', 'start_rev_deps'),
                    {'vid': 'apycot.inherited'})
_pvs.tag_subject_of(('*', 'refinement_of', '*'), 'attributes')
_pvdc.tag_object_of(('*', 'refinement_of', '*'),
                    {'subvid': 'outofcontext'})
# custom view displaying repository, dealing with inheritance
_pvs.tag_subject_of(('TestConfig', 'use_recipe', '*'), 'attributes')
_pvdc.tag_subject_of(('TestConfig', 'use_recipe', '*'),
                     {'vid': 'apycot.inherited', 'rtypevid': True})
# in a tab
_pvs.tag_object_of(('*', 'using_config', 'TestConfig'), 'hidden')
# in title
_pvs.tag_attribute(('TestConfig', 'name'), 'hidden')
# handled py apycot.tc.startmode view
_pvs.tag_attribute(('TestConfig', 'computed_start_mode'), 'hidden')
#
_pvs.tag_object_of(('*', 'for_testconfig', 'TestConfig'), 'hidden')


class TCPrimaryView(tabs.TabbedPrimaryView):
    __select__ = is_instance('TestConfig')

    tabs = [_('apycot.tc.tab_config'), _('narval.recipe.tab_executions')]
    default_tab = 'apycot.tc.tab_config'

    html_headers = no_robot_index


class TCConfigTab(tabs.PrimaryTab):
    __select__ = is_instance('TestConfig')
    __regid__ = 'apycot.tc.tab_config'

    html_headers = no_robot_index


class TCExecutionTab(EntityView):
    __select__ = (is_instance('TestConfig') &
                  has_related_entities('using_config', 'object'))
    __regid__ = 'narval.recipe.tab_executions'

    html_headers = no_robot_index

    def cell_call(self, row, col):
        rset = self._cw.execute(
            'Any T,PE,T,TB,TST,TET,TF, TS ORDERBY TST DESC WHERE '
            'T status TS, T using_config TC, T using_environment PE, '
            'T branch TB, T starttime TST, T endtime TET, T log_file TF?, '
            'TC eid %(tc)s',
            {'tc': self.cw_rset[row][col]})
        self.wview('apycot.tc.te.summarytable', rset, 'noresult')


class TCStartModeView(EntityView):
    __regid__ = 'apycot.tc.startmode'
    __select__ = is_instance('TestConfig') & match_kwargs('rtype')

    def cell_call(self, row, col, rtype, role):
        assert rtype == 'start_mode'
        tconfig = self.cw_rset.get_entity(row, col)
        self.w(tconfig.printable_value('computed_start_mode'))
        if tconfig.start_mode == 'inherited':
            self.w(self._cw._(' (inherited)'))

class TCTESummaryTable(tableview.TableView):
    __select__ = is_instance('TestExecution')
    __regid__ = 'apycot.tc.te.summarytable'

    html_headers = no_robot_index

    def call(self):
        self._cw.add_css('cubes.apycot.css')
        _ = self._cw._
        super(TCTESummaryTable, self).call(
            displayfilter=True, paginate=True,
            headers=[_('TestExecution'), _('ProjectEnvironment'),
                     _('failures'), _('branch'),
                     _('starttime'), _('endtime'), _('archive')],
            cellvids={0: 'apycot.te.statuscell',
                      2: 'apycot.te.summarycell',
                      6: 'icon'})


def available_branches(form, field):
    tc = form.edited_entity
    environment = form.cw_extra_kwargs['environment']
    # if branch specified on the environment, don't let other choices
    envcfg = environment.apycot_configuration()
    if envcfg.get('branch'):
        return [envcfg['branch']]
    if environment.repository:
        return environment.repository.branches()
    return [tc.apycot_configuration().get('branch')]

def default_branch(form):
    tc = form.edited_entity
    environment = form.cw_extra_kwargs['environment']
    cfg = tc.apycot_configuration(environment)
    if cfg.get('branch'):
        return cfg['branch']
    if environment.repository:
        return environment.repository.default_branch()
    return None

class TCStartForm(forms.EntityFieldsForm):
    __regid__ = 'apycot.starttestform'
    __select__ = (match_user_groups('managers', 'staff')
                  & match_kwargs('environment')
                  & is_instance('TestConfig')
                  & score_entity(lambda x: x.recipe and x.recipe.may_be_started()))

    form_renderer_id = 'htable'
    form_buttons = [fwdgs.SubmitButton(label=_('start test'))]
    @property
    def action(self):
        return self.edited_entity.absolute_url(vid='narval.startplan')

    using_environment = ff.StringField(widget=fwdgs.HiddenInput(),
                                       value=lambda form: form.cw_extra_kwargs['environment'].eid)
    branch = ff.StringField(choices=available_branches, label=_('vcs_branch'),
                            value=default_branch)
    startrevdeps = ff.BooleanField(label=_('start_rev_deps'),
                                   value=lambda form: form.edited_entity.start_reverse_dependencies and '1' or '')
    archivetestdir = ff.BooleanField(label=_('archivetestdir'), value='')
    priority = ff.IntField(choices=[(label, str(val))
                                    for label, val in PRIORITY.items()],
                           value=str(MEDIUM),
                           label=_('execution priority'),
                           sort=False, internationalizable=True)


class StartTestView(startplan.StartPlanView):
    __select__ = (match_user_groups('managers', 'staff') & is_instance('TestConfig')
                  & match_form_params('using_environment')
                  & score_entity(lambda x: x.recipe and x.recipe.may_be_started()))

    def cell_call(self, row, col, priority=MEDIUM):
        testconfig = self.cw_rset.get_entity(row, col)
        testconfig.start(
            self._cw.entity_from_eid(self._cw.form['using_environment']),
            priority=int(priority), branch=self._cw.form.get('branch'),
            start_rev_deps=bool(self._cw.form.get('startrevdeps')),
            archive=bool(self._cw.form.get('archivetestdir')),
            check_duplicate=False)


# TestExecution ################################################################

class TESummaryTable(tableview.TableView):
    __regid__ = 'apycot.te.summarytable'
    __select__ = is_instance('TestExecution') | none_rset()

    html_headers = no_robot_index
    title = _('Apycot executions')
    category = 'startupview'

    def call(self, showpe=True):
        self._cw.add_css('cubes.apycot.css')
        _ = self._cw._
        if self.cw_rset is None:
            assert showpe
            self.cw_rset = self._cw.execute(
                'Any T,PE,TC,T,TB,TST,TET,TF, TS ORDERBY TST DESC WHERE '
                'T status TS, T using_config TC, TC use_environment PE, '
                'T branch TB, T starttime TST, T endtime TET, T log_file TF?')
            self.w('<h1>%s</h1>' % _(self.title))
        if showpe:
            headers = [_('TestExecution'), _('ProjectEnvironment'), _('TestConfig'),
                       _('checks'), _('branch'),
                       _('starttime'), _('endtime'), _('archive')]
            cellvids = {0: 'apycot.te.statuscell',
                        3: 'apycot.te.summarycell',
                        7: 'icon'}
        else:
            headers = [_('TestExecution'), _('TestConfig'),
                       _('checks'), _('branch'),
                       _('starttime'), _('endtime'), _('archive')]
            cellvids = {0: 'apycot.te.statuscell',
                        2: 'apycot.te.summarycell',
                        6: 'icon'}
        super(TESummaryTable, self).call(displayfilter=True, paginate=True,
                                         headers=headers, cellvids=cellvids)


_pvdc.tag_attribute(('TestExecution', 'priority',), {'vid': 'tasksqueue.priority'}) # XXX rtag inheritance bug
_pvs.tag_attribute(('TestExecution', 'execution_log'), 'relations')
_pvdc.tag_attribute(('TestExecution', 'execution_log'), {'vid': 'narval.formated_log'})
_pvs.tag_attribute(('TestExecution', 'log'), 'relations')
_pvdc.tag_attribute(('TestExecution', 'log'), {'vid': 'narval.formated_log'})
_pvs.tag_subject_of(('TestExecution', 'using_revision', '*'), 'hidden')
_pvs.tag_subject_of(('TestExecution', 'using_config', '*'), 'hidden')
_pvs.tag_subject_of(('TestExecution', 'log_file', '*'), 'hidden')
_pvs.tag_subject_of(('TestExecution', 'execution_of', '*'), 'hidden')
_pvs.tag_object_of(('*', 'during_execution', 'TestExecution'), 'hidden')


class TestExecutionPrimaryView(tabs.TabbedPrimaryView):
    __select__ = is_instance('TestExecution')

    default_tab = 'apycot.te.tab_setup'

    html_headers = no_robot_index

    @property
    def tabs(self):
        tabs = ['apycot.te.tab_setup']
        entity = self.cw_rset.get_entity(self.cw_row or 0, self.cw_col or 0)
        for check in entity.reverse_during_execution:#configuration.all_checks:
            label = u'%s [<b class="status_%s">%s</b>]' % (
                xml_escape(check.name), check.status, self._cw._(check.status))
            tabs.append((anchor_name(check.name),
                         {'vid': 'apycot.te.checkresult', 'label': label,
                          'rset': check.as_rset()}))
        return tabs

    def render_entity_title(self, entity):
        self._cw.add_css('cubes.apycot.css')
        title = self._cw._('Execution of %(pe)s/%(config)s#%(branch)s') % {
            'config': entity.configuration.view('outofcontext'),
            'pe':     entity.environment.view('outofcontext'),
            'branch': entity.branch and xml_escape(entity.branch)}
        self.w('<h1>%s</h1>' % title)


class TEConfigTab(InfoLogMixin, tabs.PrimaryTab):
    __regid__ = _('apycot.te.tab_setup')
    __select__ = is_instance('TestExecution')

    html_headers = no_robot_index

    def display_version_configuration(self, entity):
        title = self._cw._('version configuration')
        try:
            rset = self._cw.execute(
                'Any R, REV, B ORDERBY RN '
                'WHERE TE using_revision REV, TE eid %(te)s, '
                'REV from_repository R, REV branch B, R path RN',
                {'te': entity.eid})
        except Unauthorized:
            return # user can't read repositories for instance
        self.wview('table', rset, 'null', title=title, divid='vc%s'%entity.eid)

    def render_entity_relations(self, entity):
        self.display_version_configuration(entity)
        self.display_info_section(entity)
        super(TEConfigTab, self).render_entity_relations(entity)


class TECheckResultsTab(InfoLogMixin, tabs.PrimaryTab):
    __regid__ = 'apycot.te.checkresult'
    __select__ = is_instance('CheckResult')

    html_headers = no_robot_index

    def render_entity_relations(self, entity):
        self.display_info_section(entity)
        super(TECheckResultsTab, self).render_entity_relations(entity)


class TEBreadCrumbTextView(ibreadcrumbs.BreadCrumbTextView):
    __select__ = is_instance('TestExecution')
    def cell_call(self, row, col):
        entity = self.cw_rset.get_entity(row, col)
        self.w(entity.printable_value('starttime'))


class TEStatusCell(tabs.PrimaryTab):
    __select__ = is_instance('TestExecution')
    __regid__ = 'apycot.te.statuscell'
    def cell_call(self, row, col):
        entity = self.cw_rset.get_entity(row, col)
        self.w(tags.a(entity.status, href=entity.absolute_url(),
                      klass="global status_%s" % entity.status,
                      title=self._cw._('see detailed execution report')))

class TESummaryCell(tabs.PrimaryTab):
    __select__ = is_instance('TestExecution')
    __regid__ = 'apycot.te.summarycell'
    def cell_call(self, row, col):
        entity = self.cw_rset.get_entity(row, col)
        checks = []
        for check in entity.reverse_during_execution:
            if check.status == 'success':
                continue
            content = u'%s (%s)' % (self._cw._(check.name), check.status)
            url = entity.absolute_url(tab=anchor_name(check.name))
            title = self._cw._('see execution report for %s') % check.name
            checks.append(tags.a(content, href=url, title=title))
        if checks:
            self.w(u', '.join(checks))


class TEDownloadBox(box.EntityBoxTemplate):
    __regid__ = 'apycot.te.download_box'
    __select__ = (box.EntityBoxTemplate.__select__ & is_instance('TestExecution') &
                  score_entity(lambda x: x.log_file))

    def cell_call(self, row, col, **kwargs):
        archive = self.cw_rset.get_entity(row, col).log_file[0]
        idownloadable.download_box(self.w, archive,
                                   self._cw._('download execution environment'))


class TEIBreadCrumbsAdapter(ibreadcrumbs.IBreadCrumbsAdapter):
    __select__ = is_instance('TestExecution')

    def parent_entity(self):
        """hierarchy, used for breadcrumbs"""
        try:
            return self.entity.environment
        except IndexError: # XXX bw compat
            return self.entity.configuration

    def breadcrumbs(self, view=None, recurs=False):
        projectenv = self.parent_entity()
        breadcrumbs = projectenv.cw_adapt_to('IBreadCrumbs').breadcrumbs(view, True)
        if projectenv.__regid__ == 'ProjectEnvironment': # XXX bw compat
            breadcrumbs.append(self.entity.configuration)
        breadcrumbs.append(self.entity)
        return breadcrumbs


class TEIPrevNextAdapter(navigation.IPrevNextAdapter):
    __select__ = is_instance('TestExecution')

    def previous_entity(self):
        return self.entity.previous_execution()

    def next_entity(self):
        entity = self.entity
        rset = self._cw.execute(
            'Any X,C ORDERBY X ASC LIMIT 1 '
            'WHERE X is TestExecution, X using_config C, C eid %(c)s, '
            'X branch %(branch)s, X eid > %(x)s',
            {'x': entity.eid, 'c': entity.configuration.eid,
             'branch': entity.branch})
        if rset:
            return rset.get_entity(0, 0)


# CheckResult ##################################################################

_pvs.tag_attribute(('CheckResult', 'name'), 'hidden')
_pvs.tag_attribute(('CheckResult', 'status'), 'hidden')
_pvs.tag_attribute(('CheckResult', 'log'), 'relations')
_pvdc.tag_attribute(('CheckResult', 'log'), {'vid': 'narval.formated_log'})
_pvs.tag_subject_of(('CheckResult', 'during_execution', '*'), 'hidden')
_pvs.tag_object_of(('*', 'for_check', '*'), 'hidden')


class CRPrimaryView(TECheckResultsTab):
    __regid__ = 'primary'
    __select__ = is_instance('CheckResult')

    html_headers = no_robot_index

    def render_entity_title(self, entity):
        self._cw.add_css('cubes.apycot.css')
        self.w('<h4 id="%s" >%s [<span class="status_%s">%s</span>]</h4>'
               % (anchor_name(entity.name),
                  xml_escape(entity.name), entity.status, entity.status))



class CRIBreadCrumbsAdapter(ibreadcrumbs.IBreadCrumbsAdapter):
    __select__ = is_instance('CheckResult')

    def parent_entity(self):
        return self.entity.execution


class CRIPrevNextAdapter(navigation.IPrevNextAdapter):
    __select__ = is_instance('CheckResult')

    def previous_entity(self):
        previous_exec = self.entity.execution.cw_adapt_to('IPrevNext').previous_entity()
        if previous_exec:
            return previous_exec.check_result_by_name(self.entity.name)

    def next_entity(self):
        next_exec = self.entity.execution.cw_adapt_to('IPrevNext').next_entity()
        if next_exec:
            return next_exec.check_result_by_name(self.entity.name)


class CRIIBreadCrumbsAdapter(ibreadcrumbs.IBreadCrumbsAdapter):
    __select__ = is_instance('CheckResultInfo')

    def parent_entity(self):
        return self.entity.check_result


# TestDependency ###############################################################

class TestDependencyOutOfContextView(baseviews.OutOfContextView):
    __select__ = is_instance('TestDependency')
    def cell_call(self, row, col):
        entity = self.cw_rset.get_entity(row, col)
        entity.from_environment.view('oneline', w=self.w)
        self.w(' ')
        entity.configuration.view('oneline', w=self.w)
