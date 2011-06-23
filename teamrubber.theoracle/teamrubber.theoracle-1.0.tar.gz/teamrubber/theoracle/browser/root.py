from zope.interface import implements, providedBy, Interface
from Products.Five.browser import BrowserView
from teamrubber.theoracle.interfaces import IOracle,ICategory
from zope.component import getSiteManager, queryMultiAdapter
from zope.app.component.hooks import getSite

class TheOracle(BrowserView):
    implements(IOracle)
    
    def getBaseURL(self):
        site = getSite()
        if site is not None:
            return site.absolute_url()
        
        for parent in self.request.get("PARENTS",[])[::-1]:
            if hasattr(parent,'absolute_url'):
                return parent.absolute_url()

        return "/"
    
    def getCategories(self):
        sm = getSiteManager()
        result = []
        for name,factory in sm.adapters.lookupAll((providedBy(self),providedBy(self.request)),Interface):
            if ICategory.implementedBy(factory):
                result.append({'id':name,'title':factory.title})
        return result

    def getCurrentCategory(self):
        return self.request.form.get('category','request')

    def getCategoryContent(self):
        category = self.getCurrentCategory()
        view = queryMultiAdapter((self,self.request),Interface,name=category)
        
        if view is None or not ICategory.providedBy(view):
            return "Category not found"
        return view()
        
    def getPath(self):
        try:
            return '/'.join(self.context.getPhysicalPath())
        except AttributeError:
            return None