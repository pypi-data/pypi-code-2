from Acquisition import aq_base
from Products.CMFCore.utils import getToolByName
from Products.ZCatalog.ProgressHandler import ZLogHandler
from ZODB.POSException import ConflictError

from plone.app.upgrade.utils import logger
from plone.app.upgrade.utils import loadMigrationProfile


def alpha5_beta1(context):
    """4.0alpha5 -> 4.0beta1"""
    loadMigrationProfile(context, 'profile-plone.app.upgrade.v40:4alpha5-4beta1')


def repositionRecursiveGroupsPlugin(context):
    """If the recursive groups plugin is active, make sure it's at the bottom of the active plugins list"""
    from Products.PluggableAuthService.interfaces.plugins import IGroupsPlugin
    acl = getToolByName(context, 'acl_users')
    plugins = acl.plugins
    existingGroupsPlugins = plugins.listPlugins(IGroupsPlugin)
    if 'recursive_groups' in [a[0] for a in existingGroupsPlugins]:
        while plugins.getAllPlugins('IGroupsPlugin')['active'].index('recursive_groups') < len(existingGroupsPlugins)-1:
            plugins.movePluginsDown(IGroupsPlugin, ['recursive_groups'])


def beta1_beta2(context):
    """4.0beta1 -> 4.0beta2
    """
    loadMigrationProfile(context, 'profile-plone.app.upgrade.v40:4beta1-4beta2')


def updateSafeHTMLConfig(context):
    """Update the safe_html transform with the new config params, migrating existing config from Kupu."""
    transform = getToolByName(context, 'portal_transforms').safe_html
    transform._tr_init(1) # load new config items
    kupu_tool = getToolByName(context, 'kupu_library_tool', None)
    if kupu_tool is None:
        return
    list_conf = []
    # Kupu sets its attributes on first use, rather than providing class level defaults.
    if hasattr(kupu_tool.aq_base, 'style_whitelist'):
        styles = list(kupu_tool.style_whitelist)
        if 'padding-left' not in styles:
            styles.append('padding-left')
        list_conf.append(('style_whitelist', styles))
    if hasattr(kupu_tool.aq_base, 'class_blacklist'):
        list_conf.append(('class_blacklist', kupu_tool.class_blacklist))
    if hasattr(kupu_tool.aq_base, 'html_exclusions'):
        list_conf.append(('stripped_attributes', kupu_tool.get_stripped_attributes()))
    for k, v in list_conf:
        tdata = transform._config[k]
        if tdata == v:
            continue
        while tdata:
            tdata.pop()
        tdata.extend(v)
    if hasattr(kupu_tool.aq_base, 'html_exclusions'):
        ksc = dict((str(' '.join(k)), str(' '.join(v))) for k, v in kupu_tool.get_stripped_combinations())
        tsc = transform._config['stripped_combinations']
        if tsc != ksc:
            tsc.clear()
            tsc.update(ksc)
    transform._p_changed = True
    transform.reload()


def updateIconMetadata(context):
    """Update getIcon metadata column for all core content"""
    catalog = getToolByName(context, 'portal_catalog')
    logger.info('Updating `getIcon` metadata.')
    search = catalog.unrestrictedSearchResults
    _catalog = getattr(catalog, '_catalog', None)
    getIconPos = None
    if _catalog is not None:
        metadata = _catalog.data
        getIconPos = _catalog.schema.get('getIcon', None)
    typesToUpdate = {
        'Document' : ('document_icon.gif', 'document_icon.png'),
        'Event' : ('event_icon.gif', 'event_icon.png'),
        'File' : ('file_icon.gif', 'file_icon.png'),
        'Folder' : ('folder_icon.gif', 'folder_icon.png'),
        'Image' : ('image_icon.gif', 'image_icon.png'),
        'Link' : ('link_icon.gif', 'link_icon.png'),
        'News Item' : ('newsitem_icon.gif', 'newsitem_icon.png'),
        'Topic' : ('topic_icon.gif', 'topic_icon.png'),
    }
    ttool = getToolByName(context, 'portal_types')
    empty_icons = []
    for name in typesToUpdate.keys():
        fti = ttool.get(name)
        if fti:
            icon_expr = fti.getIconExprObject()
            if not icon_expr:
                empty_icons.append(name)

    brains = search(portal_type=empty_icons, sort_on="path")
    num_objects = len(brains)
    pghandler = ZLogHandler(1000)
    pghandler.init('Updating getIcon metadata', num_objects)
    i = 0
    for brain in brains:
        pghandler.report(i)
        brain_icon = brain.getIcon
        if not brain_icon:
            continue
        old_icons = typesToUpdate[brain.portal_type]
        if getIconPos is not None:
            # if the old icon is a standard icon, we assume no customization
            # has taken place and we can simply empty the getIcon metadata
            # without loading the object
            new_value = ''
            if brain_icon not in old_icons:
                # Otherwise we need to ask the object
                new_value = ''
                obj = brain.getObject()
                method = getattr(aq_base(obj), 'getIcon', None)
                if method is not None:
                    try:
                        new_value = obj.getIcon
                        if callable(new_value):
                            new_value = new_value()
                    except ConflictError:
                        raise
                    except Exception:
                        new_value = ''
            if brain_icon != new_value:
                rid = brain.getRID()
                record = metadata[rid]
                new_record = list(record)
                new_record[getIconPos] = new_value
                metadata[rid] = tuple(new_record)
        else:
            # If we don't have a standard catalog tool, fall back to the
            # official API
            obj = brain.getObject()
            # passing in a valid but inexpensive index, makes sure we don't
            # reindex the entire catalog including expensive indexes like
            # SearchableText
            brain_path = brain.getPath()
            try:
                catalog.catalog_object(obj, brain_path, ['id'], True, pghandler)
            except ConflictError:
                raise
            except Exception:
                pass
        i += 1
    pghandler.finish()
    logger.info('Updated `getIcon` metadata.')


def beta2_beta3(context):
    """4.0beta2 -> 4.0beta3
    """
    loadMigrationProfile(context, 'profile-plone.app.upgrade.v40:4beta2-4beta3')


def beta3_beta4(context):
    """4.0beta3 -> 4.0beta4
    """
    loadMigrationProfile(context, 'profile-plone.app.upgrade.v40:4beta3-4beta4')


def removeLargePloneFolder(context):
    """Complete removal of Large Plone Folder
    (Most of it is accomplished by the profile.)
    """
    ftool = getToolByName(context, 'portal_factory')
    l = set(ftool.getFactoryTypes())
    if 'Large Plone Folder' in l:
        l.remove('Large Plone Folder')
        ftool.manage_setPortalFactoryTypes(listOfTypeIds=list(l))


def convertToBlobs(context):
    logger.info('Started migration of files to blobs.')
    from plone.app.blob.migrations import migrateATBlobFiles
    output = migrateATBlobFiles(context)
    count = len(output.split('\n')) - 1
    logger.info('Migrated %s files to blobs.' % count)

    logger.info('Started migration of images to blobs.')
    from plone.app.blob.migrations import migrateATBlobImages
    output = migrateATBlobImages(context)
    count = len(output.split('\n')) - 1
    logger.info('Migrated %s images to blobs.' % count)

def beta4_beta5(context):
    """4.0beta4 -> 4.0beta5
    """
    loadMigrationProfile(context, 'profile-plone.app.upgrade.v40:4beta4-4beta5')

def beta5_rc1(context):
    """4.0beta5 -> 4.0rc1
    """
    loadMigrationProfile(context, 'profile-plone.app.upgrade.v40:4beta5-4rc1')

def rc1_final(context):
    """4.0rc1 -> 4.0
    """
    loadMigrationProfile(context, 'profile-plone.app.upgrade.v40:4rc1-4final')
