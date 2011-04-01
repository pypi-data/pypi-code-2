from Acquisition import aq_inner
from zope.component import getMultiAdapter
from zope.component import getUtility
from zope.interface import implements

from plone.portlets.interfaces import IPortletDataProvider
from plone.app.portlets.portlets import base

from plone.i18n.normalizer.interfaces import IIDNormalizer

from zope import schema
from zope.formlib import form

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from collective.portlet.contentprovider import ContentProviderPortletMessageFactory as _


class IContentProviderPortlet(IPortletDataProvider):
    """A portlet

    It inherits from IPortletDataProvider because for this portlet, the
    data that is being rendered and the portlet assignment itself are the
    same.
    """

    header = schema.TextLine(
        title=_(u"Portlet header"),
        description=_(u"Title of the rendered portlet"),
        required=True)

    provider = schema.TextLine(
        title=_(u"Provider"),
        description=_(u"Name of the content provider to render"),
        default=u"collective.portlet.contentprovider_vmanager",
        required=True)

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

    implements(IContentProviderPortlet)

    header = _(u"title_static_portlet", default=u"Content provider portlet")
    provider = _(u"collective.portlet.contentprovider_vmanager", default=u"collective.portlet.contentprovider_vmanager")
    omit_border = False
    footer = u""
    more_url = ''
    hide = False

    def __init__(self, header=u"", provider=u"", omit_border=False, footer=u"",
                 more_url='', hide=False):
        self.header = header
        self.provider = provider
        self.omit_border = omit_border
        self.footer = footer
        self.more_url = more_url
        self.hide = hide


    @property
    def title(self):
        """This property is used to give the title of the portlet in the
        "manage portlets" screen.
        """
        return "ContentProvider Portlet"


class Renderer(base.Renderer):
    """Portlet renderer.

    This is registered in configure.zcml. The referenced page template is
    rendered, and the implicit variable 'view' will refer to an instance
    of this class. Other methods can be added and referenced in the template.
    """

    render = ViewPageTemplateFile('contentproviderportlet.pt')
    
    def css_class(self):
        """Generate a CSS class from the portlet header
        """
        header = self.data.header
        normalizer = getUtility(IIDNormalizer)
        return "portlet-static-%s" % normalizer.normalize(header)

    def has_link(self):
        return bool(self.data.more_url)

    def has_footer(self):
        return bool(self.data.footer)

    def showProvider(self):
        """ test """
        cp = getMultiAdapter((self.context, self.request, self.view), name=self.data.provider)
        cp.update()
        return cp.render()
        


class AddForm(base.AddForm):
    """Portlet add form.

    This is registered in configure.zcml. The form_fields variable tells
    zope.formlib which fields to display. The create() method actually
    constructs the assignment that is being added.
    """
    form_fields = form.Fields(IContentProviderPortlet)

    def create(self, data):
        return Assignment(**data)


class EditForm(base.EditForm):
    """Portlet edit form.

    This is registered with configure.zcml. The form_fields variable tells
    zope.formlib which fields to display.
    """
    form_fields = form.Fields(IContentProviderPortlet)
