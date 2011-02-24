import os
import sys
from dm.exceptions import DataMigrationError
from dm.ioc import RequiredFeature
from dm.plugin.base import PluginBase
from dm.configwriter import ConfigWriter
from provide.dom.builder import Provision
from provide.dictionarywords import DOMAIN_NAME, SYSTEM_NAME
from provide.dictionarywords import DB_NAME, DB_TYPE, DB_USER, DB_PASS, DB_SUPER_USER, DB_SUPER_PASS 
from provide.dictionarywords import PROVISIONS_DIR_PATH
from provide.dictionarywords import TIMEZONE
from dm.migrate import DomainModelMigrator
from time import sleep
import simplejson
import re
import commands
import random
import string

# todo: Automatically distinguish purpose locations either with domain name, uri prefix, or both.
# todo: Know whether we are running in dual-mode or not, so we need to chmod for group, or not.
# todo: Use commands.getstatusoutput() instead of os.system(), a la:
#    status, output = commands.getstatusoutput(cmd)
#    if status:
#        msg = 'Creation of trac project environment failed'
#        msg += '(cmd was: %s) (output was: %s)' % (cmd, output)


class PluginBase(PluginBase):

    isVerbose = '-v' in sys.argv or '--verbose' in sys.argv
    fs = RequiredFeature('FileSystem')

    # Methods to handle model change events.
    def onProvisionCreate(self, provision):
        if self.isNativeProvision(provision):
            self.doProvisionCreate(provision)

    def onProvisionDelete(self, provision):
        if self.isNativeProvision(provision):
            self.doProvisionDelete(provision)

    def onApplicationCreate(self, application):
        if self.isNativeProvision(application.provision):
            self.doApplicationCreate(application)

    def onApplicationDelete(self, application):
        if self.isNativeProvision(application.provision):
            self.doApplicationDelete(application)

    def onDependencyCreate(self, dependency):
        if self.isNativeProvision(dependency.application.provision):
            self.doDependencyCreate(dependency)

    def onServiceCreate(self, service):
        if self.isNativeProvision(service.application.provision):
            self.doServiceCreate(service)

    def onServiceDelete(self, service):
        if self.isNativeProvision(service.application.provision):
            self.doServiceDelete(service)

    def onMigrationPlanCreate(self, migrationPlan):
        if self.isNativeProvision(migrationPlan.provision):
            self.doMigrationPlanCreate(migrationPlan)

    def onPurposeCreate(self, purpose):
        if self.isNativeProvision(purpose.provision):
            self.doPurposeCreate(purpose)

    def onPurposeUpdate(self, purpose):
        if self.isNativeProvision(purpose.provision):
            self.doPurposeUpdate(purpose)

    def onServiceEditConfig(self, service):
        if self.isNativeProvision(service.application.provision):
            self.doServiceEditConfig(service)

    def onServiceUnitTest(self, service):
        if self.isNativeProvision(service.application.provision):
            self.doServiceUnitTest(service)

    def onServiceCommission(self, service):
        if self.isNativeProvision(service.application.provision):
            self.doServiceCommission(service)

    def onDataDumpCreate(self, dataDump):
        if self.isNativeProvision(dataDump.service.application.provision):
            self.doDataDumpCreate(dataDump)

    def onDataDumpDelete(self, dataDump):
        if self.isNativeProvision(dataDump.service.application.provision):
            self.doDataDumpDelete(dataDump)

    def onDataDumpCommissionService(self, dataDump):
        if self.isNativeProvision(dataDump.service.application.provision):
            self.doDataDumpCommissionService(dataDump)

    def doProvisionCreate(self, provision):
        pass

    def doProvisionDelete(self, provision):
        pass

    def doApplicationCreate(self, application):
        pass

    def doApplicationDelete(self, application):
        pass

    def doDependencyCreate(self, dependency):
        pass

    def doServiceCreate(self, service):
        pass

    def doServiceDelete(self, service):
        pass

    def doMigrationPlanCreate(self, migrationPlan):
        pass

    def doPurposeCreate(self, purpose):
        pass

    def doPurposeUpdate(self, purpose):
        pass

    def doServiceEditConfig(self, service):
        pass

    def doServiceUnitTest(self, service):
        pass

    def doServiceCommission(self, service):
        pass

    def doDataDumpCreate(self, dataDump):
        pass

    def doDataDumpDelete(self, dataDump):
        pass

    def doDataDumpCommissionService(self, dataDump):
        pass


    # Todo: Move this method into the model's service object.
    def getServicePurpose(self, service):
        purposeRegister = service.application.provision.purposes
        if not purposeRegister:
            msg = "Purpose register is completely empty! Service: %s, Application: %s, Provision: %s, Register: %s" % (
                service, service.application, service.application.provision, purposeRegister
            )
            raise Exception(msg)
        serviceName = service.name
        if serviceName in purposeRegister:
            purpose = purposeRegister[serviceName]
        else:
            purpose = None
        return purpose

    # Todo: Move this method into the model's service object.
    def getLinkedService(self, service, provisionName):
        if not provisionName in self.registry.provisions:
            return None
        provision = self.registry.provisions[provisionName]
        for link in service.application.links:
            if link.service.application.provision == provision:
                return link.service
        return None

    # Todo: Extract method as class. This code is repeated in several places.
    def system(self, cmd, msg='run given command'):
        msg = "Unable to %s" % msg
        if self.isVerbose:
            print cmd
            if os.system(cmd):
                self.exit(msg + ".")
        else:
            (s, o) = commands.getstatusoutput(cmd)
            if s:
                print cmd
                if o:
                    msg = "%s: %s" % (msg, o)
                else:
                    msg = "%s (no output)." % (msg)
                self.exit(msg)

    def exit(self, msg, code=1):
        raise Exception, 'Error: %s' % msg

    def fetchFileToDir(self, sourcePath, destPath, altBasename="download.tar.gz"):
        #print "Fetching file to dir: %s %s" % (sourcePath, destPath)
        self.sourcePath = sourcePath
        self.destDirPath = destPath
        self.destFilePath = self.join(
            destPath, os.path.basename(self.sourcePath) or altBasename
        )
        self.fetch()

    def fetchFileToFile(self, sourcePath, destPath):
        self.sourcePath = sourcePath
        self.destDirPath = os.path.dirname(destPath)
        self.destFilePath = destPath
        self.fetch()

    def fetch(self):
        self.fs.validateSourcePath(self.sourcePath)
        self.fs.validateDirPath(self.destDirPath)
        if os.path.exists(self.sourcePath):
            cmd = "cp %s %s" % (
                self.sourcePath, self.destFilePath
            )
        else:
            cmd = "wget %s --tries=45 --output-document=%s %s" % (
                not self.isVerbose and "--quiet" or "",
                self.destFilePath, self.sourcePath
            )
        msg = "download source from: %s" % self.sourcePath
        self.system(cmd, msg)

    def hasProvision(self, provision):
        if not self.isNativeProvision(provision):
            return False
        if not self.fs.provisionDirExists(provision):
            return False
        return True

    def purposeDirExists(self, purpose):
        purposePath = self.fs.makePurposePath(purpose)
        return os.path.exists(purposePath)
        
    def applicationDirExists(self, application):
        applicationPath = self.fs.makeApplicationPath(application)
        return os.path.exists(applicationPath)
        
    def hasApplication(self, application):
        if not self.isNativeProvision(application.provision):
            return False
        if not self.applicationDirExists(application):
            return False
        return True

    def serviceDirExists(self, service):
        servicePath = self.fs.makeServicePath(service)
        return os.path.exists(servicePath)

    def hasService(self, service):
        if not self.isNativeProvision(service.application.provision):
            return False
        if not self.serviceDirExists(service):
            return False
        return True

    def isNativeProvision(self, provision):
        if not issubclass(provision.__class__, Provision):
            raise Exception("Not a Provision object: %s" % provision)
        return provision.name == self.domainObject.name
    
    ## Methods to install from tarball.

    def runInstaller(self, tarballPath, installPath):
        self.runPythonInstaller(tarballPath, installPath)

    def runPythonInstaller(self, tarballPath, installPath):
        if not os.path.exists(tarballPath):
            raise Exception("Tarball path doesn't exist: %s" % tarballPath)
        if not os.path.exists(installPath):
            raise Exception("Install path doesn't exist: %s" % installPath)

        # change to dir containing source archive
        sourceDirPath = os.path.dirname(tarballPath)
        if not os.path.exists(sourceDirPath):
            raise Exception("Source path has no dir: %s" % tarballPath)
        print "Changing dir to: %s" % sourceDirPath
        self.fs.chdir(sourceDirPath)
        # extract archive
        cmd = 'tar zxvf %s' % tarballPath
        msg = "extract archive: %s" % tarballPath
        self.system(cmd, msg)
        # change to unpacked archive root
        unpackedDirPath = self.join(
            sourceDirPath,
            os.path.basename(tarballPath)[:-7]
        )
        self.fs.chdir(unpackedDirPath)
        # run installer
        cmd = self.getPythonInstallCmdLine(installPath=installPath)
        self.system(cmd, "run installer: %s" % cmd)
        self.fs.chdir(sourceDirPath)
        # remove extracted archive
        self.fs.remove(unpackedDirPath, "unpacked source archive")

    def getPythonInstallCmdLine(self, installPath=''):
        cmd = self.getPythonInstallCmdLineBase()
        if installPath:
            cmd += " --home=%s" % installPath
        return cmd
        
    def getPythonInstallCmdLineBase(self):
        return "python %s install" % self.getPythonSetupFilename()

    def getPythonSetupFilename(self):
        return "setup.py"

    ## Method to run the application's script runner program.

    def runScriptRunnerScript(self, scriptPath, commandString, stdoutPath="",
            stdinPath=""):
        cmd = '%s "%s"' % (scriptPath, commandString)
        if stdinPath:
            cmd += ' < %s' % stdinPath
        if stdoutPath:
            cmd += ' > %s' % stdoutPath
        print cmd
        return os.system(cmd)
        if self.isVerbose:
            return os.system(cmd)
        else:
            return commands.getstatus(cmd)


    ## Methods to manipulate config files.

    def rewriteConfigFile(self, service, updateLines):
        configPath = self.fs.makeConfigPath(service)
        configWriter = ConfigWriter()
        print "Updating config file %s with:" % configPath
        print "\n".join(updateLines)
        configWriter.updateFile(configPath, updateLines)

    def writeNewConfigFile(self, service, configContent):
        configPath = self.fs.makeConfigPath(service)
        configFile = open(configPath, 'w')
        configFile.write(configContent)
        configFile.close()

    def checkConfigFileExists(self, service):
        configPath = self.fs.makeConfigPath(service)
        if not os.path.exists(configPath):
            msg = "Config file not found on: %s" % configPath
            raise Exception(msg)
    
    def substituteConfig(self, service, placeHolder, realValue):
        print "Substituting '%s' for '%s'." % (realValue, placeHolder)
        configPath = self.fs.makeConfigPath(service)
        configFile = open(configPath, 'r')
        configContentIn = configFile.readlines()
        configFile.close()
        configContentOut = []
        # todo: Check that one and only one change is made.
        for inLine in configContentIn:
            outLine = re.sub(placeHolder, realValue, inLine)
            configContentOut.append(outLine)
        configFile = open(configPath, 'w')
        configFile.writelines(configContentOut)
        configFile.close()

    def join(self, *args, **kwds):
        return self.fs.join(*args, **kwds)


class ProvisionPlugin(PluginBase):

    purposeLocator = RequiredFeature('PurposeLocator')
    tarballBaseName = ''

    def doProvisionCreate(self, provision):
        self.checkPluginDependencies()
        self.createProvision(provision)

    def doProvisionDelete(self, provision):
        self.deleteProvision(provision)

    def doApplicationCreate(self, application):
        self.createApplication(application)

    def doApplicationDelete(self, application):
        self.deleteApplication(application)

    def doDependencyCreate(self, dependency):
        self.createDependency(dependency)

    def doServiceCreate(self, service):
        self.assertServicePurpose(service)
        self.createService(service)

    def doServiceDelete(self, service):
        self.deleteService(service)


    def checkPluginDependencies(self):
        pass 

    def createProvision(self, provision):
        if not self.fs.provisionDirExists(provision):
            self.fs.createProvisionDirs(provision)

    def deleteProvision(self, provision):
        if self.fs.provisionDirExists(provision):
            self.deleteProvisionDirs(provision)

    def deleteProvisionDirs(self, provision):
        self.fs.chdirProvisions()
        provisionPath = self.fs.makeProvisionPath(provision)
        self.fs.remove(provisionPath, "provision folder")

    def createApplication(self, application):
        if not self.applicationDirExists(application):
            self.fs.createApplicationDirs(application)
        self.acquireApplication(application)

    def acquireApplication(self, application):
        sourcePath = self.makeApplicationDownloadUrl(application)
        destPath = self.fs.makeApplicationPath(application)
        try:
            self.fetchFileToDir(sourcePath, destPath)
        except:
            application.delete()
            raise

    def makeApplicationDownloadUrl(self, application):
        "URL for downloading application tarball."
        if application.location and 'using ' not in application.location:
            return application.location
        elif application.provision.location:
            baseLocation = application.provision.location
            if baseLocation[-1] != '/':
                baseLocation += '/'
            fileName = self.fs.makeTarballName(
                self.tarballBaseName or application.provision.name, application.name
            )
            return "%s%s" % (baseLocation, fileName)
        else:
            msg = "Neither application nor provision has a location."
            raise Exception(msg)

    def deleteApplication(self, application):
        if self.applicationDirExists(application):
            self.deleteApplicationDirs(application)
        else:
            print "Application folder not found."

    def deleteApplicationDirs(self, application):
        self.fs.chdirProvisions()
        applicationPath = self.fs.makeApplicationPath(application)
        self.fs.remove(applicationPath, "application folder")

    def createDependency(self, dependency):
        destPath = self.fs.makeDependenciesPath(dependency)
        sourcePath = dependency.location
        try:
            self.fetchFileToDir(sourcePath, destPath, "%s.tar.gz" % dependency.name)
        except:
            dependency.delete()
            raise

    def assertServicePurpose(self, service):
        if not self.getServicePurpose(service):
            msg = "Can't find service name '%s' in provisions purposes: %s" % (
                service.name,
                 ', '.join(service.application.provision.purposes.keys())
            )
            raise Exception(msg)

    def createService(self, service):
        if not self.serviceDirExists(service):
            service.isFsCreated = True
            service.save()
            self.fs.createServiceDirs(service)
            self.setupService(service)
        else:
            print "Warning: Service folder already exists."

    def setupService(self, service):
        tarballPath = self.fs.makeApplicationTarballPath(service.application)
        self.runInstaller(tarballPath, installPath)

    def deleteService(self, service):
        if service.isDbCreated:
            self.deleteServiceDatabase(service)
            service.isDbCreated = False
            service.save()
        if service.isFsCreated:
            self.deleteServiceDirs(service)
            service.isFsCreated = False
            service.save()

    def deleteServiceDirs(self, service):
        self.fs.chdirProvisions()
        servicePath = self.fs.makeServicePath(service)
        self.fs.remove(servicePath, "service folder")
        
    def deleteServiceDatabase(self, service):
        self.runServiceDbDelete(service)
        
    def runServiceDbDelete(self, service):
        scriptPath = self.fs.makeScriptRunnerPath(service)
        scriptDirPath = os.path.dirname(scriptPath)
        self.fs.chdir(scriptDirPath)
        commandString = self.getDbDeleteCmdLine(service)
        if self.runScriptRunnerScript(scriptPath, commandString):
            raise Exception("Wasn't able to delete the database.")

    def getDbDeleteCmdLine(self, service):
        return "%s db delete" % self.fs.makeAdminScriptPath(service)

        
class DomainModelApplicationPlugin(ProvisionPlugin):
    "Supports provision of domainmodel applications."

    def doMigrationPlanCreate(self, migrationPlan):
        self.createMigrationPlan(migrationPlan)

    def doPurposeCreate(self, purpose):
        self.createPurpose(purpose)

    def doPurposeUpdate(self, purpose):
        self.updatePurpose(purpose)

    def doServiceEditConfig(self, service):
        self.editServiceConfig(service)

    def doServiceUnitTest(self, service):
        self.unitTestService(service)

    def doServiceCommission(self, service):
        self.commissionService(service)

    def doDataDumpCreate(self, dataDump):
        self.createDataDump(dataDump)

    def doDataDumpDelete(self, dataDump):
        self.deleteDataDumpDirs(dataDump)

    def doDataDumpCommissionService(self, dataDump):
        self.commissionServiceFromDataDump(dataDump)

    def createMigrationPlan(self, migrationPlan):
        sourcePath = migrationPlan.location
        destPath = self.fs.makeMigrationPlanPath(migrationPlan)
        try:
            self.fetchFileToFile(sourcePath, destPath)
        except:
            migrationPlan.delete()
            raise

    def createPurpose(self, purpose):
        if not self.purposeDirExists(purpose):
            self.fs.createPurposeDirs(purpose)

    def updatePurpose(self, purpose):
        if not purpose.service:
            return
        apacheConfigPath = self.fs.makePurposeApacheConfigPath(purpose)
        print "Writing '%s' purpose Apache config for %s %s: %s" % (
            purpose.name,
            purpose.service.application.name,
            purpose.service.name,
            apacheConfigPath
        )
        apacheConfigContent = self.makePurposeApacheConfigContent(purpose)
        # todo: Write purpose attributes into service config copy.
        apacheConfigFile = open(apacheConfigPath, 'w')
        apacheConfigFile.write(apacheConfigContent)
        apacheConfigFile.close()

    def makePurposeApacheConfigContent(self, purpose):
        nameValues = {}
        nameValues['SERVICE_CONFIG'] = self.fs.makeServiceApacheConfigPath(purpose.service)
        if self.purposeLocator.distinguishesDomains():
            nameValues['DOMAIN_NAME'] = self.purposeLocator.getFQDN(purpose) 
            configFragment = """NameVirtualHost *
<VirtualHost *>
    ServerName %(DOMAIN_NAME)s
    Include %(SERVICE_CONFIG)s
    # Favicon location.
    <Location "/favicon.ico">
      SetHandler None
    </Location>
</VirtualHost>
""" % nameValues
        else:
            configFragment = """Include %(SERVICE_CONFIG)s
""" % nameValues
        return configFragment

    def editServiceConfig(self, service):
        self.presentConfigFileForEditing(service)

    def presentConfigFileForEditing(self, service):
        editorName = 'editor'
        configPath = self.fs.makeConfigPath(service)
        cmd = '%s %s' % (editorName, configPath)
        self.system(cmd, "present file for manual editing")

    def unitTestService(self, service):
        self.runServiceTests(service)
        self.buildApacheConfig(service)

    def runServiceTests(self, service):
        self.setConfigFileForTest(service)
        self.runDbInitScript(service)
        self.runTestScript(service)

    def setConfigFileForTest(self, service):
        self.rewriteConfigFile(service, [
            '[DEFAULT]',
            'system_mode = development'
        ])

    def runDbInitScript(self, service):
        scriptPath = self.fs.makeScriptRunnerPath(service)
        scriptDirPath = os.path.dirname(scriptPath)
        self.fs.chdir(scriptDirPath)
        commandString = self.getDbCreateCmdLine(service)
        if self.runScriptRunnerScript(scriptPath, commandString):
            raise Exception("Wasn't able to create the database.")
        service.isDbCreated = True
        service.save()
        commandString = self.getDbInitCmdLine(service)
        if self.runScriptRunnerScript(scriptPath, commandString):
            raise Exception("Wasn't able to initialise the database.")

    def getDbCreateCmdLine(self, service):
        return "%s db create" % self.fs.makeAdminScriptPath(service)
        
    def getDbInitCmdLine(self, service):
        return "%s db init" % self.fs.makeAdminScriptPath(service)

    def runTestScript(self, service):
        scriptPath = self.fs.makeScriptRunnerPath(service)
        scriptDirPath = os.path.dirname(scriptPath)
        self.fs.chdir(scriptDirPath)
        commandString = self.getUnitTestCmdLine(service)
        if self.runScriptRunnerScript(scriptPath, commandString):
            raise Exception("There were some failing tests.")

    def getUnitTestCmdLine(self, service):
        raise Exception("Method not implemented on %s" % self.__class__)

    def buildApacheConfig(self, service):
        print "Building Apache server config...."
        scriptPath = self.fs.makeScriptRunnerPath(service)
        scriptDirPath = os.path.dirname(scriptPath)
        self.fs.chdir(scriptDirPath)
        commandString = self.getBuildApacheConfigCmdLine(service)
        if self.runScriptRunnerScript(scriptPath, commandString):
            raise Exception("Wasn't able to build Apache server configuration.")

    def commissionService(self, service):
        self.runServiceDbInit(service)
        self.buildApacheConfig(service)

    def runServiceDbInit(self, service):
        print "Building application service database tables...."
        scriptPath = self.fs.makeScriptRunnerPath(service)
        scriptDirPath = os.path.dirname(scriptPath)
        self.fs.chdir(scriptDirPath)
        commandString = self.getDbCreateCmdLine(service)
        if self.runScriptRunnerScript(scriptPath, commandString):
            raise Exception("Wasn't able to create the database.")
        else:
            service.isDbCreated = True
            service.save()
        print "Importing application service domain objects...."
        commandString = self.getDbInitCmdLine(service)
        if self.runScriptRunnerScript(scriptPath, commandString):
            raise Exception("Wasn't able to initialise the database.")

    def createDataDump(self, dataDump):
        self.createDataDumpDirs(dataDump)
        if dataDump.sourceDump:
            self.runDataMigration(dataDump)
        elif dataDump.location:
            self.loadDataDumpSource(dataDump)
        else:
            self.runDataDump(dataDump)

    def createDataDumpDirs(self, dataDump):
        dataDumpPath = self.fs.makeDataDumpPath(dataDump)
        filesDumpDirPath = self.fs.makeFilesDumpDirPath(dataDump)
        self.fs.make(dataDumpPath)
        self.fs.make(filesDumpDirPath)

    def runDataMigration(self, dataDump):
        scriptPath = self.fs.makeScriptRunnerPath(dataDump.service)
        scriptDirPath = os.path.dirname(scriptPath)
        self.fs.chdir(scriptDirPath)
        sourceDumpPath = self.fs.makeDomainModelDumpPath(dataDump.sourceDump)
        sourceDumpFile = open(sourceDumpPath, 'r')
        sourceDumpContent = sourceDumpFile.read()
        dumpedData = simplejson.loads(sourceDumpContent)
        planSteps = self.getMigrationPlanSteps(dataDump)
        # Todo: Push this down to application.
        strategy = DomainModelMigrator(dumpedData, planSteps)
        strategy.migrate()
        destDumpContent = simplejson.dumps(dumpedData)
        destDumpPath = self.fs.makeDomainModelDumpPath(dataDump)
        destDumpFile = open(destDumpPath, 'w')
        destDumpFile.write(destDumpContent)

    def getMigrationPlanSteps(self, dataDump):
        planPath = self.fs.makeMigrationPlanPath(dataDump.migrationPlan)
        planFile = open(planPath, 'r')
        planSteps = []
        for line in planFile.readlines():
            strippedLine = line.strip()
            if strippedLine:
                planSteps.append(strippedLine)
        return planSteps

    def loadDataDumpSource(self, dataDump):
        destPath = self.fs.makeDomainModelDumpPath(dataDump)
        sourcePath = dataDump.location
        try:
            self.fetchFileToFile(sourcePath, destPath)
        except:
            dataDump.delete()
            raise

    def runDataDump(self, dataDump):
        self.runDomainModelDump(dataDump)
        self.runFilesDump(dataDump)

    def runDomainModelDump(self, dataDump):
        scriptPath = self.fs.makeScriptRunnerPath(dataDump.service)
        scriptDirPath = os.path.dirname(scriptPath)
        self.fs.chdir(scriptDirPath)
        dumpFilePath = self.fs.makeDomainModelDumpPath(dataDump)
        commandString = self.getMigrateDataDumpCmdLine(
            dataDump.service, dumpFilePath
        )
        if self.runScriptRunnerScript(scriptPath, commandString):
            raise Exception("Wasn't able to dump the domain model.")

    def getMigrateDataDumpCmdLine(self, service, dumpFilePath):
        adminScriptPath = self.fs.makeAdminScriptPath(service)
        return "%s migratedump %s" % (adminScriptPath, dumpFilePath)

    def runFilesDump(self, dataDump):
        scriptPath = self.fs.makeScriptRunnerPath(dataDump.service)
        scriptDirPath = os.path.dirname(scriptPath)
        self.fs.chdir(scriptDirPath)
        dumpDirPath = self.fs.makeFilesDumpDirPath(dataDump)
        commandString = self.getMigrateFilesDumpCmdLine(
            dataDump.service, dumpDirPath
        )
        if self.runScriptRunnerScript(scriptPath, commandString):
            raise Exception("Wasn't able to dump filesystem files.")

    def deleteDataDump(self, dataDump):
        self.deleteDataDump(dataDump)

    def deleteDataDumpDirs(self, dataDump):
        dataDumpPath = self.fs.makeDataDumpPath(dataDump)
        self.fs.remove(dataDumpPath, "dump folder")

    def commissionServiceFromDataDump(self, dataDump):
        self.runDataInit(dataDump)
        self.buildApacheConfig(dataDump.service)

    def runDataInit(self, dataDump):
        scriptPath = self.fs.makeScriptRunnerPath(dataDump.service)
        scriptDirPath = os.path.dirname(scriptPath)
        self.fs.chdir(scriptDirPath)
        commandString = self.getDbCreateCmdLine(dataDump.service)
        if self.runScriptRunnerScript(scriptPath, commandString):
            raise Exception("Wasn't able to create service database.")
        else:
            dataDump.service.isDbCreated = True
            dataDump.service.save()
        dumpFilePath = self.fs.makeDomainModelDumpPath(dataDump)
        commandString = self.getMigrateDataLoadCmdLine(
            dataDump.service, dumpFilePath
        )
        if self.runScriptRunnerScript(scriptPath, commandString):
            msg = "Wasn't able to initialise database from migration data."
            raise Exception(msg)

    def getMigrateDataLoadCmdLine(self, service, dumpFilePath):
        adminScriptPath = self.fs.makeAdminScriptPath(service)
        return "%s migrateload %s" % (adminScriptPath, dumpFilePath)

    def setupService(self, service):
        # Replacement method.
        libPythonPath = self.fs.makeLibPythonPath(service) # satisfy setuptools
        self.replacePythonPath(libPythonPath)
        # install dependencies (first)
        installPath = self.fs.makeInstallPath(service)
        for dependency in service.application.dependencies:
            dependencyPath = self.fs.makeDependencyPath(dependency)
            if dependencyPath[-7:] == '.tar.gz':
                self.runPythonInstaller(dependencyPath, installPath)
            elif dependencyPath[-4:] == '.egg':
                self.copyInstallEgg(dependencyPath, libPythonPath)
            else:
                raise Exception, "Dependency's downloaded file neither .tar.gz nor .egg: %s" % dependencyPath
        # install application software
        applicationPath = self.fs.makeApplicationPath(service.application)
        tarballPath = self.fs.makeApplicationTarballPath(service.application)
        self.runPythonInstaller(tarballPath, installPath)
        self.fixupPythonEggsForModPython(service)
        self.createPythonPackageLinks(service)
        # setup application instance files (not database)
        self.writeScriptRunnerScript(service)
        self.setTemplates(service)
        self.setConfigFile(service)
        self.generateFilesystemData(service)

    def replacePythonPath(self, newPath):
        os.environ['PYTHONPATH'] = newPath
        print "PYTHONPATH=%s" % os.environ['PYTHONPATH']

    def addPathToPythonPath(self, newPath):
        pythonPath = os.environ['PYTHONPATH']
        pythonPath = "%s:%s" % (pythonPath, newPath)
        os.environ['PYTHONPATH'] = pythonPath
        print "PYTHONPATH=%s" % os.environ['PYTHONPATH']

    def copyInstallEgg(self, tarballPath, libPythonPath):
        if not os.path.exists(tarballPath):
            raise Exception("Tarball path doesn't exist: %s" % tarballPath)
        if not os.path.exists(libPythonPath):
            raise Exception("Path to python library doesn't exist: %s" % libPythonPath)
        cmd = 'cp %s %s' % (tarballPath, libPythonPath)
        msg = "copy downloaded egg to Python library: %s" % tarballPath 
        self.system(cmd, msg)

    def fixupPythonEggsForModPython(self, service):
        # Apache mod_python imports with the imp module.
        print "Hatching setuptools' Python eggs for mod_python...."
        eggCount = 0
        libPythonPath = self.fs.makeLibPythonPath(service)
        self.fs.chdir(libPythonPath)
        for i in os.listdir(libPythonPath):
            if i[-4:] == '.egg':
                eggPath = os.path.join(libPythonPath, i)
                if os.path.isfile(eggPath):
                    print "Hatching zip-shaped Python egg: %s" % i
                    cmd = 'unzip %s' % eggPath
                    msg = "Unable to unzip egg file: %s" % eggPath
                    self.system(cmd, msg)
                    cmd = 'rm -rf %s' % (
                        os.path.join(libPythonPath, 'EGG-INFO')
                    )
                    self.system(cmd, "remove EGG-INFO folder")
                    eggCount += 1
                elif os.path.isdir(eggPath):
                    print "Hatching folder-shaped Python egg: %s" % i
                    for j in os.listdir(eggPath):
                        if j == 'EGG-INFO':
                            continue
                        packagePath = os.path.join(eggPath, j)
                        #cmd = 'ln -s %s %s' % (
                        #    packagePath, libPythonPath
                        #)
                        #msg = "Unable to symlink egg dir: %s" % packagePath
                        #self.system(cmd, msg)
                        
                        targetPath = os.path.join(libPythonPath, j)
                        if not os.path.exists(targetPath):
                            cmd = 'mkdir %s' % targetPath
                            msg = "Unable to make egg dir: %s" % packagePath
                            self.system(cmd, msg)
                        for nodeName in os.listdir(packagePath):
                            if not os.path.exists(os.path.join(targetPath, nodeName)):
                                cmd = 'ln -s %s %s' % (os.path.join(packagePath, nodeName), targetPath)
                                msg = "Unable to link egg stuff: %s %s %s" % (nodeName, packagePath, targetPath)
                                self.system(cmd, msg)
                        eggCount += 1
        print "Hatched %d egg(s) in support of mod_python's imp usage." % (
            eggCount
        )

    def createPythonPackageLinks(self, service):
        pass
        
    def writeScriptRunnerScript(self, service):
        print "Writing scriptrunner...."
        scriptRunnerPath = self.fs.makeScriptRunnerPath(service)
        print scriptRunnerPath
        try:
            file = open(scriptRunnerPath, 'w')
        except IOError, inst:
            raise Exception("Couln't write scriptrunner: %s" % inst)
        
        djangoSettingsModuleName = self.getDjangoSettingsModuleName()
        file.write('#!/usr/bin/env sh\n')
        file.write('export DJANGO_SETTINGS_MODULE=%s\n' % (
                djangoSettingsModuleName
            )
        )
        file.write('export PYTHONPATH=%s\n' % self.fs.makeLibPythonPath(service))
        serviceSettingsEnvvarName = self.getServiceSettingsEnvvarName()
        installPath = self.fs.makeInstallPath(service)
        configPath = self.fs.makeConfigPath(service)
        file.write('export %s=%s\n' % ( serviceSettingsEnvvarName, configPath))
        file.write('$1\n')
        file.close()
        cmd = 'chmod +x %s' % scriptRunnerPath
        msg = "set execute permission on script runner: %s" % scriptRunnerPath
        self.system(cmd, msg)

    def getDjangoSettingsModuleName(self):
        return '%s.django.settings.main' % self.domainObject.name
    
    def getServiceSettingsEnvvarName(self):
        return '%s_SETTINGS' % self.domainObject.name.upper()
    
    def setTemplates(self, service):
        pass

    def setConfigFile(self, service):
        print "Setting up application service config file...."
        self.generateNewConfigFile(service)
        self.checkConfigFileExists(service)
        print "Updating config file values...."
        updateLines = self.getUpdateLines(service)
        self.rewriteConfigFile(service, updateLines)

    def generateNewConfigFile(self, service):
        self.copyExampleConfig(service)

    def copyExampleConfig(self, service):
        configContent = self.readExampleConfigFile(service)
        self.writeNewConfigFile(service, configContent)

    def readExampleConfigFile(self, service):
        examplePath = self.fs.makeExampleConfigPath(service)
        if not os.path.exists(examplePath):
            msg = "Example config file not found on: %s" % examplePath
            raise Exception(msg)
        exampleFile = open(examplePath, 'r')
        configContent = exampleFile.read()
        exampleFile.close()
        return configContent

    def getUpdateLines(self, service):
        lines = []
        lines.append('[DEFAULT]')
        lines.append('domain_name = %s' % self.makeDomainName(service))
        lines += self.getUpdateLinesDefault(service)
        lines.append('[db]')
        lines.append('name = %s' % self.makeDbName(service))
        lines.append('user = %s' % self.makeDbUser(service))
        lines.append('pass = %s' % self.makeDbPass(service))
        lines.append('[logging]')
        lines.append('log_file = %s' % self.fs.makeLogFilePath(service))
        lines.append('[www]')
        lines.append('apache_config_file = %s' % self.makeApacheConfigPath(service))
        lines.append('media_root = %s' % self.makeMediaRoot(service))
        lines.append('uri_prefix = %s' % self.makeUriPrefix(service))
        lines.append('media_prefix = %s' % self.makeMediaPrefix(service))
        lines.append('[django]')
        lines.append('templates_dir = %s' % self.fs.makeTemplatesPath(service))
        #lines.append('secret_key = %s' % self.makeSecretKey())
        return lines

    #def makeSecretKey(self, keyLength=60):
    #    characterList = string.letters + string.digits
    #    secretKey = ''
    #    for i in range(keyLength):
    #        secretKey += random.choice(characterList)
    #    return secretKey

    def makeDomainName(self, service):
        purpose = self.getServicePurpose(service)
        return self.purposeLocator.getFQDN(purpose)

    def getUpdateLinesDefault(self, service):
        return []

    #def makeObjectImagesPath(self, service):
    #    return os.path.join(self.makeInstallPath(service), 'var', 'images')

    def makeDbType(self, *args):
        return self.dictionary[DB_TYPE]
        
    def makeDbName(self, service):
        dbName = '%s-%s-%s-%s' % (
            self.dictionary[DB_NAME],
            service.application.provision.name,
            service.application.name,
            service.name,
        )
        if self.makeDbType(service) == 'mysql':
            dbName = dbName.replace('-','_').replace('.','_')
        return dbName
        
    def makeDbUser(self, *args):
        return self.dictionary[DB_USER]
        
    def makeDbPass(self, *args):
        return self.dictionary[DB_PASS]
        
    def makeDbSuperUser(self, *args):
        return self.dictionary[DB_SUPER_USER]
        
    def makeDbSuperPass(self, *args):
        return self.dictionary[DB_SUPER_PASS]
        
    def makeApacheConfigPath(self, service):
        installPath = self.fs.makeInstallPath(service)
        return os.path.join(installPath, 'etc', 'httpd.conf')

    def makeMediaRoot(self, service):
        return os.path.join(self.fs.makeInstallPath(service), 'media')

    def makeUriPrefix(self, service):
        purpose = self.getServicePurpose(service)
        return self.purposeLocator.getPath(purpose)

    def makeMediaPrefix(self, service):
        uriPrefix = self.makeUriPrefix(service)
        if uriPrefix:
            mediaPrefix = uriPrefix + 'media'
        else:
            mediaPrefix = '/' + service.application.provision.name + 'media'
        return mediaPrefix

    def generateFilesystemData(self, service):
        pass

    def getBuildApacheConfigCmdLine(self, service):
        return "%s www build" % self.fs.makeAdminScriptPath(service)
        
    def getMigrateFilesDumpCmdLine(self, service, dumpDirPath):
        adminScriptPath = self.fs.makeAdminScriptPath(service)
        return "%s migratedumpfiles %s" % (adminScriptPath, dumpDirPath)

    def getUnitTestCmdLine(self, service):
        return self.fs.makeTestScriptPath(service)


class VirtualenvDomainModelApplicationPlugin(DomainModelApplicationPlugin):

    installerScriptUrl = None
    installerScriptPath = None
    makeconfigScriptPath = None
    testScriptPath = None
    configEnvvarName = None
    isEgenixDateTimeRequired = False

    def acquireApplication(self, application):
        if self.installerScriptUrl:
            if not self.installerScriptPath:
                msg = "Missing installerScriptPath on class: %s" % self.__class__
                raise Exception, msg
            self.acquireApplicationWithInstaller(application)
        else:
            self.acquireApplicationWithoutInstaller(application)

    def acquireApplicationWithInstaller(self, application):
        applicationPath = self.fs.makeApplicationPath(application)
        # Download installer.
        self.fetchFileToDir(self.installerScriptUrl, applicationPath)
        self.fs.chdir(applicationPath)
        cmd = 'chmod +x %s' % self.installerScriptPath
        self.system(cmd, 'make %s installer executable' % application.provision.name)
        # Assemble installer command options.
        cmd = '%s -v ' % self.installerScriptPath
        # Specify specially requested system.
        sourceUrl = self.makeApplicationDownloadUrl(application)
        cmd += ' --install-requirement-or-url=%s' % sourceUrl
        # Specify specially requested dependencies.
        if 'using ' in application.location:
            requirementOrUrl = application.location.split(' ', 1)[1]
            cmd += ' --extra-requirement-or-url="%s"' % requirementOrUrl
        # Pass in the database type, it's used to install database drivers.
        dbType = self.makeDbType()
        if dbType == 'sqlite':
            pass # Assume SQLite.
        elif dbType in ['mysql', 'postgres']:
            cmd += ' --db-type=%s' % dbType
        else:
            raise Exception, "Db type '%s' not supported." % dbType
        # Only install, don't make a service.
        cmd += ' --skip-service-setup'
        # Install to 'virtualenv' path.
        vePath = self.fs.makeVePath(application)
        cmd += ' %s' % vePath
        self.system(cmd, 'run the %s installer' % application.provision.name)

    def acquireApplicationWithoutInstaller(self, application):
        self.system('easy_install virtualenv', 'install virtualenv')
        # Create 'virtualenv' environment.
        vePath = self.fs.makeVePath(application)
        cmd = "virtualenv --no-site-packages %s" % vePath
        self.system(cmd, 'create a virtualenv')
        # Prepare virtualenv for domainmodel.
        if self.isEgenixDateTimeRequired:
            self.installEgenixDateTime(application)
        self.installMarkdown(application)
        # Install application to 'virtualenv' path.
        veBinPath = self.fs.makeVeBinPath(application)
        self.fs.chdir(veBinPath)
        sourceUrl = self.makeApplicationDownloadUrl(application)
        cmd = './easy_install %s' % sourceUrl
        self.system(cmd, 'install %s to virtualenv' % application.provision.name)

    def installEgenixDateTime(self, application, egenixVersion = '3.1.3'):
        print "Attempting to install egenix-mx-base %s from source..." % egenixVersion
        egenixDownloadUrl = 'http://downloads.egenix.com/python/egenix-mx-base-%s.tar.gz' % egenixVersion
        egenixArchivePath = 'egenix-mx-base-%s.tar.gz' % egenixVersion
        egenixSourcePath = 'egenix-mx-base-%s' % egenixVersion
        print "Downloading %s" % egenixDownloadUrl
        cmd = 'wget %s -O %s' % (egenixDownloadUrl, egenixArchivePath)
        self.system(cmd, 'download egenix-mx-datetime')
        print "Extracting %s" % egenixArchivePath
        cmd = 'tar zxvf %s' % egenixArchivePath
        self.system(cmd, 'extract egenix-mx-datetime')
        veBinPath = self.fs.makeVeBinPath(application)
        pythonBinPath = self.fs.join(veBinPath, 'python')
        print "Installing %s" % egenixSourcePath
        cmd = 'cd %s; %s setup.py install' % (egenixSourcePath, pythonBinPath)
        self.system(cmd, 'install egenix-mx-datetime')
        self.fs.remove(egenixArchivePath, 'egenix archive path')
        self.fs.remove(egenixSourcePath, 'egenix source path')

    def installMarkdown(self, application, markdownVersion = '2.0.3'):
        print "Attempting to install markdown %s from source..." % markdownVersion
        markdownDownloadUrl = 'http://pypi.python.org/packages/source/M/Markdown/Markdown-%s.tar.gz' % markdownVersion
        veBinPath = self.fs.makeVeBinPath(application)
        easyInstallPath = self.fs.join(veBinPath, 'easy_install')
        print "Installing %s" % markdownDownloadUrl
        cmd = '%s %s' % (easyInstallPath, markdownDownloadUrl)
        self.system(cmd, 'install markdown')

    def setupService(self, service):
        # Make a service from installation.
        self.generateNewConfigFile(service)
        self.setupServiceFromConfig(service)

    def generateNewConfigFile(self, service):
        arguments = self.makeConfigArguments(service)
        configPath = self.fs.makeConfigPath(service)
        arguments.append(configPath)
        if not self.makeconfigScriptPath:
            msg = "Missing makeconfigScriptPath on class: %s" % self.__class__
            raise Exception, msg
        cmd = '%s %s' % (self.makeconfigScriptPath, ' '.join(arguments))
        veBinPath = self.fs.makeVeBinPath(service.application)
        self.fs.chdir(veBinPath)
        self.system(cmd, 'make %s configuration file' % service.application.provision.name)

    def makeConfigArguments(self, service):
        arguments = []
        arguments.append("--virtualenv-bin-dir=%s" % (
            self.fs.makeVeBinPath(service.application)))
        arguments.append("--master-dir=%s" % self.fs.makeInstallPath(service))
        #if options.serviceName != None:
        #    arguments.append("--service-name=%s" % options.serviceName)
        if 'test' in service.name:
            arguments.append("--system-mode=%s" % 'development')
        else:
            # Todo: Fix domainmodel to clear access control memos when access control changes?
            arguments.append("--enable-memoization")
        if self.dictionary[TIMEZONE]:
            arguments.append("--environment-timezone=%s" %  self.dictionary[TIMEZONE])
        dbType = self.makeDbType()
        if dbType == 'sqlite':
            pass # Assume this is the default.
        elif dbType in ['mysql', 'postgres']:
            dbName = self.makeDbName(service)
            dbUser = self.makeDbUser(service)
            dbPass = self.makeDbPass(service)
            dbSuperUser = self.makeDbSuperUser(service)
            dbSuperPass = self.makeDbSuperPass(service)
            arguments.append("--db-type=%s" % dbType)
            arguments.append("--db-name=%s" % dbName)
            arguments.append("--db-user=%s" % dbUser)
            arguments.append("--db-pass=%s" % dbPass)
            if dbSuperUser != dbUser:
                arguments.append("--db-super-user=%s" % dbSuperUser)
                arguments.append("--db-super-pass=%s" % dbSuperPass)
        else:
            raise Exception, "Db type '%s' not supported." % dbType
        return arguments

    def setupServiceFromConfig(self, service):
        self.setConfigPathInEnviron(service)
        self.runAdminSetup(service)

    def runAdminSetup(self, service):
        self.fs.chdir(self.fs.makeVeBinPath(service.application))
        if not self.adminScriptPath:
            msg = "Missing adminScriptPath on class: %s" % self.__class__
            raise Exception, msg
        cmd = "%s setup" % self.adminScriptPath
        self.system(cmd, "set up new %s service" % service.application.provision.name)
        ## todo: This only if supporting apache running as another user.
        #installPath = self.makeInstallPath(service)
        #cmd = "chmod -R g+rX %s" % installPath
        #self.system(cmd, 'chmod to support group')

    def setConfigPathInEnviron(self, service):
        if not self.configEnvvarName:
            msg = "Missing configEnvvarName on class: %s" % self.__class__
            raise Exception, msg
        configPath = self.fs.makeConfigPath(service)
        os.environ[self.configEnvvarName] = configPath

    def unitTestService(self, service):
        self.setConfigPathInEnviron(service)
        self.fs.chdir(self.fs.makeVeBinPath(service.application))
        if not self.testScriptPath:
            msg = "Missing testScriptPath on class: %s" % self.__class__
            raise Exception, msg
        cmd = self.testScriptPath
        self.system(cmd, "pass unit tests")



