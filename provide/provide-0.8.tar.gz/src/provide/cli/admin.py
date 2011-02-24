import dm.cli.admin
import os.path
import sys
import commands

# Todo: Rename the model objects nicely, then bubble the names up.

class AdministrationUtility(dm.cli.admin.AdministrationUtility):

    # todo: Do something with this thing.
    servicePathEnvironVariableName = 'PROVIDEHOME'

    def handleNullArgs(self):
        self.runScript()

    def buildApplication(self):
        import provide.soleInstance
        self.appInstance = provide.soleInstance.application

    def backupSystemService(self):
        import provide.soleInstance
        commandSet = provide.soleInstance.application.commands
        backupCommandName = 'Backup'
        backupCommand = commandSet[backupCommandName](self.args[0])
        backupCommand.execute()

    def takeDatabaseAction(self, actionName):
        from provide.utils.db import Database
        db = Database()
        actionMethod = getattr(db, actionName)
        actionMethod()

    def buildApacheConfig(self):
        from dm.apache.apacheconfig import ApacheConfigBuilder
        configBuilder = ApacheConfigBuilder()
        configBuilder.buildConfig()

    def reloadApacheConfig(self):
        from dm.apache.apacheconfig import ApacheConfigBuilder
        configBuilder = ApacheConfigBuilder()
        configBuilder.reloadConfig()

    def getSystemName(self):
        return "Provide"
        
    def getSystemVersion(self):
        import provide
        return provide.__version__
        
    def createAboutMessage(self):
        systemName = self.getSystemName()
        systemVersion = self.getSystemVersion()
        aboutMessage = \
'''This is %s version %s.

Copyright the Appropriate Software Foundation. Provide is open-source
software licensed under the GPL v2.0. See COPYING for details.
''' % (systemName, systemVersion)
        return aboutMessage

    def do_scripts(self, line=None):
        self.convertLineToArgs(line)
        if len(self.args) == 2:
            provisionName = self.args[0]
            provisionVersion = self.args[1]
            self.getScripts(provisionName, provisionVersion)
            return 0
        else:
            self.help_scripts(line)
            return 1

    def help_scripts(self, line=None):
        usage  = 'scripts application version [path]\n'
        usage += '\tapplication is the name of the application system\n'
        usage += '\tversion is the version of the application system\n'
        print usage

    def do_provision(self, line=None):
        return self.do_provisioncreate(line)

    def help_provision(self, line=None):
        usage  = 'provision application\n'
        usage += '\tapplication is the name of the application system\n'
        print usage

    def do_rmprovision(self, line=None):
        return self.do_provisiondelete(line)

    def do_remove(self, line=None):
        return self.do_provisiondelete(line)

    def do_link(self, line=None):
        return self.do_linkcreate(line)

    def do_rmlink(self, line=None):
        return self.do_linkdelete(line)

    def do_release(self, line=None):
        return self.do_appload(line)

    def help_release(self, line=None):
        usage  = 'provision application version\n'
        usage += '\tapplication is the name of the application system\n'
        usage += '\tversion is the version of the application system\n'
        print usage

    def do_rmrelease(self, line=None):
        return self.do_appdelete(line)

    def do_application(self, line=None):
        return self.do_appload(line)

    def do_rmapplication(self, line=None):
        return self.do_appdelete(line)

    def do_depends(self, line=None):
        return self.do_depload(line)

    def do_service(self, line=None):
        return self.do_servicecreate(line)

    def do_deploy(self, line=None):
        return self.do_servicecreate(line)

    def do_test(self, line=None):
        return self.do_servicetest(line)

    def do_commission(self, line=None):
        return self.do_serviceinit(line)

    def help_commission(self, line=None):
        usage  = 'commission application version service\n'
        usage += '\tapplication is the name of the application system\n'
        usage += '\tversion is the version of the application system\n'
        usage += '\tservice is the deployment of the application system\n'
        print usage

    def do_rmservice(self, line=None):
        return self.do_servicedelete(line)

    def do_dump(self, line=None):
        return self.do_datadump(line)

    def do_rmdump(self, line=None):
        return self.do_datadelete(line)

    def do_plan(self, line=None):
        return self.do_planload(line)

    def help_plan(self, line=None):
        usage  = 'plan application plan path\n'
        usage += '\tapplication is the name of the application system\n'
        usage += '\tplan is the name of the migration plan\n'
        usage += '\tpath is the location of the migration plan file'
        print usage

    def do_rmplan(self, line=None):
        return self.do_plandelete(line)


# old command names....

    def do_provisioncreate(self, line=None):
        self.convertLineToArgs(line)
        if len(self.args) == 1:
            provisionName = self.args[0]
            self.createProvision(provisionName)
            return 0
        elif len(self.args) == 2:
            provisionName = self.args[0]
            location = self.args[1]
            self.createProvision(provisionName, location)
            return 0
        else:
            self.help_provisioncreate(line)
            return 1

    def help_provisioncreate(self, line=None):
        usage  = 'provisioncreate application [location]\n'
        usage += '\tapplication is the name of the application system\n'
        usage += '\tlocation is the base path to released files\n'
        print usage

    def do_provisionlist(self, line=None):
        self.convertLineToArgs(line)
        if len(self.args) != 0:
            print 'ERROR: Inadequate arguments (%s)\n' % len(self.args)
            self.help_provisionlist(line)
            return 1
        else:
            self.listProvisions()
            return 0

    def help_provisionlist(self, line=None):
        usage  = 'provisionlist\n'
        print usage

    def do_provisiondelete(self, line=None):
        self.convertLineToArgs(line)
        if len(self.args) != 1:
            print 'ERROR: Inadequate arguments (%s)\n' % len(self.args)
            self.help_provisiondelete(line)
            return 1
        else:
            provisionName = self.args[0]
            self.deleteProvision(provisionName)
            return 0

    def help_provisiondelete(self, line=None):
        usage  = 'provisiondelete application\n'
        usage += '\tapplication is the name of the application system\n'
        print usage

    def do_provisionpurge(self, line=None):
        self.convertLineToArgs(line)
        if len(self.args) != 1:
            print 'ERROR: Inadequate arguments (%s)\n' % len(self.args)
            self.help_provisionpurge(line)
            return 1
        else:
            provisionName = self.args[0]
            self.purgeProvision(provisionName)
            return 0

    def help_provisionpurge(self, line=None):
        usage  = 'provisionpurge application\n'
        usage += '\tapplication is the name of the application system\n'
        print usage
    
    def do_linkcreate(self, line=None):
        self.convertLineToArgs(line)
        if len(self.args) == 5:
            usedProvisionName = self.args[0]
            usedApplicationName = self.args[1]
            usedServiceName = self.args[2]
            usingProvisionName = self.args[3]
            usingApplicationName = self.args[4]
            self.createLink(
                usedProvisionName,
                usedApplicationName,
                usedServiceName,
                usingProvisionName,
                usingApplicationName
            )
            return 0
        else:
            self.help_linkcreate(line)
            return 1

    def help_linkcreate(self, line=None):
        usage  = 'link usedapp usedver usedser usingapp usingver\n'
        usage += '\tusedapp is the name of the used application system\n'
        usage += '\tusedver is the version of the used application system\n'
        usage += '\tusedser is the name of the used application service\n'
        usage += '\tusingapp is the name of the using using application system\n'
        usage += '\tusingver is the version of the using application system\n'
        print usage

    def do_linkdelete(self, line=None):
        self.convertLineToArgs(line)
        if len(self.args) == 5:
            usedProvisionName = self.args[0]
            usedApplicationName = self.args[1]
            usedServiceName = self.args[2]
            usingProvisionName = self.args[3]
            usingApplicationName = self.args[4]
            self.deleteLink(
                usedProvisionName,
                usedApplicationName,
                usedServiceName,
                usingProvisionName,
                usingApplicationName
            )
        else:
            self.help_linkcreate(line)
            return 1

    def help_linkdelete(self, line=None):
        usage  = 'rmlink usedapp usedver usedser usingapp usingver\n'
        usage += '\tusedapp is the name of the used application system\n'
        usage += '\tusedver is the version of the used application system\n'
        usage += '\tusedser is the name of the used application service\n'
        usage += '\tusingapp is the name of the using using application system\n'
        usage += '\tusingver is the version of the using application system\n'
        print usage

    def do_planload(self, line=None):
        self.convertLineToArgs(line)
        if len(self.args) != 3:
            print 'ERROR: Inadequate arguments (%s)\n' % len(self.args)
            self.help_planload(line)
            return 1
        else:
            provisionName = self.args[0]
            planName = self.args[1]
            planPath = self.args[2]
            self.loadPlan(
                provisionName, planName, planPath
            )
            return 0

    def help_planload(self, line=None):
        usage  = 'planload application plan path\n'
        usage += '\tapplication is the name of the application system\n'
        usage += '\tplan is the name of the migration plan\n'
        usage += '\tpath is the location of the migration plan file'
        print usage

    def do_plandelete(self, line=None):
        self.convertLineToArgs(line)
        if len(self.args) != 2:
            print 'ERROR: Inadequate arguments (%s)\n' % len(self.args)
            self.help_plandelete(line)
            return 1
        else:
            provisionName = self.args[0]
            planName = self.args[1]
            self.deletePlan(provisionName, planName)
            return 0

    def help_plandelete(self, line=None):
        usage  = 'plandelete application plan\n'
        usage += '\tapplication is the name of the application system\n'
        usage += '\tplan is the name of the migration plan\n'
        print usage

    def do_appload(self, line=None):
        self.convertLineToArgs(line)
        if len(self.args) == 2:
            provisionName = self.args[0]
            applicationName = self.args[1]
            self.loadApplication(
                provisionName, applicationName
            )
            return 0
        if len(self.args) == 3:
            provisionName = self.args[0]
            applicationName = self.args[1]
            applicationPath = self.args[2]
            self.loadApplication(
                provisionName, applicationName, applicationPath
            )
            return 0
        if len(self.args) >= 4 :
            provisionName = self.args[0]
            applicationName = self.args[1]
            self.loadApplication(
                provisionName, applicationName, " ".join(self.args[2:])
            )
            return 0
        else:
            print 'ERROR: Inadequate arguments (%s)\n' % len(self.args)
            self.help_appload(line)
            return 1

    def help_appload(self, line=None):
        usage  = 'appload application version [path]\n'
        usage += '\tapplication is the name of the application system\n'
        usage += '\tversion is the version of the application system\n'
        usage += '\tpath is the path to an application system tarball'
        print usage

    def do_releaselist(self, line=None):
        self.convertLineToArgs(line)
        if len(self.args) != 1:
            print 'ERROR: Inadequate arguments (%s)\n' % len(self.args)
            self.help_releaselist(line)
            return 1
        else:
            provisionName = self.args[0]
            self.listApplications(provisionName)
            return 0

    def help_releaselist(self, line=None):
        usage  = 'releaselist provision\n'
        usage += '\tprovision is the name of the application system\n'
        print usage

    def do_applist(self, line=None):
        self.convertLineToArgs(line)
        if len(self.args) != 1:
            print 'ERROR: Inadequate arguments (%s)\n' % len(self.args)
            self.help_applist(line)
            return 1
        else:
            provisionName = self.args[0]
            self.listApplications(provisionName)
            return 0

    def help_applist(self, line=None):
        usage  = 'applist provision\n'
        usage += '\tprovision is the name of the application system\n'
        print usage

    def do_appdelete(self, line=None):
        self.convertLineToArgs(line)
        if len(self.args) != 2:
            print 'ERROR: Inadequate arguments (%s)\n' % len(self.args)
            self.help_appdelete(line)
            return 1
        else:
            provisionName = self.args[0]
            applicationName = self.args[1]
            self.deleteApplication(provisionName, applicationName)
            return 0

    def help_appdelete(self, line=None):
        usage  = 'appdelete application version\n'
        usage += '\tapplication is the name of the application system\n'
        usage += '\tversion is the version of the application system\n'
        print usage

    def do_apppurge(self, line=None):
        self.convertLineToArgs(line)
        if len(self.args) != 2:
            print 'ERROR: Inadequate arguments (%s)\n' % len(self.args)
            self.help_apppurge(line)
            return 1
        else:
            provisionName = self.args[0]
            applicationName = self.args[1]
            self.purgeApplication(provisionName, applicationName)
            return 0

    def help_apppurge(self, line=None):
        usage  = 'apppurge application version\n'
        usage += '\tapplication is the name of the application system\n'
        usage += '\tversion is the version of the application system\n'
        print usage

    def do_depload(self, line=None):
        self.convertLineToArgs(line)
        if len(self.args) == 3:
            provisionName = self.args[0]
            applicationName = self.args[1]
            dependencyName = ""
            dependencyVersion = ""
            dependencyPath = self.args[2]
        elif len(self.args) == 4:
            provisionName = self.args[0]
            applicationName = self.args[1]
            dependencyName = self.args[2]
            dependencyVersion = self.args[3]
            dependencyPath = ""
        elif len(self.args) == 5:
            provisionName = self.args[0]
            applicationName = self.args[1]
            dependencyName = self.args[2]
            dependencyVersion = self.args[3]
            dependencyPath = self.args[4]
        else:
            print 'ERROR: Inadequate arguments (%s)\n' % len(self.args)
            self.help_depload(line)
            return 1
        self.loadDependency(
            provisionName,
            applicationName,
            dependencyName,
            dependencyVersion,
            dependencyPath,
        )
        return 0

    def help_depload(self, line=None):
        usage  = 'depload application version deppath\n'
        usage  = 'depload application version depname depversion\n'
        usage += '\tapplication is the name of the application system\n'
        usage += '\tversion is the version of the application system\n'
        usage += '\tdeppath is the path to the tarball'
        usage += '\tdepname is the name of the dependency\n'
        usage += '\tdepversion is the name of the dependency\n'
        print usage

    def do_depdelete(self, line=None):
        self.convertLineToArgs(line)
        if len(self.args) != 3:
            print 'ERROR: Inadequate arguments (%s)\n' % len(self.args)
            self.help_depdelete(line)
            return 1
        else:
            provisionName = self.args[0]
            applicationName = self.args[1]
            dependencyName = self.args[2]
            self.deleteDependency(
                provisionName, applicationName, dependencyName
            )
            return 0

    def help_depdelete(self, line=None):
        usage  = 'depunload application version dependency\n'
        usage += '\tapplication is the name of the application system\n'
        usage += '\tversion is the version of the application system\n'
        usage += '\tdependency is the name of the application dependency\n'
        print usage

    def do_servicecreate(self, line=None):
        self.convertLineToArgs(line)
        if len(self.args) == 3:
            provisionName = self.args[0]
            applicationName = self.args[1]
            serviceName = self.args[2]
            self.createService(provisionName, applicationName, serviceName)
            return 0
        else:
            print 'ERROR: Inadequate arguments (%s)\n' % len(self.args)
            self.help_servicecreate(line)
            return 1

    def help_servicecreate(self, line=None):
        usage  = 'servicecreate application version service\n'
        usage += '\tapplication is the name of the application system\n'
        usage += '\tversion is the version of the application system\n'
        usage += '\tservice is the name of the new service\n'
        print usage

    def do_path(self, line=None):
        self.convertLineToArgs(line)
        if len(self.args) == 3:
            provisionName = self.args[0]
            applicationName = self.args[1]
            serviceName = self.args[2]
            self.writePath(provisionName, applicationName, serviceName)
            return 0
        else:
            self.help_path(line)
            return 1

    def help_path(self, line=None):
        usage  = 'path application version service\n'
        usage += '\tapplication is the name of the application system\n'
        usage += '\tversion is the version of the application system\n'
        usage += '\tservice is the name of the application service\n'
        print usage

    def do_servicelist(self, line=None):
        self.convertLineToArgs(line)
        if len(self.args) != 2:
            print 'ERROR: Inadequate arguments (%s)\n' % len(self.args)
            self.help_servicelist(line)
            return 1
        else:
            provisionName = self.args[0]
            applicationName = self.args[1]
            self.listServices(provisionName, applicationName)
            return 0

    def help_servicelist(self, line=None):
        usage  = 'servicelist application version\n'
        usage += '\tapplication is the name of the application system\n'
        usage += '\tversion is the version of the application system\n'
        print usage

    def do_serviceconfig(self, line=None):
        self.convertLineToArgs(line)
        if len(self.args) != 3:
            print 'ERROR: Inadequate arguments (%s)\n' % len(self.args)
            self.help_serviceconfig(line)
            return 1
        else:
            provisionName = self.args[0]
            applicationName = self.args[1]
            serviceName = self.args[2]
            self.editServiceConfig(provisionName, applicationName, serviceName)
            return 0

    def help_serviceconfig(self, line=None):
        usage  = 'serviceconfig application version service\n'
        usage += '\tapplication is the application system name\n'
        usage += '\tversion is the version of the application system\n'
        usage += '\tservice is the application service to be tested\n'
        print usage

    def do_servicetest(self, line=None):
        self.convertLineToArgs(line)
        if len(self.args) != 3:
            print 'ERROR: Inadequate arguments (%s)\n' % len(self.args)
            self.help_servicetest(line)
            return 1
        else:
            provisionName = self.args[0]
            applicationName = self.args[1]
            serviceName = self.args[2]
            self.unitTestService(provisionName, applicationName, serviceName)
            return 0

    def help_servicetest(self, line=None):
        usage  = 'servicetest application version service\n'
        usage += '\tapplication is the application system name\n'
        usage += '\tversion is the version of the application system\n'
        usage += '\tservice is the application service to be tested\n'
        print usage

    def do_serviceinit(self, line=None):
        self.convertLineToArgs(line)
        if len(self.args) != 3:
            print 'ERROR: Inadequate arguments (%s)\n' % len(self.args)
            self.help_serviceinit(line)
            return 1
        else:
            provisionName = self.args[0]
            applicationName = self.args[1]
            serviceName = self.args[2]
            self.commissionService(provisionName, applicationName, serviceName)
            return 0

    def help_serviceinit(self, line=None):
        usage  = 'serviceinit application version service\n'
        usage += '\tapplication is the application system name\n'
        usage += '\tversion is the version of the application system\n'
        usage += '\tservice is the service to be initialised for production\n'
        print usage

    def do_servicedelete(self, line=None):
        self.convertLineToArgs(line)
        if len(self.args) != 3:
            print 'ERROR: Inadequate arguments (%s)\n' % len(self.args)
            self.help_servicedelete(line)
            return 1
        else:
            provisionName = self.args[0]
            applicationName = self.args[1]
            serviceName = self.args[2]
            self.deleteService(provisionName, applicationName, serviceName)
            return 0

    def help_servicedelete(self, line=None):
        usage  = 'servicedelete application version service\n'
        usage += '\tapplication is the application system name\n'
        usage += '\tversion is the version of the application system\n'
        usage += '\tservice is the old application service name\n'
        print usage

    def do_servicepurge(self, line=None):
        self.convertLineToArgs(line)
        if len(self.args) != 3:
            print 'ERROR: Inadequate arguments (%s)\n' % len(self.args)
            self.help_servicepurge(line)
            return 1
        else:
            provisionName = self.args[0]
            applicationName = self.args[1]
            serviceName = self.args[2]
            self.purgeService(provisionName, applicationName, serviceName)
            return 0

    def help_servicepurge(self, line=None):
        usage  = 'servicepurge application version service\n'
        usage += '\tapplication is the application system name\n'
        usage += '\tversion is the version of the application system\n'
        usage += '\tservice is the delete application service name\n'
        print usage

    def do_purpose(self, line=None):
        self.convertLineToArgs(line)
        if len(self.args) == 2:
            provisionName = self.args[0]
            purposeName = self.args[1]
            self.createPurpose(provisionName, purposeName)
            return 0
        else:
            print 'ERROR: Inadequate arguments (%s)\n' % len(self.args)
            self.help_purpose(line)
            return 1

    def help_purpose(self, line=None):
        usage  = 'purpose application intention\n'
        usage += '\tapplication is the application system name\n'
        usage += '\tintention is the name of the purpose\n'
        print usage

    def do_rmpurpose(self, line=None):
        return self.do_delpurpose(line)

    def do_delpurpose(self, line=None):
        self.convertLineToArgs(line)
        if len(self.args) == 2:
            provisionName = self.args[0]
            purposeName = self.args[1]
            self.deletePurpose(provisionName, purposeName)
            return 0
        else:
            print 'ERROR: Inadequate arguments (%s)\n' % len(self.args)
            self.help_delpurpose(line)
            return 1

    def help_delpurpose(self, line=None):
        usage  = 'delpurpose application intention\n'
        usage += '\tapplication is the application system name\n'
        usage += '\tintention is the name of the purpose\n'
        print usage

    def do_designate(self, line=None):
        self.convertLineToArgs(line)
        if len(self.args) == 4:
            provisionName = self.args[0]
            applicationName = self.args[1]
            serviceName = self.args[2]
            purposeName = self.args[3]
            self.designatePurpose(
                provisionName, applicationName, serviceName, purposeName
            )
            return 0
        else:
            print 'ERROR: Inadequate arguments (%s)\n' % len(self.args)
            self.help_designate(line)
            return 1

    def help_designate(self, line=None):
        usage  = 'designate application version service purpose\n'
        usage += '\tapplication is the application system name\n'
        usage += '\tversion is the version of the application system\n'
        usage += '\tservice is the application service name\n'
        usage += '\tpurpose is the name of the purpose\n'
        print usage

    def do_which(self, line=None):
        self.convertLineToArgs(line)
        if len(self.args) == 2:
            provisionName = self.args[0]
            purposeName = self.args[1]
            self.whichPurpose(provisionName, purposeName)
            return 0
        else:
            print 'ERROR: Inadequate arguments (%s)\n' % len(self.args)
            self.help_which(line)
            return 1

    def help_which(self, line=None):
        usage  = 'which application purpose\n'
        usage += '\tapplication is the application system name\n'
        usage += '\tpurpose is the name of the purpose\n'
        usage += '\n'
        usage += '\tPrints the version and service name which the purpose designates\n'
        print usage

    def do_datadump(self, line=None):
        self.convertLineToArgs(line)
        if len(self.args) != 4:
            print 'ERROR: Inadequate arguments (%s)\n' % len(self.args)
            self.help_datadump(line)
            return 1
        else:
            provisionName = self.args[0]
            applicationName = self.args[1]
            serviceName = self.args[2]
            dumpName = self.args[3]
            self.dumpData(provisionName, applicationName, serviceName, dumpName)
            return 0

    def help_datadump(self, line=None):
        usage  = 'datadump application version service dump\n'
        usage += '\tapplication is the application system name\n'
        usage += '\tversion is the version of the application system\n'
        usage += '\tservice is the application service name\n'
        usage += '\tdump is the name of the data dump\n'
        print usage

    def do_dataload(self, line=None):
        self.convertLineToArgs(line)
        if len(self.args) != 5:
            print 'ERROR: Inadequate arguments (%s)\n' % len(self.args)
            self.help_dataload(line)
            return 1
        else:
            provisionName = self.args[0]
            applicationName = self.args[1]
            serviceName = self.args[2]
            dumpName = self.args[3]
            dumpLocation = self.args[4]
            self.loadData(
                provisionName,
                applicationName,
                serviceName,
                dumpName,
                dumpLocation
            )
            return 0

    def help_dataload(self, line=None):
        usage  = 'dataload application version service dump path\n'
        usage += '\tapplication is the application system name\n'
        usage += '\tversion is the version of the application system\n'
        usage += '\tservice is the application service name\n'
        usage += '\tpath is the location of the datadump file'
        print usage

    def do_datainit(self, line=None):
        self.convertLineToArgs(line)
        if len(self.args) != 4:
            print 'ERROR: Inadequate arguments (%s)\n' % len(self.args)
            self.help_datainit(line)
            return 1
        else:
            provisionName = self.args[0]
            applicationName = self.args[1]
            serviceName = self.args[2]
            dumpName = self.args[3]
            self.initData(provisionName, applicationName, serviceName, dumpName)
            return 0

    def help_datainit(self, line=None):
        usage  = 'datainit application version service dump\n'
        usage += '\tapplication is the application system name\n'
        usage += '\tversion is the version of the application system\n'
        usage += '\tservice is the application service name\n'
        usage += '\tdump is the name of the data dump\n'
        print usage

    def do_datamove(self, line=None):
        self.convertLineToArgs(line)
        if len(self.args) != 7:
            print 'ERROR: Inadequate arguments (%s)\n' % len(self.args)
            self.help_datamove(line)
            return 1
        else:
            provisionName = self.args[0]
            applicationSourceName = self.args[1]
            serviceSourceName = self.args[2]
            dumpSourceName = self.args[3]
            applicationDestName = self.args[4]
            serviceDestName = self.args[5]
            dumpDestName = self.args[6]
            self.moveData(
                provisionName, 
                applicationSourceName, serviceSourceName, dumpSourceName,
                applicationDestName, serviceDestName, dumpDestName
            )
            return 0

    def help_datamove(self, line=None):
        usage  = 'datamove application fromversion fromservice fromdump toversion toservice todump\n'
        usage += '\tapplication is the application system name\n'
        usage += '\tfromversion is the source version\n'
        usage += '\tfromservice is the source service name\n'
        usage += '\tfromdump is the source data dump\n'
        usage += '\ttoversion is the destination version\n'
        usage += '\ttoservice is the destination service\n'
        usage += '\ttodump is the destination data dump\n'
        print usage

    def do_datadelete(self, line=None):
        self.convertLineToArgs(line)
        if len(self.args) != 4:
            print 'ERROR: Inadequate arguments (%s)\n' % len(self.args)
            self.help_datadelete(line)
            return 1
        else:
            provisionName = self.args[0]
            applicationName = self.args[1]
            serviceName = self.args[2]
            dumpName = self.args[3]
            self.deleteData(
                provisionName, applicationName, serviceName, dumpName
            )
            return 0

    def help_datadelete(self, line=None):
        usage  = 'datadelete application version service dump\n'
        usage += '\tapplication is the application system name\n'
        usage += '\tversion is the source version\n'
        usage += '\tservice is the source service name\n'
        usage += '\tdump is the source data dump\n'
        print usage

    def getScripts(self, provisionName, provisionVersion):
        scriptsUrl = "http://appropriatesoftware.net/provide/docs/provide-%s-%s.tar.gz" % (
            provisionName, provisionVersion)
        cmd = "easy_install %s" % scriptsUrl
        print cmd
        if os.system(cmd):
            raise Exception, "Couldn't install provide scripts for %s %s." % (provisionName, provisionVersion)
#        tmpPath = '.provide-provide-working-temp'
#        if os.path.exists(tmpPath):
#            if os.system('rm -rf %s' % tmpPath):
#                raise Exception, "Can't remove old temporary working folder: %s" % tmpPath
#        if os.system('mkdir %s' % tmpPath):
#            raise Exception, "Can't create temporary working folder: %s" % tmpPath
#        os.chdir(tmpPath)
#        os.system("rm provide-%s-%s.tar.gz" % (provisionName, provisionVersion))
#        scriptsUrl = "http://appropriatesoftware.net/provide/docs/provide-%s-%s.tar.gz" % (
#            provisionName, provisionVersion)
#        if os.system("wget %s" % scriptsUrl):
#           raise Exception, "Couldn't download scripts release." 
#        if os.system("tar zxvf provide-%s-%s.tar.gz" % (provisionName, provisionVersion)):
#           raise Exception, "Couldn't untar downloaded scripts release." 
#        os.chdir("provide-%s-%s" % (provisionName, provisionVersion))
#        try:
#            if os.system("which provide"):
#                raise Exception, "The provide command doesn't appear to be on the path."
#            cmd = "python setup.py install --home=`dirname \`which provide\`/`/.."
#            print cmd
#            if os.system(cmd):
#                raise Exception, "Couldn't run scripts installer."
#        finally:
#            os.chdir("..")
#            os.chdir("..")
#            if os.system("rm -rf %s" % tmpPath):
#                raise Exception, "Couldn't remove temporary working folder: %s" % tmpPath

    def createProvision(self, provisionName, location=''):
        import provide.soleInstance
        registry = provide.soleInstance.application.registry
        if provisionName in registry.provisions:
            raise Exception("That provision already exists.")
        if not provisionName in registry.plugins:
            plugin = registry.plugins.create(provisionName)
        else:
            plugin = registry.plugins[provisionName]
        if not plugin.getSystem():
            plugin.delete()
            raise Exception("The plugin for that provision won't load.")
        try:
            registry.provisions.create(provisionName, location=location)
        except:
            if provisionName in registry.provisions:
                del(registry.provisions[provisionName])
            raise

    def listProvisions(self):
        import provide.soleInstance
        registry = provide.soleInstance.application.registry
        register = registry.provisions
        self.printRegisterNames(register)

    def printRegisterNames(self, register):
        registerNames = [i.name for i in register]
        print "\n".join(registerNames)

    def deleteProvision(self, provisionName):
        import provide.soleInstance
        registry = provide.soleInstance.application.registry
        if provisionName not in registry.provisions:
            raise Exception("That provision doesn't exist.")
        if provisionName not in registry.plugins:
            raise Exception("That provision plugin doesn't exist.")
        provision = registry.provisions[provisionName]
        provision.delete()
        plugin = registry.plugins[provisionName]
        plugin.delete()

    def purgeProvision(self, provisionName):
        import provide.soleInstance
        registry = provide.soleInstance.application.registry
        if provisionName not in registry.provisions.getDeleted():
            raise Exception("That deleted provision doesn't exist.")
        if provisionName not in registry.plugins.getDeleted():
            raise Exception("That deleted provision plugin doesn't exist.")
        provision = registry.provisions.getDeleted()[provisionName]
        provision.purge()
        plugin = registry.plugins.getDeleted()[provisionName]
        plugin.purge()

    def loadPlan(self, provisionName, planName, planPath):
        import provide.soleInstance
        registry = provide.soleInstance.application.registry
        if provisionName not in registry.provisions:
            raise Exception("That provision hasn't been created.")
        else:
            provision = registry.provisions[provisionName]
        if planName in provision.migrationPlans:
            raise Exception("That plan is already loaded.")
        plan = provision.migrationPlans.create(
            planName, location=planPath
        )

    def deletePlan(self, provisionName, planName):
        import provide.soleInstance
        registry = provide.soleInstance.application.registry
        if not provisionName in registry.provisions:
            raise Exception("That provision hasn't been created.")
        provision = registry.provisions[provisionName]
        if not planName in provision.migrationPlans:
            raise Exception("That plan hasn't been loaded.")
        plan = provision.migrationPlans[planName]
        plan.delete()

    def loadApplication(self, provisionName, applicationName, location=''):
        import provide.soleInstance
        registry = provide.soleInstance.application.registry
        if provisionName not in registry.provisions:
            raise Exception("That provision isn't established.")
        provision = registry.provisions[provisionName]
        if applicationName in provision.applications:
            raise Exception("That application is already loaded.")
        application = provision.applications.create(
            applicationName, location=location
        )

    def listApplications(self, provisionName):
        import provide.soleInstance
        registry = provide.soleInstance.application.registry
        if provisionName not in registry.provisions:
            raise Exception("That provision hasn't been created.")
        else:
            provision = registry.provisions[provisionName]
        register = provision.applications
        self.printRegisterNames(register)

    def deleteApplication(self, provisionName, applicationName):
        import provide.soleInstance
        registry = provide.soleInstance.application.registry
        if not provisionName in registry.provisions:
            raise Exception("That provision hasn't been created.")
        provision = registry.provisions[provisionName]
        if not applicationName in provision.applications:
            raise Exception("That application hasn't been loaded.")
        application = provision.applications[applicationName]
        application.delete()

    def purgeApplication(self, provisionName, applicationName):
        import provide.soleInstance
        registry = provide.soleInstance.application.registry
        if not provisionName in registry.provisions.getAll():
            raise Exception("That provision hasn't been created.")
        provision = registry.provisions.getAll()[provisionName]
        if not applicationName in provision.applications.getDeleted():
            raise Exception("That application isn't deleted.")
        application = provision.applications.getDeleted()[applicationName]
        application.purge()

    def loadDependency(self, provisionName, applicationName, dependencyName, dependencyVersion, dependencyPath):
        import provide.soleInstance
        registry = provide.soleInstance.application.registry
        if provisionName not in registry.provisions:
            raise Exception("That provision hasn't been created.")
        else:
            provision = registry.provisions[provisionName]
        if applicationName not in provision.applications:
            raise Exception("That application isn't already loaded.")
        application = provision.applications[applicationName]

        if not dependencyPath:
            if not (dependencyName and dependencyVersion):
                msg = "Can't infer dependency download path without both dependency name and version."
                raise Exception(msg)
            elif not provision.location:
                msg = "Can't infer dependency download path without a provision location."
                raise Exception(msg)
            else:
                baseLocation = provision.location
                fileName = "%s-%s.tar.gz" % (dependencyName, dependencyVersion)
                dependencyPath = "%s%s" % (baseLocation, fileName)

        if not dependencyName:
            fileName = dependencyPath.split('/')[-1]
            dependencyName = fileName.split('-')[0]
            if not dependencyName:
                dependencyName = fileName
        if not dependencyName:
            msg = "Can't infer dependency name, somehow."
            raise Exception(msg)

        if dependencyName in application.dependencies:
            raise Exception("That dependency is already loaded.")
        dependency = application.dependencies.create(
            dependencyName, location=dependencyPath
        )

    def deleteDependency(self, provisionName, applicationName, dependencyName):
        import provide.soleInstance
        registry = provide.soleInstance.application.registry
        if provisionName not in registry.provisions:
            raise Exception("That provision hasn't been created.")
        else:
            provision = registry.provisions[provisionName]
        if applicationName not in provision.applications:
            raise Exception("That application isn't already loaded.")
        application = provision.applications[applicationName]
        if dependencyName not in application.dependencies:
            raise Exception("That dependency isn't already loaded.")
        dependency = application.dependencies[dependencyName]
        dependency.delete()

    def createLink(self, usedProvisionName, usedApplicationName, usedServiceName,
            usingProvisionName, usingApplicationName):
        import provide.soleInstance
        registry = provide.soleInstance.application.registry
        if not usedProvisionName in registry.provisions:
            raise Exception("Used provision hasn't been created.")
        if not usingProvisionName in registry.provisions:
            raise Exception("Using provision hasn't been created.")
        usedProvision = registry.provisions[usedProvisionName]
        usingProvision = registry.provisions[usingProvisionName]
        if not usedApplicationName in usedProvision.applications:
            raise Exception("Used application hasn't been loaded.")
        if not usingApplicationName in usingProvision.applications:
            raise Exception("Using application hasn't been loaded.")
        usedApplication = usedProvision.applications[usedApplicationName]
        usingApplication = usingProvision.applications[usingApplicationName]
        if not usedServiceName in usedApplication.services:
            raise Exception("Used service hasn't been created.")
        usedService = usedApplication.services[usedServiceName]
        if usedService in usingApplication.links:
            raise Exception("That service has already been linked with that application.")
        usingApplication.links.create(usedService)

    def deleteLink(self, usedProvisionName, usedApplicationName, usedServiceName,
            usingProvisionName, usingApplicationName):
        import provide.soleInstance
        registry = provide.soleInstance.application.registry
        if not usedProvisionName in registry.provisions:
            raise Exception("Used provision hasn't been created.")
        if not usingProvisionName in registry.provisions:
            raise Exception("Using provision hasn't been created.")
        usedProvision = registry.provisions[usedProvisionName]
        usingProvision = registry.provisions[usingProvisionName]
        if not usedApplicationName in usedProvision.applications:
            raise Exception("Used application hasn't been loaded.")
        if not usingApplicationName in usingProvision.applications:
            raise Exception("Using application hasn't been loaded.")
        usedApplication = usedProvision.applications[usedApplicationName]
        usingApplication = usingProvision.applications[usingApplicationName]
        if not usedServiceName in usedApplication.services:
            raise Exception("Used service hasn't been created.")
        usedService = usedApplication.services[usedServiceName]
        if not usedService in usingApplication.links:
            raise Exception("That service hasn't been lined with that application.")
        del(usingApplication.links[usedService])

    def createService(self, provisionName, applicationName, serviceName):
        import provide.soleInstance
        registry = provide.soleInstance.application.registry
        if not provisionName in registry.provisions:
            raise Exception("That provision hasn't been created.")
        provision = registry.provisions[provisionName]
        if not applicationName in provision.applications:
            raise Exception("That application hasn't been loaded.")
        application = provision.applications[applicationName]
        if serviceName in application.services:
            raise Exception("That service already exists.")
        application.services.create(serviceName)

    def writePath(self, provisionName, applicationName, serviceName):
        import provide.soleInstance
        registry = provide.soleInstance.application.registry
        if not provisionName in registry.provisions:
            raise Exception("That provision hasn't been created.")
        provision = registry.provisions[provisionName]
        if not applicationName in provision.applications:
            raise Exception("That application hasn't been loaded.")
        application = provision.applications[applicationName]
        if serviceName not in application.services:
            raise Exception("That service doesn't exist.")
        service = application.services[serviceName]
        plugin = service.application.provision.getPluginSystem()
        path = plugin.makeInstallPath(service)
        sys.stdout.write(path)

    def listServices(self, provisionName, applicationName):
        import provide.soleInstance
        registry = provide.soleInstance.application.registry
        if not provisionName in registry.provisions:
            raise Exception("That provision hasn't been created.")
        provision = registry.provisions[provisionName]
        if not applicationName in provision.applications:
            raise Exception("That application hasn't been loaded.")
        application = provision.applications[applicationName]
        register = application.services
        self.printRegisterNames(register)

    def editServiceConfig(self, provisionName, applicationName, serviceName):
        import provide.soleInstance
        registry = provide.soleInstance.application.registry
        if provisionName not in registry.provisions:
            raise Exception("That provision hasn't been created.")
        provision = registry.provisions[provisionName]
        if applicationName not in provision.applications:
            raise Exception("That application hasn't been loaded.")
        application = provision.applications[applicationName]
        if serviceName not in application.services:
            raise Exception("That service doesn't exist.")
        service = application.services[serviceName]
        service.editConfig()

    def unitTestService(self, provisionName, applicationName, serviceName):
        import provide.soleInstance
        registry = provide.soleInstance.application.registry
        if provisionName not in registry.provisions:
            raise Exception("That provision hasn't been created.")
        provision = registry.provisions[provisionName]
        if applicationName not in provision.applications:
            raise Exception("That application hasn't been loaded.")
        application = provision.applications[applicationName]
        if serviceName not in application.services:
            raise Exception("That service doesn't exist.")
        service = application.services[serviceName]
        service.unitTest()

    def commissionService(self, provisionName, applicationName, serviceName):
        import provide.soleInstance
        registry = provide.soleInstance.application.registry
        if provisionName not in registry.provisions:
            raise Exception("That provision hasn't been created.")
        provision = registry.provisions[provisionName]
        if applicationName not in provision.applications:
            raise Exception("That application hasn't been loaded.")
        application = provision.applications[applicationName]
        if serviceName not in application.services:
            raise Exception("That service doesn't exist.")
        service = application.services[serviceName]
        service.commission()

    def deleteService(self, provisionName, applicationName, serviceName):
        import provide.soleInstance
        registry = provide.soleInstance.application.registry
        if provisionName not in registry.provisions:
            raise Exception("That provision hasn't been created.")
        provision = registry.provisions[provisionName]
        if applicationName not in provision.applications:
            raise Exception("That application hasn't been loaded.")
        application = provision.applications[applicationName]
        if serviceName not in application.services:
            raise Exception("That service doesn't exist.")
        service = application.services[serviceName]
        service.delete()

    def purgeService(self, provisionName, applicationName, serviceName):
        import provide.soleInstance
        registry = provide.soleInstance.application.registry
        if provisionName not in registry.provisions.getAll():
            raise Exception("That provision hasn't been created.")
        provision = registry.provisions.getAll()[provisionName]
        if applicationName not in provision.applications.getAll():
            raise Exception("That application hasn't been loaded.")
        application = provision.applications.getAll()[applicationName]
        if serviceName not in application.services.getDeleted():
            raise Exception("That deleted service doesn't exist.")
        service = application.services.getDeleted()[serviceName]
        service.purge()

    def createPurpose(self, provisionName, purposeName):
        import provide.soleInstance
        registry = provide.soleInstance.application.registry
        if not provisionName in registry.provisions:
            raise Exception("That provision doesn't exist.")
        provision = registry.provisions[provisionName]
        if purposeName in provision.purposes:
            raise Exception("That purpose already exists.")
        provision.purposes.create(purposeName)

    def deletePurpose(self, provisionName, purposeName):
        import provide.soleInstance
        registry = provide.soleInstance.application.registry
        if not provisionName in registry.provisions:
            raise Exception("That provision doesn't exist.")
        provision = registry.provisions[provisionName]
        if not purposeName in provision.purposes:
            raise Exception("That purpose doesn't exist.")
        del(provision.purposes[purposeName])

    def designatePurpose(self, provisionName, applicationName, serviceName, purposeName):
        import provide.soleInstance
        registry = provide.soleInstance.application.registry
        if not provisionName in registry.provisions:
            raise Exception("That provision doesn't exist.")
        provision = registry.provisions[provisionName]
        if not purposeName in provision.purposes:
            raise Exception("That purpose doesn't exist.")
        purpose = provision.purposes[purposeName]
        if not applicationName in provision.applications:
            raise Exception("That application doesn't exist.")
        application = provision.applications[applicationName]
        if not serviceName in application.services:
            raise Exception("That service doesn't exist.")
        service = application.services[serviceName]
        if purpose.service == service:
            raise Exception("Purpose already designates that service.")
        purpose.service = service
        purpose.save()

    def whichPurpose(self, provisionName, purposeName):
        import provide.soleInstance
        registry = provide.soleInstance.application.registry
        if not provisionName in registry.provisions:
            raise Exception("That provision doesn't exist.")
        provision = registry.provisions[provisionName]
        if not purposeName in provision.purposes:
            raise Exception("That purpose doesn't exist.")
        purpose = provision.purposes[purposeName]
        if purpose.service:
            print purpose.service.application.name, purpose.service.name

    def dumpData(self, provisionName, applicationName, serviceName, dumpName):
        import provide.soleInstance
        registry = provide.soleInstance.application.registry
        if provisionName not in registry.provisions:
            raise Exception("That provision hasn't been created.")
        provision = registry.provisions[provisionName]
        if applicationName not in provision.applications:
            raise Exception("That application hasn't been loaded.")
        application = provision.applications[applicationName]
        if serviceName not in application.services:
            raise Exception("That service doesn't exist.")
        service = application.services[serviceName]
        if dumpName in service.dataDumps:
            raise Exception("That dump already exists.")
        service.dataDumps.create(dumpName)

    def loadData(self, provisionName, applicationName, serviceName, dumpName,
            dumpLocation):
        import provide.soleInstance
        registry = provide.soleInstance.application.registry
        if provisionName not in registry.provisions:
            raise Exception("That provision hasn't been created.")
        provision = registry.provisions[provisionName]
        if applicationName not in provision.applications:
            raise Exception("That application hasn't been loaded.")
        application = provision.applications[applicationName]
        if serviceName not in application.services:
            raise Exception("That service doesn't exist.")
        service = application.services[serviceName]
        if dumpName in service.dataDumps:
            raise Exception("That dump already exists.")
        service.dataDumps.create(dumpName, location=dumpLocation)

    def initData(self, provisionName, applicationName, serviceName, dumpName):
        import provide.soleInstance
        registry = provide.soleInstance.application.registry
        if provisionName not in registry.provisions:
            raise Exception("That provision hasn't been created.")
        provision = registry.provisions[provisionName]
        if applicationName not in provision.applications:
            raise Exception("That application hasn't been loaded.")
        application = provision.applications[applicationName]
        if serviceName not in application.services:
            raise Exception("That service doesn't exist.")
        service = application.services[serviceName]
        if dumpName not in service.dataDumps:
            raise Exception("That dump doesn't exist.")
        dataDump = service.dataDumps[dumpName]
        dataDump.commissionService()

    def moveData(self, provisionName, fromApplicationName, fromServiceName,
            fromDumpName, toApplicationName, toServiceName, toDumpName):
        import provide.soleInstance
        registry = provide.soleInstance.application.registry
        if provisionName not in registry.provisions:
            raise Exception("That provision hasn't been created.")
        provision = registry.provisions[provisionName]
        planName = "%s-%s" % (fromApplicationName, toApplicationName)
        if planName not in provision.migrationPlans:
            raise Exception("That plan '%s' hasn't been loaded." % planName)
        migrationPlan = provision.migrationPlans[planName]
        if fromApplicationName not in provision.applications:
            raise Exception("That source application hasn't been loaded.")
        fromApplication = provision.applications[fromApplicationName]
        if fromServiceName not in fromApplication.services:
            raise Exception("That source service doesn't exist.")
        fromService = fromApplication.services[fromServiceName]
        if fromDumpName not in fromService.dataDumps:
            raise Exception("That source dump doesn't exist.")
        fromDump = fromService.dataDumps[fromDumpName]
        if toApplicationName not in provision.applications:
            raise Exception("That destination application hasn't been loaded.")
        toApplication = provision.applications[toApplicationName]
        if toServiceName not in toApplication.services:
            raise Exception("That destination service doesn't exist.")
        toService = toApplication.services[toServiceName]
        if toDumpName in toService.dataDumps:
            raise Exception("That destination dump already exists.")
        toService.dataDumps.create(
            toDumpName, sourceDump=fromDump, migrationPlan=migrationPlan
        )


    def deleteData(self,provisionName,applicationName,serviceName,dumpName):
        import provide.soleInstance
        registry = provide.soleInstance.application.registry
        if provisionName not in registry.provisions:
            raise Exception("That provision hasn't been created.")
        provision = registry.provisions[provisionName]
        if applicationName not in provision.applications:
            raise Exception("That application hasn't been loaded.")
        application = provision.applications[applicationName]
        if serviceName not in application.services:
            raise Exception("That service doesn't exist.")
        service = application.services[serviceName]
        if dumpName not in service.dataDumps:
            raise Exception("That dump doesn't exist.")
        dataDump = service.dataDumps[dumpName]
        dataDump.delete()


class UtilityRunner(dm.cli.admin.UtilityRunner):

    systemName = 'provide'
    servicePathEnvironVariableName = 'PROVIDEHOME'
    utilityClass = AdministrationUtility
    usage  = """Usage: %prog [options] [command]

Administer an Provide service, including its domain objects. 

Can be run in three modes:
   1. single command: run the command provided and exit (Default)
   2. interactive (use the "--interactive" option)
   3. scripted commands, either write a file of commands and run it with
      provide --script path, or write a file of commands, put the shebang
      #!/usr/bin/env provide at the top, and make it executable.

To obtain information about the commands available run the "help" command.

Domain objects (e.g. persons, projects, etc) are administered by starting
a python shell from within interactive mode. Run "help shell" for more details.

"""

    def isScriptRequest(self):
        if super(UtilityRunner, self).isScriptRequest():
            return True
        if len(self.args) == 1 and os.path.exists(self.args[0]):
            return True
        return False

    def runScript(self):
        from provide.script import ProvideScript
        if self.args:
            scriptPath = self.args[0]
            scriptFile = open(scriptPath, 'r')
            statements = scriptFile.readlines()
        else:
            statements = sys.stdin.readlines()
        ProvideScript(statements)



