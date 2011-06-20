import unittest

from kforge.plugin.trac.command import AddAdminUserCommand
from kforge.plugin.trac.command import RemoveAdminUserCommand
from kforge.plugin.trac.command import IsAdminUserCommand
from kforge.plugin.trac.command import TracProjectEnvironmentCreate
import kforge.plugin.trac.dom
import kforge.command.service
from kforge.exceptions import *
from kforge.testunit import *

def suite():
    suites = [
        unittest.makeSuite(TestTracCommands)
    ]
    return unittest.TestSuite(suites)

class TestTracCommands(TestCase):

    def setUp(self):
        super(TestTracCommands, self).setUp()
        registerClass = kforge.plugin.trac.dom.TracProject.registerClass
        self.tracRegister = registerClass('TracProject', keyName='service')
        if not self.registry.plugins.has_key('trac'):
            self.registry.plugins.create('trac')
        self.plugin = self.registry.plugins['trac']
        self.project = self.registry.projects['annakarenina']
        
        svn = self.registry.plugins['svn']
        self.svnService = self.project.services.create('svn', plugin=svn)
        try:
            self.service = self.project.services.create('trac',
                    plugin=self.plugin)
        except:
            self.svnService.delete()
            self.svnService.purge()
            raise
        try:
            self.tracProject = self.tracRegister.create(
                self.service, svn=self.svnService
            )
        except:
            try:
                self.tracProject.delete()
            finally:
                self.service.delete()
                self.svnService.delete()
                self.service.purge()
                self.svnService.purge()
            raise
        try:
            self.command = TracProjectEnvironmentCreate(self.tracProject)
        except:
            self.tracProject.delete()
            self.service.delete()
            self.service.purge()
            self.svnService.delete()
            self.svnService.purge()
            raise

    def tearDown(self):
        try:
            self.tracProject.delete()
        finally:
            try:
                self.service.delete()
                self.service.purge()
            finally:
                self.svnService.delete()
                self.svnService.purge()

    def test_TracProjectEnvironmentCreate(self):
        self.command.execute()

    def test_AddAdminUser(self):
        self.command.execute()
        username = 'natasha'
        setAdminUser = AddAdminUserCommand(self.tracProject, username)
        isAdminUser = IsAdminUserCommand(self.tracProject, username)
        setAdminUser.execute()
        isAdminUser.execute()
        self.failUnless(isAdminUser.result)

        removeAdmin = RemoveAdminUserCommand(self.tracProject, username)
        removeAdmin.execute()
        isAdminUser.execute()
        self.failIf(isAdminUser.result)

