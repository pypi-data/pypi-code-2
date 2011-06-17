import logging
from Products.CMFPlone.utils import getToolByName
from Products.MimetypesRegistry.MimeTypeItem import MimeTypeItem
# The profile id of your package:
PROFILE_ID = 'profile-collective.geo.file:default'

gis_mimetypes = [
    {'name': 'application/vnd.google-earth.kml+xml',
    'extensions': ('kml',),
    'globs': ('*.kml',),
    'icon_path': 'text.png',
    'binary': True,
    'mimetypes': ('application/vnd.google-earth.kml+xml',)},
    {'name': 'application/gpx+xml',
    'extensions': ('gpx',),
    'globs': ('*.gpx',),
    'icon_path': 'text.png',
    'binary': True,
    'mimetypes': ('application/gpx+xml',)}
]


def do_nothing(context, logger=None):
    if logger is None:
        # Called as upgrade step: define our own logger.
        logger = logging.getLogger('collective.geo.file')
        logger.info("Empty upgrade step")




def import_various(context):
    """Import step for configuration that is not handled in xml files.
    """
    # Only run step if a flag file is present
    if context.readDataFile('collective.geo.file-default.txt') is None:
        return
    logger = context.getLogger('collective.geo.file')
    site = context.getSite()

    mimetypes_registry = getToolByName(site, 'mimetypes_registry')
    all_mimetypes = mimetypes_registry.list_mimetypes()

    for mtype in gis_mimetypes:
        if mtype['name'] not in all_mimetypes:
            logger.info('Registering mimetype %s' % mtype['name'])
            mimetypes_registry.register(MimeTypeItem(**mtype))
