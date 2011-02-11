from logilab.mtconverter import xml_escape

from cubicweb.web.views import startup

class IndexView(startup.IndexView):
    title = _('Index')

    def call(self):
        _ = self._cw._
        user = self._cw.user
        self.w(u'<h1>%s</h1>' % self._cw.property_value('ui.site-title'))
        # email addresses not linked
        rql = 'Any X WHERE NOT P use_email X'
        title = u'email addresses not linked to a person'
        rset = self._cw.execute(rql)
        if rset:
            self.w(u'<p><a href="%s">%s %s</a></p>'
                   % (xml_escape(self.build_url(rql=rql, vtitle=title)),
                      len(rset), title))
        # email threads not linked to an application
        rql = 'Any T WHERE T is EmailThread, NOT T topic X'
        title = u'message threads without topic'
        rset = self._cw.execute(rql)
        if rset:
            self.w(u'<p><a href="%s">%s %s</a></p>'
                   % (xml_escape(self.build_url(rql=rql, vtitle=title)),
                      len(rset), title))
        # candidatures en attente
        rset = self._cw.execute('Any A,P,group_concat(TN),E,B '
                                'GROUPBY A,P,E,B,CD ORDERBY CD '
                                'WHERE A is Application, A in_state X, '
                                'X name "received", '
                                'A for_person P, P has_studied_in E?, '
                                'P birthday B, T? tags A, T name TN, '
                                'A creation_date CD')
        if rset:
            self.w(u'<h2>%s</h2>' % _('Juger candidatures'))
            self.wview('table',rset,'null')
        else:
            self.w(u'<p>%s</p>' % _('aucune candidature en attente'))




def registration_callback(vreg):
    vreg.register_and_replace(IndexView, startup.IndexView)
