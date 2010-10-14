"""cube-specific forms/views/actions/components

Specific views for cards

:organization: Logilab
:copyright: 2001-2010 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
"""
__docformat__ = "restructuredtext en"
_ = unicode

from cubicweb.selectors import is_instance
from cubicweb.web import uicfg
from cubicweb.web.views import primary
from cubicweb.web.views.autoform import AutomaticEntityForm

uicfg.primaryview_section.tag_attribute(('Card', 'title'), 'hidden')
uicfg.primaryview_section.tag_attribute(('Card', 'synopsis'), 'hidden')
uicfg.primaryview_section.tag_attribute(('Card', 'wikiid'), 'hidden')

class CardPrimaryView(primary.PrimaryView):
    __select__ = is_instance('Card')
    show_attr_label = False

    def summary(self, entity):
        return entity.dc_description('text/html')


class CardInlinedView(CardPrimaryView):
    """hide card title and summary"""
    __regid__ = 'inlined'
    title = _('inlined view')
    main_related_section = False

    def render_entity_title(self, entity):
        pass

    def render_entity_metadata(self, entity):
        pass

    def content_navigation_components(self, context):
        pass


def registration_callback(vreg):
    vreg.register(CardPrimaryView)
    vreg.register(CardInlinedView)
    if 'preview' in vreg.config.cubes():

        from cubes.preview.views.forms import PreviewFormMixin
        class PreviewAutomaticEntityForm(PreviewFormMixin, AutomaticEntityForm):
            preview_mode = 'inline'
            __select__ = AutomaticEntityForm.__select__ & is_instance('Card')

        vreg.register(PreviewAutomaticEntityForm)

