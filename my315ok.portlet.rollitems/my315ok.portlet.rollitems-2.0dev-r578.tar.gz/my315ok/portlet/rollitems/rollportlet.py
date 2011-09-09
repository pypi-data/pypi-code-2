from zope.interface import implements
from plone.portlets.interfaces import IPortletDataProvider
from plone.app.portlets.portlets import base
from zope.component import getMultiAdapter
from Acquisition import aq_inner

from zope import schema
from zope.formlib import form
from plone.memoize.instance import memoize
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from plone.portlet.collection import PloneMessageFactory as _a
from my315ok.portlet.rollitems import RollPortletMessageFactory as _

##class ICollectionPortlet(IPortletDataProvider):
class IRollPortlet(IPortletDataProvider):
    """A portlet which renders the results of a collection object.
    """

    header = schema.TextLine(title=_a(u"Portlet header"),
                             description=_a(u"Title of the rendered portlet"),
                             required=True)
    ajaxsrc = schema.TextLine(title=_(u"target URI"),
                             description=_(u"the URI of the resouce images view"),
                             required=True)				  
    show_more = schema.Bool(title=_a(u"Show more... link"),
                       description=_a(u"If enabled, a more... link will appear in the footer of the portlet, "
                                      "linking to the underlying Collection."),
                       required=True,
                       default=True)
    show_text = schema.Bool(title=_a(u"Show text"),
                       description=_a(u"If enabled, will display text description under image ."),
                       required=True,
                       default=False)
    topid = schema.TextLine(title=_a(u"top id"),
                             description=_a(u"the wraped top id of the roll zone"),
                             required=True)
    cssid = schema.TextLine(title=_a(u"css id"),
                             description=_a(u"the css id of the roll zone"),
                             required=True)
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
    implements(IRollPortlet)
    header = u""
    ajaxsrc = u""
    show_more = True
    topid = u""
    cssid = u""
    roll_direc = "left"
    speed = 30
    pause = 1000
    step = 1
    show_text = False

    def __init__(self, header=u"", ajaxsrc=u"", show_more=True,topid=u"",
                 cssid=u"",roll_direc="left",speed=None,pause=None,step=None,show_text=False):
        self.header = header
        self.ajaxsrc = ajaxsrc
        self.show_more = show_more
        self.show_text = show_text
        self.speed = speed
        self.pause = pause
        self.step = step
        self.topid = topid
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

    render = ViewPageTemplateFile('rollportlet.pt')
   

    def __init__(self, *args):
        base.Renderer.__init__(self, *args)
   
    @memoize
    def render_marqueejs(self):
        cssid = self.data.cssid 
        imgsrc = self.data.ajaxsrc
        context = aq_inner(self.context)
        portal_state = getMultiAdapter((context, self.request), name=u'plone_portal_state')
        portal_url = portal_state.portal_url()
        if  imgsrc[:4] != 'http':
            imgsrc = portal_url + '/' + imgsrc            
        topid = self.data.topid
        if  self.data.show_text:
            showtext = 1
        else:
            showtext = 0    
        out="""jq(document).ready(function(){ajaxfetchimg("%(topid)s","%(url)s",".%(mid)s",%(text)s);});""" % dict(topid=topid,url=imgsrc,mid=cssid,text=showtext)
        return out     

        
class AddForm(base.AddForm):
    """Portlet add form.
    
    This is registered in configure.zcml. The form_fields variable tells
    zope.formlib which fields to display. The create() method actually
    constructs the assignment that is being added.
    """
    form_fields = form.Fields(IRollPortlet)
    description = _a(u"This portlet display a listing of items from a Collection.")

    def create(self, data):
        return Assignment(**data)

class EditForm(base.EditForm):
    """Portlet edit form.
    
    This is registered with configure.zcml. The form_fields variable tells
    zope.formlib which fields to display.
    """

    form_fields = form.Fields(IRollPortlet)
    label = _a(u"Edit Collection Portlet")
    description = _a(u"This portlet display a listing of items from a Collection.")
