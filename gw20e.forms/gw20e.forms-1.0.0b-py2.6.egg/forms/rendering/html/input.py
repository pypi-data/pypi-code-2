from templates import CONTROL_HDR, CONTROL_FTR
from gw20e.forms.rendering.interfaces import IControlRenderer
from zope.interface import implements


INPUT_TPL = """<input id="input-%(id)s" type="text" name="%(id)s" value="%(value)s" size="%(cols)s"/>"""

INPUT_LARGE_TPL = """<textarea id="input-%(id)s" name="%(id)s" rows="%(rows)s" cols="%(cols)s">%(value)s</textarea>"""


class InputRenderer:

    implements(IControlRenderer)

    def render(self, renderer, form, renderable, out, **kwargs):

        """ render Input to HTML """
    
        fmtmap = renderer.createFormatMap(form, renderable, **kwargs)

        try:
            fmtmap['value'] = form.data[renderable.bind] or ""
        except:
            fmtmap['value'] = ""
            
        print >> out, CONTROL_HDR % fmtmap
    
        if fmtmap.get("rows", 1) == 1:
            print >> out, INPUT_TPL % fmtmap
        else:
            print >> out, INPUT_LARGE_TPL % fmtmap
                   
        print >> out, CONTROL_FTR
