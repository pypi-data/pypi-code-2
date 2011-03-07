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

    @cached
    def filter_box_context_info(self):
        rset = self._cw.execute(
            'Any P,PO,PB,PS,COUNT(VC),R GROUPBY R,P,PO,PB,PS ORDERBY R,PB,PO WHERE '
            'P originator PO, P branch PB, P patch_revision VC, P patch_repository R, '
            'P in_state PS, PS name IN ("in-progress", "pending-review", "deleted")'
            )
        return rset, 'vcreview.patches.table', domid(self.__regid__), False

    def call(self):
        self.w(u'<h1>%s</h1>' % self._cw._(self.title))
        rset, vid, divid, paginate = self.filter_box_context_info()
        self.wview(vid, rset, 'noresult', divid=divid)


class AllActivePatchesTable(tableview.TableView):
    __regid__ = 'vcreview.patches.table'
    # XXX selector
    def call(self, **kwargs):
        kwargs['paginate'] = True
        super(AllActivePatchesTable, self).call(**kwargs)

