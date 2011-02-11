from cubicweb.selectors import is_instance, rql_condition
from cubicweb.web import component

class SentMailVComponent(component.EntityCtxComponent):
    """email sent by this person"""
    __regid__ = 'sentmail'
    __select__ = (component.EntityCtxComponent.__select__
                  & is_instance('Person')
                  & rql_condition('X use_email EA, E sender EA'))
    title = _('ctxcomponents_sentmail')
    order = 40

    def render_body(self, w):
        rset = self._cw.execute('Any E ORDERBY D DESC WHERE P use_email EA, '
                                'E sender EA, E date D, P eid %(x)s',
                                {'x': self.entity.eid})
        self._cw.view('list', rset, w=w)

class ThreadTopicVComponent(component.EntityCtxComponent):
    """email in threads related to this topic"""
    __regid__ = 'threadtopic'
    __select__ = (component.EntityCtxComponent.__select__
                  & is_instance('Application')
                  & rql_condition('E in_thread T, T topic X'))
    title = _('ctxcomponents_mailtopic')
    order = 40

    def render_body(self, w):
        rset = self._cw.execute('Any E ORDERBY D DESC WHERE E date D, '
                                'E in_thread T, T topic A, A eid %(x)s',
                                {'x': self.entity.eid})
        self._cw.view('list', rset, w=w)

