from zope import schema
from zope.interface import Interface 

from zope.app.container.constraints import contains
from zope.app.container.constraints import containers

from medialog.boardfile import boardfileMessageFactory as _


class IPublication(Interface):
    """Publication content type"""
    
    publicationtitle= schema.TextLine(
        title=_(u"Publication Title"), 
        required=True,
        description=_(u"Title as it appears in Publication"),
    )

    authorlist = schema.List(
        title=_(u"Authorlist"), 
        required=True,
        description=_(u"List of Authors"),
    )


    wp = schema.TextLine(
        title=_(u"WP"), 
        required=True,
        description=_(u"Select one"),
    )

    publishingyear = schema.Int(
        title=_(u"Publishing Year"), 
        required=True,
        description=_(u"Publishing Year"),
    )

