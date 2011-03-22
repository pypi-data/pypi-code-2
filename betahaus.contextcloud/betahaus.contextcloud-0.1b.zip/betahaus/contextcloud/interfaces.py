from zope import schema
from zope.interface import Interface
from plone.portlets.interfaces import IPortletDataProvider

from betahaus.contextcloud import ContextCloudMessageFactory as _


class IContextCloud(Interface):
    """ Context cloud methods for a specific context. This is an adapter. """

    def getResults(index=['Subject'], nosort=False):
        """ Return a list of Tag objects with count/occurence information.
        """

    def addCloud(tags, level=5):
        """ Add tag weight information to tags.
            tags must be a list of Tag objects.
        """

    def addUrlInfo(tags, base_url=None):
        """ Add url info"""


class IContextCloudPortlet(IPortletDataProvider):
    """ Display information about context.
    """
    portlet_title = schema.TextLine(
        title = _(u"Display title"),
        required = False,
        default = _(u"Context cloud portlet"),
    )
    
    catalog_index = schema.Choice(
        title = _(u"Catalog index to use"),
        description = _(u"Will be used to generate the tags."),
        required=True,
        vocabulary="betahaus.contextcloud.SelectableCatalogIndexes",
    )

    layout = schema.Choice(
        title = _(u"Layout of results"),
        description = _(u"Show as a tag cloud or as a list."),
        required=True,
        default = 'Subject',
        vocabulary="betahaus.contextcloud.SelectableLayouts",
    )
    
    cloud_levels = schema.Int(
        title = _(u"Number of levels for the cloud"),
        description = _(u"How many different sizes should exist? Only valid if it's a cloud."),
        required = True,
        default = 5,
    )