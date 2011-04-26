"""Definition of the MediaPage content type
"""

from zope.interface import implements

from Products.Archetypes import atapi
from Products.ATContentTypes.content import folder
from Products.ATContentTypes.content import document
from Products.ATContentTypes.content import schemata

# -*- Message Factory Imported Here -*-

from Products.mediaPage.interfaces import IMediaPage
from Products.mediaPage.config import PROJECTNAME

MediaPageSchema = folder.ATFolderSchema.copy() + document.ATDocumentSchema.copy() + atapi.Schema((

    # -*- Your Archetypes field definitions here ... -*-

))

# Set storage on fields copied from ATFolderSchema, making sure
# they work well with the python bridge properties.

MediaPageSchema['title'].storage = atapi.AnnotationStorage()
MediaPageSchema['description'].storage = atapi.AnnotationStorage()
MediaPageSchema['text'].storage = atapi.AnnotationStorage()



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

    # -*- Your ATSchema to Python Property Bridges Here ... -*-

atapi.registerType(MediaPage, PROJECTNAME)
