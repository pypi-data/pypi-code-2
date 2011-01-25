"""most views used by the document cube

:organization: Logilab
:copyright: 2008-2010 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
"""
from __future__ import with_statement

import uuid

from cubicweb.web.component import EmptyComponent, RQLCtxComponent

_ = unicode

class ReposBrowsingBox(RQLCtxComponent):
    __regid__ = 'browsing_box'
    title = _('browse the repositories')
    # XXX check
    rql = 'Any F,N ORDERBY N WHERE F is Folder, F name N, REPO root_folder RF, F filed_under RF'
    # for the etype_rtype_selector
    etype = 'Folder'
    rtype = 'filed_under'
    order = 2
    treeid_key = "repotree"
    vid = 'filetree'

    # XXX can be dropped for cw > 3.10.7
    def init_rendering(self):
        self.cw_rset = self._cw.execute(*self.to_display_rql())
        if not self.cw_rset:
            raise EmptyComponent()

    def render_body(self, w):
        # don't use a property here since we want same uuid hex number
        treeid = self._cw.data.setdefault(self.treeid_key, uuid.uuid1().hex)
        self._cw.view(self.vid, rset=self.cw_rset, treeid=treeid, w=w)
