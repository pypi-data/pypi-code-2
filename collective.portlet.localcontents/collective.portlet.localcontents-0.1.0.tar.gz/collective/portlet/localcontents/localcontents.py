# -*- coding: utf-8 -*-

from Acquisition import aq_inner, aq_parent
from zope.interface import implements
from zope.component import getUtility
from zope.component import getMultiAdapter
from zope import schema
from zope.formlib import form
from plone.portlets.interfaces import IPortletDataProvider
from plone.app.portlets.portlets import base
from Products.CMFCore.utils import getToolByName
from Products.ATContentTypes.interface.folder import IATFolder
from OFS.interfaces import IFolder
from plone.i18n.normalizer.interfaces import IIDNormalizer
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from collective.portlet.localcontents import LocalContentsMessageFactory as _

class ILocalContents(IPortletDataProvider):
    """Browser local subcontents"""

    name = schema.TextLine(title=_(u"Portlet title"),
                                   description=_(u"Choose the title you want to display"),
                                   required=True)

    display_when_not_default_page = schema.Bool(title=_(u"label_display_when_not_default_page",
                                                       default="Show when not using default content view"),
                                   description=_(u"help_display_when_not_default_page",
                                                 default=u"Check this to show the portlet also when current location is not "
                                                         u"using a default content to be view of the folder"),
                                   required=False)


class Assignment(base.Assignment):

    implements(ILocalContents)

    name = u""

    def __init__(self, name=u"", display_when_not_default_page=False):
        self.name = name
        self.display_when_not_default_page = display_when_not_default_page

    @property
    def title(self):
        return _(u"Local contents")+": "+ self.name
#        translation_service = getToolByName(context,'translation_service')
#        return translation_service.utranslate(domain='collective.portlet.localcontents',
#                                              msgid=u"Local contents",
#                                              default=u"Local contents",
#                                              context=context)


class Renderer(base.Renderer):
    render = ViewPageTemplateFile('localcontents.pt')

    # Stolen from ploneview
    def isFolderOrFolderDefaultPage(self, context, request):
        context_state = getMultiAdapter((aq_inner(context), request), name=u'plone_context_state')
        return context_state.is_structural_folder() or context_state.is_default_page()

    @property
    def available(self):
        """Available only if we are on ATFolder and if the folder has a default page view
        (but for this, check the 'display_when_not_default_page' flag)
        """
        context = self.context
        display_when_not_default_page = self.data.display_when_not_default_page
        folder = self._getFolder()

        if not IATFolder.providedBy(folder):
            return False

        if not display_when_not_default_page:
            if context==folder:
                return False

        return True

    def css_class(self):
        """Generate a CSS class from the portlet header
        """
        name = self.data.name
        normalizer = getUtility(IIDNormalizer)
        return "portletLocalContents-%s" % normalizer.normalize(name)

    def _getFolder(self):
        """Return the containing folder of the current context, or the context itself if it is a folder"""
        context = self.context
        request = self.request
        if IFolder.providedBy(context):
            folder = context
        elif self.isFolderOrFolderDefaultPage(context, request):
            folder = aq_parent(aq_inner(context))
        else:
            # don't know how to handle this
            folder = aq_parent(aq_inner(context))
        return folder

    @property
    def isAnon(self):
        mtool = getToolByName(self.context, 'portal_membership')
        return mtool.isAnonymousUser()

    def contents(self):
        """Generate a list of contents of the current location"""
        context = self.context
        
        portal_url = getToolByName(context, 'portal_url')
        ptool = getToolByName(context, 'plone_utils')
        metaTypesNotToList = getToolByName(context, 'portal_properties').navtree_properties.metaTypesNotToList;

        folder = self._getFolder()
        dpage = folder.getProperty('default_page', '')
        contents = folder.getFolderContents()
        
        navElems = []
        for x in contents:
            if not x.exclude_from_nav and x.portal_type not in metaTypesNotToList and x.getId!=dpage:
                navElems.append({'title': x.Title,
                                 'url': x.getURL(),
                                 'type': x.portal_type,
                                 'type_normalized': ptool.normalizeString(x.portal_type),
                                 'review_state_normalized': ptool.normalizeString(x.review_state),
                                 'icon': "%s/%s" % (portal_url(), x.getIcon),
                                 'description': x.Description,
                                 'current': False # TODO for giving the navTreeCurrentItem class
                                 })
        
        return navElems

class AddForm(base.AddForm):
    form_fields = form.Fields(ILocalContents)

    def create(self, data):
        return Assignment(**data)


class EditForm(base.EditForm):
    form_fields = form.Fields(ILocalContents)
