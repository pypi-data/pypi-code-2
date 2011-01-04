from zope import schema
from zope.interface import Interface

from zope.app.container.constraints import contains
from zope.app.container.constraints import containers

from rc.docs import docsMessageFactory as _

class IFachartikel(Interface):
    """Description of the Example Type"""
    
    # -*- schema definition goes here -*-

    untertitel = schema.TextLine(
        title=_(u"Untertitel"), 
        required=False,
        description=_(u"Untertitel des Fachartikels."),
    )


    aboutauthors = schema.Text(
        title=_(u"Zu den Autoren"), 
        required=False,
        description=_(u"Zus&auml;tzliche Angaben &uuml;ber die Autoren."),
    )

    fabstract = schema.Text(
        title=_(u"Abstract"), 
        required=False,
        description=_(u"Eine kurze Beschreibung."),
    )

    fachartikeltext = schema.Text(
        title=_(u"Fachartikel"), 
        required=False,
        description=_(u"Fachartikel erfassen."),
    )
