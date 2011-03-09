import zope.event
import unittest
from new import instancemethod
from zope.lifecycleevent import ObjectModifiedEvent

from collective.salesforce.query import config
from collective.salesforce.query.content.salesforcequery import SalesforceQuery
INDEXES_FORMAT = "SalesforceQueryIndex_"


from Products.CMFCore.utils import getToolByName
from base import TestCase, default_user

class DummyData:
    def __init__(self,**kwars):
        for k,v in kwars.items():
            setattr(self,k,v)

class Case:
    def __init__(self, case_id, case_subject, case_description):
        self.Id = case_id
        self.Subject = case_subject
        self.Description = case_description

    def get(self, attr, fallback=None):
        return getattr(self, attr, fallback)

    def __getitem__(self, attr):
        return self.get(attr)

dummy_data = {'Case': DummyData(fields={'Id': DummyData(**{'type':'string','name':'Id','label':'CaseId','filterable':True}),
                                        'Subject': DummyData(**{'type':'string','name':'Subject','label':'Subject','filterable':True}),
                                        'Description': DummyData(**{'type':'string','name':'Description','label':'Description','filterable':True}),
                                        },
                                objects=[Case('50001X1','50001X1 Subject', '50001X1 Description'),
                                        Case('50001X2','50001X2 Subject', '50001X2 Description'),
                                        Case('50001X3','50001X3 Subject', '50001X3 Description')]),
              'Contact': DummyData(fields={'Id': DummyData(**{'type':'string','name':'Id','label':'ContactId','filterable':True}),
                                           'FirstName': DummyData(**{'type':'string','name':'FirstName','label':'First Name','filterable':True}),
                                           'LastName':  DummyData(**{'type':'string','name':'LastName','label':'Last Name','filterable':True}),
                                          }),
              'Account': DummyData(fields={'Id':DummyData(**{})}),
             }

class dummy_salesforcetool(object):
    """ dummy salesforce function """

    def __init__(self, context):
        self.context = context
        self.bsize = 3

    def setBatchSize(self, size):
        self.bsize = size

    def query(self, q):
        results = {'records':dummy_data['Case'].objects[:self.bsize]}
        results['done'] = True
        results['queryLocator'] = '12345'
        if self.bsize < len(dummy_data['Case'].objects):
            results['done'] = False
        return results  

    def queryMore(self, querylocator):
        """
        We do not pretend to know if the batching of sforce works, only
        that we fetch all when there is more than one batch
        """
        results = {'records':dummy_data['Case'].objects[self.bsize:]}
        results['done'] = True
        return results

    def getUserInfo(self):
        pass

    def getDeleted(self,datatype, start, end):
        pass

    def getUpdated(self,datatype, start, end):
        pass

    def describeSObjects(self, datatypelist):
        return [dummy_data[datatype] for datatype in datatypelist]

    def describeGlobal(self):
        return {'types':dummy_data.keys()}


class TestSFQueryBase(TestCase):
    def afterSetUp(self):
        TestCase.afterSetUp(self)
        self.ctool = getToolByName(self.portal, 'portal_sfq_catalog')
        self.setRoles(['Manager',])
        self.portal.invokeFactory("SalesforceQuery",'sfquery')
        self.sfquery = self.portal.sfquery
        self.sfquery._get_sf_tool = instancemethod(lambda context: dummy_salesforcetool(context), self.sfquery, self.sfquery.__class__)
        self.portal.invokeFactory("SalesforceQuery",'sfquery2')
        self.sfquery2 = self.portal.sfquery2
        self.sfquery2._get_sf_tool = instancemethod(lambda context: dummy_salesforcetool(context), self.sfquery2,
                self.sfquery2.__class__)


class TestSFQuery_SFFields(TestSFQueryBase):
    """ testing the salesforce fields to use """
    def afterSetUp(self):
        TestSFQueryBase.afterSetUp(self)

    def test_sf_fields_per_datatype(self):
        """Check that after setting a SF Datatype on a SFQuery, the salesforce
        fields that SFQuery has are the ones that salesforce API say"""
        sfquery = self.sfquery
        a_datatype = 'Case'
        sfquery.setDatatype(a_datatype)
        self.assertEqual(sorted(dummy_data[a_datatype].fields.items()),
                         sorted(sfquery.getSFFields()))



class TestSFQuery_CatalogIndexes(TestSFQueryBase):
    """ testing catalog indexes creations and removals depending on SFQuery configurations"""
    def afterSetUp(self):
        TestSFQueryBase.afterSetUp(self)
        self.a_datatype = 'Case'
        self.sfquery.setDatatype(self.a_datatype)
        self.sfquery2.setDatatype(self.a_datatype)
        self.list_indexes = self.ctool.Indexes.keys

    def fire_modified_event(self, sfquery=None):
        sfquery = sfquery or self.sfquery
        zope.event.notify(ObjectModifiedEvent(sfquery,sfquery.REQUEST))

    def _base_test_adding_index(self, callable, fname='Subject', many_values=True):
        a_sf_field_id = fname
        new_index_id = '%s%s' % (INDEXES_FORMAT,a_sf_field_id)
        if many_values:
            callable([a_sf_field_id])
        else:
            callable(a_sf_field_id)
        self.fire_modified_event()
        self.failUnless(new_index_id in self.list_indexes())


    def test_adding_searchable_field_creates_index(self):
        self._base_test_adding_index(self.sfquery.setSearchable_fields)

    def test_adding_index_does_not_alter_other_indexes(self):
        a_sf_field_id = 'Subject'
        new_index_id = '%s%s' % (INDEXES_FORMAT,a_sf_field_id)
        previous_indexes = self.list_indexes()
        self._base_test_adding_index(self.sfquery.setSearchable_fields,
                                     fname=a_sf_field_id)
        self.assertEqual(sorted(previous_indexes+[new_index_id]),
                         sorted(self.list_indexes()))

    def _base_test_remove_added_field_removes_index(self, callable, many_values=True):
        a_sf_field_id = 'Subject'
        new_index_id = '%s%s' % (INDEXES_FORMAT,a_sf_field_id)
        #let's add the a field
        self._base_test_adding_index(callable,fname=a_sf_field_id,many_values=many_values)
        if many_values:
            callable([])
        else:
            callable('')
        self.fire_modified_event()
        self.failUnless(new_index_id in self.list_indexes())

    def test_removing_searchable_field_removes_index(self):
        self._base_test_remove_added_field_removes_index(self.sfquery.setSearchable_fields)

    def test_set_searchable_fields_in_second_query_does_not_produce_index_conflicts(self):
        """
        Test that adding an indexable field with the same name in another query does not
        create conflicts with existing ones or duplicates or strange things.
        The actual proof of this tests is that it does not tracebacks.
        """
        previous_indexes = self.list_indexes()
        fname = 'try_conflicting_01'
        self._base_test_adding_index(self.sfquery.setSearchable_fields, fname)
        self.assertEqual(sorted(previous_indexes + ["%s%s" % (INDEXES_FORMAT,fname) ]),sorted(self.list_indexes()))
        self._base_test_adding_index(self.sfquery2.setSearchable_fields, fname)
        self.assertEqual(sorted(previous_indexes + ["%s%s" % (INDEXES_FORMAT,fname) ]),sorted(self.list_indexes()))

    def test_index_not_removed_until_none_references(self):
        """
        Catalog indexes should not be removed until no object references them
        """
        previous_indexes = self.list_indexes()
        fname = 'try_conflicting_02'
        self._base_test_adding_index(self.sfquery.setSearchable_fields, fname )
        self.assertEqual(sorted(previous_indexes + ["%s%s" % (INDEXES_FORMAT,fname) ]),sorted(self.list_indexes()))
        self._base_test_adding_index(self.sfquery2.setSearchable_fields, fname)
        self.assertEqual(sorted(previous_indexes + ["%s%s" % (INDEXES_FORMAT,fname) ]),sorted(self.list_indexes()))
        self.sfquery.setSearchable_fields([])
        self.fire_modified_event()
        self.assertEqual(sorted(previous_indexes + ["%s%s" % (INDEXES_FORMAT,fname) ]),sorted(self.list_indexes()))
        self.sfquery2.setSearchable_fields([])
        self.fire_modified_event(self.sfquery2)
        self.assertEqual(sorted(previous_indexes),sorted(self.list_indexes()))

    def test_update_gets_all_content(self):
        self.sfquery.purge_cache()
        self.failUnless(len(self.sfquery.data()) == 0)
        self.sfquery.update()
        self.failUnless(len(self.sfquery.data()) == 3)
        dummy_data['Case'].objects.append(Case('50001X4','50001X4 Subject', '50001X4 Description'))
        self.sfquery.update()
        self.failUnless(len(self.sfquery.data()) == 4)


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestSFQuery_SFFields))
    suite.addTest(unittest.makeSuite(TestSFQuery_CatalogIndexes))

    return suite
