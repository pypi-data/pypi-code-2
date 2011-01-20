import json
import os
import pkg_resources
import wdmmg.model as model
from wdmmgext.load import departments
from wdmmgext.tests import DATADIR
from wdmmg.lib import loader

class TestDepartments(object):
    @classmethod
    def setup_class(self):
        model.mongo.drop_db()
        self.name = departments.DATASET_NAME
        test_file = os.path.join(DATADIR,
                'departmental-test-AGO-TSol-05-May-2010-after-12th.csv')
        department_loader = loader.Loader(departments.DATASET_NAME, u"Testing",
                u"gbp", u"Testing")
        departments.load_file(test_file, 'Attorney General\'s Office', \
                'Treasury Solicitor\'s Department', department_loader)

    @classmethod
    def teardown_class(self):
        model.mongo.drop_db()

    # check dataset exists
    def test_01_dataset(self):
        out = model.Dataset.find_one({'name': departments.DATASET_NAME})
        assert out, out

    # Get all our keys, and check values exist for them.
    def test_02_classification(self):
        entry = model.Entry.find_one({'dataset.name': departments.DATASET_NAME})
        for key_name in [u'from', u'time', u'filename', u'sub_unit',
                u'department_family', u'dept_entity', u'expense_type', u'expense_area',
                u'transaction_number']:
            assert key_name in entry.keys(), "Key %s is missing" % key_name

    # Check there are some entries and none of them are null
    def test_03_entry(self):
        count = model.Entry.find({'dataset.name': departments.DATASET_NAME}).count()
        assert count, 'There are no Entries'
        assert not model.Entry.find({'dataset.name': departments.DATASET_NAME, 
                                'amount': None}).count(), 'Some Entries have NULL amounts'
    
    # Look for a 'to' field on the first entry in the dataset.
    def test_04_entry_to(self):
        entry = model.Entry.find_one({'dataset.name': departments.DATASET_NAME})
        print entry['to']['label']
        assert entry['to']['label'] == u'Altodigital (UK) Limited'
