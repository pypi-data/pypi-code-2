

def setupVarious(context):

    # Ordinarily, GenericSetup handlers check for the existence of XML files.
    # Here, we are not parsing an XML file, but we use this text file as a
    # flag to check that we actually meant for this import step to be run.
    # The file is found in profiles/default.

    if context.readDataFile('plumi.migration_various.txt') is None:
        return

    # Add additional setup code here
    from plumi.migration.interfaces.migration import IMemberMigrationConfiguration, IContentMigrationConfiguration
    from plumi.migration.browser.config import MemberMigrationConfiguration, ContentMigrationConfiguration
    from zope.component import getSiteManager
    import logging

    portal = context.getSite()
    sm = getSiteManager(portal)
    log = logging.getLogger('plumi.migration')

    if not sm.queryUtility(IMemberMigrationConfiguration, name='member_migration_config'):
        sm.registerUtility(MemberMigrationConfiguration(), IMemberMigrationConfiguration, 'member_migration_config')
        log.info('registered local utility member_migration_config')

    if not sm.queryUtility(IContentMigrationConfiguration, name='content_migration_config'):
        sm.registerUtility(ContentMigrationConfiguration(), IContentMigrationConfiguration, 'content_migration_config')
        log.info('registered local utility content_migration_config')

    log.info('setupVairous finished')

