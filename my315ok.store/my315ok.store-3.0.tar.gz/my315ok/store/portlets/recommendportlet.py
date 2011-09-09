
from zope.interface import implements
from zope.component import getMultiAdapter
from plone.app.portlets.portlets import base
from plone.portlets.interfaces import IPortletDataProvider
from plone.memoize.instance import memoize
from Products.CMFCore.utils import getToolByName

from zope import schema
from zope.formlib import form
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.app.vocabularies.catalog import SearchableTextSourceBinder
from Products.ATContentTypes.interface import IATTopic

#from plone.app.form.widgets.uberselectionwidget import UberSelectionWidget
from my315ok.store import storeMessageFactory as _
from plone.portlet.collection import PloneMessageFactory as _a

class IRecommendPortlet(IPortletDataProvider):
    """A portlet

    It inherits from IPortletDataProvider because for this portlet, the
    data that is being rendered and the portlet assignment itself are the
    same.
    """

    # TODO: Add any zope.schema fields here to capture portlet configuration
    # information. Alternatively, if there are no settings, leave this as an
    # empty interface - see also notes around the add form and edit form
    # below.

    header = schema.TextLine(title=_a(u"Portlet header"),
                             description=_a(u"Title of the rendered portlet"),
                             required=True)

    target_collection = schema.Choice(title=_a(u"Target collection"),
                                  description=_a(u"Find the collection which provides the items to list"),
                                  required=True,
                                  source=SearchableTextSourceBinder({'object_provides' : IATTopic.__identifier__},
                                                                    default_query='path:'))

    limit = schema.Int(title=_a(u"Limit"),
                       description=_a(u"Specify the maximum number of items to show in the portlet. "
                                       "Leave this blank to show all items."),
                       required=False)
    show_more = schema.Bool(title=_a(u"Show more... link"),
                       description=_a(u"If enabled, a more... link will appear in the footer of the portlet, "
                                      "linking to the underlying Collection."),
                       required=True,
                       default=True)
    previewmode = schema.Choice(
        title=_(u"image size"),
        description=_(u"Choose source image size"),
        required = True,
        default = "thumb",
        vocabulary = 'hot.ImageSizeVocabulary' )


class Assignment(base.Assignment):
    """Portlet assignment.

    This is what is actually managed through the portlets UI and associated
    with columns.
    """

    implements(IRecommendPortlet)

    # TODO: Set default values for the configurable parameters here

    # some_field = u""
    header = u""
    target_collection = None
    limit = 5
    show_more = True
    previewmode = u"thumb"
    # TODO: Add keyword parameters for configurable parameters here
    # def __init__(self, some_field=u"):
    #    self.some_field = some_field

    def __init__(self, header=u"", target_collection=None, limit=None, show_more=True, previewmode=u"thumb"):
        self.header = header
        self.target_collection = target_collection
        self.limit = limit
        self.show_more = show_more
        self.previewmode = previewmode
    @property
    def title(self):
        """This property is used to give the title of the portlet in the
        "manage portlets" screen.
        """
        if self.header:
            return self.header
        else:

            return _(u"Hot goods portlet")


class Renderer(base.Renderer):
    """Portlet renderer.

    This is registered in configure.zcml. The referenced page template is
    rendered, and the implicit variable 'view' will refer to an instance
    of this class. Other methods can be added and referenced in the template.
    """

    render = ViewPageTemplateFile('recommendportlet.pt')

    @property
    def available(self):
        return len(self.results())

    def collection_url(self):
        collection = self.collection()
        if collection is None:
            return None
        else:
            return collection.absolute_url()

    def results(self):
        """ Get the actual result brains from the collection. 
            This is a wrapper so that we can memoize if and only if we aren't
            selecting random items."""
        
        return self._standard_results()

    @memoize
    def _standard_results(self):
        results = []
        collection = self.collection()
        if collection is not None:
            results = collection.queryCatalog()
            if self.data.limit and self.data.limit > 0:
                results = results[:self.data.limit]
        return results         
        
    @memoize
    def collection(self):
        """ get the collection the portlet is pointing to"""
        
        collection_path = self.data.target_collection
        if not collection_path:
            return None

        if collection_path.startswith('/'):
            collection_path = collection_path[1:]
        if not collection_path:
            return None
        portal_state = getMultiAdapter((self.context, self.request), name=u'plone_portal_state')
        portal = portal_state.portal()
        return portal.restrictedTraverse(collection_path, default=None)
    @memoize   
    def main_parameters(self):
        """ fetch goods parameters"""              
        brains = self.results()
        sc = self.data.previewmode
        goods = []
    
        if len(brains) >0:            
            for brain in brains:                
#                bs is a brain of goods              
                tmp = self.add_paras(brain,sc)
                goods.append(tmp)
        return goods
    # here is set local varible item avoid by overed.
    def add_paras(self,brain,scale):
##        import pdb
##        pdb.set_trace()
        item={}
        url = brain.getURL()
        item['title'] = brain.Title
        item['mprice'] = brain.market_price
        item['oprice'] = brain.our_price
        item['photo'] = self.get_goods_img(brain,scale)['tag']
        item['goods_url'] = url
        item['img_url'] = url + "/@@store_view"
        return item
        
        
        
    @memoize
    def get_goods_img(self,brain,scale):
##        import pdb
##        pdb.set_trace()
        catalog = getToolByName(self.context, 'portal_catalog')
        try:
            sepath = brain.getPath()
        except:
            sepath =  '/'.join(brain.getObject().getPhysicalPath()) 
        query = {'meta_type':('goods_image'),
                 'sort_on':'getObjPositionInParent',
                 'sort_order':'forward',
                 'path':sepath,
                 }        
        sd = catalog(query)
        mainimgbrain = sd[0]
        tl = mainimgbrain.Title
        url = mainimgbrain.getURL()
        surl = url + "/image"  + "_" + scale
                    
        imgtag = "<img src='%s' alt='%s' title='%s' />" % (surl,tl,tl)
#        imgtag = mainimg.getField('image').tag(mainimg,scale=scale)
        img_info = {}
        img_info['tag']= imgtag
        img_info['url']= url
        return img_info      

class Renderer2(Renderer):

     render = ViewPageTemplateFile('recommendportlet.pt')


# NOTE: If this portlet does not have any configurable parameters, you can
# inherit from NullAddForm and remove the form_fields variable.

class AddForm(base.AddForm):
    """Portlet add form.

    This is registered in configure.zcml. The form_fields variable tells
    zope.formlib which fields to display. The create() method actually
    constructs the assignment that is being added.
    """
    form_fields = form.Fields(IRecommendPortlet)

    def create(self, data):
        return Assignment(**data)


# NOTE: IF this portlet does not have any configurable parameters, you can
# remove this class definition and delete the editview attribute from the
# <plone:portlet /> registration in configure.zcml

class EditForm(base.EditForm):
    """Portlet edit form.

    This is registered with configure.zcml. The form_fields variable tells
    zope.formlib which fields to display.
    """
    form_fields = form.Fields(IRecommendPortlet)

