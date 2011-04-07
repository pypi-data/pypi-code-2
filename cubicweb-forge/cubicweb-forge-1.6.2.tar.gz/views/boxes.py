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
from cubicweb.web import component
from cubicweb.web.views import boxes

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


class ProjectDownloadBox(component.EntityCtxComponent):
    __regid__ = 'download_box'
    __select__ = (component.EntityCtxComponent.__select__
                  & is_instance('Project') &
                  score_entity(lambda x: x.downloadurl and x.latest_version()))
    title = 'download' # no _() to use cw's translation

    def render_body(self, w):
        project = self.entity
        version = project.latest_version()
        w(u'<a href="%s"><img src="%s" alt="%s"/> %s</a>'
          % (xml_escape(version.cw_adapt_to('IDownloadable').download_url()),
             self._cw.uiprops['DOWNLOAD_ICON'],
             self._cw._('download latest version'),
             xml_escape(version.tarball_name())))
        w(u' [<a href="%s">%s</a>]' % (
            project.downloadurl, self._cw._('see them all')))



class ImageSideboxView(boxes.RsetBox): # XXX Project.screenshots / Ticket.attachment
    __select__ = boxes.RsetBox.__select__ & is_instance('File')

    def render_body(self, w):
        self._cw.add_css('cubes.file.css')
        sample = self.cw_rset.get_entity(self.cw_row or 0, self.cw_col or 0)
        idownloadable = sample.cw_adapt_to('IDownloadable')
        if idownloadable.download_content_type().startswith('image/'):
            icon = idownloadable.download_url(small='true')
        else:
            icon =  self._cw.uiprops['FILE_ICON']
        if getattr(sample, 'reverse_screenshot', None):
            gallery_url = '%s/?tab=screenshots_tab&selected=%s' % (
                sample.project.absolute_url(), sample.eid)
        elif getattr(sample, 'reverse_attachment', None):
            gallery_url = sample.reverse_attachment[0].absolute_url(
                vid='ticketscreenshots', selected=sample.eid)
        elif getattr(sample, 'project', None): # documentation file
            # XXX huumm
            gallery_url = '%s/documentation' % sample.project.absolute_url()
        else:
            gallery_url = u'%s%s' % (self._cw.build_url(vid='gallery',
                                                        rql=self.cw_rset.printable_rql()),
                                     '&selected=%s' % sample.eid)
        if len(self.cw_rset) > 1:
            see_all_url = u'[<a href="%s">%s (%s)</a>]' % (xml_escape(gallery_url),
                                                           self._cw._('see them all'),
                                                           len(self.cw_rset))
        else:
            see_all_url = u''
        w(u'<a href="%s" title="%s"><img alt="" src="%s"/><br/>%s</a><br/>%s'
          % (xml_escape(gallery_url), xml_escape(sample.data_name),
             xml_escape(icon), xml_escape(sample.data_name), see_all_url))

