import urllib

from zope.interface import implements
from zope.component import getMultiAdapter
from zope.component import getAdapter

from plone.portlets.interfaces import IPortletDataProvider
from plone.app.portlets.portlets import base
from plone.memoize.instance import memoize

from zope import schema
from zope.formlib import form
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from quintagroup.portlet.cumulus import cumulusportlet as pbase

from collective.portlet.localcumulus.localcumulus import LocalCumulusPortletMessageFactory as _
from collective.portlet.localcumulus.interfaces import (
    ILocalTagsRetriever, 
    ICustomLocalTagsRetriever,
)

class ICumulusPortlet(pbase.ICumulusPortlet):
    """ A cumulus tag cloud portlet.
    """
    path = schema.TextLine(
         title=_(u'Path to search'),
         description=_(u'Path to restrict searches'),)
    refreshInterval = schema.Int(
        title = _(u"Refresh interval"),
        description = _(u"The maximum time in seconds for which the portal"\
                        " will cache the results. Be careful not to use low values."),
        required = True,
        min = 1,
        default = 3600,
    )


class Assignment(pbase.Assignment):
    """Portlet assignment.

    This is what is actually managed through the portlets UI and associated
    with columns.
    """
    implements(ICumulusPortlet)
    path = u''
    refreshInterval = 1

    @property
    def title(self):
        """This property is used to give the title of the portlet in the
        "manage portlets" screen.
        """
        return _("Local Tag Cloud (cumulus)")



class Renderer(pbase.Renderer):
    """Portlet renderer.
    """

    render = ViewPageTemplateFile('cumulusportlet.pt')

    @property
    def title(self):
        return _("Local Tag Cloud")

    tagsretriever = ILocalTagsRetriever

    def getTags(self):
        tags = self.tagsretriever(self.context).getTags(data=self.data)
        if not tags: return []

        number_of_entries = [i[1] for i in tags]

        min_number = min(number_of_entries)
        max_number = max(number_of_entries)
        distance = float(max_number - min_number) or 1
        step = (self.data.largest - self.data.smallest) / distance

        result = []
        for name, number, url in tags:
            size = self.data.smallest + step * (number - min_number)
            result.append({
                'name': name,
                'size': size,
                'number_of_entries': number,
                'url': url
            })
        return result

class AddForm(pbase.AddForm):
    """Portlet add form.

    This is registered in configure.zcml. The form_fields variable tells
    zope.formlib which fields to display. The create() method actually
    constructs the assignment that is being added.
    """
    form_fields = form.Fields(ICumulusPortlet)
    def create(self, data):
        return Assignment(**data)


class EditForm(pbase.EditForm):
    """Portlet edit form.

    This is registered with configure.zcml. The form_fields variable tells
    zope.formlib which fields to display.
    """
    form_fields = form.Fields(ICumulusPortlet)

class ICustomCumulusPortlet(ICumulusPortlet):
    """ A cumulus tag cloud portlet.
    """
    search_url = schema.TextLine(
        title=_(u'Custom search url'),
        description=_(
            "Custom url to forge against"
            "choosen tag in python string formating format\n"
            "Available variables are: portal_url, portal_path, here_url, here_path, tag, tag_weight."
            ),
            default = u'%(portal_url)s/search?Subject=%(tag)s'
        )

class CustomAssignment(Assignment):
    """Portlet assignment.  """
    implements(ICustomCumulusPortlet)
    search_url=''

    @property
    def title(self):
        """This property is used to give the title of the portlet in the
        "manage portlets" screen.
        """
        return _("Custom Local Tag Cloud (cumulus)")

class CustomAddForm(AddForm):
    """Portlet add form.

    This is registered in configure.zcml. The form_fields variable tells
    zope.formlib which fields to display. The create() method actually
    constructs the assignment that is being added.
    """
    form_fields = form.Fields(ICustomCumulusPortlet)
    def create(self, data):
        return CustomAssignment(**data)


class CustomEditForm(EditForm):
    """Portlet edit form.

    This is registered with configure.zcml. The form_fields variable tells
    zope.formlib which fields to display.
    """
    form_fields = form.Fields(ICustomCumulusPortlet)

class CustomRenderer(Renderer):
    """Portlet renderer.
    """
    tagsretriever = ICustomLocalTagsRetriever
    @property
    def title(self):
        return _("Custom Local Tag Cloud")

