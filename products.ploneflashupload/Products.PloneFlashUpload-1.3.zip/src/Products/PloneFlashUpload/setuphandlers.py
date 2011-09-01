from StringIO import StringIO
from Products.CMFCore import utils as cmfutils


def _remove_old_action(logger, tool, action):
    """Remove old Extensions/install.py-installed actions.

    The way that ploneflashupload added the actions doesn't even show up in
    the 3.0 portal_actions user interface.

    """
    still_existing = None
    for index, info in enumerate(tool.listActions()):
        if info.getId() == action:
            still_existing = index
    if not still_existing is None:
        tool.deleteActions([still_existing])
        logger.info('Removed old action "%s".', action)


def importVarious(context):
    if context.readDataFile('ploneflashupload.txt') is None:
        return
    site = context.getSite()
    logger = context.getLogger('ploneflashupload')
    _remove_old_action(logger,
                       cmfutils.getToolByName(site, 'portal_actions'),
                       'folderflashupload')
    _remove_old_action(logger,
                       cmfutils.getToolByName(site, 'portal_controlpanel'),
                       'flashuploadconfiglet')
