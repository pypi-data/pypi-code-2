"""primary views for entities used by the document cube

:organization: Logilab
:copyright: 2008-2010 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
"""
from __future__ import with_statement
__docformat__ = "restructuredtext en"
_ = unicode

from contextlib import contextmanager

from cubicweb import NoSelectableObject
from cubicweb.selectors import is_instance, score_entity
from cubicweb.web import uicfg
from cubicweb.web.views import tabs, primary

from cubes.folder import views as folderviews
from cubes.vcsfile.views import primary as vcsfileviews

from cubes.document.entities import req_branch_scope
from cubes.document.html import div, span, tr, td, table

_afs = uicfg.autoform_section
#_afs.tag_subject_of(('Folder', 'filed_under', '*'), False)
for relname in ('translation_of', 'filed_under', 'name', 'directory',
                'from_repository', 'content_for', 'might_edit'):
    _afs.tag_subject_of(('VersionedFile', relname, '*'), 'main', 'hidden')
_afs.tag_subject_of(('VersionedFile', 'lang', '*'), 'main', 'attributes')
_afs.tag_subject_of(('VersionedFile', 'filed_under', '*'), 'main', 'hidden')

_abaa = uicfg.actionbox_appearsin_addmenu
_abaa.tag_object_of(('VersionContent', 'content_for', 'VersionedFile'), False)
_abaa.tag_object_of(('VersionedFile', 'filed_under', 'Folder'), False)

@contextmanager
def related_box(w, label):
    with div(w, Class="docRelated"):
        with div(w, Class="sideBoxTitle"):
            w(span(label))
        with div(w, Class="sideBox sideBoxBody"):
            yield


class EntityViewMixin(object):

    def render_entity(self, entity):
        w = self.w
        with table(w, border="0", width="100%"):
            with tr(w):
                with td(w, style="width:75%", valign="top"):
                    self.render_entity_attributes(entity)
                    self.render_entity_relations(entity)
                with td(w, valign="top"):
                    self.render_side_related(entity)

class TabbedDocumentPrimaryView(tabs.TabsMixin, primary.PrimaryView):
    __select__ = is_instance('VersionedFile')

    tabs = [_('document'), _('revisions')]
    default_tab = 'document'

    def render_entity(self, entity):
        """return html to display the given entity"""
        # XXX still necessary?
        self._cw.add_css('cubicweb.form.css')
        self._cw.add_js(('cubicweb.tabs.js', 'cubicweb.tabs.js', 'jquery.tablesorter.js',
                         'cubes.document.revision.js', 'cubes.document.js',
                         'cubicweb.edition.js', 'cubicweb.calendar.js'))
        if not entity.exists_under_branch_scope():
            self.wview('document', entity.as_rset())
        elif entity.deleted_in_branch():
            super(TabbedDocumentPrimaryView, self).render_entity(entity)
        else:
            self.render_entity_title(entity)
            self.render_tabs(self.tabs, self.default_tab, entity)


class DocumentView(EntityViewMixin, primary.PrimaryView):
    __regid__ = 'document'
    __select__ = (is_instance('VersionedFile')
                  & score_entity(lambda x: x.exists_under_branch_scope()))

    def render_entity_attributes(self, entity):
        entity.branch_head().view('primary', w=self.w)

    def render_side_related(self, entity):
        w = self.w
        for vid in ('master_translation_status', 'non_master_translation_status',
                    'download', 'edition_status'):
            try:
                view = self._cw.vreg['views'].select(vid, self._cw, rset=self.cw_rset)
            except NoSelectableObject:
                continue
            with related_box(w, self._cw._(vid)):
                view.render(w=w)


class DocumentInAnotherBranchPrimary(DocumentView):
    __select__ = (is_instance('VersionedFile')
                  & score_entity(lambda x: not x.exists_under_branch_scope()))

    def render_entity_attributes(self, entity):
        self.w(_('This document does not exist in the branch named "%s".'
                 % req_branch_scope(self._cw)))

    def render_entity_relations(self, entity):
        pass

    def render_entity_related(self, entity):
        pass


# get back to default primary view for folder entities
class FolderPrimaryView(primary.PrimaryView):
    __select__ = is_instance('Folder')


def registration_callback(vreg):
    vreg.register_all(globals().values(), __name__,
                      (TabbedDocumentPrimaryView, FolderPrimaryView))
    vreg.register_and_replace(TabbedDocumentPrimaryView,
                              vcsfileviews.VFPrimaryView)
    vreg.register_and_replace(FolderPrimaryView,
                              folderviews.FolderPrimaryView)
