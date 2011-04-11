from Acquisition import aq_inner

from zope import schema
from zope.formlib import form
from zope.component import getMultiAdapter, queryUtility
from zope.interface import Interface, implements

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.interfaces import IPropertiesTool
from Products.ATContentTypes.interface import IATFolder, IATImage, \
    IATBTreeFolder

from plone.app.portlets.portlets import base
from plone.app.form.widgets.wysiwygwidget import WYSIWYGWidget
from plone.portlets.interfaces import IPortletDataProvider
from plone.app.vocabularies.catalog import SearchableTextSourceBinder
from plone.memoize.instance import memoize

try:
    from plone.app.imaging.utils import getAllowedSizes
    HAS_SCALES = True
except ImportError:
    HAS_SCALES = False

from collective.portlet.foldercontents import siteMessageFactory as _
from collective.portlet.foldercontents.widget import \
    FixedErrorMessageChoiceInputWidget


class IFolderContentsPortlet(IPortletDataProvider):
    """A portlet

    It inherits from IPortletDataProvider because for this portlet, the
    data that is being rendered and the portlet assignment itself are the
    same.
    """

    use_folder_name = schema.Bool(
        title=_(u"Folder title as a portlet header"),
        description=_(u"Check this option to use folder title as a portlet "
                      u"header. Note: below field will be ignored even if "
                      u"filled in in this case."),
        required=False,
        default=False)

    name = schema.TextLine(
        title=_(u"Header"),
        description=_(u"Enter here portlet header. This header won't be used "
                      u"in case above option is selected."),
        required=False,
        default=u"")

    use_folder_desc = schema.Bool(
        title=_(u"Folder description as a portlet body"),
        description=_(u"Check this option to use folder description as a "
                      u"portlet body. Note: below field will be ignored even "
                      u"if filled in in this case."),
        required=False,
        default=False)

    body = schema.Text(
        title=_(u"Portlet Body"),
        description=_(u"Enter here portlet body if needed. This field won't be "
                      u"used in case above option is selected."),
        required=False,
        default=u"")

    folder = schema.Choice(
        title=_(u"Select folder"),
        description=_(u"Folder to get contents from."),
        required=True,
        source=SearchableTextSourceBinder(
            {'object_provides' : (IATFolder.__identifier__,
                IATBTreeFolder.__identifier__)},
            default_query='path:'))

    number = schema.Int(
        title=_(u"Number of folder items to show"),
        description=_(u"Enter here the number of folder items to display. Note:"
                      u" set 0 to show all items."),
        min=0,
        required=True,
        default=5)

    image = schema.Choice(
        title=_(u"Image"),
        description=_(u"You may pick here image object to be shown right after"
                      u" portlet header."),
        required=False,
        source=SearchableTextSourceBinder(
            {'object_provides' : IATImage.__identifier__},
            default_query='path:'))
    
    image_scale = schema.TextLine(
        title=_(u"Image Scale"),
        description=_(u"Enter here image scale you're willing to use (e.g. mini"
                      u", list, thumb, etc...)."),
        required=False)
    
    image_scale_list = schema.Choice(
        title=_(u"Default Image Scale List"),
        description=_(u"You can select scale from list here. In this case "
                      u"'image_scale' field should be empty."),
        vocabulary='collective.portler.foldercontents.PortalScales',
        required=False)
    
    html_class = schema.ASCIILine(
        title=_(u"HTML Class Name"),
        description=_(u"Enter here html class for this portlet wrapper element"
                      u" in order to apply custom styling."),
        required=False)
    
    more_url = schema.Bool(
        title=_(u"More link"),
        description=_(u"Check this option in order to show more link pointing "
                      u"to folder."),
        required=True,
        default=True)

class Assignment(base.Assignment):
    """Portlet assignment.

    This is what is actually managed through the portlets UI and associated
    with columns.
    """

    implements(IFolderContentsPortlet)

    use_folder_name = False
    name = u""
    use_folder_desc = False
    body = u""
    folder = None
    number = 5
    image = None
    image_scale = ''
    image_scale_list = None
    html_class = ''
    more_url = True

    def __init__(self, use_folder_name=False, name=u"", use_folder_desc=False,
                 body=u"", folder=None, number=5, image=None, image_scale='',
                 image_scale_list=None, html_class='', more_url=True):
           
       self.use_folder_name = use_folder_name
       self.name = name
       self.use_folder_desc = use_folder_desc
       self.body = body
       self.folder = folder
       self.number = number
       self.image = image
       self.image_scale = image_scale
       self.image_scale_list = image_scale_list
       self.html_class = html_class
       self.more_url = more_url

    @property
    def title(self):
        """This property is used to give the title of the portlet in the
        "manage portlets" screen.
        """
        return self.name and _(u"Folder Contents: %s" % self.name) or \
            _(u"Folder Contents")


class Renderer(base.Renderer):
    """Portlet renderer.

    This is registered in configure.zcml. The referenced page template is
    rendered, and the implicit variable 'view' will refer to an instance
    of this class. Other methods can be added and referenced in the template.
    """

    render = ViewPageTemplateFile('foldercontents.pt')

    def __init__(self, *args, **kwargs):
        super(Renderer, self).__init__(*args, **kwargs)
        self.portal = getMultiAdapter((self.context, self.request),
                                       name=u'plone_portal_state').portal()
    @property
    def available(self):
        """If this portlet has what to show"""
        return self._getContainer(self.data.folder) is not None
    
    def getData(self):
        """Return data dictionary"""
        # get folder contents
        folder = self._getContainer(self.data.folder)
        catalog = getToolByName(self.context, 'portal_catalog')
        utils = getToolByName(self.context, 'plone_utils')
        brains = catalog(path={'query': '/'.join(folder.getPhysicalPath()),
                               'depth': 1},
                         portal_type=utils.getUserFriendlyTypes(),
                         sort_on='getObjPositionInParent')
        if self.data.number:
            brains = brains[:self.data.number]
        contents = []
        for brain in brains:
            contents.append({'title': brain.Title,
                             'desc': brain.Description,
                             'url': brain.getURL()})
        
        # get image
        image = self._getContainer(self.data.image)
        if image is not None:
            scale = ''
            if self.data.image_scale:
                scale = '/image_' + self.data.image_scale
            elif self.data.image_scale_list:
                scale = '/image_' + self.data.image_scale_list
            image = {'url': '%s%s' % (image.absolute_url(), scale),
                     'alt': image.Title()}

        return {'html_class': self.data.html_class,
                'header': self.data.use_folder_name and folder.Title() or \
                          self.data.name,
                'image': image,
                'body': self.data.use_folder_desc and folder.Description() or \
                        self.data.body,
                'contents': tuple(contents),
                'more_url': self.data.more_url and folder.absolute_url() or ''}
    
    @memoize
    def _getContainer(self, path):
        if not path:
            return None
        
        if path.startswith('/'):
            path = path[1:]
            
        if not path:
            return None
        return aq_inner(self.portal).restrictedTraverse(path, default=None)
        

class AddForm(base.AddForm):
    """Portlet add form.

    This is registered in configure.zcml. The form_fields variable tells
    zope.formlib which fields to display. The create() method actually
    constructs the assignment that is being added.
    """
    
    label = _(u"Add Folder Contents portlet")
    description = _("A portlet which can display folder contents.")
    
    @property
    def form_fields(self):
        form_fields = form.Fields(IFolderContentsPortlet)
  
        if not HAS_SCALES:
            form_fields = form_fields.omit('image_scale_list')
        form_fields['body'].custom_widget = WYSIWYGWidget
        form_fields['folder'].custom_widget = FixedErrorMessageChoiceInputWidget
        form_fields['image'].custom_widget = FixedErrorMessageChoiceInputWidget
        return form_fields

    def create(self, data):
        return Assignment(**data)


class EditForm(base.EditForm):
    """Portlet edit form.

    This is registered with configure.zcml. The form_fields variable tells
    zope.formlib which fields to display.
    """
    
    label = _(u"Edit Folder Contents portlet")
    description = _("A portlet which can display folder contents.")
    
    @property
    def form_fields(self):
        form_fields = form.Fields(IFolderContentsPortlet)
  
        if not HAS_SCALES:
            form_fields = form_fields.omit('image_scale_list')
        
        form_fields['body'].custom_widget = WYSIWYGWidget
        form_fields['folder'].custom_widget = FixedErrorMessageChoiceInputWidget
        form_fields['image'].custom_widget = FixedErrorMessageChoiceInputWidget
        return form_fields
