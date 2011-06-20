import dm.cli.admin
import dm.environment
from kforge.ioc import RequiredFeature
import os
import sys

os.environ['DJANGO_SETTINGS_MODULE'] = 'kforge.django.settings.main'
os.umask(2)

class AdministrationUtility(dm.cli.admin.AdministrationUtility):

    def buildApplication(self):
        import kforge.soleInstance
        self.appInstance = kforge.soleInstance.application

    def do_updatefeed(self, line=None):
        args = self.convertLineToArgs(line)
        if len(args) != 0:
            print 'Error: Unexpected arguments\n'
            self.help_updatefeed(line)
            return 1
        self.updateFeedEntries()

    def updateFeedEntries(self):
        # Loop over Trac projects.
        application = self.getApplication()
        accessController = RequiredFeature('AccessController')
        if 'trac' in application.registry.plugins:
            tracPlugin = application.registry.plugins['trac']
        else:
            print "Warning: The 'trac' plugin is not enabled."
            return 1
        from kforge.url import UrlScheme
        urls = UrlScheme()
        sourceUrls = []
        tracServices = tracPlugin.services
        print "Aggregating from the following locations (set 'domain_name' if necessary):"
        for service in tracServices:
            if accessController.isAuthorised(None, 'Read', service.plugin, service.project):
                sourceUrl = urls.getServiceUrl(service) + '/timeline?ticket=on&changeset=on&milestone=on&wiki=on&max=50&daysback=90&format=rss'
                sourceUrls.append(sourceUrl)
                print sourceUrl
        application.registry.feedentries.readSources(sourceUrls)
        application.registry.feedentries.truncate()
        print "Feed summary now:"
        for e in application.registry.feedentries.listSummary():
            msg = u"%s %s %s" % (e.updated, e.source, e.title)
            print msg.encode('utf-8')

    def help_updatefeed(self, line=None):
        usage = \
'''updatefeed

Update feeds from site services.'''
        print usage

    def constructSystemDictionary(self):
        from kforge.dictionary import SystemDictionary
        return SystemDictionary()

    def do_plugin(self, line=None):
        args = self.convertLineToArgs(line)

        if len(args) == 0:
            print 'Error: Insufficient arguments\n'
            self.help_plugin(line)
            return 1
        actionName = args[0]
        if len(args) > 1:
            pluginName = args[1]
        else:
            pluginName = ''

        application = self.getApplication()
        pluginFactory = RequiredFeature('PluginFactory')
        plugin_points = pluginFactory.getEntryPoints()

        hiddenServiceNames = ['example', 'example_non_service', 'example_single_service', 'testingexample', 'apacheconfig', 'accesscontrol']
        if actionName == 'choices':
            pluginNames = [e.name for e in plugin_points]
            pluginNames.sort()
            for name in pluginNames:
                if name not in hiddenServiceNames:
                    print name
            return 0
        if actionName == 'list':
            for plugin in application.registry.plugins:
                if plugin.name not in hiddenServiceNames:
                    print plugin.name
            return 0
        if not pluginName:
            print 'Error: Plugin name required. See command help for details.'
            return 1
        if actionName == 'enable':
            if pluginName not in application.registry.plugins:
                try:
                    plugin = application.registry.plugins.create(pluginName)
                    if not plugin.getSystem():
                        raise Exception("No plugin named '%s'." % pluginName)
                    dependencyErrors = plugin.getSystem().checkDependencies()
                    if dependencyErrors:
                        print "Error: The plugin's dependencies didn't check out:"
                        for e in dependencyErrors:
                            print e
                        plugin.delete()
                        plugin.purge()
                        print
                        print "Please refer to 'doc %s' for more information." % pluginName
                        return 1
                    else:
                        msg = '''The '%s' plugin is now enabled (see 'doc' and 'show').''' % (pluginName)
                        print msg
                        return 0
                except Exception, inst:
                    if pluginName in application.registry.plugins:
                        del(application.registry.plugins[pluginName])
                    msg = "Error: Couldn't create '%s' plugin: %s" % (pluginName, str(inst))
                    print msg
                    return 1
            else:
                msg = '''The '%s' plugin is already enabled.''' % (pluginName)
                print msg
                return 0
        elif actionName == 'show' or actionName == 'status':
            try:
                pluginClass = pluginFactory.getPluginClass(pluginName)
                if not pluginClass:
                    raise Exception("No plugin named '%s'." % pluginName)
            except Exception, inst:
                print "Error: %s" % str(inst)
                return 1
            print "Package: %s" % pluginClass.__module__
            try:
                pluginObject = application.registry.plugins[pluginName]
            except:
                pluginObject = None
            pluginState = bool(pluginObject) and 'enabled' or 'disabled'
            print "State: %s" % pluginState
            print "Depends:"
            for line in pluginClass.showDepends():
                print " %s" % line
            pluginServices = pluginObject and pluginObject.services or []
            print "Services:"
            paths = RequiredFeature('FileSystem')
            for service in pluginServices:
                print " %s %s %s" % (service.project.name, service.name, str(paths.getServicePath(service)))
           
        elif actionName == 'disable':
            if pluginName in application.registry.plugins:
                plugin = application.registry.plugins[pluginName]
                from kforge.plugin.base import NonServicePlugin
                isNonServicePlugin = isinstance(plugin.getSystem(), NonServicePlugin)
                plugin.delete()
                if isNonServicePlugin:
                    print "Plugin '%s' is now disabled. All '%s' functionality" % (pluginName, pluginName)
                    print "will be suspended unless the plugin is enabled again."
                else:
                    print "Plugin '%s' is now disabled. Existing '%s' services" % (pluginName, pluginName)
                    print "will be unaffected. Users will not be able to create"
                    print "new services unless the plugin is enabled again."
                return 0
            else:
                msg = "The '%s' plugin is already disabled." % (pluginName)
                print msg
                return 0
        elif actionName == 'doc':
            # bit of a hack until we move docstring into plugin class from
            # module
            try:
                plugin_system = pluginFactory.getPluginClass(pluginName)
                pluginPackage = __import__(plugin_system.__module__, '', '', '*')
                print pluginPackage.__doc__
                return 0
            except Exception, inst:
                msg = "Couldn't get doc for '%s' plugin: %s" % (
                    pluginName, str(inst)
                )
                print msg
                return 1
        else:
            self.help_plugin()
            return 1

    def help_plugin(self, line=None):
        usage = \
'''plugin {action} [plugin-name]

{action} is one of: choices | list | doc | show | enable | disable

  * choices: list the available plugins installed on the system.
  * list: list the enabled plugins available for use by project.
  * doc: documentation on the specified plugin including details of any
    additional software that needs to be installed to use the plugin's
    functionality.
  * show: status of the plugin, indicates status of dependencies, and
    lists all project services that have been created with this plugin.
  * enable: enable the specified plugin on this KForge service.
  * disable: disable the specified plugin on this KForge service. Warning: you
    will not be able to delete a plugin if it has any associated services.
'''
        print usage

    def backupSystemService(self):
        application = self.getApplication()
        commandSet = application.commands
        backupCommandName = 'Backup'
        backupCommand = commandSet[backupCommandName](self.args[0])
        backupCommand.execute()

    def createFilesDumper(self):
        from kforge.migrate import FilesDumper
        return FilesDumper()

    def getDomainModelLoaderClass(self):
        from kforge.migrate import DomainModelLoader
        return DomainModelLoader

    def takeDatabaseAction(self, actionName):
        from kforge.utils.db import Database
        db = Database()
        actionMethod = getattr(db, actionName)
        actionMethod()

    def upgradeSystemServiceDatabase(self):
        # TODO fix this to be generic
        import kforge.utils.upgrade
        dbCommand = kforge.utils.upgrade.UpgradeDbTo0Point14()
        dbCommand.execute()
        # print 'No changes required.'

    def upgradeSystemServiceFilesystem(self):
        # ditto here with filesystem
        # should make this generic 
        # import kforge.utils.upgrade
        # filesystemCommand = kforge.utils.upgrade.UpgradeDataTo0Point11(
        #     self.servicePath, self.systemPath
        # )
        # filesystemCommand.execute()
        # nothing in fact to do
        print 'No changes required.'

    def getApacheConfigBuilderClass(self):
        from kforge.apache.config import ApacheConfigBuilder
        return ApacheConfigBuilder

    def getSystemName(self):
        return "KForge"
        
    def getSystemVersion(self):
        import kforge
        return kforge.__version__
        
    def createAboutMessage(self):
        systemName = self.getSystemName()
        systemVersion = self.getSystemVersion()
        return '%s %s' % (systemName, systemVersion)

    def touchMigratedDomainModel(self):
        application = self.getApplication()
        system = application.registry.systems[1]
        version = system.version.split('.')

        # Migrate versions earlier than v0.19.
        version_0_19 = '0.19'.split('.')
        if version < version_0_19:
           self.migrateDataDump__pre0_19__to__0_19()
           versionDump = version_0_19

        return # That's all folks! However, future migrateDataDump() 
        # method might be extended like this:

        # Migrate from v0.19 to v0.20.
        version_0_20 = '0.20'.split('.')
        if version == version_0_19:
           self.migrateDataDump__0_19__to__0_20()
           versionDump = version_0_20

        # Migrate from v0.20 to v1.0.
        version_1_0 = '1.0'.split('.')
        if version == version_0_20:
           self.migrateDataDump__0_20__to__1_0()
           versionDump = version_1_0

    def migrateDataDump__pre0_19__to__0_19(self):
        # Update system version number.
        application = self.getApplication()
        system = application.registry.systems[1]
        system.version = '0.19'
        system.save()

        # Grant permission for members to leave projects.
        from dm.strategy import CreateProtectionObject
        for person in application.registry.persons:
            for membership in person.memberships:
                protectionObject = CreateProtectionObject(membership).create()
                for permission in protectionObject.permissions:
                    if permission.action.name == 'Delete':
                        if not permission in person.grants:
                            person.grants.create(permission)

        # Digest the passwords more, see dm.dom.meta.Password.makeDigest().
        from dm.messagedigest import hmac
        from dm.messagedigest import sha256
        from dm.dictionarywords import PASSWORD_DIGEST_SECRET
        dictionary = self.constructSystemDictionary()
        for person in application.registry.persons:
            md5hexdigest = person.password
            key = dictionary[PASSWORD_DIGEST_SECRET]
            text = hmac(key=key, msg=md5hexdigest, digestmod=sha256).hexdigest()
            person.password = text
            person.save()
        

class UtilityRunner(dm.cli.admin.UtilityRunner):

    systemName = 'kforge'
    utilityClass = AdministrationUtility
    usage  = """Usage: %prog [options] [command]

Administer a KForge service, including its domain objects. 

To obtain information about the commands available run the "help" command.

    $ kforge-admin help

Domain objects (e.g. persons, projects, etc) can be administered by starting
a python shell from within interactive mode. Run "help shell" for more details.

Report bugs to <bugs@appropriatesoftware.net>."""

