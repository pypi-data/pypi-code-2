from dm.migrate import FilesDumper
from dm.migrate import DomainModelLoader
from kforge.command.backup import BackupPathBuilder
import os
import shutil

class FilesDumper(FilesDumper):

    def dumpInDir(self, fileDumpDirPath):
        super(FilesDumper, self).dumpInDir(fileDumpDirPath)
        self.backupPathBuilder = BackupPathBuilder(fileDumpDirPath)
        self.dumpProjects()

    def dumpProjects(self):
        for project in self.registry.projects:
            self.dumpProjectFiles(project)

    def dumpProjectFiles(self, project):
        projectBackupPath = self.backupPathBuilder.getProjectPath(project)
        if os.path.exists(projectBackupPath):
            shutil.rmtree(projectBackupPath)
        os.makedirs(projectBackupPath)
        print "Dumping project: %s" % projectBackupPath 
        for service in project.services:
            projectPluginPath = self.backupPathBuilder.getProjectPluginPath(
                service
            )
            if not os.path.exists(projectPluginPath):
                os.makedirs(projectPluginPath)
            pluginSystem = service.plugin.getSystem()
            pluginSystem.backup(service, self.backupPathBuilder)


#class DomainModelLoader(DomainModelLoader):
#
#    def migrateDataDump(self):
#        version = self.getDumpVersion().split('.')
#
#        # Migrate versions earlier than v0.19.
#        version_0_19 = '0.19'.split('.')
#        if version < version_0_19:
#           self.migrateDataDump__pre0_19__to__0_19()
#           versionDump = version_0_19
#
#        return # That's all folks! However, future migrateDataDump() 
#        # method might be extended like this:
#
#        # Migrate from v0.19 to v0.20.
#        version_0_20 = '0.20'.split('.')
#        if version == version_0_19:
#           self.migrateDataDump__0_19__to__0_20()
#           versionDump = version_0_20
#
#        # Migrate from v0.20 to v1.0.
#        version_1_0 = '1.0'.split('.')
#        if version == version_0_20:
#           self.migrateDataDump__0_20__to__1_0()
#           versionDump = version_1_0
#
#    def migrateDataDump__pre0_19__to__0_19(self):
#        self.dataDump['System']['1']['version'] = '0.19'


