from zope.interface import Interface
from zope import schema

from plone.directives import form

from collective.fourohfour import MessageFactory as _

class IBrowserLayer(Interface):
    """Browser layer for the 404 view.
    """

class IFourOhFourSettings(form.Schema):
    """Settings for the 404 view
    """
    
    displaySuggestions = schema.Bool(
            title=_(u"Display suggestions"),
            description=_(u"Whether or not to display a list of suggested "
                           "pages when there are no exact redirect matches"),
            default=True,
        )
