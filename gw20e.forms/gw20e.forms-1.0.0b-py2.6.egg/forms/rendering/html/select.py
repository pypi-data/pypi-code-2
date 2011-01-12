from templates import *
from gw20e.forms.rendering.interfaces import IControlRenderer
from zope.interface import implements


SELECT_HDR_TPL = """<select id="input-%(id)s" name="%(id)s" %(multiple)s size="%(size)s">"""

SELECT_FTR_TPL = """</select>"""


class SelectRenderer:

    implements(IControlRenderer)

    def render(self, renderer, form, renderable, out, **kwargs):

        fmtmap = renderer.createFormatMap(form, renderable, **kwargs)

        print >> out, CONTROL_HDR % fmtmap

        if renderable.format == "full":

            value = form.data[renderable.bind]

            for opt in renderable.options:
                optfmt = renderer.createFormatMap(form, opt)
                optfmt.update({"id":renderable.id})

                if hasattr(value, "__iter__") and opt.value in value:
                    optfmt.update({'checked': 'checked="yes"'})
                elif opt.value == value:
                    optfmt.update({'checked': 'checked="yes"'})                
                else:
                    optfmt.update({'checked': ""})

                if renderable.multiple:
                    print >> out, CHECK_TPL % optfmt
                else:
                    print >> out, RADIO_TPL % optfmt
        else:
            print >> out, SELECT_HDR_TPL % fmtmap

            value = form.data[renderable.bind]

            for opt in renderable.options:
                
                if hasattr(value, "__iter__") and opt.value in value:
                    opt.selected = "selected"
                elif opt.value == value:
                    opt.selected = "selected"
                else:
                    opt.selected = ""
                    
                print >> out, OPTION_TPL % renderer.createFormatMap(form, opt)
                   
            print >> out, SELECT_FTR_TPL

        print >> out, CONTROL_FTR
