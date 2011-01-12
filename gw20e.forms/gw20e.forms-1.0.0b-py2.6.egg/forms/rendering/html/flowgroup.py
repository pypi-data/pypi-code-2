from templates import FLOWGROUP_TPL_HDR, FLOWGROUP_TPL_FTR
from gw20e.forms.rendering.interfaces import IControlRenderer
from zope.interface import implements


class FlowGroupRenderer:

    implements(IControlRenderer)

    def render(self, renderer, form, renderable, out, **kwargs):


        """ Render flow group that flows horizontally or vertically """

        print >> out, FLOWGROUP_TPL_HDR % renderer.createFormatMap(form, renderable, **kwargs)

        for item in renderable.getRenderables():

            renderer.render(form, item, out)

        print >> out, FLOWGROUP_TPL_FTR
