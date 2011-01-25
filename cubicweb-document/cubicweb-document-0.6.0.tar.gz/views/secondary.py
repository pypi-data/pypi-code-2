"""most views used by the document cube

:organization: Logilab
:copyright: 2008-2010 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
"""
from __future__ import with_statement
_ = unicode

from difflib import ndiff

from logilab.mtconverter import xml_escape

from cubicweb.view import EntityView
from cubicweb.selectors import is_instance, one_line_rset, score_entity
from cubicweb.uilib import cut as text_cut, rql_for_eid
from cubicweb.web.views import baseviews

from cubes.document.entities import req_branch_scope
from cubes.document.views.forms import up_to_revision_form
from cubes.document.html import a, span, div, table, tr, td, th, p, input, form


class LangView(EntityView):
    __select__ = EntityView.__select__ & score_entity(lambda x: hasattr(x, 'lang') and len(x.lang))
    __regid__ = 'lang'

    def cell_call(self, row, col):
        entity = self.cw_rset.get_entity(row, col)
        self.w(a(xml_escape(entity.dc_language()),
                 href=xml_escape(entity.absolute_url())))

class InContextView(EntityView):
    """for VersionedFiles, it is nicer to show
    a longer portion of the description
    """
    __select__ = is_instance('VersionedFile')
    __regid__ = 'incontext'

    def cell_call(self, row, col, **_kwargs):
        w = self.w
        entity = self.cw_rset.get_entity(row, col)
        desc = text_cut(entity.dc_description(), 300)
        w(a(xml_escape(self._cw.view('textincontext', self.cw_rset, row=row, col=col)),
            href=xml_escape(entity.absolute_url()),
            title=xml_escape(desc)))

class FileItemInnerView(baseviews.OneLineView):
    """inner view used by the TreeItemView instead of oneline view

    This view adds an enclosing <span> with some specific CSS classes
    around the oneline view. This is needed by the jquery treeview plugin.
    """
    __select__ = baseviews.OneLineView.__select__ & \
                 is_instance('Folder')
    __regid__ = 'filetree-oneline'

    def cell_call(self, row, col):
        w = self.w; _ = self._cw._
        entity = self.cw_rset.get_entity(row, col)
        itree = entity.cw_adapt_to('ITree')
        if itree and not itree.is_leaf():
            w(span(entity.view('oneline'), Class='folder'))
        else:
            branch = req_branch_scope(self._cw)
            if hasattr(entity, 'keyword'): # XXX docaster specific
                name = entity.keyword
            elif hasattr(entity, 'data_name'): # File
                name = entity.data_name
            else:
                name = entity.name
            # exists ? deleted ?
            if (hasattr(entity, 'exists_under_branch_scope') and
                not entity.exists_under_branch_scope()):
                name = '%s (not there)' % name
                w(span(xml_escape(name), Class='file'))
            elif (hasattr(entity, 'deleted_in_branch') and
                  entity.deleted_in_branch(branch)):
                name = '%s (deleted)' % name
                w(span(xml_escape(name), Class='file'))
            else:
                w(span(a(xml_escape(name or u''),
                         href=xml_escape(entity.absolute_url()),
                         Class='file')))

class MasterOdtTranslationStatus(EntityView):
    __regid__ = _('master_translation_status')
    __select__ = is_instance('VersionedFile') & score_entity(lambda x: x.pivot_lang or 0)

    def cell_call(self, row, col):
        _, w = self._cw._, self.w
        entity = self.cw_rset.get_entity(row, col)
        self.field(_('language :'), xml_escape(entity.dc_language()), tr=False)
        w(_('this is the master document'))
        if not entity.translations:
            return w(p(_('no translation available yet')))
        ent_rev = entity.branch_head().revision
        with table(w, Class='listing'):
            with tr(w):
                for header in (_('translation'), _('status')):
                    w(th(header))
            for translation in entity.translations:
                tr_uptorev = translation.up_to_revision()
                if ent_rev == tr_uptorev:
                    msg = _('up to date')
                    style = 'uptodate'
                elif tr_uptorev is None:
                    msg = _('unknown')
                    style = 'needs_update'
                else:
                    msg = _('up to rev. %s') % tr_uptorev
                    style = 'needs_update'
                with tr(w):
                    w(td(a(translation.dc_language(),
                           href=xml_escape(translation.absolute_url()))))
                    w(td(span(msg, Class=style)))

class NonMasterOdtTranslationStatus(EntityView):
    __select__ = is_instance('VersionedFile') & score_entity(lambda x: not x.pivot_lang)
    __regid__ = _('non_master_translation_status')

    def cell_call(self, row, col):
        _, w = self._cw._, self.w
        entity = self.cw_rset.get_entity(row, col)
        self.field(_('language :'), xml_escape(entity.dc_language()), tr=False)
        master = entity.master_document
        if not master:
            w(span(_('this document is not a master document and has no master set'),
                   Class="needs_update"))
            return
        self.field(_('master document :'), master.view('lang'), tr=False)
        mheadrev = master.branch_head().revision
        uptorev = entity.up_to_revision()
        status_label = u'<span class="%s">%s</span>'
        if uptorev is not None and uptorev != mheadrev:
            self.field(_('up to revision :'), status_label % ('needs_update', uptorev), tr=False)
            w(up_to_revision_form(entity))
        elif uptorev is None:
            self.field(_('up to revision :'), status_label % ('needs_update', _('unknown')), tr=False)
            if entity.head:
                # no up_to_revision_form if the file doesn't exists in this branch
                w(up_to_revision_form(entity))
        else:
            self.field(_('status :'), status_label % ('uptodate', _('up to date')), tr=False)


class EditionStatus(EntityView):
    __select__ = one_line_rset() & is_instance('VersionedFile')
    __regid__ = _('edition_status')
    _msg_help = _('Users having downloaded the editable version of the document are listed there. '
                  'You might want to coordinate with them to avoid edition conflicts later. '
                  'It is possible to assess one\'s intention not to make modifications.')
    _msg_nouser = _('No single user ever got this document in odt form. '
                    'Or they pretend not to make editions on it.')
    _msg_mightedit = (_('Might edit'), _('Edition conflicts are a pain. '
                                         'You should try to avoid them.'))
    _msg_hewontedit = (_('He will not edit'), _('God forbids !'))
    _msg_iwontedit = _('I will not edit'), _('I swear !')

    def cell_call(self, row, col):
        w, _ = self.w, self._cw._
        entity = self.cw_rset.get_entity(row, col)
        rset = self._cw.execute('Any U WHERE U might_edit VF, VF eid %(vfeid)s ',
                                {'vfeid' : entity.eid})
        with div(w, id='edition-status'):
            w(p(_(self._msg_help),
                Class='needsvalidation'))
            if not rset:
                w(p(_(self._msg_nouser),
                    Class='uptodate'))
                return
            self._cw.add_js('cubes.document.js')
            this_user = self._cw.user
            with table(w, Class='listing'):
                with tr(w):
                    for header in (_('user'), _('expectations')):
                        w(th(header))
                for idx, row in enumerate(rset.rows):
                    user = rset.get_entity(idx, 0)
                    if this_user.login == user.login:
                        value, title = self._msg_iwontedit
                    elif this_user.is_in_group('managers'):
                        value, title = self._msg_hewontedit
                    else:
                        value, title = self._msg_mightedit
                    value, title = _(value), _(title)
                    if user.eid == this_user.eid or this_user.is_in_group('managers'):
                        status = input(type='button', value=value, title=title, Class='validateButton',
                                       onclick="update_edition_status('%s', %s, false)" % (
                                           rql_for_eid(entity.eid), user.eid))
                    else:
                        status = p(value, title=title)
                    mail = user.use_email[0].address if user.use_email else None
                    userlink = a(user.name() if mail else user.name(),
                                 href=xml_escape('mailto:%s' % mail))
                    with tr(w):
                        w(td(userlink))
                        w(td(status))

class DocumentRevisionsView(EntityView):
    __select__ = is_instance('VersionedFile')
    __regid__ = 'revisions'

    def cell_call(self, row, col):
        _, w = self._cw._, self.w
        entity = self.cw_rset.get_entity(row, col)
        self._cw.add_js(('cubes.document.revision.js', 'cubes.document.js'))
        w(p(_('Inline diffs : you can click on the title to make it disappear.'),
            Class='needsvalidation'))
        with form(w, id="revisions_select", method="post", enctype="multipart/form-data",
                  action=entity.build_url('documentdiff')):
            legend = _('check two boxes to see a diff between the corresponding revisions')
            with table(w, Class='listing', title=legend):
                with tr(w):
                    for header in (_('show diff'), _('vcs revision'), _('branch'),
                                   _('author'), _('comment'), _('download')):
                        w(th(header))
                for vc in reversed(entity.reverse_content_for):
                    revision = vc.rev
                    rnum = revision.revision
                    if vc.is_deletion():
                        url = ''
                    else:
                        might_edit = str(vc.is_head()).lower()
                        url = a(_('download'),
                                href="javascript:download_document('%s', %s, %s, %s)" %
                                (rql_for_eid(entity.eid), self._cw.user.eid,
                                 vc.revision, might_edit))
                    with tr(w):
                        w(td(input(type="checkbox", value=str(rnum),
                                   onclick="check_boxes_of('#revisions_select', %s);" % entity.eid)))
                        for elt in (td(rnum), td(xml_escape(revision.branch)),
                                    td(xml_escape(revision.author)),
                                    td(xml_escape(revision.description)), td(url)):
                            w(elt)
        with div(self.w, id="documentdiff", style="display: none"):
            self.wview('diffform', self.cw_rset)


class DocumentDiffView(EntityView):
    __select__ = is_instance('VersionedFile')
    __regid__ = 'diff'

    def cell_call(self, row, col, rev1=None, rev2=None, **_kwargs):
        if not (rev1 and rev2):
            return
        entity = self.cw_rset.get_entity(row, col)
        r1 = int(rev1)
        r2 = int(rev2)
        assert r1 != r2, '%s == %s' % (r1, r2)
        if r1 > r2:
            r1, r2 = r2, r1
        rev1 = entity.revision(r1).data
        rev2 = entity.revision(r2).data
        with div(self.w, onclick="jqNode(this).hide('fast')"):
            self.w(h(1, self._cw._('Content diff (revision %(r1)s to %(r2)s)') % (r1, r2)))
            self.w(ndiff(rev1, rev2))
