"""Definition of the InfoBlad content type
"""

from zope.interface import implements

from Products.Archetypes import atapi
from Products.ATContentTypes.content import folder
from Products.ATContentTypes.content import document
from Products.ATContentTypes.content import schemata

# -*- Message Factory Imported Here -*-
from mvob.InfoBlad import InfoBladMessageFactory as _

from mvob.InfoBlad.interfaces import IInfoBlad
from mvob.InfoBlad.config import PROJECTNAME

InfoBladSchema = folder.ATFolderSchema.copy() + document.ATDocumentSchema.copy()

# Set storage on fields copied from ATFolderSchema, making sure
# they work well with the python bridge properties.

InfoBladSchema['title'].storage = atapi.AnnotationStorage()
InfoBladSchema['description'].storage = atapi.AnnotationStorage()

schemata.finalizeATCTSchema(
    InfoBladSchema,
    folderish=True,
    moveDiscussion=False
)


class InfoBlad(folder.ATFolder, document.ATDocument):
    """Type that is similar to Document but is folderish and has a view to display images in a photoalbum"""
    implements(IInfoBlad)

    meta_type = "InfoBlad"
    schema = InfoBladSchema

    title = atapi.ATFieldProperty('title')
    description = atapi.ATFieldProperty('description')

    # -*- Your ATSchema to Python Property Bridges Here ... -*-
    body = atapi.ATFieldProperty('body')


atapi.registerType(InfoBlad, PROJECTNAME)
