import os
import sys
from dm.exceptions import DataMigrationError
from dm.ioc import RequiredFeature
from dm.plugin.base import PluginBase
from dm.configwriter import ConfigWriter
from quant.dom.builder import Provision
from quant.dictionarywords import DOMAIN_NAME, SYSTEM_NAME
from quant.dictionarywords import DB_NAME, DB_TYPE, DB_USER, DB_PASS, DB_SUPER_USER, DB_SUPER_PASS 
from quant.dictionarywords import TIMEZONE
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
        self.remove(unpackedDirPath, "unpacked source archive")

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


