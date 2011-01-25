"""action links used by the document cube

:organization: Logilab
:copyright: 2008-2010 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
"""
__docformat__ = "restructuredtext en"
_ = unicode

from cubicweb.selectors import is_instance, one_line_rset, score_entity
from cubicweb.web import action


class DocumentPutTranslation(action.Action):
    __regid__ = 'documentputtranslation'
    __select__ = (one_line_rset() & is_instance('VersionedFile')
                  & score_entity(lambda x: len(x.lang))
                  & score_entity(lambda x: x.pivot_lang or 0)
                  & score_entity(lambda x: len(x.untranslated_langs)))

    title = _('upload document translation')
    category = 'mainactions'

    def url(self):
        return self.cw_rset.get_entity(0, 0).absolute_url(vid='documentuploadnewtranslationform')


# XXX vcsaddform defined in docaster
class VcsAddAction(action.Action):
    __regid__ = 'vcsaddaction'
    __select__ = one_line_rset() & is_instance('File')

    title = _('add this file in the repository')
    category = 'mainactions'

    def url(self):
        return self.cw_rset.get_entity(0, 0).absolute_url(vid='vcsaddform')


def registration_callback(vreg):
    vreg.register_all(globals().values(), __name__)
    # disable some vcsfile actions
    from cubes.vcsfile.views import actions
    for actioncls in (actions.VFHEADRevisionAction,
                      actions.VFAddRevisionAction,
                      actions.VFAllRevisionsAction,
                      actions.VCHeadRevisionAction,
                      actions.VCAllRevisionsAction,
                                            ):
        vreg.unregister(actioncls)
