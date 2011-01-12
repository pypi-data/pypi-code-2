from zope.interface import implements

from gw20e.forms.rendering.interfaces import IRenderer
from gw20e.forms.rendering.baserenderer import BaseRenderer

from select import SelectRenderer
from checkbox import CheckboxRenderer
from input import InputRenderer
from text import TextRenderer
from cardgroup import CardGroupRenderer
from flowgroup import FlowGroupRenderer
from stepgroup import StepGroupRenderer
from submit import SubmitRenderer
from richtext import RichTextRenderer
from file import FileRenderer


class HTMLRenderer(BaseRenderer):

    """ The HTML renderer expects to recive some kind of output
    stream, that can be used to append to. This can obviously be
    sys.stdout, but also a stringIO instance.
    """
    
    implements(IRenderer)


    def __init__(self, **kwargs):

        BaseRenderer.__init__(self, **kwargs)
        
        self.registerType("submit", SubmitRenderer())
        self.registerType("text", TextRenderer())
        self.registerType("input", InputRenderer())
        self.registerType("file", FileRenderer())
        self.registerType("checkbox", CheckboxRenderer())
        self.registerType("richtext", RichTextRenderer())
        self.registerType("select", SelectRenderer())
        self.registerType("flowgroup", FlowGroupRenderer())
        self.registerType("cardgroup", CardGroupRenderer())
        self.registerType("stepgroup", StepGroupRenderer())        


    def renderFrontMatter(self, form, out):

        """ Render whatever needs to be rendered before the actual form
        components """
        
        print >> out, """<form class="gw20e-form" method="post" action="%s" enctype="multipart/form-data">""" % getattr(form.submission, 'action', '')
        print >> out, """<input type="hidden" name="formprocess" value="1"/>"""
        print >> out, """<div class="alert"></div>"""


    def renderBackMatter(self, form, out):

        print >> out, "</form>"


    def render(self, form, renderable, out, **kwargs):

        try:            
            rtype = renderable.type
            renderer = self.getRendererForType(rtype)
            renderer.render(self, form, renderable, out, **kwargs)
        except:
            print >> out, "<blink>No renderer found for %s!</blink>" % rtype
