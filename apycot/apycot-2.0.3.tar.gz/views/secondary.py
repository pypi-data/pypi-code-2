from datetime import datetime

from logilab.mtconverter import xml_escape

from cubicweb.view import EntityView
from cubicweb.selectors import is_instance
from cubicweb.web.views.baseviews import InContextView

from cubes.narval.views.plan import PlanOptionsCell


class TestExecutionDescriptorMixin(object):
    def describe_execution(self, exc, changes_only=False, xml_compat=False):
        self._cw.add_css('cubes.apycot.css')
        _ = self._cw._
        if xml_compat:
            w = lambda x: self.w(xml_escape(x))
        else:
            w = self.w
        if not changes_only:
            if exc.endtime is not None:
                nb_checkers = len(exc.checkers)
                duration = exc.endtime - exc.starttime
                if nb_checkers > 1:
                    w(u'<p>')
                    w(_(u'%(nb)s checkers run in %(dur)s')
                           % {'nb': nb_checkers, 'dur': duration})
                    w(u'</p>')
                else:
                    w(u'<p>')
                    w(_(u'%(nb)s checker run in %(dur)s')
                           % {u'nb': nb_checkers, 'dur': duration})
                    w(u'</p>')
            else:
                w(u'<p>')
                w(_(u'running for %(dur)s')
                       % {'dur': datetime.now() - exc.starttime})
                w(u'</p>')
        changes = exc.status_changes()
        if changes_only:
            if changes:
                checkers = (new for old, new in changes.values())
            else:
                checkers = ()
                w(_(u'nothing changed'))
        else:
            checkers = exc.checkers
        if checkers:
            w(u'<dl>')
            for checker in checkers:
                w(u'<dt>%s</dt>' % xml_escape(checker.name))
                status = checker.view(u'incontext')
                if changes_only or (changes is not None and checker.name in changes):
                    old_status = changes[checker.name][0].view(u'incontext')
                    w(u'<dd><strong>%s</strong> (previously <strike><em>%s</em></strike>)</dd>'
                      % (status, old_status))
                else:
                    w(u'<dd><strong>%s</strong></dd>' % status)
            w(u'</dl>')


class CheckStatusView(InContextView):
    __select__ = is_instance('CheckResult')

    def cell_call(self, row, col):
        entity = self.cw_rset.get_entity(row, col)
        self.w('<a href="%s" class="status_%s" title="%s">%s</a>' % (
               entity.absolute_url(),
               entity.status,
               self._cw._('view details'),
               self._cw._(entity.status)))


class TestExecutionOptionsCell(PlanOptionsCell):
    __select__ = PlanOptionsCell.__select__ & is_instance('TestExecution')

    def cell_call(self, row, col, **kwargs):
        entity = self.cw_rset.get_entity(row, col)
        self.w(self._cw._(u'branch="%s"<br/>') % xml_escape(entity.branch))
        if entity.options:
            self.w(u'; ')
            self.w(xml_escape(u'; '.join(entity.options.splitlines())))


class TestExecutionDescriptionView(EntityView, TestExecutionDescriptorMixin):
    __regid__ = 'apycot.te.description'
    __select__ = is_instance('TestExecution')

    changes_only = False

    def cell_call(self, row, col):
        entity = self.cw_rset.get_entity(row, col)
        self.w(u'<h2>')
        entity.view('outofcontext', w=self.w)
        self.w(u'</h2>')
        self.describe_execution(entity,changes_only=self.changes_only)


class TestExecutionChangeView(TestExecutionDescriptionView):
    __regid__ = 'apycot.te.changes'
    changes_only = True
