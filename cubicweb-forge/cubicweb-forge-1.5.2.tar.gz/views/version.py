"""views for Project entities

:organization: Logilab
:copyright: 2006-2010 LOGILAB S.A. (Paris, FRANCE), license is LGPL.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
"""
__docformat__ = "restructuredtext en"
_ = unicode

from cubicweb.selectors import is_instance
from cubicweb.web import uicfg, component

from cubes.tracker.views import version as tracker

_pvs = uicfg.primaryview_section
for attr in ('progress_target', 'progress_done', 'progress_todo'):
    _pvs.tag_attribute(('Version', attr), 'hidden')

class VersionBurndownChartVComponent(component.EntityVComponent):
    __regid__ = 'versionburndown'
    __select__ = component.EntityVComponent.__select__ & is_instance('Version')
    rql = ('Any X,CD,L,LL where X load L, X load_left LL, '
           'X creation_date CD, X done_in V, V eid %s')

    def cell_call(self, row, col, view=None):
        version = self.cw_rset.entities().next()
        alt = self._cw._('Burn Down Chart')
        self.w('<h3>%s</h3>' % alt)
        # the following rql is useful to detect Ticket which is
        # created directly with a done state (validation pending,
        # resolved, deprecated or rejected). In this case, graph is
        # probably wrong.
        ticketcls = self._cw.vreg['etypes'].etype_class('Ticket')
        rset = self._cw.execute(
            'Any T GROUPBY T  WHERE T done_in V, V eid %%(v)s, '
            'T in_state S, NOT S name IN (%s), TR wf_info_for T '
            'HAVING COUNT(TR)=0' % ','.join('"%s"' % st for st in ticketcls.OPEN_STATES),
           {'v': version.eid})
        if rset:
            self.w(u'<div class="needsvalidation">%s</div>'
                   % self._cw._("Some tickets don't have a regular workflow, "
                                "the graph may be wrong."))
        tickets_rset = self._cw.execute(self.rql % self.cw_rset[row][col])
        if tickets_rset:
            self.wview('burndown_chart', tickets_rset, width=800, height=500)


class VersionTestCardBarVComponent(component.RelatedObjectsVComponent):
    """display version's test instances of test card"""
    __regid__ = 'versiontests'
    __select__ = component.RelatedObjectsVComponent.__select__ & is_instance('Version')

    rtype = 'for_version'
    target = 'subject'

    title = _('Test case instances')
    context = 'navcontentbottom'
    vid = 'table'

    def rql(self):
        return 'Any X,S WHERE X for_version E, E eid %(x)s, X in_state S'


class VersionProgressTableView(tracker.VersionProgressTableView):
    columns = (_('project'), _('milestone'), _('state'), _('planned_start'),
               _('planned_delivery'),
               _('cost'), _('progress'),
               _('depends_on'), _('todo_by'))

    def header_for_cost(self, ecls):
        """``cost`` column cell renderer"""
        return self._cw._('load')


def registration_callback(vreg):
    vreg.register_all(globals().values(), __name__, (VersionProgressTableView,))
    vreg.register_and_replace(VersionProgressTableView,
                              tracker.VersionProgressTableView)
