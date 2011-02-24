from provide.dom.testunit import TestCase
import unittest

def suite():
    suites = [
        unittest.makeSuite(TestProvision),
        unittest.makeSuite(TestApplication),
        unittest.makeSuite(TestDependency),
        unittest.makeSuite(TestPurpose),
        unittest.makeSuite(TestService),
        unittest.makeSuite(TestDataDump),
        unittest.makeSuite(TestMigrationPlan),
    ]
    return unittest.TestSuite(suites)


class TestProvision(TestCase):

    provisionName = 'scanbooker'
    applicationName = 'scanbooker-0.1'
    purposeName = 'production'
    migrationPlanName = '0.1-0.2'

    def setUp(self):
        super(TestProvision, self).setUp()
        self.provision = self.registry.provisions.create(self.provisionName)

    def tearDown(self):
        super(TestProvision, self).tearDown()
        if self.provisionName in self.registry.provisions:
            provision = self.registry.provisions[self.provisionName]
            provision.delete()

    def test_applications(self):
        self.failIf(len(self.provision.applications))
        application = self.provision.applications.create(self.applicationName)
        self.failUnlessEqual(application.name, self.applicationName)
        self.failUnless(len(self.provision.applications))
        application.delete()
        self.failIf(len(self.provision.applications))
    
    def test_purposes(self):
        self.failIf(len(self.provision.purposes))
        purpose = self.provision.purposes.create(self.purposeName)
        self.failUnlessEqual(purpose.name, self.purposeName)
        self.failUnless(len(self.provision.purposes))
        purpose.delete()
        self.failIf(len(self.provision.purposes))
    
    def test_migrationPlans(self):
        self.failIf(len(self.provision.migrationPlans))
        migrationPlan = self.provision.migrationPlans.create(self.migrationPlanName)
        self.failUnlessEqual(migrationPlan.name, self.migrationPlanName)
        self.failUnless(len(self.provision.migrationPlans))
        migrationPlan.delete()
        self.failIf(len(self.provision.migrationPlans))


class TestApplication(TestCase):

    provisionName = 'scanbooker'
    applicationName = 'scanbooker-0.1'
    applicationPath = ''
    serviceName = 'scanbooker-0.1_1'
    
    def setUp(self):
        super(TestApplication, self).setUp()
        self.provision = self.registry.provisions.create(self.provisionName)
        self.application = self.provision.applications.create(
            self.applicationName,
            location=self.applicationPath
        )

    def tearDown(self):
        super(TestApplication, self).tearDown()
        if self.provisionName in self.registry.provisions:
            provision = self.registry.provisions[self.provisionName]
            provision.delete()
        if self.applicationName in self.registry.applications:
            application = self.registry.applications[self.applicationName]
            application.delete()

    def test_name(self):
        self.failUnlessEqual(self.application.name, self.applicationName)
        
    def test_provision(self):
        self.failUnlessEqual(self.application.provision, self.provision)

    def test_services(self):
        self.failIf(len(self.application.services))
        service = self.application.services.create(self.serviceName)
        self.failUnlessEqual(service.name, self.serviceName)
        self.failUnless(len(self.application.services))
        service.delete()
        self.failIf(len(self.application.services))


class TestDependency(TestCase):

    provisionName = 'scanbooker'
    applicationName = 'scanbooker-0.1'
    dependencyName = 'domainmodel'
    dependencyPath = ''
    serviceName = 'scanbooker-0.1_1'
    
    def setUp(self):
        super(TestDependency, self).setUp()
        self.provision = self.registry.provisions.create(self.provisionName)
        self.application = self.provision.applications.create(
            self.applicationName,
        )
        self.dependency = self.application.dependencies.create(
            self.dependencyName, location=self.dependencyPath
        )

    def tearDown(self):
        super(TestDependency, self).tearDown()
        if self.dependencyName in self.registry.dependencies:
            dependency = self.registry.dependencies[self.dependencyName]
            dependency.delete()
        if self.applicationName in self.registry.applications:
            application = self.registry.applications[self.applicationName]
            application.delete()
        if self.provisionName in self.registry.provisions:
            provision = self.registry.provisions[self.provisionName]
            provision.delete()

    def test_name(self):
        self.failUnlessEqual(self.dependency.name, self.dependencyName)
        
    def test_application(self):
        self.failUnlessEqual(self.dependency.application, self.application)


class TestPurpose(TestCase):

    provisionName = 'scanbooker'
    purposeName = 'scanbooker-0.1'
    
    def setUp(self):
        super(TestPurpose, self).setUp()
        self.provision = self.registry.provisions.create(self.provisionName)
        self.purpose = self.provision.purposes.create(self.purposeName)

    def tearDown(self):
        super(TestPurpose, self).tearDown()
        if self.provisionName in self.registry.provisions:
            provision = self.registry.provisions[self.provisionName]
            provision.delete()
        if self.purposeName in self.registry.purposes:
            purpose = self.registry.purposes[self.purposeName]
            purpose.delete()

    def test_name(self):
        self.failUnless(self.purpose.name, self.purposeName)
        
    def test_provision(self):
        self.failUnless(self.purpose.provision, self.provision)


class TestService(TestCase):

    provisionName = 'scanbooker'
    applicationName = 'scanbooker-0.1'
    serviceName = 'scanbooker-0.1_1'
    
    def setUp(self):
        super(TestService, self).setUp()
        self.provision = self.registry.provisions.create(self.provisionName)
        self.application = self.provision.applications.create(self.applicationName)
        self.service = self.application.services.create(self.serviceName)

    def tearDown(self):
        super(TestService, self).tearDown()
        if self.provisionName in self.registry.provisions:
            provision = self.registry.provisions[self.provisionName]
            provision.delete()
        if self.applicationName in self.registry.applications:
            application = self.registry.applications[self.applicationName]
            application.delete()
        if self.serviceName in self.registry.services:
            service = self.registry.services[self.serviceName]
            service.delete()

    def test_name(self):
        self.failUnless(self.service.name, self.serviceName)
        
    def test_application(self):
        self.failUnless(self.service.application, self.application)


class TestDataDump(TestCase):

    provisionName = 'scanbooker'
    applicationName = 'scanbooker-0.1'
    serviceName = 'scanbooker-0.1_1'
    dataDumpName = 'scanbooker-0.1_1_1'
    migrationPlanName = 'scanbooker-0.1_0.2'
    
    def setUp(self):
        super(TestDataDump, self).setUp()
        self.provision = self.registry.provisions.create(self.provisionName)
        self.application = self.provision.applications.create(self.applicationName)
        self.migrationPlan = self.provision.migrationPlans.create(self.migrationPlanName)
        self.service = self.application.services.create(self.serviceName)
        self.dataDump = self.service.dataDumps.create(self.dataDumpName)

    def tearDown(self):
        super(TestDataDump, self).tearDown()
        if self.provisionName in self.registry.provisions:
            provision = self.registry.provisions[self.provisionName]
            provision.delete()
        if self.applicationName in self.registry.applications:
            application = self.registry.applications[self.applicationName]
            application.delete()
        if self.migrationPlanName in self.registry.migrationPlans:
            migrationPlan = self.registry.migrationPlans[self.migrationPlanName]
            migrationPlan.delete()
        if self.serviceName in self.registry.services:
            service = self.registry.services[self.serviceName]
            service.delete()
        if self.dataDumpName in self.registry.dataDumps:
            dataDump = self.registry.dataDumps[self.dataDumpName]
            dataDump.delete()

    def test_name(self):
        self.failUnlessEqual(self.dataDump.name, self.dataDumpName)
        
    def test_service(self):
        self.failUnlessEqual(self.dataDump.service, self.service)


class TestMigrationPlan(TestCase):

    provisionName = 'scanbooker'
    applicationName = 'scanbooker-0.1'
    serviceName = 'scanbooker-0.1_1'
    dataDumpName = 'scanbooker-0.1_1_1'
    migrationPlanName = 'scanbooker-0.1_0.2'
    
    def setUp(self):
        super(TestMigrationPlan, self).setUp()
        self.provision = self.registry.provisions.create(self.provisionName)
        self.application = self.provision.applications.create(self.applicationName)
        self.service = self.application.services.create(self.serviceName)
        self.dataDump = self.service.dataDumps.create(self.dataDumpName)
        self.migrationPlan = self.provision.migrationPlans.create(self.migrationPlanName)

    def tearDown(self):
        super(TestMigrationPlan, self).tearDown()
        if self.provisionName in self.registry.provisions:
            provision = self.registry.provisions[self.provisionName]
            provision.delete()
        if self.applicationName in self.registry.applications:
            application = self.registry.applications[self.applicationName]
            application.delete()
        if self.serviceName in self.registry.services:
            service = self.registry.services[self.serviceName]
            service.delete()
        if self.dataDumpName in self.registry.dataDumps:
            dataDump = self.registry.dataDumps[self.dataDumpName]
            dataDump.delete()
        if self.migrationPlanName in self.registry.migrationPlans:
            migrationPlan = self.registry.migrationPlans[self.migrationPlanName]
            migrationPlan.delete()

    def test_name(self):
        self.failUnlessEqual(self.migrationPlan.name, self.migrationPlanName)
    
    def test_provision(self):
        self.failUnlessEqual(self.migrationPlan.provision, self.provision)

