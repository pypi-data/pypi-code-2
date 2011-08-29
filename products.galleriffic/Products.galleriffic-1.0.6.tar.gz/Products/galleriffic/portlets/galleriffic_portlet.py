from zope.interface import implements
from plone.portlets.interfaces import IPortletDataProvider
from plone.app.portlets.portlets import base
from zope import schema
from zope.formlib import form
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.galleriffic import AbstractGallerifficMessageFactory as _
from Products.CMFCore.utils import getToolByName

from zope.schema.vocabulary import SimpleVocabulary
from zope.schema.vocabulary import SimpleTerm

from Products.ATContentTypes.interface.topic import IATTopic
from Products.galleriffic.interfaces import IGallerifficView
from zope.component import getUtility
from plone.i18n.normalizer.interfaces import IIDNormalizer
from plone.app.vocabularies.catalog import SearchableTextSourceBinder
from plone.app.form.widgets.uberselectionwidget import UberSelectionWidget

class IGallerifficPortlet(IPortletDataProvider):
    
    header = schema.TextLine(title=_(u"Portlet header"),
            description=_(u"Title of the rendered portlet"),
            required=True
    )
    
    target = schema.Choice(title=_(u"Target"),
                         description=_(u"Select the collection which provides the items to list"),
                         required=True,
                         source=SearchableTextSourceBinder(
                            {'object_provides' : IGallerifficView.__identifier__},
                            default_query='path:'
                         )
            )
    
    delay = schema.Int(title=_(u"Time sliding"),
                  description=_(u"Time sliding"),
                  required=True,
                  default = 5
            )
    size = schema.Choice(title=_(u"Size preview"),
                         description=_(u"label_size_desciption", u"Select the image size"),
                         required=True,
                         default="image_mini",
                         vocabulary=SimpleVocabulary([SimpleTerm('image_preview',_(u'Image 400x400')),
                                                      SimpleTerm('image_mini',_(u'Image 200x200')),
                                                      SimpleTerm('image_thumb',_(u'Image 128x128')),
                                                      SimpleTerm('image_tile',_(u'Image 64x64'))])
                  )
    limit = schema.Int(title=_(u"Limit"),
                  description=_(u"Specify the maximum number of items to show in the portlet. "
                                     "Leave this blank to show all items."),
                  required=False,
                  default = 5
            )
    
    omit_border = schema.Bool(
        title=_(u"Omit portlet border"),
        description=_(u"Tick this box if you want to render the text above "
                      "without the standard header, border or footer."),
        required=True,
        default=False)

    footer = schema.TextLine(
        title=_(u"Portlet footer"),
        description=_(u"Text to be shown in the footer"),
        required=False)

    more_url = schema.ASCIILine(
        title=_(u"Details link"),
        description=_(u"If given, the header and footer "
                      "will link to this URL."),
        required=False)

class Assignment(base.Assignment):
    """Portlet assignment.

    This is what is actually managed through the portlets UI and associated
    with columns.
    """

    implements(IGallerifficPortlet)
    
    target = ''
    delay = 5
    limit = 0
    size = 'image_mini'
    header = 'rotator'
    omit_border = False
    footer = ''
    more_url = ''
    
    def __init__(self, target='', delay=5, limit=0, size='image_mini',
                 header='rotator', omit_border=False, footer='', more_url=''):
        self.target = target
        self.delay = delay
        self.limit= limit
        self.size = size
        self.header = header
        self.omit_border = omit_border
        self.footer = footer
        self.more_url = more_url

    @property
    def title(self):
        """This property is used to give the title of the portlet in the
        "manage portlets" screen.
        """
        return "Galleriffic Portlet"
    
class Renderer(base.Renderer):
    """Portlet renderer.

    This is registered in configure.zcml. The referenced page template is
    rendered, and the implicit variable 'view' will refer to an instance
    of this class. Other methods can be added and referenced in the template.
    """

    render = ViewPageTemplateFile('galleriffic_portlet.pt')
    
    def __init__(self, context, request, view, manager, data):
        self.context = context
        self.request = request
        self.view = view
        self.__parent__ = view
        self.manager = manager
        self.data = data
        self.catalog_tool = getToolByName(self.context,'portal_catalog')
        urltool = getToolByName(self.context, 'portal_url')
        portal = urltool.getPortalObject()
        rootPath = '/'.join(portal.getPhysicalPath()) + self.data.target
        self.target = portal.unrestrictedTraverse(rootPath, None)
    
    @property
    def available(self):
        """docstring for available"""
        if not self.target:
            return False
        
        images = self.getImages()
                
        if len(images) > 0:
            return True
            
        return False
    
    def has_link(self):
        return bool(self.data.more_url)

    def has_footer(self):
        return bool(self.data.footer)
    
    def css_class(self):
        """Generate a CSS class from the portlet header
        """
        header = self.data.header
        normalizer = getUtility(IIDNormalizer)
        return normalizer.normalize(header).replace('-', '_')
    
    def getJavascript(self):
        """ doc """

        list_img = self.getImages()

        if len(list_img) > 0:
            return """
            <script type="text/javascript">
                jq(document).ready(function(){
                    %(class)s_interval = %(delay)s * 1000;
                    %(class)s_image_index = 0;
                    %(class)s_items = %(images)s;
                    %(class)s_Next = function(){
                         if (%(class)s_items.length > 0){
                             jq('#galleriffic-%(class)s-rimage').attr('src', %(class)s_items[%(class)s_image_index %% %(class)s_items.length ]);
                             %(class)s_image_index++;
                         }
                    }
                    %(class)s_Next();
                    setInterval(%(class)s_Next, %(class)s_interval);
                })
            </script>
            """ % {'delay': self.data.delay, 'images':list_img, 'class': self.css_class()}
        else:
            return ""
    
    def getImages(self):
        """ """
        target = self.target
        
        items = []
        
        if IATTopic.providedBy(target):
            items = target.queryCatalog()
        else:
            items = self.catalog_tool.searchResults(portal_type=['Image',],
                            path = {'query' : '/'.join(target.getPhysicalPath()),'depth' : 100})
            
        limit = self.data.limit
        images = []
        images = [ item.getURL() + '/' + self.data.size for item in items ]
        
        if limit:
            return images[:limit]
        return images

class AddForm(base.AddForm):
    """Portlet add form.

    This is registered in configure.zcml. The form_fields variable tells
    zope.formlib which fields to display. The create() method actually
    constructs the assignment that is being added.
    """
    form_fields = form.Fields(IGallerifficPortlet)
    form_fields['target'].custom_widget = UberSelectionWidget
    def create(self, data):
        return Assignment(**data)

class EditForm(base.EditForm):
    """Portlet edit form.

    This is registered with configure.zcml. The form_fields variable tells
    zope.formlib which fields to display.
    """
    form_fields = form.Fields(IGallerifficPortlet)
    form_fields['target'].custom_widget = UberSelectionWidget