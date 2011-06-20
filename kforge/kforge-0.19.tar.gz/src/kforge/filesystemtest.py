import kforge.filesystem
import unittest
from kforge.testunit import TestCase

def suite():
    suites = [
        unittest.makeSuite(FileSystemPathBuilderTest),
    ]
    return unittest.TestSuite(suites)

class FileSystemPathBuilderTest(TestCase):
    
    def setUp(self):
        super(FileSystemPathBuilderTest, self).setUp()
        self.builder = kforge.filesystem.FileSystemPathBuilder()
    
    def getAllServices(self):
        servicesList = []
        for project in self.registry.projects:
            for service in project.services:
                servicesList.append(service)
        return servicesList
        
    def testGetProjectPath(self):
        for project in self.registry.projects:
            path = self.builder.getProjectPath(project)
            self.failUnless(project.name in path)
    
    def testGetProjectPluginPath(self):
        for service in self.getAllServices():
            project = service.project
            plugin = service.plugin
            path = self.builder.getProjectPluginPath(project, plugin)
            self.failUnless(project.name in path)
    
    def testGetServicePath(self):
        for service in self.getAllServices():
            self.builder.getServicePath(service)
 
