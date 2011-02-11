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
"""cubicweb-vcreview views/forms/actions/components for web ui"""
__docformat__ = "restructuredtext en"
_ = unicode

from logilab.common.decorators import cached
from logilab.mtconverter import xml_escape

from cubicweb.selectors import (score_entity, is_instance, relation_possible,
                                match_form_params)
from cubicweb.view import EntityView, StartupView
from cubicweb.uilib import js, domid
from cubicweb.utils import json_dumps
from cubicweb.web import stdmsgs, uicfg, component, form, formwidgets as wdg
from cubicweb.web.views import (primary, workflow, ibreadcrumbs, idownloadable,
                                ajaxedit)

from cubes.vcsfile.views import primary as vcsfile
from cubes.comment import views as comment


_afs = uicfg.autoform_section
_affk = uicfg.autoform_field_kwargs
_abaa = uicfg.actionbox_appearsin_addmenu
_pvs = uicfg.primaryview_section

# primary views ################################################################

_pvs.tag_subject_of(('Patch', 'patch_repository', '*'), 'hidden') # in title
_pvs.tag_subject_of(('Patch', 'patch_revision', '*'), 'hidden') # table in attributes

class PatchPrimaryView(primary.PrimaryView):
    __select__ = primary.PrimaryView.__select__ & is_instance('Patch')

    def render_entity_title(self, entity):
        self.w(u'<h1>%s (%s)</h1>' % (xml_escape(entity.dc_title()),
                                      entity.repository.view('oneline')))

    def render_entity_attributes(self, entity):
        super(PatchPrimaryView, self).render_entity_attributes(entity)
        self.w(u'<div class="componentTitle">%s</div>' % self._cw._('Patch revisions'))
        rset = self._cw.execute('Any VC, RA, RB, RC, RD ORDERBY RC DESC '
                                'WHERE X patch_revision VC, VC from_revision R,'
                                'R author RA, R branch RB, R description RD, '
                                'R creation_date RC, X eid %(x)s', {'x': entity.eid})
        self.wview('table', rset)


_pvs.tag_object_of(('*', 'patch_revision', '*'), 'hidden') # in breadcrumbs
# ease change of detected mime type for version content for patches without
# .diff extension
_afs.tag_attribute(('VersionContent', 'data_format'), 'main', 'attributes')
_afs.tag_attribute(('VersionContent', 'data_encoding'), 'main', 'attributes')

class VCPrimaryView(vcsfile.VCPrimaryView):
    __select__ = (vcsfile.VCPrimaryView.__select__
                  & score_entity(lambda x: x.patch))

    def render_entity_attributes(self, entity):
        # XXX have to call primary.PrimaryView directly to avoid duplicated display
        # of version's content
        primary.PrimaryView.render_entity_attributes(self, entity)
        self.w(u'<div class="content">')
        adapter = entity.cw_adapt_to('IDownloadable')
        contenttype = adapter.download_content_type()
        targetmt = self._cw.form.get('nocomment') and 'text/html' or 'text/annotated-html'
        if not self.render_data(entity, contenttype, targetmt) and targetmt != 'text/html':
            self.render_data(entity, contenttype, 'text/html')
        self.w(u'</div>')

idownloadable.DownloadBox.__select__ &= ~(
    is_instance('VersionContent') & score_entity(lambda x: x.patch))

_abaa.tag_subject_of(('Repository', 'has_patch_repository', '*'), True)

def repo_patches_rql(is_patch_repo):
    rql = ('Any P,PS,COUNT(VC) GROUPBY P,PS WHERE P in_state PS, '
           'P patch_revision VC, P patch_repository R'
           )
    if is_patch_repo:
        rql += ', R eid %(x)s'
    else:
        rql += ', X has_patch_repository R, X eid %(x)s'
    return rql


class RepositoryPatchesTab(EntityView):
    __regid__ = _('vcreview.repositorypatches_tab')
    __select__ = is_instance('Repository') & score_entity(
        lambda x: x.patchrepo or x.patchrepo_of)

    def entity_call(self, entity):
        rql = repo_patches_rql(entity.patchrepo_of)
        linktitle = self._cw._('Patches for %s') % entity.dc_title()
        linkurl = self._cw.build_url(rql=rql % {'x': entity.eid},
                                     vtitle=linktitle)
        self.w('<p>%s. <a href="%s">%s</a></p>' % (
            self._cw._('Table below only show active patches'),
            xml_escape(linkurl), self._cw._('Show all patches')))
        rql += ', PS name IN ("in-progress", "pending-review")'
        rset = self._cw.execute(rql, {'x': entity.eid})
        self.wview('table', rset, 'noresult', paginate=True, displayfilter=True)

vcsfile.RepositoryPrimaryView.tabs.append(RepositoryPatchesTab.__regid__)


# insertion point handling #####################################################

_pvs.tag_object_of(('InsertionPoint', 'point_of', '*'), 'hidden')
_abaa.tag_object_of(('InsertionPoint', 'point_of', '*'), False)
_affk.tag_attribute(('InsertionPoint', 'id'),
                    {'widget': wdg.HiddenInput})
_affk.tag_subject_of(('InsertionPoint', 'point_of', '*'),
                     {'widget': wdg.HiddenInput})



# activities ###################################################################

_pvs.tag_subject_of(('*', 'has_activity', '*'), 'hidden') # component
_affk.tag_object_of(('*', 'has_activity', 'Task'),
                    {'widget': wdg.HiddenInput})


class AddActivityFormView(form.FormViewMixIn, EntityView):
    __regid__ = 'vcreview.addactivityform'
    __select__ = (relation_possible('has_activity', 'subject', 'Task', 'add')
                  | match_form_params('etype'))

    def call(self, **kwargs):
        if self.cw_rset is None:
            entity = self._cw.vreg['etypes'].etype_class(self._cw.form['etype'])(self._cw)
            entity.eid = self._cw.form['tempEid']
            self.entity_call(entity)
        else:
            super(AddActivityFormView, self).call(**kwargs)

    def entity_call(self, container):
        self._cw.add_js(('cubicweb.edition.js', 'cubes.vcreview.js'))
        activity = self._cw.vreg['etypes'].etype_class('Task')(self._cw)
        activity.eid = self._cw.varmaker.next()
        okjs = js.addActivity(container.eid, not container.has_eid(),
                              self.cw_extra_kwargs.get('context'))
        canceljs = "jQuery('#activity%sSlot').remove()" % container.eid
        form, formvalues = ajaxedit.ajax_composite_form(
            container, activity, 'has_activity', okjs, canceljs,
            dict(display_fields=(('title', 'subject'),
                                 ('description', 'subject'),
                                 ('has_activity', 'object'))))
        self.w(u'<div id="activity%sSlot">' % container.eid)
        form.render(w=self.w, main_form_title=u'', display_label=False,
                    formvalues={'has_activity': container.eid})
        self.w(u'</div>')


class ActivityComponent(component.EntityCtxComponent):
    """a component to display an html section displaying activities related to
    an object
    """
    __regid__ = 'vcreview.activitysection'
    __select__ = (component.EntityCtxComponent.__select__
                  & relation_possible('has_activity', 'subject', 'Task'))

    context = 'navcontentbottom'

    def render_body(self, w):
        req = self._cw
        req.add_js('cubicweb.ajax.js')
        if self.entity.has_eid():
            self.display_existing_tasks(w)
            eid = self.entity.eid
        else:
            eid = None
        rdef = self.entity.e_schema.rdef('has_activity', 'subject', 'Task')
        if (req.vreg.schema['Task'].has_perm(req, 'add') and
            rdef.has_perm(req, 'add', fromeid=eid)):
            url = self.lazy_view_holder(w, self.entity, 'vcreview.addactivityform')
            w(u'(<a href="%s">%s</a>)' % (xml_escape(url), req._('add a task')))

    existing_tasks_rql = (
        u'Any T,TD,TS,TCD,U,T, TT,TDF,UL,UF,US ORDERBY TCD DESC WHERE '
        'X has_activity T, T description TD, T in_state TS,'
        'T creation_date TCD, T created_by U?,'
        'T title TT, T description_format TDF, '
        'U login UL, U firstname UF, U surname US, X eid %(x)s')

    def display_existing_tasks(self, w):
        rset = self._cw.execute(self.existing_tasks_rql, {'x': self.entity.eid})
        if rset:
            w(u'<div class="componentTitle">%s</div>' % self._cw._('Activities'))
            self._cw.view('editable-table', rset, w=w,
                          headers=[self._cw.__('Task_plural'),
                                   self._cw._('detail'),
                                   self._cw.__('in_state'),
                                   self._cw.__('creation_date'),
                                   self._cw.__('created_by'),
                                   self._cw.__('todo_by'),],
                          cellvids={5: 'vcreview.task-todoers'})


class PatchActivityComponent(ActivityComponent):
    __select__ = ActivityComponent.__select__ & is_instance('Patch')
    existing_tasks_rql = (
        u'Any T,TD,TS,TCD,U,T, TT,TDF,UL,UF,US ORDERBY TCD DESC '
        'WITH T,TD,TS,TCD,U,TT,TDF,UL,UF,US BEING ('
        '(Any T,TD,TS,TCD,U,TT,TDF,UL,UF,US WHERE '
        'X has_activity T, T description TD, T in_state TS,'
        'T creation_date TCD, T created_by U?, '
        'T title TT, T description_format TDF, '
        'U login UL, U firstname UF, U surname US, X eid %(x)s)'
        ' UNION '
        '(Any T,TD,TS,TCD,U,TT,TDF,UL,UF,US WHERE '
        'X patch_revision VC, IP point_of VC, IP has_activity T, '
        'T description TD, T in_state TS, T creation_date TCD, '
        'T created_by U?, T title TT, T description_format TDF, '
        'U login UL, U firstname UF, U surname US, X eid %(x)s)'
        ')')


ActivityComponent.order = 10
workflow.WFHistoryVComponent.order = 20
comment.CommentSectionVComponent.order = 30

class TaskTodoersView(EntityView):
    __regid__ = 'vcreview.task-todoers'
    __select__ = is_instance('Task')

    def entity_call(self, entity):
        self.wview('csv', entity.related('todo_by'), 'null')


# breadcrumbs ##################################################################

class PatchIBreadCrumbsAdapter(ibreadcrumbs.IBreadCrumbsAdapter):
    __select__ = is_instance('Patch')

    def parent_entity(self):
        return self.entity.repository

class DVCIBreadCrumbsAdapter(ibreadcrumbs.IBreadCrumbsAdapter):
    __select__ = (is_instance('VersionContent', 'DeletedVersionContent')
                  & score_entity(lambda x: x.patch))

    def parent_entity(self):
        return self.entity.patch


# startup ######################################################################

class AllActivePatches(StartupView):
    __regid__ = 'vcreview.allactivepatches'
    title = _('All active patches')

    @cached
    def filter_box_context_info(self):
        rset = self._cw.execute(
            'Any P,PS,COUNT(VC),R GROUPBY R,P,PS ORDERBY R WHERE '
            'P patch_revision VC, P patch_repository R, '
            'P in_state PS, PS name IN ("in-progress", "pending-review")'
            )
        return rset, 'table', domid(self.__regid__), True

    def call(self):
        self.w(u'<h1>%s</h1>' % self._cw._(self.title))
        rset, vid, divid, paginate = self.filter_box_context_info()
        self.wview(vid, rset, 'noresult', paginate=paginate, divid=divid)


def registration_callback(vreg):
    vreg.register_all(globals().values(), __name__, (VCPrimaryView,))
    vreg.register_and_replace(VCPrimaryView, vcsfile.VCPrimaryView)

