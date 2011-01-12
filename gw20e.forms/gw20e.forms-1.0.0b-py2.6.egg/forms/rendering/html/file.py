from templates import CONTROL_HDR, CONTROL_FTR
from gw20e.forms.rendering.interfaces import IControlRenderer
from zope.interface import implements


FILE_TPL = """<input id="input-%(id)s" type="file" name="%(id)s" value="%(value)s"/>"""


class FileRenderer:

    implements(IControlRenderer)

    def render(self, renderer, form, renderable, out, **kwargs):

        """ render File to HTML """
    
        fmtmap = renderer.createFormatMap(form, renderable, **kwargs)

        try:
            fmtmap['value'] = form.data[renderable.bind] or ""
        except:
            fmtmap['value'] = ""
            
        print >> out, CONTROL_HDR % fmtmap
        print >> out, FILE_TPL % fmtmap
        print >> out, CONTROL_FTR
