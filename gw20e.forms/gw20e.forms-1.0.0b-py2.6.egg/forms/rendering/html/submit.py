from templates import SUBMIT_TPL
from gw20e.forms.rendering.interfaces import IControlRenderer
from zope.interface import implements


class SubmitRenderer:

    implements(IControlRenderer)

    def render(self, renderer, form, renderable, out, **kwargs):

        print >> out, SUBMIT_TPL % renderer.createFormatMap(form, renderable)
