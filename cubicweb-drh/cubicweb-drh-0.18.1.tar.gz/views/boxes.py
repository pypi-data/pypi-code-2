
from logilab.mtconverter import xml_escape

from cubicweb.selectors import is_instance, score_entity
from cubicweb.web import component
from cubicweb.web.htmlwidgets import BoxWidget, BoxLink, SideBoxWidget

class StartupViewsBox(component.CtxComponent):
    """display a box containing links to all startup views"""
    __regid__ = 'drh.workflow_box'
    visible = True # disabled by default
    title = _('State')
    order = 70

    def init_rendering(self):
        super(StartupViewsBox, self).init_rendering()
        self.cw_rset = self._cw.execute('Any S,SN,count(A) GROUPBY S,SN ORDERBY SN '
                                     'WHERE A is Application, A in_state S, S name SN')
        if not self.cw_rset:
            raise component.EmptyComponent()

    def render_body(self, w):
        for eid, state, count in self.cw_rset:
            rql_syn = ('Any A,P,group_concat(TN),E,B '
                       'GROUPBY A,P,E,B,CD ORDERBY CD '
                       'WHERE A in_state X, X eid %s, '
                       'A for_person P, P is Person, '
                       'T? tags A, T name TN, P has_studied_in E?, '
                       'P birthday B?, A creation_date CD')
            state = self._cw._(state)
            url = self._cw.build_url(rql=rql_syn % eid, vtitle=state)
            self.append(self.link(u'%s: %s' % (state, count), url))
        self.render_items(w)


class AttachmentsDownloadBox(component.EntityCtxComponent):
    """
    A box containing all downloadable attachments concerned by Person.
    """
    __regid__ = 'drh.concerned_by_box'
    __select__ = (component.EntityCtxComponent.__select__
                  & is_instance('Person')
                  & score_entity(lambda x: x.concerned_by))
    title = _('concerned_by')
    order = 0

    def render_body(self, w):
        for attachment in self.entity.concerned_by:
            idownloadable = attachment.cw_adapt_to('IDownloadable')
            w(u'<div><a href="%s"><img src="%s" alt="%s"/> %s</a>'
              % (xml_escape(idownloadable.download_url()),
                 self._cw.uiprops['DOWNLOAD_ICON'],
                 _('download icon'), xml_escape(attachment.dc_title())))
            w(u'</div>')


class PeopleBox(component.EntityCtxComponent):
    __regid__ = 'drh.123people_box'
    __select__ = component.EntityCtxComponent.__select__ & is_instance('Person')
    title = _('The url\'s Person on 123people ')
    order = 25

    def render_body(self, w):
        firstname = self.entity.firstname
        surname = self.entity.surname
        url = 'http://www.123people.com/s/%s+%s/world' % (firstname, surname)
        label = '%s %s' % (firstname, surname)
        self.append(self.link(label, url))
        self.render_items(w)
