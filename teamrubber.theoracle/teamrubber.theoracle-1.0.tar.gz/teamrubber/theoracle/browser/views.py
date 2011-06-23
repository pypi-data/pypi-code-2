from Products.Five.browser import BrowserView
from teamrubber.theoracle.interfaces import ICategory
from zope.interface import implements, Interface
from zope.component import getSiteManager, providedBy

class Views(BrowserView):
    implements(ICategory)
    title = "Browser views"
    
    def getViews(self):
        sm = getSiteManager()
        result = []
        views = sm.adapters.lookupAll(map(providedBy,(self.context,self.request)), Interface)
        views = sorted(views)
        for name,view in views:
            if not ICategory.implementedBy(view):
                if hasattr(view,'__of__'):
                    
                    permission = getattr(view,'__ac_permissions__',None)
                    if permission is not None:
                        if not permission:
                            permission = "Public"
                        else:
                            permission = permission[0][0]
                    
                    template = ""
                    index = getattr(view,'index',None)
                    if index is not None:
                        template = getattr(index,'filename','')
                    
                    
                    if name:
                        result.append({'name':name,
                                       'doc':getattr(view,'__doc__',None),
                                       'template':template,
                                       'permission':permission})
        
        return result
            
            