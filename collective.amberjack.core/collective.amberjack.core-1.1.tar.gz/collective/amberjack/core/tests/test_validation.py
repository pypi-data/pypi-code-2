from unittest import defaultTestLoader, main
from zope.component import queryUtility, getUtility
from collective.amberjack.core.interfaces import ITourRegistration
from collective.amberjack.core.interfaces import ITourDefinition
from zope.publisher.browser import TestRequest
from Products.Five import zcml
import os

import zope.component
import plone.i18n.normalizer
import collective.amberjack.core.tests
from collective.amberjack.core.tests import base

class DummyStep(object):
    def __init__(self, url):
        self.url = url

class ValidationTests(base.AmberjackCoreTestCase):

    def setUp(self):
        super(ValidationTests, self).setUp()
        self.test_folder = os.path.dirname(collective.amberjack.core.tests.__file__)
        archive_path = os.path.join(self.test_folder, 'basic_tours.zip')  

        archive = open(archive_path,'r')
        archive.seek(0)
        source = archive.read()
        archive.close()
        filename = os.path.basename(archive_path)

        zcml.load_config('meta.zcml', zope.component)
        zcml.load_config('configure.zcml', plone.i18n.normalizer)

        zcml.load_string('''<configure
        xmlns="http://namespaces.zope.org/zope">
        <utility component="collective.amberjack.core.blueprints.Step"
                 name="collective.amberjack.blueprints.step" />
        </configure>''')

        zcml.load_string('''<configure
        xmlns="http://namespaces.zope.org/zope">
        <utility component="collective.amberjack.core.blueprints.MicroStep"
                 name="collective.amberjack.blueprints.microstep" />
        </configure>''')

        zcml.load_string('''<configure
        xmlns="http://namespaces.zope.org/zope">
        <utility component="collective.amberjack.core.registration.FileArchiveRegistration"
                 name="zip_archive" />
        </configure>''')

        reg = queryUtility(ITourRegistration, 'zip_archive')
        registration = reg(source, filename)
        registration.register()
        self.tour = getUtility(ITourDefinition, u'tour1-add-and-publish-a-folder')

        step = DummyStep('/')
        self.tour.steps = [step,]

        self.context = self.portal


    def test_validation_sandbox_isCreated(self):
        '''checks the presence or the absence of a folder: sandbox active
           sandbox active
        '''
        request = TestRequest()
        self.setRoles('Manager')
        self.context.portal_amberjack.sandbox=True
        user_id = self.portal.portal_membership.getAuthenticatedMember().getId()
        user_folder = getattr(self.portal.Members, user_id)
        user_folder.invokeFactory('Folder', id='myfolder')
        self.tour.validators = ["python: isCreated(context,'/myfolder-XXX')", ]
        self.assertNotEquals(self.tour.validators, [])
        self.assertNotEquals(self.tour.validate(self.context, request), [])
        self.tour.validators = ["python: isCreated(context,'/myfolder')", ]
        self.assertNotEquals(self.tour.validators, [])
        self.assertEquals(self.tour.validate(self.context, request), [])
        user_folder.manage_delObjects(['myfolder',])

    def test_validation_nosandbox_isCreated(self):
        '''checks the presence or the absence of a folder
           sandbox not active
        '''
        request = TestRequest()
        self.setRoles('Manager')
        self.portal.invokeFactory('Folder', id='myfolder')
        self.tour.validators = ["python: isCreated(context,'/myfolder-XXX')", ]
        self.assertNotEquals(self.tour.validators, [])
        self.assertNotEquals(self.tour.validate(self.context, request), [])
        self.tour.validators = ["python: isCreated(context,'/myfolder')", ]
        self.assertNotEquals(self.tour.validators, [])
        self.assertEquals(self.tour.validate(self.context, request), [])
        self.portal.manage_delObjects(['myfolder',])


    def test_validation_sandbox_hasRoles(self):
        '''checks if the authenticated user has (or not) the given permission 
           where the tutorial will run
           sandbox active
        '''
        request = TestRequest()
        user = self.portal.portal_membership.getAuthenticatedMember()
        user_id = user.getId()
        request.AUTHENTICATED_USER = user
        self.context.portal_amberjack.sandbox=True
        user_folder = getattr(self.portal.Members, user_id)
        user_folder.manage_setLocalRoles(user_id, ['Reviewer',])
        self.tour.validators = ["python: hasRole(context, request, 'Editor')", ]
        self.assertNotEquals(self.tour.validate(self.context, request), [])
        self.tour.validators = ["python: hasRole(context, request, 'Reviewer')", ]
        self.assertEquals(self.tour.validate(self.context, request), [])


    def test_validation_nosandbox_hasRoles(self):
        '''checks if the authenticated user has (or not) the given permission 
           where the tutorial will run
           sandbox not active
        '''
        request = TestRequest()
        user = self.portal.portal_membership.getAuthenticatedMember()
        user_id = user.getId()
        request.AUTHENTICATED_USER = user
        self.portal.manage_setLocalRoles(user_id, ['Reviewer',])
        self.tour.validators = ["python: hasRole(context, request, 'Editor')", ]
        self.assertNotEquals(self.tour.validate(self.context, request), [])
        self.tour.validators = ["python: hasRole(context, request, 'Reviewer')", ]
        self.assertEquals(self.tour.validate(self.context, request), [])


def test_suite():
    return defaultTestLoader.loadTestsFromName(__name__)

if __name__ == '__main__':
    main(defaultTest='test_suite')
