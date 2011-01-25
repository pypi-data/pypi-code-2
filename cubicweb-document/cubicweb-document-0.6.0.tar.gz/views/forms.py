"""forms used by the document cube

:organization: Logilab
:copyright: 2008-2010 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
"""
__docformat__ = "restructuredtext en"
_ = unicode

from cubicweb import ValidationError, tags
from cubicweb.selectors import is_instance
from cubicweb.view import EntityView
from cubicweb.web import Redirect, eid_param
from cubicweb.web.form import FormViewMixIn
from cubicweb.web.formfields import StringField
from cubicweb.web.formwidgets import Select, SubmitButton
from cubicweb.web.controller import Controller

from cubes.vcsfile.views import forms
from cubes.document.html import div, ul, li, span

def up_to_revision_form(vdoc):
    req = vdoc.req
    form = vdoc.vreg['forms'].select('base', req,
                                     entity=vdoc.head,
                                     form_renderer_id='base',
                                     action=req.build_url('documentsetuptorev'),
                                     form_buttons=[SubmitButton()])
    uptorev = vdoc.up_to_revision()
    if uptorev is None:
        uptorev = -1
    branch = vdoc.head.rev.branch
    vocab = ['%s (%s)' % (vc.rev.revision, vc.rev.branch)
             for vc in vdoc.master_document.reverse_content_for
             if branch == vc.rev.branch and vc.rev.revision > uptorev]
    form.append_field(StringField(name="up_to_revision", eidparam=True,
                                  label=_('change to :'), widget=Select,
                                  choices=vocab))
    return form.render()


class DocumentSetUpToRevisionController(Controller):
    """simple controller setting the up_to_revision relation for a folder"""
    __regid__ = 'documentsetuptorev'

    def publish(self, rset=None):
        """publish the current request, with an option input rql string
        (already processed if necessary)
        """
        for eid in self._cw.edited_eids():
            formparams = self._cw.extract_entity_params(eid, minparams=2)
            vc = self._cw.eid_rset(eid).get_entity(0, 0)
            rev = int(formparams['up_to_revision'].split()[0]) # XXX split???
            vc.set_up_to_master_revision(rev)
        goto = self._cw.form.get('__redirectpath')
        if goto:
            raise Redirect(self._cw.build_url(goto))
        raise Redirect(vc.file.absolute_url())


class DocumentUploadNewFormView(forms.VFUploadFormView):
    """upload a new document"""
    __regid__ = 'documentuploadnewform'
    __select__ = is_instance('Folder')

    def form_title(self, _entity):
        return self._cw._('Upload a new document')


class DocumentUploadTranslationFormView(forms.VFUploadFormView):
    """upload a new translation of a document"""
    __regid__ = 'documentuploadnewtranslationform'
    __select__ = is_instance('VersionedFile')


    submitmsg = _('new translation has been checked-in')
    action = 'documentuploadtranslation' # XXX controller in docaster

    def form_title(self, entity):
        return self._cw._('Upload a new translation for %s') % tags.a(
            entity.dc_title(), href=entity.absolute_url())

    def get_form(self, entity):
        form = super(DocumentUploadTranslationFormView, self).get_form(entity)
        vocab = [('%s (%s)' % (self._cw._(name), code), eid)
                 for eid, code, name in entity.untranslated_langs]
        form.append_field(StringField(name=_('lang'), eidparam=True,
                                      widget=Select, choices=vocab))
        return form


class ShowDiffFormView(FormViewMixIn, EntityView):
    """show diff between two revisions"""
    __regid__ = 'diffform'
    __select__ = is_instance('VersionedFile')

    def cell_call(self, row, col, **_kwargs):
        _ = self._cw._
        return u'NOT IMPLEMENTED'
        # XXX generic diff for vcsfile
