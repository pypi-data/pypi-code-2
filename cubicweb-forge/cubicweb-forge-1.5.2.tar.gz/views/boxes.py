"""forge components boxes

:organization: Logilab
:copyright: 2006-2010 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
"""
__docformat__ = "restructuredtext en"

from logilab.mtconverter import xml_escape

from cubicweb.schema import display_name
from cubicweb.selectors import is_instance, score_entity
from cubicweb.view import EntityAdapter
from cubicweb.web import box, htmlwidgets
from cubicweb.web.views import idownloadable, boxes

class VersionIDownloadableAdapter(EntityAdapter):
    __regid__ = 'IDownloadable'
    __select__ = (is_instance('Version') &
                  score_entity(lambda x: x.project.downloadurl and x.cw_adapt_to('IWorkflowable').state == 'published'))

    def download_url(self):
        downloadurl = self.entity.project.downloadurl
        if not downloadurl:
            return
        if not downloadurl[-1] == '/':
            downloadurl +=  '/'
        return '%s%s' % (downloadurl, self.entity.tarball_name())

    def download_file_name(self):
        return self.entity.tarball_name()

    def download_content_type(self):
        return 'application/x-tar'

    def download_encoding(self):
        return 'gzip'


class ProjectDownloadBox(box.EntityBoxTemplate):
    __regid__ = 'download_box'
    __select__ = (box.EntityBoxTemplate.__select__ & is_instance('Project') &
                  score_entity(lambda x: x.downloadurl and x.latest_version()))

    def cell_call(self, row, col, **kwargs):
        project = self.cw_rset.get_entity(row, col)
        version = project.latest_version()
        footer = u' [<a href="%s">%s</a>]' % (
            project.downloadurl, self._cw._('see them all'))
        idownloadable.download_box(self.w, version,
                                   self._cw._('download latest version'),
                                   version.tarball_name(), footer=footer)



class ImageSideboxView(boxes.SideBoxView):
    __regid__ = 'sidebox'
    __select__ = boxes.SideBoxView.__select__ & is_instance('File')

    def call(self, boxclass='sideBox', title=u''):
        self._cw.add_css('cubes.file.css')
        box = htmlwidgets.SideBoxWidget(display_name(self._cw, title), self.__regid__)
        entity = self.cw_rset.get_entity(0, 0)
        idownloadable = entity.cw_adapt_to('IDownloadable')
        if idownloadable.download_content_type().startswith('image/'):
            file_icon = idownloadable.download_url(small='true')
        else:
            file_icon =  self._cw.uiprops['FILE_ICON']

        if getattr(entity, 'reverse_screenshot', None):
            gallery_url = '%s/?tab=screenshots_tab&selected=%s' % (
                entity.project.absolute_url(), entity.eid)
        elif getattr(entity, 'reverse_attachment', None):
            gallery_url = entity.reverse_attachment[0].absolute_url(vid='ticketscreenshots',
                                                                    selected=entity.eid)
        elif getattr(entity, 'project', None): # documentation file
            # XXX huumm
            gallery_url = '%s/documentation' % entity.project.absolute_url()
        else:
            gallery_url = u'%s%s' % (self._cw.build_url(vid='gallery',
                                                        rql=self.cw_rset.printable_rql()),
                                     '&selected=%s' % entity.eid)
        if len(self.cw_rset) > 1:
            see_all_url = u'[<a href="%s">%s (%s)</a>]' % (xml_escape(gallery_url),
                                                           self._cw._('see them all'),
                                                           len(self.cw_rset))
        else:
            see_all_url = u''
        html_container = (u'<li class="screenshot">'
                          u'<a href="%s" title="%s"><img alt="" src="%s"/>'
                          u'<br/>%s</a><br/>%s</li>')
        html = html_container % (xml_escape(gallery_url),
                                 xml_escape(entity.data_name),
                                 xml_escape(file_icon),
                                 xml_escape(entity.data_name),
                                 see_all_url)
        box.items = [htmlwidgets.BoxHtml(html)]
        box.render(self.w)

