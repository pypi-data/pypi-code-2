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
"""cubicweb-vcreview startup views"""

__docformat__ = "restructuredtext en"
_ = unicode

from logilab.common.decorators import cached

from cubicweb.view import StartupView
from cubicweb.uilib import domid
from cubicweb.web.views import tableview

class AllActivePatches(StartupView):
    __regid__ = 'vcreview.allactivepatches'
    title = _('All active patches')

    rql = ('Any P,PO,PB,PS,COUNT(TR),R GROUPBY R,P,PO,PB,PS '
           'ORDERBY RT,PB,PO WHERE P originator PO, P branch PB, P in_state PS,'
           'TR? wf_info_for P, P patch_repository R, R title RT, '
           'PS name IN ("in-progress", "pending-review", "deleted")')

    @cached
    def filter_box_context_info(self):
        rset = self._cw.execute(self.rql)
        return rset, 'vcreview.patches.table', domid(self.__regid__), False

    def call(self):
        self.w(u'<h1>%s</h1>' % self._cw._(self.title))
        rset, vid, divid, paginate = self.filter_box_context_info()
        self.wview(vid, rset, 'noresult', divid=divid)


class UserWorkList(AllActivePatches):
    __regid__ = 'vcreview.patches.worklist'
    title = _('My review worklist')

    rql = ('Any P,PO,PB,PS,COUNT(TR),R GROUPBY R,P,PO,PB,PS '
           'ORDERBY RT,PB,PO WHERE P originator PO, P branch PB, P in_state PS,'
           'TR? wf_info_for P, P patch_repository R, R title RT, U eid %(u)s, '
           'EXISTS(PS name "pending-review" AND P patch_reviewer U) '
           'OR EXISTS(PS name IN ("reviewed", "deleted") AND EXISTS(R repository_committer U) '
           'OR EXISTS(U in_group G, G name "commiters"))')

    @cached
    def filter_box_context_info(self):
        rset = self._cw.execute(self.rql, {'u': self._cw.user.eid})
        return rset, 'vcreview.patches.table', domid(self.__regid__), False



class PatchesTable(tableview.TableView):
    __regid__ = 'vcreview.patches.table'
    # XXX selector
    def call(self, **kwargs):
        kwargs['paginate'] = True
        super(PatchesTable, self).call(**kwargs)
