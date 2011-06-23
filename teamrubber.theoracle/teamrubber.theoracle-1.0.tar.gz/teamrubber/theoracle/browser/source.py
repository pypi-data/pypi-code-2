from Products.Five.browser import BrowserView
from teamrubber.theoracle.interfaces import ICategory
from zope.interface import implements
import inspect

from teamrubber.theoracle.utils import safe_import

try:
    from pygments import highlight
    from pygments.lexers import PythonLexer
    from pygments.formatters import HtmlFormatter
    pygments_installed = True
except ImportError:
    pygments_installed = False

from zope.app.component.hooks import getSite


class SourceBase(BrowserView):

    def getBaseURL(self):
        site = getSite()
        if site is not None:
            return site.absolute_url()
        
        for parent in self.request.get("PARENTS",[])[::-1]:
            if hasattr(parent,'absolute_url'):
                return parent.absolute_url()

        return "/"

    def __init__(self,context,request):
        self.context = context
        self.request = request

    def getObject(self):
        name = self.request.get('object',None)
        if name is not None:
            return safe_import(name)
        return self.context

    def getStyle(self):
        if pygments_installed:
            return HtmlFormatter().get_style_defs()
        return ''
    
    def getSource(self,context=None):
        if context is None:
            context = self.context.__class__
            
        try:
            filename = inspect.getsourcefile(context)
        except:
            filename = None
            
        try:
            source = inspect.getsource(context)
        except:
            source = None

        try:
            module = context.__module__
        except AttributeError:
            module = None

        # Get starting line number
        start = 0
        end = 0
        if filename is not None and source is not None:
            full_source = open(filename).read()
            index = full_source.find(source)    
            start = len(full_source[:index].split('\n'))
            

        structure = False
        if source is not None:
            end = start + len(source.split('\n'))
            if pygments_installed:
                structure = True
                source = highlight(source, PythonLexer(), HtmlFormatter())

        return {'source':source,
                'filename':filename,
                'start':start,
                'end':end,
                'structure':structure,
                'module':module}




class Source(SourceBase):
    implements(ICategory)
    title = "Source"
    
    def __init__(self,context,request):
        self.oracle = context
        self.context = self.oracle.context
        self.request = request
