"""Custom form for tracker

:organization: Logilab
:copyright: 2003-2010 LOGILAB S.A. (Paris, FRANCE), license is LGPL.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
"""
__docformat__ = "restructuredtext en"

from datetime import datetime

from cubicweb.selectors import is_instance, match_transition, attribute_edited
from cubicweb.web import uicfg, formfields
from cubicweb.web.views import workflow, editviews
from cubicweb.web.views.autoform import AutomaticEntityForm


_afs = uicfg.autoform_section
_afs.tag_attribute(('Version', 'publication_date'), 'main', 'hidden')
_afs.tag_attribute(('Version', 'starting_date'), 'main', 'attributes')
_afs.tag_attribute(('Version', 'prevision_date'), 'main', 'attributes')
_afs.tag_subject_of(('Version', 'version_of', 'Project'), 'main', 'hidden')
_afs.tag_object_of(('Version', 'version_of', 'Project'), 'main', 'hidden')
_afs.tag_subject_of(('Ticket', 'concerns', 'Project'), 'main', 'attributes')
_afs.tag_object_of(('Ticket', 'concerns', 'Project'), 'main', 'hidden')
_afs.tag_subject_of(('Ticket', 'done_in', 'Version'), 'main', 'attributes')

def ticket_done_in_choices(form, field):
    entity = form.edited_entity
    # first see if its specified by __linkto form parameters
    linkedto = formfields.relvoc_linkedto(entity, 'done_in', 'subject')
    if linkedto:
        return linkedto
    # it isn't, check if the entity provides a method to get correct values
    vocab = formfields.relvoc_init(entity, 'done_in', 'subject')
    if not entity.has_eid():
        peids = entity.linked_to('concerns', 'subject')
        peid = peids and peids[0]
        veid = None
    else:
        peid = entity.project.eid
        veid = entity.done_in and entity.done_in[0].eid
    if peid:
        rschema = form._cw.vreg.schema['done_in'].rdef('Ticket', 'Version')
        rset = form._cw.execute(
            'Any V, VN, P ORDERBY version_sort_value(VN) '
            'WHERE V version_of P, P eid %(p)s, V num VN, '
            'V in_state ST, NOT ST name "published"', {'p': peid})
        vocab += [(v.view('combobox'), unicode(v.eid)) for v in rset.entities()
                  if rschema.has_perm(form._cw, 'add', toeid=v.eid)
                  and not v.eid == veid]
    return vocab

_affk = uicfg.autoform_field_kwargs
_affk.tag_attribute(('Ticket', 'priority'), {'sort': False})
_affk.tag_subject_of(('Ticket', 'done_in', '*'), {'sort': False,
                                                  'choices': ticket_done_in_choices})

from cubicweb.web.formfields import eid_param, role_name

class VersionChangeStateForm(workflow.ChangeStateForm):
    __select__ = is_instance('Version') & (match_transition('publish')
                                           | attribute_edited('publication_date'))

    publication_date = formfields.DateField(eidparam=True, role='subject',
                                            fallback_on_none_attribute=True,
                                            value=lambda form: datetime.now())


class ShortComboboxView(editviews.ComboboxView):
    """by default combobox view is redirecting to textoutofcontext view
    but in the case of projects we want a shorter view
    """
    __select__ = is_instance('Project')
    def cell_call(self, row, col):
        self.w(self.cw_rset.get_entity(row, col).dc_title())


def registration_callback(vreg):
    vreg.register_all(globals().values(), __name__)
    if 'preview' in vreg.config.cubes():

        from cubes.preview.views.forms import PreviewFormMixin
        class PreviewForm(PreviewFormMixin, AutomaticEntityForm):
            __select__ = AutomaticEntityForm.__select__ & is_instance('Ticket', 'Version')
            preview_mode = 'inline'

        vreg.register(PreviewForm)
