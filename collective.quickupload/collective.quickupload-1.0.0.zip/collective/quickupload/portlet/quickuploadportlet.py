# -*- coding: utf-8 -*-
## Copyright (C)2010 Alter Way Solutions

from Acquisition import aq_inner, aq_base, aq_parent
from zope.interface import implements
from zope import schema
from zope.schema.vocabulary import SimpleVocabulary
from zope.schema.vocabulary import SimpleTerm
from zope.formlib import form
from plone.memoize.compress import xhtml_compress
from plone.portlets.interfaces import IPortletDataProvider
from plone.app.portlets.portlets import base
from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFPlone.FactoryTool import TempFolder

from collective.quickupload import siteMessageFactory as _

def isTemporary(obj):
    """Check to see if an object is temporary"""
    parent = aq_base(aq_parent(aq_inner(obj)))
    return hasattr(parent, 'meta_type') and parent.meta_type == TempFolder.meta_type


class IQuickUploadPortlet(IPortletDataProvider):
    """Quickupload portlet schema
    """

    header = schema.TextLine(
        title= _(u"Box title"),
        default= u"",
        description= _(u"If title is empty, the portlet title will be the Media Choice + ' Quick Upload'."),
        required=False)


    upload_portal_type = schema.Choice ( title= _(u"Content type"),
                                         description= _(u"Choose the portal type used for file upload. "
                                                         "Let the default configuration for an automatic portal type, "
                                                         "depending on settings defined in content_type_registry."),
                                         required=True,
                                         default='auto',
                                         vocabulary="collective.quickupload.fileTypeVocabulary")

    upload_media_type = schema.Choice ( title= _(u"Media type"),
                                        description = _(u"Choose the media type used for file upload. "
                                                         "image, audio, video ..."),
                                        required=False,
                                        default='',
                                        vocabulary = SimpleVocabulary([SimpleTerm('', '', _(u"All")),
                                                                       SimpleTerm('image', 'image', _(u"Images")),
                                                                       SimpleTerm('video', 'video', _(u"Video files")),
                                                                       SimpleTerm('audio', 'audio', _(u"Audio files")),
                                                                       SimpleTerm('flash', 'flash', _(u"Flash files")),
                                                                       ]), )    

class Assignment(base.Assignment):
    """Portlet assignment.
    """

    implements(IQuickUploadPortlet)

    def __init__(self, header= "", upload_portal_type = 'auto',
                 upload_media_type=''):
        self.header = header
        self.upload_portal_type = upload_portal_type
        self.upload_media_type = upload_media_type

    @property
    def title(self):
        """portlet title
        """
        if self.header :
            return self.header
        media = self.upload_media_type or 'files'
        if media == 'image' :
            return _('Images Quick Upload')
        return _('%s Quick Upload' %media.capitalize())


class Renderer(base.Renderer):
    """Portlet renderer.
    """

    _template = ViewPageTemplateFile('quickuploadportlet.pt')

    def __init__(self, *args):
        base.Renderer.__init__(self, *args)
        context = aq_inner(self.context)
        request = self.request
        session = request.get('SESSION', None)
        # empty typeupload and mediaupload session 
        # since the portlet don't use it, but another app could
        if session :
            if session.has_key('typeupload') :
                session.delete('typeupload')
            if session.has_key('mediaupload') :
                session.delete('mediaupload')
        self.ploneview = context.restrictedTraverse('@@plone')
        self.pm = getToolByName(context, 'portal_membership')

    def render(self):
        return xhtml_compress(self._template())
    
    @property
    def available(self):
        context = aq_inner(self.context)
        if self.ploneview.isStructuralFolder() and \
           self.pm.checkPermission('Add portal content', context) and \
           not isTemporary(context) :
            return True
        return False
    
    def getUploadUrl(self):
        """
        return upload url
        in current folder
        """
        context = aq_inner(self.context)
        folder_url = self.ploneview.getCurrentFolderUrl()                      
        return '%s/@@quick_upload' %folder_url
        
    def getDataForUploadUrl(self):
        data_url = ''
        if self.data.upload_portal_type != 'auto' :
            data_url+= 'typeupload=%s&' % self.data.upload_portal_type      
        if self.data.upload_media_type :
            data_url+= 'mediaupload=%s' % self.data.upload_media_type  
        return data_url      


class AddForm(base.AddForm):
    """Portlet add form.
    """
    form_fields = form.Fields(IQuickUploadPortlet)

    def create(self, data):
        return Assignment(**data)


class EditForm(base.EditForm):
    """Portlet edit form.
    """
    form_fields = form.Fields(IQuickUploadPortlet)
