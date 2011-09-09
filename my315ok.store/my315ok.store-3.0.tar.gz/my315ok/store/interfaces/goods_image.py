from zope import schema
from zope.interface import Interface

from zope.app.container.constraints import contains
from zope.app.container.constraints import containers

from my315ok.store import storeMessageFactory as _

class Igoods_image(Interface):
    """a image of the goods"""
    
    # -*- schema definition goes here -*-
    link2 = schema.TextLine(
        title=_(u"link to URL"), 
        required=False,
        description=_(u"LINK TO URL"),
    )

    comments = schema.SourceText(
        title=_(u"image comments"), 
        required=False,
        description=_(u"image comments"),
    )

