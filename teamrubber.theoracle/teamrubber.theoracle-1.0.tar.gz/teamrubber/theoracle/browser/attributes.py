from Products.Five.browser import BrowserView
from teamrubber.theoracle.interfaces import ICategory
from zope.interface import implements

def isFunction(method):
    """ Is something functionish, because callable is a bit generic for us """
    if method is None:
        return False
    if hasattr(method,'__class__'):
        if '<type' in repr(method.__class__):
            type_name = repr(method.__class__).split("'")[1]
            if type_name in ['function','instancemethod','builtin_function_or_method']:
                return True 
    else:
        pass
    return False

class Attributes(BrowserView):
    implements(ICategory)
    title = "Attributes"
    
    def __init__(self,context,request):
        self.oracle = context
        self.context = self.oracle.context
        self.request = request

    def getAttributes(self):
        result = []
        
        if hasattr(self.context,'aq_base'):
            ob = self.context.aq_base
        else:
            ob = self.context
        
        poss = set(dir(ob))

        # Remove stuff that is actually content
        if hasattr(ob,'objectIds'): #Object manager
            for id in ob.objectIds():
                poss.remove(id)
        
        for attr_name in poss:
            try:
                attr = getattr(self.context,attr_name)
            except AttributeError:
                attr = None
            
            
            if attr is not None and not isFunction(attr):
                result.append({'name':attr_name,'value':repr(attr)})
        
        result.sort(key=lambda x:x['name'])
        return result
        
        
        
