from logilab.mtconverter import xml_escape

from cubicweb.selectors import is_instance
from cubicweb.web import component


class InterestedInVComponent(component.Component):
    """section to control user intrested in a talk """
    __regid__ = 'interesting'
    __select__ = is_instance('Talk',)
    context = 'header'
    rtype = 'interested_in'
    target = 'object'
    htmlclass = 'mainRelated'
    cw_property_defs = {
        _('visible'):  dict(type='Boolean', default=True,
                            help=_('display the box or not')),
    }

    def call(self):
        user = self._cw.user
        _ = self._cw._
        eid = self.cw_rset[0][0]
        rset = self._cw.execute('Any X WHERE U interested_in X, U eid %(u)s, X eid %(x)s',
                                {'u': user.eid, 'x': eid})

        self.w(u'<div class="%s" id="%s">' % (self.__regid__, self.domid))
        if not rset.rowcount:
            # user isn't registered
            rql = 'SET U interested_in X WHERE U eid %(u)s, X eid %(x)s'
            title = _('click here if you are interested by this talk')
            msg = _('you are now registered for this talk')
        else:
            # user is registered
            rql = 'DELETE U interested_in X WHERE U eid %(u)s, X eid %(x)s'
            title = _('click here if you are not any more interested by this talk')
            msg = _('you are not anymore registered for this project')
        url = self._cw.user_rql_callback((rql, {'u': self._cw.user.eid, 'x': eid}),
                                         msg)
        self.w(u'<a href="%s">%s</a>' % (xml_escape(url), title))
        self.w(u'</div>')
        self.w(u'<div class="clear"></div>')
