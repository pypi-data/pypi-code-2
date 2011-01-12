from templates import CONTROL_HDR, CONTROL_FTR, CHECK_TPL
from gw20e.forms.rendering.interfaces import IControlRenderer
from zope.interface import implements


class CheckboxRenderer:

    implements(IControlRenderer)

    def render(self, renderer, form, renderable, out, **kwargs):

        """ render Input to HTML """

        value = form.data[renderable.bind]
        fmtmap = renderer.createFormatMap(form, renderable, **kwargs)

        fmtmap['checked'] = ""
        fmtmap['value'] = "1"
            
        if value:
            fmtmap['checked'] = 'checked="yes"'
            
        print >> out, CONTROL_HDR % fmtmap
        print >> out, CHECK_TPL % fmtmap                   
        print >> out, CONTROL_FTR
