#
from collective.geo.mapwidget.browser.widget import MapLayers
from collective.geo.mapwidget.maplayers import MapLayer
from collective.geo.contentlocations.interfaces import IGeoManager

class KMLMapLayer(MapLayer):
    """
    a layer for one level sub objects.
    """

    def __init__(self, context):
        self.context = context

    @property
    def jsfactory(self):
        context_url = self.context.absolute_url()
        if not context_url.endswith('/'):
            context_url += '/'

        return"""
        function() { return new OpenLayers.Layer.GML('%s', '%s' + '@@kml-document',
            { format: OpenLayers.Format.KML,
              projection: cgmap.createDefaultOptions().displayProjection,
              eventListeners: { 'loadend': function(event) {
                                 var extent = this.getDataExtent()
                                 this.map.zoomToExtent(extent);
                                }
                            },
              formatOptions: {
                  extractStyles: true,
                  extractAttributes: true }
            });}""" % (self.context.Title().replace("'", "&apos;"), context_url)


class KMLFileMapLayer(MapLayer):
    """
    a layer for a KML/GPX File.
    """

    def __init__(self, context, kmlfile):
        self.context = context
        self.kmlfile = kmlfile

    @property
    def jsfactory(self):
        context_url = self.kmlfile.absolute_url()
        mimetype = self.kmlfile.content_type
        if not context_url.endswith('/'):
            context_url += '/'
        if mimetype == 'application/vnd.google-earth.kml+xml':
            return u"""
            function() { return new OpenLayers.Layer.GML('%s', '%s',
                { format: OpenLayers.Format.KML,
                  projection: cgmap.createDefaultOptions().displayProjection,
                  formatOptions: {
                      extractStyles: true,
                      extractAttributes: true }
                });}""" % (self.kmlfile.Title().replace("'", "&apos;"),
                            context_url)
        elif mimetype == 'application/gpx+xml':
            return u"""function() {
                return new OpenLayers.Layer.Vector("%s", {
                    protocol: new OpenLayers.Protocol.HTTP({
                      url: "%s",
                      format: new OpenLayers.Format.GPX({
                                    extractWaypoints: true,
                                    extractRoutes: true,
                                    extractAttributes: true})
                      }),
                    strategies: [new OpenLayers.Strategy.Fixed()],
                    projection: new OpenLayers.Projection("EPSG:4326")
                  });
                }""" % (self.kmlfile.Title().replace("'", "&apos;"),
                            context_url)






class KMLFileMapLayers(MapLayers):
    '''
    create all layers for this view.
    the file itself as a layer +
    the layer defined by the annotations (if any)
    '''

    def layers(self):
        layers = super(KMLFileMapLayers, self).layers()
        try:
            geo = IGeoManager(self.context)
            if geo.isGeoreferenceable():
                if geo.getCoordinates()[0]:
                    layers.append(KMLMapLayer(self.context))
        except TypeError:
            # catch TypeError: ('Could not adapt', <ATFile ...>, <Interfa...oManager>)
            pass
        layers.append(KMLFileMapLayer(self.context,self.context))
        return layers

class KMLFileTopicMapLayers(MapLayers):
    '''
    create all layers for this view.
    the layer defined by the annotations +
    all kml files as layers
    '''


    def layers(self):
        layers = super(KMLFileTopicMapLayers, self).layers()
        layers.append(KMLMapLayer(self.context))
        for brain in self.context.queryCatalog():
            if brain.portal_type == 'File':
                object = brain.getObject()
                if object.content_type in ['application/vnd.google-earth.kml+xml',
                                            'application/gpx+xml']:
                    layers.append(KMLFileMapLayer(self.context,object))
        return layers
