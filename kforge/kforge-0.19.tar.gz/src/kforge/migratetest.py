import unittest
from kforge.testunit import TestCase
from kforge.dictionarywords import *

def suite():
    suites = [
        unittest.makeSuite(MigrationTest),
    ]
    return unittest.TestSuite(suites)

class MigrationTest(TestCase):

    def test_registry(self):
        # Check system version in the model equals system version in the code.
        systemVersion = self.registry.systems[1].version
        self.failUnlessEqual(systemVersion, self.dictionary[SYSTEM_VERSION])

        # Check everybody can delete their memberships.
        for person in self.registry.persons:
            for membership in person.memberships:
                ac = self.accessController
                canAccess = ac.isAccessAuthorised(
                    person=person,
                    actionName='Delete',
                    protectedObject=membership,
                )
                msg = "Person '%s' can't leave project '%s'." % (
                    person.name, membership.project.name)
                self.failUnless(canAccess, msg)
            
                 

