from templates import TEXT_TPL
from gw20e.forms.rendering.interfaces import IControlRenderer
from zope.interface import implements


class TextRenderer:

    implements(IControlRenderer)

    def render(self, renderer, form, renderable, out, **kwargs):

        print >> out, TEXT_TPL % renderer.createFormatMap(form, renderable)
