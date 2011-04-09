from zope.interface import implements, Interface
from zope.component import adapts, getMultiAdapter, queryUtility

from plone.i18n.normalizer.interfaces import IIDNormalizer
from plone.portlets.interfaces import IPortletDataProvider
from plone.app.portlets.portlets import base

from zope import schema
from zope.formlib import form
from Products.ATContentTypes.interface import IATFolder
from plone.memoize.instance import memoize

from Acquisition import aq_inner, aq_base, aq_parent
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFCore.utils import getToolByName

from Products.CMFPlone.interfaces import INonStructuralFolder, IBrowserDefault
from Products.CMFPlone import utils
from Products.CMFPlone import PloneMessageFactory as _

from plone.app.layout.navigation.interfaces import INavtreeStrategy
from plone.app.layout.navigation.interfaces import INavigationQueryBuilder

from plone.app.layout.navigation.root import getNavigationRoot
from plone.app.layout.navigation.navtree import buildFolderTree

from plone.app.vocabularies.catalog import SearchableTextSourceBinder
from plone.app.form.widgets.uberselectionwidget import UberSelectionWidget

from Products.CMFPlone.browser.navtree import SitemapNavtreeStrategy


class IFolderPortlet(IPortletDataProvider):
    """To initalized & provide a interface

    """
    header = schema.TextLine(
            title=_(u"label_folder_title", default=u"Title"),
            description=_(u"help_folder_title",
                          default=u"The title of the folder items. Leave "
                                   "blank for the default, translated title."),
            default=u"",
            required=False)

    folder_path = schema.Choice(title=_(u"label_folder_path",default=u"Target Folder"),
                                  description=_(u"Find the folder which provides the modified items to list"),
                                  required=True,
                                  source=SearchableTextSourceBinder({'object_provides' : IATFolder.__identifier__},
                                                                    default_query='path:'))

    limit = schema.Int(title=_(u"label_folder_limit",default=u"Limit"),
                       description=_(u"Specify the maximum number of items to show in the portlet. "
                                       "Leave this blank to show all items."),
                       default=5,
                       required=False)
    show_more = schema.Bool(title=_(u"label_folder_showmore",default=u"Show more... link"),
                       description=_(u"If enabled, a more... link will appear in the footer of the portlet, "
                                      "linking to the designated folder."),
                       required=True,
                       default=True)

class Assignment(base.Assignment):
    implements(IFolderPortlet)


    @property
    def title(self):
        return "Folder Items"
    
    header = u""
    folder_path=None
    limit = None
    show_more = True

    def __init__(self, header=u"", folder_path=None, limit=None, show_more=True):

        self.header = header
        self.folder_path = folder_path
        self.limit = limit
        self.show_more = show_more

    @property
    def title(self):
        """This property is used to give the title of the portlet in the
        "manage portlets" screen. Here, we use the title that the user gave.
        """
        return self.header or self.folder_path


class Renderer(base.Renderer):

    _template = ViewPageTemplateFile('Folder.pt')
    def __init__(self, *args):
        base.Renderer.__init__(self, *args)

    # Cached version - needs a proper cache key
    # @ram.cache(render_cachekey)
    # def render(self):
    #     if self.available:
    #         return xhtml_compress(self._template())
    #     else:
    #         return ''

    render = _template
    
    @property    
    def title(self):
        """return title of feed for portlet"""

        return getattr(self.data, 'header', '') or self.folder().title_or_id()

    @property
    def available(self):
        return len(self.results())

    def folder_url(self):
        folder = self.folder()
        if folder is None:
            return None
        else:
            return folder.absolute_url()

    def results(self):
        """ Get the actual modified items brains in the folder. 
            This is a wrapper so that we can memoize."""
        return self._standard_results()

    @memoize
    def _standard_results(self):
        results = []
        folder = self.folder()
        if folder is not None:

            portal_state = getMultiAdapter((self.context, self.request), name=u'plone_portal_state')
            portal = portal_state.portal()
            relative_path = self.relative_path()

            results = portal.queryCatalog(REQUEST={'path':{'query': relative_path, 'depth':1},'sort_on':'modified','sort_order':'reverse'})
            if self.data.limit and self.data.limit > 0:
                results = results[:self.data.limit]

        return results

    @memoize
    def folder(self):
        """ get the folder the portlet is pointing to"""
        
        folder_path = self.data.folder_path
        if not folder_path:
            return None

        if folder_path.startswith('/'):
            folder_path = folder_path[1:]
        
        if not folder_path:
            return None

        portal_state = getMultiAdapter((self.context, self.request), name=u'plone_portal_state')
        portal = portal_state.portal()
        return portal.restrictedTraverse(folder_path, default=None)

    @memoize
    def relative_path(self):
        """ get the relative path of the folder"""
        
        folder_path = self.data.folder_path
        if not folder_path:
            return None

        if folder_path.startswith('/'):
            folder_path = folder_path[1:]
        
        if not folder_path:
            return None

        portal_state = getMultiAdapter((self.context, self.request), name=u'plone_portal_state')
        portal = portal_state.portal()

        return portal.getId() + '/' + folder_path


class AddForm(base.AddForm):
    form_fields = form.Fields(IFolderPortlet)
    form_fields['folder_path'].custom_widget = UberSelectionWidget
    label = _(u"Add Folder Portlet")
    description = _(u"This portlet display a Folder items.")

    def create(self, data):
        return Assignment(**data)

class EditForm(base.EditForm):
    form_fields = form.Fields(IFolderPortlet)
    form_fields['folder_path'].custom_widget = UberSelectionWidget
    label = _(u"Edit Folder Portlet")
    description = _(u"This portlet display a Folder items.")

