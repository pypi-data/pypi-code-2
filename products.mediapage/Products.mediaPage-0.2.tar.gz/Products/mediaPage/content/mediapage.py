"""Definition of the MediaPage content type
"""

from zope.interface import implements

from Products.Archetypes import atapi
from Products.ATContentTypes.content import folder
from Products.ATContentTypes.content import event
from Products.ATContentTypes.content import document
from Products.ATContentTypes.content import schemata
from Products.Archetypes.atapi import DateTimeField
from Products.Archetypes.atapi import StringField
from Products.CMFCore.permissions import ModifyPortalContent, View
from Products.Archetypes.atapi import CalendarWidget
from Products.Archetypes.atapi import StringWidget
from Products.ATContentTypes import ATCTMessageFactory as _

# -*- Message Factory Imported Here -*-

from Products.mediaPage.interfaces import IMediaPage
from Products.mediaPage.config import PROJECTNAME

MediaPageSchema = folder.ATFolderSchema.copy() + document.ATDocumentSchema.copy() + atapi.Schema((

    # -*- Your Archetypes field definitions here ... -*-
    
    DateTimeField('startDate',
        required=False,
        searchable=False,
        accessor='start',
        write_permission = ModifyPortalContent,
        default_method=None,
        languageIndependent=True,
        widget = CalendarWidget(
              description= '',
              label=_(u'label_event_start', default=u'Event Starts')
              )),

    DateTimeField('endDate',
        required=False,
        searchable=False,
        accessor='end',
        write_permission = ModifyPortalContent,
        default_method = None,
        languageIndependent=True,
        widget = CalendarWidget(
              description = '',
              label = _(u'label_event_end', default=u'Event Ends')
              )),
    
    StringField('location',
        searchable=True,
        write_permission = ModifyPortalContent,
        widget = StringWidget(
            description = '',
            label = _(u'label_event_location', default=u'Event Location')
            )),
))

# Set storage on fields copied from ATFolderSchema, making sure
# they work well with the python bridge properties.

MediaPageSchema['title'].storage = atapi.AnnotationStorage()
MediaPageSchema['description'].storage = atapi.AnnotationStorage()
MediaPageSchema['text'].storage = atapi.AnnotationStorage()
MediaPageSchema['startDate'].storage = atapi.AnnotationStorage()
MediaPageSchema['endDate'].storage = atapi.AnnotationStorage()
MediaPageSchema['location'].storage = atapi.AnnotationStorage()


schemata.finalizeATCTSchema(
    MediaPageSchema,
    folderish=True,
    moveDiscussion=False
)


class MediaPage(folder.ATFolder):
    """Folderish Page"""
    implements(IMediaPage)

    meta_type = "MediaPage"
    schema = MediaPageSchema

    title = atapi.ATFieldProperty('title')
    description = atapi.ATFieldProperty('description')
    text = atapi.ATFieldProperty('text')
    startDate = atapi.ATFieldProperty('startDate')
    endDate = atapi.ATFieldProperty('endDate')
    location = atapi.ATFieldProperty('location')

    # -*- Your ATSchema to Python Property Bridges Here ... -*-

atapi.registerType(MediaPage, PROJECTNAME)
