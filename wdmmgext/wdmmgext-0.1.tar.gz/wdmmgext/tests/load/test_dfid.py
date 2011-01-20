import json
import os
import pkg_resources
import wdmmg.model as model
from wdmmgext.load import dfid
from wdmmgext.tests import DATADIR

class TestDfid(object):

    @classmethod
    def setup_class(self):
        model.mongo.drop_db()
        filepath = os.path.join(DATADIR, 'dfid_short.xls')
        print filepath
        dfid.load_file(filepath)
        
    @classmethod
    def teardown_class(self):
        model.mongo.drop_db()

    # check dataset exists
    def test_01_dataset(self):
        out = model.Dataset.find_one({'name': dfid.DATASET_NAME})
        assert out, out

    # Get our keys, and check values exist for them.
    def test_02_classification(self):
        entry = model.Entry.find_one({'dataset.name': dfid.DATASET_NAME})
        for key_name in [u'from', u'time', u'dfid']:
            assert key_name in entry.keys(), "Key %s is missing" % key_name

    # Check there are some entries and none of them are null
    def test_03_entry(self):
        count = model.Entry.find({'dataset.name': dfid.DATASET_NAME}).count()
        assert count, 'There are no Entries'
        assert not model.Entry.find({'dataset.name': dfid.DATASET_NAME, 
                                'amount': None}).count(), 'Some Entries have NULL amounts'
    
    # Look for a 'to' field on the first entry in the dataset.
    def test_04_entry_to(self):
        entry = model.Entry.find_one({'dataset.name': dfid.DATASET_NAME})
        print entry['to']['label']
        assert entry['to']['label'] == u'Society (the General Public)'
