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
"""cubicweb-vcreview primary views adapters for web ui"""
__docformat__ = "restructuredtext en"
_ = unicode

from logilab.mtconverter import xml_escape

from cubicweb.selectors import score_entity, is_instance
from cubicweb.view import EntityView
from cubicweb.schema import display_name
from cubicweb.web import uicfg
from cubicweb.web.views import primary, ibreadcrumbs

from cubes.vcsfile.views import primary as vcsfile

_pvs = uicfg.primaryview_section
_abaa = uicfg.actionbox_appearsin_addmenu
_afs = uicfg.autoform_section


# patch primary view ###########################################################

_pvs.tag_subject_of(('Patch', 'patch_repository', '*'), 'hidden') # in breadcrumbs
_pvs.tag_subject_of(('Patch', 'patch_revision', '*'), 'hidden') # table in attributes

class PatchPrimaryView(primary.PrimaryView):
    __select__ = primary.PrimaryView.__select__ & is_instance('Patch')

    def render_entity_title(self, entity):
        self.w(u'<h1>%s <span class="state">[%s]</span></h1>'
               % (xml_escape(entity.dc_title()),
                  xml_escape(entity.cw_adapt_to('IWorkflowable').printable_state)))

    def render_entity_attributes(self, entity):
        super(PatchPrimaryView, self).render_entity_attributes(entity)
        self.w(u'<div class="componentTitle">%s</div>' % self._cw._('Patch revisions'))
        rset = self._cw.execute('Any VC, RA, RB, RC, RD ORDERBY RC DESC '
                                'WHERE X patch_revision VC, VC from_revision R,'
                                'R author RA, R branch RB, R description RD, '
                                'R creation_date RC, X eid %(x)s', {'x': entity.eid})
        self.wview('table', rset)


# version content primary view #################################################
# only when version content is detected has being a patch revision

_pvs.tag_object_of(('*', 'patch_revision', '*'), 'hidden') # in breadcrumbs

class VCPrimaryView(vcsfile.VCPrimaryView):
    __select__ = (vcsfile.VCPrimaryView.__select__
                  & score_entity(lambda x: x.patch))

    def render_entity_attributes(self, entity):
        # XXX have to call primary.PrimaryView directly to avoid duplicated display
        # of version's content
        primary.PrimaryView.render_entity_attributes(self, entity)
        self.w(u'<div class="content">')
        adapter = entity.cw_adapt_to('IDownloadable')
        contenttype = adapter.download_content_type()
        targetmt = self._cw.form.get('nocomment') and 'text/html' or 'text/annotated-html'
        if not self.render_data(entity, contenttype, targetmt) and targetmt != 'text/html':
            self.render_data(entity, contenttype, 'text/html')
        self.w(u'</div>')

# ease change of detected mime type for version content for patches without
# .diff extension
_afs.tag_attribute(('VersionContent', 'data_format'), 'main', 'attributes')
_afs.tag_attribute(('VersionContent', 'data_encoding'), 'main', 'attributes')


# repository primary view ######################################################

_abaa.tag_subject_of(('Repository', 'has_patch_repository', '*'), True)
_abaa.tag_object_of(('*', 'patch_repository', 'Repository'), False)
_pvs.tag_object_of(('*', 'patch_repository', 'Repository'), 'hidden')


def repo_patches_rql(is_patch_repo):
    rql = ('Any P,PO,PB,PS,COUNT(VC) GROUPBY P,PO,PB,PS WHERE P in_state PS, '
           'P originator PO, P branch PB, P patch_revision VC, P patch_repository R'
           )
    if is_patch_repo:
        rql += ', R eid %(x)s'
    else:
        rql += ', X has_patch_repository R, X eid %(x)s'
    return rql


class RepositoryPatchesTab(EntityView):
    __regid__ = _('vcreview.repositorypatches_tab')
    __select__ = is_instance('Repository') & score_entity(
        lambda x: x.patchrepo or x.patchrepo_of)

    def entity_call(self, entity):
        rql = repo_patches_rql(entity.patchrepo_of)
        linktitle = self._cw._('Patches for %s') % entity.dc_title()
        linkurl = self._cw.build_url(rql=rql % {'x': entity.eid},
                                     vtitle=linktitle)
        self.w('<p>%s. <a href="%s">%s</a></p>' % (
            self._cw._('Table below only show active patches'),
            xml_escape(linkurl), self._cw._('Show all patches')))
        rql += ', PS name IN ("in-progress", "pending-review")'
        rset = self._cw.execute(rql, {'x': entity.eid})
        self.wview('table', rset, 'noresult', paginate=True, displayfilter=True)

vcsfile.RepositoryPrimaryView.tabs.append(RepositoryPatchesTab.__regid__)


# breadcrumbs ##################################################################

class PatchIBreadCrumbsAdapter(ibreadcrumbs.IBreadCrumbsAdapter):
    __select__ = is_instance('Patch')

    def parent_entity(self):
        return self.entity.repository

class DVCIBreadCrumbsAdapter(ibreadcrumbs.IBreadCrumbsAdapter):
    __select__ = (is_instance('VersionContent', 'DeletedVersionContent')
                  & score_entity(lambda x: x.patch))

    def parent_entity(self):
        return self.entity.patch


class DVCBreadCrumbTextView(ibreadcrumbs.BreadCrumbTextView):
    __select__ = (is_instance('VersionContent', 'DeletedVersionContent')
                  & score_entity(lambda x: x.patch))

    def cell_call(self, row, col, **kwargs):
        entity = self.cw_rset.get_entity(row, col)
        self.w('%s %s' % (display_name(self._cw, 'revision', context='Revision'),
                          entity.revision))


def registration_callback(vreg):
    vreg.register_all(globals().values(), __name__, (VCPrimaryView,))
    vreg.register_and_replace(VCPrimaryView, vcsfile.VCPrimaryView)
