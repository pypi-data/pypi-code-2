"""Definition of the Map Content content type
"""

from zope.interface import implements

from Products.Archetypes import atapi
from Products.ATContentTypes.content import folder
from Products.ATContentTypes.content import schemata

# -*- Message Factory Imported Here -*-
from collective.geo.mapcontent import mapcontentMessageFactory as _

from collective.geo.mapcontent.interfaces import IMapContent
from collective.geo.mapcontent.config import PROJECTNAME
from collective.geo.mapwidget import interfaces

MapContentSchema = folder.ATFolderSchema.copy() + atapi.Schema((

    # -*- Your Archetypes field definitions here ... -*-

    atapi.TextField(
        '_js',
        storage=atapi.AnnotationStorage(),
        allowable_content_types = ['text/plain',],
        default_content_type = 'text/plain',
        default_output_type = 'text/plain',
        accessor="js",
        widget=atapi.TextAreaWidget(
            label=_(u"OpenLayers Javascript"),
            description=_(u"Openlayers full map javascript"),
            rows=50,
            format = 1,
        ),
    ),


))

# Set storage on fields copied from ATFolderSchema, making sure
# they work well with the python bridge properties.

MapContentSchema['title'].storage = atapi.AnnotationStorage()
MapContentSchema['description'].storage = atapi.AnnotationStorage()

schemata.finalizeATCTSchema(
    MapContentSchema,
    folderish=True,
    moveDiscussion=False
)


class MapContent(folder.ATFolder):
    """Map Content"""
    implements([interfaces.IMapWidget, IMapContent])

    meta_type = "MapContent"
    schema = MapContentSchema

    title = atapi.ATFieldProperty('title')
    description = atapi.ATFieldProperty('description')

    # -*- Your ATSchema to Python Property Bridges Here ... -*-
    _js = atapi.ATFieldProperty('_js')

    @property
    def mapid(self):
        return 'mapcontent'

atapi.registerType(MapContent, PROJECTNAME)
