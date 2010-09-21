from zope.interface import implements

from plone.portlets.interfaces import IPortletDataProvider
from plone.app.portlets.portlets import base

from zope import schema
from zope.formlib import form
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from auslfe.portlet.multimedia import AuslfePortletMultimediaMessageFactory as _

from plone.app.vocabularies.catalog import SearchableTextSourceBinder
from Products.ATContentTypes.interface import IATTopic
from plone.app.form.widgets.wysiwygwidget import WYSIWYGWidget
from plone.app.form.widgets.uberselectionwidget import UberSelectionWidget
from plone.memoize.instance import memoize
from zope.component import getMultiAdapter
import random

from Products.ATContentTypes.interface import IImageContent

class IAuslfePortletMultimedia(IPortletDataProvider):
    """A portlet"""

    portlet_title = schema.TextLine(title=_(u"multimedia_title_label", default=u"Portlet title"),
                               required = True)
    
    portlet_text = schema.Text(title=_(u"multimedia_text_label", default=u"Portlet text"),
                               description=_(u"multimedia_text_help", default=u"Insert there a text you want to display above the multimedia data."),
                               required=False)
    
    target_collection = schema.Choice(title=_(u"multimedia_archive_label", default=u"Images archive"),
                                      description=_(u"multimedia_archive_help", default=u"Select a collection that contains all your image or image-like contents."),
                                      required=False,
                                      source=SearchableTextSourceBinder({'object_provides' : IATTopic.__identifier__},
                                                                        default_query='path:'))
    
    target_collection_title = schema.TextLine(title=_(u"multimedia_archive_title_label", default=u"Label of the link to archive"),
                                              description=_(u"multimedia_archive_title_help", default=(u"You can customize the link to the archive "
                                                                                                        "(if empty, will be \"All images\").")),
                                              required=False)
    
    random = schema.Bool(title=_(u"multimedia_random_label", default=u"Choose random images"),
                         description=_(u"multimedia_random_help", default=u"If checked, the normal sorting of the collection will be ignored, and random images will be returned"),
                         required=False,
                         default=True)

    client_reload = schema.Bool(title=_(u"multimedia_client_random_label", default=u"Random reload at client side"),
                                description=_(u"multimedia_client_random_help", default=u"If checked, and if you choose for random images, they will be changed every 30 seconds"),
                                required=False,
                                default=False)
    
    portlet_class = schema.TextLine(title=_(u"multimedia_css_label", default=u"CSS class"),
                                   description=_(u"multimedia_css_help", default=u"Put there additional CSS class(es) that will be added to the HTML"),
                                   required=False)


class Assignment(base.Assignment):
    """Portlet assignment"""

    implements(IAuslfePortletMultimedia)
    
    client_reload = False
    
    def __init__(self, portlet_title='', portlet_text='', target_collection=None,
                 target_collection_title='', random=True, portlet_class='', client_reload=False):
        """
        """        
        base.Assignment.__init__(self)
        self.portlet_title = portlet_title
        self.portlet_text = portlet_text
        self.target_collection = target_collection
        self.target_collection_title = target_collection_title
        self.random = random
        self.portlet_class = portlet_class
        self.client_reload = client_reload

    @property
    def title(self):
        """This property is used to give the title of the portlet in the
        "manage portlets" screen.
        """
        return _(u"Multimedia portlet") + (self.portlet_title and ": "+self.portlet_title or '')

class Renderer(base.Renderer):
    """Portlet renderer"""

    render = ViewPageTemplateFile('auslfeportletmultimedia.pt')
    
    def getPortletClass(self):
        if self.data.portlet_class:
            return self.data.portlet_class
        else:
            return ""
    
    @memoize
    def targetCollection(self):
        """Get the collection the portlet is pointing to"""
        
        target_collection = self.data.target_collection
        if not target_collection:
            return None

        if target_collection.startswith('/'):
            target_collection = target_collection[1:]
        
        if not target_collection:
            return None

        portal_state = getMultiAdapter((self.context, self.request), name=u'plone_portal_state')
        portal = portal_state.portal()
        return portal.restrictedTraverse(target_collection, default=None)
    
    def limit(self):
        if self.targetCollection():
            return self.targetCollection().getItemCount()
        return 0
    
    def getTargetCollectionPath(self):
        """Restituisce l'url della collezione che fornisce le foto da visualizzare"""
        
        collection = self.targetCollection()
        if collection is None:
            return None
        else:
            return collection.absolute_url()
        
    def results(self):
        """Get the actual result brains from the collection"""
        if self.data.random:
            return self.randomResults()
        return self.standardResults()
        
    @memoize
    def standardResults(self):
        collection = self.targetCollection()
        limit = collection.getItemCount()
        if collection is not None:
            if limit:
                return collection.queryCatalog()[:limit]
            return collection.queryCatalog(object_provides=IImageContent.__identifier__)
        return []
        
    def randomResults(self):
        collection = self.targetCollection()
        if collection is not None:
            limit = collection.getItemCount()
            if collection is not None:
                results = [x for x in collection.queryCatalog(sort_on=None,
                                                              object_provides=IImageContent.__identifier__)]
                try:
                    random.shuffle(results)
                    if limit:
                        return results[:limit]
                    return results
                except AttributeError:
                    return []
        return []
    

class AddForm(base.AddForm):
    """Portlet add form"""
    form_fields = form.Fields(IAuslfePortletMultimedia)
    form_fields['portlet_text'].custom_widget = WYSIWYGWidget
    form_fields['target_collection'].custom_widget = UberSelectionWidget

    def create(self, data):
        return Assignment(**data)


class EditForm(base.EditForm):
    """Portlet edit form"""
    form_fields = form.Fields(IAuslfePortletMultimedia)
    form_fields['portlet_text'].custom_widget = WYSIWYGWidget
    form_fields['target_collection'].custom_widget = UberSelectionWidget
