import json
import os
import pkg_resources
import wdmmg.model as model
from wdmmgext.load import uganda
from wdmmgext.tests import DATADIR

# The Uganda data is entirely stored in Google Docs.
# Rather than use sample data here and rewrite the loader to use Excel,
# we supply the is_test parameter, which loads one sheet of the Google Doc.

class TestUganda(object):

    @classmethod
    def setup_class(self):
        model.mongo.drop_db()
        uganda.load(is_test=True)
        
    @classmethod
    def teardown_class(self):
        model.mongo.drop_db()

    # check dataset exists
    def test_01_dataset(self):
        out = model.Dataset.find_one({'name': uganda.DATASET_NAME})
        assert out, out

    # Get our keys, and check values exist for them.
    def test_02_classification(self):
        entry = model.Entry.find_one({'dataset.name': uganda.DATASET_NAME})
        for key_name in [u'from', u'time', u'uganda_id', u'gou_vote',
                u'project', u'cap_or_cur', u'wage_or_nonwage', 
                u'mtef_sector', u'mtef_reference', u'swg']:
            assert key_name in entry.keys(), "Key %s is missing" % key_name

    # Check there are some entries and none of them are null
    def test_03_entry(self):
        count = model.Entry.find({'dataset.name': uganda.DATASET_NAME}).count()
        assert count, 'There are no Entries'
        assert not model.Entry.find({'dataset.name': uganda.DATASET_NAME, 
                                'amount': None}).count(), 'Some Entries have NULL amounts'
    
    # Look for a 'to' field on the first entry in the dataset.
    def test_04_entry_to(self):
        entry = model.Entry.find_one({'dataset.name': uganda.DATASET_NAME})
        print entry['to']['label'] 
        assert entry['to']['label'] == u"President's Office"
