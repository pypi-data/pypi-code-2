from zope.interface import implements

from plone.portlets.interfaces import IPortletDataProvider
from plone.app.portlets.portlets import base

from zope import schema
from zope.formlib import form
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.memoize.instance import memoize

from medialog.portlet.sitemap import SitemapPortletMessageFactory as _

class ISitemapPortlet(IPortletDataProvider):
    """A portlet

    It inherits from IPortletDataProvider because for this portlet, the
    data that is being rendered and the portlet assignment itself are the
    same.
    """

    # TODO: Add any zope.schema fields here to capture portlet configuration
    # information. Alternatively, if there are no settings, leave this as an
    # empty interface - see also notes around the add form and edit form
    # below.

    sitemaptitle = schema.TextLine(title=_(u"Title"),
                             description=_(u"The title of the sitemap portlet"),
                             required=True)

class Assignment(base.Assignment):
    """Portlet assignment.

    This is what is actually managed through the portlets UI and associated
    with columns.
    """

    implements(ISitemapPortlet)
    
    sitemaptitle = u''

    def __init__(self, sitemaptitle=None):
        self.sitemaptitle = sitemaptitle

    # TODO: Set default values for the configurable parameters here

    # some_field = u""

    # TODO: Add keyword parameters for configurable parameters here
    # def __init__(self, some_field=u""):
    #    self.some_field = some_field


    @property
    def title(self):
        """This property is used to give the title of the portlet in the
        "manage portlets" screen.
        """
        return "Sitemap Portlet"


class Renderer(base.Renderer):
    """Portlet renderer.

    This is registered in configure.zcml. The referenced page template is
    rendered, and the implicit variable 'view' will refer to an instance
    of this class. Other methods can be added and referenced in the template.
    """

    render = ViewPageTemplateFile('sitemapportlet.pt')


class AddForm(base.AddForm):
    """Portlet add form.

    This is registered in configure.zcml. The form_fields variable tells
    zope.formlib which fields to display. The create() method actually
    constructs the assignment that is being added.
    """
    form_fields = form.Fields(ISitemapPortlet)

    def create(self, data):
        return Assignment(**data)        

class AddForm(base.AddForm):
    form_fields = form.Fields(ISitemapPortlet)
    label = _(u'Add the Sitemap Portlet')
    description = _(u'This portlet whows the sitemap in a portlet (suprise). You should also install jquery / jquery ui.')

    def create(self, data):
        assignment = Assignment()
        form.applyChanges(assignment, self.form_fields, data)
        return assignment


# NOTE: If this portlet does not have any configurable parameters, you
# can use the next AddForm implementation instead of the previous.

# class AddForm(base.NullAddForm):
#     """Portlet add form.
#     """
#     def create(self):
#         return Assignment()


# NOTE: If this portlet does not have any configurable parameters, you
# can remove the EditForm class definition and delete the editview
# attribute from the <plone:portlet /> registration in configure.zcml


class EditForm(base.EditForm):
    """Portlet edit form.

    This is registered with configure.zcml. The form_fields variable tells
    zope.formlib which fields to display.
    """
    form_fields = form.Fields(ISitemapPortlet)
