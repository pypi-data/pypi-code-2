import os
import commands
import re
import distutils.version
# import inline so that access to docstring works even when trac not installed
# import trac

import kforge.command
import kforge.plugin.trac.dom
from kforge.ioc import *
import kforge.exceptions
from kforge.dictionarywords import TRAC_ADMIN_SCRIPT
from kforge.dictionarywords import TRAC_TEMPLATES_PATH
from kforge.dictionarywords import GIT_ADMIN_SCRIPT

class TracCommand(kforge.command.Command):
    
    def __init__(self, tracProject):
        super(TracCommand, self).__init__()
        self.tracProject = tracProject
        self.envname = self.tracProject.service.getDirPath()
        scriptPath = self.dictionary[TRAC_ADMIN_SCRIPT]
        self.tracadminBase = '%s %s ' % (scriptPath, self.envname)

    def getstatusoutput(self, cmd): 
        """Return (status, output) of executing cmd in a shell."""
        # From http://stackoverflow.com/questions/1193583/what-is-the-multiplatform-alternative-to-subprocess-getstatusoutput-older-comman
        try:
            import subprocess
            pipe = subprocess.Popen(cmd, shell=True, universal_newlines=True,
                    stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            output = str.join("", pipe.stdout.readlines()) 
            sts = pipe.wait()
            if sts is None:
                sts = 0
            return sts, output
        except Exception, inst:
            import traceback
            return (1, traceback.format_exc())
    getstatusoutput = classmethod(getstatusoutput)

class AdminUserBaseCommand(TracCommand):
    """
    Notes: must define self.shellCmd in inheriting classes.
    """

    def __init__(self, tracProject, username):
        super(AdminUserBaseCommand, self).__init__(tracProject)
        self.username = username
    
    def execute(self):
        self.status, self.output = commands.getstatusoutput(self.shellCmd)
        if self.status:
            msg = \
'''Error on attempt to execute admin user command on trac environment
associated with service %s.

Shell command was: %s

Output was %s''' % (self.tracProject.service, self.shellCmd, self.output)
            self.logger.error(msg)


class AddAdminUserCommand(AdminUserBaseCommand):

    def __init__(self, tracProject, username):
        super(AddAdminUserCommand, self).__init__(tracProject, username)
        tracAction = ' permission add %s TRAC_ADMIN '  % self.username
        self.shellCmd = self.tracadminBase + tracAction


class RemoveAdminUserCommand(AdminUserBaseCommand):

    def __init__(self, tracProject, username):
        super(RemoveAdminUserCommand, self).__init__(tracProject, username)
        tracAction = ' permission remove %s TRAC_ADMIN '  % self.username
        self.shellCmd = self.tracadminBase + tracAction


class IsAdminUserCommand(AdminUserBaseCommand):
    """Tests whether the user is a TRAC_ADMIN.
    @rtype: bool
    @return: in result attribute
    """

    def __init__(self, tracProject, username):
        super(IsAdminUserCommand, self).__init__(tracProject, username)
        # user argument only added in trac 0.9
        # tracAction = ' permission list %s'  % self.username
        tracAction = ' permission list'
        self.shellCmd = self.tracadminBase + tracAction
        self.result = None

    def execute(self):
        super(IsAdminUserCommand, self).execute()
        regex = '%s\s* TRAC_ADMIN' % self.username
        searchResult = re.search(regex, self.output)
        if searchResult is not None:
            self.result = True
        else:
            self.result = False


class TracProjectEnvironmentCreate(TracCommand):
    "Command to create a new Trac instance."

    def __init__(self, tracProject):
        super(TracProjectEnvironmentCreate, self).__init__(tracProject)
        self.svnService = self.tracProject.svn

    def execute(self):
        super(TracProjectEnvironmentCreate, self).execute()
        self.logger.info("%s: Creating new Trac environment: %s" % (self.__class__.__name__, self.envname))
        self.assertSvnService()
        self.assertTracIniNotFound()
        self.createTracProjectEnvironment()
        self.assertTracIniExists()
        self.tracProject.isEnvironmentInitialised = True
        self.tracProject.save()

    def assertSvnService(self):
        if not self.svnService:
            error = "No svn service for trac project %s." % self.tracProject
            self.raiseError(error)

    def checkProjectPluginDir(self):
        self.tracProject.service.checkProjectPluginDir()

    def createTracProjectEnvironment(self):
        import trac
        tracVersion = distutils.version.LooseVersion(trac.__version__)
        v0_9 = distutils.version.LooseVersion('0.9')
        v0_10 = distutils.version.LooseVersion('0.10')
        v0_11 = distutils.version.LooseVersion('0.11')
        project_name = self.tracProject.service.project.getLabelValue()
        if self.tracProject.service.name != self.tracProject.service.plugin.name:
            project_name += " " + self.tracProject.service.name.capitalize()
        db_str = 'sqlite:db/trac.db'
        if tracVersion < v0_9:
            db_str = '' # no db_str stuff in trac < 0.9
        if tracVersion < v0_10:
            repostype = '' # no repostype stuff in trac < 0.10
        else:
            if self.svnService.plugin.name == 'mercurial':
                repostype = 'hg'
            else:
                repostype = self.svnService.plugin.name
        templates_dir = self.dictionary[TRAC_TEMPLATES_PATH]
        if tracVersion >= v0_11:
            templates_dir = '' # no templates_dir in trac >= v0.11
        service_dir = self.svnService.getDirPath()
        if self.svnService.plugin.name == 'mercurial':
            repository_dir = os.path.join(service_dir, 'repo')
        else:
            repository_dir = service_dir
        cmd = [self.dictionary[TRAC_ADMIN_SCRIPT], self.envname, 'initenv', project_name,
            db_str, repostype, repository_dir]
        if templates_dir:
            cmd.append(templates_dir)
        cmd = [s.replace(' ', '\ ').encode('utf-8') for s in cmd]
        cmd = " ".join(cmd)
        status, output = self.getstatusoutput(cmd)
        if status:
            msg = 'Error initialising environment: %s: %s' % (repr(cmd), output)
            self.raiseError(msg)
        elif "Unknown syntax" in  output:
            msg = 'Error initialising environment: %s: %s' % (repr(cmd), output)
            self.raiseError(msg)
        # Append the trac.ini file, if necessary.
        if self.svnService.plugin.name == 'mercurial':
            if tracVersion == v0_10:
                iniComponents = "\n\n[components]\ntracvc.hg.* = enabled\n"
            else:
                iniComponents = "\n\n[components]\ntracext.hg.* = enabled\n"
            self.appendTracIni(iniComponents)
        elif self.svnService.plugin.name == 'git':
            if tracVersion == v0_10:
                iniComponents = "\n\n[components]\ngitplugin.* = enabled\n"
            else:
                iniComponents = "\n\n[components]\ntracext.git.* = enabled\n"
            gitPath = self.dictionary[GIT_ADMIN_SCRIPT]
            whichCmd = 'which %s' % gitPath
            (status, whichOutput) = commands.getstatusoutput(whichCmd)
            if status:
                raise Exception("Couldn't find Git binary '%s'." % gitPath)
            gitPath = whichOutput
            # Todo: Replace in already existing [git], if not found Trac-Git
            # isn't installed so raise error? Check and implement if true.
            iniComponents += "\n\n[git]\ngit_bin = %s\n" % gitPath
            self.appendTracIni(iniComponents)
            
    def appendTracIni(self, lines):
        tracIniFile = open(self.getTracIniPath(), 'a')
        tracIniFile.writelines(lines)
        tracIniFile.close()

    def assertTracIniExists(self):
        if not self.existsTracIni():
            msg = "Trac .ini not found on path: %s" % self.getTracIniPath()
            self.raiseError(msg)

    def assertTracIniNotFound(self):
        if self.existsTracIni():
            msg = "Trac .ini not found on path: %s" % self.getTracIniPath()
            self.raiseError(msg)

    def existsTracIni(self):
        return os.path.exists(self.getTracIniPath())

    def getTracIniPath(self):
        tracDirPath = self.tracProject.service.getDirPath()
        return os.path.join(tracDirPath, 'conf', 'trac.ini')

