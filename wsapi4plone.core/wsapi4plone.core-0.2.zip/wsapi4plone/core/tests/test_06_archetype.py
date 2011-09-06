# -*- coding: utf-8 -*-
import unittest
import xmlrpclib

from zope.component import getMultiAdapter, getSiteManager
from zope.interface import Interface
from zope.interface.verify import verifyObject 

from DateTime import DateTime
from Products.Archetypes.interfaces import IBaseFolder, IBaseObject
from Products.ATContentTypes.interface.topic import IATTopic
# from Products.Five import zcml
from Products.PloneTestCase import PloneTestCase
from Products.PloneTestCase.layer import onsetup


@onsetup
def setup():
    # We may eventually want to put something here when the wsapi4plone is
    # GenericSetup installable.
    pass

setup()
PloneTestCase.setupPloneSite()


class BaseATTestCase(PloneTestCase.PloneTestCase):

    def afterSetUp(self):
        super(BaseATTestCase, self).afterSetUp()
        sm = getSiteManager()
        # Register the archetypes service adapters.
        from wsapi4plone.core.interfaces import IService, IServiceContainer
        from wsapi4plone.core.services.archetype import (
            ATObjectService, ATFolderService)
        sm.registerAdapter(ATObjectService,
                           required=(IBaseObject,),
                           provided=IService)
        sm.registerAdapter(ATFolderService,
                           required=(IBaseFolder,),
                           provided=IServiceContainer)

    def beforeTearDown(self):
        sm = getSiteManager()
        # Unregister the archetypes service adapters.
        from wsapi4plone.core.interfaces import IService, IServiceContainer
        from wsapi4plone.core.services.archetype import (
            ATObjectService, ATFolderService)
        sm.unregisterAdapter(factory=ATObjectService,
                             required=(IBaseObject,),
                             provided=IService)
        sm.unregisterAdapter(factory=ATFolderService,
                             required=(IBaseFolder,),
                             provided=IServiceContainer)
        super(BaseATTestCase, self).beforeTearDown()


def destroyCollection(test):
    pass


class TestATObjectService(BaseATTestCase):
    # The wsapi4plone.services.archetype_service.ATObjectService does not
    # need tested unless functionality is added to it. Its base class has
    # been tested in test_01_plone_service.
    pass


class TestATFolderService(BaseATTestCase):
    # The wsapi4plone.services.archetype_service.ATFolderService does not
    # need tested unless functionality is added to it. Its base class has
    # been tested in test_01_plone_service.
    pass


class BaseATTopicTestCase(BaseATTestCase):

    def afterSetUp(self):
        super(BaseATTopicTestCase, self).afterSetUp()
        self._setUpCollection()

    def beforeTearDown(self):
        self._tearDownCollection()
        super(BaseATTopicTestCase, self).beforeTearDown()

    def _createCollection(self, id, title, parent=None):
        if parent is None:
            parent = self.portal
        self.loginAsPortalOwner()
        collect = parent.invokeFactory('Topic', id, title=title)
        self.logout()
        return getattr(parent, collect)

    def _setUpCollection(self):
        self.login('test_user_1_')
        # Create two Events (event1 and event2) for use in the Collection.
        event_url = "http://weblion.psu.edu/"
        event_location = "University Park, Pennsylvania, United States " \
                         "of America"
        event1 = self.folder.invokeFactory('Event', 'event1',
                                           title="Event One",
                                           start_date="2009-01-01",
                                           end_date="2012-12-21",
                                           event_url=event_url,
                                           location=event_location)
        self.event1 = getattr(self.folder, event1)
        event2 = self.folder.invokeFactory('Event', 'event2',
                                           title="Event Two",
                                           start_date="2008-09-01",
                                           end_date="2009-05-13",
                                           event_url=event_url,
                                           location=event_location)
        self.event2 = getattr(self.folder, event2)
        self.loginAsPortalOwner()
        # Create a Collection.
        self.collect1 = self._createCollection('collect1', 'Collection One')
        # Assign a serviced collection.
        from wsapi4plone.core.interfaces import IServiceContainer
        self.serviced_collect = IServiceContainer(self.collect1)
        # Create a Type criteria.
        self.criteria = self.collect1.addCriterion('Type',
                                                   'ATSelectionCriterion')
        self.criteria.setValue('Event')
        self.logout()

    def _tearDownCollection(self):
        self.loginAsPortalOwner()
        # Deleted the serviced collection.
        del self.serviced_collect
        # Delete the two Events (event1 and event2).
        del self.event1
        del self.event2
        # Delete the criteria.
        del self.criteria
        # Delete the Collection.
        del self.collect1
        self.logout()


class BaseATTopicExtensionTestCase(BaseATTopicTestCase):

    ext_key = ''
    ext_has_callback = False

    @property
    def callback_ext_key(self):
        return '%s.callback' % self.ext_key

    def afterSetUp(self):
        super(BaseATTopicExtensionTestCase, self).afterSetUp()
        if self.ext_key == '':
            raise ValueError("You must assign a value to 'ext_key' in your "
                             "test case. Otherwise the test case will not "
                             "work correctly.")

    def test_extension_is_registered(self):
        result = self.serviced_collect.get_extensions()
        key = self.ext_key
        self.failUnless(key in result, "Couldn't find the extension data. " \
                                       "The component must not have been " \
                                       "registered properly.")
        # Now test for the extension as a callback
        result = self.serviced_collect.get_extensions(as_callback=True)
        if self.ext_has_callback:
            checker = self.assertTrue
        else:
            checker = self.assertFalse
        checker((self.callback_ext_key in result) and \
                (self.ext_key not in result))
        # We aren't checking for the data in this test, just that the
        # extension exists and can function as a callback.

    def test_extension_implements(self):
        from wsapi4plone.core.interfaces import IExtension
        collect = self.serviced_collect.context
        ext = getMultiAdapter((self.serviced_collect, collect,),
                              IExtension, name=self.ext_key)
        self.assert_(verifyObject(IExtension, ext))

    def get_extension(self):
        context = self.serviced_collect.context
        # Grab the extension
        from wsapi4plone.core.interfaces import IExtension
        ext = getMultiAdapter((self.serviced_collect, context,),
                              IExtension,
                              name=self.ext_key)
        return ext


class TestATTopicCriteriaExtension(BaseATTopicExtensionTestCase):

    ext_key = 'criteria'

    def afterSetUp(self):
        super(TestATTopicCriteriaExtension, self).afterSetUp()
        sm = getSiteManager()
        # Register the criteria extension
        from wsapi4plone.core.interfaces import (
            IServiceContainer, IServiceExtension)
        from wsapi4plone.core.extensions.archetype import (
            ATTopicCriteria, IATTopicCriteria)
        sm.registerUtility(IATTopicCriteria,
                           provided=IServiceExtension,
                           name=self.ext_key)
        sm.registerAdapter(ATTopicCriteria,
                           required=(IServiceContainer, IATTopic,),
                           provided=IATTopicCriteria,
                           name=self.ext_key)

    def beforeTearDown(self):
        sm = getSiteManager()
        # Register the criteria extension
        from wsapi4plone.core.interfaces import (
            IServiceContainer, IServiceExtension)
        from wsapi4plone.core.extensions.archetype import (
            ATTopicCriteria, IATTopicCriteria)
        sm.unregisterUtility(component=IATTopicCriteria,
                             provided=IServiceExtension,
                             name=self.ext_key)
        sm.unregisterAdapter(factory=ATTopicCriteria,
                             required=(IServiceContainer, IATTopic,),
                             provided=IATTopicCriteria,
                             name=self.ext_key)
        super(TestATTopicCriteriaExtension, self).beforeTearDown()

    def test_get_skeleton(self):
        # Delete all criteria currently defined on the test's collection.
        # Otherwise, the test will fail because the Type index will not be
        # in the fields value computed by the collection. Why? I don't know.
        for crit in self.collect1.listCriteria():
            self.collect1.deleteCriterion(crit.getId())
        # Create a new collection as the get_schema call would do.
        context = self._createCollection('newcollect', 'New Topic')
        # Define what we expect the extension to deliver.
        types = [t['name'] for t in context.listCriteriaTypes()]
        fields = [f[0] for f in context.listAvailableFields()]
        # Which is better, fields to types or types to fields?
        fields_to_types = dict([(f, context.allowedCriteriaForField(f),)
                                for f in fields
                                ])
        types_to_fields = [(t, [f for f in fields
                                if context.validateAddCriterion(f,t)
                                ]
                            ,)
                           for t in types]
        critters = {}
        for type, fields in types_to_fields:
            crit = context.addCriterion(fields[0], type)
            critters[type] = {}
            # criteria schema apparently does not have an items method
            fields = zip(crit.schema.keys(), crit.schema.values())
            for name, field in fields:
                critters[type][field.getName()] = {
                    'type': field.type,
                    'required': bool(field.required)}
        expected_results = [fields_to_types, critters]
        # Call the code to be tested into action.
        self.login('test_user_1_')
        ext = self.get_extension()
        actual_results = ext.get_skeleton()
        self.logout()
        # Check if they are equal.
        self.assertEqual(actual_results, expected_results)

    def test_get(self):
        # Define what we expect this tests results to look and feel like.
        collection = self.serviced_collect.context
        expected_results = {}
        for crit in collection.listCriteria():
            key = (crit.field, crit.meta_type,)
            critter = expected_results[key] = {}
            for field in crit.schema.values():
                fid = field.getName()
                critter[fid] = crit[fid]
        # Call the code to be tested into action.
        self.login('test_user_1_')
        ext = self.get_extension()
        actual_results = ext.get()
        self.logout()
        # Check for the results for accuracy.
        self.assertEqual(actual_results, expected_results)


# # Check for the collection content results.
# accepted_paths = (u'/'.join(self.event1.getPhysicalPath()),
#                   u'/'.join(self.event2.getPhysicalPath()),)
# for path in actual_results['contents']:
#     if path not in accepted_paths:
#         self.fail("Could not find %s in the list of expected paths." % path)



# # The call back should always have a function and args
# self.failUnless(callback.get('args', False) and callback.get('function', False))
# # The query criteria should look like the compiled query from the collection.
# self.failUnlessEqual(callback['args'][0], self.collect1.buildQuery())
# self.failUnlessEqual(callback['function'], 'query')






def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestATObjectService))
    suite.addTest(unittest.makeSuite(TestATFolderService))
    suite.addTest(unittest.makeSuite(TestATTopicCriteriaExtension))
    return suite