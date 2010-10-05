"""Specific views for links

:organization: Logilab
:copyright: 2003-2009 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
"""
__docformat__ = "restructuredtext en"
_ = unicode

from logilab.mtconverter import xml_escape

from cubicweb.selectors import is_instance
from cubicweb.view import EntityView
from cubicweb.web import uicfg, formwidgets
from cubicweb.web.views import primary, baseviews
from cubicweb.web.views import xbel, bookmark

for attr in ('title', 'url', 'embed', 'description'):
    uicfg.primaryview_section.tag_attribute(('Link', attr), 'hidden')

uicfg.autoform_field_kwargs.tag_attribute(('Link', 'url'),
                                          {'widget': formwidgets.TextInput})


class LinkPrimaryView(primary.PrimaryView):
    __select__ = is_instance('Link')
    show_attr_label = False

    def render_entity_title(self, entity):
        title = u'<a href="%s">%s</a>' % (xml_escape(entity.actual_url()),
                                          xml_escape(entity.title))
        self.w(u'<h1><span class="etype">%s</span> %s</h1>'
               % (entity.dc_type().capitalize(), title))

    def summary(self, entity):
        return entity.view('reledit', rtype='description')


class LinkOneLineView(baseviews.OneLineView):
    __select__ = is_instance('Link')

    def cell_call(self, row, col):
        entity = self.cw_rset.complete_entity(row, col)
        descr = entity.printable_value('description', format='text/plain')
        descr = descr and descr.splitlines()[0]
        values = {'title': xml_escape(entity.title),
                  'url': xml_escape(entity.absolute_url()),
                  'description': xml_escape(descr),
                  }
        self.w(u'<a href="%(url)s" title="%(description)s">%(title)s</a>'
               % values)
        self.w(u'&nbsp;[<a href="%s">%s</a>]'
               % (xml_escape(entity.actual_url()),
                  self._cw._('follow')))


class LinkView(EntityView):
    __regid__ = 'link'
    __select__ = is_instance('Link')
    title = _('link')

    def cell_call(self, row, col):
        entity = self.cw_rset.complete_entity(row, col)
        values = {'title': xml_escape(entity.title),
                  'url': xml_escape(entity.actual_url()),
                  'description': xml_escape(entity.printable_value('description')),
                  }
        self.w(u'<a href="%(url)s" title="%(description)s">%(title)s</a>'
               % values)

class XbelItemLinkView(xbel.XbelItemView):
    __select__ = is_instance('Link')

    def url(self, entity):
        return entity.url


class LinkFollowAction(bookmark.FollowAction):
    __select__ = is_instance('Link')
