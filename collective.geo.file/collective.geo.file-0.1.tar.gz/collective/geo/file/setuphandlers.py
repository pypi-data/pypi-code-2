import logging
# The profile id of your package:
PROFILE_ID = 'profile-collective.geo.file:default'


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
    pass
