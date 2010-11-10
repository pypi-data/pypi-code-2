from zope.interface import Interface
# -*- Additional Imports Here -*-
from zope import schema

from collective.geo.mapcontent import mapcontentMessageFactory as _

class IMapContent(Interface):
    """Map Content"""

    # -*- schema definition goes here -*-
    # come from collective.geo.mapwidget
    #js = schema.Text(
    #    title=_(u"OpenLayers Javascript"),
    #    required=False,
    #    description=_(u"Openlayers full map javascript"),
    #)
#
