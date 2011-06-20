from kforge.test.customer.base import KforgeWebTestCase
import tempfile
import commands
from time import sleep
import os
from subprocess import Popen, PIPE
import shlex
import sys

class PluginTestCase(KforgeWebTestCase):

    requiredPlugins = []

    def setUp(self):
        KforgeWebTestCase.setUp(self)
        self.enableRequiredPlugins()
        self.registerPerson()
        self.loginPerson()
        self.registerProject()

    def enableRequiredPlugins(self):
        for pluginName in self.requiredPlugins:
            if pluginName not in self.registry.plugins:
                self.registry.plugins.create(pluginName)

    def createService(self, pluginName, serviceName, wait=True):
        url = self.urlProjectServiceCreate
        params = {
            'plugin': pluginName,
            'name': serviceName,
        }
        page = self.postPage(url, params)
        if wait:
            self.waitRunningService(serviceName)
        return page

    def waitRunningService(self, serviceName):
        url = self.getProjectServicePath(serviceName)
        patience = 5
        interval = 0.5
        isRunning = False
        while patience and not isRunning:
            page = self.page(url)
            if 'Running' in page.body: 
                isRunning = True
            else:
                sleep(interval)
                patience -= interval
        if not isRunning:
            print page
            self.fail("Service isn't running: %s: %s" % (url, page.body))

    def getProjectServiceEditPath(self, serviceName):
        return self.getProjectServicePath(serviceName) + 'edit/'

    def getProjectServicePath(self, serviceName):
        return self.urlProjectServices + '%s/' % serviceName

    def getServicePath(self, serviceName):
        return self.urlSiteHome + '%s/%s/' % (self.kuiProjectName, serviceName)

    def getServiceUrl(self, serviceName):
        url = "http://%s" % self.server
        if self.port != "80":
            url += ":%s" % self.port
        url += self.getServicePath(serviceName)
        return url

    def makeTempFolder(self, prefix='kforgetest'):
        return tempfile.mkdtemp(prefix=prefix)

    def system(self, cmd):
        self.lastStatusOutput = ""
        import commands
        s,o = commands.getstatusoutput(cmd)
        if s:
            self.lastStatusOutput = "Error %s: %s" % (s, o)
            return s

    def svnCheckoutAddCommit(self, serviceName, commitMsg, expectCheckoutFail=False, expectCommitFail=False):
        oldcwd = os.getcwd()
        os.chdir(self.makeTempFolder())
        try:
            self.svnCheckout(serviceName, expectCheckoutFail=expectCheckoutFail)
            if not expectCheckoutFail:
                os.chdir(serviceName)
                # Add file.
                fileName = 'file.txt'
                self.writeFile(fileName, 'Lorem ipsum...\n')
                cmd = 'svn add %s' % fileName
                if self.system(cmd):
                    self.fail('Failed to add file: %s' % self.lastStatusOutput)
                cmd = 'svn ci --username %s --password %s %s -m "%s\n"' % (
                    self.kuiPersonName,
                    self.kuiPersonPassword,
                    fileName,
                    commitMsg
                )
                # Commit file.
                if self.system(cmd):
                    if not expectCommitFail:
                        self.fail('Failed to commit file: %s' % self.lastStatusOutput)
                elif expectCommitFail:
                    self.fail('Commit was a success, but failure was expected.')
                # Now test for adding folder with a file.
                if not expectCommitFail:
                    folderName = 'folder'
                    cmd = 'mkdir %s' % folderName
                    if self.system(cmd):
                        self.fail('Failed to create folder: %s' % self.lastStatusOutput)
                    cmd = 'svn add %s' % folderName
                    if self.system(cmd):
                        self.fail('Failed to add folder: %s' % self.lastStatusOutput)
                    cmd = 'svn ci --username %s --password %s %s -m "%s\n"' % (
                        self.kuiPersonName,
                        self.kuiPersonPassword,
                        folderName,
                        commitMsg
                    )
                    # Commit folder.
                    if self.system(cmd):
                        self.fail('Failed to commit folder: %s' % self.lastStatusOutput)
                    # Add file to folder.
                    fileName = '%s/file.txt' % folderName
                    self.writeFile(fileName, 'Lorem ipsum...\n')
                    cmd = 'svn add %s' % fileName
                    if self.system(cmd):
                        self.fail('Failed to add file to folder: %s' % self.lastStatusOutput)
                    cmd = 'svn ci --username %s --password %s %s -m "%s\n"' % (
                        self.kuiPersonName,
                        self.kuiPersonPassword,
                        fileName,
                        commitMsg
                    )
                    # Commit file to folder.
                    if self.system(cmd):
                        self.fail('Failed to commit file to folder: %s' % self.lastStatusOutput)
                    # Todo: Checkout folder... :-)
        finally:
            os.chdir(oldcwd)

    def svnCheckout(self, serviceName, expectCheckoutFail=False):
        url = self.getServiceUrl(serviceName)
        cmd = 'svn co --username %s --password %s %s %s' % (
            self.kuiPersonName,
            self.kuiPersonPassword,
            url,
            serviceName
        )
        if self.system(cmd):
            if not expectCheckoutFail:
                self.fail('Failed to checkout: %s' % self.lastStatusOutput)
        elif expectCheckoutFail:
            self.fail('Checkout was a success, but failure was expected.')

    def mercurialCloneAddCommitPush(self, serviceName, commitMsg, expectCloneFail=False, expectPushFail=False):
        oldcwd = os.getcwd()
        os.chdir(self.makeTempFolder())
        try:
            self.mercurialClone(serviceName, expectCloneFail=expectCloneFail)
            if not expectCloneFail:
                os.chdir(serviceName)

                fileName = 'mercurialCloneAddCommitPush.txt'
                self.writeFile(fileName, 'Lorem ipsum...\n')
                
                cmd = 'hg add %s' % fileName
                if self.system(cmd):
                    self.fail('Failed to add file: %s' % self.lastStatusOutput)
                cmd = 'hg ci . -m"%s\n"' % (commitMsg)
                if self.system(cmd):
                    self.fail('Failed to commit: %s' % self.lastStatusOutput)
                cmd = 'hg push' % ()
                if self.system(cmd):
                    if not expectPushFail:
                        self.fail('Failed to push: %s' % self.lastStatusOutput)
                elif expectPushFail:
                        self.fail('Push was a success, but expected failure.')
        finally:
            os.chdir(oldcwd)

    def mercurialClone(self, serviceName, expectCloneFail=False):
        url = self.getServiceUrl(serviceName)
        cmd = 'hg clone %s %s' % (url, serviceName)
        # Todo: Check ~/.hgrc has the lines we need (or add them?).
        #stdindata = "%s\n%s\n" % ('admin', 'pass')  # Needs .hgrc file.
        stdindata = "\n\n"  # Prevents hanging when ~/.hgrc file is wrong.
        try:
            self.runPopen(cmd, stdindata)
        except Exception, inst:
            if not expectCloneFail:
                msg = "%s" % inst
                if 'http authorization required' in msg:
                    msg += '... Hint from the KForge test suite:'
                    msg += ''' Please check your ~/.hgrc contains:
[ui]
username = Your Name <your.name@appropriatesoftware.net>

[auth]
kforgedev.prefix = http://kforge.dev.localhost
kforgedev.username = admin 
kforgedev.password = pass
kforgetest.prefix = http://kforge.test.localhost
kforgetest.username = admin 
kforgetest.password = pass
'''
                self.fail('Failed to clone: %s' % msg)
            else:
                self.fail('Clone was a success, but failure was expected.')

    def gitCloneAddCommitPush(self, serviceName, commitMsg, expectCloneFail=False, expectPushFail=False):
        oldcwd = os.getcwd()
        os.chdir(self.makeTempFolder())
        try:
            self.gitClone(serviceName, expectCloneFail=expectCloneFail)

            if not expectCloneFail:
                os.chdir(serviceName)

                fileName = 'gitCloneAddCommitPush.txt'
                self.writeFile(fileName, 'Lorem ipsum...\n')
                
                cmd = 'git add %s' % fileName
                if self.system(cmd):
                    self.fail('Failed to add file: %s' % self.lastStatusOutput)
                cmd = 'git commit %s -m"%s\n"' % (fileName, commitMsg)
                if self.system(cmd):
                    self.fail('Failed to commit: %s' % self.lastStatusOutput)
                cmd = 'git push origin master' % ()
                pressReturn = 0
                if expectPushFail:
                    pressReturn = 15
                try:
                    self.runPopen(cmd, pressReturn=pressReturn)
                except Exception, inst:
                    if not expectPushFail:
                        self.fail('Failed to push: %s' % inst)
                else:
                    if expectPushFail:
                        self.fail('Push was a success, but failure was expected.')
        finally:
            os.chdir(oldcwd)

    def gitClone(self, serviceName, expectCloneFail=False):
        url = self.getServiceUrl(serviceName)
        cmd = 'git clone %s %s' % (url, serviceName)
        #stdindata = "%s\n%s\n" % (self.kuiPersonName, self.kuiPersonPassword)
        stdindata = "\n\n\n\n\n\n\n\n"
        # This doesn't seem to prevent prompt for 'Username:' from git.
        # Todo: Check ~/.netrc has the lines we need (or add them?).
        # Todo: Check ~/.netrc has the permissions we need (or set them?).
        try:
            pressReturn = 0
            if expectCloneFail:
                pressReturn = 10
                stdindata = None
            self.runPopen(cmd, stdindata, pressReturn=pressReturn)
        except Exception, inst:
            if not expectCloneFail:
                msg = "%s" % inst
                if 'Authentication failed' in msg:
                    msg += '... Hint from the KForge test suite:'
                    msg += ''' Please check your ~/.netrc file contains:
    machine kforge.dev.local
    login admin
    password pass
    machine kforge.test.local
    login admin
    password pass

    Please note, the ~/.netrc file must have permission set to 600.
    '''
                self.fail('Failed to clone: %s' % msg)
        else:
            if expectCloneFail:
                self.fail('Clone was a success, but failure was expected.')

    def writeFile(self, path, content):
        f = open(path, 'w')
        f.write(content)
        f.close()

    def runPopen(self, cmd, stdindata=None, pressReturn=0):
        if stdindata:
            p = Popen(shlex.split(str(cmd)), stdin=PIPE, stdout=PIPE, stderr=PIPE, env={})
            stdoutdata, stderrdata = p.communicate(stdindata)
        #elif pressReturn:
        #    p = Popen(shlex.split(str(cmd)), stdin=PIPE, stdout=PIPE, stderr=PIPE, env={})
        #    for i in range(pressReturn):
        #        sleep(0.5)
        #        #print "Pressing return..."
        #        sys.stdin.write('\n\n')
        #        sys.stdin.flush()
        #    stdoutdata, stderrdata = p.communicate()
        else:
            p = Popen(shlex.split(str(cmd)), stdin=None, stdout=PIPE, stderr=PIPE, env={})
            stdoutdata, stderrdata = p.communicate()
        if p.wait():
            msg = "Error: cmd '%s' caused error: %s %s" % (cmd, stdoutdata, stderrdata)
            raise Exception(msg)

