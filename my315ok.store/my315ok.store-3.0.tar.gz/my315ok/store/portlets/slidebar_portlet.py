from zope.interface import Interface
from zope.interface import implements
from zope.component import getMultiAdapter
from Acquisition import aq_inner

from plone.app.portlets.portlets import base
from plone.portlets.interfaces import IPortletDataProvider

from zope import schema
from zope.formlib import form
from plone.memoize.instance import memoize

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.app.vocabularies.catalog import SearchableTextSourceBinder
from plone.app.form.widgets.uberselectionwidget import UberSelectionWidget

from Products.ATContentTypes.interface import IATTopic

from plone.portlet.collection import PloneMessageFactory as _a

from my315ok.store import storeMessageFactory as _

class Islidebar_portlet(IPortletDataProvider):
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

    ajaxsrc = schema.TextLine(title=_(u"target URI"),
                             description=_(u"the URI of the resouce images view"),
                             required=True)
    interval = schema.Int(title=_(u"Interval"),
                       description=_(u"Specify the maximum number(ms) of slide image change."),
                       required=False)                   
                          
    show_more = schema.Bool(title=_a(u"Show more... link"),
                       description=_a(u"If enabled, a more... link will appear in the footer of the portlet, "
                                      "linking to the underlying Collection."),
                       required=True,
                       default=False)
    bar_height = schema.Int(title=_(u"focus_height"),
                       description=_(u"Specify the height of the images bar."),
                       required=True)

    outerid = schema.TextLine(title=_(u"images bar's located CSS id"),
                             description=_(u"the images bar's position will put"),
                             required=True)
    topid = schema.TextLine(title=_(u"images bar's top located CSS id"),
                             description=_(u"the images bar's top position will put"),
                             required=True)


    
class Assignment(base.Assignment):
    """Portlet assignment.

    This is what is actually managed through the portlets UI and associated
    with columns.
    """

    implements(Islidebar_portlet)

    header = u""
    ajaxsrc = u""
    interval = 6000         
    show_more = False
    outerid = "TopAD"
    bar_height = 180
    topid = "topid"

    def __init__(self, header=u"",ajaxsrc=u"",interval=6000,show_more=False,outerid="",bar_height=180,topid=""):
        self.header = header
        self.ajaxsrc = ajaxsrc
        self.interval = interval
        self.outerid = outerid
        self.show_more = show_more
        self.bar_height = bar_height
        self.topid = topid

    @property
    def title(self):
        """This property is used to give the title of the portlet in the
        "manage portlets" screen.
        """
        return _(u"Slide bar")


class Renderer(base.Renderer):
    """Portlet renderer.

    This is registered in configure.zcml. The referenced page template is
    rendered, and the implicit variable 'view' will refer to an instance
    of this class. Other methods can be added and referenced in the template.
    """

    render = ViewPageTemplateFile('slidebar_portlet.pt')

    def top_css(self):
        out = "height:%spx;" % str(self.data.bar_height)
        return out

    @memoize
    def render_imgjs(self):
#        import pdb
#        pdb.set_trace()
        context = aq_inner(self.context)
        outid = self.data.outerid
        imgsrc = self.data.ajaxsrc
        portal_state = getMultiAdapter((context, self.request), name=u'plone_portal_state')
        portal_url = portal_state.portal_url()
        if  imgsrc[:4] != 'http':
            imgsrc = portal_url + '/' + imgsrc  
        intervalset = self.data.interval
        out="""jq(document).ready(function()
        {imgPlayer("%(slideid)s", "%(url)s",function()
          {setTimeout(function(){ jq("#%(slideid)s").show();},200);});
         var interval = setInterval('showNumImg("%(slideid)s")', %(ms)s);
         jq("#%(slideid)s .num").bind("mouseenter",function(){clearInterval(interval);})
         jq("#%(slideid)s .num").bind("mouseleave",function(){interval = setInterval('showNumImg("%(slideid)s")', %(ms)s);})
 });""" % dict(slideid=outid,url=imgsrc,ms=intervalset)
        return out


# NOTE: If this portlet does not have any configurable parameters, you can
# inherit from NullAddForm and remove the form_fields variable.

class AddForm(base.AddForm):
    """Portlet add form.

    This is registered in configure.zcml. The form_fields variable tells
    zope.formlib which fields to display. The create() method actually
    constructs the assignment that is being added.
    """
    form_fields = form.Fields(Islidebar_portlet)

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
    form_fields = form.Fields(Islidebar_portlet)
