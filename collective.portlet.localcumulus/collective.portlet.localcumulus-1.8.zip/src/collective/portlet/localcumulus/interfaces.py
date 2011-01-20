from Products.PluggableAuthService.interfaces.authservice import IPropertiedUser
from quintagroup.portlet.cumulus import interfaces

from zope import interface
class IMyPortalUser(IPropertiedUser):
    """ Marker interface implemented by users in my portal. """


class ILocalTagsRetriever(interfaces.ITagsRetriever):
    """."""

    data = interface.Attribute("data", "Data Assigment")

    def getTags(number=None, data=None):
        """Return keywords restricted to data.path if present."""


class ICustomLocalTagsRetriever(ILocalTagsRetriever):
    """ICustomLocalTagsRetriever."""
