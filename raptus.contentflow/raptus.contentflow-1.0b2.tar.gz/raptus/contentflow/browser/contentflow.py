from zope.component import getMultiAdapter, queryAdapter

from plone.memoize.instance import memoize
from plone.app.layout.viewlets.common import ViewletBase

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from raptus.contentflow.interfaces import IContentFlowProperties

class Viewlet(ViewletBase):
    """ Viewlet displaying the contentflow
    """
    index = ViewPageTemplateFile('contentflow.pt')
    
    def render(self):
        if not getMultiAdapter((self.context, self.request), name=self.xmlPath()).items():
            return ''
        return super(Viewlet, self).render()
    
    @property
    @memoize
    def properties(self):
        return dict(queryAdapter(self.context, interface=IContentFlowProperties)())
    
    @memoize
    def width(self):
        return self.properties and self.properties.get('width', '100%') or '100%'
    
    @memoize
    def height(self):
        return self.properties and self.properties.get('height', '300') or '300'
    
    @memoize
    def backgroundColor(self):
        return self.properties and self.properties.get('backgroundColor', '0x000000') or '0x000000'
    
    @memoize
    def labelColor(self):
        return self.properties and self.properties.get('labelColor', '0xFFFFFF') or '0xFFFFFF'
    
    @memoize
    def xmlPath(self):
        return self.properties and self.properties.get('xmlPath', 'contentflow.data.xml') or 'contentflow.data.xml'
