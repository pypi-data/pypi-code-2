"""document components

:organization: Logilab
:copyright: 2008-2010 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
"""
from __future__ import with_statement
_ = unicode

from cubicweb.web.views import basetemplates, basecomponents, ibreadcrumbs
from cubicweb.selectors import is_instance

from cubes.document.entities import req_branch_scope, main_repository
from cubes.document.html import select_widget, span


basetemplates.HTMLPageHeader.main_cell_components = (
    'appliname', 'branch_scope_chooser', 'breadcrumbs')


class BreadCrumbEntityVComponent(ibreadcrumbs.BreadCrumbEntityVComponent):

    def render_breadcrumbs(self, w, contextentity, path):
        root = path.pop(0)
        self.wpath_part(w, root, contextentity, not path)
        for i, parent in enumerate(path):
            w(self.separator)
            w(u"\n")
            self.wpath_part(w, parent, contextentity, i == len(path) - 1)


class FolderBreadCrumbsAdapter(ibreadcrumbs.IBreadCrumbsAdapter):
    __select__ = ibreadcrumbs.IBreadCrumbsAdapter.__select__ & is_instance('Folder')

    def breadcrumbs(self, view=None, recurs=None):
        if self.entity.reverse_root_folder:
            return []
        parent = self.parent_entity()
        if parent:
            adapter = parent.cw_adapt_to('IBreadCrumbs')
            return adapter.breadcrumbs(view, True) + [self.entity]
        return []

class DocumentBreadCrumbsAdapter(ibreadcrumbs.IBreadCrumbsAdapter):
    __select__ = (ibreadcrumbs.IBreadCrumbsAdapter.__select__
                  & is_instance('VersionedFile', 'File'))

    def breadcrumbs(self, view=None, recurs=None):
        parent = self.parent_entity()
        if parent:
            adapter = parent.cw_adapt_to('IBreadCrumbs')
            return adapter.breadcrumbs(view, True)
        return []


class BranchScopeComponent(basecomponents.HeaderComponent):
    """tiny widget to control the branch under which all furthers
    views and actions are scoped"""
    __regid__ = 'branch_scope_chooser'
    order = 1

    def render(self, w):
        repository = main_repository(self._cw.vreg.config, self._cw)
        if not repository:
            return
        choices = repository.branches()
        if not choices:
            return
        self._cw.add_js(( 'cubicweb.ajax.js', 'cubes.document.js' ))
        curr_branch = req_branch_scope(self._cw)
        with span(w, Class='pathbar'):
            w(u'&nbsp;')
            select_widget(w, zip(choices, choices), selected=curr_branch,
                          id='branch_scope',
                          onchange="switch_branch('branch_scope')")


def registration_callback(vreg):
    vreg.register_all(globals().values(), __name__,
                      (BreadCrumbEntityVComponent,))
    vreg.register_and_replace(BreadCrumbEntityVComponent,
                              ibreadcrumbs.BreadCrumbEntityVComponent)


