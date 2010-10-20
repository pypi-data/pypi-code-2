## Script (Python) "raptus.article.maps.js.py"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=foo=None,bar=None
##title=
##

from Products.CMFCore.utils import getToolByName

# LinguaPlone needs this to get the preferred language
context.REQUEST.environ['PATH_TRANSLATED'] = '/'.join(context.getPhysicalPath())
catalog = getToolByName(context, 'portal_catalog')
maps = catalog(portal_type='Map')

if not len(maps):
    return ''

template = """
jQuery(document).ready(function() {
  %(maps)s
});
"""

map_template = """
var props = {};
%(props)s%(markers)s
jQuery('.map.%(id)s').each(function() {
  jQuery(this).googleMaps(props);
});
"""

markers_template = """props['markers'] = [
%(markers)s
];"""

marker_template = """{
 %(props)s,
 'info': {
   'layer': '.%(map_id)s + .markers .%(marker_id)s'
 }
}"""

map_templates = []
for map in maps:
    obj = map.getObject()
    props = {}
    if obj.getLatitude():
        props['latitude'] = obj.getLatitude()
    if obj.getLongitude():
        props['longitude'] = obj.getLongitude()
    if obj.getDepth():
        props['depth'] = obj.getDepth()
    if obj.getHideControls():
        props['controls'] = "{'hide': true}"
    props['scroll'] = obj.getEnableScrollZoom() and 'true' or 'false'
    props['type'] = '"%s"' % obj.getMapType()
    if obj.getLayer():
        props['layer'] = '"%s"' % obj.getLayer()
    marker_brains = catalog(portal_type='Marker', path={'query': '/'.join(obj.getPhysicalPath()),
                                                        'depth': 1})
    markers = []
    for marker in marker_brains:
        marker_obj = marker.getObject()
        marker_props = {}
        if marker_obj.getLatitude():
            marker_props['latitude'] = marker_obj.getLatitude()
        if marker_obj.getLongitude():
            marker_props['longitude'] = marker_obj.getLongitude()
        markers.append(marker_template % dict(props=',\n '.join(["'%(name)s': %(value)s" % dict(name=name, value=value) for name, value in marker_props.items()]),
                                              map_id=map.UID,
                                              marker_id=marker.UID))
    map_templates.append(map_template % dict(id=map.UID,
                                             props=''.join(['props["%(name)s"] = %(value)s;\n' % dict(name=name, value=value) for name, value in props.items()]),
                                             markers=markers and markers_template % dict(markers=',\n'.join(markers)) or ''))

return template % dict(maps='\n'.join(map_templates))