from templates import CONTROL_HDR, CONTROL_FTR, COLORPICKER_TPL
from gw20e.forms.rendering.interfaces import IControlRenderer
from zope.interface import implements


class ColorPickerRenderer:

    implements(IControlRenderer)

    def render(self, renderer, form, renderable, out, **kwargs):
        
        fmtmap = renderer.createFormatMap(form, renderable, **kwargs)
        
        fmtmap['value'] = form.data[renderable.bind] or ""

        print >> out, CONTROL_HDR % fmtmap
        print >> out, COLORPICKER_TPL % fmtmap
        print >> out, CONTROL_FTR
