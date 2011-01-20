import pkg_resources, json

import wdmmg.model as model
from wdmmgext.load import barnet
import os

# Deprecating this class, as we no longer support Barnet data.

class TestBarnet(object):
    @classmethod
    def setup_class(self):
        #barnet.load()
        pass

    @classmethod
    def teardown_class(self):
        model.repo.delete_all()

	# check dataset exists
    def test_01_dataset(self):
        # out = (model.Session.query(model.Dataset)
        #     .filter_by(name=u'barnet')
        #     ).first()
        # assert out, out
        pass

	# get all our keys, and check values exist for them
    def test_02_classification(self):
        # for key_name in [u'from', u'time', u'key_barnet_level_1', u'key_barnet_level_2']:
        #     key = model.Session.query(model.Key).filter_by(name=key_name).first()
        #     assert key, key_name
        #     count = (model.Session.query(model.ClassificationItem)
        #         .join(model.EnumerationValue)
        #         .filter_by(key=key)
        #         ).count()
        #     assert count, (key_name, count)
        pass

    # check there are some entries and none of them are null
    def test_03_entry(self):
        # dataset_ = (model.Session.query(model.Dataset)
        #     .filter_by(name=u'barnet')
        #     ).one()
        # count = (model.Session.query(model.Entry)
        #     .filter_by(dataset_=dataset_)
        #     ).count()
        # assert count, 'There are no Entries'
        # assert not (model.Session.query(model.Entry)
        #     .filter_by(dataset_=dataset_)
        #     .filter_by(amount=None)
        #     ).first(), 'Some Entries have NULL amounts'
        pass
    
    # look for a 'to' field on the first entry in the dataset
    def test_04_entry_to(self):
        # dataset_ = (model.Session.query(model.Dataset)
        #     .filter_by(name=u'barnet')
        #     ).one()
        # txn = (model.Session.query(model.Entry)
        #     .filter_by(dataset_=dataset_)
        #     ).first()
        # classif = txn.classification_as_dict()
        # assert classif['to'] == u'society'
        pass
