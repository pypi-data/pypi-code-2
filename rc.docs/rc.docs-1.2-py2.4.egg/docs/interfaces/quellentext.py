from zope import schema
from zope.interface import Interface

from zope.app.container.constraints import contains
from zope.app.container.constraints import containers

from rc.docs import docsMessageFactory as _

class IQuellentext(Interface):
    """Quellentext zum Projekt einfügen"""
    
    # -*- schema definition goes here -*-

    fundort = schema.TextLine(
        title=_(u"Fundort"), 
        required=False,
        description=_(u"ID oder String"),
    )


    druckort = schema.TextLine(
        title=_(u"Druckort"), 
        required=False,
        description=_(u"ID oder String"),
    )

    regest = schema.Text(
        title=_(u"Regest"), 
        required=False,
        description=_(u"Kurzbeschreibung eingeben."),
    )

    originaltext = schema.Text(
        title=_(u"Originaltext"), 
        required=False,
        description=_(u"Text erfassen."),
    )

    #kommentar = schema.Text(
        #title=_(u"Kommentar"), 
        #required=False,
        #description=_(u"Kommentare zum Artikel eingeben."),
    #)


