from kforge.dictionarywords import *
import kforge.testunit
import unittest
import kforge.command
import kforge.plugin.trac.commandtest
import kforge.plugin.trac

def suite():
    suites = [
            kforge.plugin.trac.commandtest.suite(),
            unittest.makeSuite(TestTrac),
        ]
    return unittest.TestSuite(suites)

class TracTestCase(kforge.testunit.TestCase):

    # Todo: Refactor to a declarative syntax.
    def setUp(self):
        super(TracTestCase, self).setUp() 
        if not self.registry.plugins.has_key('trac'):
            self.registry.plugins.create('trac')


class TestTrac(TracTestCase):

    def setUp(self):
        super(TestTrac, self).setUp() 
        registerClass = kforge.plugin.trac.dom.TracProject.registerClass
        self.tracRegister = registerClass('TracProject', keyName='service')
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
            # split into create and update to trigger onTracProjectUpdate
            self.tracProject.svn = self.svnService
            self.tracProject.save()
        except:
            try:
                self.tracProject.delete()
            finally:
                self.service.delete()
                self.svnService.delete()
                self.service.purge()
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

    def test_onTracProjectUpdate(self):
        # levin is admin of annakarenina and should be a trac admin now
        cmd = kforge.plugin.trac.command.IsAdminUserCommand(self.tracProject,
                'levin')
        cmd.execute()
        self.failUnless(cmd.result)

    # def test_onMemberUpdate(self):
    #    natasha = self.registry.persons['natasha']
    #    self.project.members.create(natasha)

