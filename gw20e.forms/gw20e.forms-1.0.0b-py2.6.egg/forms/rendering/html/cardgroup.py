from templates import CARDGROUP_TPL_HDR, CARDGROUP_TPL_FTR
from gw20e.forms.rendering.interfaces import IControlRenderer
from zope.interface import implements


class CardGroupRenderer:

    implements(IControlRenderer)

    def render(self, renderer, form, renderable, out, **kwargs):

        print >> out, CARDGROUP_TPL_HDR % renderer.createFormatMap(form, renderable, **kwargs)

        print >> out, "<ul>"

        for item in renderable.getRenderables():
            print >> out, """<li id="tab-%s">%s</li>""" % (item.id, item.label)

        print >> out, "</ul>"
        
        for item in renderable.getRenderables():        

            renderer.render(form, item, out, extra_classes="card")

        print >> out, CARDGROUP_TPL_FTR
