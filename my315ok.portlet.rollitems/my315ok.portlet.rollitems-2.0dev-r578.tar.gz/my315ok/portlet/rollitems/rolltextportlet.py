from zope.interface import implements
from plone.portlets.interfaces import IPortletDataProvider
from plone.app.portlets.portlets import base
from zope.component import getMultiAdapter
from Acquisition import aq_inner

from plone.app.vocabularies.catalog import SearchableTextSourceBinder
from plone.app.form.widgets.uberselectionwidget import UberSelectionWidget
from Products.ATContentTypes.interface import IATTopic

from zope import schema
from zope.formlib import form
from plone.memoize.instance import memoize
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from plone.portlet.collection import PloneMessageFactory as _a
from my315ok.portlet.rollitems import RollPortletMessageFactory as _

##class ICollectionPortlet(IPortletDataProvider):
class IRollTextPortlet(IPortletDataProvider):
    """A portlet which renders the results of a collection object.
    """

    header = schema.TextLine(title=_a(u"Portlet header"),
                             description=_a(u"Title of the rendered portlet"),
                             required=True)
    target_collection = schema.Choice(title=_a(u"Target collection"),
                                  description=_a(u"Find the collection which provides the items to list"),
                                  required=False,
                                  source=SearchableTextSourceBinder({'object_provides' : IATTopic.__identifier__},
                                                                    default_query='path:'))
    			  
    show_more = schema.Bool(title=_a(u"Show more... link"),
                       description=_a(u"If enabled, a more... link will appear in the footer of the portlet, "
                                      "linking to the underlying Collection."),
                       required=True,
                       default=True)
    show_dates = schema.Bool(title=_a(u"Show dates"),
                       description=_a(u"If enabled, effective dates will be shown underneath the items listed."),
                       required=True,
                       default=True)
    
    topid = schema.TextLine(title=_a(u"top id"),
                             description=_a(u"the wraped top id of the roll zone"),
                             required=True)
    cssid = schema.TextLine(title=_a(u"css id"),
                             description=_a(u"the css id of the roll zone"),
                             required=True)
    wordsnum = schema.Int(title=_(u"number"),
                       description=_(u"Specify the maximum number of words to show as title. "
                                       "Leave this blank to show all items."),
                       default=6,
                       required=False)
    limit = schema.Int(title=_a(u"Limit"),
                       description=_a(u"Specify the maximum number of items to show in the portlet. "
                                       "Leave this blank to show all items."),
                       required=False)
    roll_direc = schema.Choice(
        title=_(u"direction"),
        description=_(u"Choose the roll direction"),
        vocabulary = 'rollitems.RollDirectionVocabulary' )
    
    speed = schema.Int(title=_(u"speed"),
                       description=_(u"Specify the speed of the roll items "),                                      
                       required=True)
    pause = schema.Int(title=_(u"pause time"),
                       description=_(u"Specify the time of pause(ms)"),
                       required=True)
    step = schema.Int(title=_(u"step length"),
                       description=_(u"Specify the step length of every move."),
                       required=True)

class Assignment(base.Assignment):
    """
    Portlet assignment.    
    This is what is actually managed through the portlets UI and associated
    with columns.
    """
    implements(IRollTextPortlet)
    header = u""
    target_collection = u""
    show_more = True
    show_dates = True
    topid = u""
    cssid = u""
    wordsnum = None
    limit = None
    roll_direc = "left"
    speed = 30
    pause = 1000
    step = 1
    

    def __init__(self, header=u"", target_collection=u"", show_more=True,show_dates=True,topid=u"",
                 cssid=u"",roll_direc="left",wordsnum=6,limit=None,speed=None,pause=None,step=None):
        self.header = header
        self.target_collection = target_collection
        self.show_more = show_more
        self.show_dates = show_dates
        self.speed = speed
        self.pause = pause
        self.step = step
        self.topid = topid
        self.wordsnum = wordsnum
        self.limit = limit
        self.cssid = cssid
        self.roll_direc = roll_direc

    @property
    def title(self):
        """This property is used to give the title of the portlet in the
        "manage portlets" screen. Here, we use the title that the user gave.
        """
        return self.header


class Renderer(base.Renderer):
    """Portlet renderer.
    
    This is registered in configure.zcml. The referenced page template is
    rendered, and the implicit variable 'view' will refer to an instance
    of this class. Other methods can be added and referenced in the template.
    """

    render = ViewPageTemplateFile('rolltextportlet.pt')
    
    def collection_url(self):
        collection = self.collection()
        if collection is None:
            return None
        else:
            return collection.absolute_url()
        
    def ifdate(self):
        if self.data.show_dates:
            return True
        else:
            return False
    @memoize
    def results(self):
#        import pdb
#        pdb.set_trace()
        results = []
        cols = []
        item = {}
        collection = self.collection()
        if collection is not None:
            cols = collection.queryCatalog()
            m = self.data.limit
            if m and m > len(cols):
                brains = cols[:m]
            else:
                brains = cols
                
            for brain in brains:
                item["url"] = brain.getURL()
                tl = brain.Title
                num = self.data.wordsnum
                if len(tl) > num and num >0:                    
                    tl = self.cropTitle(tl, num)                    
                item["title"] = tl
                item["modified"] = self.toLocalizedTime(brain.modified, date_only=True)
                results.append(item)
                item={}       
                           
        return results
    @memoize
    def collection(self):
        """ get the collection the portlet is pointing to"""
        
        context = aq_inner(self.context)
        collection_path = self.data.target_collection
        if not collection_path:
            return None

        if collection_path.startswith('/'):
            collection_path = collection_path[1:]
        
        if not collection_path:
            return None
        portal_state = getMultiAdapter((context, self.request), name=u'plone_portal_state')
        portal = portal_state.portal()
        return portal.unrestrictedTraverse(collection_path, default=None)
   

    def __init__(self, *args):
        base.Renderer.__init__(self, *args)
   
    def cropTitle(self,text, length, ellipsis='...'):
        context = aq_inner(self.context)
        pview = getMultiAdapter((context,self.request),name=u"plone")
#        pview = getMultiAdapter((self.parent(), self.request), name=u'earthqk_event_view')
        croped = pview.cropText(text, length)
        return croped
    def toLocalizedTime(self, time, date_only=None, time_only=None):
        """Convert time to localized time
        """
        fmt = '%Y/%m/%d %H:%M:%S'
        datefmt = '%Y/%m/%d'
        timefmt  = '%H:%M:%S'
        if date_only:
            date = time.strftime(datefmt)
            return date
        elif time_only:
            time = time.strftime(timefmt)
            return time
        else:
            tmp = time.strftime(fmt)
            return tmp
    @memoize
    def render_marqueejs(self):      
        cssid = self.data.cssid
       
        out="""jq(document).ready(function(){rolltext(".%(mid)s");});""" % dict(mid=cssid)
        return out     

        
class AddForm(base.AddForm):
    """Portlet add form.
    
    This is registered in configure.zcml. The form_fields variable tells
    zope.formlib which fields to display. The create() method actually
    constructs the assignment that is being added.
    """
    form_fields = form.Fields(IRollTextPortlet)
    form_fields['target_collection'].custom_widget = UberSelectionWidget
    description = _a(u"This portlet display a listing of items from a Collection.")

    def create(self, data):
        return Assignment(**data)

class EditForm(base.EditForm):
    """Portlet edit form.
    
    This is registered with configure.zcml. The form_fields variable tells
    zope.formlib which fields to display.
    """

    form_fields = form.Fields(IRollTextPortlet)
    form_fields['target_collection'].custom_widget = UberSelectionWidget
    label = _a(u"Edit Collection Portlet")
    description = _a(u"This portlet display a listing of items from a Collection.")
