from templates import CONTROL_HDR, CONTROL_FTR, RICHTEXT_TPL
from gw20e.forms.rendering.interfaces import IControlRenderer
from zope.interface import implements



class RichTextRenderer:

    implements(IControlRenderer)

    def render(self, renderer, form, renderable, out, **kwargs):

        """ render Input to HTML """
        
        fmtmap = renderer.createFormatMap(form, renderable, **kwargs)

        fmtmap['value'] = form.data[renderable.bind] or ""
        fmtmap['richconfig'] = renderer.opts.get('richconfig', '')
    
        print >> out, CONTROL_HDR % fmtmap    
        print >> out, RICHTEXT_TPL % fmtmap
        print >> out, CONTROL_FTR
