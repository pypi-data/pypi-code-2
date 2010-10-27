from Products.Archetypes.public import BaseFolderSchema, Schema
from Products.Archetypes.public import StringField, LinesField, ComputedField, ComputedWidget
from Products.Archetypes.public import LinesWidget, TextAreaWidget, IdWidget, StringWidget
from Products.Archetypes.public import BaseFolder, registerType
from Products.CMFCore import permissions

from Products.ATContentTypes.content.base import ATCTFolder

import Products.SimpleBlog.Permissions
from Products.SimpleBlog.config import PROJECTNAME


schema = ATCTFolder.schema.copy() +  Schema((
    StringField('description',
                isMetadata=1,
                accessor='Description',
                widget=TextAreaWidget(label='Description',
                                      label_msgid="label_blogfolder_description",
                                      description_msgid="help_blogfolder_description",
                                      i18n_domain="SimpleBlog",
                                      description='Give a description for this SimpleBlog folder.'),),
    ComputedField('existingCats',
                  expression='here.getInheritedCategories()',
                  widget=ComputedWidget(label='Existing categories.',
                                  label_msgid="label_blogfolder_existing_cats",
                                  i18n_domain="SimpleBlog",)),
    LinesField('categories',
               widget=LinesWidget(label='Additional categories',
                                  label_msgid="label_additional_categories",
                                  description_msgid="help_additional_categories",
                                  i18n_domain="SimpleBlog",
                                  description='Supply a list of possible additional categories that will be available to BlogEntries inside this folder or in sub folders.'),
               )
        ))


class BlogFolder(ATCTFolder):
    """
    A folder object to store BlogEntries in
    """

    schema = schema

    def canSetDefaultPage(self):
        return False

    def getInheritedCategories(self):
        # traverse upwards in the tree to collect all the available categories
        # stop collecting when a SimpleBlog object is reached

        cats=[]
        parent=self.aq_parent
        portal=self.portal_url.getPortalObject()
        categories='<ul>'
        while parent!=portal:
           if parent.portal_type=='Blog' or parent.portal_type=='BlogFolder':
               # add cats
               pcats=parent.getCategories()
               for c in pcats:
                   if c not in cats:
                       categories=categories + '<li>' + c + '</li>'
                       cats.append(c)
               if parent.portal_type=='Blog':
                   break
           parent=parent.aq_parent
        categories = categories + '</li>'
        if len(cats)==0:
            return '-'
        else:
            return categories

    def getEntries(self, maxResults=None, **kwargs):
        """ Return all the contained published entries, real objects, not the brains """
        # see simpleblog_tool.searchForEntries for API description

        query=kwargs

        publishedState = self.simpleblog_tool.getPublishedState()

        query['getAlwaysOnTop']=1

        # first the items that need to be listed on top
        localOnTop = self.portal_catalog.searchResults(query, meta_type='BlogEntry', path={'query':self.simpleblog_tool.getObjectPath(self),'level':0}, sort_order='reverse', sort_on='effective')
        localOnTop = [r.getObject() for r in localOnTop ]

        # then the other items
        query['getAlwaysOnTop']=0
        localNoTop = self.portal_catalog.searchResults(query, meta_type='BlogEntry', path={'query':self.simpleblog_tool.getObjectPath(self),'level':0}, sort_order='reverse', sort_on='effective')
        localNoTop= [r.getObject() for r in localNoTop]

        results = localOnTop+localNoTop

        # make compatible with simpleblog_view/Blog.getEntries
        results = [(e,0) for e in results]
        if maxResults==0:
            return results
        elif maxResults==None:
            return results[:self.simpleblog_tool.getMaxItemsInPortlet()]
        else:
            return results[:maxResults]

    def synContentValues(self):
        # get brains for items that are published within the context of this blog.
        entries = self.simpleblog_tool.searchForEntries(self, fromHere=1, maxResults=0)

        # convert to objects
        objs = [e.getObject() for e in entries]
        return objs

registerType(BlogFolder, PROJECTNAME)
