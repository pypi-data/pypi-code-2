from zope.app.component.hooks import getSite
from zope.interface import implements
from zope.component import getMultiAdapter, getUtility
from zope.app.container.interfaces import INameChooser
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Acquisition import aq_base, aq_inner, aq_parent
from OFS.SimpleItem import SimpleItem
from Products.Five.browser import BrowserView
from Products.statusmessages.interfaces import IStatusMessage


class PrintAll(BrowserView):
    """ Render all folder pages as continuos view for printing """
    
    index = ViewPageTemplateFile("all.pt")
            
    def __call__(self):
        
        objects = []
        # Walk through all objects recursively
        
        def walk(folder, level):
                        
            for id, object in folder.contentItems():
                
                if object.portal_type == "Image":
                    continue
                
                objects.append({"object":object, "level":level} )
        
                if object.portal_type == "Folder":
                    walk(object,level+1)
                    
        
        walk(self.context, 1)
        
        self.objects = objects
        
        return self.index()