import unittest
from kforge.test.customer.plugin.base import PluginTestCase
import commands
from kforge.dictionary import *

def suite():
    suites = [
        unittest.makeSuite(TestGitAccess),
        unittest.makeSuite(TestSvnAccess),
        unittest.makeSuite(TestMercurialAccess),
        unittest.makeSuite(TestSshKeyRegistration),
        unittest.makeSuite(TestSshKeyRegistrationFailBase64),
    ]
    return unittest.TestSuite(suites)

# Todo: Svn SSH access (is harder because we don't get told the service path in the command).
# Or given we know the user, create symlinks according to user, and start svnserve in
# user's folder (access control by only making symlinks to repos the user can write to. Will
# need to run checks whenever a repository is created/deleted and when a member is created/
# updated/deleted and when any access control objects (roles etc.) are changed....

class SshTestCase(PluginTestCase):

    requiredPlugins = None

    def setUp(self):
        super(SshTestCase, self).setUp()
        self.urlPersonSshKeys = self.url_for('person.admin', person=self.kuiPersonName,
            subcontroller='sshKeys')
        self.urlPersonSshKeyCreate = self.url_for('person.admin', person=self.kuiPersonName,
            subcontroller='sshKeys', action='create')

    def createSshKey(self):
        sshKeyIds = set(self.registry.sshKeys.keys())
        sshKeyString = self.getSshKeyString()
        params = {
            'keyString': sshKeyString,
        }
        self.postAssertCode(self.urlPersonSshKeyCreate, params)
        sshKeyId = (set(self.registry.sshKeys.keys()) - set(sshKeyIds)).pop()
        return sshKeyId

    def deleteSshKey(self, sshKeyId):
        url = self.url_for('person.admin', person=self.kuiPersonName,
            subcontroller='sshKeys', action='delete', id=sshKeyId)
        self.postAssertCode(url, {'Submit':'Delete'}, code=302)

    def getSshKeyString(self):
        keyString = ''
        paths = ['~/.ssh/id_rsa.pub', '~/.ssh/id_dsa.pub']
        for path in paths:
            s,o = commands.getstatusoutput('cat %s' % path)
            if not s:
                keyString = o
                break
        assert keyString, "Couldn't read SSH key: %s" % paths
        return keyString.strip()


class SshAccessTestCase(SshTestCase):

    def setUp(self):
        super(SshAccessTestCase, self).setUp()
        self.sshKeyId = self.createSshKey()

    def tearDown(self):
        self.deleteSshKey(self.sshKeyId)
        super(SshAccessTestCase, self).tearDown()

    def testAccess(self):
        self.fail("Test not implemented.")


class TestGitAccess(SshAccessTestCase):

    requiredPlugins = ['ssh', 'git']

    def testAccess(self):
        # As project administrator.
        self.createService('git', 'git')
        self.createService('git', 'git2')
        self.createService('git', 'git3')
        self.createService('git', 'git4')
        self.createService('git', 'git5')
        self.gitCloneAddCommitPush('git', 'Testing SSH access (project admin)...')
        # As project developer.
        self.changePersonProjectRole('Developer')
        self.gitCloneAddCommitPush('git2', 'Testing SSH access (project developer)...')
        # As project friend.
        self.changePersonProjectRole('Friend')
        self.gitCloneAddCommitPush('git3', 'Testing SSH access (project friend)...', expectPushFail=True)
        # As project visitor.
        self.changePersonProjectRole('Visitor')
        self.gitCloneAddCommitPush('git4', 'Testing SSH access (project visitor)...', expectCloneFail=True)
        # As project administrator, again.
        self.changePersonProjectRole('Administrator')
        self.gitCloneAddCommitPush('git5', 'Testing SSH access (project admin, again)...')
        
    def gitClone(self, serviceName, expectCloneFail=False):
        url = '%('+SSH_USER_NAME+')s@%('+SSH_HOST_NAME+')s:'
        url %= self.dictionary
        url += self.getServicePath(serviceName)
        cmd = 'git clone %s %s' % (url, serviceName)
        if self.system(cmd):
            if not expectCloneFail:
                self.fail('Failed to clone: %s' % self.lastStatusOutput)
        elif expectCloneFail:
            self.fail('Clone was a success, but failure was expected.')


class TestSvnAccess(SshAccessTestCase):

    requiredPlugins = ['ssh', 'svn']

    def testAccess(self):
        # As project administrator.
        self.createService('svn', 'svn')
        self.createService('svn', 'svn2')
        self.createService('svn', 'svn3')
        self.createService('svn', 'svn4')
        self.createService('svn', 'svn5')
        self.svnCheckoutAddCommit('svn', 'Testing SSH access (project admin)...')
        # As project developer.
        self.changePersonProjectRole('Developer')
        self.svnCheckoutAddCommit('svn2', 'Testing SSH access (project developer)...')
        # As project friend.
        self.changePersonProjectRole('Friend')
        self.svnCheckoutAddCommit('svn3', 'Testing SSH access (project friend)...', expectCommitFail=True)
        # As project visitor.
        self.changePersonProjectRole('Visitor')
        self.svnCheckoutAddCommit('svn4', 'Testing SSH access (project visitor)...', expectCheckoutFail=True)
        # As project administrator, again.
        self.changePersonProjectRole('Administrator')
        self.svnCheckoutAddCommit('svn5', 'Testing SSH access (project admin, again)...')
        
        
    def svnCheckout(self, serviceName, expectCheckoutFail=False):
        url = 'svn+ssh://%('+SSH_USER_NAME+')s@%('+SSH_HOST_NAME+')s'
        url %= self.dictionary
        url += self.getServicePath(serviceName)
        cmd = 'svn co %s %s' % (url, serviceName)
        if self.system(cmd):
            if not expectCheckoutFail:
                self.fail('Failed to checkout: %s' % self.lastStatusOutput)
        elif expectCheckoutFail:
            self.fail('Checkout was a success, but failure was expected.')


class TestMercurialAccess(SshAccessTestCase):

    requiredPlugins = ['ssh', 'mercurial']

    def testAccess(self):
        # As project administrator.
        self.createService('mercurial', 'mercurial')
        self.createService('mercurial', 'mercurial2')
        self.createService('mercurial', 'mercurial3')
        self.createService('mercurial', 'mercurial4')
        self.createService('mercurial', 'mercurial5')
        self.mercurialCloneAddCommitPush('mercurial', 'Testing SSH access (project admin)...')
        # As project developer.
        self.changePersonProjectRole('Developer')
        self.mercurialCloneAddCommitPush('mercurial2', 'Testing SSH access (project developer)...')
        # As project friend.
        self.changePersonProjectRole('Friend')
        # Todo: Make this work with expectPushFail=True instead. :-)
        self.mercurialCloneAddCommitPush('mercurial3', 'Testing SSH access (project friend)...', expectPushFail=True)
        # As project visitor.
        self.changePersonProjectRole('Visitor')
        self.mercurialCloneAddCommitPush('mercurial4', 'Testing SSH access (project visitor)...', expectCloneFail=True)
        # As project administrator, again.
        self.changePersonProjectRole('Administrator')
        self.mercurialCloneAddCommitPush('mercurial5', 'Testing SSH access (project admin, again)...')
        
    def mercurialClone(self, serviceName, expectCloneFail=False):
        url = 'ssh://%('+SSH_USER_NAME+')s@%('+SSH_HOST_NAME+')s'
        url %= self.dictionary
        url += self.getServicePath(serviceName)
        cmd = 'hg clone %s %s' % (url, serviceName)
        if self.system(cmd):
            if not expectCloneFail:
                self.fail('Failed to clone: %s' % self.lastStatusOutput)
        elif expectCloneFail:
            self.fail('Clone was a success, but failure was expected.')


class TestSshKeyRegistration(SshTestCase):

    requiredPlugins = ['ssh']

    def testCreateDelete(self):
        self.getAssertContent(self.urlPersonHome, 'Register SSH key')
        sshKeyString = self.getSshKeyString()
        # Check the SSH key doesn't exist.
        wrapableKeyString = '&#8203;'.join(list(sshKeyString)) # For Firefox.
        self.getAssertNotContent(self.urlPersonHome, wrapableKeyString)
        # Create the SSH key.
        self.getAssertContent(self.urlPersonSshKeyCreate, 'Register SSH Key')
        sshKeyId = self.createSshKey()
        # Check the SSH key does exist.
        self.getAssertContent(self.urlPersonHome, wrapableKeyString)
        # Delete the SSH key.
        self.deleteSshKey(sshKeyId)
        # Check the SSH key doesn't exist.
        self.getAssertNotContent(self.urlPersonHome, wrapableKeyString)
        

class TestSshKeyRegistrationFailBase64(SshTestCase):

    requiredPlugins = ['ssh']

    def testCreate(self):
        self.getAssertContent(self.urlPersonHome, 'Register SSH key')
        sshKeyString = self.getSshKeyString()
        # Check the SSH key doesn't exist.
        self.getAssertNotContent(self.urlPersonHome, sshKeyString)
        # Create the SSH key.
        self.getAssertContent(self.urlPersonSshKeyCreate, 'Register SSH Key')
        sshKeyId = self.createSshKey()
        sshKeyString = 'ssh-rsa fff some@domain'
        params = {'keyString': sshKeyString}
        self.postAssertContent(self.urlPersonSshKeyCreate, params, "Key does not appear to be encoded with base64.", code=400)
        # Check the SSH key doesn't exist.
        self.getAssertNotContent(self.urlPersonHome, sshKeyString)

