#

def set_mapview(context, event):
    mimetype = context.content_type
    if mimetype in ['application/vnd.google-earth.kml+xml',
                    'application/gpx+xml']:
        if 'filekml_view' in [l[0] for l in context.getAvailableLayouts()]:
            context.setLayout('filekml_view')
