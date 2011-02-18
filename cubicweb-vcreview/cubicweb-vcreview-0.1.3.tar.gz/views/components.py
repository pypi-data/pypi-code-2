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
"""cubicweb-vcreview components (boxes, pluggable sections)"""

__docformat__ = "restructuredtext en"
_ = unicode

from logilab.mtconverter import xml_escape

from cubicweb.selectors import (is_instance, relation_possible,
                                score_entity, match_form_params)
from cubicweb.view import EntityView
from cubicweb.uilib import js
from cubicweb.web import uicfg, component, form, formwidgets as wdg
from cubicweb.web.views import workflow, idownloadable, ajaxedit

from cubes.comment import views as comment


_afs = uicfg.autoform_section
_affk = uicfg.autoform_field_kwargs
_abaa = uicfg.actionbox_appearsin_addmenu
_pvs = uicfg.primaryview_section


idownloadable.DownloadBox.__select__ &= ~(
    is_instance('VersionContent') & score_entity(lambda x: x.patch))


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
                    formvalues=formvalues)
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
