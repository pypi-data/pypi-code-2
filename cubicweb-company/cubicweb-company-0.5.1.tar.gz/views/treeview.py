"""treeviews

:organization: Logilab
:copyright: 2009 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
"""
__docformat__ = "restructuredtext en"
_ = unicode

from logilab.mtconverter import xml_escape

from cubicweb.selectors import one_line_rset, is_instance, match_kwargs
from cubicweb.view import EntityView
from cubicweb.web.views.treeview import TreeViewItemView

class CompanyTree(EntityView):
    __regid__ = 'companytree'
    __select__ = one_line_rset() & is_instance('Company')

    def cell_call(self, row, col):
        entity = self.cw_rset.get_entity(row, col)
        root_company = entity.cw_adapt_to('ITree').root()
        self.wview('treeview', root_company.as_rset(), subvid='oneline-selectable',
                   onscreen=entity.eid)

class ComponentTreeItemView(TreeViewItemView):
    """keeps track of which branches to open according to current component"""
    __select__ = (TreeViewItemView.__select__ & is_instance('Company'))

    def cell_call(self, row, col, treeid, vid, parentvid='treeview',
                  **morekwargs):
        onscreen = morekwargs.get('onscreen')
        if onscreen:
            self._compute_open_branches(onscreen)
        else:
            self._open_branch_memo = set()
        super(ComponentTreeItemView, self).cell_call(row, col, treeid,
                                                     vid, parentvid,
                                                     **morekwargs)

    def _compute_open_branches(self, comp_eid):
        entity = self._cw.execute('Any C WHERE C eid %(c)s',
                                  {'c': comp_eid}).get_entity(0, 0)
        self._open_branch_memo = set(entity.cw_adapt_to('ITree').path())

    def open_state(self, eeid, treeid):
        return eeid in self._open_branch_memo

class OneLineSelectableView(EntityView):
    """custom oneline view used by company / division treeview"""
    __regid__ = 'oneline-selectable'
    __select__ = is_instance('Company') & match_kwargs('onscreen')

    def cell_call(self, row, col, onscreen):
        entity = self.cw_rset.get_entity(row, col)
        if entity.eid == onscreen:
            self.w(u'<span class="currentCompany">%s</span>'
                   % xml_escape(entity.view('textincontext')))
        else:
            if entity.headquarters:
                tooltip = xml_escape(entity.headquarters[0].dc_long_title())
            else:
                tooltip = u''
            self.w(u'<a href="%s" title="%s">%s</a>'
                   % (xml_escape(entity.absolute_url()),
                      xml_escape(tooltip),
                      xml_escape(entity.dc_title())))
