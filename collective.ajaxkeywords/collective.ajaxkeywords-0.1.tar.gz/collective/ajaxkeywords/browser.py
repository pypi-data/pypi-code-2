from five import grok
from plone.app.layout.viewlets.interfaces import IBelowContent
from plone.app.layout.globals.interfaces import IViewView
from plone.app.layout.globals.interfaces import Interface
from Products.CMFCore.utils import getToolByName
from AccessControl import getSecurityManager
from Products.CMFCore import permissions

class TagsViewlet(grok.Viewlet):
    """Show a jquery keywords/tags widget 
    """

    grok.name('collective.ajaxkeywords.TagsViewlet')
    grok.require('zope2.View')
    grok.context(Interface)
    grok.view(IViewView)
    grok.viewletmanager(IBelowContent)
    
    def getJS(self):
        if(getSecurityManager().checkPermission(permissions.ModifyPortalContent, self.context)):
            allowEdit = 'true'
        else:
            allowEdit = 'false'
        return """
        $(document).ready(function(){
            $('#ajaxkeywords').tagHandler({
                getURL: '/%s/subjectsasjson',
                updateURL: '/%s/setsubjects',
                autocomplete: true,
                allowEdit: %s
            });
        });""" % (self.context.virtual_url_path(), self.context.virtual_url_path(), allowEdit)
    
class SubjectsAsJson(grok.View):
    """Show the Subjects as JSON object
    """
    
    grok.context(Interface)
    grok.require('zope2.View')
    grok.name('subjectsasjson')
    
    def render(self):
        available_keywords = sorted(getToolByName(self.context, 'portal_catalog').uniqueValuesFor('Subject'))
        selected_keywords = sorted(self.context.Subject())
        recommended_keywords = sorted([""])
        
        available_keywords = map(lambda k: '"%s"' % k,  available_keywords)
        selected_keywords = map(lambda k: '"%s"' % k,  selected_keywords)
        recommended_keywords = map(lambda k: '"%s"' % k,  recommended_keywords)
        return '{"availableTags": [%s], "assignedTags": [%s], "recommendedTags": [%s]}' % (', '.join(available_keywords), 
                                                                                           ', '.join(selected_keywords),
                                                                                           ', '.join(recommended_keywords))
class SetSubjects(grok.View):
    """Show the Subjects as JSON object
    """
    
    grok.context(Interface)
    grok.require('cmf.ModifyPortalContent')
    grok.name('setsubjects')
    
    def render(self):
        if('tags[]' in self.request.form):
            self.context.setSubject(self.request.form['tags[]'])
            self.context.reindexObject(idxs=['Subject'])
            return ""
        
        return "bad request", self.request
        
    